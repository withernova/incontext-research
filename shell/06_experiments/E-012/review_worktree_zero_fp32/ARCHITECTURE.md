# Architecture and maintenance guide

`iploc-szy` follows the useful parts of MMEngine/MMDetection—Python configs,
registries, builders, runners, and hooks—without depending on the full stack.
The dependency direction is deliberately one-way:

```text
config -> registry/builder -> dataset/collator -> model -> runner/hooks
                                              \-> evaluator <- inference tool
```

## Contracts

### Dataset sample

A dataset item is a dictionary with:

- `id`: stable sample identifier;
- `messages`: Qwen chat-template conversation ending in an assistant answer;
- `answer`: canonical normalized bbox string;
- `image_paths`: images in the same order in which they appear in messages.

### Collator output

The collator returns Qwen3-VL processor tensors, `labels`, and a `metadata`
dictionary. Every user, image, template, and generation-prefix token is masked
with `-100`; only the final assistant answer is supervised. Prefix equality is
an integrity gate, not a best-effort heuristic.

### Model wrapper

A wrapper owns one processor and one model. `trainable_parameters()` must expose
only LoRA tensors. The current Qwen3-VL wrapper freezes base and visual weights
through PEFT and validates the trainable names after attachment.

### Runner and hooks

The runner owns optimization and lifecycle ordering. Hooks observe or validate
state but do not redefine data, model, or metrics. Metrics are assembled before
`after_run`, allowing `GpuMemoryHook` to extend them and `MetricsWriterHook` to
publish the final object atomically.

## Style

- Prefer explicit names over compressed local aliases.
- One principal action per line.
- Public classes and functions require docstrings and type annotations.
- Comments explain invariants and rationale, not obvious syntax.
- New batching, distributed, or resume features require focused tests for token
  alignment, visual patch layout, optimizer state, and artifact compatibility.
- Legacy repositories are protocol references only; new modules must not import
  their internal implementation directly.

See `MODULE_MAP.md` for the file-level relationship to IPLoc, IPLoc-ID, and
Rex-Omni.
