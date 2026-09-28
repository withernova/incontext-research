"""Adapter from legacy IPLoc JSON manifests to supervised conversations."""

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

from PIL import Image
from torch.utils.data import Dataset

from ..prompting.coordinates import format_box, parse_box, pixel_to_normalized
from ..prompting.messages import (
    focus_messages,
    iploc_messages,
    qwen3_grounding_messages,
)
from ..registry import DATASETS


def _unwrap(value: Any) -> Any:
    """Remove the singleton lists introduced by legacy DataLoader collation."""
    return value[0] if isinstance(value, list) and len(value) == 1 else value


def _image_size(path: str) -> Sequence[int]:
    """Read image dimensions while closing the file immediately."""
    with Image.open(path) as image:
        return image.size


@DATASETS.register_module()
class IPLocManifestDataset(Dataset):
    """Convert IPLoc records into reference-conditioned SFT samples.

    Expected record fields are ``element``, ``bbox``, and ``image_path``.
    ``role`` or ``data_role`` should identify reference and target entries. If
    omitted, all but the final image are treated as references and the final
    image as a positive target, matching the legacy IPLoc convention.
    """

    def __init__(
        self,
        ann_file: Union[str, Sequence[str]],
        target_role: str = "positive-image",
        normalized_scale: int = 1000,
        prompt_protocol: str = "focus",
        prompt_text: str = None,
        prompt_version: str = None,
        dataset_names: Optional[Sequence[str]] = None,
    ) -> None:
        if prompt_protocol not in {"focus", "iploc", "qwen3_grounding"}:
            raise ValueError(
                "prompt_protocol must be 'focus', 'iploc', or 'qwen3_grounding'"
            )
        if prompt_text is not None and (not isinstance(prompt_text, str) or not prompt_text.strip()):
            raise ValueError("prompt_text must be a non-empty string")
        if prompt_text is not None and prompt_protocol == "iploc":
            raise ValueError("custom prompt_text is supported for focus/qwen3_grounding only")
        self.prompt_options = {} if prompt_text is None else {"prompt": prompt_text}
        self.prompt_version = prompt_version
        if isinstance(ann_file, (str, Path)):
            ann_files = [str(ann_file)]
        else:
            ann_files = [str(path) for path in ann_file]
        if not ann_files:
            raise ValueError("ann_file must contain at least one manifest")
        self.ann_file = ann_files[0] if len(ann_files) == 1 else ann_files
        self.prompt_protocol = prompt_protocol
        selected_datasets = (
            None if dataset_names is None else {str(name) for name in dataset_names}
        )
        if selected_datasets == set():
            raise ValueError("dataset_names must contain at least one dataset")
        records = []
        available_datasets = set()
        for manifest_path in ann_files:
            manifest_records = json.loads(
                Path(manifest_path).read_text(encoding="utf-8")
            )
            if not isinstance(manifest_records, list):
                raise ValueError(f"IPLoc manifest must be a JSON list: {manifest_path}")
            available_datasets.update(
                str(record.get("dataset")) for record in manifest_records
            )
            records.extend(
                record for record in manifest_records
                if selected_datasets is None
                or str(record.get("dataset")) in selected_datasets
            )
        missing_datasets = (selected_datasets or set()) - available_datasets
        if missing_datasets:
            raise ValueError(
                f"dataset_names not present in manifests: {sorted(missing_datasets)}"
            )

        self.rows: List[Dict[str, Any]] = []
        for record_index, record in enumerate(records):
            self._append_record(
                record_index,
                record,
                target_role=target_role,
                normalized_scale=normalized_scale,
            )
        if not self.rows:
            raise ValueError("manifest produced zero target samples")

    def _append_record(
        self,
        record_index: int,
        record: Mapping[str, Any],
        *,
        target_role: str,
        normalized_scale: int,
    ) -> None:
        paths = [_unwrap(value) for value in record["image_path"]]
        boxes = [_unwrap(value) for value in record["bbox"]]
        raw_roles = record.get("role") or record.get("data_role")
        if raw_roles is None:
            raw_roles = ["reference"] * (len(paths) - 1) + [target_role]
        roles = [_unwrap(value) for value in raw_roles]

        if not (len(paths) == len(boxes) == len(roles)):
            raise ValueError(
                f"record {record_index} has inconsistent path/bbox/role lengths"
            )

        references: List[Dict[str, str]] = []
        for path, box, role in zip(paths, boxes, roles):
            if role == "reference":
                references.append(
                    {
                        "image": path,
                        "answer": self._normalized_answer(
                            path, box, normalized_scale
                        ),
                    }
                )

        for target_index, (path, box, role) in enumerate(zip(paths, boxes, roles)):
            if role != target_role:
                continue
            answer = self._normalized_answer(path, box, normalized_scale)
            self.rows.append(
                {
                    "id": f"{record_index}-{target_index}",
                    "messages": self._build_messages(
                        references,
                        path,
                        str(record["element"]),
                        answer,
                    ),
                    "prompt_protocol": self.prompt_protocol,
                    "prompt_version": self.prompt_version,
                    "answer": answer,
                    "reference_answers": [item["answer"] for item in references],
                    "query_answer": answer,
                    "group": (
                        record.get("source", {}).get("sequence_cluster")
                        if isinstance(record.get("source"), Mapping)
                        else None
                    ) or str(record["element"]),
                    "image_paths": [item["image"] for item in references] + [path],
                    "raw": dict(record),
                }
            )

    def _build_messages(
        self,
        references: Sequence[Mapping[str, str]],
        query_path: str,
        element: str,
        answer: str,
    ) -> List[Dict[str, Any]]:
        """Dispatch to the explicitly configured paper protocol."""
        if self.prompt_protocol == "focus":
            return focus_messages(references, query_path, answer, **self.prompt_options)
        if self.prompt_protocol == "qwen3_grounding":
            return qwen3_grounding_messages(
                references, query_path, element, answer, **self.prompt_options
            )
        return iploc_messages(references, query_path, element, answer)

    @staticmethod
    def _normalized_answer(path: str, box: Any, scale: int) -> str:
        parsed_box = parse_box(box)
        if parsed_box is None:
            raise ValueError(f"cannot parse bbox {box!r} for {path}")
        normalized = pixel_to_normalized(parsed_box, _image_size(path), scale)
        return format_box(normalized)

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> Dict[str, Any]:
        return self.rows[index]
