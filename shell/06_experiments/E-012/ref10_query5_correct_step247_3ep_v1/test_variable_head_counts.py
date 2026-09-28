from types import SimpleNamespace

import pytest

from iploc_szy.attention_distillation.loss import ReferenceQueryAttentionDistillation
from iploc_szy.attention_distillation.precompute import precompute_fixed_teacher


def _wrapper():
    base = SimpleNamespace(
        config=SimpleNamespace(
            image_token_id=151655,
            vision_config=SimpleNamespace(spatial_merge_size=2),
        )
    )
    peft_model = SimpleNamespace(get_base_model=lambda: base)
    return SimpleNamespace(peft_model=peft_model)


def _heads(count, *, layer=1):
    return [f"L{layer:02d}H{head:02d}" for head in range(count)]


def test_fixed_teacher_loss_accepts_explicit_variable_head_counts():
    loss = ReferenceQueryAttentionDistillation(
        wrapper=_wrapper(),
        dataset=[],
        collator=None,
        treatment="baseline",
        teacher_manifest=None,
        teacher_heads=_heads(10),
        student_heads=_heads(5, layer=2),
        allow_variable_head_counts=True,
    )

    assert len(loss.teacher_heads) == 10
    assert len(loss.student_heads) == 5


def test_fixed_teacher_loss_keeps_legacy_three_by_five_default():
    with pytest.raises(ValueError, match="exactly three teacher and five student heads"):
        ReferenceQueryAttentionDistillation(
            wrapper=_wrapper(),
            dataset=[],
            collator=None,
            treatment="baseline",
            teacher_manifest=None,
            teacher_heads=_heads(10),
            student_heads=_heads(5, layer=2),
        )


def test_variable_head_counts_reject_duplicates_in_loss_and_precompute(tmp_path):
    duplicate_teachers = ["L01H00", "L01H00"]
    with pytest.raises(ValueError, match="nonempty and unique"):
        ReferenceQueryAttentionDistillation(
            wrapper=_wrapper(),
            dataset=[],
            collator=None,
            treatment="baseline",
            teacher_manifest=None,
            teacher_heads=duplicate_teachers,
            student_heads=_heads(5, layer=2),
            allow_variable_head_counts=True,
        )

    with pytest.raises(ValueError, match="nonempty and unique"):
        precompute_fixed_teacher(
            SimpleNamespace(),
            {
                "output_dir": str(tmp_path / "teacher"),
                "checkpoint": str(tmp_path / "checkpoint"),
                "teacher_heads": duplicate_teachers,
                "allow_variable_head_counts": True,
            },
        )
