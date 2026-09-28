from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from iploc_szy.attention_distillation.artifacts import (
    FixedTeacherStore,
    SampleGeometry,
    ensemble_teacher,
    finalize_teacher_manifest,
    load_teacher_record,
    write_teacher_record,
)
from iploc_szy.attention_distillation.loss import (
    AuxiliaryLossOutput,
    ReferenceQueryAttentionDistillation,
    nonzero_cyclic_shift,
)
from iploc_szy.attention_distillation.selected import selected_attention_from_layer
from iploc_szy.compat import ensure_torchvision_nms_schema
from iploc_szy.engine.runner import SFTLoRARunner


def _qwen_layer():
    ensure_torchvision_nms_schema()
    from transformers.models.qwen3_vl.modeling_qwen3_vl import (
        Qwen3VLTextConfig,
        Qwen3VLTextDecoderLayer,
        Qwen3VLTextRotaryEmbedding,
    )

    config = Qwen3VLTextConfig(
        vocab_size=64,
        hidden_size=32,
        intermediate_size=64,
        num_hidden_layers=1,
        num_attention_heads=4,
        num_key_value_heads=2,
        head_dim=8,
        max_position_embeddings=64,
        attention_dropout=0.0,
        rope_scaling={"rope_type": "default", "mrope_section": [2, 1, 1]},
        _attn_implementation="eager",
    )
    return Qwen3VLTextDecoderLayer(config, 0), Qwen3VLTextRotaryEmbedding(config)


def test_selected_attention_matches_installed_qwen3vl_eager_and_is_differentiable():
    torch.manual_seed(9)
    layer, rotary = _qwen_layer()
    layer.eval()
    hidden = torch.randn(2, 7, 32, requires_grad=True)
    position_ids = torch.arange(7).view(1, 1, 7).expand(3, 2, 7)
    position_embeddings = rotary(hidden, position_ids)
    mask = torch.zeros(2, 1, 7, 7)
    mask.masked_fill_(
        torch.triu(torch.ones(7, 7, dtype=torch.bool), diagonal=1),
        float("-inf"),
    )
    normalized = layer.input_layernorm(hidden)
    _, eager = layer.self_attn(
        normalized,
        position_embeddings=position_embeddings,
        attention_mask=mask,
    )
    rows = [[3, 5], [2, 6]]
    selected = selected_attention_from_layer(
        layer, hidden, position_embeddings, mask, rows, heads=[1, 3]
    )
    for head in (1, 3):
        for batch_index in range(2):
            torch.testing.assert_close(
                selected[head][batch_index],
                eager[batch_index, head, rows[batch_index]],
                atol=1e-6,
                rtol=1e-6,
            )
    selected[1][0][:, :3].sum().backward()
    assert layer.self_attn.q_proj.weight.grad is not None
    assert layer.self_attn.k_proj.weight.grad is not None
    assert bool(torch.isfinite(hidden.grad).all())


def test_selected_attention_materializes_sdpa_causality_when_mask_is_none():
    torch.manual_seed(10)
    layer, rotary = _qwen_layer()
    layer.eval()
    hidden = torch.randn(2, 7, 32)
    position_ids = torch.arange(7).view(1, 1, 7).expand(3, 2, 7)
    position_embeddings = rotary(hidden, position_ids)
    explicit_mask = torch.zeros(2, 1, 7, 7)
    explicit_mask.masked_fill_(
        torch.triu(torch.ones(7, 7, dtype=torch.bool), diagonal=1),
        float("-inf"),
    )
    rows = [[1, 5], [2, 6]]
    explicit = selected_attention_from_layer(
        layer, hidden, position_embeddings, explicit_mask, rows, heads=[1, 3]
    )
    implicit = selected_attention_from_layer(
        layer, hidden, position_embeddings, None, rows, heads=[1, 3]
    )
    for head in (1, 3):
        for batch_index in range(2):
            torch.testing.assert_close(
                implicit[head][batch_index],
                explicit[head][batch_index],
                atol=1e-6,
                rtol=1e-6,
            )
            for row_index, query_row in enumerate(rows[batch_index]):
                assert torch.count_nonzero(
                    implicit[head][batch_index][row_index, query_row + 1 :]
                ) == 0


def _geometry(sample_id="s0"):
    occupancy = np.asarray([[1.0, 0.5], [0.0, 0.0]], dtype=np.float32)
    return SampleGeometry(
        sample_id=sample_id,
        bbox_token_positions=(9, 10),
        prediction_rows=(8, 9),
        reference_span=(1, 5, 2, 2),
        query_span=(5, 9, 2, 2),
        reference_grid_thw=(1, 4, 4),
        query_grid_thw=(1, 4, 4),
        reference_occupancy=occupancy,
    )


def test_teacher_averages_rows_then_normalizes_each_head_equally():
    heads = ((20, 15), (20, 20), (14, 23))
    maps = (
        torch.tensor([[0.0, 1.0, 1.0, 2.0, 0.0, 0.0], [0.0, 3.0, 1.0, 0.0, 0.0, 0.0]]),
        torch.tensor([[0.0, 8.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]),
        torch.tensor([[0.0, 1.0, 2.0, 3.0, 4.0, 0.0], [0.0, 1.0, 2.0, 3.0, 4.0, 0.0]]),
    )
    selected = {head: [value] for head, value in zip(heads, maps)}
    values = ensemble_teacher(selected, 0, _geometry(), heads)
    per_head = []
    raw = []
    for value in maps:
        head_raw = value[:, 1:5].mean(0)
        raw.append(head_raw)
        per_head.append(head_raw / head_raw.sum())
    torch.testing.assert_close(
        torch.from_numpy(values["distribution"]).reshape(-1),
        torch.stack(per_head).mean(0),
    )
    torch.testing.assert_close(
        torch.from_numpy(values["raw_reference_map"]).reshape(-1),
        torch.stack(raw).mean(0),
    )


def test_teacher_store_is_one_to_one_hashed_and_geometry_fail_closed(tmp_path: Path):
    root = tmp_path / "teacher"
    root.mkdir()
    heads = ((20, 15), (20, 20), (14, 23))
    records = []
    for index, sample_id in enumerate(("s0", "s1")):
        geometry = _geometry(sample_id)
        raw = np.asarray([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
        values = {
            "distribution": raw / raw.sum(),
            "raw_reference_map": raw,
            "reference_occupancy": geometry.reference_occupancy,
            "reference_span_mass": np.asarray(raw.sum(), dtype=np.float32),
            "reference_object_mass": np.asarray(
                (raw * geometry.reference_occupancy).sum(), dtype=np.float32
            ),
        }
        records.append(write_teacher_record(root, index, geometry, values))
        resumed = load_teacher_record(root, index, geometry)
        assert resumed is not None
        assert resumed["dataset_index"] == index
        assert resumed["sample_id"] == sample_id
        assert resumed["artifact_sha256"] == records[-1]["artifact_sha256"]
    assert load_teacher_record(root, 2, _geometry("s2")) is None
    manifest = finalize_teacher_manifest(
        root,
        records=records,
        expected_sample_ids=["s0", "s1"],
        teacher_heads=heads,
        checkpoint="checkpoint",
        source_manifest="train.json",
    )
    store = FixedTeacherStore(str(manifest), ["s0", "s1"], heads)
    assert np.isclose(store.load(_geometry("s0"))["distribution"].sum(), 1.0)
    bad = _geometry("s0")
    object.__setattr__(bad, "prediction_rows", (7, 8))
    with pytest.raises(ValueError, match="geometry mismatch"):
        store.load(bad)
    assert nonzero_cyclic_shift("s0", 2, 2, 20260901) != (0, 0)


def test_runner_adds_auxiliary_before_gradient_accumulation_scaling():
    parameter = torch.tensor(2.0, requires_grad=True)

    class Model:
        def __call__(self, **batch):
            return SimpleNamespace(loss=parameter.square(), logits=torch.zeros(1, 2, 2))

    class Auxiliary:
        def begin_batch(self, batch, metadata):
            self.began = True

        def compute(self, output, batch, metadata):
            value = 0.1 * parameter
            return AuxiliaryLossOutput(value, {"auxiliary_loss": value.detach()})

    runner = object.__new__(SFTLoRARunner)
    runner.model = Model()
    runner.assistant_only_logits = False
    runner.auxiliary_loss = Auxiliary()
    _, _, total, metrics = runner._loss_forward({"labels": torch.ones(1, 2)}, [{}])
    for _ in range(4):
        (total / 4).backward(retain_graph=True)
    assert total.item() == pytest.approx(4.2)
    assert parameter.grad.item() == pytest.approx(4.1)
    assert metrics["sft_loss"] == pytest.approx(4.0)
    assert metrics["total_loss"] == pytest.approx(4.2)



def test_dynamic_teacher_is_online_detached_and_student_is_differentiable():
    geometry = _geometry()
    teacher_heads = ((20, 15), (20, 20), (14, 23))
    student_heads = ((21, 10), (17, 4), (17, 7), (24, 16), (18, 15))
    teacher_values = [
        torch.full((2, 9), 0.02 * (index + 1), requires_grad=True)
        for index in range(3)
    ]
    student_values = [
        torch.full((2, 9), 0.03 * (index + 1), requires_grad=True)
        for index in range(5)
    ]
    selected = {
        head: [value]
        for head, value in zip(
            teacher_heads + student_heads, teacher_values + student_values
        )
    }

    class Extractor:
        def extract(self, rows):
            assert rows == [geometry.prediction_rows]
            return selected

    loss = object.__new__(ReferenceQueryAttentionDistillation)
    loss.treatment = "dynamic_teacher"
    loss.coefficient = 0.1
    loss.teacher_heads = teacher_heads
    loss.student_heads = student_heads
    loss.extractor = Extractor()
    loss.store = None
    loss._geometries = [geometry]
    output = SimpleNamespace(loss=torch.tensor(0.0, requires_grad=True))
    result = loss.compute(output, {}, [{}])
    result.loss.backward()

    assert result.loss.item() > 0.0
    assert all(value.grad is None for value in teacher_values)
    assert all(value.grad is not None for value in student_values)
    assert all(bool(torch.isfinite(value.grad).all()) for value in student_values)
