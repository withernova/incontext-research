#!/usr/bin/env python3
"""Distributed autoregressive localization evaluation for one named branch."""

from __future__ import annotations

import argparse
import json
import os
import random
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import torch
from PIL import Image

from iploc_szy import DATASETS, EVALUATORS, MODELS
from iploc_szy.run_snapshot import save_snapshot, save_prompt_example
from iploc_szy.branching import load_experiment_config
from iploc_szy.checkpointing import load_adapter_checkpoint
from iploc_szy.run_management import mark_run_event, validate_prepared_run
from iploc_szy.utils.distributed import (
    barrier,
    gather_objects,
    shutdown_distributed,
)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    parser.add_argument("--cfg-options", nargs="*", default=[])
    return parser.parse_args(argv)


def configure_vision_limit(processor: Any, settings: Dict[str, Any]) -> Optional[int]:
    """Match evaluation image resizing to the training visual-token cap."""
    configured = settings.get("vision_max_patch_tokens")
    if configured in (None, "None"):
        return None
    patch_tokens = int(configured)
    if patch_tokens < 1:
        raise ValueError("evaluation.vision_max_patch_tokens must be positive or None")
    patch_size = getattr(processor.image_processor, "patch_size", None)
    if not isinstance(patch_size, int) or patch_size < 1:
        raise ValueError("processor image patch_size must be a positive integer")
    max_pixels = patch_tokens * patch_size * patch_size
    processor.image_processor.size["longest_edge"] = max_pixels
    return max_pixels


def _generate(wrapper: Any, sample: Dict[str, Any], settings: Dict[str, Any]) -> str:
    prompt_messages = sample["messages"][:-1]
    images = []
    for path in sample["image_paths"]:
        with Image.open(path) as image:
            images.append(image.convert("RGB"))
    text = wrapper.processor.apply_chat_template(
        prompt_messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = wrapper.processor(
        text=[text],
        images=images,
        return_tensors="pt",
    ).to(wrapper.input_device)
    model = getattr(wrapper, "peft_model", wrapper.model)
    if settings.get("_attention_intervention") is not None:
        from iploc_szy.evaluation.query_attention import generate_comparison
        return generate_comparison(model, wrapper.processor, inputs, sample["answer"],
                                   settings, settings["_attention_intervention"])
    with torch.inference_mode():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=int(settings.get("max_new_tokens", 32)),
            do_sample=bool(settings.get("do_sample", False)),
        )
    generated_ids = output_ids[:, inputs.input_ids.shape[1] :]
    return wrapper.processor.batch_decode(
        generated_ids,
        skip_special_tokens=True,
    )[0]


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def evaluation_indices(dataset_size: int, settings: Dict[str, Any]):
    """Choose a reproducible subset without defaulting to manifest head rows."""
    configured_limit = settings.get("limit")
    limit = (
        dataset_size
        if configured_limit in (None, "None")
        else min(int(configured_limit), dataset_size)
    )
    if limit < 1:
        raise ValueError("evaluation.limit must select at least one sample")
    selection = str(settings.get("selection", "head"))
    if selection == "head":
        return list(range(limit))
    if selection == "seeded_random":
        seed = int(settings.get("seed", 20260901))
        return sorted(random.Random(seed).sample(range(dataset_size), limit))
    raise ValueError("evaluation.selection must be 'head' or 'seeded_random'")


def metrics_by_dataset(rows: Sequence[Dict[str, Any]], evaluator_config: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """Compute primary per-dataset metrics for a combined manifest."""
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["dataset"]), []).append(row)
    result: Dict[str, Dict[str, float]] = {}
    for dataset_name, dataset_rows in sorted(grouped.items()):
        evaluator = EVALUATORS.build(evaluator_config)
        for row in dataset_rows:
            evaluator.process(row["prediction"], row["target"], row["id"])
        result[dataset_name] = evaluator.evaluate()
    return result


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    config = load_experiment_config(args.config, args.cfg_options)
    validate_prepared_run(config)
    launcher_rank_zero = int(os.environ.get("RANK", "0")) == 0
    snapshot = save_snapshot(config, args.config, "evaluate") if launcher_rank_zero else None
    wrapper = None
    try:
        if launcher_rank_zero:
            mark_run_event(config, "evaluation_started", "running")
        settings = dict(config.get("evaluation") or {})
        intervention_enabled = (config.get("branch") or {}).get("action") == "attention_intervene"
        if intervention_enabled:
            from iploc_szy.evaluation.query_attention import validate_run_config
            validate_run_config(config)
            settings["_attention_intervention"] = dict(config["attention_intervention"])
        dataloader_key = str(settings.get("dataloader", "train_dataloader"))
        if dataloader_key not in config:
            raise KeyError(f"evaluation dataloader is missing: {dataloader_key}")
        wrapper = MODELS.build(config["model"])
        vision_max_pixels = configure_vision_limit(wrapper.processor, settings)
        context = getattr(wrapper, "context", None)
        rank = context.rank if context else 0
        world_size = context.world_size if context else 1
        checkpoint = config["named_run"]["resolved_resume_checkpoint"]
        load_adapter_checkpoint(wrapper, checkpoint)
        model = getattr(wrapper, "peft_model", wrapper.model)
        model.eval()

        dataset = DATASETS.build(config[dataloader_key]["dataset"])
        if snapshot is not None:
            save_prompt_example(snapshot, dataset[0])
        if intervention_enabled and settings.get("limit") not in (None, "None") and int(settings["limit"]) > len(dataset):
            raise ValueError("fixed evaluation.limit exceeds dataset size")
        selected_indices = evaluation_indices(len(dataset), settings)
        total = len(selected_indices)
        if intervention_enabled:
            from iploc_szy.evaluation.auto_query_heads import resolve_query_heads
            settings["_attention_intervention"] = resolve_query_heads(
                wrapper, dataset, selected_indices, config, settings)
            import hashlib
            manifest = Path(config[dataloader_key]["dataset"]["ann_file"])
            _write_json(Path(config["work_dir"]) / "query_attention" / f"frozen_rank_{rank}.json",
                        dict(indices=selected_indices, manifest=str(manifest),
                             manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),
                             settings=settings, checkpoint=str(checkpoint)))
        local_rows = []
        started = time.time()
        log_interval = max(1, int(settings.get("log_interval", 10)))
        local_indices = selected_indices[rank::world_size]
        for local_count, index in enumerate(local_indices, start=1):
            sample = dataset[index]
            prediction = _generate(wrapper, sample, settings)
            comparison = prediction if intervention_enabled else None
            if comparison is not None:
                prediction = comparison["conditions"]["baseline"]["prediction"]
                _write_json(Path(config["work_dir"]) / "query_attention" / f"sample_{index:08d}.json",
                            dict(dataset_index=index, id=sample["id"], **comparison))
            local_rows.append(
                {
                    "dataset_index": index,
                    "id": sample["id"],
                    "prediction": prediction,
                    "target": sample["answer"],
                    "dataset": str(sample["raw"].get("dataset", "unknown")),
                    "sequence": str(sample["raw"].get("sequence", "")),
                    "rank": rank,
                    **({"attention_comparison": {
                        **{k: v for k, v in comparison.items() if k not in ("geometry", "conditions")},
                        "conditions": {
                            mode: {k: v for k, v in values.items() if k != "attention"}
                            for mode, values in comparison["conditions"].items()},
                        "audit_path": str(Path(config["work_dir"]) / "query_attention" / f"sample_{index:08d}.json"),
                    }} if comparison is not None else {}),
                }
            )
            if local_count % log_interval == 0:
                elapsed = max(time.time() - started, 1e-9)
                print(
                    f"[EVAL_PROGRESS] rank={rank} local={local_count} "
                    f"rate={local_count / elapsed:.3f}_samples_per_second",
                    flush=True,
                )
        payloads = gather_objects(local_rows, context) if context else [local_rows]

        if rank == 0:
            rows = sorted(
                (row for payload in payloads for row in payload),
                key=lambda row: row["dataset_index"],
            )
            evaluator_config = config.get(
                "evaluator", {"type": "LocalizationEvaluator"}
            )
            evaluator = EVALUATORS.build(evaluator_config)
            for row in rows:
                evaluator.process(row["prediction"], row["target"], row["id"])
            enriched = []
            for source, scored in zip(rows, evaluator.rows):
                enriched.append({**source, **scored})
            elapsed = time.time() - started
            metrics = {
                "status": "completed",
                "action": "evaluate",
                "checkpoint": str(checkpoint),
                "dataloader": dataloader_key,
                "dataset_size": len(dataset),
                "evaluated_samples": len(rows),
                "world_size": world_size,
                "max_new_tokens": int(settings.get("max_new_tokens", 32)),
                "vision_max_patch_tokens": (
                    int(settings["vision_max_patch_tokens"])
                    if settings.get("vision_max_patch_tokens") not in (None, "None")
                    else None
                ),
                "vision_max_pixels": vision_max_pixels,
                "selection": str(settings.get("selection", "head")),
                "selection_seed": (
                    int(settings.get("seed", 20260901))
                    if settings.get("selection", "head") == "seeded_random"
                    else None
                ),
                "seconds": elapsed,
                "samples_per_second": len(rows) / elapsed if elapsed else 0.0,
                **evaluator.evaluate(),
                "by_dataset": metrics_by_dataset(rows, evaluator_config),
            }
            if intervention_enabled:
                from iploc_szy.evaluation.query_attention import summarize_comparisons
                metrics["action"] = "attention_intervene"
                metrics["attention_intervention"] = summarize_comparisons(rows)
                if not metrics["attention_intervention"]["integrity_passed"]:
                    metrics["status"] = "integrity_failed"
            output_dir = Path(config["work_dir"]) / "evaluation"
            output_dir.mkdir(parents=True, exist_ok=False)
            predictions_path = output_dir / "predictions.jsonl"
            with predictions_path.open("x", encoding="utf-8") as handle:
                for row in enriched:
                    handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            _write_json(output_dir / "metrics.json", metrics)
            if intervention_enabled and metrics["status"] == "integrity_failed":
                raise RuntimeError("query attention integrity gate failed; audits and metrics saved")
            mark_run_event(
                config,
                "evaluation_finished",
                "completed",
                {
                    "samples": len(rows),
                    "miou": metrics["miou"],
                    "metrics": str(output_dir / "metrics.json"),
                },
            )
            print("[EVAL_DONE]", json.dumps(metrics, ensure_ascii=False), flush=True)
        if context:
            barrier(context)
        return 0
    except BaseException as error:
        if launcher_rank_zero:
            try:
                mark_run_event(
                    config,
                    "evaluation_failed",
                    "failed",
                    {"exception_type": type(error).__name__},
                )
            except Exception:
                pass
        raise
    finally:
        context = getattr(wrapper, "context", None) if wrapper is not None else None
        if context:
            shutdown_distributed(context)


if __name__ == "__main__":
    raise SystemExit(main())
