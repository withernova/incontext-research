import importlib.util
from pathlib import Path

import pytest

TOOL = Path(__file__).parents[1] / "tools" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("evaluate", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_seeded_random_selection_is_complete_unique_and_reproducible():
    settings = {"limit": 10, "selection": "seeded_random", "seed": 7}
    first = MODULE.evaluation_indices(100, settings)
    second = MODULE.evaluation_indices(100, settings)
    assert first == second
    assert len(first) == len(set(first)) == 10
    assert first != list(range(10))


def test_full_and_invalid_selections():
    assert MODULE.evaluation_indices(4, {"limit": None}) == [0, 1, 2, 3]
    with pytest.raises(ValueError, match="selection"):
        MODULE.evaluation_indices(4, {"selection": "unknown"})
    with pytest.raises(ValueError, match="at least one"):
        MODULE.evaluation_indices(4, {"limit": 0})


def test_metrics_by_dataset_keeps_component_metrics_separate():
    rows = [
        {"dataset": "LaSOT", "prediction": "[0, 0, 10, 10]", "target": "[0, 0, 10, 10]", "id": "l"},
        {"dataset": "TAO", "prediction": "invalid", "target": "[0, 0, 10, 10]", "id": "t"},
    ]
    metrics = MODULE.metrics_by_dataset(rows, {"type": "LocalizationEvaluator"})
    assert metrics["LaSOT"]["miou"] == 1.0
    assert metrics["TAO"]["miou"] == 0.0
    assert metrics["LaSOT"]["samples"] == metrics["TAO"]["samples"] == 1


class _ImageProcessor:
    patch_size = 16
    size = {"longest_edge": 999999}


class _Processor:
    image_processor = _ImageProcessor()


def test_configure_vision_limit_matches_training_patch_cap():
    processor = _Processor()
    assert MODULE.configure_vision_limit(processor, {"vision_max_patch_tokens": 1024}) == 262144
    assert processor.image_processor.size["longest_edge"] == 262144
    assert MODULE.configure_vision_limit(processor, {"vision_max_patch_tokens": None}) is None
    with pytest.raises(ValueError, match="positive"):
        MODULE.configure_vision_limit(processor, {"vision_max_patch_tokens": 0})
