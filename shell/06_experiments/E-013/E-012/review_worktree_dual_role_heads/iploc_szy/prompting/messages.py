"""Paper-grounded conversation builders for IPLoc and FOCUS training."""

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

ImageLike = Union[str, Path]
Message = Dict[str, Any]

FOCUS_PROMPT = (
    "Locate the same object across the sequence of frames shown below. "
    "Your goal is to identify the target object consistently using the visual "
    "context provided.\n\n"
    "For the first T-1 frames, the bounding box of the object is already "
    "provided. Use this information and the visual context to predict where "
    "the same object appears in the final frame.\n\n"
    "Output the predicted bounding box for the last frame in the following "
    "format: <answer>[x_min, y_min, x_max, y_max]</answer>"
)

QWEN3_GROUNDING_PROMPT = (
    "Use the annotated reference image or images to identify the same target "
    "object in the final image. Coordinates are integers normalized to the "
    "range 0 to 1000. Report bbox coordinates as a JSON list with exactly one "
    "item in this format: "
    '[{"bbox_2d": [x1, y1, x2, y2], "label": "target label"}]. '
    "Output JSON only, without Markdown fences or additional explanation."
)


def _assistant_text_message(text: str) -> Message:
    """Build one text-only assistant turn."""
    return {
        "role": "assistant",
        "content": [{"type": "text", "text": text}],
    }


def localization_messages(
    image: ImageLike,
    prompt: str,
    answer: Optional[str] = None,
) -> List[Message]:
    """Build a generic single-image localization conversation."""
    messages: List[Message] = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": str(image)},
                {"type": "text", "text": prompt},
            ],
        }
    ]
    if answer is not None:
        messages.append(_assistant_text_message(answer))
    return messages


def focus_messages(
    references: Sequence[Mapping[str, Any]],
    query_image: ImageLike,
    answer: Optional[str] = None,
    prompt: str = FOCUS_PROMPT,
) -> List[Message]:
    """Build the category-free sequence specified by FOCUS Section 5.1.

    The fixed task prompt appears once. It is followed by interleaved support
    images and their textual BBOX annotations, then the query image without a
    box. Only the final query answer is an assistant turn. Category names and
    pseudo-names are intentionally absent from this protocol.
    """
    content: List[Dict[str, str]] = [{"type": "text", "text": prompt}]
    for frame_index, reference in enumerate(references, start=1):
        content.extend(
            [
                {"type": "image", "image": str(reference["image"])},
                {
                    "type": "text",
                    "text": f"Frame {frame_index} BBOX: {reference['answer']}",
                },
            ]
        )
    content.extend(
        [
            {"type": "image", "image": str(query_image)},
            {
                "type": "text",
                "text": (
                    f"Frame {len(references) + 1} is the final frame. "
                    "Predict its BBOX."
                ),
            },
        ]
    )
    messages: List[Message] = [{"role": "user", "content": content}]
    if answer is not None:
        messages.append(_assistant_text_message(f"<answer>{answer}</answer>"))
    return messages


def iploc_messages(
    references: Sequence[Mapping[str, Any]],
    query_image: ImageLike,
    element: str,
    answer: Optional[str] = None,
) -> List[Message]:
    """Build the category/pseudo-name protocol from IPLoc Section 3.1.

    Support boxes are part of human input turns, not assistant demonstrations.
    The same label (real category or per-conversation pseudo-name) identifies the
    tracked object throughout the sequence. The final assistant predicts only
    the query box using standard language-model supervision.
    """
    content: List[Dict[str, str]] = []
    for reference in references:
        content.extend(
            [
                {"type": "image", "image": str(reference["image"])},
                {
                    "type": "text",
                    "text": f"<ref>{element}</ref> BBOX: {reference['answer']}",
                },
            ]
        )
    content.extend(
        [
            {"type": "image", "image": str(query_image)},
            {
                "type": "text",
                "text": f"<ref>{element}</ref> Predict the BBOX.",
            },
        ]
    )
    messages: List[Message] = [{"role": "user", "content": content}]
    if answer is not None:
        messages.append(_assistant_text_message(answer))
    return messages


def qwen3_grounding_messages(
    references: Sequence[Mapping[str, Any]],
    query_image: ImageLike,
    element: str,
    answer: Optional[str] = None,
    prompt: str = QWEN3_GROUNDING_PROMPT,
) -> List[Message]:
    """Build reference-conditioned input using Qwen3-VL grounding JSON format."""
    label = json.dumps(str(element), ensure_ascii=False)
    content: List[Dict[str, str]] = [
        {"type": "text", "text": prompt}
    ]
    for reference in references:
        content.extend(
            [
                {"type": "image", "image": str(reference["image"])},
                {
                    "type": "text",
                    "text": (
                        "Reference target annotation: "
                        f'{{"bbox_2d": {reference["answer"]}, "label": {label}}}'
                    ),
                },
            ]
        )
    content.extend(
        [
            {"type": "image", "image": str(query_image)},
            {
                "type": "text",
                "text": (
                    f"Locate the same {element} in this final image. "
                    "Report its bbox coordinates in the required JSON format."
                ),
            },
        ]
    )
    messages: List[Message] = [{"role": "user", "content": content}]
    if answer is not None:
        messages.append(
            _assistant_text_message(
                f'[{{"bbox_2d": {answer}, "label": {label}}}]'
            )
        )
    return messages
