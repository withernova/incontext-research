from copy import deepcopy
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from iploc_szy.attention_distillation.loss import ReferenceQueryAttentionDistillation
from iploc_szy.engine.pipeline import TrainingPipeline
from iploc_szy.registry import AUXILIARY_LOSSES


@AUXILIARY_LOSSES.register_module()
class PipelineTestLoss:
    def __init__(self, wrapper, dataset, collator, coefficient, student_heads=()):
        self.coefficient = coefficient
        self.student_heads = student_heads
        self.extractor = SimpleNamespace(close=lambda: None)


def specification():
    def active(start, coefficient, interval):
        return dict(start_step=start,
                    auxiliary_loss=dict(type="PipelineTestLoss", coefficient=coefficient),
                    ramp_steps=2, head_selection=dict(top_k=3, refresh_steps=interval))
    return dict(stages=dict(warmup=dict(start_step=0, auxiliary_loss=None),
                            early=active(83, 0.02, 83),
                            adaptive=active(494, 0.05, 83),
                            fixed=active(1482, 0.1, None)), screening=dict(probe={}, finder={}))


def runner(tmp_path):
    return SimpleNamespace(auxiliary_loss=None, wrapper=None, dataset=[], collator=None,
                           work_dir=tmp_path, is_main_process=True)


def test_boundaries_refresh_and_resume_preserve_selected_heads(tmp_path, monkeypatch):
    pipeline = TrainingPipeline(**specification())
    model_runner = runner(tmp_path)
    calls = []

    def screen(runner, completed, name, selection):
        calls.append((name, completed))
        return ["L2H00", "L2H01", "L2H02"], f"selection-{completed}"

    monkeypatch.setattr(pipeline, "_screen", screen)
    for completed in (0, 82):
        pipeline.prepare(model_runner, completed)
        assert model_runner.auxiliary_loss is None
    assert calls == []
    pipeline.prepare(model_runner, 83)
    assert calls == [("early", 83)]
    assert model_runner.auxiliary_loss.coefficient == pytest.approx(0.01)
    for completed in (84, 165):
        pipeline.prepare(model_runner, completed)
        assert model_runner.auxiliary_loss.coefficient == pytest.approx(0.02)
    pipeline.prepare(model_runner, 166)
    assert calls[-1] == ("early", 166)
    pipeline.prepare(model_runner, 494)
    assert calls[-1] == ("adaptive", 494)
    pipeline.prepare(model_runner, 1482)
    assert calls[-1] == ("fixed", 1482)
    state = deepcopy(pipeline.state_dict())
    resumed = TrainingPipeline(**specification())
    resumed.load_state_dict(state)
    monkeypatch.setattr(resumed, "_screen", lambda *args: pytest.fail("fixed resume must not rescreen"))
    restored_runner = runner(tmp_path / "resume")
    for completed in (1483, 1729):
        resumed.prepare(restored_runner, completed)
    assert restored_runner.auxiliary_loss.student_heads == ["L2H00", "L2H01", "L2H02"]
    assert restored_runner.auxiliary_loss.coefficient == pytest.approx(0.1)
    assert resumed.last_selection_step == 1482


def test_resume_rejects_changed_schedule_and_bad_stage_order():
    spec = specification()
    pipeline = TrainingPipeline(**spec)
    state = pipeline.state_dict()
    spec["stages"]["early"]["start_step"] = 41
    with pytest.raises(ValueError, match="differs"):
        TrainingPipeline(**spec).load_state_dict(state)
    spec["stages"]["early"]["start_step"] = 494
    with pytest.raises(ValueError, match="strictly increasing"):
        TrainingPipeline(**spec)


def test_adaptive_resume_rebuilds_but_waits_until_next_refresh(tmp_path, monkeypatch):
    pipeline = TrainingPipeline(**specification())
    monkeypatch.setattr(pipeline, "_screen", lambda *args: (["L2H00"], "selection"))
    pipeline.prepare(runner(tmp_path), 83)
    resumed = TrainingPipeline(**specification())
    resumed.load_state_dict(pipeline.state_dict())
    calls = []
    monkeypatch.setattr(resumed, "_screen", lambda *args: (calls.append(args[1]) or ["L3H00"], "new"))
    restored = runner(tmp_path)
    resumed.prepare(restored, 165)
    assert calls == []
    resumed.prepare(restored, 166)
    assert calls == [166]


def test_gt_mask_needs_no_teacher_and_backpropagates_at_small_weight(monkeypatch):
    import iploc_szy.attention_distillation.loss as module

    logits = torch.tensor([0.1, 0.2, -0.1, 0.0, 0.3], requires_grad=True)
    selected = {(2, 0): [logits.softmax(0).reshape(1, 5)]}
    monkeypatch.setattr(module, "SelectedAttentionExtractor", lambda *args:
                        SimpleNamespace(extract=lambda rows: selected))
    config = SimpleNamespace(image_token_id=99, vision_config=SimpleNamespace(spatial_merge_size=2))
    wrapper = SimpleNamespace(peft_model=SimpleNamespace(get_base_model=lambda: SimpleNamespace(config=config)))
    loss = ReferenceQueryAttentionDistillation(
        wrapper=wrapper, dataset=[], collator=None, treatment="gt_mask",
        teacher_manifest=None, teacher_heads=(), student_heads=["L2H00"], coefficient=0.02,
    )
    assert loss.store is None
    geometry = SimpleNamespace(prediction_rows=[4], reference_span=(0, 4, 2, 2),
                               reference_occupancy=np.array([[1.0, 0.5], [0.0, 0.0]], dtype=np.float32))
    target = loss._teacher_targets(geometry, logits)
    torch.testing.assert_close(target["distribution"], torch.tensor([2 / 3, 1 / 3, 0., 0.]))
    assert target["reference_span_mass"].item() == pytest.approx(1.0)
    assert target["reference_object_mass"].item() == pytest.approx(5 / 6)
    loss._geometries = [geometry]
    result = loss.compute(SimpleNamespace(loss=torch.tensor(0.)), {}, [{}])
    result.loss.backward()
    assert torch.isfinite(logits.grad).all() and logits.grad.abs().sum() > 0
    loss.coefficient = 0.1
    larger = loss.compute(SimpleNamespace(loss=torch.tensor(0.)), {}, [{}])
    assert larger.loss.item() == pytest.approx(5 * result.loss.item())


def test_screening_preserves_rng_and_uses_fixed_training_sample_seed(tmp_path, monkeypatch):
    import random
    import iploc_szy.engine.pipeline as module

    r = runner(tmp_path)
    r.context = None
    r.dataset = SimpleNamespace(ann_file="train-only.json")
    pipeline = TrainingPipeline(**specification())
    indices = []

    def collect(runner, index, root):
        indices.append(index)
        random.random(); np.random.rand(); torch.rand(1)
        return dict(records=[dict(dataset_index=3)], failures=[])

    monkeypatch.setattr(module.HEAD_PROBES, "build", lambda cfg: SimpleNamespace(collect=collect))
    monkeypatch.setattr(module.HEAD_FINDERS, "build", lambda cfg: SimpleNamespace(find=lambda rows:
                        dict(status="completed", selected_sets={"query": {"3": ["L2H00"]}})))
    random.seed(19); np.random.seed(19); torch.manual_seed(19)
    expected = (random.random(), np.random.rand(), torch.rand(1))
    random.seed(19); np.random.seed(19); torch.manual_seed(19)
    pipeline._screen(r, 83, "early", dict(top_k=3))
    pipeline._screen(r, 166, "early", dict(top_k=3))
    actual = (random.random(), np.random.rand(), torch.rand(1))
    assert indices == [0, 0]
    assert actual[:2] == expected[:2]
    torch.testing.assert_close(actual[2], expected[2])


def test_recipe_keeps_focus_and_accepts_stage_overrides():
    from pathlib import Path
    from iploc_szy.branching import load_experiment_config

    path = Path(__file__).resolve().parents[1] / "configs/sft/qwen3vl_8b_focus_gt_mask_pipeline.py"
    cfg = load_experiment_config(path, [
        "runner.pipeline.stages.early.start_step=41",
        "runner.pipeline.stages.early.auxiliary_loss.coefficient=0.01",
    ])
    assert cfg["train_dataloader"]["dataset"]["prompt_protocol"] == "focus"
    assert cfg["named_run"]["parent_checkpoint"] is None
    assert cfg["runner"]["initialize_from"] is None
    assert cfg["runner"]["auxiliary_loss"] is None
    stages = cfg["runner"]["pipeline"]["stages"]
    assert stages["early"]["start_step"] == 41
    assert stages["early"]["auxiliary_loss"]["coefficient"] == 0.01
    TrainingPipeline(**cfg["runner"]["pipeline"])
    assert len(cfg.source_files) >= 5


def test_actual_runner_switches_only_between_accumulated_updates(tmp_path, monkeypatch):
    from iploc_szy.engine.runner import SFTLoRARunner

    class Model(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.weight = torch.nn.Parameter(torch.tensor(1.0))

        def forward(self, **batch):
            return SimpleNamespace(loss=self.weight.square(), logits=torch.zeros(1, 2, 3))

    class Wrapper:
        def __init__(self):
            self.model = Model()
            self.input_device = torch.device("cpu")

        def trainable_parameters(self):
            return self.model.parameters()

        def save_adapter(self, path):
            pass

    @AUXILIARY_LOSSES.register_module(name="PipelineIntegrationLoss")
    class Auxiliary:
        def __init__(self, wrapper, dataset, collator, coefficient):
            self.coefficient = coefficient

        def begin_batch(self, batch, metadata):
            pass

        def compute(self, output, batch, metadata):
            from iploc_szy.attention_distillation.loss import AuxiliaryLossOutput
            loss = self.coefficient * output.loss
            return AuxiliaryLossOutput(loss, {"auxiliary_loss": loss.detach()})

    def collate(samples):
        return dict(labels=torch.tensor([[-100, 1]]), metadata=[dict(id="s0")])

    r = SFTLoRARunner(
        model=Wrapper(), dataset=[{}], collator=collate, work_dir=str(tmp_path),
        max_steps=3, gradient_accumulation_steps=2, hooks=[],
        pipeline=dict(stages=dict(
            warmup=dict(start_step=0, auxiliary_loss=None),
            active=dict(start_step=1, auxiliary_loss=dict(
                type="PipelineIntegrationLoss", coefficient=0.02)),
        )),
    )
    monkeypatch.setattr(r, "_localization_metric_counts", lambda *args: {})
    r.run()
    assert [row["pipeline_stage"] for row in r.auxiliary_history] == [0., 1., 1.]
    assert [row["auxiliary_coefficient"] for row in r.auxiliary_history] == [0., .02, .02]
    assert r.metrics["loss_comparison_objective"] == "sft_ce"
    # Final loss gate compares CE to CE, not CE to CE + the activated auxiliary.
    assert r.metrics["loss_after"] == pytest.approx(r.model.weight.item() ** 2)
