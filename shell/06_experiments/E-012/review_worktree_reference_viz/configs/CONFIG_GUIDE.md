# 按职能组织的配置入口

共同主配置：`configs/_base_/localization_sft.py`。
它继承模型配置 `qwen3vl_lora_ddp.py`，集中定义 SFT runner、默认优化器和日志 hooks。

| 职能 | 配置 |
| --- | --- |
| Grounding JSON 训练配方及评估数据/参数 | `configs/sft/qwen3vl_8b_grounding.py` |
| Grounding 任务、checkpoint、实验命名 | `configs/sft/qwen3vl_8b_grounding_tasks.py` |
| FOCUS 训练配方 | `configs/sft/qwen3vl_8b_lora_focus_1shot_ddp4_4bit.py` |
| FOCUS 训练/评估/head screening 任务 | `configs/sft/qwen3vl_8b_focus_tasks.py` |

两个任务配置都通过各自的配方追溯到共同主配置。
选择任务用 `branch.action=train|evaluate|head_screen`；head screening 需要配置
`head_screening`，当前只有 FOCUS 任务预设提供这一段。
新建实验时修改任务中的 `named_run`（实验 ID、名称、checkpoint），
用 `runtime` 覆盖配方的数据和参数。配方内现有实验路径保留为当前预设，
不是跨实验通用数据集；迁移不会更换数据、prompt 或训练设置。

带 E-009/E-011 的旧配置文件仅作为兼容入口，新的设置应修改上述职能配置。
旧 bash 入口仍可使用；也可以传入职能配置路径，例如：

```bash
bash tools/run/train/run_e011_qwen3_grounding_sft_ddp4.sh configs/sft/qwen3vl_8b_grounding.py
bash tools/run/eval/run_e011_qwen3_grounding_adapter_eval.sh configs/sft/qwen3vl_8b_grounding_tasks.py
```

每次启动保存 `<work_dir>/logs/config_snapshots/<调用>/`：
依赖配置原文、最终合成配置、路径与哈希、prompt 实现及样例。
旧入口经过的兼容配置也会保存在依赖快照中。
