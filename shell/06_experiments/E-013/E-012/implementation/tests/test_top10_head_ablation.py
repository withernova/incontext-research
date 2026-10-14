"""新入口的独立输入/统计测试；数值 hook 测试需要 PyTorch。"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
from types import ModuleType, SimpleNamespace

import pytest

MODULE = Path(__file__).parents[1] / "iploc_szy/head_screening/top10_head_ablation.py"
module_spec = importlib.util.spec_from_file_location("e012_top10_test", MODULE)
m = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(m)


def test_control_sets_are_reproducible_layer_matched_and_disjoint():
    heads = [(0, h) for h in range(4)] + [(2, h) for h in range(6)]
    actual = m.conditions(heads, 32, [11, 12, 13])
    assert len(actual) == 15
    assert actual == m.conditions(heads, 32, [11, 12, 13])
    for control in actual[-3:]:
        assert len(set(control["heads"])) == 10
        assert not set(control["heads"]) & set(heads)
        assert m.Counter(l for l, _ in control["heads"]) == {0: 4, 2: 6}
    with pytest.raises(ValueError, match="insufficient"):
        m.conditions([(0, h) for h in range(5)], 8, [11])


@pytest.mark.parametrize("heads", [[[0, 0]] * 10, [[0.1, 0]], [[True, 0]], [[36, 0]], [[0, 32]], [[-1, 0]]])
def test_bad_head_spec_fails(heads):
    with pytest.raises(ValueError):
        m.heads_checked(heads, 36, 32)


def test_invalid_outputs_keep_full_iou_denominator():
    base = dict(box=[0, 0, 10, 10], bbox_token_ce=1.0, text="[0,0,10,10]")
    bad = dict(box=None, bbox_token_ce=2.0, text="invalid")
    metrics = m.paired_metrics(base, bad, [0, 0, 10, 10], 1000)
    assert metrics["iou"] == 0 and metrics["delta_iou"] == -1
    assert metrics["invalid_output"] is True
    assert metrics["coordinate_mae_normalized"] is None
    assert metrics["delta_bbox_token_ce"] == 1
    # 只有两侧都有效才计算坐标位移；失效样本仍计入总体 IoU。
    good = dict(box=[5, 0, 15, 10], bbox_token_ce=0.5, text="[5,0,15,10]")
    moved = m.paired_metrics(base, good, [0, 0, 10, 10], 1000)
    assert moved["iou"] == pytest.approx(1 / 3)
    assert moved["coordinate_mae_normalized"] == 0.0025
    records = [dict(dataset="A", condition="x", metrics=metrics), dict(dataset="A", condition="x", metrics=moved)]
    summary = m.summarize(records, ["x"])["x"]["all"]
    assert summary["samples"] == 2
    assert summary["iou_mean"] == pytest.approx(1 / 6)
    assert summary["coordinate_mae_normalized_count"] == 1


@pytest.mark.parametrize("text", ["no box", "[10,0,0,10]", "[-1,0,10,10]", "[0,0,1001,10]",
                                   "[0,0,0,10]", "[0,0,10,10] [1,1,2,2]", "[nan,0,1,1]", "[0,0,10,10)"])
def test_invalid_bbox_is_not_clipped_or_repaired(text):
    assert m.parse_generated_box(text, 1000) is None


def test_valid_bbox_parser():
    assert m.parse_generated_box("<box>(0, 2, 300, 400)</box>", 1000) == [0, 2, 300, 400]


def test_empty_hook_parity_is_teacher_forced_only():
    source = MODULE.read_text()
    assert "empty hook changes greedy generated tokens" not in source
    assert "empty_hook_teacher_forced_logit_parity_passed=True" in source


def frozen_fixture(tmp_path):
    def save(name, value):
        path = tmp_path / name
        data = value.encode() if isinstance(value, str) else json.dumps(value).encode()
        path.write_bytes(data)
        return str(path), hashlib.sha256(data).hexdigest()
    ranking = dict(schema="iploc-szy.bbox-gradient-ranking/v1", status="completed", ranking=[])
    cfg_path, cfg_hash = save("runtime.py", "model = {}\n")
    samples_path, samples_hash = save("samples.json", dict(schema="iploc-szy.head-ablation-samples/v1",
        coordinate_scale=1000, target_box_source="annotation", samples=[
            dict(dataset_index=7, dataset="LaSOT", sample_id="sample7", target_box=[0, 0, 10, 10])]))
    # 每层留足 10 个非 candidate heads，方便同层随机抽样。
    ranking["ranking"] = [dict(layer=l, head=h, absolute=100 - (l * 32 + h), rank=l * 32 + h + 1)
                          for l in range(2) for h in range(32)]
    rank_path, rank_hash = save("ranking.json", ranking)
    return dict(source_run_id="E-012/R-001", ranking_metric="bbox_grad_abs_contrib_mean",
                heads=[[0, h] for h in range(10)], num_layers=2, num_heads=32,
                random_seeds=[1, 2, 3], coordinate_scale=1000, max_sequence_tokens=2048, max_new_tokens=128,
                parity_atol=0.0, parity_rtol=0.0, ranking_path=rank_path, ranking_sha256=rank_hash,
                runtime_config=cfg_path, runtime_config_sha256=cfg_hash,
                input_manifest_sha256="a" * 64, samples_path=samples_path, samples_sha256=samples_hash,
                output_dir=str(tmp_path / "new_output"))


def test_frozen_contract_and_missing_inputs_do_not_create_output(tmp_path):
    spec = frozen_fixture(tmp_path)
    plan, snapshots = m.validate_spec(spec)
    assert len(plan["conditions"]) == 15 and len(plan["samples"]) == 1
    assert len(snapshots) == 3 and not Path(spec["output_dir"]).exists()
    spec["heads"] = []
    with pytest.raises(ValueError, match="unresolved run inputs.*heads"):
        m.validate_spec(spec)


def test_head_list_must_match_ranked_top10_and_hash(tmp_path):
    spec = frozen_fixture(tmp_path)
    spec["heads"][-1] = [1, 0]
    with pytest.raises(ValueError, match="Top-10"):
        m.validate_spec(spec)
    spec["heads"][-1] = [0, 9]
    Path(spec["ranking_path"]).write_text("{}")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        m.validate_spec(spec)


def test_source_run_contract_resolves_ranking_and_rejects_manifest_drift(tmp_path):
    source = tmp_path / "R-001"
    source.mkdir()
    manifest = tmp_path / "manifest.json"
    manifest.write_text("[]")
    manifest_hash = hashlib.sha256(manifest.read_bytes()).hexdigest()
    ranking = [dict(layer=l, head=h, absolute=200 - (l * 32 + h), rank=l * 32 + h + 1)
               for l in range(2) for h in range(32)]
    config = dict(work_dir=str(source), model=dict(attn_implementation="eager"), checkpoint_path="/fixed/adapter",
                  screen_dataloader=dict(dataset=dict(ann_file=str(manifest), normalized_scale=1000),
                                         collator=dict(assistant_only=True)))
    frozen = dict(config=config, manifests_sha256={str(manifest): manifest_hash}, selected_indices=[0, 1, 2])
    (source / "frozen_input.json").write_text(json.dumps(frozen))
    (source / "summary.json").write_text(json.dumps(dict(schema="iploc-szy.bbox-gradient-ranking/v1",
                                             status="completed", ranking=ranking)))
    spec = dict(source_run_id="E-012/R-001", ranking_metric="bbox_grad_abs_contrib_mean", source_run_dir=str(source),
                output_dir=str(tmp_path / "output"), samples_per_dataset=dict(LaSOT=1), num_layers=2, num_heads=32,
                random_seeds=[1, 2, 3], coordinate_scale=1000, max_sequence_tokens=2048, max_new_tokens=128,
                parity_atol=0.0, parity_rtol=0.0)
    plan, snapshots = m.validate_spec(spec)
    assert plan["sample_count"] == 1
    assert plan["conditions"][1]["heads"] == [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9)]
    assert set(snapshots) == {"r001_frozen_input_snapshot.json", "r001_summary_snapshot.json", "r001_manifest_sha256.txt", "resolved_r001_config.json"}
    manifest.write_text("changed")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        m.validate_spec(spec)


def test_source_run_can_parse_hashed_legacy_fixed5_config(tmp_path):
    source = tmp_path / "R-001"
    source.mkdir()
    manifest = tmp_path / "manifest.json"
    manifest.write_text("[]")
    legacy = tmp_path / "legacy_e009.py"
    legacy.write_text("runtime = {'runner': {'auxiliary_loss': {'student_heads': ('L01H02', 'L03H04')}}}\n")
    ranking = [dict(layer=l, head=h, absolute=200 - (l * 32 + h), rank=l * 32 + h + 1)
               for l in range(4) for h in range(32)]
    frozen = dict(config=dict(work_dir=str(source), model=dict(attn_implementation="eager"), checkpoint_path="/fixed/adapter",
        screen_dataloader=dict(dataset=dict(ann_file=str(manifest), normalized_scale=1000), collator=dict(assistant_only=True))),
        manifests_sha256={str(manifest): hashlib.sha256(manifest.read_bytes()).hexdigest()}, selected_indices=[0])
    (source / "frozen_input.json").write_text(json.dumps(frozen))
    (source / "summary.json").write_text(json.dumps(dict(schema="iploc-szy.bbox-gradient-ranking/v1", status="completed", ranking=ranking)))
    spec = dict(source_run_id="E-012/R-001", ranking_metric="bbox_grad_abs_contrib_mean", source_run_dir=str(source),
                output_dir=str(tmp_path / "output"), samples_per_dataset=dict(LaSOT=1), num_layers=4, num_heads=32,
                random_seeds=[1, 2, 3], coordinate_scale=1000, max_sequence_tokens=2048, max_new_tokens=128,
                parity_atol=0.0, parity_rtol=0.0,
                legacy_head_source=dict(config_path=str(legacy), config_sha256=hashlib.sha256(legacy.read_bytes()).hexdigest(), field="student_heads"))
    plan, snapshots = m.validate_spec(spec)
    assert plan["source"]["candidate_selection"]["heads"] == ["L01H02", "L03H04"]
    assert plan["conditions"][1]["heads"] == [(1, 2), (3, 4)]
    assert snapshots["legacy_e009_head_config.py"] == legacy.read_bytes()
    spec["combine_r001_top10_with_legacy"] = True
    union_plan, _ = m.validate_spec(spec)
    assert [row["name"] for row in union_plan["conditions"]] == [
        "baseline", "r001_top10_joint", "e009_fixed5_joint", "new_old_union15_joint",
        "random_seed_1", "random_seed_2", "random_seed_3",
    ]
    assert len(union_plan["conditions"][3]["heads"]) == 12
    legacy.write_text("changed")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        m.validate_spec(spec)


def test_cli_static_preflight_and_existing_output_rejection(tmp_path):
    spec = frozen_fixture(tmp_path)
    config = tmp_path / "proposal.py"
    config.write_text("run_spec = " + repr(spec) + "\n")
    result = subprocess.run([sys.executable, str(MODULE), str(config), "--validate-only"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["model_runtime_checked"] is False
    assert not Path(spec["output_dir"]).exists()
    Path(spec["output_dir"]).mkdir()
    with pytest.raises(ValueError, match="refusing overwrite"):
        m.validate_spec(spec)


def test_missing_source_stops_before_model_import(tmp_path):
    config = tmp_path / "missing_source.py"
    config.write_text("run_spec = " + repr(dict(source_run_id="E-012/R-001", ranking_metric="bbox_grad_abs_contrib_mean",
        source_run_dir=str(tmp_path / "missing"), output_dir=str(tmp_path / "output"), samples_per_dataset=dict(LaSOT=1),
        num_layers=36, num_heads=32, random_seeds=[1, 2, 3], coordinate_scale=1000,
        max_sequence_tokens=2048, max_new_tokens=128, parity_atol=0.0, parity_rtol=0.0)) + "\n")
    result = subprocess.run([sys.executable, str(MODULE), str(config), "--validate-only"], capture_output=True, text=True)
    assert result.returncode != 0
    assert "source run must contain frozen_input.json and summary.json" in result.stderr
    assert "ModuleNotFoundError" not in result.stderr


def test_prompt_truncation_removes_all_gt_and_rejects_leakage():
    torch = pytest.importorskip("torch")
    ids = torch.arange(12).reshape(1, -1)
    labels = torch.full_like(ids, -100)
    labels[0, 8:] = ids[0, 8:]
    tokenizer = SimpleNamespace(decode=lambda tokens, **kw: "prompt<|im_start|>assistant\n" if tokens == list(range(8)) else "bad boundary")
    encoded = dict(input_ids=ids, attention_mask=torch.ones_like(ids), pixel_values=torch.ones(3, 4),
                   image_grid_thw=torch.tensor([[1, 2, 2], [1, 2, 2]]))
    prefix, length = m.generation_prefix(encoded, labels, tokenizer, [(1, 3), (4, 6)])
    assert length == 8 and prefix["input_ids"].tolist() == [list(range(8))]
    assert prefix["attention_mask"].shape == (1, 8)
    assert prefix["pixel_values"] is encoded["pixel_values"]
    labels[0, 5] = 5
    with pytest.raises(ValueError, match="both complete images"):
        m.generation_prefix(encoded, labels, tokenizer, [(1, 3), (4, 6)])


def test_hook_gqa_prefill_decode_untouched_heads_and_exception_cleanup(monkeypatch):
    torch = pytest.importorskip("torch")
    # 用真实 torch 的 GQA attention 数值路径，替代 heavyweight transformers import。
    impl = ModuleType("transformers.models.qwen3_vl.modeling_qwen3_vl")
    def repeat_kv(x, groups):
        return x.repeat_interleave(groups, dim=1)
    def eager(module, q, k, v, mask, scaling, dropout=0, **kwargs):
        a = torch.softmax(q @ repeat_kv(k, module.num_key_value_groups).transpose(-1, -2) * scaling + mask, -1)
        return (a @ repeat_kv(v, module.num_key_value_groups)).transpose(1, 2).contiguous(), a
    impl.repeat_kv, impl.eager_attention_forward = repeat_kv, eager
    package = ModuleType("transformers.models.qwen3_vl")
    package.modeling_qwen3_vl = impl
    monkeypatch.setitem(sys.modules, "transformers.models.qwen3_vl", package)
    module_cls = type("Qwen3VLTextAttention", (), {})
    attention_module = module_cls()
    attention_module.layer_idx = 0
    attention_module.num_key_value_groups = 2
    attention_module.config = SimpleNamespace(_attn_implementation="eager")
    model = SimpleNamespace(training=False, modules=lambda: [attention_module])
    torch.manual_seed(17)
    hook = m.WholeHeadZeroHook([(0, 1)])
    with hook.installed(model):
        for query_length, key_length in [(5, 5), (1, 6), (1, 7)]:
            q, k, v = torch.randn(1, 4, query_length, 3), torch.randn(1, 2, key_length, 3), torch.randn(1, 2, key_length, 3)
            mask = torch.zeros(1, 1, query_length, key_length)
            clean, clean_a = eager(attention_module, q, k, v, mask, 0.5)
            actual, a = impl.eager_attention_forward(attention_module, q, k, v, mask, 0.5)
            assert torch.count_nonzero(actual[:, :, 1]) == 0 and torch.count_nonzero(a[:, 1]) == 0
            torch.testing.assert_close(actual[:, :, [0, 2, 3]], clean[:, :, [0, 2, 3]], atol=0, rtol=0)
            torch.testing.assert_close(a[:, [0, 2, 3]], clean_a[:, [0, 2, 3]], atol=0, rtol=0)
    hook.validate(3, 1)
    assert hook.audits["L00H01"]["decode_calls"] == 2
    assert impl.eager_attention_forward is eager
    with pytest.raises(RuntimeError, match="test failure"):
        with m.WholeHeadZeroHook([]).installed(model):
            raise RuntimeError("test failure")
    assert impl.eager_attention_forward is eager
