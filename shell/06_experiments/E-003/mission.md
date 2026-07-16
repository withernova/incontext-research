# Experiment Mission · E-003

## 标题
IPLoc-ID identification F1 与 localization correctness 的联合评测审计

## 研究问题
Personal / IPLoc-ID 论文将 instance identification F1 与 bbox mIoU 分开计算。E-003 检验：高 identification F1 是否会高估端到端 personalized identification-and-localization 的联合成功率，以及最终 Yes/No 是否真正依赖所生成的候选框区域。

## 非预设性原则
“F1 虚高”只能作为待检验的通俗动机，不能作为预设结论。正式表述使用：

> identification-only F1 是否与 localization correctness 解耦，并因而高估 joint task success。

## 与 E-002 的边界
- E-002：hidden visual-token / containerization / identity-detail mechanism。
- E-003：evaluation metric coupling 与 candidate verifier auditing。
- E-003 不以 token intervention 作为主证据。

## 主实验
1. Joint F1@IoU={0.3,0.5,0.7}。
2. Forced-candidate verifier：固定不同候选框，测试 Yes/No 是否随候选区域变化。

## 结论边界
- Joint F1 下降可证明 identification-only F1 不等于 joint localization-identification success。
- 它不能单独证明背景、类别或整体外观捷径。
- Forced candidate 是 prefix-conditioned probe，需报告 exposure-shift 局限。
