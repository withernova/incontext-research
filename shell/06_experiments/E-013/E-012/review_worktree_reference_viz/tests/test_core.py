"""Fast unit tests for framework primitives that do not load model weights."""

from iploc_szy.config import Config
from iploc_szy.evaluation.bbox import LocalizationEvaluator, box_iou
from iploc_szy.prompting.coordinates import normalized_to_pixel, pixel_to_normalized
from iploc_szy.registry import Registry


def test_registry_builds_registered_class() -> None:
    registry = Registry("example")

    @registry.register_module()
    class Component:
        def __init__(self, value: int) -> None:
            self.value = value

    assert registry.build(dict(type="Component", value=2)).value == 2


def test_coordinate_round_trip_and_iou() -> None:
    normalized = pixel_to_normalized([0, 0, 50, 100], (100, 200))
    assert normalized == [0, 0, 500, 500]
    assert normalized_to_pixel(normalized, (100, 200)) == [0, 0, 50, 100]
    assert box_iou([0, 0, 10, 10], [0, 0, 10, 10]) == 1.0


def test_config_inheritance(tmp_path) -> None:
    (tmp_path / "base.py").write_text("value = dict(a=1, b=2)\n")
    (tmp_path / "child.py").write_text(
        "_base_ = 'base.py'\nvalue = dict(b=3)\n"
    )
    config = Config.fromfile(tmp_path / "child.py")
    assert config["value"] == {"a": 1, "b": 3}


def test_config_override_parses_literals(tmp_path) -> None:
    (tmp_path / "config.py").write_text("runner = dict(max_steps=3)\n")
    config = Config.fromfile(tmp_path / "config.py")
    config.merge_options(["runner.max_steps=5", "name=experiment"])
    assert config["runner"]["max_steps"] == 5
    assert config["name"] == "experiment"


def test_localization_evaluator_reports_iou_distribution() -> None:
    evaluator = LocalizationEvaluator()
    for index, iou_width in enumerate((0, 1, 2, 4, 8)):
        evaluator.process([0, 0, iou_width, 10], [0, 0, 10, 10], str(index))
    distribution = evaluator.evaluate()["iou_distribution"]
    assert distribution["count"] == 5
    assert distribution["min"] == 0.0
    assert distribution["q25"] == 0.1
    assert distribution["median"] == 0.2
    assert distribution["q75"] == 0.4
    assert distribution["max"] == 0.8
    assert sum(distribution["bins"].values()) == 5
