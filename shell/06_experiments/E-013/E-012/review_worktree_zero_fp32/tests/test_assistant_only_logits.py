import torch
import torch.nn.functional as F
from types import SimpleNamespace

from iploc_szy.engine.runner import SFTLoRARunner


def _causal_loss(logits, labels):
    shifted = F.pad(labels, (0, 1), value=-100)[..., 1:]
    return F.cross_entropy(logits.float().view(-1, logits.shape[-1]), shifted.reshape(-1), ignore_index=-100)


def test_assistant_only_suffix_matches_full_loss_and_lm_head_gradient():
    torch.manual_seed(7)
    hidden_full = torch.randn(2, 12, 5, requires_grad=True)
    labels = torch.full((2, 12), -100, dtype=torch.long)
    labels[0, 8:] = torch.tensor([1, 2, 3, 4])
    labels[1, 9:] = torch.tensor([2, 1, 4])
    weight_full = torch.randn(7, 5, requires_grad=True)
    full = _causal_loss(hidden_full @ weight_full.t(), labels)
    full.backward()

    runner = object.__new__(SFTLoRARunner)
    runner.assistant_only_logits = True
    batch = {"labels": labels}
    keep = runner._logits_to_keep(batch)
    assert keep == 5
    selected = runner._forward_batch(batch)
    assert selected["logits_to_keep"] == keep

    hidden_selected = hidden_full.detach().clone().requires_grad_(True)
    weight_selected = weight_full.detach().clone().requires_grad_(True)
    suffix = _causal_loss(
        hidden_selected[:, -keep:] @ weight_selected.t(), selected["labels"]
    )
    suffix.backward()
    torch.testing.assert_close(suffix, full)
    torch.testing.assert_close(weight_selected.grad, weight_full.grad)
    torch.testing.assert_close(hidden_selected.grad, hidden_full.grad)


def test_assistant_only_suffix_rejects_invalid_labels():
    runner = object.__new__(SFTLoRARunner)
    runner.assistant_only_logits = True
    try:
        runner._logits_to_keep({"labels": torch.full((1, 4), -100)})
    except ValueError as exc:
        assert "supervised" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_teacher_forced_localization_iou_counts_and_thresholds():
    class Tokenizer:
        def decode(self, token_ids, skip_special_tokens=True):
            rendered = {
                (1, 2, 3, 4): "<answer>[0,0,10,10]</answer>",
                (5, 6, 7, 8): "<answer>[0,0,5,5]</answer>",
            }
            return rendered[tuple(token_ids)]

    runner = object.__new__(SFTLoRARunner)
    runner.collator = SimpleNamespace(processor=SimpleNamespace(tokenizer=Tokenizer()))
    runner.localization_iou_thresholds = (0.25, 0.5, 0.75)
    runner._gather = lambda value: [value]

    labels = torch.tensor([[-100, 1, 2, 3, 4], [-100, 1, 2, 3, 4]])
    logits = torch.zeros(2, 5, 9)
    for position, token in enumerate((1, 2, 3, 4)):
        logits[0, position, token] = 1.0
    for position, token in enumerate((5, 6, 7, 8)):
        logits[1, position, token] = 1.0
    counts = runner._localization_metric_counts(logits, labels)
    metrics = runner._aggregate_localization_counts([counts])

    assert metrics["teacher_forced_bbox_parse_rate"] == 1.0
    assert metrics["teacher_forced_mean_iou"] == 0.625
    assert metrics["teacher_forced_iou_at_0.25"] == 1.0
    assert metrics["teacher_forced_iou_at_0.5"] == 0.5
    assert metrics["teacher_forced_iou_at_0.75"] == 0.5
