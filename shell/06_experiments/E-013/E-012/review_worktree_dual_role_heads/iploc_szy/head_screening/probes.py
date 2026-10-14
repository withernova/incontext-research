"""Isolated teacher-forced dual-span attention probe for head screening."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager, nullcontext
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

import numpy as np
import torch

from ..prompting.coordinates import parse_box
from ..registry import HEAD_PROBES
from .metrics import normalized_box_occupancy
from .dual_role_metrics import (
    coordinate_prediction_rows,
    coordinate_target_positions,
    validate_coordinate_positions,
)


def consecutive_spans(token_ids: Sequence[int], token_id: int) -> List[Tuple[int, int]]:
    positions = [index for index, value in enumerate(token_ids) if value == token_id]
    if not positions:
        return []
    spans = []
    start = previous = positions[0]
    for position in positions[1:]:
        if position != previous + 1:
            spans.append((start, previous + 1))
            start = position
        previous = position
    spans.append((start, previous + 1))
    return spans


def unique_subsequence(
    tokens: Sequence[int], needle: Sequence[int], start: int, stop: int
) -> List[int]:
    matches = [
        index
        for index in range(start, stop - len(needle) + 1)
        if list(tokens[index : index + len(needle)]) == list(needle)
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one bbox token alignment, found {matches}")
    return list(range(matches[0], matches[0] + len(needle)))


def _attention_configs(model: torch.nn.Module) -> List[Any]:
    candidates = []
    base = model.get_base_model() if hasattr(model, "get_base_model") else model
    for value in (getattr(base, "config", None), getattr(getattr(base, "config", None), "text_config", None)):
        if value is not None and all(id(value) != id(item) for item in candidates):
            candidates.append(value)
    for module in base.modules():
        value = getattr(module, "config", None)
        if value is not None and all(id(value) != id(item) for item in candidates):
            candidates.append(value)
    return candidates


@contextmanager
def temporary_eager_attention(model: torch.nn.Module):
    """Switch only the probe forward to eager attention, then restore SDPA."""
    snapshots = []
    for config in _attention_configs(model):
        if hasattr(config, "_attn_implementation_internal"):
            snapshots.append((config, config._attn_implementation_internal))
            config._attn_implementation_internal = "eager"
    if not snapshots:
        raise RuntimeError("could not locate a mutable attention implementation config")
    try:
        yield
    finally:
        for config, value in snapshots:
            config._attn_implementation_internal = value


@HEAD_PROBES.register_module()
class TeacherForcedDualSpanAttentionProbe:
    """Extract Qbbox p-1 to query/reference maps from deterministic train samples.

    This probe intentionally uses the ground-truth assistant suffix already
    present in SFT batches.  Its row contract is therefore different from the
    natural-response replay used by E010-R003.
    """

    schema = "iploc-szy.teacher-forced-dual-span-probe/v1"

    def __init__(
        self,
        samples_per_screening: int = 20,
        seed: int = 20260901,
        require_reference_count: int = 1,
        artifact_dtype: str = "float16",
        attention_mode: str = "eager",
    ) -> None:
        if attention_mode not in ("eager", "selected"):
            raise ValueError("attention_mode must be eager or selected")
        self.attention_mode = attention_mode
        self.samples_per_screening = int(samples_per_screening)
        self.seed = int(seed)
        self.require_reference_count = int(require_reference_count)
        if self.samples_per_screening <= 0 or self.require_reference_count <= 0:
            raise ValueError("probe sample/reference counts must be positive")
        if artifact_dtype not in {"float16", "float32"}:
            raise ValueError("artifact_dtype must be float16 or float32")
        self.artifact_dtype = np.dtype(artifact_dtype)

    def sample_indices(self, dataset_size: int, screening_index: int) -> List[int]:
        if self.samples_per_screening > dataset_size:
            raise ValueError("samples_per_screening exceeds dataset size")
        rng = np.random.default_rng(self.seed + int(screening_index))
        return sorted(
            map(
                int,
                rng.choice(dataset_size, self.samples_per_screening, replace=False),
            )
        )

    def collect(
        self,
        runner: Any,
        screening_index: int,
        screen_dir: Path,
    ) -> Dict[str, Any]:
        indices = self.sample_indices(len(runner.dataset), screening_index)
        local_indices = indices[runner.rank :: runner.world_size]
        rank_dir = Path(screen_dir) / "probe" / f"rank_{runner.rank:02d}"
        rank_dir.mkdir(parents=True, exist_ok=True)
        model = runner.wrapper.peft_model
        was_training = bool(model.training)
        records = []
        failures = []
        model.eval()
        try:
            attention_context = temporary_eager_attention(model) if self.attention_mode == "eager" else nullcontext()
            with attention_context, torch.inference_mode():
                for dataset_index in local_indices:
                    try:
                        records.append(
                            self._collect_one(
                                runner,
                                model,
                                dataset_index,
                                rank_dir,
                            )
                        )
                    except Exception as exc:
                        failures.append(
                            {
                                "dataset_index": dataset_index,
                                "reason": f"{type(exc).__name__}: {exc}",
                            }
                        )
                    if (len(records) + len(failures)) % 10 == 0:
                        print(f"[HEAD_SCREEN_PROGRESS] rank={runner.rank} "
                              f"done={len(records)+len(failures)}/{len(local_indices)} "
                              f"failures={len(failures)}", flush=True)
        finally:
            model.train(was_training)
        manifest = {
            "schema": self.schema,
            "rank": runner.rank,
            "screening_index": int(screening_index),
            "global_indices": indices,
            "local_indices": local_indices,
            "row_contract": "teacher_forced_query_bbox_pminus1/v1",
            "records": records,
            "failures": failures,
        }
        path = rank_dir / "records.json"
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, path)
        return manifest

    def _collect_one(
        self,
        runner: Any,
        model: torch.nn.Module,
        dataset_index: int,
        rank_dir: Path,
    ) -> Dict[str, Any]:
        sample = runner.dataset[dataset_index]
        encoded = runner.collator([sample])
        metadata = encoded.pop("metadata")[0]
        input_ids_cpu = encoded["input_ids"][0].tolist()
        labels_cpu = encoded["labels"][0]
        supervised = labels_cpu.ne(-100).nonzero(as_tuple=False).flatten().tolist()
        if not supervised:
            raise ValueError("probe sample has no supervised answer tokens")

        tokenizer = runner.collator.processor.tokenizer
        coordinate_positions = validate_coordinate_positions(
            input_ids_cpu,
            labels_cpu.tolist(),
            metadata["coordinate_token_positions"],
        )
        bbox_positions = list(coordinate_target_positions(coordinate_positions))
        if not bbox_positions or not set(bbox_positions).issubset(supervised):
            raise ValueError("coordinate positions are outside the supervised suffix")
        prediction_rows = list(coordinate_prediction_rows(coordinate_positions))

        image_token_id = int(tokenizer.convert_tokens_to_ids("<|image_pad|>"))
        spans = consecutive_spans(input_ids_cpu, image_token_id)
        grids = metadata.get("image_grid_thw")
        if grids is None or len(spans) != len(grids):
            raise ValueError("image token spans do not match image_grid_thw")
        reference_count = len(spans) - 1
        if reference_count != self.require_reference_count:
            raise ValueError(
                f"probe requires {self.require_reference_count} reference image(s), "
                f"got {reference_count}"
            )

        base = model.get_base_model() if hasattr(model, "get_base_model") else model
        merge = int(base.config.vision_config.spatial_merge_size)
        shaped_spans = []
        for span, grid in zip(spans, grids):
            temporal, height, width = map(int, grid)
            if temporal != 1 or height % merge or width % merge:
                raise ValueError("probe only supports one-frame divisible image grids")
            merged_h, merged_w = height // merge, width // merge
            if span[1] - span[0] != merged_h * merged_w:
                raise ValueError("image span length does not equal merged token grid")
            shaped_spans.append((span[0], span[1], merged_h, merged_w))

        forward = {
            key: value.to(runner.wrapper.input_device)
            for key, value in encoded.items()
            if key != "labels"
        }
        forward.update(
            output_attentions=True,
            return_dict=True,
            use_cache=False,
            logits_to_keep=1,
        )
        reference_span = shaped_spans[0]
        query_span = shaped_spans[-1]
        if self.attention_mode == "selected":
            from ..evaluation.auto_query_heads import selected_probe_maps
            q_to_r, q_to_q = selected_probe_maps(
                model, forward, prediction_rows, [reference_span, query_span])
            head_shape = list(q_to_q.shape[:2])
        else:
            output = model(**forward)
            attentions = output.attentions
            if not attentions or any(value is None for value in attentions):
                raise RuntimeError(
                    "model returned no attention matrices; eager probe switching is unsupported")
            q_to_r = self._maps(attentions, prediction_rows, reference_span)
            q_to_q = self._maps(attentions, prediction_rows, query_span)
            head_shape = [len(attentions), int(attentions[0].shape[1])]
        reference_box = parse_box(metadata["reference_answers"][0])
        query_box = parse_box(metadata["query_answer"])
        if reference_box is None or query_box is None:
            raise ValueError("probe metadata contains an invalid normalized box")
        reference_target = normalized_box_occupancy(
            reference_box, reference_span[2], reference_span[3]
        )
        query_target = normalized_box_occupancy(
            query_box, query_span[2], query_span[3]
        )

        artifact = rank_dir / f"sample_{dataset_index:06d}.npz"
        temporary_artifact = artifact.with_suffix(".tmp.npz")
        np.savez_compressed(
            temporary_artifact,
            q_to_q=q_to_q.astype(self.artifact_dtype),
            q_to_r=q_to_r.astype(self.artifact_dtype),
            query_target=query_target.astype(np.float32),
            reference_target=reference_target.astype(np.float32),
        )
        os.replace(temporary_artifact, artifact)
        return {
            "dataset_index": int(dataset_index),
            "sample_id": metadata["id"],
            "group": metadata["group"],
            "artifact": str(artifact),
            "bbox_token_positions": bbox_positions,
            "coordinate_token_positions": {
                field: list(positions) for field, positions in coordinate_positions.items()
            },
            "prediction_rows": prediction_rows,
            "spans": {
                "reference": list(reference_span),
                "query": list(query_span),
            },
            "head_shape": head_shape,
        }

    @staticmethod
    def _maps(
        attentions: Iterable[torch.Tensor],
        rows: Sequence[int],
        span: Tuple[int, int, int, int],
    ) -> np.ndarray:
        start, stop, height, width = span
        maps = []
        for attention in attentions:
            value = (
                attention[0, :, rows, start:stop]
                .float()
                .mean(dim=1)
                .detach()
                .cpu()
                .numpy()
            )
            maps.append(value.reshape(value.shape[0], height, width))
        return np.stack(maps, axis=0)
