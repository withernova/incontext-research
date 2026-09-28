"""Numerical contracts for the real installed Qwen3-VL attention, on tiny CPU models."""
import json
import hashlib
from types import SimpleNamespace

import numpy as np
import pytest
import torch
from PIL import Image

from iploc_szy.compat import ensure_torchvision_nms_schema
from iploc_szy.head_screening.bbox_gradient import (
    BBoxGradientHeadFinder, BBoxGradientAttentionProbe, bbox_loss, gradient_attention, reduce_edges,
    resolve_checkpoint, attach_checkpoint, select_eval_indices,
)
from iploc_szy.head_screening.lasot_screen_manifest import prepare_manifest


def tiny_model():
    ensure_torchvision_nms_schema()
    from transformers.models.qwen3_vl.configuration_qwen3_vl import Qwen3VLTextConfig
    from transformers.models.qwen3_vl.modeling_qwen3_vl import Qwen3VLTextModel
    torch.manual_seed(17)
    config = Qwen3VLTextConfig(vocab_size=32, hidden_size=64, intermediate_size=96,
                             num_hidden_layers=2, num_attention_heads=4,
                             num_key_value_heads=2, head_dim=16,
                             rope_scaling={"rope_type": "default", "mrope_section": [2, 3, 3]})
    config._attn_implementation = "eager"

    class Model(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.config = config
            self.body = Qwen3VLTextModel(config)
            self.lm_head = torch.nn.Linear(64, 32, bias=False)

        def forward(self, ids):
            return self.lm_head(self.body(input_ids=ids, use_cache=False).last_hidden_state)

    return Model().eval().requires_grad_(False)


def test_bbox_ce_uses_pminus1_and_excludes_other_assistant_tokens():
    logits = torch.randn(1, 9, 32, requires_grad=True)
    ids = torch.arange(9).unsqueeze(0)
    loss = bbox_loss(logits, ids, [5, 7])
    expected = torch.nn.functional.cross_entropy(logits[0, [4, 6]], ids[0, [5, 7]])
    torch.testing.assert_close(loss, expected)
    loss.backward()
    assert logits.grad[0, [0, 1, 2, 3, 5, 7, 8]].count_nonzero() == 0
    assert logits.grad[0, [4, 6]].count_nonzero() > 0
    with pytest.raises(ValueError):
        bbox_loss(logits[:, -1:], ids, [5])


def test_absolute_before_sum_and_value_output_gradient_identity():
    attention = torch.tensor([[[0.2, 0.3], [0.4, 0.1]]], requires_grad=True)
    values = torch.tensor([[2., -1.], [-3., 4.]])
    downstream = torch.tensor([[[1., 2.], [-1., 1.]]])
    loss = ((attention @ values) * downstream).sum()
    loss.backward()
    products = attention.detach() * attention.grad
    explicit = ((attention.detach()[..., None] * values) * downstream.unsqueeze(-2)).sum(-1)
    torch.testing.assert_close(products, explicit)
    reduced = reduce_edges(attention.detach(), attention.grad)
    torch.testing.assert_close(reduced[:, 0], products.abs().sum((-2, -1)))
    assert reduced[0, 0] > abs(reduced[0, 1])


def test_real_qwen_gqa_attention_parity_gradients_and_finite_difference():
    model = tiny_model()
    ids = torch.tensor([[1, 2, 3, 4, 5, 6, 7, 8]])
    positions, rows, span = [5, 6, 7], [4, 5, 6], (0, 3)
    with torch.no_grad():
        baseline = model(ids)
    scores = {}
    with gradient_attention(model, rows, span, scores) as layers:
        actual = model(ids)
        torch.testing.assert_close(actual, baseline, atol=0, rtol=0)
        bbox_loss(actual, ids, positions).backward()
    assert layers == 2 and sorted(scores) == [0, 1]
    assert all(score.shape == (4, 4) for score in scores.values())
    assert all(p.grad is None and not p.requires_grad for p in model.parameters())
    signed = torch.stack([scores[i][:, 1] for i in range(layers)])
    layer, head = np.unravel_index(int(signed.abs().argmax()), signed.shape)
    losses = []
    for epsilon in [-0.001, 0.001]:
        with torch.no_grad(), gradient_attention(model, rows, span, {},
                    perturbation=(int(layer), int(head), epsilon), collect=False):
            losses.append(float(bbox_loss(model(ids), ids, positions)))
    finite = (losses[1] - losses[0]) / 0.002
    assert finite == pytest.approx(float(signed[layer, head]), rel=0.015, abs=0.0002)
    with torch.no_grad():
        torch.testing.assert_close(model(ids), baseline, atol=0, rtol=0)


def test_attention_function_restored_after_error():
    model = tiny_model()
    from transformers.models.qwen3_vl import modeling_qwen3_vl as implementation
    original = implementation.eager_attention_forward
    with pytest.raises(RuntimeError, match="deliberate"):
        with gradient_attention(model, [4], (0, 3), {}):
            raise RuntimeError("deliberate")
    assert implementation.eager_attention_forward is original
    assert model.config._attn_implementation == "eager"


def test_finder_equal_sample_weight_and_signed_cancellation(tmp_path):
    records = []
    for i, sign in enumerate([1., -1.]):
        path = tmp_path / f"{i}.npz"
        np.savez(path, absolute=np.array([[4., 1.]]), signed=np.array([[sign * 4, sign]]),
                 positive=np.array([[max(sign, 0) * 4, max(sign, 0)]]),
                 negative_magnitude=np.array([[max(-sign, 0) * 4, max(-sign, 0)]]))
        records.append(dict(artifact=str(path), bbox_ce=1.))
    result = BBoxGradientHeadFinder().find(records)
    first = result["ranking"][0]
    assert first["head"] == 0 and first["absolute"] == 4 and first["signed"] == 0
    assert first["positive"] == first["negative_magnitude"] == 2


def test_manifest_independent_sequences_visibility_and_xywh_conversion(tmp_path):
    root = tmp_path / "data"
    for name in ["cat-1", "cat-2", "dog-1"]:
        sequence = root / name
        (sequence / "img").mkdir(parents=True)
        for i in range(4):
            Image.new("RGB", (20, 20)).save(sequence / "img" / f"{i+1:08d}.jpg")
        (sequence / "groundtruth.txt").write_text("2,3,4,5\n" * 4)
        (sequence / "full_occlusion.txt").write_text("0,1,0,0")
        (sequence / "out_of_view.txt").write_text("0,0,0,0")
    outputs = [tmp_path / "a.json", tmp_path / "b.json"]
    for output in outputs:
        prepare_manifest(root, output, 2, 17)
    assert outputs[0].read_text() == outputs[1].read_text()
    records = json.loads(outputs[0].read_text())
    assert len({r["source"]["sequence_cluster"] for r in records}) == 2
    assert all(r["bbox"] == [[2, 3, 6, 8]] * 2 for r in records)
    assert all(r["source"]["frame_indices_zero_based"] == [0, 2] for r in records)
    with pytest.raises(FileExistsError):
        prepare_manifest(root, outputs[0], 2, 17)


def test_existing_manifest_can_be_larger_than_screening_subset():
    probe = BBoxGradientAttentionProbe(samples=20, seed=17)
    first = probe.sample_indices(1766)
    assert len(first) == len(set(first)) == 20
    assert first == probe.sample_indices(1766)
    assert max(first) >= 20
    with pytest.raises(ValueError):
        probe.sample_indices(19)


def test_adapter_root_resolution_base_check_and_exact_weight_loading(tmp_path, monkeypatch):
    ensure_torchvision_nms_schema()
    from peft import LoraConfig, get_peft_model
    from transformers import AutoProcessor
    base_dir = tmp_path / "base"
    base_dir.mkdir()
    base = tiny_model()
    base.name_or_path = str(base_dir)
    trained = get_peft_model(base, LoraConfig(r=2, lora_alpha=4, target_modules=["q_proj", "v_proj"]))
    with torch.no_grad():
        for name, parameter in trained.named_parameters():
            if "lora_B" in name:
                parameter.fill_(0.125)
    trained.eval()
    run = tmp_path / "run"
    trained.save_pretrained(run / "adapter")
    checkpoint = resolve_checkpoint(run, base_dir)
    direct = resolve_checkpoint(run / "adapter", base_dir)
    assert checkpoint["adapter_path"] == direct["adapter_path"]
    assert resolve_checkpoint(None, base_dir) is None
    with pytest.raises(ValueError, match="base_model"):
        resolve_checkpoint(run, tmp_path / "wrong-base")
    with pytest.raises(FileNotFoundError):
        resolve_checkpoint(tmp_path / "missing", base_dir)
    sentinel = object()
    monkeypatch.setattr(AutoProcessor, "from_pretrained", lambda *a, **k: sentinel)
    loaded = attach_checkpoint(SimpleNamespace(model=tiny_model(), processor=None), checkpoint)
    ids = torch.tensor([[1, 2, 3, 4, 5, 6, 7, 8]])
    with torch.no_grad():
        torch.testing.assert_close(loaded.model(ids), trained(ids), atol=0, rtol=0)
    assert loaded.processor is sentinel
    assert all(not p.requires_grad for p in loaded.model.parameters())
    scores = {}
    with gradient_attention(loaded.model, [4, 5, 6], (0, 3), scores):
        bbox_loss(loaded.model(ids), ids, [5, 6, 7]).backward()
    assert sorted(scores) == [0, 1]


def test_eval_selection_excludes_train_video_and_balances_distinct_sequences(tmp_path):
    def record(dataset, video, frame=1):
        return dict(dataset=dataset, image_path=[f"/images/{dataset}/{video}/{frame}.jpg"])
    train = tmp_path / "train.json"
    train.write_text(json.dumps([record("LaSOT", "seen")]))
    raw = [record("LaSOT", "seen"), record("LaSOT", "unseen", 1),
           record("LaSOT", "unseen", 2), record("GOT10k", "val-1"), record("TAO", "val-1")]
    dataset = [dict(raw=r) for r in raw]
    settings = dict(training_manifest=str(train),
                    training_manifest_sha256=hashlib.sha256(train.read_bytes()).hexdigest(),
                    samples_per_dataset=dict(LaSOT=1, GOT10k=1, TAO=1))
    probe = BBoxGradientAttentionProbe(samples=3, seed=17)
    selected, audit = select_eval_indices(dataset, probe, settings)
    assert len(selected) == 3 and 0 not in selected
    assert len(set(selected) & {1, 2}) == 1
    assert audit["excluded_eval_rows"] == 1
    assert audit["selected_train_sequence_overlap"] == 0
    assert selected == select_eval_indices(dataset, probe, settings)[0]
    train.write_text("[]")
    with pytest.raises(ValueError, match="hash changed"):
        select_eval_indices(dataset, probe, settings)


def test_complete_multimodal_lora_probe_and_ranking(tmp_path):
    """真实小型双图 Qwen3-VL + LoRA，贯通采集、反向、扰动与落盘排名。"""
    ensure_torchvision_nms_schema()
    from transformers import Qwen3VLConfig, Qwen3VLForConditionalGeneration
    from peft import LoraConfig, get_peft_model
    config = Qwen3VLConfig(
        text_config=dict(vocab_size=128, hidden_size=64, intermediate_size=96,
                         num_hidden_layers=2, num_attention_heads=4, num_key_value_heads=2,
                         head_dim=16, rope_scaling={"rope_type": "default", "mrope_section": [2, 3, 3]}),
        vision_config=dict(depth=1, hidden_size=32, intermediate_size=64, num_heads=4,
                           patch_size=2, temporal_patch_size=2, spatial_merge_size=2,
                           out_hidden_size=64, deepstack_visual_indexes=[]),
        image_token_id=98, video_token_id=97, vision_start_token_id=99, vision_end_token_id=100,
    )
    config._attn_implementation = "eager"
    torch.manual_seed(23)
    model = get_peft_model(Qwen3VLForConditionalGeneration(config),
                          LoraConfig(task_type="CAUSAL_LM", r=2, lora_alpha=4,
                                     target_modules=["q_proj", "v_proj"]))
    # 两个图像各4个merged视觉tokens，bbox位于最后3个tokens。
    ids = torch.tensor([[1, 99, 98, 98, 98, 98, 100, 2, 3, 99,
                         98, 98, 98, 98, 100, 4, 5, 6, 7, 8]])
    labels = torch.full_like(ids, -100)
    labels[0, 17:] = ids[0, 17:]
    pixels = torch.randn(32, 24)
    grids = torch.tensor([[1, 4, 4], [1, 4, 4]])

    class Collator:
        processor = SimpleNamespace(tokenizer=SimpleNamespace(convert_tokens_to_ids=lambda name: 98))

        def __call__(self, samples):
            return dict(input_ids=ids.clone(), attention_mask=torch.ones_like(ids),
                        pixel_values=pixels.clone(), image_grid_thw=grids.clone(), labels=labels.clone(),
                        metadata=[dict(bbox_token_positions=[17, 18, 19], image_grid_thw=grids.tolist())])

    dataset = [dict(id="tiny-0", group="tiny", raw=dict(dataset="LaSOT", image_path=["/tiny/video/img/1.jpg"]))]
    runner = SimpleNamespace(dataset=dataset, collator=Collator(), world_size=1,
                             wrapper=SimpleNamespace(model=model, input_device=torch.device("cpu")))
    flags = [p.requires_grad for p in model.parameters()]
    was_training = model.training
    probe = BBoxGradientAttentionProbe(samples=1, seed=23, finite_difference_epsilon=0.01)
    result = probe.collect(runner, 0, tmp_path / "probe")
    assert model.training == was_training
    assert [p.requires_grad for p in model.parameters()] == flags
    assert all(p.grad is None for p in model.parameters())
    record = result["records"][0]
    assert record["prediction_rows"] == [16, 17, 18]
    assert record["query_visual_token_count"] == 4
    assert record["parity_max_abs_logit_error"] == 0
    assert record["finite_difference"]["sign_agreement"]
    ranking = BBoxGradientHeadFinder().find(result["records"])
    assert len(ranking["ranking"]) == 8
    assert ranking["ranking"][0]["absolute"] > 0
    # 同一输入校验会在预检阶段拒绝越界bbox，不需要等到模型前向。
    labels[0, 17] = -100
    with pytest.raises(ValueError, match="supervised"):
        probe.encode_sample(runner, 0)
