"""E-012 A/B/C 三套 head 统计，复用现有 bbox 梯度探针的模型/数据/行契约。

- mode=decodability（B）：teacher-forced 前向一次；对每个 head 取 bbox 预测行上的
  A@V 输出（对行取均值），用岭回归做 5 折交叉验证预测 GT 框坐标，得到"该 head 输出
  里能否线性读出框位置"的 R²。只前向、不反传。
- mode=steerability（C）：对候选 head 逐个做"误导"干预——把该 head 在 bbox 预测行上
  对 query 视觉 token 的注意力换成中心从 GT 平移 ±δ 的高斯目标，再用 teacher-forced
  argmax 解码框，统计框中心位移对注入位移的斜率。镜像 ±δ 配对抵消固定偏置。

样本集合从已有 A run 的 frozen_input.json 读取 selected_indices，保证 A/B/C 同批样本。
两种模式都不写回任何训练状态，只读模型与数据。
"""
from __future__ import annotations

import argparse
import csv
import json
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch

from ..config import Config
from ..registry import DATASETS, HEAD_PROBES, MODELS
from ..prompting.coordinates import parse_box
from .bbox_gradient import attach_checkpoint, publish, resolve_checkpoint
from .probes import temporary_eager_attention

DECODABILITY_SCHEMA = "iploc-szy.head-decodability/v1"
STEERABILITY_SCHEMA = "iploc-szy.head-steerability/v1"


def head_label(layer, head):
    return f"L{int(layer):02d}H{int(head):02d}"


@contextmanager
def capture_head_outputs(model, rows, store):
    """在每个文本层捕获各 head 在指定预测行上的 A@V 输出（对行取均值）。"""
    from transformers.models.qwen3_vl import modeling_qwen3_vl as implementation

    original = implementation.eager_attention_forward

    def intercepted(module, query, key, value, attention_mask, scaling, dropout=0.0, **kwargs):
        output, attention = original(module, query, key, value, attention_mask,
                                     scaling, dropout, **kwargs)
        if module.__class__.__name__ != "Qwen3VLTextAttention":
            return output, attention
        if dropout != 0 or query.shape[0] != 1:
            raise ValueError("head-output capture requires batch=1 and zero dropout")
        layer = int(module.layer_idx)
        values = implementation.repeat_kv(value, module.num_key_value_groups)
        picked = torch.einsum("hrk,hkd->hrd", attention[0].float(), values[0].float())
        store[layer] = picked.mean(dim=1).cpu()
        return output, attention

    implementation.eager_attention_forward = intercepted
    try:
        with temporary_eager_attention(model):
            yield
    finally:
        implementation.eager_attention_forward = original


@contextmanager
def steer_rows(model, head, rows, query_span, target):
    """把指定 head 在给定预测行上的 query 视觉注意力换成 target（保留原 query mass）。"""
    from transformers.models.qwen3_vl import modeling_qwen3_vl as implementation

    original = implementation.eager_attention_forward
    layer, head_index = int(head[0]), int(head[1])
    start, stop = query_span[:2]
    fired = {"count": 0}

    def intercepted(module, query, key, value, attention_mask, scaling, dropout=0.0, **kwargs):
        output, attention = original(module, query, key, value, attention_mask,
                                     scaling, dropout, **kwargs)
        if module.__class__.__name__ != "Qwen3VLTextAttention":
            return output, attention
        if int(module.layer_idx) != layer:
            return output, attention
        if query.shape[0] != 1 or dropout != 0:
            raise ValueError("steering requires batch=1 and zero dropout")
        attention = attention.clone()
        block = attention[0, head_index, rows, start:stop]
        mass = block.sum(-1, keepdim=True)
        if not bool(torch.isfinite(mass).all()) or not bool((mass > 0).all()):
            raise ValueError("nonfinite or zero query mass on steered rows")
        attention[0, head_index, rows, start:stop] = target.to(
            device=attention.device, dtype=attention.dtype) * mass
        values = implementation.repeat_kv(value, module.num_key_value_groups)
        output = torch.matmul(attention, values).transpose(1, 2).contiguous()
        fired["count"] += 1
        return output, attention

    implementation.eager_attention_forward = intercepted
    try:
        with temporary_eager_attention(model):
            yield fired
    finally:
        implementation.eager_attention_forward = original


def shifted_answer(box, shift_x):
    """把 GT 框整体沿 x 平移，并夹在 [0,1000] 内保持面积不变；返回答案串与实际位移。"""
    x1, y1, x2, y2 = box
    width, height = x2 - x1, y2 - y1
    center_x = (x1 + x2) / 2.0
    low, high = width / 2.0 + 1.0, 999.0 - width / 2.0
    new_center = float(min(max(center_x + shift_x, low), high))
    delta = new_center - center_x
    text = f"[{new_center - width / 2.0:.4f},{y1:.4f},{new_center + width / 2.0:.4f},{y2:.4f}]"
    return text, delta


def box_center(box):
    return np.array([(box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0], dtype=np.float64)


def argmax_text(logits, positions, tokenizer):
    """teacher-forced argmax：用 p-1 行的 logits 预测每个 bbox token。"""
    rows = torch.tensor(positions, device=logits.device) - 1
    tokens = logits[0, rows].argmax(dim=-1)
    return tokenizer.decode(tokens.tolist())


def ridge_cv_r2(features, targets, folds=5, alpha=1.0, seed=20260912):
    """岭回归 5 折交叉验证 R²（逐输出求 R² 后取均值）。"""
    count = features.shape[0]
    if count < folds * 2:
        raise ValueError("too few samples for cross-validated ridge")
    order = np.random.default_rng(seed).permutation(count)
    splits = np.array_split(order, folds)
    predicted = np.zeros_like(targets)
    for fold in range(folds):
        test = splits[fold]
        train = np.concatenate([splits[i] for i in range(folds) if i != fold])
        mean = features[train].mean(0)
        scale = features[train].std(0) + 1e-6
        x_train = (features[train] - mean) / scale
        x_test = (features[test] - mean) / scale
        y_mean = targets[train].mean(0)
        gram = x_train.T @ x_train + alpha * np.eye(features.shape[1])
        weights = np.linalg.solve(gram, x_train.T @ (targets[train] - y_mean))
        predicted[test] = x_test @ weights + y_mean
    residual = ((targets - predicted) ** 2).sum(0)
    total = ((targets - targets.mean(0)) ** 2).sum(0)
    per_output = 1.0 - residual / np.maximum(total, 1e-12)
    return float(np.mean(per_output)), per_output.tolist()


def load_sample_indices(cfg):
    source = cfg.get("sample_source")
    if not source:
        raise ValueError("sample_source must point to an existing A run frozen_input.json")
    payload = json.loads(Path(str(source)).read_text())
    indices = [int(i) for i in payload["selected_indices"]]
    if len(indices) != len(set(indices)):
        raise ValueError("frozen input indices are not unique")
    limit = cfg.get("head_criteria", {}).get("samples")
    if limit not in (None, "None"):
        indices = indices[: int(limit)]
    if not indices:
        raise ValueError("no samples selected")
    return sorted(indices), str(source)


def build_context(cfg):
    from ..compat import ensure_torchvision_nms_schema
    ensure_torchvision_nms_schema()
    dataset = DATASETS.build(cfg["screen_dataloader"]["dataset"])
    probe = HEAD_PROBES.build(cfg["head_screening"]["probe"])
    if not Path(cfg["model"]["model_path"]).is_dir():
        raise FileNotFoundError("configured model directory is missing")
    checkpoint = resolve_checkpoint(cfg.get("checkpoint_path"), cfg["model"]["model_path"])
    wrapper = MODELS.build(cfg["model"])
    wrapper = attach_checkpoint(wrapper, checkpoint)
    collator = DATASETS.build(cfg["screen_dataloader"]["collator"], processor=wrapper.processor)
    runner = SimpleNamespace(wrapper=wrapper, dataset=dataset, collator=collator, world_size=1)
    return dataset, probe, checkpoint, wrapper, collator, runner


def encode_forward(runner, probe, index):
    sample, encoded, metadata, positions, rows, spans = probe.encode_sample(runner, index)
    forward = {k: v.to(runner.wrapper.input_device) for k, v in encoded.items()}
    forward.update(use_cache=False, output_attentions=False, return_dict=True, logits_to_keep=0)
    return sample, positions, rows, spans, forward


def run_decodability(cfg, root):
    indices, source = load_sample_indices(cfg)
    dataset, probe, checkpoint, wrapper, collator, runner = build_context(cfg)
    model = wrapper.model
    layers_expected = None
    features = {}
    targets = []
    used = []
    for order, index in enumerate(indices, 1):
        sample, positions, rows, spans, forward = encode_forward(runner, probe, index)
        box = parse_box(sample["answer"])
        if box is None or len(box) != 4:
            raise ValueError("sample answer does not carry a parseable box")
        store = {}
        with torch.no_grad():
            with capture_head_outputs(model, rows, store):
                model(**forward)
        if layers_expected is None:
            layers_expected = sorted(store)
        elif sorted(store) != layers_expected:
            raise ValueError("captured layer set changed between samples")
        for layer, tensor in store.items():
            for head in range(tensor.shape[0]):
                features.setdefault((layer, head), []).append(tensor[head].numpy())
        targets.append(np.asarray(box, dtype=np.float64))
        used.append(index)
        if order % 25 == 0 or order == len(indices):
            print(f"[DECODABILITY] {order}/{len(indices)}", flush=True)
    target_matrix = np.stack(targets)
    center_matrix = np.stack([[(box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0]
                              for box in targets])
    alpha = float(cfg.get("head_criteria", {}).get("ridge_alpha", 1.0))
    ranking = []
    for (layer, head), rows_list in features.items():
        matrix = np.stack(rows_list).astype(np.float64)
        r2, per_output = ridge_cv_r2(matrix, target_matrix, alpha=alpha)
        r2_center, _ = ridge_cv_r2(matrix, center_matrix, alpha=alpha)
        ranking.append(dict(layer=layer, head=head, label=head_label(layer, head),
                            r2_cv=r2, r2_center_cv=r2_center, r2_per_output=per_output,
                            output_norm_mean=float(np.linalg.norm(matrix, axis=1).mean())))
    ranking.sort(key=lambda row: (-row["r2_cv"], row["layer"], row["head"]))
    for rank, row in enumerate(ranking, 1):
        row["rank"] = rank
    payload = dict(schema=DECODABILITY_SCHEMA, status="completed", mode="decodability",
                   samples=len(used), selected_indices=used, sample_source=source,
                   checkpoint=checkpoint, head_shape=[max(r["layer"] for r in ranking) + 1,
                                                      max(r["head"] for r in ranking) + 1],
                   probe="teacher_forced_bbox_pminus1_row_mean_A_times_V",
                   decoder="ridge_5fold_cv", target="normalized_gt_box_xyxy_0_1000 (+center)",
                   ranking=ranking)
    with (root / "ranking_b.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["rank", "layer", "head", "label", "r2_cv",
                                                    "r2_center_cv", "output_norm_mean"])
        writer.writeheader()
        for row in ranking:
            writer.writerow({k: row[k] for k in writer.fieldnames})
    publish(root / "summary_b.json", payload)
    print(f"[DECODABILITY_DONE] samples={len(used)} heads={len(ranking)} best={ranking[0]['label']}",
          flush=True)
    return payload


def resolve_candidate_heads(cfg, root):
    criteria = cfg.get("head_criteria", {})
    heads = criteria.get("heads")
    if heads:
        return sorted({(int(h[0]), int(h[1])) for h in heads})
    source = criteria.get("heads_from_ranking")
    if not source:
        raise ValueError("head_criteria.heads or head_criteria.heads_from_ranking is required")
    top_k = int(criteria.get("top_k", 10))
    payload = json.loads(Path(str(source)).read_text())
    ranking = payload["ranking"]
    key = str(criteria.get("rank_key", "r2_cv"))
    ranking = sorted(ranking, key=lambda row: -float(row[key]))
    return sorted({(int(row["layer"]), int(row["head"])) for row in ranking[:top_k]})


def run_steerability(cfg, root):
    indices, source = load_sample_indices(cfg)
    criteria = cfg.get("head_criteria", {})
    candidates = resolve_candidate_heads(cfg, root)
    shift = float(criteria.get("shift", 200.0))
    sigma_scale = float(criteria.get("gaussian_sigma_scale", 0.5))
    sigma_floor = float(criteria.get("gaussian_sigma_floor_cells", 0.5))
    dataset, probe, checkpoint, wrapper, collator, runner = build_context(cfg)
    model = wrapper.model
    tokenizer = wrapper.processor.tokenizer
    per_head = {head: [] for head in candidates}
    baseline_records = []
    skipped_degenerate = 0
    skipped_geometry = 0
    for order, index in enumerate(indices, 1):
        sample, positions, rows, spans, forward = encode_forward(runner, probe, index)
        with torch.no_grad():
            logits = model(**forward).logits
        baseline_text = argmax_text(logits, positions, tokenizer)
        baseline_box = parse_box(baseline_text)
        del logits
        if baseline_box is None:
            continue
        if (baseline_box[2] - baseline_box[0]) <= 1.0 or (baseline_box[3] - baseline_box[1]) <= 1.0:
            skipped_degenerate += 1
            continue
        baseline_records.append(dict(dataset_index=index, text=baseline_text, box=baseline_box))
        for head in candidates:
            deltas = {}
            for sign in (1.0, -1.0):
                text, actual = shifted_answer(baseline_box, sign * shift)
                if abs(actual) < 0.5 * shift:
                    deltas[sign] = None
                    continue
                geometry_text = text
                # 用与干预完全相同的几何/高斯构造路径得到目标分布
                with torch.no_grad():
                    from ..evaluation.query_attention import query_geometry
                    try:
                        geometry = query_geometry(forward, wrapper.processor, model, geometry_text,
                                                  normalization="gaussian_preserve_query_mass",
                                                  gaussian_sigma_scale=sigma_scale,
                                                  gaussian_sigma_floor_cells=sigma_floor)
                    except ValueError:
                        skipped_geometry += 1
                        deltas[sign] = None
                        continue
                    target = torch.tensor(geometry["gt_distribution"],
                                          device=wrapper.input_device, dtype=torch.float32)
                    with steer_rows(model, head, rows, geometry["query_span"], target) as fired:
                        steered = model(**forward).logits
                if fired["count"] < 1:
                    raise ValueError("steering hook did not fire on any layer call")
                steered_box = parse_box(argmax_text(steered, positions, tokenizer))
                del steered
                deltas[sign] = None if steered_box is None else (box_center(steered_box), actual)
            if deltas[1.0] and deltas[-1.0]:
                plus = (deltas[1.0][0] - box_center(baseline_box))[0]
                minus = (deltas[-1.0][0] - box_center(baseline_box))[0]
                span = deltas[1.0][1] - deltas[-1.0][1]
                per_head[head].append(dict(dataset_index=index, plus=float(plus), minus=float(minus),
                                           injected_span=float(span),
                                           slope=float((plus - minus) / span)))
        if order % 10 == 0 or order == len(indices):
            print(f"[STEERABILITY] {order}/{len(indices)}", flush=True)
    ranking = []
    for head in candidates:
        rows_here = per_head[head]
        slopes = np.array([r["slope"] for r in rows_here]) if rows_here else np.zeros(0)
        ranking.append(dict(layer=head[0], head=head[1], label=head_label(*head),
                            samples=len(rows_here),
                            slope_mean=float(slopes.mean()) if slopes.size else None,
                            slope_median=float(np.median(slopes)) if slopes.size else None,
                            slope_std=float(slopes.std(ddof=1)) if slopes.size > 1 else None,
                            follow_fraction=float((slopes > 0).mean()) if slopes.size else None,
                            strong_follow_fraction=float((slopes > 0.5).mean()) if slopes.size else None))
    ranking.sort(key=lambda row: (-(row["slope_mean"] if row["slope_mean"] is not None else -9e9),
                                  row["layer"], row["head"]))
    for rank, row in enumerate(ranking, 1):
        row["rank"] = rank
    agreement = None
    reference = criteria.get("reference_predictions")
    if reference and baseline_records:
        lookup = {}
        for line in Path(str(reference)).read_text().splitlines():
            row = json.loads(line)
            lookup[int(row["dataset_index"])] = row
        matched = total = 0
        for record in baseline_records:
            row = lookup.get(record["dataset_index"])
            if row is None:
                continue
            total += 1
            target_box = parse_box(row["prediction"])
            if target_box is not None:
                def inter(a, b):
                    return max(0.0, min(a[2], b[2]) - max(a[0], b[0])) * max(0.0, min(a[3], b[3]) - max(a[1], b[1]))

                union = (target_box[2] - target_box[0]) * (target_box[3] - target_box[1]) + \
                        (record["box"][2] - record["box"][0]) * (record["box"][3] - record["box"][1]) - inter(target_box, record["box"])
                if union > 0 and inter(target_box, record["box"]) / union >= 0.5:
                    matched += 1
        agreement = dict(compared=total, iou_ge_0_5=int(matched),
                         rate=float(matched / total) if total else None)
    payload = dict(schema=STEERABILITY_SCHEMA, status="completed", mode="steerability",
                   samples=len(baseline_records), selected_indices=[r["dataset_index"] for r in baseline_records],
                   sample_source=source, checkpoint=checkpoint, shift=shift,
                   gaussian_sigma_scale=sigma_scale, gaussian_sigma_floor_cells=sigma_floor,
                   readout="teacher_forced_argmax_box", baseline_vs_greedy=agreement,
                   skipped_degenerate_baseline=skipped_degenerate,
                   skipped_geometry=skipped_geometry,
                   candidates=[head_label(*h) for h in candidates], ranking=ranking,
                   baseline_records=baseline_records)
    with (root / "ranking_c.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["rank", "layer", "head", "label", "samples",
                                                    "slope_mean", "slope_median", "slope_std",
                                                    "follow_fraction", "strong_follow_fraction"])
        writer.writeheader()
        for row in ranking:
            writer.writerow({k: row[k] for k in writer.fieldnames})
    publish(root / "summary_c.json", payload)
    print(f"[STEERABILITY_DONE] heads={len(ranking)} best={ranking[0]['label']} "
          f"slope={ranking[0]['slope_mean']}", flush=True)
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    parser.add_argument("overrides", nargs="*")
    args = parser.parse_args(argv)
    cfg = Config.fromfile(args.config).merge_options(args.overrides)
    criteria = cfg.get("head_criteria") or {}
    mode = str(criteria.get("mode", "decodability"))
    if mode not in ("decodability", "steerability"):
        raise ValueError("head_criteria.mode must be decodability or steerability")
    root = Path(cfg["work_dir"])
    root.mkdir(parents=True, exist_ok=False)
    try:
        if mode == "decodability":
            run_decodability(cfg, root)
        else:
            run_steerability(cfg, root)
    except BaseException as error:
        publish(root / "failure.json", dict(status="failed", mode=mode,
                                            exception=type(error).__name__, reason=str(error)))
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
