"""Qwen3-VL LoRA wrapper with one complete model replica per DDP rank."""

from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import torch
from torch.nn.parallel import DistributedDataParallel

from ..compat import ensure_torchvision_nms_schema
from ..registry import MODELS
from ..utils.distributed import DistributedContext, initialize_distributed


@MODELS.register_module()
class Qwen3VLLoRADDP:
    """Load a complete Qwen3-VL model on each rank and synchronize LoRA gradients.

    Unlike ``Qwen3VLLoRASFT``, this wrapper never uses ``device_map=auto``. Each
    torchrun process binds to exactly one visible GPU, loads a full frozen base
    model there, attaches language-side LoRA, then wraps the PEFT model in DDP.
    Only LoRA gradients are communicated between ranks.
    """

    def __init__(
        self,
        model_path: str,
        lora: Dict[str, Any],
        dtype: str = "bfloat16",
        gradient_checkpointing: bool = True,
        gradient_checkpointing_kwargs: Optional[Dict[str, Any]] = None,
        attn_implementation: Optional[str] = None,
        quantization: Optional[Dict[str, Any]] = None,
        local_files_only: bool = True,
        find_unused_parameters: bool = False,
    ) -> None:
        ensure_torchvision_nms_schema()
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from transformers import AutoProcessor, Qwen3VLForConditionalGeneration

        self.context: DistributedContext = initialize_distributed()
        if self.context.device.type != "cuda":
            raise RuntimeError("the full-model DDP wrapper requires CUDA")
        self.model_path = str(model_path)
        torch_dtype = getattr(torch, dtype, None)
        if torch_dtype is None:
            raise ValueError(f"torch has no dtype named {dtype!r}")

        self.processor = AutoProcessor.from_pretrained(
            self.model_path,
            local_files_only=local_files_only,
        )
        model_kwargs: Dict[str, Any] = dict(
            dtype=torch_dtype,
            # A concrete device prevents Accelerate from sharding this replica.
            device_map={"": self.context.local_rank},
            attn_implementation=attn_implementation,
            local_files_only=local_files_only,
        )
        if quantization:
            if not quantization.get("load_in_4bit", False):
                raise ValueError("only load_in_4bit quantization is supported")
            from transformers import BitsAndBytesConfig

            compute_dtype_name = quantization.get("bnb_4bit_compute_dtype", dtype)
            compute_dtype = getattr(torch, compute_dtype_name, None)
            if compute_dtype is None:
                raise ValueError(
                    "torch has no 4-bit compute dtype named "
                    f"{compute_dtype_name!r}"
                )
            model_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type=quantization.get("bnb_4bit_quant_type", "nf4"),
                bnb_4bit_use_double_quant=quantization.get(
                    "bnb_4bit_use_double_quant", True
                ),
                bnb_4bit_compute_dtype=compute_dtype,
            )
        base_model = Qwen3VLForConditionalGeneration.from_pretrained(
            self.model_path,
            **model_kwargs,
        )
        base_model.config.use_cache = False
        if quantization:
            base_model = prepare_model_for_kbit_training(
                base_model,
                use_gradient_checkpointing=gradient_checkpointing,
                gradient_checkpointing_kwargs=gradient_checkpointing_kwargs,
            )
        elif gradient_checkpointing:
            base_model.gradient_checkpointing_enable(
                gradient_checkpointing_kwargs=gradient_checkpointing_kwargs
            )
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
        peft_model = get_peft_model(base_model, lora_config)
        self._validate_trainable_parameters(peft_model)
        self.peft_model = peft_model
        self.model = DistributedDataParallel(
            peft_model,
            device_ids=[self.context.local_rank],
            output_device=self.context.local_rank,
            find_unused_parameters=find_unused_parameters,
        )

    @property
    def input_device(self) -> torch.device:
        """Return this rank's single CUDA device."""
        return self.context.device

    @property
    def is_main_process(self) -> bool:
        """Return whether this rank owns shared output artifacts."""
        return self.context.is_main_process

    def trainable_parameters(self) -> Iterable[torch.nn.Parameter]:
        """Return the LoRA parameters optimized and synchronized by DDP."""
        return [
            parameter
            for parameter in self.peft_model.parameters()
            if parameter.requires_grad
        ]

    def save_adapter(self, path: str) -> None:
        """Save one adapter copy on rank zero; other ranks perform no I/O."""
        if not self.is_main_process:
            return
        adapter_path = Path(path)
        self.peft_model.save_pretrained(adapter_path, safe_serialization=True)
        self.processor.save_pretrained(f"{adapter_path}_processor")

    @staticmethod
    def _validate_trainable_parameters(model: torch.nn.Module) -> None:
        names = [
            name for name, parameter in model.named_parameters() if parameter.requires_grad
        ]
        if not names:
            raise RuntimeError("LoRA attachment produced zero trainable parameters")
        invalid = [name for name in names if "lora_" not in name]
        if invalid:
            raise RuntimeError(f"non-LoRA trainable parameters found: {invalid[:5]}")
