"""Exact differentiable selected-row attention for installed Qwen3-VL text layers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple

import torch


Head = Tuple[int, int]


def parse_head(value: Any) -> Head:
    """Parse ``L20H15`` or a two-integer sequence into a zero-based head pair."""
    if isinstance(value, str):
        text = value.strip().upper()
        if not (text.startswith("L") and "H" in text):
            raise ValueError(f"invalid head label: {value!r}")
        layer_text, head_text = text[1:].split("H", 1)
        pair = (int(layer_text), int(head_text))
    elif isinstance(value, Sequence) and len(value) == 2:
        pair = (int(value[0]), int(value[1]))
    else:
        raise ValueError(f"invalid head specification: {value!r}")
    if pair[0] < 0 or pair[1] < 0:
        raise ValueError(f"head indices must be nonnegative: {value!r}")
    return pair


def head_label(head: Head) -> str:
    return f"L{head[0]}H{head[1]:02d}"


def _rotate_half(value: torch.Tensor) -> torch.Tensor:
    first, second = value.chunk(2, dim=-1)
    return torch.cat((-second, first), dim=-1)


def _apply_rotary(
    query: torch.Tensor,
    key: torch.Tensor,
    position_embeddings: Tuple[torch.Tensor, torch.Tensor],
) -> Tuple[torch.Tensor, torch.Tensor]:
    cos, sin = position_embeddings
    cos = cos.unsqueeze(1)
    sin = sin.unsqueeze(1)
    return (
        query * cos + _rotate_half(query) * sin,
        key * cos + _rotate_half(key) * sin,
    )


def _validate_layer(layer: torch.nn.Module) -> None:
    """Fail closed if the installed Transformers Qwen3-VL contract changes."""
    if layer.__class__.__name__ != "Qwen3VLTextDecoderLayer":
        raise TypeError(
            "selected attention requires Qwen3VLTextDecoderLayer, got "
            f"{layer.__class__.__name__}"
        )
    attention = getattr(layer, "self_attn", None)
    required = (
        "q_proj",
        "k_proj",
        "q_norm",
        "k_norm",
        "head_dim",
        "num_key_value_groups",
        "scaling",
    )
    missing = [name for name in required if not hasattr(attention, name)]
    if missing or not hasattr(layer, "input_layernorm"):
        raise RuntimeError(
            "installed Qwen3-VL attention is incompatible with selected extraction; "
            f"missing={missing}"
        )
    if float(getattr(attention, "attention_dropout", 0.0)) != 0.0:
        raise RuntimeError("selected raw attention requires attention_dropout=0")


def selected_attention_from_layer(
    layer: torch.nn.Module,
    layer_input: torch.Tensor,
    position_embeddings: Tuple[torch.Tensor, torch.Tensor],
    attention_mask: Optional[torch.Tensor],
    rows_by_sample: Sequence[Sequence[int]],
    heads: Sequence[int],
) -> Dict[int, Sequence[torch.Tensor]]:
    """Recompute exact pre-dropout probabilities without a sequence-squared tensor.

    The returned mapping is ``head -> batch list[row, key]``.  Q/K projections,
    Q/K RMSNorm, interleaved MRoPE, GQA head mapping, additive causal mask, scale,
    and float32 softmax match Transformers 4.57 Qwen3-VL eager attention.
    """
    _validate_layer(layer)
    attention = layer.self_attn
    hidden = layer.input_layernorm(layer_input)
    batch, sequence, _ = hidden.shape
    if len(rows_by_sample) != batch:
        raise ValueError("rows_by_sample must have one row list per batch item")
    num_query_heads = int(attention.config.num_attention_heads)
    num_key_value_heads = int(attention.config.num_key_value_heads)
    head_dim = int(attention.head_dim)
    selected = sorted(set(map(int, heads)))
    if not selected or selected[0] < 0 or selected[-1] >= num_query_heads:
        raise ValueError("selected query head is outside the model head range")

    query = attention.q_norm(
        attention.q_proj(hidden).view(batch, sequence, num_query_heads, head_dim)
    ).transpose(1, 2)
    key = attention.k_norm(
        attention.k_proj(hidden).view(
            batch, sequence, num_key_value_heads, head_dim
        )
    ).transpose(1, 2)
    query, key = _apply_rotary(query, key, position_embeddings)

    output: Dict[int, Sequence[torch.Tensor]] = {}
    groups = int(attention.num_key_value_groups)
    for query_head in selected:
        key_head = query_head // groups
        per_sample = []
        for sample_index, raw_rows in enumerate(rows_by_sample):
            rows = torch.as_tensor(
                list(map(int, raw_rows)), dtype=torch.long, device=query.device
            )
            if rows.numel() == 0 or bool((rows < 0).any()) or bool((rows >= sequence).any()):
                raise ValueError("selected attention rows are empty or out of range")
            scores = torch.matmul(
                query[sample_index, query_head, rows],
                key[sample_index, key_head].transpose(0, 1),
            ) * float(attention.scaling)
            if attention_mask is None:
                # Transformers SDPA intentionally elides an all-valid causal mask
                # and delegates causality to scaled_dot_product_attention.  This
                # selected-row recomputation must materialize the same constraint.
                key_positions = torch.arange(sequence, device=query.device)
                scores = scores.masked_fill(
                    key_positions.unsqueeze(0) > rows.unsqueeze(1),
                    torch.finfo(scores.dtype).min,
                )
            else:
                mask_batch = 0 if attention_mask.shape[0] == 1 else sample_index
                scores = scores + attention_mask[mask_batch, 0, rows, :sequence]
            probabilities = torch.softmax(scores, dim=-1, dtype=torch.float32).to(
                query.dtype
            )
            if not bool(torch.isfinite(probabilities).all()):
                raise RuntimeError("selected attention produced non-finite values")
            per_sample.append(probabilities)
        output[query_head] = per_sample
    return output


@dataclass
class _Capture:
    hidden_states: torch.Tensor
    position_embeddings: Tuple[torch.Tensor, torch.Tensor]
    attention_mask: Optional[torch.Tensor]


class SelectedAttentionExtractor:
    """Capture selected layer inputs and recompute only requested heads/rows."""

    def __init__(self, model: torch.nn.Module, heads: Iterable[Any]) -> None:
        parsed = tuple(parse_head(value) for value in heads)
        if not parsed or len(set(parsed)) != len(parsed):
            raise ValueError("selected heads must be nonempty and unique")
        self.heads = parsed
        self.by_layer: Dict[int, Tuple[int, ...]] = {}
        for layer_index, head_index in parsed:
            self.by_layer.setdefault(layer_index, tuple())
            self.by_layer[layer_index] += (head_index,)
        self.layers: Dict[int, torch.nn.Module] = {}
        for module in model.modules():
            if module.__class__.__name__ != "Qwen3VLTextDecoderLayer":
                continue
            layer_index = int(module.self_attn.layer_idx)
            if layer_index in self.by_layer:
                _validate_layer(module)
                self.layers[layer_index] = module
        missing = sorted(set(self.by_layer) - set(self.layers))
        if missing:
            raise RuntimeError(f"selected Qwen3-VL decoder layers not found: {missing}")
        self._captures: Dict[int, _Capture] = {}
        self._recording = False
        self._handles = [
            layer.register_forward_pre_hook(
                self._make_hook(layer_index), with_kwargs=True
            )
            for layer_index, layer in self.layers.items()
        ]

    def _make_hook(self, layer_index: int):
        def capture(module, args, kwargs):
            if not self._recording:
                return
            if not args:
                raise RuntimeError("Qwen3-VL decoder hidden states were not positional")
            position_embeddings = kwargs.get("position_embeddings")
            attention_mask = kwargs.get("attention_mask")
            if position_embeddings is None:
                raise RuntimeError("Qwen3-VL layer omitted position embeddings")
            self._captures[layer_index] = _Capture(
                hidden_states=args[0],
                position_embeddings=position_embeddings,
                attention_mask=attention_mask,
            )

        return capture

    def begin(self) -> None:
        self._captures.clear()
        self._recording = True

    def extract(
        self, rows_by_sample: Sequence[Sequence[int]]
    ) -> Dict[Head, Sequence[torch.Tensor]]:
        self._recording = False
        missing = sorted(set(self.layers) - set(self._captures))
        if missing:
            raise RuntimeError(f"selected layer inputs were not captured: {missing}")
        output: Dict[Head, Sequence[torch.Tensor]] = {}
        for layer_index, heads in self.by_layer.items():
            capture = self._captures[layer_index]
            values = selected_attention_from_layer(
                self.layers[layer_index],
                capture.hidden_states,
                capture.position_embeddings,
                capture.attention_mask,
                rows_by_sample,
                heads,
            )
            for head_index, probabilities in values.items():
                output[(layer_index, head_index)] = probabilities
        return output

    def close(self) -> None:
        for handle in self._handles:
            handle.remove()
        self._handles.clear()

