"""E010-R-008: complete-LaSOT natural-query-row exact-replay audit.

All maps use natural Query-bbox prediction rows.  Query heads read Q→Q and
Q→R; independently frozen Reference heads read Qbbox→Reference (R→R).
No Reference-bbox token rows are used.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import torch
from iplocid.attention.metrics import area_normalized_enrichment, fractional_mass, fractional_token_iou, pointing_hit, retained_mass_support
from iplocid.attention.spans import locate_image_spans
from iplocid.inference.images import load_and_resize_image
from iplocid.inference.replay import prediction_rows
from iplocid.models.qwen import load_qwen3vl_with_lora
from iplocid.pipelines.outcome_stratified_core30 import metrics as core30_metrics
from iplocid.pipelines.role_audit_pipeline import occupancy, token_ids_with_offsets, unique_subsequence
from iplocid.prompts.coordinates import pixel_to_vlm_format, vlm_to_pixel_format
from iplocid.prompts.messages import build_messages

SCHEMA = "iplocid.e010.full-lasot-frozen-query-and-reference-top5/v2"
QUERY_TOP5 = ("L20H15", "L24H16", "L25H10", "L15H13", "L21H10")
# R-006 held-out frozen GT-frequency Top-5; authority is recorded in config.
REFERENCE_TOP5 = ("L18H05", "L20H12", "L20H15", "L20H08", "L14H02")
READOUTS = (("q_to_q", "query", QUERY_TOP5), ("q_to_r", "reference", QUERY_TOP5), ("r_to_r", "reference", REFERENCE_TOP5))


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def hindex(name):
    layer, head = name[1:].split("H", 1); return int(layer) * 32 + int(head)
def head_tuple(name):
    layer, head = name[1:].split("H", 1); return int(layer), int(head)
def sequence(row): return row["source"]["sequence_cluster"]
def category(row): return row["source"]["category"]
def xywh(line):
    values = [float(x) for x in re.split(r"[ ,\t]+", line.strip()) if x]
    if len(values) < 4 or not np.isfinite(values[:4]).all() or values[2] <= 0 or values[3] <= 0: return None
    x, y, w, h = values[:4]; return [x, y, x + w, y + h]


def deterministic_split(groups, rows, seed):
    evaluation, discovery = {}, {}
    for cls, indices in sorted(groups.items()):
        ordered = sorted(indices, key=lambda i: hashlib.sha256(f"{seed}:{cls}:{sequence(rows[i])}".encode()).hexdigest())
        evaluation[cls], discovery[cls] = ordered[:10], ordered[10:]
    if any(len(evaluation[c]) != 10 or len(discovery[c]) != 10 or set(evaluation[c]) & set(discovery[c]) for c in groups):
        raise RuntimeError("per-category evaluation/discovery split contract failed")
    return evaluation, discovery


def build_manifest(config):
    root = Path(config["dataset_root"])
    categories = sorted(x for x in root.iterdir() if x.is_dir() and any(y.is_dir() for y in x.iterdir()))
    pairs = [(c, s) for c in categories for s in sorted(x for x in c.iterdir() if x.is_dir())]
    ids = [f"{c.name}/{s.name}" for c, s in pairs]
    if len(categories) != 70 or len(pairs) != 1400 or hashlib.sha256("\n".join(ids).encode()).hexdigest() != config["sequence_ids_sha256"]:
        raise RuntimeError("complete LaSOT 70x20 sequence contract failed")
    rows = []
    for c, s in pairs:
        valid = [(i, xywh(line)) for i, line in enumerate((s / "groundtruth.txt").read_text().splitlines()) if xywh(line)]
        if not valid: raise ValueError(f"no valid annotation: {s}")
        (ri, rb), (qi, qb) = valid[0], valid[-1]
        ref, query = s / "img" / f"{ri+1:08d}.jpg", s / "img" / f"{qi+1:08d}.jpg"
        if not ref.is_file() or not query.is_file(): raise FileNotFoundError(f"frame/annotation mismatch: {s}")
        rows.append({"element": c.name, "image_path": [str(ref), str(query)], "bbox": [rb, qb], "source": {"category": c.name, "sequence_cluster": f"{c.name}/{s.name}", "reference_line": ri + 1, "query_line": qi + 1}})
    return rows


def prepare(config):
    rows = build_manifest(config); groups = {c: [i for i, r in enumerate(rows) if category(r) == c] for c in sorted({category(r) for r in rows})}
    evaluation, discovery = deterministic_split(groups, rows, int(config["seed"]))
    out = Path(config["run_dir"]) / "manifests"; out.mkdir(parents=True, exist_ok=True)
    payloads = {"full_manifest.json": rows, "evaluation_manifest.json": [rows[i] for v in evaluation.values() for i in v], "discovery_manifest.json": [rows[i] for v in discovery.values() for i in v], "split_summary.json": {"seed": config["seed"], "records": 1400, "classes": 70, "evaluation_records": 700, "discovery_records": 700, "zero_overlap": True, "evaluation": evaluation, "discovery": discovery}}
    for name, payload in payloads.items(): (out / name).write_text(json.dumps(payload, indent=2) + "\n")
    return rows, {i for v in evaluation.values() for i in v}


def make_inputs(model, processor, row, config):
    ref_path, query_path = row["image_path"]
    ref, _, ref_scale = load_and_resize_image(ref_path, int(config["max_side"])); query, _, query_scale = load_and_resize_image(query_path, int(config["max_side"]))
    adapter = SimpleNamespace(data_path=str(Path(config["run_dir"]) / "manifests/full_manifest.json"))
    ref_box = [x * ref_scale for x in row["bbox"][0]]
    ref_text = str(pixel_to_vlm_format(adapter, str(ref_box), ref.size, "NotGT", model_id=config["model_id"]))
    messages, _ = build_messages(element=row["element"], reference_img_path=ref_path, ref_box_text=ref_text, query_img_path=query_path)
    prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[prompt], images=[ref, query], videos=None, padding=True, return_tensors="pt").to(next(model.parameters()).device)
    return ref, query, ref_scale, query_scale, adapter, messages, inputs


def box_iou(a, b):
    x1, y1 = torch.maximum(a[:, None, 0], b[None, :, 0]), torch.maximum(a[:, None, 1], b[None, :, 1])
    x2, y2 = torch.minimum(a[:, None, 2], b[None, :, 2]), torch.minimum(a[:, None, 3], b[None, :, 3])
    inter = (x2-x1).clamp_min(0) * (y2-y1).clamp_min(0); aa = (a[:, 2]-a[:, 0]).clamp_min(0) * (a[:, 3]-a[:, 1]).clamp_min(0); bb = (b[:, 2]-b[:, 0]).clamp_min(0) * (b[:, 3]-b[:, 1]).clamp_min(0)
    return inter / (aa[:, None] + bb[None, :] - inter).clamp_min(1e-12)


def natural_record(model, processor, row, index, config):
    _, query, _, qscale, adapter, _, inputs = make_inputs(model, processor, row, config); prompt_length = inputs.input_ids.shape[1]
    with torch.inference_mode(): generated = model.generate(**inputs, max_new_tokens=int(config["max_new_tokens"]), do_sample=False)
    ids = generated[0, prompt_length:].detach().cpu().tolist(); text = processor.tokenizer.decode(ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)
    close = text.find("]"); pred = vlm_to_pixel_format(adapter, text[:close+1], query.size, "NotGT", config["model_id"]) if close >= 0 else None
    positive = bool(re.search(r"\byes\b", text, re.I)); status = "ok" if pred is not None else "unparsed"
    iou = None if pred is None else float(box_iou(torch.tensor([pred], dtype=torch.float), torch.tensor([[x*qscale for x in row["bbox"][1]]], dtype=torch.float))[0, 0])
    return {"index": index, "sequence": sequence(row), "category": category(row), "response": text, "response_token_ids": ids, "positive": positive, "parse_status": status, "natural_iou": iou, "pred_bbox": pred}


def classify(n):
    if n.get("parse_status") != "ok": return "unparsed"
    if not n.get("positive"): return "nonpositive"
    return "correct" if n["natural_iou"] >= .7 else "error" if n["natural_iou"] < .1 else "middle"


def spatial(attention, target):
    d, _, _ = core30_metrics(attention, target); support50 = retained_mass_support(attention, .5)
    return {"pointing": int(pointing_hit(attention, target)), "fractional_mass": fractional_mass(attention, target), "enrichment": area_normalized_enrichment(attention, target), "s50_fiou": fractional_token_iou(support50, target), "core30_hit": d["hit"], "s30_iou": d["s30_iou"], "largest4n_hit": d["largest4n_hit"], "largest4n_iou": d["largest4n_iou"], "selected_token_count_s50": int(support50.sum()), "s30_token_count": d["selected_token_count"], "largest4n_token_count": d["largest4n_token_count"]}


def layer_matched_random_heads(index, seed, frozen_names, label):
    # One deterministic independently named control per sequence/readout; same layer multiset.
    rng = np.random.default_rng(int(seed) + 1000003 * int(index) + sum(map(ord, label)))
    layers = [head_tuple(name)[0] for name in frozen_names]
    return {f"L{layer}H{head:02d}": (layer, head) for layer, head in [(layer, int(rng.integers(32))) for layer in layers]}


def maps_for_edge(attentions, rows, span, heads):
    return {name: attentions[layer][0, head, rows, span.start:span.end].float().mean(0).cpu().numpy().reshape(span.merged_h, span.merged_w) for name, (layer, head) in heads.items()}


def replay_record(model, processor, row, natural, config):
    ref, query, rscale, qscale, adapter, messages, _ = make_inputs(model, processor, row, config); text = natural["response"]; close = text.find("]")
    if close < 0: raise ValueError("natural response lacks bbox close")
    rendered = processor.apply_chat_template(messages + [{"role": "assistant", "content": [{"type": "text", "text": text}]}], tokenize=False, add_generation_prompt=False)
    inputs = processor(text=[rendered], images=[ref, query], videos=None, padding=True, return_tensors="pt").to(next(model.parameters()).device)
    tok = processor.tokenizer; spans = locate_image_spans(inputs.input_ids, inputs.image_grid_thw, int(tok.convert_tokens_to_ids("<|image_pad|>")), int(model.config.vision_config.spatial_merge_size))
    if len(spans) != 2: raise ValueError("exact replay requires two spans")
    ids = inputs.input_ids[0].tolist(); start = rendered.rfind(text); pos = unique_subsequence(ids, token_ids_with_offsets(tok, rendered, start, start + close + 1), spans[1].end, len(ids)); rows = prediction_rows(pos)
    with torch.inference_mode(): result = model(**inputs, output_attentions=True, return_dict=True)
    all_heads = {f"L{l}H{h:02d}": (l, h) for l in range(len(result.attentions)) for h in range(result.attentions[l].shape[1])}
    targets = {"query": occupancy([x*qscale for x in row["bbox"][1]], query.width, query.height, spans[1].merged_h, spans[1].merged_w), "reference": occupancy([x*rscale for x in row["bbox"][0]], ref.width, ref.height, spans[0].merged_h, spans[0].merged_w)}
    output = {}
    for edge, target_name, frozen_names in READOUTS:
        # Every branch keeps exactly the natural Query-bbox p−1 rows above.
        frozen = {name: head_tuple(name) for name in frozen_names}
        span = spans[1] if target_name == "query" else spans[0]; frozen_maps = maps_for_edge(result.attentions, rows, span, frozen)
        all_map = np.mean([v / v.sum() for v in maps_for_edge(result.attentions, rows, span, all_heads).values()], axis=0)
        random_maps = maps_for_edge(result.attentions, rows, span, layer_matched_random_heads(natural["index"], int(config["seed"]), frozen_names, edge))
        output[edge] = {"heads": {k: spatial(v, targets[target_name]) for k, v in frozen_maps.items()}, "top5": spatial(np.mean([v / v.sum() for v in frozen_maps.values()], axis=0), targets[target_name]), "layer_matched_random": spatial(np.mean([v / v.sum() for v in random_maps.values()], axis=0), targets[target_name]), "all_head_mean": spatial(all_map, targets[target_name])}
    return output


def bootstrap_difference(records, metric, repeats, seed):
    correct = [x for x in records if x["outcome"] == "correct"]; error = [x for x in records if x["outcome"] == "error"]
    if not correct or not error: return {"n_correct": len(correct), "n_error": len(error), "difference": None, "ci95": None}
    rng = np.random.default_rng(seed); c = np.asarray([x[metric] for x in correct]); e = np.asarray([x[metric] for x in error]); draws = [float(c[rng.integers(len(c), size=len(c))].mean() - e[rng.integers(len(e), size=len(e))].mean()) for _ in range(repeats)]
    return {"n_correct": len(c), "n_error": len(e), "difference": float(c.mean()-e.mean()), "ci95": [float(np.quantile(draws, .025)), float(np.quantile(draws, .975))]}


def run(config):
    rows, evaluation = prepare(config); out = Path(config["run_dir"]); (out / "outputs").mkdir(parents=True, exist_ok=True); (out / "analysis").mkdir(exist_ok=True)
    natural_path = out / "outputs/natural_records.jsonl"; existing = {x["index"]: x for x in map(json.loads, natural_path.read_text().splitlines())} if natural_path.exists() else {}
    model, processor = load_qwen3vl_with_lora(config["model_path"], config["lora_path"], max_memory={0: "22GiB", 1: "22GiB"})
    with natural_path.open("a") as f:
        for i, row in enumerate(rows):
            if i in existing: continue
            try: record = natural_record(model, processor, row, i, config)
            except Exception as exc: record = {"index": i, "sequence": sequence(row), "category": category(row), "parse_status": "generation_failure", "failure": f"{type(exc).__name__}: {exc}"}
            f.write(json.dumps(record, allow_nan=False) + "\n"); f.flush(); existing[i] = record
            if torch.cuda.is_available(): torch.cuda.empty_cache()
    per_image, failures = [], []
    for i, row in enumerate(rows):
        natural = existing[i]
        if classify(natural) == "unparsed": failures.append({"index": i, "phase": "replay", "reason": natural.get("parse_status")}); continue
        try:
            scores = replay_record(model, processor, row, natural, config)
            per_image.append({"index": i, "sequence": sequence(row), "category": category(row), "cohort": "evaluation" if i in evaluation else "discovery", "outcome": classify(natural), "natural": natural, "scores": scores})
        except Exception as exc: failures.append({"index": i, "phase": "exact_replay", "reason": f"{type(exc).__name__}: {exc}"})
        if torch.cuda.is_available(): torch.cuda.empty_cache()
    (out / "analysis/per_image.jsonl").write_text("".join(json.dumps(x, allow_nan=False) + "\n" for x in per_image))
    summary = {"schema": SCHEMA, "status": "completed" if len(existing) == 1400 and len(per_image) == 1400 else "failed_integrity", "frozen_query_top5": list(QUERY_TOP5), "frozen_reference_top5": list(REFERENCE_TOP5), "row_contract": "all Q→Q/Q→R/R→R maps use natural Query-bbox p−1 rows; no Reference-bbox rows", "integrity": {"manifest_records": len(rows), "natural_records": len(existing), "exact_replay_records": len(per_image), "replay_failures": failures, "evaluation_records": 700, "readouts": [x[0] for x in READOUTS]}}
    for cohort, indices in (("evaluation", evaluation), ("all", set(range(1400)))):
        block = {}
        for edge, _, frozen_names in READOUTS:
            block[edge] = {}
            for method in list(frozen_names) + ["top5", "layer_matched_random", "all_head_mean"]:
                values = [{"outcome": x["outcome"], **x["scores"][edge]["heads"].get(method, x["scores"][edge].get(method, {}))} for x in per_image if x["index"] in indices and x["outcome"] in ("correct", "error")]
                block[edge][method] = {metric: bootstrap_difference(values, metric, int(config["bootstrap_repeats"]), int(config["seed"])) for metric in ("pointing", "fractional_mass", "enrichment", "s50_fiou", "core30_hit", "s30_iou", "largest4n_hit", "largest4n_iou")}
        summary[cohort] = block
    (out / "analysis/summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    (out / "metrics.json").write_text(json.dumps({"schema": SCHEMA, "primary": summary.get("evaluation", {}), "integrity": summary["integrity"]}, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--config", required=True); parser.add_argument("--prepare-only", action="store_true"); args = parser.parse_args(); config = json.loads(Path(args.config).read_text())
    if args.prepare_only: prepare(config)
    else: run(config)
if __name__ == "__main__": main()
