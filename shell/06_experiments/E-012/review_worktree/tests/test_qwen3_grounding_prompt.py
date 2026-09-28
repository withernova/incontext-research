import json

from iploc_szy.prompting.coordinates import parse_box
from iploc_szy.prompting.messages import qwen3_grounding_messages


def test_qwen3_grounding_prompt_and_answer_are_json() -> None:
    messages = qwen3_grounding_messages(
        [{"image": "reference.jpg", "answer": "[1,2,300,400]"}],
        "query.jpg",
        "airplane",
        "[10,20,500,600]",
    )
    prompt = " ".join(item["text"] for item in messages[0]["content"] if item["type"] == "text")
    assert "bbox_2d" in prompt
    assert "0 to 1000" in prompt
    assert "JSON only" in prompt
    answer = json.loads(messages[-1]["content"][0]["text"])
    assert answer == [{"bbox_2d": [10, 20, 500, 600], "label": "airplane"}]


def test_parse_box_accepts_qwen3_grounding_json() -> None:
    plain = '[{"bbox_2d": [74, 361, 324, 808], "label": "plate/dish"}]'
    fenced = "```json\n" + plain + "\n```"
    assert parse_box(plain) == [74.0, 361.0, 324.0, 808.0]
    assert parse_box(fenced) == [74.0, 361.0, 324.0, 808.0]
