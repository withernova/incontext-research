import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest


ROOT = Path(__file__).parents[1]


def _load_modules():
    package = ModuleType("iploc_szy")
    package.__path__ = []
    datasets = ModuleType("iploc_szy.datasets")
    datasets.__path__ = []
    prompting = ModuleType("iploc_szy.prompting")
    prompting.__path__ = []

    class Registry:
        def register_module(self):
            return lambda value: value

    registry = ModuleType("iploc_szy.registry")
    registry.DATASETS = Registry()
    pil = ModuleType("PIL")
    pil.Image = object
    for name, module in {
        "iploc_szy": package,
        "iploc_szy.datasets": datasets,
        "iploc_szy.prompting": prompting,
        "iploc_szy.registry": registry,
        "PIL": pil,
    }.items():
        sys.modules[name] = module

    coordinate_spec = importlib.util.spec_from_file_location(
        "iploc_szy.prompting.coordinates", ROOT / "iploc_szy/prompting/coordinates.py"
    )
    coordinates = importlib.util.module_from_spec(coordinate_spec)
    assert coordinate_spec.loader is not None
    sys.modules[coordinate_spec.name] = coordinates
    coordinate_spec.loader.exec_module(coordinates)

    collator_spec = importlib.util.spec_from_file_location(
        "iploc_szy.datasets.collator", ROOT / "iploc_szy/datasets/collator.py"
    )
    collator = importlib.util.module_from_spec(collator_spec)
    assert collator_spec.loader is not None
    sys.modules[collator_spec.name] = collator
    collator_spec.loader.exec_module(collator)
    return coordinates.coordinate_field_char_spans, collator.Qwen3VLSFTCollator


coordinate_field_char_spans, Qwen3VLSFTCollator = _load_modules()


class CharacterTokenizer:
    """Minimal offset tokenizer for testing rendered-to-sequence alignment."""

    def __call__(self, text, *, add_special_tokens, return_offsets_mapping):
        assert not add_special_tokens and return_offsets_mapping
        return {
            "input_ids": [ord(character) for character in text],
            "offset_mapping": [(index, index + 1) for index in range(len(text))],
        }


class Processor:
    tokenizer = CharacterTokenizer()


def test_coordinate_field_char_spans_exclude_bbox_formatting():
    answer = "[12, -3, 400, 5.5]"
    spans = coordinate_field_char_spans(answer)
    assert {field: answer[left:right] for field, (left, right) in spans.items()} == {
        "x1": "12", "y1": "-3", "x2": "400", "y2": "5.5"
    }


@pytest.mark.parametrize("answer", ["", "[1,2,3]", "[1,2,3,4,5]"])
def test_coordinate_field_char_spans_fail_closed(answer):
    with pytest.raises(ValueError):
        coordinate_field_char_spans(answer)


def test_collator_alignment_keeps_all_numeric_characters_only():
    full_text = "prompt assistant: [12,3,405,6] suffix"
    answer = "[12,3,405,6]"
    full_ids = type("Ids", (), {"tolist": lambda self: [ord(c) for c in full_text]})()
    collator = object.__new__(Qwen3VLSFTCollator)
    collator.processor = Processor()

    bbox, fields = collator._bbox_token_alignment(
        full_text, full_ids, answer, prefix_tokens=5
    )
    start = full_text.index(answer)
    assert bbox == list(range(start, start + len(answer)))
    assert fields == {
        "x1": [start + 1, start + 2],
        "y1": [start + 4],
        "x2": [start + 6, start + 7, start + 8],
        "y2": [start + 10],
    }
    selected = {position for positions in fields.values() for position in positions}
    punctuation = {start, start + 3, start + 5, start + 9, start + 11}
    assert selected.isdisjoint(punctuation)


def test_collator_alignment_rejects_token_shared_by_two_fields():
    class WholeAnswerTokenizer:
        def __call__(self, text, *, add_special_tokens, return_offsets_mapping):
            assert not add_special_tokens and return_offsets_mapping
            answer = "[1,2,3,4]"
            start = text.index(answer)
            return {"input_ids": [7], "offset_mapping": [(start, start + len(answer))]}

    collator = object.__new__(Qwen3VLSFTCollator)
    collator.processor = type("P", (), {"tokenizer": WholeAnswerTokenizer()})()
    full_ids = type("Ids", (), {"tolist": lambda self: [7]})()
    with pytest.raises(ValueError, match="multiple coordinate fields"):
        collator._bbox_token_alignment("x[1,2,3,4]", full_ids, "[1,2,3,4]", 0)
