#!/usr/bin/env python3
"""Generate localization answers and evaluate configured bbox metrics."""

import argparse
import json
from typing import Optional, Sequence

import torch
from PIL import Image

from iploc_szy import DATASETS, EVALUATORS, MODELS
from iploc_szy.branching import load_experiment_config
from iploc_szy.run_snapshot import save_snapshot, save_prompt_example


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse inference, adapter, generation, and sample-limit options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    parser.add_argument("--adapter", help="Optional trained PEFT adapter path")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--max-new-tokens", type=int, default=None)
    parser.add_argument("--cfg-options", nargs="*", default=[])
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Load configured components, generate predictions, and report metrics."""
    args = parse_args(argv)
    config = load_experiment_config(args.config, args.cfg_options)
    settings = config.setdefault("evaluation", {})
    for key, value in (("limit", args.limit), ("max_new_tokens", args.max_new_tokens),
                       ("adapter", args.adapter)):
        if value is not None:
            settings[key] = value
    settings.setdefault("limit", 10)
    settings.setdefault("max_new_tokens", 32)
    limit = settings["limit"]
    if limit is not None and (type(limit) is not int or limit <= 0):
        raise ValueError("evaluation.limit must be None or a positive integer")
    if type(settings["max_new_tokens"]) is not int or settings["max_new_tokens"] <= 0:
        raise ValueError("evaluation.max_new_tokens must be a positive integer")
    config.setdefault("work_dir", "work_dirs/infer")
    snapshot = save_snapshot(config, args.config, "infer")
    model_wrapper = MODELS.build(config["model"])
    dataset = DATASETS.build(config["test_dataloader"]["dataset"])
    evaluator_config = config.get(
        "evaluator", {"type": "LocalizationEvaluator"}
    )

    if settings.get("adapter"):
        from peft import PeftModel

        model_wrapper.model = PeftModel.from_pretrained(
            model_wrapper.model,
            settings["adapter"],
        ).eval()

    save_prompt_example(snapshot, dataset[0])
    rows = []
    for index in range(len(dataset) if limit is None else min(limit, len(dataset))):
        sample = dataset[index]
        prediction = generate(model_wrapper, sample, settings["max_new_tokens"])
        print(
            json.dumps(
                {
                    "id": sample["id"],
                    "dataset": str(sample.get("raw", {}).get("dataset", "unknown")),
                    "prediction": prediction,
                    "target": sample["answer"],
                },
                ensure_ascii=False,
            )
        )
        rows.append({
            "id": sample["id"],
            "dataset": str(sample.get("raw", {}).get("dataset", "unknown")),
            "prediction": prediction,
            "target": sample["answer"],
        })
    evaluator = EVALUATORS.build(evaluator_config)
    for row in rows:
        evaluator.process(row["prediction"], row["target"], row["id"])
    metrics = evaluator.evaluate()
    by_dataset = {}
    for dataset_name in sorted({row["dataset"] for row in rows}):
        per_dataset = EVALUATORS.build(evaluator_config)
        for row in rows:
            if row["dataset"] == dataset_name:
                per_dataset.process(row["prediction"], row["target"], row["id"])
        by_dataset[dataset_name] = per_dataset.evaluate()
    print(json.dumps({**metrics, "datasets": sorted(by_dataset), "by_dataset": by_dataset},
                     indent=2, ensure_ascii=False))
    return 0


def generate(model_wrapper, sample, max_new_tokens: int) -> str:
    """Generate one answer from the sample's prompt-only conversation."""
    prompt_messages = sample["messages"][:-1]
    images = []
    for path in sample["image_paths"]:
        with Image.open(path) as image:
            images.append(image.convert("RGB"))
    text = model_wrapper.processor.apply_chat_template(
        prompt_messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = model_wrapper.processor(
        text=[text],
        images=images,
        return_tensors="pt",
    ).to(model_wrapper.input_device)
    with torch.no_grad():
        output_ids = model_wrapper.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
        )
    generated_ids = output_ids[:, inputs.input_ids.shape[1] :]
    return model_wrapper.processor.batch_decode(
        generated_ids,
        skip_special_tokens=True,
    )[0]


if __name__ == "__main__":
    raise SystemExit(main())
