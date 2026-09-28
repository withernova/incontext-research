"""Native Qwen3-VL inference wrapper without PEFT or trainable adapters."""

from typing import Any, Dict, Optional

import torch

from ..compat import ensure_torchvision_nms_schema
from ..registry import MODELS


@MODELS.register_module()
class Qwen3VLNative:
    """Load an unchanged Qwen3-VL checkpoint for autoregressive inference."""

    def __init__(
        self,
        model_path: str,
        dtype: str = "bfloat16",
        device_map: Any = "auto",
        max_memory: Optional[Dict[int, str]] = None,
        attn_implementation: Optional[str] = None,
        local_files_only: bool = True,
    ) -> None:
        ensure_torchvision_nms_schema()
        from transformers import AutoProcessor, Qwen3VLForConditionalGeneration

        torch_dtype = getattr(torch, dtype, None)
        if torch_dtype is None:
            raise ValueError(f"torch has no dtype named {dtype!r}")
        self.model_path = str(model_path)
        self.processor = AutoProcessor.from_pretrained(
            self.model_path,
            local_files_only=local_files_only,
        )
        self.model = Qwen3VLForConditionalGeneration.from_pretrained(
            self.model_path,
            dtype=torch_dtype,
            device_map=device_map,
            max_memory=max_memory,
            attn_implementation=attn_implementation,
            local_files_only=local_files_only,
        ).eval()
        self.model.config.use_cache = True

    @property
    def input_device(self) -> torch.device:
        return self.model.get_input_embeddings().weight.device
