#!/usr/bin/env python3
"""E-014 step800, eight sample-sharded replicas; no training or GT selection.

Reuse the shared manifest dataset, generator, model loader, evaluator and AP.
A formal approved managed Run is required. --inspect creates no outputs.
"""
import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
ROOT = Path("/defaultShare/archive/songzhengyue/projects/IPLoc")
DEFAULT = REPO / "configs/experiments/E-014/evaluation/e014_step800_eval1766.py"


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def settings(path):
    path = Path(path).resolve()
    path.relative_to(REPO / "configs/experiments/E-014/evaluation")
    spec = deepcopy(runpy.run_path(str(path))["settings"])
    if (spec["run_id"] != "e014-step800-variable-candidates-eval1766-8gpu"
            or spec["dataset_size"] != 1766 or spec["nproc_per_node"] != 8
            or spec["evaluation"] != dict(max_new_tokens=192, do_sample=False,
                                            vision_max_patch_tokens=4096, seed=20260901)):
        raise ValueError("frozen step800/1766 evaluation settings changed")
    for key in ("manifest", "checkpoint", "model_path"):
        Path(spec[key]).resolve().relative_to(ROOT.resolve())
    if Path(spec["checkpoint"]).name != "step_000800":
        raise ValueError("this evaluation requires step800, not latest")
    return spec


def frozen_sources(spec):
    from iploc_szy.rl.e014_resume import digest, FILES
    cp = Path(spec["checkpoint"])
    hashes = {str(cp / name): digest(cp / name) for name in FILES}
    for path in (Path(spec["manifest"]), cp.parent.parent / "config_snapshot.json",
                 Path(spec["model_path"]) / "config.json"):
        hashes[str(path)] = digest(path)
    if hashes[spec["manifest"]] != spec["manifest_sha256"]:
        raise ValueError("original 1766 manifest SHA mismatch")
    return hashes


def verify_sources(spec):
    from iploc_szy.rl.e014_resume import digest
    for path, expected in spec["source_sha256"].items():
        if digest(path) != expected:
            raise ValueError("read-only evaluation source changed")


def registered_manifest(spec, destination):
    """Replace only image_path cells with existing registered read-only aliases."""
    rows = json.loads(Path(spec["manifest"]).read_text())
    if len(rows) != 1766:
        raise ValueError("expected the original 1766 records")
    aliases = [(p.resolve(), p) for p in (ROOT / "mechanism/dataset").iterdir() if p.is_dir()]
    aliases.sort(key=lambda pair: len(str(pair[0])), reverse=True)
    changed = deepcopy(rows)
    for old, new in zip(rows, changed):
        new_paths = []
        for value in old["image_path"]:
            wrapped = isinstance(value, list) and len(value) == 1
            original = Path(value[0] if wrapped else value)
            selected = None
            for physical, alias in aliases:
                try:
                    selected = alias / original.relative_to(physical)
                    break
                except ValueError:
                    continue
            if selected is None or not selected.is_file():
                raise ValueError("image has no existing registered dataset alias")
            new_paths.append([str(selected)] if wrapped else str(selected))
        new["image_path"] = new_paths
        if {k: v for k, v in old.items() if k != "image_path"} != {
                k: v for k, v in new.items() if k != "image_path"}:
            raise ValueError("manifest identity or labels changed")
    write_json(destination, changed)
    from iploc_szy.rl.e014_resume import digest
    return str(destination), digest(destination)


def dataset(spec):
    from iploc_szy import DATASETS
    result = DATASETS.build(dict(type="E014VariableCandidateLocalizationDataset",
        ann_file=spec["derived_manifest"], ann_file_sha256=spec["derived_manifest_sha256"],
        target_role="positive-image", normalized_scale=1000))
    if len(result) != 1766 or len({row["id"] for row in result.rows}) != 1766:
        raise ValueError("1766 unique query samples required")
    return result


def check_gpu_availability():
    apps = subprocess.run(["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader,nounits"],
                          capture_output=True, text=True, check=True)
    memory = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                            capture_output=True, text=True, check=True)
    values = [int(x.strip()) for x in memory.stdout.splitlines() if x.strip()]
    if apps.stdout.strip() or len(values) != 8 or any(x >= 64 for x in values):
        raise RuntimeError("eight idle GPUs required; no other process is stopped")


def worker(path):
    import torch
    from peft import prepare_model_for_kbit_training
    from tools.analysis.run_e013_reference_sensitivity import load_base_model, attach_adapters
    from tools.evaluate import _generate, configure_vision_limit
    from iploc_szy.rl.e014_resume import digest
    path = Path(path).resolve()
    path.relative_to(ROOT / "experiments/E-014")
    spec = json.loads(path.read_text())
    rank, world = int(os.environ["LOCAL_RANK"]), int(os.environ["WORLD_SIZE"])
    if world != 8 or not 0 <= rank < 8:
        raise ValueError("evaluation must use the planned eight ranks")
    verify_sources(spec)
    data = dataset(spec)
    torch.cuda.set_device(rank)
    torch.manual_seed(spec["evaluation"]["seed"] + rank)
    device = torch.device("cuda", rank)
    base, processor = load_base_model(spec["model_path"], device, load_in_4bit=True)
    # Match the old Qwen3VLLoRADDP evaluation's k-bit normalization preparation.
    base.config.use_cache = False
    base = prepare_model_for_kbit_training(base, use_gradient_checkpointing=False)
    model = attach_adapters(base, [dict(adapter=str(Path(spec["checkpoint"]) / "adapter/policy"),
                                      name="policy")])
    model.eval()
    wrapper = SimpleNamespace(model=model, peft_model=model, processor=processor, input_device=device)
    pixels = configure_vision_limit(processor, spec["evaluation"])
    directory = path.parent / "workers" / ("rank{}".format(rank))
    predictions = directory / "predictions.jsonl"
    count = 0
    with predictions.open("x", encoding="utf-8") as handle:
        for index in range(rank, len(data), world):
            sample = data[index]
            if sample["messages"][-1] != {"role": "assistant", "content": []}:
                raise ValueError("empty generation placeholder required; no query GT in prompt")
            prediction = _generate(wrapper, sample, spec["evaluation"])
            row = dict(dataset_index=index, id=sample["id"], prediction=prediction,
                       target=sample["answer"], dataset=sample["raw"]["dataset"],
                       sequence=sample["raw"].get("sequence", ""), rank=rank)
            handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
            handle.flush()
            count += 1
            if count % 10 == 0:
                print(json.dumps(dict(status="evaluation_progress", rank=rank, samples=count)), flush=True)
    verify_sources(spec)
    write_json(directory / "completed.json", dict(rank=rank, samples=count,
        predictions_sha256=digest(predictions), vision_max_pixels=pixels))
    print(json.dumps(dict(status="evaluation_rank_complete", rank=rank, samples=count)), flush=True)


def merge(spec, payload):
    from iploc_szy import EVALUATORS
    from iploc_szy.rl.e014_resume import digest
    from tools.evaluate import metrics_by_dataset
    from tools.analysis.run_e013_multi_candidate import ap_metrics, valid_target
    data = dataset(spec)
    rows, counts = [], []
    for rank in range(8):
        directory = payload / "workers" / ("rank{}".format(rank))
        path = directory / "predictions.jsonl"
        proof = json.loads((directory / "completed.json").read_text())
        part = [json.loads(line) for line in path.read_text().splitlines()]
        expected = list(range(rank, 1766, 8))
        if (proof["rank"] != rank or proof["samples"] != len(expected)
                or digest(path) != proof["predictions_sha256"]
                or [row["dataset_index"] for row in part] != expected
                or any(row["rank"] != rank for row in part)):
            raise ValueError("worker coverage or integrity failed")
        rows.extend(part)
        counts.append(len(part))
    rows.sort(key=lambda row: row["dataset_index"])
    if len(rows) != 1766 or len({row["id"] for row in rows}) != 1766:
        raise ValueError("incomplete or duplicate merged sample coverage")
    evaluator = EVALUATORS.build(spec["evaluator"])
    for row in rows:
        original = data[row["dataset_index"]]
        if (row["id"] != original["id"] or row["target"] != original["answer"]
                or row["dataset"] != original["raw"]["dataset"]
                or row["sequence"] != original["raw"].get("sequence", "")):
            raise ValueError("prediction-to-input identity mismatch")
        evaluator.process(row["prediction"], row["target"], row["id"])
    enriched = [{**a, **b} for a, b in zip(rows, evaluator.rows)]
    output = payload / "predictions.jsonl"
    with output.open("x", encoding="utf-8") as handle:
        for row in enriched:
            handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
    valid = [row for row in enriched if valid_target(row)]
    verify_sources(spec)
    return dict(status="completed", metrics=evaluator.evaluate(),
        by_dataset=metrics_by_dataset(rows, spec["evaluator"]),
        valid_gt_ap=ap_metrics(valid), legacy_all_query_ap=ap_metrics(enriched),
        evaluated_samples=1766, world_size=8, shard_counts=counts,
        source_sha256=spec["source_sha256"], checkpoint=spec["checkpoint"],
        derived_manifest_sha256=spec["derived_manifest_sha256"],
        evaluation=spec["evaluation"], predictions=str(output), predictions_sha256=digest(output),
        limitations="Previously viewed test set; no matched baseline or tuning. Selected-box single-GT AP, not full detection AP.")


def coordinator(args):
    from tools.run_e014_grpo import validate_run_layout, phase
    from iploc_szy.rl.e014_resume import digest
    spec = settings(args.config)
    run = ROOT / "experiments/E-014" / spec["run_id"]
    if args.inspect:
        print(json.dumps(spec, indent=2))
        return
    payload = validate_run_layout(run)
    check_gpu_availability()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=REPO):
        raise RuntimeError("evaluation requires clean source")
    spec["source_sha256"] = frozen_sources(spec)
    import torch
    state = torch.load(Path(spec["checkpoint"]) / "optimizer.pt", map_location="cpu", weights_only=True)
    if state["steps"] != 800:
        raise ValueError("checkpoint optimizer progress is not step800")
    del state
    payload.mkdir(parents=True, exist_ok=False)
    code = 1
    try:
        manifest, sha = registered_manifest(spec, payload / "manifest.json")
        spec.update(derived_manifest=manifest, derived_manifest_sha256=sha, git_commit=head,
                    config_sha256=digest(args.config))
        for rank in range(8):
            (payload / "workers" / ("rank{}".format(rank))).mkdir(parents=True)
        for name, subdir in (("HF_HOME", "huggingface"), ("TORCH_HOME", "torch"),
                              ("XDG_CACHE_HOME", "xdg"), ("TRITON_CACHE_DIR", "triton")):
            cache = payload / "cache" / subdir
            cache.mkdir(parents=True, exist_ok=True)
            os.environ[name] = str(cache)
        (payload / "cache/xdg/torch/kernels").mkdir(parents=True, exist_ok=True)
        spec_path = payload / "plan.json"
        write_json(spec_path, spec)
        check_gpu_availability()
        code = phase([sys.executable, "-m", "torch.distributed.run", "--standalone",
                      "--nproc_per_node=8", str(Path(__file__).resolve()),
                      "--worker-config", str(spec_path)], payload / "evaluation.log")
        if code:
            raise RuntimeError("evaluation worker exited nonzero; preserve partial results")
        code = 1
        result = merge(spec, payload)
        write_json(run / "metrics.json", result)
        code = 0
        print(json.dumps(dict(status="evaluation_complete", samples=1766, world_size=8)), flush=True)
    finally:
        (payload / "exit_code.txt").write_text(str(code) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT)
    parser.add_argument("--worker-config", type=Path)
    parser.add_argument("--inspect", action="store_true")
    args = parser.parse_args()
    if args.worker_config:
        if args.inspect:
            raise ValueError("worker cannot inspect")
        worker(args.worker_config)
    else:
        coordinator(args)


if __name__ == "__main__":
    main()
