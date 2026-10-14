import pytest
import torch


def load_module():
    # 正式pytest在仓库根运行时使用正常package import；这个fallback便于镜像语法检查。
    try:
        from iploc_szy.head_screening import head_circuit
        return head_circuit
    except ImportError:
        pytest.skip("iploc_szy package is available only in the remote repository")


def test_horizontal_flip_preserves_mass_values_and_entropy():
    m = load_module()
    block = torch.tensor([[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]])
    flat = block.reshape(1, -1)
    flipped = m.horizontal_flip_visual(flat, 2, 3)
    assert flipped.tolist() == [[3.0, 2.0, 1.0, 6.0, 5.0, 4.0]]
    torch.testing.assert_close(flat.sum(-1), flipped.sum(-1))
    torch.testing.assert_close(flat.sort(-1).values, flipped.sort(-1).values)
    torch.testing.assert_close(m.entropy(flat), m.entropy(flipped))
    torch.testing.assert_close(m.horizontal_flip_visual(flipped, 2, 3), flat)


def test_horizontal_flip_rejects_wrong_grid():
    m = load_module()
    with pytest.raises(ValueError, match="grid"):
        m.horizontal_flip_visual(torch.ones(2, 5), 2, 3)


def test_path_requires_strict_layer_order():
    m = load_module()
    good = m.path_spec(dict(name="good", upstream=[[1, 0]], upstream_control=[[1, 1]],
                            downstream=[[2, 0]], downstream_control=[[3, 1]]))
    assert good["candidate_u"] == ((1, 0),)
    with pytest.raises(ValueError, match="upstream must precede"):
        m.path_spec(dict(name="bad", upstream=[[3, 0]], upstream_control=[[1, 1]],
                         downstream=[[2, 0]], downstream_control=[[4, 1]]))
    with pytest.raises(ValueError, match="non-negative"):
        m.parse_heads([[-1, 0]])


def test_hook_constructor_rejects_grid_span_mismatch_and_unknown_mode():
    m = load_module()
    with pytest.raises(ValueError, match="span length"):
        m.CircuitHook(rows=[5], query_span=(1, 6), grid_hw=(2, 3),
                      corrupt_heads=[[1, 0]])
    with pytest.raises(ValueError, match="corruption_mode"):
        m.CircuitHook(rows=[5], query_span=(1, 5), grid_hw=(2, 2),
                      corrupt_heads=[[1, 0]], corruption_mode="unknown")


def test_effect_helpers_do_not_invent_small_denominator_fraction():
    m = load_module()
    assert m.safe_fraction(1.0, 0.0) is None
    assert m.safe_fraction(1.0, 1e-5) is None
    assert m.safe_fraction(0.25, 0.5) == 0.5
    assert m.box_iou([0, 0, 10, 10], [0, 0, 10, 10]) == 1.0
    assert m.box_iou([0, 0, 1, 1], [2, 2, 3, 3]) == 0.0


def test_real_qwen_capture_corrupt_and_clean_patch_restore():
    m = load_module()
    from iploc_szy.compat import ensure_torchvision_nms_schema
    ensure_torchvision_nms_schema()
    from transformers.models.qwen3_vl.configuration_qwen3_vl import Qwen3VLTextConfig
    from transformers.models.qwen3_vl.modeling_qwen3_vl import Qwen3VLTextModel

    torch.manual_seed(23)
    config = Qwen3VLTextConfig(
        vocab_size=32, hidden_size=64, intermediate_size=96,
        num_hidden_layers=2, num_attention_heads=4, num_key_value_heads=2,
        head_dim=16, rope_scaling={"rope_type": "default", "mrope_section": [2, 3, 3]},
    )
    config._attn_implementation = "eager"

    class TinyModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.config = config
            self.body = Qwen3VLTextModel(config)
            self.lm_head = torch.nn.Linear(64, 32, bias=False)

        def forward(self, ids):
            hidden = self.body(input_ids=ids, use_cache=False).last_hidden_state
            return self.lm_head(hidden)

    model = TinyModel().eval().requires_grad_(False)
    ids = torch.tensor([[1, 2, 3, 4, 5, 6, 7, 8]])
    rows, span, grid = [5, 6], (0, 4), (2, 2)
    with torch.no_grad():
        native = model(ids)
        capture = m.CircuitHook(rows, span, grid, capture_heads=[[0, 0]])
        with capture.installed(model):
            captured_logits = model(ids)
        capture.validate()
        torch.testing.assert_close(captured_logits, native, atol=0, rtol=0)

        corrupt = m.CircuitHook(rows, span, grid, corrupt_heads=[[0, 0]],
                                capture_heads=[[1, 0]])
        with corrupt.installed(model):
            corrupt_logits = model(ids)
        corrupt.validate()
        assert not torch.equal(corrupt_logits[:, rows], native[:, rows])
        assert corrupt.audits[0]["mass_error"] < corrupt.atol
        assert corrupt.audits[0]["sorted_value_error"] < corrupt.atol
        assert corrupt.audits[0]["entropy_error"] < corrupt.atol
        assert corrupt.audits[0]["attention_l1_change_mean"] > 0

        # 同层仅用于验证 patch 张量位置：先翻转，再把该 head 的 clean A@V
        # 写回；真实实验仍由 path_spec 强制 U layer < D layer。
        rescue = m.CircuitHook(rows, span, grid, corrupt_heads=[[0, 0]],
                               patch_values={(0, 0): capture.captured[(0, 0)]})
        with rescue.installed(model):
            rescue_logits = model(ids)
        rescue.validate()
        torch.testing.assert_close(rescue_logits[:, rows], native[:, rows], atol=0, rtol=0)

        zero = m.CircuitHook(rows, span, grid, corrupt_heads=[[0, 0]],
                             corruption_mode="zero_query_attention")
        with zero.installed(model):
            zero_logits = model(ids)
        zero.validate()
        assert not torch.equal(zero_logits[:, rows], native[:, rows])
        audit = zero.audits[0]
        assert audit["corruption_mode"] == "zero_query_attention"
        assert audit["remaining_query_mass_max"] == 0
        assert audit["full_row_sum_drop_error"] < zero.atol
        assert audit["removed_query_mass_mean"] == pytest.approx(audit["query_mass_mean"])
        assert audit["attention_l1_change_mean"] == pytest.approx(audit["query_mass_mean"])
