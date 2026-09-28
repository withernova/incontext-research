"""Qwen3-VL base-model loading and language-side LoRA attachment."""

from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import torch

from ..compat import ensure_torchvision_nms_schema
from ..registry import MODELS


@MODELS.register_module()
class Qwen3VLLoRASFT:
    """Own a Qwen3-VL processor and a LoRA-adapted causal language model.

    The caller supplies the target-module expression explicitly in config. The
    project default excludes ``visual`` modules and follows the target pattern
    used by the existing IPLoc-ID Qwen3-VL adapters.
    """

    def __init__(
        self,
        model_path: str,
        lora: Dict[str, Any],
        dtype: str = "bfloat16",
        device_map: Any = "auto",
        max_memory: Optional[Dict[int, str]] = None,
        attn_implementation: Optional[str] = None,
        gradient_checkpointing: bool = True,
        gradient_checkpointing_kwargs: Optional[Dict[str, Any]] = None,
        local_files_only: bool = True,
    ) -> None:
        ensure_torchvision_nms_schema()
        from peft import LoraConfig, get_peft_model
        from transformers import AutoProcessor, Qwen3VLForConditionalGeneration

        self.model_path = str(model_path)
        torch_dtype = getattr(torch, dtype, None)
        if torch_dtype is None:
            raise ValueError(f"torch has no dtype named {dtype!r}")

        self.processor = AutoProcessor.from_pretrained(
            self.model_path,
            local_files_only=local_files_only,
        )
        base_model = Qwen3VLForConditionalGeneration.from_pretrained(
            self.model_path,
            dtype=torch_dtype,
            device_map=device_map,
            max_memory=max_memory,
            attn_implementation=attn_implementation,
            local_files_only=local_files_only,
        )
        base_model.config.use_cache = False
        if gradient_checkpointing:
            base_model.gradient_checkpointing_enable(
                gradient_checkpointing_kwargs=gradient_checkpointing_kwargs
            )
            # Reentrant checkpointing needs a differentiable input even though
            # embeddings and base weights remain frozen by PEFT. Non-reentrant
            # checkpointing records the autograd graph and does not need this hook.
            if not gradient_checkpointing_kwargs or gradient_checkpointing_kwargs.get(
                "use_reentrant", True
            ):
                base_model.enable_input_require_grads()

        lora_config = LoraConfig(
            task_type="CAUSAL_LM",
            r=lora.get("r", 8),
            lora_alpha=lora.get("alpha", 16),
            lora_dropout=lora.get("dropout", 0.0),
            bias="none",
            target_modules=lora["target_modules"],
        )
        self.model = get_peft_model(base_model, lora_config)
        self._validate_trainable_parameters()

    @property
    def input_device(self) -> torch.device:
        """Return the device that should receive tokenized model inputs."""
        return self.model.get_input_embeddings().weight.device

    def trainable_parameters(self) -> Iterable[torch.nn.Parameter]:
        """Yield only parameters selected for optimization by PEFT."""
        return [parameter for parameter in self.model.parameters() if parameter.requires_grad]

    def save_adapter(self, path: str) -> None:
        """Save the adapter and matching processor without base weights."""
        adapter_path = Path(path)
        self.model.save_pretrained(adapter_path, safe_serialization=True)
        self.processor.save_pretrained(f"{adapter_path}_processor")

    def _validate_trainable_parameters(self) -> None:
        trainable_names = [
            name for name, parameter in self.model.named_parameters() if parameter.requires_grad
        ]
        if not trainable_names:
            raise RuntimeError("LoRA attachment produced zero trainable parameters")
        non_lora_names = [name for name in trainable_names if "lora_" not in name]
        if non_lora_names:
            raise RuntimeError(
                "expected LoRA-only training, but found non-LoRA parameters: "
                f"{non_lora_names[:5]}"
            )
