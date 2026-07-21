# Experiment Mission · E-003

## 标题
IPLoc-ID identification F1 与 localization correctness 的联合评测审计

## 研究问题
Personal / IPLoc-ID 论文将 instance identification F1 与 bbox mIoU 分开计算。E-003 检验：高 identification F1 是否会高估端到端 personalized identification-and-localization 的联合成功率，以及最终 Yes/No 是否真正依赖所生成的候选框区域。

论文将理想 POIL 输出定义为 positive 时返回正确目标框、negative 时拒绝，并将 bbox 描述为后续 identification component 要验证的 candidate；但已读取正文的评测口径分别报告 mIoU 与 identification F1，未报告要求二者在同一 positive sample 上同时成立的 joint metric。[[personal2026]] §3.1.1 Personalized object identification and localization；[[personal2026]] §3.1.2 Evaluation metric for POIL；[[personal2026]] §3.3.1 Sequential generation of localization and identification；[[personal2026]] §4.1.2 Evaluation procedure

详细成立依据与论文级结论边界见：`evaluation_audit_rationale.md`。

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
- 当前只能称为：论文评测的 **joint-metric coverage gap**；不是 F1 算错、不是论文未评测 localization、更不是研究不端。
- 本地 manifest 是 deterministic reconstruction，不能把当前幅度直接外推官方 split/Table 8。
- 它不能单独证明背景、类别或整体外观捷径。
- Forced candidate 是 prefix-conditioned probe，需报告 exposure-shift 局限。

## 强制登记入口
任何 E-003 run 创建、更新或总结前，必须读取：

```text
shell/06_experiments/E-003/ledger_filling_skill.md
shell/06_experiments/E-003/experiment_audit_notes.md
shell/06_experiments/E-003/evaluation_audit_rationale.md
```
