# e014-model-parallel-ddp4x2-capability-20261021 · 用户要求试验每个模型拆到两张卡、四个副本DDP的4x2方式。本次仅实现并验证混合模型并行＋DDP训练能力：复用现有Qwen3-VL-8B和SFT入口，fresh

- 父 Run：`e014-selector-linear-decay4041-to5388-eval1766-20261021`
- 来源版本：2026-10-21T13:39:45
- 状态：failed
- Workspace：03

## 本次任务
用户要求试验每个模型拆到两张卡、四个副本DDP的4x2方式。本次仅实现并验证混合模型并行＋DDP训练能力：复用现有Qwen3-VL-8B和SFT入口，fresh LoRA，不继承父训练checkpoint或完整训练命令；在同8张3090上核对GPU配对、跨卡前反向、全副本LoRA梯度/参数一致、checkpoint保存恢复和1/2/4-shot真实样本的短程更新及显存。先用已有Qwen3验证并行能力；FOCUS Qwen2迁移和正式长训练另行安排。本次授权必要代码发布、指定SHA部署、聚焦测试和有限GPU验证，所有产物写独立子Run，不改历史。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户要求4副本×2卡DDP能力验证。使用8个GOT训练视频真实1/2/4shot、最后帧Query、同原采样器；Qwen3-VL-8B fresh语言NF4LoRA r8/alpha16、BF16/SDPA、nonreentrant checkpoint、4096 raw patches/图、前14/后22层切分、4DDP进程、每副本batch1累积4/global16、SFT lr2e-4/warmup.03/clip.3/seed20260901。每shot2更新32呈现；4shot保存step2后独立目录恢复至step3再16呈现，共7更新112呈现。核每次更新全LoRA跨rank SHA一致、全卡峰值、保存恢复与有限梯度。包含19左右聚焦CPU测试（实际计数以日志为准）。无历史checkpoint续训、无正式泛化评测；不继承父训练预算、指标、数据定义或Claim。任一步失败停止，不自动重跑。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-capability-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'6b5204a012e6a06a5c6419a507ccc99820ccd2234207f19f63cfc1d6f195880a'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：17f494126b06b611bb18baff40d3e4ae5ea4a1b4
- 随机种子：20260901
- 配置：configs/sft/qwen3vl_lora_model_parallel_ddp.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-capability-20261021/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-capability-20261021/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-capability-20261021/metrics.json

## 结果
尚无结果。

### 分析
真实exit1。4×2 DDP的1shot与2shot各完成2步/32呈现，全部LoRA更新后四副本SHA一致且已保存checkpoint。1shot峰值allocated12.28184/reserved13.34375GiB，2shot15.37214/16.19531GiB。4shot在首步backward因GPU1请求3.33GiB、已有allocated21.13GiB而OOM，未完成4shot更新，恢复测试未执行。失败产物已保留并SHA核验36份文件。后续独立子Run只变更BF16 embedding和autocast以验证内存优化，不能在本Run中冒记成功。

### 局限
8个GOT训练序列、短程Qwen3-VL-8B NF4 SFT能力；没有mIoU评测、全数据最长序列或Qwen2/完整FOCUS结论。

### Claim 边界
仅当前Qwen3 NF4 SFT短程多图能力，非Qwen2/FOCUS attention loss/GRPO验证，不代表全量最长样本都可运行或科研性能提升。

### 审核入口
```json
[
  ".pi/analysis/e014/model-parallel-ddp-20261021/failure_download_audit.json",
  ".pi/analysis/e014/model-parallel-ddp-20261021/failure_receipt.json"
]
```

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
