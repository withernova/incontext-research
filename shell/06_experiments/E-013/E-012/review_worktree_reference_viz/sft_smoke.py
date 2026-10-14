#!/usr/bin/env python3
"""Minimal Qwen3-VL LoRA SFT capability smoke for E-009.

The runner creates deterministic synthetic localization samples, masks all
non-assistant tokens, performs a few LoRA-only optimizer steps, saves the
adapter, reloads it on the same base model, and writes an auditable metrics.json.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import time
import traceback
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--model-path", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--steps", type=int, default=3)
    p.add_argument("--learning-rate", type=float, default=1e-3)
    p.add_argument("--seed", type=int, default=20260825)
    p.add_argument("--max-memory-gib", type=int, default=22)
    p.add_argument("--self-check", action="store_true")
    return p.parse_args()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def make_dataset(root: Path) -> list[dict[str, Any]]:
    from PIL import Image, ImageDraw

    image_dir = root / "synthetic_images"
    image_dir.mkdir(parents=True, exist_ok=True)
    specs = [
        ("red square", (255, 40, 40), (32, 48, 112, 128)),
        ("green rectangle", (40, 210, 80), (80, 24, 176, 88)),
        ("blue square", (30, 90, 240), (112, 112, 208, 208)),
        ("yellow rectangle", (235, 205, 35), (24, 144, 136, 216)),
    ]
    rows: list[dict[str, Any]] = []
    for i, (name, color, box) in enumerate(specs):
        path = image_dir / f"sample_{i}.png"
        image = Image.new("RGB", (256, 256), "white")
        ImageDraw.Draw(image).rectangle(box, fill=color, outline="black", width=2)
        image.save(path)
        norm = [round(v / 256 * 1000) for v in box]
        answer = "[" + ",".join(map(str, norm)) + "]"
        for wording in (
            f"Locate the {name}. Return only its normalized [x1,y1,x2,y2] box in 0-1000 coordinates.",
            f"Give the 0-1000 normalized bounding box of the {name}; output only [x1,y1,x2,y2].",
        ):
            rows.append({"image": str(path), "prompt": wording, "answer": answer})
    write_json(root / "dataset.json", rows)
    return rows


def messages_for(row: dict[str, Any], include_answer: bool) -> list[dict[str, Any]]:
    messages = [{
        "role": "user",
        "content": [
            {"type": "image", "image": row["image"]},
            {"type": "text", "text": row["prompt"]},
        ],
    }]
    if include_answer:
        messages.append({"role": "assistant", "content": [{"type": "text", "text": row["answer"]}]})
    return messages


def encode_supervised(processor: Any, row: dict[str, Any]) -> dict[str, Any]:
    from PIL import Image

    image = Image.open(row["image"]).convert("RGB")
    prefix_text = processor.apply_chat_template(
        messages_for(row, False), tokenize=False, add_generation_prompt=True
    )
    full_text = processor.apply_chat_template(
        messages_for(row, True), tokenize=False, add_generation_prompt=False
    )
    prefix = processor(text=[prefix_text], images=[image], padding=True, return_tensors="pt")
    full = processor(text=[full_text], images=[image], padding=True, return_tensors="pt")
    prefix_ids = prefix["input_ids"][0]
    full_ids = full["input_ids"][0]
    if len(prefix_ids) >= len(full_ids):
        raise RuntimeError(f"assistant target is empty: prefix={len(prefix_ids)} full={len(full_ids)}")
    if not bool((prefix_ids == full_ids[: len(prefix_ids)]).all()):
        raise RuntimeError("generation-prefix tokens are not a prefix of the supervised sequence")
    labels = full["input_ids"].clone()
    labels[:, : len(prefix_ids)] = -100
    full["labels"] = labels
    answer_tokens = int((labels != -100).sum().item())
    if answer_tokens <= 0:
        raise RuntimeError("no supervised assistant tokens")
    full["answer_token_count"] = answer_tokens
    full["prefix_token_count"] = int(len(prefix_ids))
    return full


def move_batch(batch: dict[str, Any], device: Any) -> dict[str, Any]:
    return {
        k: v.to(device) for k, v in batch.items()
        if k not in {"answer_token_count", "prefix_token_count"}
    }


def tensor_norm(parameters: list[Any]) -> float:
    return math.sqrt(sum(float(p.detach().float().square().sum().item()) for p in parameters))


def train(args: argparse.Namespace, out: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    import torch
    from peft import LoraConfig, PeftModel, get_peft_model
    from transformers import AutoProcessor, Qwen3VLForConditionalGeneration

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for the full smoke")
    if torch.cuda.device_count() != 2:
        raise RuntimeError(f"expected exactly two visible GPUs, got {torch.cuda.device_count()}")
    model_path = Path(args.model_path)
    shards = sorted(model_path.glob("model-*-of-*.safetensors"))
    if len(shards) != 10:
        raise RuntimeError(f"expected 10 model shards, found {len(shards)}")

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    processor = AutoProcessor.from_pretrained(model_path, local_files_only=True)
    encoded = encode_supervised(processor, rows[0])
    metadata = {
        "answer_token_count": encoded.pop("answer_token_count"),
        "prefix_token_count": encoded.pop("prefix_token_count"),
        "sequence_length": int(encoded["input_ids"].shape[1]),
    }

    max_memory = {i: f"{args.max_memory_gib}GiB" for i in range(2)}
    load_started = time.time()
    model = Qwen3VLForConditionalGeneration.from_pretrained(
        model_path,
        dtype=torch.bfloat16,
        device_map="auto",
        max_memory=max_memory,
        local_files_only=True,
    )
    model.config.use_cache = False
    model.gradient_checkpointing_enable()
    model.enable_input_require_grads()
    lora_config = LoraConfig(
        task_type="CAUSAL_LM",
        r=8,
        lora_alpha=16,
        lora_dropout=0.0,
        bias="none",
        target_modules=r"^(?!.*visual).*(?:down_proj|v_proj|gate_proj|up_proj|k_proj|o_proj|q_proj).*$",
    )
    model = get_peft_model(model, lora_config)
    model.train()
    trainable = [(n, p) for n, p in model.named_parameters() if p.requires_grad]
    if not trainable or any("lora_" not in n for n, _ in trainable):
        raise RuntimeError("trainable parameter gate failed: expected LoRA-only parameters")
    lora_params = [p for _, p in trainable]
    before = [p.detach().float().cpu().clone() for p in lora_params]
    optimizer = torch.optim.AdamW(lora_params, lr=args.learning_rate, weight_decay=0.0)
    input_device = model.get_input_embeddings().weight.device
    batch = move_batch(encoded, input_device)

    model.eval()
    with torch.no_grad():
        loss_before = float(model(**batch).loss.float().item())
    if not math.isfinite(loss_before):
        raise RuntimeError("non-finite baseline loss")

    losses: list[float] = []
    finite_grad_fractions: list[float] = []
    model.train()
    for step in range(args.steps):
        optimizer.zero_grad(set_to_none=True)
        loss = model(**batch).loss
        if not bool(torch.isfinite(loss)):
            raise RuntimeError(f"non-finite loss at step {step + 1}")
        loss.backward()
        grads = [p.grad for p in lora_params if p.grad is not None]
        if not grads:
            raise RuntimeError(f"no LoRA gradients at step {step + 1}")
        finite_fraction = sum(bool(torch.isfinite(g).all()) for g in grads) / len(grads)
        if finite_fraction != 1.0:
            raise RuntimeError(f"non-finite LoRA gradients at step {step + 1}")
        optimizer.step()
        losses.append(float(loss.detach().float().item()))
        finite_grad_fractions.append(finite_fraction)
        print(f"[STEP] {step + 1}/{args.steps} loss={losses[-1]:.6f}", flush=True)

    model.eval()
    with torch.no_grad():
        loss_after = float(model(**batch).loss.float().item())
    delta_sq = 0.0
    for old, param in zip(before, lora_params):
        delta_sq += float((param.detach().float().cpu() - old).square().sum().item())
    adapter_delta_norm = math.sqrt(delta_sq)
    adapter_dir = out / "adapter"
    model.save_pretrained(adapter_dir, safe_serialization=True)
    processor.save_pretrained(out / "processor")
    peak = [torch.cuda.max_memory_allocated(i) / 2**30 for i in range(2)]
    del optimizer, model
    torch.cuda.empty_cache()

    base = Qwen3VLForConditionalGeneration.from_pretrained(
        model_path,
        dtype=torch.bfloat16,
        device_map="auto",
        max_memory=max_memory,
        local_files_only=True,
    )
    reloaded = PeftModel.from_pretrained(base, adapter_dir).eval()
    reload_device = reloaded.get_input_embeddings().weight.device
    reload_batch = move_batch(encoded, reload_device)
    with torch.no_grad():
        reload_loss = float(reloaded(**reload_batch).loss.float().item())
    reload_diff = abs(reload_loss - loss_after)
    gates = {
        "two_visible_gpus": torch.cuda.device_count() == 2,
        "ten_model_shards": len(shards) == 10,
        "assistant_tokens_present": metadata["answer_token_count"] > 0,
        "finite_baseline_loss": math.isfinite(loss_before),
        "steps_completed": len(losses) >= 3,
        "finite_gradients": min(finite_grad_fractions) == 1.0,
        "lora_only_trainable": bool(trainable) and all("lora_" in n for n, _ in trainable),
        "adapter_changed": adapter_delta_norm > 0,
        "adapter_files_present": (adapter_dir / "adapter_config.json").is_file() and any(adapter_dir.glob("adapter_model.*")),
        "reload_loss_close": reload_diff <= 1e-4,
        "loss_decreased": loss_after < loss_before,
    }
    return {
        "status": "passed" if all(gates.values()) else "gate_failed",
        "gates": gates,
        "model_path": str(model_path),
        "visible_gpu_count": torch.cuda.device_count(),
        "visible_gpu_names": [torch.cuda.get_device_name(i) for i in range(2)],
        "steps": len(losses),
        "loss_before": loss_before,
        "step_losses": losses,
        "loss_after": loss_after,
        "adapter_delta_norm": adapter_delta_norm,
        "reload_loss": reload_loss,
        "reload_loss_abs_diff": reload_diff,
        "finite_grad_fraction": min(finite_grad_fractions),
        "peak_gpu_memory_gib": peak,
        "trainable_parameter_count": sum(p.numel() for _, p in trainable),
        "trainable_tensor_count": len(trainable),
        "load_seconds": time.time() - load_started,
        **metadata,
    }


def main() -> int:
    args = parse_args()
    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    rows = make_dataset(out)
    config = vars(args).copy()
    config["model_path"] = str(Path(args.model_path).resolve())
    config["output_dir"] = str(out)
    write_json(out / "config.json", config)
    if args.self_check:
        assert len(rows) == 8
        assert len({r["image"] for r in rows}) == 4
        assert all(r["answer"].startswith("[") and r["answer"].endswith("]") for r in rows)
        result = {"status": "self_check_passed", "samples": len(rows), "images": 4}
        write_json(out / "metrics.json", result)
        print("[SELF_CHECK_PASS]", json.dumps(result), flush=True)
        return 0
    try:
        result = train(args, out, rows)
    except Exception as exc:
        result = {"status": "failed", "error_type": type(exc).__name__, "error": str(exc), "traceback": traceback.format_exc()}
        write_json(out / "metrics.json", result)
        print("[FAILED]", json.dumps({k: v for k, v in result.items() if k != "traceback"}), flush=True)
        return 1
    write_json(out / "metrics.json", result)
    print("[DONE]", json.dumps(result), flush=True)
    return 0 if result["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
