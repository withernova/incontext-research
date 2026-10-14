"""Screen the loaded checkpoint once, freeze query heads, then evaluate."""
from pathlib import Path
from types import SimpleNamespace
import hashlib
import json
import numpy as np

from ..registry import DATASETS, HEAD_PROBES
from ..head_screening.finders import R003QueryHeadFinder
from ..utils.distributed import barrier, gather_objects


def selected_probe_maps(model, forward, rows, spans):
    """Collect requested rows layer by layer, never retain sequence-square maps."""
    import torch
    from ..attention_distillation.selected import selected_attention_from_layer
    layers = [m for m in model.modules()
              if m.__class__.__name__ == "Qwen3VLTextDecoderLayer"]
    if not layers:
        raise ValueError("no Qwen3-VL decoder layers for screening")
    captures, handles = {}, []

    def capture(layer, args, kwargs):
        index = int(layer.self_attn.layer_idx)
        heads = range(int(layer.self_attn.config.num_attention_heads))
        hidden = args[0] if args else kwargs["hidden_states"]
        values = selected_attention_from_layer(
            layer, hidden, kwargs["position_embeddings"],
            kwargs.get("attention_mask"), [rows], heads)
        maps = []
        for start, stop, height, width in spans:
            maps.append(np.stack([
                values[head][0][:, start:stop].float().mean(0).cpu().numpy().reshape(height, width)
                for head in heads
            ]))
        captures[index] = maps

    try:
        for layer in layers:
            handles.append(layer.register_forward_pre_hook(capture, with_kwargs=True))
        with torch.inference_mode():
            model(**{**forward, "output_attentions": False})
    finally:
        for handle in handles:
            handle.remove()
    expected = list(range(len(layers)))
    if sorted(captures) != expected:
        raise RuntimeError("screening missed decoder layers")
    return [np.stack([captures[i][j] for i in expected]) for j in range(len(spans))]


class _QueryMaps:
    def __init__(self, records, shape):
        self.records, self.shape = records, shape

    def __iter__(self):
        for record in self.records:
            with np.load(record["artifact"]) as payload:
                array = payload["q_to_q"].astype(np.float64)
            if (array.ndim != 4 or array.shape[:2] != self.shape
                    or not np.isfinite(array).all() or (array < 0).any()):
                raise ValueError("invalid query screening map")
            yield array


class StreamingQueryFinder(R003QueryHeadFinder):
    """Use the unchanged R003 selector with two disk passes instead of all maps."""
    def _load(self, records):
        shape = tuple(map(int, records[0]["head_shape"]))
        if len(shape) != 2 or any(tuple(r["head_shape"]) != shape for r in records):
            raise ValueError("screening head shapes differ")
        return _QueryMaps(records, shape), None, None, shape


def _publish(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    temp.replace(path)


def resolve_query_heads(wrapper, dataset, selected_indices, config, settings):
    intervention = dict(settings["_attention_intervention"])
    if intervention.get("heads"):
        return intervention
    automatic = intervention.get("auto_head_screening") or {}
    if not automatic.get("enabled"):
        raise ValueError("heads are empty and automatic screening is disabled")
    context = getattr(wrapper, "context", None)
    rank, world = (context.rank, context.world_size) if context else (0, 1)
    root = Path(config["work_dir"]) / "query_attention" / "head_screening"
    # Exactly the selected eval set, with one shared model/checkpoint and processor.
    subset = [dataset[i] for i in selected_indices]
    count = automatic.get("samples")
    count = len(subset) if count in (None, "None") else int(count)
    if not 1 <= count <= len(subset):
        raise ValueError("auto screening sample count is outside the eval set")
    top_k = int(automatic.get("top_k", 5))
    probe_cfg = dict(config["head_screening"]["probe"])
    probe_cfg.update(samples_per_screening=count, seed=int(settings["seed"]),
                     attention_mode="selected")
    probe = HEAD_PROBES.build(probe_cfg)
    probe_indices = probe.sample_indices(len(subset), 0)
    checkpoint = config["named_run"]["resolved_resume_checkpoint"]
    manifest = Path(config[settings.get("dataloader", "test_dataloader")]["dataset"]["ann_file"])
    identity = dict(checkpoint=str(checkpoint), manifest=str(manifest),
                    manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),
                    eval_indices=list(selected_indices),
                    screening_indices=[selected_indices[i] for i in probe_indices],
                    seed=int(settings["seed"]), top_k=top_k,
                    screening_scope="eval", generation_steps=intervention["generation_steps"])
    if rank == 0:
        root.mkdir(parents=True, exist_ok=False)
        _publish(root / "frozen_input.json", identity)
        print(f"[QUERY_HEAD_SCREEN_START] samples={count} top_k={top_k} scope=eval", flush=True)
    if context:
        barrier(context)
    model = getattr(wrapper, "peft_model", wrapper.model)
    collator_cfg = dict(config["train_dataloader"]["collator"])
    collator_cfg["vision_max_patch_tokens"] = settings.get("vision_max_patch_tokens")
    collator = DATASETS.build(collator_cfg, processor=wrapper.processor)
    runner = SimpleNamespace(dataset=subset, rank=rank, world_size=world,
        wrapper=SimpleNamespace(peft_model=model, input_device=wrapper.input_device),
        collator=collator)
    try:
        local = probe.collect(runner, 0, root)
    except Exception as exc:
        local = dict(records=[], failures=[dict(reason=f"{type(exc).__name__}: {exc}")])
    payloads = gather_objects(local, context) if context else [local]
    result_path = root / "selected_heads.json"
    if rank == 0:
        try:
            records = sorted((r for p in payloads for r in p["records"]),
                             key=lambda r: r["dataset_index"])
            failures = [f for p in payloads for f in p["failures"]]
            if failures:
                raise RuntimeError(f"head screening failed: {failures[0]['reason']}")
            if [r["dataset_index"] for r in records] != probe_indices:
                raise RuntimeError("head screening coverage differs from frozen input")
            finder_cfg = dict(config["head_screening"]["finder"])
            finder_cfg.pop("type", None)
            finder_cfg["fixed_head_counts"] = (top_k,)
            result = StreamingQueryFinder(**finder_cfg).find(records)
            heads = result["selected_sets"]["query"][str(top_k)]
            if len(heads) != top_k or len(set(heads)) != top_k:
                raise RuntimeError("query selector did not return the requested unique heads")
            _publish(result_path, dict(**identity, status="completed", heads=heads,
                                       screening=result))
        except Exception as exc:
            _publish(result_path, dict(**identity, status="failed",
                                       reason=f"{type(exc).__name__}: {exc}"))
    if context:
        barrier(context)
    result = json.loads(result_path.read_text())
    if result["status"] != "completed":
        raise RuntimeError(result["reason"])
    intervention["heads"] = result["heads"]
    intervention["resolved_screening"] = str(result_path)
    if rank == 0:
        print("[QUERY_HEAD_SCREEN_DONE] heads=" + ",".join(result["heads"]), flush=True)
    return intervention
