"""Read-only checkpoint helpers shared by training, evaluation, and screening."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import torch


def validate_checkpoint(path_value: Any) -> Path:
    checkpoint = Path(str(path_value)).resolve()
    adapter_weights = checkpoint / "adapter" / "adapter_model.safetensors"
    trainer_state = checkpoint / "trainer_state.pt"
    if not adapter_weights.is_file() or not trainer_state.is_file():
        raise FileNotFoundError(
            "checkpoint must contain adapter/adapter_model.safetensors and "
            f"trainer_state.pt: {checkpoint}"
        )
    return checkpoint


def load_adapter_checkpoint(wrapper: Any, path_value: Any) -> Path:
    """Load adapter tensors into the already-constructed PEFT model."""
    checkpoint = validate_checkpoint(path_value)
    from peft.utils.save_and_load import set_peft_model_state_dict
    from safetensors.torch import load_file

    target = getattr(wrapper, "peft_model", None)
    if target is None:
        target = wrapper.model.module if hasattr(wrapper.model, "module") else wrapper.model
    incompatible = set_peft_model_state_dict(
        target,
        load_file(
            str(checkpoint / "adapter" / "adapter_model.safetensors"),
            device="cpu",
        ),
        adapter_name="default",
    )
    if incompatible.unexpected_keys:
        raise RuntimeError(
            "checkpoint adapter has unexpected keys: "
            f"{list(incompatible.unexpected_keys)[:5]}"
        )
    return checkpoint


def load_trainer_progress(path_value: Any) -> Dict[str, Any]:
    checkpoint = validate_checkpoint(path_value)
    state = torch.load(checkpoint / "trainer_state.pt", map_location="cpu")
    if state.get("format_version") != 1:
        raise ValueError(
            f"unsupported trainer checkpoint format: {state.get('format_version')}"
        )
    return {
        "step": int(state["step"]),
        "samples_seen": int(state["samples_seen"]),
    }
