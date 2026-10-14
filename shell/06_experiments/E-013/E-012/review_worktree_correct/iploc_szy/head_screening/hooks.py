"""Periodic, resumable head-screening hook isolated from the SFT runner."""

from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from ..registry import HEAD_FINDERS, HEAD_PROBES, HOOKS
from ..utils.distributed import barrier, gather_objects
from ..engine.hooks import Hook


def set_jaccard(first, second) -> float:
    first, second = set(first), set(second)
    return len(first & second) / len(first | second) if first | second else 1.0


@HOOKS.register_module()
class HeadScreeningHook(Hook):
    """Run an attention probe twice per epoch and persist head-set convergence."""

    priority = 70

    def __init__(
        self,
        probe: Mapping[str, Any],
        finder: Mapping[str, Any],
        interval_epochs: float = 0.5,
        start_epoch: float = 0.5,
        stability_head_count: int = 5,
        stability_jaccard: float = 1.0,
        stability_patience: int = 3,
    ) -> None:
        self.probe = HEAD_PROBES.build(dict(probe))
        self.finder = HEAD_FINDERS.build(dict(finder))
        self.interval_epochs = float(interval_epochs)
        self.start_epoch = float(start_epoch)
        self.stability_head_count = int(stability_head_count)
        self.stability_jaccard = float(stability_jaccard)
        self.stability_patience = int(stability_patience)
        if self.interval_epochs <= 0.0 or self.start_epoch < 0.0:
            raise ValueError("head-screening epoch schedule is invalid")
        if self.stability_head_count <= 0 or self.stability_patience <= 0:
            raise ValueError("head-screening stability settings must be positive")
        if not 0.0 <= self.stability_jaccard <= 1.0:
            raise ValueError("stability_jaccard must be in [0, 1]")
        self.root: Optional[Path] = None
        self.next_target_samples = 0.0
        self.screening_index = 0
        self.previous: Optional[Dict[str, Any]] = None
        self.stable_streak = 0

    def before_run(self, runner) -> None:
        self.root = Path(runner.work_dir) / "head_screening"
        if runner.is_main_process:
            self.root.mkdir(parents=True, exist_ok=True)
        if runner.context:
            barrier(runner.context)
        latest_path = self.root / "latest.json"
        if latest_path.is_file():
            latest = json.loads(latest_path.read_text(encoding="utf-8"))
            if int(latest.get("step", -1)) > runner.step:
                raise RuntimeError(
                    "head-screening history is ahead of the resumed checkpoint; "
                    "use a new work_dir for a branched training trajectory"
                )
            self.previous = latest if latest.get("status") == "completed" else None
            self.screening_index = int(latest.get("screening_index", -1)) + 1
            self.stable_streak = int(
                latest.get("stability", {}).get("consecutive_stable", 0)
            )
        self.next_target_samples = self._next_boundary(
            runner.samples_seen, len(runner.dataset)
        )

    def after_train_step(self, runner) -> None:
        if runner.samples_seen < self.next_target_samples:
            return
        target = self.next_target_samples
        self._run_screening(runner, target)
        while self.next_target_samples <= runner.samples_seen:
            self.next_target_samples += self.interval_epochs * len(runner.dataset)

    def after_run(self, runner) -> None:
        if not runner.is_main_process:
            return
        runner.metrics["head_screening"] = {
            "enabled": True,
            "interval_epochs": self.interval_epochs,
            "screenings_completed": self.screening_index,
            "latest": str(self.root / "latest.json") if self.root else None,
            "stable_candidate": bool(
                self.previous
                and self.previous.get("stability", {}).get("stable_candidate")
            ),
            "automatic_phase_transition": False,
        }

    def run_once(self, runner) -> Dict[str, Any]:
        """Run one standalone screen against the currently loaded checkpoint."""
        self.before_run(runner)
        self._run_screening(runner, float(runner.samples_seen))
        if self.root is None:
            raise RuntimeError("head-screening root was not initialized")
        return json.loads((self.root / "latest.json").read_text(encoding="utf-8"))

    def _next_boundary(self, samples_seen: int, dataset_size: int) -> float:
        start = self.start_epoch * dataset_size
        interval = self.interval_epochs * dataset_size
        if samples_seen < start:
            return start
        completed = math.floor((samples_seen - start) / interval) + 1
        return start + completed * interval

    def _run_screening(self, runner, target_samples: float) -> None:
        if self.root is None:
            raise RuntimeError("head-screening hook was not initialized")
        target_epoch = target_samples / len(runner.dataset)
        screen_dir = self.root / (
            f"screen_{self.screening_index:04d}_epoch_{target_epoch:07.3f}"
        )
        if runner.is_main_process:
            screen_dir.mkdir(parents=True, exist_ok=False)
        if runner.context:
            barrier(runner.context)

        try:
            local_payload = self.probe.collect(
                runner, self.screening_index, screen_dir
            )
        except Exception as exc:
            local_payload = {
                "rank": runner.rank,
                "records": [],
                "failures": [
                    {"reason": f"{type(exc).__name__}: {exc}", "scope": "probe"}
                ],
            }
        payloads = (
            gather_objects(local_payload, runner.context)
            if runner.context
            else [local_payload]
        )

        if runner.is_main_process:
            records = [record for payload in payloads for record in payload["records"]]
            failures = [failure for payload in payloads for failure in payload["failures"]]
            if failures:
                summary = self._failed_summary(
                    runner, target_samples, target_epoch, records, failures
                )
            else:
                try:
                    result = self.finder.find(records)
                    stability = self._stability(result)
                    summary = {
                        **result,
                        "screening_index": self.screening_index,
                        "step": runner.step,
                        "samples_seen": runner.samples_seen,
                        "scheduled_samples": target_samples,
                        "nominal_epoch": runner.samples_seen / len(runner.dataset),
                        "scheduled_epoch": target_epoch,
                        "probe_records": records,
                        "stability": stability,
                    }
                except Exception as exc:
                    summary = self._failed_summary(
                        runner,
                        target_samples,
                        target_epoch,
                        records,
                        [
                            {
                                "reason": f"{type(exc).__name__}: {exc}",
                                "scope": "finder",
                            }
                        ],
                    )
            self._publish(screen_dir, summary)
        if runner.context:
            barrier(runner.context)

        latest = json.loads((self.root / "latest.json").read_text(encoding="utf-8"))
        if latest.get("status") != "completed":
            raise RuntimeError(
                "head screening failed: "
                + str(latest.get("failures", [{}])[0].get("reason", "unknown"))
            )
        self.previous = latest
        self.stable_streak = int(latest["stability"]["consecutive_stable"])
        self.screening_index += 1
        if runner.is_main_process:
            top = str(self.stability_head_count)
            print(
                "[HEAD_SCREEN] "
                f"index={latest['screening_index']} epoch={latest['nominal_epoch']:.3f} "
                f"query_top{top}={latest['selected_sets']['query'][top]} "
                f"reference_top{top}={latest['selected_sets']['reference'][top]} "
                f"stable_streak={self.stable_streak} "
                f"stable_candidate={latest['stability']['stable_candidate']}",
                flush=True,
            )

    def _stability(self, result: Mapping[str, Any]) -> Dict[str, Any]:
        key = str(self.stability_head_count)
        current_query = result["selected_sets"]["query"][key]
        current_reference = result["selected_sets"]["reference"][key]
        if self.previous is None:
            query_jaccard = reference_jaccard = None
            stable = False
        else:
            query_jaccard = set_jaccard(
                current_query, self.previous["selected_sets"]["query"][key]
            )
            reference_jaccard = set_jaccard(
                current_reference,
                self.previous["selected_sets"]["reference"][key],
            )
            stable = (
                query_jaccard >= self.stability_jaccard
                and reference_jaccard >= self.stability_jaccard
            )
        self.stable_streak = self.stable_streak + 1 if stable else 0
        return {
            "head_count": self.stability_head_count,
            "query_jaccard_to_previous": query_jaccard,
            "reference_jaccard_to_previous": reference_jaccard,
            "jaccard_threshold": self.stability_jaccard,
            "consecutive_stable": self.stable_streak,
            "patience": self.stability_patience,
            "stable_candidate": self.stable_streak >= self.stability_patience,
            "automatic_phase_transition": False,
        }

    def _failed_summary(
        self,
        runner,
        target_samples: float,
        target_epoch: float,
        records,
        failures,
    ) -> Dict[str, Any]:
        return {
            "schema": "iploc-szy.head-screening.failure/v1",
            "status": "failed",
            "screening_index": self.screening_index,
            "step": runner.step,
            "samples_seen": runner.samples_seen,
            "scheduled_samples": target_samples,
            "nominal_epoch": runner.samples_seen / len(runner.dataset),
            "scheduled_epoch": target_epoch,
            "records_collected": len(records),
            "failures": failures,
        }

    def _publish(self, screen_dir: Path, summary: Dict[str, Any]) -> None:
        summary = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            **summary,
        }
        summary_path = screen_dir / "summary.json"
        summary_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        latest_path = self.root / "latest.json"
        temporary = latest_path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, latest_path)
        history_path = self.root / "history.jsonl"
        history_row = {
            key: summary.get(key)
            for key in (
                "timestamp_utc",
                "status",
                "screening_index",
                "step",
                "samples_seen",
                "nominal_epoch",
                "scheduled_epoch",
                "selected_sets",
                "stability",
                "failures",
            )
            if key in summary
        }
        with history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(history_row, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
