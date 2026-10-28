# e015-iploc144-qwen2-4shot-restart-r2-20261023 · IPLoc官方144修正划分后Qwen2四参考帧重新训练

- workflow: v2 / failed / 运行失败
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-a87a6fd0aa97d7e09b626e92 / failed

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
（待补充）

## 2. 目的
修正数据泄漏与近邻参考帧采样后重新启动自有SFT→GRPO多框score→VQA，使用作者发布144条评测。

## 3. 方法（干预 · 对照 · 指标与判定规则）
（待补充：干预什么、和什么比、什么算通过）

### 已注册指标定义
- **1shot VQA mIoU** (`vqa_miou_1shot`)：100*mean(selected IoU)；VQA mIoU；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **1shot VQA Acc50** (`vqa_acc50_1shot`)：100*mean(selected IoU>=0.5)；VQA Acc50；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **1shot Proposal Oracle mIoU** (`oracle_miou_1shot`)：100*mean(max candidate IoU)；Proposal Oracle mIoU；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **1shot Proposal Oracle Acc50** (`oracle_acc50_1shot`)：100*mean(max candidate IoU>=0.5)；Proposal Oracle Acc50；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **1shot Oracle与实际mIoU差距** (`oracle_gap_1shot`)：100*mean(oracle IoU-selected IoU)；Oracle与实际mIoU差距；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **1shot 候选可命中但未选中数量** (`oracle_miss_count_1shot`)：count(selected IoU<0.5<=oracle IoU)；候选可命中但未选中数量；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **2shot VQA mIoU** (`vqa_miou_2shot`)：100*mean(selected IoU)；VQA mIoU；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **2shot VQA Acc50** (`vqa_acc50_2shot`)：100*mean(selected IoU>=0.5)；VQA Acc50；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **2shot Proposal Oracle mIoU** (`oracle_miou_2shot`)：100*mean(max candidate IoU)；Proposal Oracle mIoU；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **2shot Proposal Oracle Acc50** (`oracle_acc50_2shot`)：100*mean(max candidate IoU>=0.5)；Proposal Oracle Acc50；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **2shot Oracle与实际mIoU差距** (`oracle_gap_2shot`)：100*mean(oracle IoU-selected IoU)；Oracle与实际mIoU差距；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **2shot 候选可命中但未选中数量** (`oracle_miss_count_2shot`)：count(selected IoU<0.5<=oracle IoU)；候选可命中但未选中数量；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **4shot VQA mIoU** (`vqa_miou_4shot`)：100*mean(selected IoU)；VQA mIoU；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **4shot VQA Acc50** (`vqa_acc50_4shot`)：100*mean(selected IoU>=0.5)；VQA Acc50；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **4shot Proposal Oracle mIoU** (`oracle_miou_4shot`)：100*mean(max candidate IoU)；Proposal Oracle mIoU；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **4shot Proposal Oracle Acc50** (`oracle_acc50_4shot`)：100*mean(max candidate IoU>=0.5)；Proposal Oracle Acc50；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **4shot Oracle与实际mIoU差距** (`oracle_gap_4shot`)：100*mean(oracle IoU-selected IoU)；Oracle与实际mIoU差距；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **4shot 候选可命中但未选中数量** (`oracle_miss_count_4shot`)：count(selected IoU<0.5<=oracle IoU)；候选可命中但未选中数量；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **历史E014 VQA mIoU** (`baseline_vqa_miou`)：100*mean(historical IoU on common1728 query indices)；历史E014 VQA mIoU；mean / 同1728 Query重算旧原proposal+linear5388；非单因子对照
- **历史E014 Oracle mIoU** (`baseline_oracle_miou`)：100*mean(historical IoU on common1728 query indices)；历史E014 Oracle mIoU；mean / 同1728 Query重算旧原proposal+linear5388；非单因子对照
- **IPLoc144 1shot VQA mIoU** (`iploc144_vqa_miou_1shot`)：100*mean(selected IoU)；VQA mIoU；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **IPLoc144 1shot VQA Acc50** (`iploc144_vqa_acc50_1shot`)：100*mean(selected IoU>=0.5)；VQA Acc50；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **IPLoc144 1shot Proposal Oracle mIoU** (`iploc144_oracle_miou_1shot`)：100*mean(max candidate IoU)；Proposal Oracle mIoU；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **IPLoc144 1shot Proposal Oracle Acc50** (`iploc144_oracle_acc50_1shot`)：100*mean(max candidate IoU>=0.5)；Proposal Oracle Acc50；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **IPLoc144 1shot Oracle与实际mIoU差距** (`iploc144_oracle_gap_1shot`)：100*mean(oracle IoU-selected IoU)；Oracle与实际mIoU差距；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **IPLoc144 1shot 候选可命中但未选中数量** (`iploc144_oracle_miss_count_1shot`)：count(selected IoU<0.5<=oracle IoU)；候选可命中但未选中数量；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **IPLoc144 2shot VQA mIoU** (`iploc144_vqa_miou_2shot`)：100*mean(selected IoU)；VQA mIoU；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **IPLoc144 2shot VQA Acc50** (`iploc144_vqa_acc50_2shot`)：100*mean(selected IoU>=0.5)；VQA Acc50；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **IPLoc144 2shot Proposal Oracle mIoU** (`iploc144_oracle_miou_2shot`)：100*mean(max candidate IoU)；Proposal Oracle mIoU；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **IPLoc144 2shot Proposal Oracle Acc50** (`iploc144_oracle_acc50_2shot`)：100*mean(max candidate IoU>=0.5)；Proposal Oracle Acc50；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **IPLoc144 2shot Oracle与实际mIoU差距** (`iploc144_oracle_gap_2shot`)：100*mean(oracle IoU-selected IoU)；Oracle与实际mIoU差距；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **IPLoc144 2shot 候选可命中但未选中数量** (`iploc144_oracle_miss_count_2shot`)：count(selected IoU<0.5<=oracle IoU)；候选可命中但未选中数量；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **IPLoc144 4shot VQA mIoU** (`iploc144_vqa_miou_4shot`)：100*mean(selected IoU)；VQA mIoU；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **IPLoc144 4shot VQA Acc50** (`iploc144_vqa_acc50_4shot`)：100*mean(selected IoU>=0.5)；VQA Acc50；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **IPLoc144 4shot Proposal Oracle mIoU** (`iploc144_oracle_miou_4shot`)：100*mean(max candidate IoU)；Proposal Oracle mIoU；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **IPLoc144 4shot Proposal Oracle Acc50** (`iploc144_oracle_acc50_4shot`)：100*mean(max candidate IoU>=0.5)；Proposal Oracle Acc50；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **IPLoc144 4shot Oracle与实际mIoU差距** (`iploc144_oracle_gap_4shot`)：100*mean(oracle IoU-selected IoU)；Oracle与实际mIoU差距；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **IPLoc144 4shot 候选可命中但未选中数量** (`iploc144_oracle_miss_count_4shot`)：count(selected IoU<0.5<=oracle IoU)；候选可命中但未选中数量；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理4shot；非法/空输出IoU=0

## 4. 详细实现细节
修正后独立重启：官方IPLoc commit27682bc2的LaSOT144条1/2/4shot逐条保留；训练LaSOT排除官方全部36类别，剩余真实原始类别补集（非声称FOCUS35/35）；GOT/TAO仅原train来源并保留旧holdout源视频保护。训练参考索引i*(N//4)，Query=N-1，TAO按标注目标时间线，异常样本剔除不挪动帧。GRPO双方身份按测试类别及源视频排除，整正负对及ABBA关联组过滤。旧E015有68个测试Query污染，SFT和selector均从官方Qwen2基础权重fresh LoRA启动，不复用旧adapter。复用已发布28c72aff代码、双卡×4副本及图像缓存。原SFT4epoch/global64/lr2e-4和GRPO400步奖励/score/prompt不变；GRPO后先官方144各shot评测并保存proposal，再独立VQA训练评测。新iploc144指标命名空间，无旧1728基线。任何数据审计或训练错误停止；输入脚本和来源SHA完整记录。此为自有方法在作者公开评测清单上的训练适配，不是FOCUS完整复现。

- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试路径（不代表已执行）：（未登记，可留空）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r2-20261023/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'ef47ca557038a21c16c88b41b24a7f75f514d55fc2fda929b17aac21baf5fcb9'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'`
- commit: `28c72afff503650316e37039c5931f2587b62b45`
- workspace: 03
- tmux: incontext-E-015-e015-iploc144-qwen2-4shot-restart-r2-20261023
- log: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r2-20261023/managed_console.log
- output: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r2-20261023/outputs
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
  "necessity": "旧E015训练与官方测试有68相同Query，旧adapter不复用；用户明确授权修正并重启。",
  "implementation_details": "修正后独立重启：官方IPLoc commit27682bc2的LaSOT144条1/2/4shot逐条保留；训练LaSOT排除官方全部36类别，剩余真实原始类别补集（非声称FOCUS35/35）；GOT/TAO仅原train来源并保留旧holdout源视频保护。训练参考索引i*(N//4)，Query=N-1，TAO按标注目标时间线，异常样本剔除不挪动帧。GRPO双方身份按测试类别及源视频排除，整正负对及ABBA关联组过滤。旧E015有68个测试Query污染，SFT和selector均从官方Qwen2基础权重fresh LoRA启动，不复用旧adapter。复用已发布28c72aff代码、双卡×4副本及图像缓存。原SFT4epoch/global64/lr2e-4和GRPO400步奖励/score/prompt不变；GRPO后先官方144各shot评测并保存proposal，再独立VQA训练评测。新iploc144指标命名空间，无旧1728基线。任何数据审计或训练错误停止；输入脚本和来源SHA完整记录。此为自有方法在作者公开评测清单上的训练适配，不是FOCUS完整复现。"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
