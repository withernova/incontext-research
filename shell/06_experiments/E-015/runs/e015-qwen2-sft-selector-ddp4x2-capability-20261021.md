# e015-qwen2-sft-selector-ddp4x2-capability-20261021 · 双卡副本的多帧训练检查

- workflow: v2 / failed / 运行失败
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-0c6647895fce54dc381c9378 / failed

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
（待补充）

## 2. 目的
确认换成Qwen2后，多参考帧训练与选择器能否在现有八张卡运行，并核对保存恢复是否正确。

## 3. 方法（干预 · 对照 · 指标与判定规则）
（待补充：干预什么、和什么比、什么算通过）

## 4. 详细实现细节
Qwen2-VL-7B-Instruct官方eed13092版本；4副本×2卡，10/18层，NF4/BF16/SDPA，4096rawpatch每图。固定既有8个GOT训练视频，同Query1/2/4shot各2更新、4shot恢复至3步、独立VQA选择SFT2步；global16，全部LoRA跨rank逐步SHA、有限梯度、实际参数变化、全卡显存、恢复连续性。SFT保留置信度格式损失0.1，选择器不加该损失；选择器候选为GT加错误角落框，专用于链路能力，不作为性能。尚不验证GRPO和完整数据显存。正式阶段另Run。 采样seed11451、模型初始化seed20260901；记录各自快照。 增加8例实际五图VQA推理，记录真实grid/prefix并核对每图不超过4096rawpatch；GT候选仅作接口检查，不报告定位收益。启动前执行新增GRPO launcher/worker输出目录回归。

- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试路径（不代表已执行）：（未登记，可留空）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-sft-selector-ddp4x2-capability-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'183b1b5e5cfa7f43f098b869624198a2edd9e02fee6a90978abd35df2aee8e90'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'`
- commit: `dcdf731dfa0e6d672ee8a684e4c0e23e1f7175c8`
- workspace: 03
- tmux: incontext-E-015-e015-qwen2-sft-selector-ddp4x2-capability-20261021
- log: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-sft-selector-ddp4x2-capability-20261021/managed_console.log
- output: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-sft-selector-ddp4x2-capability-20261021/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
（可留空；如有明显的数据、模型或比较限制，请简短记录。）

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "necessity": "此前成功结果只有Qwen3，不能直接证明Qwen2可运行。",
  "implementation_details": "Qwen2-VL-7B-Instruct官方eed13092版本；4副本×2卡，10/18层，NF4/BF16/SDPA，4096rawpatch每图。固定既有8个GOT训练视频，同Query1/2/4shot各2更新、4shot恢复至3步、独立VQA选择SFT2步；global16，全部LoRA跨rank逐步SHA、有限梯度、实际参数变化、全卡显存、恢复连续性。SFT保留置信度格式损失0.1，选择器不加该损失；选择器候选为GT加错误角落框，专用于链路能力，不作为性能。尚不验证GRPO和完整数据显存。正式阶段另Run。 采样seed11451、模型初始化seed20260901；记录各自快照。 增加8例实际五图VQA推理，记录真实grid/prefix并核对每图不超过4096rawpatch；GT候选仅作接口检查，不报告定位收益。启动前执行新增GRPO launcher/worker输出目录回归。",
  "claim_boundary": "仅八视频短程工程能力，非正式性能或GRPO能力。"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
