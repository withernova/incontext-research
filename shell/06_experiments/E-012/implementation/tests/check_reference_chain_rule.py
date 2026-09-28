"""Numerical check of the installed Qwen3-VL eager attention kernel.

Uses synthetic Q/K/V and downstream token CE, without a checkpoint or images.
This is an attention-kernel diagnostic, not completion of the R-004 model run.
Only the installed repeat_kv/eager_attention_forward functions are loaded; this
does not claim that the full transformers model can currently be imported.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from types import SimpleNamespace

import torch
import torch.nn.functional as F


def load_installed_kernel():
    spec = importlib.util.find_spec("transformers")
    if spec is None or spec.origin is None:
        raise RuntimeError("transformers package is required")
    source_path = Path(spec.origin).parent / "models/qwen3_vl/modeling_qwen3_vl.py"
    source = source_path.read_bytes()
    tree = ast.parse(source)
    names = {"repeat_kv", "eager_attention_forward"}
    nodes = [node for node in tree.body
             if isinstance(node, ast.FunctionDef) and node.name in names]
    if {node.name for node in nodes} != names:
        raise RuntimeError("installed Qwen3-VL kernel functions were not found")
    future = ast.ImportFrom(module="__future__",
                            names=[ast.alias(name="annotations")], level=0)
    isolated = ast.fix_missing_locations(ast.Module(body=[future] + nodes, type_ignores=[]))
    namespace = {"torch": torch, "nn": torch.nn}
    exec(compile(isolated, str(source_path), "exec"), namespace)
    return (namespace["eager_attention_forward"], namespace["repeat_kv"],
            hashlib.sha256(source).hexdigest())


def error_summary(left, right, *, atol, rtol):
    left, right = left.detach().double(), right.detach().double()
    error = (left - right).abs()
    scale = torch.maximum(left.abs(), right.abs())
    informative = scale > 1e-8
    relative = error[informative] / scale[informative]
    return {
        "n_edges": left.numel(),
        "max_abs_error": error.max().item(),
        "max_relative_error_above_1e_8": relative.max().item() if relative.numel() else None,
        "relative_l2_error": (error.norm() / scale.norm().clamp_min(1e-30)).item(),
        "pass": bool(torch.all(error <= atol + rtol * scale)),
    }


def check_case(kernel, repeat_kv, *, seed, dtype):
    generator = torch.Generator(device="cpu").manual_seed(seed)
    batch, heads, kv_heads, tokens, dim, vocab = 1, 4, 2, 16, 8, 19
    rows = slice(12, 16)
    reference = slice(2, 8)

    def normal(shape):
        return torch.randn(shape, generator=generator, dtype=torch.float64).to(dtype)

    query = normal((batch, heads, tokens, dim)).requires_grad_(True)
    key = normal((batch, kv_heads, tokens, dim))
    value = normal((batch, kv_heads, tokens, dim))
    mask = torch.full((tokens, tokens), float("-inf"), dtype=dtype).triu(1)[None, None]
    module = SimpleNamespace(num_key_value_groups=heads // kv_heads, training=False)
    output, attention = kernel(module, query, key, value, mask,
                               scaling=1.0 / math.sqrt(dim), dropout=0.0)
    expanded_value = repeat_kv(value, heads // kv_heads)
    projection = normal((heads * dim, vocab)) / math.sqrt(heads * dim)
    labels = torch.tensor([2, 5, 11, 17])

    def loss_from_output(head_output):
        hidden = head_output[0, rows].reshape(4, heads * dim)
        logits = torch.tanh(hidden) @ projection
        return F.cross_entropy(logits, labels, reduction="mean")

    loss = loss_from_output(output)
    grad_attention, grad_output = torch.autograd.grad(loss, (attention, output))
    a = attention[0, :, rows, reference].detach()
    e_attention = a * grad_attention[0, :, rows, reference]
    av = a[..., None] * expanded_value[0, :, reference, :][:, None, :, :]
    go = grad_output[0, rows].permute(1, 0, 2)
    e_value = (go[:, :, None, :] * av).sum(-1)
    atol, rtol = ((1e-12, 1e-9) if dtype == torch.float64 else (1e-8, 1e-4))
    algebra = error_summary(e_attention, e_value, atol=atol, rtol=rtol)

    frozen_a, frozen_v = attention.detach(), expanded_value.detach()

    def replay(epsilon, region):
        scaled = frozen_a * (1.0 - epsilon * region)
        replay_output = (scaled @ frozen_v).transpose(1, 2).contiguous()
        return loss_from_output(replay_output).item()

    finite_differences = []
    for head in (0, 3):
        for region_name in ("one_reference_edge", "reference_span"):
            region = torch.zeros_like(frozen_a)
            if region_name == "one_reference_edge":
                region[0, head, 12, 2] = 1
            else:
                region[0, head, rows, reference] = 1
            predicted = -(frozen_a * grad_attention * region).sum().item()
            baseline = replay(0.0, region)
            for epsilon in (1e-3, 1e-2):
                minus = replay(-epsilon, region)
                plus = replay(epsilon, region)
                central = (plus - minus) / (2.0 * epsilon)
                forward = (plus - baseline) / epsilon
                absolute_error = abs(central - predicted)
                rounding = (1e-10 if dtype == torch.float64 else 8.0 * torch.finfo(dtype).eps
                            * max(abs(plus), abs(minus), 1.0) / (2.0 * epsilon))
                sign_resolvable = abs(predicted) > rounding
                finite_differences.append({
                    "head": head, "region": region_name, "epsilon": epsilon,
                    "predicted_dloss_dremoval": predicted,
                    "central_difference": central, "forward_difference": forward,
                    "absolute_error": absolute_error,
                    "relative_error": absolute_error / max(abs(predicted), abs(central), 1e-12),
                    "rounding_floor": rounding,
                    "sign_resolvable": sign_resolvable,
                    "sign_agreement": (central * predicted > 0) if sign_resolvable else None,
                    "pass": absolute_error <= rounding + 0.01 * abs(predicted),
                    "baseline_replay_abs_error": abs(baseline - loss.item()),
                })
    return {
        "seed": seed, "dtype": str(dtype), "loss": loss.item(),
        "algebra": algebra,
        "reference_abs_contribution_per_head": e_attention.abs().sum((1, 2)).tolist(),
        "finite_differences": finite_differences,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="JSON destination, or '-' for stdout without remote writes")
    args = parser.parse_args()
    stdout_only = args.output == Path("-")
    if not stdout_only and args.output.exists():
        raise FileExistsError(args.output)
    torch.set_num_threads(1)
    kernel, repeat_kv, source_hash = load_installed_kernel()
    records = [check_case(kernel, repeat_kv, seed=20260914 + index, dtype=dtype)
               for dtype in (torch.float64, torch.float32) for index in range(8)]
    summary = {}
    for dtype in ("torch.float64", "torch.float32"):
        selected = [record for record in records if record["dtype"] == dtype]
        fd = [value for record in selected for value in record["finite_differences"]]
        resolved = [value for value in fd if value["sign_resolvable"]]
        summary[dtype] = {
            "n_synthetic_samples": len(selected),
            "n_reference_edges": sum(record["algebra"]["n_edges"] for record in selected),
            "algebra_pass": all(record["algebra"]["pass"] for record in selected),
            "max_algebra_abs_error": max(record["algebra"]["max_abs_error"] for record in selected),
            "max_algebra_relative_l2_error": max(record["algebra"]["relative_l2_error"] for record in selected),
            "n_finite_differences": len(fd),
            "finite_difference_pass": all(value["pass"] for value in fd),
            "n_sign_resolvable": len(resolved),
            "n_sign_agreement": sum(value["sign_agreement"] for value in resolved),
            "max_finite_difference_abs_error": max(value["absolute_error"] for value in fd),
            "max_baseline_replay_abs_error": max(value["baseline_replay_abs_error"] for value in fd),
        }
    result = {
        "schema": "e012.reference-chain-rule-kernel-check/v1",
        "scope": "installed eager kernel; synthetic Q/K/V and token CE; CPU",
        "real_checkpoint_tested": False, "real_images_tested": False,
        "full_model_import_tested": False,
        "torch_version": torch.__version__, "kernel_source_sha256": source_hash,
        "reference_key_range": [2, 8], "prediction_row_range": [12, 16],
        "summary": summary, "records": records,
    }
    if stdout_only:
        print(json.dumps(result, indent=2, allow_nan=False))
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
        print(json.dumps({"scope": result["scope"], "summary": summary}, indent=2))
    return 0 if all(item["algebra_pass"] and item["finite_difference_pass"]
                    for item in summary.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
