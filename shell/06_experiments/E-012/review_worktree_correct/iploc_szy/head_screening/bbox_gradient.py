"""BBox-only gradient attention screening using the existing IPLoc registries.

The Qwen3-VL eager function still computes the real Q/K attention probabilities.
We reconnect its returned A to AV so a frozen model can expose dL/dA. Nothing
is inferred from detached, recomputed display maps. Only text attention changes.
"""
from contextlib import contextmanager
import argparse
import csv
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
import torch.nn.functional as F

from ..config import Config
from ..registry import DATASETS, HEAD_FINDERS, HEAD_PROBES, MODELS
from .probes import consecutive_spans, temporary_eager_attention


def publish(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def bbox_loss(logits, input_ids, positions):
    if not positions or min(positions) < 1 or max(positions) >= input_ids.shape[1]:
        raise ValueError("invalid bbox token positions")
    if logits.shape[:2] != input_ids.shape:
        raise ValueError("bbox loss needs unshifted full-sequence logits")
    rows = torch.tensor(positions, device=logits.device) - 1
    labels = input_ids[0, positions].to(logits.device)
    return F.cross_entropy(logits[0, rows].float(), labels, reduction="mean")


def reduce_edges(attention, gradient):
    signed = attention.float() * gradient.float()
    if not bool(torch.isfinite(signed).all()):
        raise ValueError("non-finite attention-gradient product")
    return torch.stack((signed.abs().sum((-2, -1)), signed.sum((-2, -1)),
                        signed.clamp_min(0).sum((-2, -1)),
                        (-signed.clamp_max(0)).sum((-2, -1))), dim=-1)


def resolve_checkpoint(path_value, base_model_path):
    """Resolve an explicit final-run/checkpoint/adapter directory; never pick latest."""
    if path_value is None:
        return None
    root = Path(path_value).resolve()
    adapter = root if (root / "adapter_config.json").is_file() else root / "adapter"
    if not (adapter / "adapter_config.json").is_file() or not (adapter / "adapter_model.safetensors").is_file():
        raise FileNotFoundError(f"checkpoint lacks adapter_config.json/adapter_model.safetensors: {root}")
    config = json.loads((adapter / "adapter_config.json").read_text())
    if config.get("peft_type") != "LORA":
        raise ValueError("screening currently supports LoRA adapters only")
    recorded_base = config.get("base_model_name_or_path")
    if not recorded_base or Path(recorded_base).resolve() != Path(base_model_path).resolve():
        raise ValueError("adapter base_model_name_or_path differs from configured base model")
    # Final runs save adapter_processor next to adapter. Intermediate checkpoints
    # can reuse that processor from their containing run, without reading logs.
    candidates = [adapter.parent / "adapter_processor"]
    if adapter.parent.parent.name == "checkpoints":
        candidates.append(adapter.parent.parent.parent / "adapter_processor")
    processor = next((p for p in candidates if (p / "tokenizer_config.json").is_file()),
                     Path(base_model_path))
    return dict(requested_path=str(root), adapter_path=str(adapter), processor_path=str(processor),
                adapter_config_sha256=hashlib.sha256((adapter / "adapter_config.json").read_bytes()).hexdigest(),
                adapter_weights_sha256=hashlib.sha256((adapter / "adapter_model.safetensors").read_bytes()).hexdigest())


def attach_checkpoint(wrapper, checkpoint):
    """Load trained adapter weights, without optimizer state or new random LoRA."""
    if checkpoint is None:
        return wrapper
    from peft import PeftModel
    from peft.utils.save_and_load import get_peft_model_state_dict
    from safetensors.torch import load_file
    from transformers import AutoProcessor
    model = PeftModel.from_pretrained(wrapper.model, checkpoint["adapter_path"],
                                      is_trainable=False, autocast_adapter_dtype=False,
                                      local_files_only=True)
    # PEFT can warn rather than fail for missing keys. Verify exact loaded tensors.
    expected = load_file(str(Path(checkpoint["adapter_path"]) / "adapter_model.safetensors"))
    actual = get_peft_model_state_dict(model)
    if set(expected) != set(actual):
        raise ValueError("loaded adapter tensor keys differ from checkpoint")
    for key, value in expected.items():
        loaded = actual[key].detach().cpu()
        if loaded.shape != value.shape or not torch.equal(loaded, value.to(loaded.dtype)):
            raise ValueError(f"adapter tensor did not load exactly: {key}")
    wrapper.model = model.eval()
    wrapper.processor = AutoProcessor.from_pretrained(checkpoint["processor_path"], local_files_only=True)
    return wrapper


def sequence_keys(record):
    """Dataset + video directory identity for existing LaSOT/GOT10k/TAO manifests."""
    dataset = record.get("dataset")
    if dataset not in ("LaSOT", "GOT10k", "TAO"):
        raise ValueError("sequence audit supports LaSOT/GOT10k/TAO only")
    keys = set()
    for raw in record["image_path"]:
        path = Path(raw[0] if isinstance(raw, list) and len(raw) == 1 else raw)
        parent = path.parent.parent if path.parent.name == "img" else path.parent
        keys.add((dataset, parent.name))
    if not keys:
        raise ValueError("sample has no image sequence identity")
    return keys


def select_eval_indices(dataset, probe, settings):
    """Balance datasets, exclude training videos, and choose distinct eval videos."""
    if not settings:
        return probe.sample_indices(len(dataset)), None
    train_path = Path(settings["training_manifest"])
    digest = hashlib.sha256(train_path.read_bytes()).hexdigest()
    if digest != settings["training_manifest_sha256"]:
        raise ValueError("training manifest hash changed; re-audit split before screening")
    training = json.loads(train_path.read_text())
    seen = set().union(*(sequence_keys(record) for record in training))
    quotas = settings["samples_per_dataset"]
    if sum(quotas.values()) != probe.samples or any(n < 1 for n in quotas.values()):
        raise ValueError("dataset quotas must be positive and sum to probe.samples")
    pools = {name: [] for name in quotas}
    excluded = 0
    for index in range(len(dataset)):
        record = dataset[index]["raw"]
        name = record.get("dataset")
        if name not in pools:
            continue
        keys = sequence_keys(record)
        if keys & seen:
            excluded += 1
        else:
            pools[name].append((index, keys))
    rng = np.random.default_rng(probe.seed)
    selected, chosen_sequences = [], set()
    for name in sorted(quotas):
        count = 0
        for position in rng.permutation(len(pools[name])):
            index, keys = pools[name][position]
            if keys & chosen_sequences:
                continue
            selected.append(index)
            chosen_sequences.update(keys)
            count += 1
            if count == quotas[name]:
                break
        if count != quotas[name]:
            raise ValueError(f"insufficient unseen distinct sequences for {name}")
    audit = dict(training_manifest=str(train_path), training_manifest_sha256=digest,
                 training_sequences=len(seen), excluded_eval_rows=excluded,
                 eligible_rows_per_dataset={name: len(rows) for name, rows in pools.items()},
                 selected_per_dataset=quotas,
                 selected_sequences=[list(key) for key in sorted(chosen_sequences)],
                 selected_train_sequence_overlap=0,
                 scope="relative to the specified current training manifest; eval samples used for head discovery")
    return sorted(selected), audit


@contextmanager
def gradient_attention(model, rows, query_span, scores, perturbation=None, collect=True):
    from transformers.models.qwen3_vl import modeling_qwen3_vl as implementation
    original = implementation.eager_attention_forward
    modules = [m for m in model.modules() if m.__class__.__name__ == "Qwen3VLTextAttention"]
    if not modules:
        raise ValueError("gradient probe requires Qwen3-VL text attention")
    if model.training:
        raise ValueError("gradient probe requires eval mode")
    start, stop = query_span[:2]

    def intercepted(module, query, key, value, attention_mask, scaling, dropout=0.0, **kwargs):
        if module.__class__.__name__ != "Qwen3VLTextAttention":
            return original(module, query, key, value, attention_mask, scaling, dropout, **kwargs)
        if dropout != 0 or query.shape[0] != 1 or attention_mask is None:
            raise ValueError("probe requires batch=1, dropout=0 and explicit causal mask")
        unused_output, attention = original(module, query, key, value, attention_mask,
                                            scaling, dropout, **kwargs)
        del unused_output
        layer = int(module.layer_idx)
        if collect:
            # The first text layer can be a leaf when all model weights are frozen.
            if not attention.requires_grad:
                attention.requires_grad_(True)
            selected = attention[0, :, rows, start:stop].detach().float()

            def save_gradient(gradient):
                if layer in scores:
                    raise RuntimeError("duplicate layer gradient; checkpoint recomputation unsupported")
                scores[layer] = reduce_edges(selected, gradient[0, :, rows, start:stop]).cpu()

            attention.register_hook(save_gradient)
        if perturbation is not None and layer == perturbation[0]:
            head, epsilon = perturbation[1:]
            attention = attention.clone()
            attention[0, head, rows, start:stop] *= 1.0 + epsilon
        # Reuse the installed implementation's GQA value expansion and output layout.
        values = implementation.repeat_kv(value, module.num_key_value_groups)
        output = torch.matmul(attention, values).transpose(1, 2).contiguous()
        return output, attention

    implementation.eager_attention_forward = intercepted
    try:
        with temporary_eager_attention(model):
            yield len(modules)
    finally:
        implementation.eager_attention_forward = original


@HEAD_PROBES.register_module()
class BBoxGradientAttentionProbe:
    def __init__(self, samples=20, seed=20260910, max_sequence_tokens=2048,
                 parity_atol=0.002, parity_rtol=0.002, finite_difference_epsilon=0.02):
        self.samples, self.seed = int(samples), int(seed)
        self.max_sequence_tokens = int(max_sequence_tokens)
        self.parity_atol, self.parity_rtol = float(parity_atol), float(parity_rtol)
        self.epsilon = float(finite_difference_epsilon)
        if self.samples < 1 or self.max_sequence_tokens < 2 or not 0 < self.epsilon < 1:
            raise ValueError("invalid screening budget or perturbation epsilon")

    def sample_indices(self, dataset_size):
        if dataset_size < self.samples:
            raise ValueError("dataset smaller than requested screening count")
        return sorted(map(int, np.random.default_rng(self.seed).choice(
            dataset_size, self.samples, replace=False)))

    def collect(self, runner, screening_index, screen_dir):
        if screening_index != 0 or runner.world_size != 1:
            raise ValueError("initial gradient screening supports one single-process pass")
        indices = getattr(runner, "selected_indices", None)
        if indices is None:
            indices = self.sample_indices(len(runner.dataset))
        if len(indices) != self.samples or len(set(indices)) != len(indices):
            raise ValueError("selected sample count/uniqueness mismatch")
        model = runner.wrapper.model
        flags = [(p, p.requires_grad) for p in model.parameters()]
        was_training = model.training
        records = []
        model.eval()
        try:
            for parameter, _ in flags:
                parameter.requires_grad_(False)
            for index in indices:
                record = self._collect_one(runner, index, Path(screen_dir), not records)
                records.append(record)
                publish(Path(screen_dir) / "records.json", dict(records=records, indices=indices))
                print(f"[BBOX_GRADIENT] {len(records)}/{len(indices)} loss={record['bbox_ce']:.6f}", flush=True)
        finally:
            for parameter, enabled in flags:
                parameter.requires_grad_(enabled)
            model.train(was_training)
        return dict(records=records, failures=[], indices=indices)

    def encode_sample(self, runner, index):
        """预检和正式采集共用同一套 bbox、prediction row 与视觉网格校验。"""
        sample = runner.dataset[index]
        encoded = runner.collator([sample])
        metadata = encoded.pop("metadata")[0]
        labels = encoded.pop("labels")
        positions = list(map(int, metadata["bbox_token_positions"]))
        input_ids = encoded["input_ids"]
        if (not positions or positions != sorted(set(positions)) or min(positions) < 1
                or max(positions) >= input_ids.shape[1]):
            raise ValueError("bbox positions must be sorted, unique and have valid p-1 rows")
        if not torch.equal(labels[0, positions], input_ids[0, positions]):
            raise ValueError("bbox positions are outside the correctly supervised answer")
        if input_ids.shape[1] > self.max_sequence_tokens:
            raise ValueError("sequence exceeds explicit screening budget; no truncation")
        tokenizer = runner.collator.processor.tokenizer
        spans = consecutive_spans(input_ids[0].tolist(), tokenizer.convert_tokens_to_ids("<|image_pad|>"))
        grids = metadata["image_grid_thw"]
        if len(spans) != 2 or len(grids) != 2:
            raise ValueError("initial screening requires exactly one reference and one query")
        merge = int(runner.wrapper.model.config.vision_config.spatial_merge_size)
        for (a, b), (t, h, w) in zip(spans, grids):
            if t != 1 or h % merge or w % merge or b - a != (h // merge) * (w // merge):
                raise ValueError("visual span/token-grid mismatch")
        rows = [p - 1 for p in positions]
        if spans[-1][1] > min(rows):
            raise ValueError("query visual keys must precede prediction rows")
        return sample, encoded, metadata, positions, rows, spans

    def _collect_one(self, runner, index, directory, check_parity):
        sample, encoded, metadata, positions, rows, spans = self.encode_sample(runner, index)
        input_ids = encoded["input_ids"]
        grids = metadata["image_grid_thw"]
        forward = {k: v.to(runner.wrapper.input_device) for k, v in encoded.items()}
        forward.update(use_cache=False, output_attentions=False, return_dict=True, logits_to_keep=0)
        model = runner.wrapper.model
        baseline = None
        if check_parity:
            with temporary_eager_attention(model), torch.no_grad():
                baseline = model(**forward).logits[0, rows].float().cpu()
        scores = {}
        with torch.enable_grad(), gradient_attention(model, rows, spans[-1], scores) as layers:
            output = model(**forward)
            loss = bbox_loss(output.logits, forward["input_ids"], positions)
            if not bool(torch.isfinite(loss)):
                raise ValueError("non-finite bbox loss")
            if baseline is not None:
                actual = output.logits[0, rows].float().detach().cpu()
                torch.testing.assert_close(actual, baseline, atol=self.parity_atol, rtol=self.parity_rtol)
                parity_error = float((actual - baseline).abs().max())
            loss.backward()
            loss_value = float(loss.detach())
        del output, loss
        if sorted(scores) != list(range(layers)):
            raise ValueError("missing layer gradients; no partial ranking")
        values = torch.stack([scores[layer] for layer in range(layers)]).numpy()
        if not np.isfinite(values).all() or not np.any(values[..., 0] > 0):
            raise ValueError("all-zero/non-finite gradient contributions")
        directory.mkdir(parents=True, exist_ok=True)
        artifact = directory / f"sample_{index:06d}.npz"
        np.savez_compressed(artifact, absolute=values[..., 0], signed=values[..., 1],
                            positive=values[..., 2], negative_magnitude=values[..., 3])
        record = dict(dataset_index=index, sample_id=sample["id"], group=sample["group"],
                      artifact=str(artifact), bbox_ce=loss_value, bbox_token_positions=positions,
                      bbox_token_ids=input_ids[0, positions].tolist(), prediction_rows=rows,
                      visual_spans=spans, image_grid_thw=grids,
                      query_visual_token_count=spans[-1][1] - spans[-1][0],
                      bbox_token_count=len(positions), sequence_tokens=input_ids.shape[1])
        if sample.get("raw", {}).get("dataset") in ("LaSOT", "GOT10k", "TAO"):
            record["dataset"] = sample["raw"]["dataset"]
            record["sequence_keys"] = [list(key) for key in sorted(sequence_keys(sample["raw"]))]
        if baseline is not None:
            record["parity_max_abs_logit_error"] = parity_error
            record["finite_difference"] = self._finite_difference(model, forward, positions, rows,
                                                                    spans[-1], values)
        return record

    def _finite_difference(self, model, forward, positions, rows, span, values):
        # Validate the largest signed derivative to reduce cancellation/roundoff.
        layer, head = np.unravel_index(np.abs(values[..., 1]).argmax(), values.shape[:2])
        losses = []
        for epsilon in (-self.epsilon, self.epsilon):
            with torch.no_grad(), gradient_attention(model, rows, span, {},
                    perturbation=(int(layer), int(head), epsilon), collect=False):
                output = model(**forward)
                losses.append(float(bbox_loss(output.logits, forward["input_ids"], positions)))
            del output
        finite = (losses[1] - losses[0]) / (2 * self.epsilon)
        predicted = float(values[layer, head, 1])
        if not np.isfinite(losses).all():
            raise ValueError("non-finite perturbation loss")
        return dict(layer=int(layer), head=int(head), epsilon=self.epsilon,
                    loss_minus=losses[0], loss_plus=losses[1], signed_derivative=predicted,
                    central_difference=finite, sign_agreement=bool(finite * predicted > 0),
                    relative_error=abs(finite - predicted) / max(abs(finite), abs(predicted), 1e-8),
                    interpretation="post-softmax edge scaling without renormalization; diagnostic only")


@HEAD_FINDERS.register_module()
class BBoxGradientHeadFinder:
    def find(self, records):
        if not records:
            raise ValueError("no records to rank")
        samples = []
        for record in records:
            with np.load(record["artifact"]) as data:
                samples.append(np.stack([data[k] for k in ("absolute", "signed", "positive", "negative_magnitude")], -1))
        values = np.stack(samples)
        if values.ndim != 4 or not np.isfinite(values).all():
            raise ValueError("invalid per-sample head scores")
        mean = values.astype(np.float64).mean(0)
        ranking = []
        for layer, head in np.ndindex(mean.shape[:2]):
            absolute, signed, positive, negative = map(float, mean[layer, head])
            ranking.append(dict(layer=layer, head=head, absolute=absolute, signed=signed,
                                positive=positive, negative_magnitude=negative,
                                std_absolute=float(values[:, layer, head, 0].std()),
                                positive_signed_sample_fraction=float((values[:, layer, head, 1] > 0).mean())))
        ranking.sort(key=lambda r: (-r["absolute"], r["layer"], r["head"]))
        for rank, row in enumerate(ranking, 1):
            row["rank"] = rank
        return dict(schema="iploc-szy.bbox-gradient-ranking/v1", status="completed",
                    samples=len(records), row_contract="teacher_forced_query_bbox_pminus1/v1",
                    loss="per_sample_mean_bbox_token_CE_including_bbox_punctuation",
                    aggregation="sum_absolute_edges_then_equal_weight_mean_over_samples",
                    mean_bbox_ce=float(np.mean([r["bbox_ce"] for r in records])), ranking=ranking)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args(argv)
    if args.prepare_only and args.check_only:
        parser.error("choose one preflight mode")
    cfg = Config.fromfile(args.config)
    if args.prepare_only:
        if not cfg.get("manifest_preparation"):
            raise ValueError("existing-manifest mode: preparation disabled; set ann_file directly")
        from .lasot_screen_manifest import prepare_manifest
        provenance = prepare_manifest(**cfg["manifest_preparation"])
        print(json.dumps(provenance, ensure_ascii=False), flush=True)
        return 0
    dataset = DATASETS.build(cfg["screen_dataloader"]["dataset"])
    probe = HEAD_PROBES.build(cfg["head_screening"]["probe"])
    finder = HEAD_FINDERS.build(cfg["head_screening"]["finder"])
    selected_indices, split_audit = select_eval_indices(dataset, probe, cfg.get("eval_selection"))
    if not Path(cfg["model"]["model_path"]).is_dir():
        raise FileNotFoundError("configured model directory is missing")
    checkpoint = resolve_checkpoint(cfg.get("checkpoint_path"), cfg["model"]["model_path"])
    if args.check_only:
        from ..compat import ensure_torchvision_nms_schema
        ensure_torchvision_nms_schema()
        from transformers import AutoConfig, AutoProcessor
        processor_path = checkpoint["processor_path"] if checkpoint else cfg["model"]["model_path"]
        processor = AutoProcessor.from_pretrained(processor_path, local_files_only=True)
        collator = DATASETS.build(cfg["screen_dataloader"]["collator"], processor=processor)
        model_config = AutoConfig.from_pretrained(cfg["model"]["model_path"], local_files_only=True)
        runner = SimpleNamespace(dataset=dataset, collator=collator,
            wrapper=SimpleNamespace(model=SimpleNamespace(config=model_config)))
        lengths, bbox_counts = [], []
        for index in selected_indices:
            _, encoded, _, positions, _, _ = probe.encode_sample(runner, index)
            lengths.append(int(encoded["input_ids"].shape[1]))
            bbox_counts.append(len(positions))
        if max(lengths) > probe.max_sequence_tokens:
            raise ValueError("preflight sequence exceeds configured budget")
        print(json.dumps(dict(status="preflight_passed", samples=len(selected_indices), dataset_size=len(dataset),
                              selected_indices=selected_indices, checkpoint=checkpoint, split_audit=split_audit,
                              model=cfg["model"]["type"], probe=type(probe).__name__,
                              finder=type(finder).__name__, sequence_tokens_range=[min(lengths), max(lengths)],
                              bbox_tokens_range=[min(bbox_counts), max(bbox_counts)]), ensure_ascii=False))
        return 0
    root = Path(cfg["work_dir"])
    root.mkdir(parents=True, exist_ok=False)
    manifest_paths = cfg["screen_dataloader"]["dataset"]["ann_file"]
    manifest_paths = [manifest_paths] if isinstance(manifest_paths, str) else manifest_paths
    publish(root / "frozen_input.json", dict(config=dict(cfg),
            config_sources_sha256={p: hashlib.sha256(s.encode()).hexdigest() for p, s in cfg.source_files.items()},
            manifests_sha256={str(p): hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in manifest_paths},
            selected_indices=selected_indices, checkpoint=checkpoint, split_audit=split_audit,
            seed=probe.seed, parameter_updates=False))
    try:
        torch.manual_seed(probe.seed)
        np.random.seed(probe.seed)
        wrapper = MODELS.build(cfg["model"])
        wrapper = attach_checkpoint(wrapper, checkpoint)
        placement = getattr(wrapper.model, "hf_device_map", {})
        if any(str(device) in ("cpu", "disk") for device in placement.values()):
            raise ValueError("gradient screening requires GPU-resident model; CPU/disk offload unsupported")
        import transformers
        publish(root / "runtime.json", dict(torch_version=torch.__version__,
                transformers_version=transformers.__version__, device_map=placement))
        collator = DATASETS.build(cfg["screen_dataloader"]["collator"], processor=wrapper.processor)
        runner = SimpleNamespace(wrapper=wrapper, dataset=dataset, collator=collator, world_size=1,
                                 selected_indices=selected_indices)
        payload = probe.collect(runner, 0, root / "probe")
        result = finder.find(payload["records"])
        datasets = sorted({record.get("dataset", "unspecified") for record in payload["records"]})
        result["per_dataset"] = {name: finder.find([record for record in payload["records"]
            if record.get("dataset", "unspecified") == name]) for name in datasets}
        result["checks"] = {k: payload["records"][0][k] for k in
                            ("parity_max_abs_logit_error", "finite_difference")}
        with (root / "ranking.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(result["ranking"][0]))
            writer.writeheader()
            writer.writerows(result["ranking"])
        publish(root / "summary.json", result)
        print(f"[BBOX_GRADIENT_DONE] samples={result['samples']} summary={root / 'summary.json'}", flush=True)
    except BaseException as error:
        publish(root / "failure.json", dict(status="failed", exception=type(error).__name__, reason=str(error)))
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
