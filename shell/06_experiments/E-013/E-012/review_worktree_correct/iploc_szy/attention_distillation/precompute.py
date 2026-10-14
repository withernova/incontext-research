"""Offline fixed-teacher precomputation using exact selected attention slices."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import torch

from ..checkpointing import load_adapter_checkpoint
from ..utils.distributed import barrier, gather_objects
from .artifacts import (
    ensemble_teacher,
    finalize_teacher_manifest,
    load_teacher_record,
    sample_geometries,
    write_teacher_record,
)
from .selected import SelectedAttentionExtractor, parse_head


def precompute_fixed_teacher(runner: Any, config: Mapping[str, Any]) -> Path:
    """Create a complete immutable teacher directory, distributed by dataset row."""
    output_dir = Path(str(config["output_dir"])).resolve()
    checkpoint = str(config["checkpoint"])
    teacher_heads = tuple(parse_head(value) for value in config["teacher_heads"])
    if config.get("allow_variable_head_counts", False):
        if not teacher_heads or len(set(teacher_heads)) != len(teacher_heads):
            raise ValueError("teacher heads must be nonempty and unique")
    elif len(teacher_heads) != 3:
        raise ValueError("fixed E009 teacher requires exactly three heads")
    manifest_path = output_dir / "manifest.json"
    if manifest_path.exists():
        raise FileExistsError(f"teacher manifest already exists: {manifest_path}")
    if runner.context:
        barrier(runner.context)
    if runner.is_main_process:
        output_dir.mkdir(parents=True, exist_ok=True)
    if runner.context:
        barrier(runner.context)

    load_adapter_checkpoint(runner.wrapper, checkpoint)
    model = runner.wrapper.peft_model
    model.eval()
    extractor = SelectedAttentionExtractor(model, teacher_heads)
    base = model.get_base_model()
    image_token_id = int(base.config.image_token_id)
    merge = int(base.config.vision_config.spatial_merge_size)
    local_records = []
    try:
        with torch.inference_mode():
            for dataset_index in range(runner.rank, len(runner.dataset), runner.world_size):
                sample = runner.dataset[dataset_index]
                encoded = runner.collator([sample])
                metadata = encoded.pop("metadata")
                batch = {
                    key: value.to(runner.wrapper.input_device)
                    for key, value in encoded.items()
                }
                geometries = sample_geometries(
                    batch["input_ids"],
                    metadata,
                    image_token_id=image_token_id,
                    spatial_merge_size=merge,
                )
                existing = load_teacher_record(output_dir, dataset_index, geometries[0])
                if existing is not None:
                    local_records.append(existing)
                else:
                    extractor.begin()
                    forward = {key: value for key, value in batch.items() if key != "labels"}
                    forward.update(use_cache=False, return_dict=True, logits_to_keep=1)
                    model(**forward)
                    selected = extractor.extract([geometries[0].prediction_rows])
                    values = ensemble_teacher(
                        selected, 0, geometries[0], teacher_heads
                    )
                    local_records.append(
                        write_teacher_record(
                            output_dir, dataset_index, geometries[0], values
                        )
                    )
                if len(local_records) == 1 or len(local_records) % 100 == 0:
                    print(
                        f"[TEACHER_PROGRESS] rank={runner.rank} "
                        f"processed={len(local_records)} "
                        f"rank_total={(len(runner.dataset) - 1 - runner.rank) // runner.world_size + 1} "
                        f"dataset_index={dataset_index} resumed={existing is not None}",
                        flush=True,
                    )
    finally:
        extractor.close()

    gathered = (
        gather_objects(local_records, runner.context)
        if runner.context
        else [local_records]
    )
    if runner.is_main_process:
        records = [record for rank_records in gathered for record in rank_records]
        expected_ids = [
            str(runner.dataset[index]["id"]) for index in range(len(runner.dataset))
        ]
        manifest_path = finalize_teacher_manifest(
            output_dir,
            records=records,
            expected_sample_ids=expected_ids,
            teacher_heads=teacher_heads,
            checkpoint=checkpoint,
            source_manifest=str(config["source_manifest"]),
        )
        print(
            "[TEACHER_DONE] "
            + json.dumps(
                {"manifest": str(manifest_path), "sample_count": len(records)},
                ensure_ascii=False,
            ),
            flush=True,
        )
    if runner.context:
        barrier(runner.context)
    return manifest_path
