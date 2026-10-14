from PIL import Image

from ..registry import DATASETS
from ..prompting.coordinates import coordinate_field_char_spans


@DATASETS.register_module()
class Qwen3VLSFTCollator:
    """Batch Qwen3-VL conversations and supervise assistant suffixes only."""

    def __init__(self, processor, assistant_only=True, vision_max_patch_tokens=None):
        self.processor = processor
        self.assistant_only = assistant_only
        if vision_max_patch_tokens is not None and (
            not isinstance(vision_max_patch_tokens, int)
            or isinstance(vision_max_patch_tokens, bool)
            or vision_max_patch_tokens <= 0
        ):
            raise ValueError("vision_max_patch_tokens must be a positive integer or None")
        self.vision_max_patch_tokens = vision_max_patch_tokens
        patch_size = getattr(self.processor.image_processor, "patch_size", None)
        if not isinstance(patch_size, int) or patch_size <= 0:
            raise ValueError("processor image patch_size must be a positive integer")
        self.vision_max_pixels = (
            None if vision_max_patch_tokens is None
            else vision_max_patch_tokens * patch_size * patch_size
        )
        # transformers 4.57 does not forward processor-level max_pixels to the
        # fast Qwen image processor. Set its canonical longest_edge instead.
        if self.vision_max_pixels is not None:
            self.processor.image_processor.size["longest_edge"] = self.vision_max_pixels

    def _processor_kwargs(self):
        return {}

    def _bbox_token_alignment(self, full_text, full_ids, answer, prefix_tokens):
        """Locate bbox and numeric-field tokens in the rendered conversation."""
        start = full_text.rfind(answer)
        if start < 0:
            raise ValueError("normalized bbox answer is absent from rendered conversation")
        stop = start + len(answer)
        tokenized = self.processor.tokenizer(
            full_text,
            add_special_tokens=False,
            return_offsets_mapping=True,
        )
        bbox_token_indices = [
            index for index, (left, right) in enumerate(tokenized["offset_mapping"])
            if right > start and left < stop
        ]
        bbox_ids = [tokenized["input_ids"][index] for index in bbox_token_indices]
        if not bbox_ids:
            raise ValueError("rendered bbox answer has no overlapping tokens")
        values = full_ids.tolist()
        matches = [
            index
            for index in range(prefix_tokens, len(values) - len(bbox_ids) + 1)
            if values[index:index + len(bbox_ids)] == bbox_ids
        ]
        if len(matches) != 1:
            raise ValueError(f"expected one rendered bbox token alignment, found {matches}")
        bbox_positions = list(range(matches[0], matches[0] + len(bbox_ids)))
        text_to_sequence = dict(zip(bbox_token_indices, bbox_positions))
        coordinate_positions = {}
        for field, (left, right) in coordinate_field_char_spans(answer).items():
            field_start, field_stop = start + left, start + right
            positions = [
                text_to_sequence[index]
                for index in bbox_token_indices
                if tokenized["offset_mapping"][index][1] > field_start
                and tokenized["offset_mapping"][index][0] < field_stop
            ]
            if not positions:
                raise ValueError(f"coordinate field {field} has no aligned token")
            coordinate_positions[field] = positions
        flattened = [position for field in ("x1", "y1", "x2", "y2")
                     for position in coordinate_positions[field]]
        if len(flattened) != len(set(flattened)):
            raise ValueError(
                "a tokenizer token overlaps multiple coordinate fields; "
                "coordinate-only supervision is ambiguous"
            )
        return bbox_positions, coordinate_positions

    def _bbox_token_positions(self, full_text, full_ids, answer, prefix_tokens):
        """Backward-compatible full-answer bbox token positions."""
        return self._bbox_token_alignment(
            full_text, full_ids, answer, prefix_tokens
        )[0]

    def _render(self, sample):
        full = sample["messages"]
        if not full or full[-1]["role"] != "assistant":
            raise ValueError("SFT sample must end with assistant")
        prefix = full[:-1]
        images = [Image.open(path).convert("RGB") for path in sample["image_paths"]]
        prefix_text = self.processor.apply_chat_template(prefix, tokenize=False, add_generation_prompt=True)
        full_text = self.processor.apply_chat_template(full, tokenize=False, add_generation_prompt=False)
        kwargs = self._processor_kwargs()
        prefix_encoded = self.processor(text=[prefix_text], images=images, padding=False, return_tensors="pt", **kwargs)
        full_encoded = self.processor(text=[full_text], images=images, padding=False, return_tensors="pt", **kwargs)
        prefix_ids = prefix_encoded["input_ids"][0]
        full_ids = full_encoded["input_ids"][0]
        if len(prefix_ids) >= len(full_ids):
            raise ValueError("assistant answer has zero tokens")
        if not bool((prefix_ids == full_ids[: len(prefix_ids)]).all()):
            raise ValueError("assistant prefix alignment failed")
        bbox_positions, coordinate_positions = self._bbox_token_alignment(
            full_text, full_ids, sample["answer"], len(prefix_ids)
        )
        return (
            full_text,
            images,
            len(prefix_ids),
            len(full_ids) - len(prefix_ids),
            bbox_positions,
            coordinate_positions,
        )

    def __call__(self, samples):
        if not samples:
            raise ValueError("cannot collate an empty batch")
        rendered = [self._render(sample) for sample in samples]
        texts, images = [x[0] for x in rendered], [x[1] for x in rendered]
        batch = self.processor(text=texts, images=images, padding=True, return_tensors="pt", **self._processor_kwargs())
        labels = batch["input_ids"].clone()
        labels.fill_(-100)
        grids = batch.get("image_grid_thw")
        cursor = 0
        metadata = []
        for row, (
            sample,
            (_, sample_images, prefix_tokens, answer_tokens, bbox_positions,
             coordinate_positions),
        ) in enumerate(zip(samples, rendered)):
            valid = batch["attention_mask"][row].nonzero(as_tuple=False).flatten()
            if len(valid) != prefix_tokens + answer_tokens:
                raise ValueError(f"batched token count changed for {sample['id']}: valid={len(valid)} expected={prefix_tokens + answer_tokens}")
            labels[row, valid[-answer_tokens:]] = batch["input_ids"][row, valid[-answer_tokens:]]
            sample_grids = grids[cursor:cursor + len(sample_images)] if grids is not None else None
            cursor += len(sample_images)
            metadata.append({"id": sample["id"], "prefix_tokens": prefix_tokens, "answer_tokens": answer_tokens,
                             "answer": sample["answer"],
                             "reference_answers": list(sample.get("reference_answers", [])),
                             "query_answer": sample.get("query_answer", sample["answer"]),
                             "group": sample.get("group", sample["id"]),
                             "image_paths": list(sample["image_paths"]),
                             "bbox_token_positions": [int(valid[position]) for position in bbox_positions],
                             "coordinate_token_positions": {
                                 field: [int(valid[position]) for position in positions]
                                 for field, positions in coordinate_positions.items()
                             },
                             "vision_max_patch_tokens": self.vision_max_patch_tokens,
                             "vision_max_pixels": self.vision_max_pixels,
                             "image_grid_thw": sample_grids.tolist() if sample_grids is not None else None,
                             "image_patch_tokens": sample_grids.prod(dim=1).tolist() if sample_grids is not None else None})
        batch["labels"] = labels
        batch["metadata"] = metadata
        return batch
