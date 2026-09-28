"""Set-level reference-to-query attention distillation loss."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Sequence

import numpy as np
import torch
import torch.nn.functional as F

from ..registry import AUXILIARY_LOSSES
from .artifacts import FixedTeacherStore, SampleGeometry, sample_geometries
from .selected import Head, SelectedAttentionExtractor, parse_head


@dataclass
class AuxiliaryLossOutput:
    loss: torch.Tensor
    metrics: Dict[str, torch.Tensor]


def nonzero_cyclic_shift(sample_id: str, height: int, width: int, seed: int):
    """Choose one deterministic nonzero same-grid 2D cyclic offset."""
    choices = height * width - 1
    if choices <= 0:
        raise ValueError("cyclic-roll control requires at least two grid cells")
    digest = hashlib.sha256(f"{seed}:{sample_id}".encode("utf-8")).digest()
    flat = int.from_bytes(digest[:8], "big") % choices + 1
    return divmod(flat, width)


def _tensor(value: np.ndarray, like: torch.Tensor) -> torch.Tensor:
    return torch.as_tensor(value, dtype=torch.float32, device=like.device)


@AUXILIARY_LOSSES.register_module()
class ReferenceQueryAttentionDistillation:
    """Distill a fixed Reference Top-3 ensemble into Query Top-5 as a set."""

    treatments = {"baseline", "correct", "cyclic_roll", "gt_mask", "dynamic_teacher"}

    def __init__(
        self,
        wrapper: Any,
        dataset: Any,
        collator: Any,
        treatment: str,
        teacher_manifest: Optional[str],
        teacher_heads: Sequence[Any],
        student_heads: Sequence[Any],
        coefficient: float = 0.1,
        cyclic_roll_seed: int = 20260901,
    ) -> None:
        self.treatment = str(treatment)
        if self.treatment not in self.treatments:
            raise ValueError(f"unknown attention-distillation treatment: {treatment!r}")
        self.coefficient = float(coefficient)
        if not math.isfinite(self.coefficient) or self.coefficient < 0:
            raise ValueError("coefficient must be finite and nonnegative")
        self.teacher_heads = tuple(parse_head(value) for value in teacher_heads)
        self.student_heads = tuple(parse_head(value) for value in student_heads)
        if self.treatment == "gt_mask":
            if not self.student_heads or len(set(self.student_heads)) != len(self.student_heads):
                raise ValueError("gt_mask requires nonempty unique student heads")
        elif len(self.teacher_heads) != 3 or len(self.student_heads) != 5:
            raise ValueError("E009 requires exactly three teacher and five student heads")
        self.cyclic_roll_seed = int(cyclic_roll_seed)
        self.extractor = None
        self.store = None
        self._geometries = None

        base = wrapper.peft_model.get_base_model()
        self.image_token_id = int(base.config.image_token_id)
        self.spatial_merge_size = int(base.config.vision_config.spatial_merge_size)
        if self.treatment != "baseline":
            if self.treatment == "dynamic_teacher":
                # Head IDs stay fixed, but the Reference-head targets are computed
                # from the current model on every batch.  The target tensors are
                # detached in ``compute`` so distillation remains Reference -> Query.
                self.extractor = SelectedAttentionExtractor(
                    wrapper.peft_model, self.teacher_heads + self.student_heads
                )
            elif self.treatment == "gt_mask":
                # GT targets are constructed directly from the current batch.
                # No archived teacher or teacher-head selection is needed.
                self.extractor = SelectedAttentionExtractor(
                    wrapper.peft_model, self.student_heads
                )
            else:
                dataset_ids = [str(dataset[index]["id"]) for index in range(len(dataset))]
                if len(set(dataset_ids)) != len(dataset_ids):
                    raise ValueError("training dataset sample_ids are not unique")
                if not teacher_manifest:
                    raise ValueError(
                        "fixed-teacher treatment requires a teacher manifest"
                    )
                self.store = FixedTeacherStore(
                    teacher_manifest, dataset_ids, self.teacher_heads
                )
                self.extractor = SelectedAttentionExtractor(
                    wrapper.peft_model, self.student_heads
                )

    def begin_batch(
        self, batch: Mapping[str, torch.Tensor], metadata: Sequence[Mapping[str, Any]]
    ) -> None:
        if self.extractor is None:
            return
        self._geometries = sample_geometries(
            batch["input_ids"],
            metadata,
            image_token_id=self.image_token_id,
            spatial_merge_size=self.spatial_merge_size,
        )
        self.extractor.begin()

    def compute(
        self,
        output: Any,
        batch: Mapping[str, torch.Tensor],
        metadata: Sequence[Mapping[str, Any]],
    ) -> AuxiliaryLossOutput:
        if self.extractor is None:
            zero = output.loss.new_zeros(())
            return AuxiliaryLossOutput(
                loss=zero,
                metrics={
                    "auxiliary_loss": zero,
                    "auxiliary_shape_kl": zero,
                    "auxiliary_span_mass": zero,
                    "auxiliary_object_mass": zero,
                },
            )
        geometries = self._geometries
        if geometries is None or len(geometries) != len(metadata):
            raise RuntimeError("attention distillation begin_batch was not called")
        rows = [geometry.prediction_rows for geometry in geometries]
        selected = self.extractor.extract(rows)
        shape_losses = []
        span_losses = []
        object_losses = []
        student_span_masses = []
        student_object_masses = []
        for sample_index, geometry in enumerate(geometries):
            student = self._ensemble_targets(
                selected, sample_index, geometry, self.student_heads
            )
            if self.treatment == "dynamic_teacher":
                online = self._ensemble_targets(
                    selected, sample_index, geometry, self.teacher_heads
                )
                teacher = {key: value.detach() for key, value in online.items()}
            else:
                teacher = self._teacher_targets(geometry, student["distribution"])
            distribution = student["distribution"].clamp_min(1e-12)
            target = teacher["distribution"].clamp_min(1e-12)
            shape_losses.append(
                torch.sum(target * (target.log() - distribution.log()))
            )
            span_losses.append(
                F.smooth_l1_loss(
                    student["reference_span_mass"],
                    teacher["reference_span_mass"],
                )
            )
            object_losses.append(
                F.smooth_l1_loss(
                    student["reference_object_mass"],
                    teacher["reference_object_mass"],
                )
            )
            student_span_masses.append(student["reference_span_mass"])
            student_object_masses.append(student["reference_object_mass"])
        shape = torch.stack(shape_losses).mean()
        span = torch.stack(span_losses).mean()
        object_mass = torch.stack(object_losses).mean()
        unweighted = shape + span + object_mass
        weighted = self.coefficient * unweighted
        values = (shape, span, object_mass, weighted)
        if any(not bool(torch.isfinite(value)) for value in values):
            raise RuntimeError("attention-distillation loss is non-finite")
        return AuxiliaryLossOutput(
            loss=weighted,
            metrics={
                "auxiliary_loss": weighted.detach(),
                "auxiliary_shape_kl": shape.detach(),
                "auxiliary_span_mass": span.detach(),
                "auxiliary_object_mass": object_mass.detach(),
                "student_reference_span_mass": torch.stack(student_span_masses).mean().detach(),
                "student_reference_object_mass": torch.stack(student_object_masses).mean().detach(),
            },
        )

    @staticmethod
    def _ensemble_targets(
        selected: Mapping[Head, Sequence[torch.Tensor]],
        sample_index: int,
        geometry: SampleGeometry,
        heads: Sequence[Head],
    ) -> Dict[str, torch.Tensor]:
        start, stop, _, _ = geometry.reference_span
        normalized = []
        raw_maps = []
        for head in heads:
            raw = selected[head][sample_index][:, start:stop].float().mean(dim=0)
            mass = raw.sum()
            if not bool(torch.isfinite(mass)) or float(mass.detach().item()) <= 0.0:
                raise RuntimeError("student head has nonpositive reference-span mass")
            raw_maps.append(raw)
            normalized.append(raw / mass)
        raw_map = torch.stack(raw_maps).mean(dim=0)
        occupancy = torch.as_tensor(
            geometry.reference_occupancy.reshape(-1),
            dtype=raw_map.dtype,
            device=raw_map.device,
        )
        return {
            "distribution": torch.stack(normalized).mean(dim=0),
            "reference_span_mass": raw_map.sum(),
            "reference_object_mass": (raw_map * occupancy).sum(),
        }

    def _teacher_targets(
        self, geometry: SampleGeometry, like: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        if self.treatment == "gt_mask":
            occupancy = _tensor(geometry.reference_occupancy.reshape(-1), like)
            if not bool(torch.isfinite(occupancy).all()) or float(occupancy.sum()) <= 0:
                raise ValueError("gt_mask requires finite positive reference occupancy")
            distribution = occupancy / occupancy.sum()
            return {
                "distribution": distribution,
                "reference_span_mass": distribution.sum(),
                "reference_object_mass": (distribution * occupancy).sum(),
            }
        assert self.store is not None
        values = self.store.load(geometry)
        distribution = _tensor(values["distribution"].reshape(-1), like)
        raw_map = _tensor(values["raw_reference_map"].reshape(-1), like)
        occupancy = _tensor(values["reference_occupancy"].reshape(-1), like)
        if self.treatment == "cyclic_roll":
            height, width = geometry.reference_span[2:]
            shift = nonzero_cyclic_shift(
                geometry.sample_id, height, width, self.cyclic_roll_seed
            )
            distribution = torch.roll(
                distribution.reshape(height, width), shift, dims=(0, 1)
            ).reshape(-1)
            raw_map = torch.roll(
                raw_map.reshape(height, width), shift, dims=(0, 1)
            ).reshape(-1)
        span_mass = raw_map.sum()
        object_mass = (raw_map * occupancy).sum()
        if self.treatment == "correct":
            archived_span = _tensor(values["reference_span_mass"], like).reshape(())
            archived_object = _tensor(values["reference_object_mass"], like).reshape(())
            if not torch.allclose(span_mass, archived_span, atol=2e-5, rtol=2e-5):
                raise ValueError("archived teacher span mass is inconsistent")
            if not torch.allclose(object_mass, archived_object, atol=2e-5, rtol=2e-5):
                raise ValueError("archived teacher object mass is inconsistent")
        return {
            "distribution": distribution,
            "reference_span_mass": span_mass,
            "reference_object_mass": object_mass,
        }
