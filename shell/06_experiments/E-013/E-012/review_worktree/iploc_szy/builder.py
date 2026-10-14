"""Top-level builders that connect configuration sections."""

from typing import Any, Mapping

from .registry import DATASETS, MODELS, RUNNERS


def build_training(cfg: Mapping[str, Any]) -> Any:
    """Build the model, dataset, collator, and training runner.

    The processor is owned by the model wrapper and injected into the collator,
    ensuring both components use exactly the same tokenizer and image settings.
    """
    model = MODELS.build(cfg["model"])
    print(model.__dict__.keys())
    hf_model = model.model
    dataloader_cfg = cfg["train_dataloader"]
    dataset = DATASETS.build(dataloader_cfg["dataset"])
    collator = DATASETS.build(
        dataloader_cfg["collator"],
        processor=model.processor,
    )
    
    total = sum(p.numel() for p in hf_model.parameters())
    trainable = sum(p.numel() for p in hf_model.parameters() if p.requires_grad)
    lora = sum(
        p.numel()
        for name, p in hf_model.named_parameters()
        if "lora_" in name
    )

    print(f"[Model] Total params:     {total:,}")
    print(f"[Model] Trainable params: {trainable:,}")
    print(f"[Model] LoRA params:      {lora:,}")
    print(f"[Model] Trainable ratio:  {100 * trainable / total:.6f}%")

    runner_cfg = dict(cfg["runner"])
    runner_cfg.update(
        model=model,
        dataset=dataset,
        collator=collator,
        work_dir=cfg["work_dir"],
        batch_size=dataloader_cfg.get("batch_size", 1),
    )
    return RUNNERS.build(runner_cfg)
