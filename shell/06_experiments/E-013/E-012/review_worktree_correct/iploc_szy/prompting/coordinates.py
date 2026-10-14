"""Bounding-box parsing and pixel/normalized coordinate conversion."""

import ast
import json
import re
from typing import Any, List, Mapping, Optional, Sequence, Tuple

Box = List[float]
ImageSize = Tuple[int, int]
_NUMBER_PATTERN = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


def parse_box(value: Any) -> Optional[Box]:
    """Parse common xyxy representations into four floats.

    Accepted inputs include flat lists, two-point lists, Python-literal strings,
    and free text containing at least four numbers. Invalid values return None.
    """
    if isinstance(value, Mapping):
        for key in ("bbox_2d", "box_2d", "bbox"):
            if key in value:
                return parse_box(value[key])
        return None

    if isinstance(value, (list, tuple)):
        if len(value) == 4 and not any(isinstance(item, (list, tuple)) for item in value):
            return [float(item) for item in value]
        if (
            len(value) == 2
            and all(isinstance(item, (list, tuple)) and len(item) >= 2 for item in value)
        ):
            return [
                float(value[0][0]),
                float(value[0][1]),
                float(value[1][0]),
                float(value[1][1]),
            ]
        for item in value:
            if isinstance(item, Mapping):
                parsed_item = parse_box(item)
                if parsed_item is not None:
                    return parsed_item

    if isinstance(value, str):
        text = value.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines:
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        try:
            parsed = json.loads(text)
        except (ValueError, TypeError):
            try:
                parsed = ast.literal_eval(text)
            except (ValueError, SyntaxError):
                numeric_text = re.sub(
                    r"(?:bbox|box)_2d", "", text, flags=re.IGNORECASE
                )
                numbers = _NUMBER_PATTERN.findall(numeric_text)
                return (
                    [float(number) for number in numbers[:4]]
                    if len(numbers) >= 4
                    else None
                )
        return parse_box(parsed)
    return None


def pixel_to_normalized(box: Any, size: ImageSize, scale: int = 1000) -> Box:
    """Convert pixel xyxy coordinates to the IPLoc 0--``scale`` convention."""
    parsed = parse_box(box)
    width, height = size
    if parsed is None or width <= 0 or height <= 0:
        raise ValueError("invalid box or image size")
    x1, y1, x2, y2 = parsed
    return [
        round(x1 / width * scale),
        round(y1 / height * scale),
        round(x2 / width * scale),
        round(y2 / height * scale),
    ]


def normalized_to_pixel(box: Any, size: ImageSize, scale: int = 1000) -> Optional[Box]:
    """Convert normalized xyxy coordinates back to pixel coordinates."""
    parsed = parse_box(box)
    if parsed is None:
        return None
    width, height = size
    x1, y1, x2, y2 = parsed
    return [
        round(x1 / scale * width),
        round(y1 / scale * height),
        round(x2 / scale * width),
        round(y2 / scale * height),
    ]


def format_box(box: Sequence[float]) -> str:
    """Serialize a box in the compact format used in model answers."""
    return "[" + ",".join(str(int(round(value))) for value in box) + "]"
