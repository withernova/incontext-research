"""CPU checks against the installed Qwen3-VL attention, without dataset/model weights."""
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch

from iploc_szy.compat import ensure_torchvision_nms_schema
from iploc_szy.branching import load_experiment_config
from iploc_szy.evaluation.query_attention import (
    QueryAttentionHook, query_geometry, validate_settings, validate_run_config,
)

ensure_torchvision_nms_schema()
from transformers.models.qwen3_vl.modeling_qwen3_vl import Qwen3VLTextAttention
from transformers.models.qwen3_vl.configuration_qwen3_vl import Qwen3VLTextConfig
from transformers.cache_utils import DynamicCache


def fixture(impl="eager"):
    torch.manual_seed(13)
    config = Qwen3VLTextConfig(hidden_size=32, intermediate_size=64,
        num_hidden_layers=1, num_attention_heads=4, num_key_value_heads=2,
        head_dim=8, attention_dropout=0.0)
    config._attn_implementation = impl
    model = torch.nn.Module()
    model.attn = Qwen3VLTextAttention(config, layer_idx=0).eval()
    geometry = dict(query_span=[1, 5], token_grid=[2, 2],
        selected_token_count=1, gt_distribution=[1., 0., 0., 0.], prompt_length=6)
    return model, geometry


def invoke(model, x, cache=None):
    n = x.shape[1]
    mask = None if n == 1 else torch.triu(torch.full((1,1,n,n), float("-inf")), diagonal=1)
    return model.attn(x, position_embeddings=(torch.ones(1,n,8), torch.zeros(1,n,8)),
        attention_mask=mask, past_key_values=cache)


@pytest.mark.parametrize("impl", ["eager", "sdpa"])
def test_native_noop_gt_and_restore(impl):
    model, geometry = fixture(impl)
    x = torch.randn(1, 6, 32)
    baseline, base_weights = invoke(model, x)
    original_func = model.attn.forward.__func__
    with QueryAttentionHook(model, [(0, 1)], [0], geometry, "noop") as hook:
        noop, _ = invoke(model, x)
    torch.testing.assert_close(noop, baseline, atol=1e-6, rtol=1e-5)
    assert len(hook.records) == 1
    assert hook.records[0]["before_map"] == hook.records[0]["after_map"]
    assert model.attn.forward.__func__ is original_func
    assert "forward" not in model.attn.__dict__
    with QueryAttentionHook(model, [(0, 1)], [0], geometry, "gt_align") as hook:
        changed, weights = invoke(model, x)
    torch.testing.assert_close(changed[:, :-1], baseline[:, :-1], atol=0, rtol=0)
    assert not torch.equal(changed[:, -1], baseline[:, -1])
    record = hook.records[0]
    assert record["alignment_passed"]
    assert record["after_map"][1:] == [0., 0., 0.]
    assert record["query_mass_after"] == pytest.approx(record["query_mass_before"], abs=1e-6)
    assert record["head_output_delta_l2"] > 0
    if base_weights is not None:
        torch.testing.assert_close(weights[:, [0,2,3]], base_weights[:, [0,2,3]], atol=0, rtol=0)
        torch.testing.assert_close(weights[0,1,-1,[0,5]], base_weights[0,1,-1,[0,5]], atol=0, rtol=0)


@pytest.mark.parametrize("impl", ["eager", "sdpa"])
def test_decode_cache_row_and_coverage(impl):
    model, geometry = fixture(impl)
    cache = DynamicCache()
    with QueryAttentionHook(model, [(0, 3)], [1], geometry, "gt_align") as hook:
        invoke(model, torch.randn(1,6,32), cache)
        assert hook.records == []
        invoke(model, torch.randn(1,1,32), cache)
    assert len(hook.records) == 1
    assert hook.records[0]["generation_step"] == 1
    assert hook.records[0]["prediction_row"] == 6
    assert hook.records[0]["key_length"] == 7


def test_restore_after_exception_and_invalid_head():
    model, geometry = fixture()
    func = model.attn.forward.__func__
    with pytest.raises(RuntimeError, match="test"):
        with QueryAttentionHook(model, [(0,0)], [0], geometry, "noop"):
            raise RuntimeError("test")
    assert model.attn.forward.__func__ is func
    with pytest.raises(ValueError, match="outside"):
        with QueryAttentionHook(model, [(0,0),(1,0)], [0], geometry, "noop"):
            pass
    assert model.attn.forward.__func__ is func


def test_map_change_can_leave_value_output_unchanged():
    model, geometry = fixture()
    hook = QueryAttentionHook(model, [(0,1)], [0], geometry, "gt_align")
    q, k = torch.randn(1,4,6,8), torch.randn(1,2,6,8)
    # Identical V at all key positions: mass redistribution cannot change AV.
    v = torch.ones(1,2,6,8)
    from transformers.models.qwen3_vl.modeling_qwen3_vl import eager_attention_forward
    output, _ = hook._interface(eager_attention_forward, 0)(
        model.attn, q,k,v,None,scaling=0.5)
    assert hook.records[0]["before_map"] != hook.records[0]["after_map"]
    assert hook.records[0]["head_output_delta_l2"] < 1e-5


def test_geometry_area_and_merged_grid():
    processor = SimpleNamespace(tokenizer=SimpleNamespace(convert_tokens_to_ids=lambda x: 7))
    model = SimpleNamespace(config=SimpleNamespace(vision_config=SimpleNamespace(spatial_merge_size=2)))
    inputs = dict(input_ids=torch.tensor([[1,7,7,7,7,2]]),
        attention_mask=torch.ones(1,6), image_grid_thw=torch.tensor([[1,4,4]]))
    geometry = query_geometry(inputs, processor, model, "[250,250,750,750]")
    assert geometry["token_grid"] == [2,2]
    assert geometry["selected_token_count"] == 4
    assert geometry["gt_distribution"] == [0.25]*4
    inputs["image_grid_thw"] = torch.tensor([[1,4,6]])
    with pytest.raises(ValueError, match="mapping"):
        query_geometry(inputs, processor, model, "[250,250,750,750]")


def test_branch_config_and_fail_closed_defaults():
    root = Path(__file__).resolve().parents[1]
    path = root / "configs/sft/qwen3vl_8b_focus_query_attention_branch.py"
    config = load_experiment_config(path)
    assert config["branch"]["action"] == "attention_intervene"
    assert config["branch"]["resolved_source"] == "e011_gt_mask"
    assert config["model"]["type"] == "Qwen3VLLoRADDP"
    assert "samples_00005261_step_000083" in config["named_run"]["parent_checkpoint"]
    assert config["test_dataloader"]["dataset"]["ann_file"]
    assert config["evaluation"]["limit"] is None
    assert config["attention_intervention"]["auto_head_screening"]["enabled"]
    assert config["attention_intervention"]["generation_steps"] == "all"
    assert config["train_dataloader"]["dataset"]["prompt_protocol"] == "focus"
    validate_settings(config["attention_intervention"], allow_auto=True)
    assert load_experiment_config(path, ["branch.action=head_screen"])["branch"]["action"] == "head_screen"


def test_settings_reject_missing_and_ambiguous_rows():
    base = dict(heads=["L0H01"], generation_steps=[0],
                normalization="overlap_area_preserve_query_mass")
    validate_settings(base)
    for update in (dict(heads=[]), dict(generation_steps=[]),
                   dict(generation_steps=[0,0]), dict(generation_steps=[-1]),
                   dict(normalization="uniform"), dict(logits_atol=-1)):
        with pytest.raises(ValueError):
            validate_settings(dict(base, **update))


@pytest.mark.parametrize("steps", [(0,1), "all"])
def test_real_tiny_qwen3_generation_three_conditions(steps):
    from transformers import Qwen3VLConfig, Qwen3VLForConditionalGeneration
    from iploc_szy.evaluation.query_attention import generate_comparison
    torch.manual_seed(29)
    config = Qwen3VLConfig(
        text_config=dict(vocab_size=64, hidden_size=32, intermediate_size=64,
            num_hidden_layers=1, num_attention_heads=4, num_key_value_heads=2,
            head_dim=8, rope_scaling=dict(rope_type="default", mrope_section=[1,1,2])),
        vision_config=dict(depth=1, hidden_size=32, intermediate_size=64, num_heads=4,
            out_hidden_size=32, spatial_merge_size=2, patch_size=2),
        image_token_id=62, video_token_id=61, vision_start_token_id=60,
    )
    config._attn_implementation = "eager"
    model = Qwen3VLForConditionalGeneration(config).eval()
    model.generation_config.eos_token_id = None
    model.generation_config.pad_token_id = 0
    # Synthetic text positions represent the map grid; no image/8B weights are loaded.
    processor = SimpleNamespace(
        tokenizer=SimpleNamespace(convert_tokens_to_ids=lambda x: 7),
        batch_decode=lambda ids, **kw: [" ".join(map(str, row.tolist())) for row in ids],
    )
    inputs = dict(input_ids=torch.tensor([[2,7,7,7,7,3]]),
        attention_mask=torch.ones(1,6,dtype=torch.long),
        image_grid_thw=torch.tensor([[1,4,4]]))
    result = generate_comparison(model, processor, inputs, "[0,0,500,500]",
        dict(max_new_tokens=3, do_sample=False, seed=31),
        dict(heads=["L0H01"], generation_steps=steps,
             normalization="overlap_area_preserve_query_mass",
             logits_atol=0.0, logits_rtol=0.0))
    assert set(result["conditions"]) == {"baseline","noop","gt_align"}
    assert result["gates"]["noop_tokens_equal"]
    assert result["gates"]["noop_logits_close"]
    assert result["gates"]["intervention_coverage"]
    assert result["gates"]["attention_alignment"]
    assert len(result["conditions"]["gt_align"]["attention"]) == (3 if steps == "all" else 2)
    assert "predicted_token_text" in result["conditions"]["gt_align"]["attention"][0]

def test_auto_settings_and_all_generation():
    settings = dict(heads=(), generation_steps="all",
        normalization="overlap_area_preserve_query_mass",
        auto_head_screening=dict(enabled=True, top_k=5, samples=None))
    assert validate_settings(settings, allow_auto=True) == ((), "all")
    with pytest.raises(ValueError, match="heads"):
        validate_settings(settings)
    assert validate_settings(dict(settings, heads=["L0H00"])) == (((0,0),), "all")


def test_selected_probe_matches_real_eager_rows():
    from transformers.models.qwen3_vl.modeling_qwen3_vl import Qwen3VLTextModel
    from iploc_szy.evaluation.auto_query_heads import selected_probe_maps
    from iploc_szy.head_screening.probes import TeacherForcedDualSpanAttentionProbe
    cfg = Qwen3VLTextConfig(vocab_size=64, hidden_size=32, intermediate_size=64,
        num_hidden_layers=2, num_attention_heads=4, num_key_value_heads=2, head_dim=8,
        rope_scaling=dict(rope_type="default", mrope_section=[1,1,2]))
    cfg._attn_implementation = "eager"
    model = Qwen3VLTextModel(cfg).eval()
    forward = dict(input_ids=torch.tensor([[2,7,7,7,7,3]]),
        attention_mask=torch.ones(1,6,dtype=torch.long), use_cache=False, return_dict=True)
    rows, spans = [4,5], [(1,3,1,2),(3,5,1,2)]
    with torch.inference_mode():
        eager = model(**forward, output_attentions=True).attentions
        maps = selected_probe_maps(model, forward, rows, spans)
    import numpy as np
    for actual, span in zip(maps, spans):
        expected = TeacherForcedDualSpanAttentionProbe._maps(eager, rows, span)
        np.testing.assert_allclose(actual, expected, atol=1e-6, rtol=1e-5)
    assert all(not m._forward_pre_hooks for m in model.layers)


def test_streaming_finder_matches_existing_query_ranking(tmp_path):
    import numpy as np
    from iploc_szy.evaluation.auto_query_heads import StreamingQueryFinder
    from iploc_szy.head_screening.finders import R003QueryHeadFinder
    rng = np.random.default_rng(18)
    records = []
    for i in range(4):
        p = tmp_path / f"sample{i}.npz"
        maps = rng.random((3,4,3,3)).astype(np.float32)
        maps[2] *= 8
        np.savez(p, q_to_q=maps, q_to_r=maps,
                 reference_target=np.ones((3,3)))
        records.append(dict(artifact=str(p), head_shape=[3,4]))
    kwargs = dict(fixed_head_counts=(1,), excluded_layers=(), per_sample=2)
    assert StreamingQueryFinder(**kwargs).find(records) == R003QueryHeadFinder(**kwargs).find(records)


def test_automatic_screen_freezes_same_eval_and_checkpoint(tmp_path, monkeypatch):
    import iploc_szy.evaluation.auto_query_heads as auto
    import json
    seen = {}
    class Probe:
        def sample_indices(self, size, index):
            return list(range(size))
        def collect(self, runner, index, root):
            seen["dataset"] = runner.dataset
            seen["model"] = runner.wrapper.peft_model
            return dict(records=[dict(dataset_index=i, head_shape=[1,2]) for i in range(3)],
                        failures=[])
    class Finder:
        def __init__(self, **kw):
            seen["finder"] = kw
        def find(self, records):
            seen["records"] = records
            return dict(selected_sets=dict(query={"2":["L0H00","L0H01"]}))
    def probe_build(cfg):
        seen["probe"] = cfg
        return Probe()
    monkeypatch.setattr(auto.HEAD_PROBES, "build", probe_build)
    monkeypatch.setattr(auto.DATASETS, "build", lambda *a, **kw: object())
    monkeypatch.setattr(auto, "StreamingQueryFinder", Finder)
    manifest = tmp_path / "eval.json"
    manifest.write_text("[]")
    model = torch.nn.Linear(2,2)
    wrapper = SimpleNamespace(model=model, peft_model=model, input_device="cpu", processor=object())
    cfg = dict(work_dir=str(tmp_path/"run"),
        named_run=dict(resolved_resume_checkpoint="/specified/checkpoint"),
        test_dataloader=dict(dataset=dict(ann_file=str(manifest))),
        train_dataloader=dict(collator=dict(type="Qwen3VLSFTCollator")),
        head_screening=dict(probe=dict(type="TeacherForcedDualSpanAttentionProbe"),
                            finder=dict(type="R003QueryHeadFinder")))
    settings = dict(seed=21, dataloader="test_dataloader", vision_max_patch_tokens=4096,
        _attention_intervention=dict(heads=(), generation_steps="all",
            auto_head_screening=dict(enabled=True, samples=None, top_k=2)))
    result = auto.resolve_query_heads(wrapper, ["eval0","eval1","eval2"], [0,1,2], cfg, settings)
    assert result["heads"] == ["L0H00","L0H01"]
    assert seen["dataset"] == ["eval0","eval1","eval2"]
    assert seen["model"] is model
    assert seen["probe"]["samples_per_screening"] == 3
    assert seen["probe"]["attention_mode"] == "selected"
    saved = json.loads(Path(result["resolved_screening"]).read_text())
    assert saved["checkpoint"] == "/specified/checkpoint"
    assert saved["screening_indices"] == [0,1,2]
    assert saved["status"] == "completed"
    # Explicit heads reuse the chosen set and do not screen a second time.
    assert auto.resolve_query_heads(wrapper, [], [], cfg,
        dict(settings, _attention_intervention=result)) == result


def test_launcher_and_alias_use_unified_branch_config():
    root = Path(__file__).resolve().parents[1]
    unified = load_experiment_config(root / "configs/sft/qwen3vl_8b_focus_branch.py",
                                    ["branch.action=attention_intervene"])
    alias = load_experiment_config(root / "configs/sft/qwen3vl_8b_focus_query_attention_branch.py")
    for key in ("evaluation", "attention_intervention", "model", "test_dataloader", "named_run"):
        assert unified[key] == alias[key]
    launcher = (root / "tools/run/eval/run_e011_inter.sh").read_text()
    assert "DEFAULT_CONFIG=configs/sft/qwen3vl_8b_focus_branch.py" in launcher
    assert 'branch.action=attention_intervene "$@"' in launcher
    assert load_experiment_config(root / "configs/sft/qwen3vl_8b_focus_branch.py")["branch"]["action"] == "evaluate"
