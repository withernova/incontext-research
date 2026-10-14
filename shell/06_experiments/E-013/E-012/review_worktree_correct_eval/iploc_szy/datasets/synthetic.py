"""Deterministic synthetic localization data for capability smoke tests."""

from pathlib import Path
from typing import Any, Dict, List, Tuple

from PIL import Image, ImageDraw
from torch.utils.data import Dataset

from ..prompting.coordinates import format_box, pixel_to_normalized
from ..prompting.messages import localization_messages
from ..registry import DATASETS


@DATASETS.register_module()
class SyntheticLocalizationDataset(Dataset):
    """Generate four simple shapes and repeated localization instructions.

    This dataset tests the multimodal SFT plumbing only. It is intentionally
    deterministic and must not be interpreted as evidence on IPLoc data.
    """

    _SPECS = (
        ("red square", (255, 40, 40), (32, 48, 112, 128)),
        ("green rectangle", (40, 210, 80), (80, 24, 176, 88)),
        ("blue square", (30, 90, 240), (112, 112, 208, 208)),
        ("yellow rectangle", (235, 205, 35), (24, 144, 136, 216)),
    )

    def __init__(self, root: str, repeat: int = 2, image_size: int = 256) -> None:
        if repeat < 1:
            raise ValueError("repeat must be positive")
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.rows: List[Dict[str, Any]] = []
        for index, (name, color, box) in enumerate(self._SPECS):
            image_path = self._create_image(index, color, box, image_size)
            answer = format_box(pixel_to_normalized(box, (image_size, image_size)))
            for repetition in range(repeat):
                prompt = self._prompt(name, repetition)
                self.rows.append(
                    {
                        "id": f"synthetic-{index}-{repetition}",
                        "messages": localization_messages(image_path, prompt, answer),
                        "answer": answer,
                        "image_paths": [str(image_path)],
                    }
                )

    def _create_image(
        self,
        index: int,
        color: Tuple[int, int, int],
        box: Tuple[int, int, int, int],
        image_size: int,
    ) -> Path:
        image_path = self.root / f"sample_{index}.png"
        image = Image.new("RGB", (image_size, image_size), "white")
        ImageDraw.Draw(image).rectangle(box, fill=color, outline="black", width=2)
        image.save(image_path)
        return image_path

    @staticmethod
    def _prompt(name: str, repetition: int) -> str:
        if repetition % 2 == 0:
            return (
                f"Locate the {name}. Return only its normalized "
                "[x1,y1,x2,y2] box in 0-1000 coordinates."
            )
        return (
            f"Give the 0-1000 normalized bounding box of the {name}; "
            "output only [x1,y1,x2,y2]."
        )

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> Dict[str, Any]:
        return self.rows[index]
