"""Config-defined auxiliary-loss stages, measured in completed optimizer updates."""

from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import random

import numpy as np
import torch

from ..registry import AUXILIARY_LOSSES, HEAD_FINDERS, HEAD_PROBES
from ..utils.distributed import barrier, gather_objects


class TrainingPipeline:
    """Change losses/heads only between optimizer updates; checkpoint selection state."""

    def __init__(self, stages, screening=None):
        self.specification = deepcopy(dict(stages=stages, screening=screening))
        self.signature = hashlib.sha256(
            json.dumps(self.specification, sort_keys=True).encode()
        ).hexdigest()
        if not isinstance(stages, dict) or not stages:
            raise ValueError("pipeline.stages must be a nonempty ordered mapping")
        self.stages = []
        previous = -1
        for name, raw in stages.items():
            stage = deepcopy(raw)
            start = stage.get("start_step")
            if not isinstance(start, int) or isinstance(start, bool) or start <= previous:
                raise ValueError("stage start_step must be strictly increasing integers")
            if not self.stages and start != 0:
                raise ValueError("the first pipeline stage must start at step 0")
            previous = start
            if not name or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789_-" for c in name):
                raise ValueError("stage names must use lowercase letters, digits, _ or -")
            auxiliary = stage.get("auxiliary_loss")
            selection = stage.get("head_selection")
            if selection:
                if not auxiliary or not screening:
                    raise ValueError("head_selection requires auxiliary_loss and screening")
                count = selection.get("top_k")
                interval = selection.get("refresh_steps")
                if not isinstance(count, int) or count < 1:
                    raise ValueError("head_selection.top_k must be positive")
                if interval is not None and (not isinstance(interval, int) or interval < 1):
                    raise ValueError("refresh_steps must be positive or None (freeze)")
            ramp = stage.get("ramp_steps", 0)
            if not isinstance(ramp, int) or ramp < 0:
                raise ValueError("ramp_steps must be a nonnegative integer")
            for value in (stage.get("ramp_from_coefficient", 0.0),
                          (auxiliary or {}).get("coefficient", 0.0)):
                if not math.isfinite(float(value)) or float(value) < 0:
                    raise ValueError("pipeline coefficients must be finite and nonnegative")
            self.stages.append((name, stage))
        self.screening = deepcopy(screening)
        self.stage_index = None
        self.last_selection_step = None
        self.active_loss_config = None
        self.selection_source = None
        self._built = False

    def state_dict(self):
        return dict(signature=self.signature, stage_index=self.stage_index,
                    last_selection_step=self.last_selection_step,
                    active_loss_config=deepcopy(self.active_loss_config),
                    selection_source=self.selection_source)

    def load_state_dict(self, state):
        if not state or state.get("signature") != self.signature:
            raise ValueError("resume pipeline specification differs from checkpoint")
        self.stage_index = state["stage_index"]
        self.last_selection_step = state["last_selection_step"]
        self.active_loss_config = deepcopy(state["active_loss_config"])
        self.selection_source = state.get("selection_source")
        self._built = False

    def prepare(self, runner, completed_steps):
        """At completed_steps=83, prepare the loss used for update 84."""
        index = max(i for i, (_, stage) in enumerate(self.stages)
                    if stage["start_step"] <= completed_steps)
        name, stage = self.stages[index]
        changed = index != self.stage_index
        if changed:
            self.stage_index = index
            self.last_selection_step = None
            self.selection_source = None
            self.active_loss_config = deepcopy(stage.get("auxiliary_loss"))
        selection = stage.get("head_selection")
        refresh = False
        if selection:
            interval = selection.get("refresh_steps")
            refresh = self.last_selection_step is None or (
                interval is not None and completed_steps >= self.last_selection_step + interval
            )
        if changed or refresh or not self._built:
            self._close_loss(runner)
            if refresh:
                heads, source = self._screen(runner, completed_steps, name, selection)
                self.active_loss_config["student_heads"] = heads
                self.last_selection_step = completed_steps
                self.selection_source = source
            runner.auxiliary_loss = AUXILIARY_LOSSES.build(
                deepcopy(self.active_loss_config), wrapper=runner.wrapper,
                dataset=runner.dataset, collator=runner.collator,
            )
            self._built = True
            if changed or refresh:
                self._record(runner, completed_steps, name)
        coefficient = 0.0
        if runner.auxiliary_loss is not None:
            coefficient = float(self.active_loss_config.get("coefficient", 0.0))
            ramp = stage.get("ramp_steps", 0)
            if ramp:
                fraction = min(1.0, (completed_steps - stage["start_step"] + 1) / ramp)
                initial = float(stage.get("ramp_from_coefficient", 0.0))
                coefficient = initial + (coefficient - initial) * fraction
            runner.auxiliary_loss.coefficient = coefficient
        runner.pipeline_metrics = dict(pipeline_stage=float(index),
                                       auxiliary_coefficient=coefficient)

    @staticmethod
    def _close_loss(runner):
        loss = runner.auxiliary_loss
        extractor = getattr(loss, "extractor", None)
        if extractor is not None:
            extractor.close()
        runner.auxiliary_loss = None

    def _screen(self, runner, completed_steps, name, selection):
        """Use the current training dataset; preserve RNG and a fixed sampled subset."""
        root = Path(runner.work_dir) / "pipeline" / name / f"step_{completed_steps:06d}"
        if runner.is_main_process:
            root.mkdir(parents=True, exist_ok=True)
        if runner.context:
            barrier(runner.context)
        probe = HEAD_PROBES.build(deepcopy(self.screening["probe"]))
        finder_config = deepcopy(self.screening["finder"])
        finder_config["fixed_head_counts"] = [selection["top_k"]]
        finder = HEAD_FINDERS.build(finder_config)
        # Cover the model's actual devices without initializing unrelated GPUs.
        model = getattr(runner.wrapper, "peft_model", None)
        devices = sorted({parameter.device.index for parameter in model.parameters()
                          if parameter.device.type == "cuda"}) if model is not None else []
        python_state, numpy_state = random.getstate(), np.random.get_state()
        try:
            with torch.random.fork_rng(devices=devices):
                try:
                    local = probe.collect(runner, 0, root)
                except Exception as error:
                    local = dict(records=[], failures=[dict(reason=str(error))])
        finally:
            random.setstate(python_state)
            np.random.set_state(numpy_state)
        payloads = gather_objects(local, runner.context) if runner.context else [local]
        records = sorted((row for payload in payloads for row in payload["records"]),
                         key=lambda row: row["dataset_index"])
        failures = [row for payload in payloads for row in payload["failures"]]
        summary = None
        if runner.is_main_process:
            try:
                if failures:
                    raise RuntimeError(str(failures[0]))
                result = finder.find(records)
                heads = list(result["selected_sets"][selection.get("role", "query")][str(selection["top_k"])])
                summary = dict(**result, heads=heads, completed_steps=completed_steps,
                               dataset_manifest=getattr(runner.dataset, "ann_file", None),
                               probe_records=records)
            except Exception as error:
                summary = dict(status="failed", reason=str(error))
            self._write_json(root / "selection.json", summary)
        if runner.context:
            summary = gather_objects(summary, runner.context)[0]
        if summary["status"] != "completed":
            raise RuntimeError("pipeline head screening failed: " + summary["reason"])
        return summary["heads"], str(root / "selection.json")

    def _record(self, runner, completed_steps, name):
        if not runner.is_main_process:
            return
        root = Path(runner.work_dir) / "logs"
        root.mkdir(parents=True, exist_ok=True)
        payload = dict(completed_steps=completed_steps, next_update=completed_steps + 1,
                       stage=name, **self.state_dict())
        with (root / "pipeline_events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        print(f"[TRAIN_PIPELINE] stage={name} next_update={completed_steps + 1} "
              f"heads={(self.active_loss_config or {}).get('student_heads', [])}", flush=True)

    @staticmethod
    def _write_json(path, payload):
        temporary = path.with_suffix(".tmp.json")
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
        temporary.replace(path)
