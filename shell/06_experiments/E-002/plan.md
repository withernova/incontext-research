# E-002 · 使用 Personalize / POIL 数据集验证 ICOL instance-level identification

- status: draft
- kind: idea_validation / dataset_protocol_reproduction
- source_ref: personal2026
- claim_refs: 
- priority: medium
- created: 2026-07-13T00:00:00+08:00
- updated: 2026-07-13T14:04:49

## 实验目标
基于 Personalize / POIL positive/negative query protocol，评估 Rex-Omni/ICOL 模型是否具备 reference-conditioned instance localization 与 negative rejection 能力。

## 假设
Localization-only ICOL 模型可能在 in-class negative query 上产生高 false-positive；加入 self-posed identification 或相关训练目标可能降低 false positives。

## 成功标准
- 完成 POIL manifest 检查、小样本 localization-only baseline，并报告 positive mIoU、negative false-positive rate 与 F1。

## 失败/证伪标准
- 无法获取/构造 POIL 数据，或模型输出无法稳定解析为 bbox/rejection。

## 实验安排
（待补充）

## 变量与对照
（待补充）

## 最小测试
（待补充）

## Baseline
（待补充）

## 处理组与消融
（待补充）

## 指标与混淆变量
（待补充）

（待补充）

## 风险与开放问题
（待补充）

（待补充）

## 资源预算
（待补充）
