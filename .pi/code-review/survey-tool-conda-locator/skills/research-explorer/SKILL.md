---
name: research-explorer
description: 对 Experiment、Idea、Question 或 Comparison 做按时长或轮次限制的自由探索。触发包括“自由探索”“围绕某对象自动调研”“按时长探索”“按轮次探索”。
---

# Research Explorer（自由研究探索器）

用于在固定 deadline/轮次预算内积累候选证据、反证、不确定性与 proposal。每轮先运行 `surveyctl.py --project <绝对路径> exploration context <id>`，复用已有证据，再进行一个有界焦点。

## 与其他组件的边界

- `research-survey` 是正式的人机审核研究流程和唯一 Claim promotion/validated synthesis 管道；Explorer 的 final 只是 linked proposal/draft。
- Experiment Steward 只监控已批准远程实验、修复和归档；Explorer 不复用其 scheduler/queue，也不 SSH、运行 Run 或长实验。
- Experiment 代码修改必须走 `experiment_code_edit`；执行必须经过 Run 审核、授权和 Execution Outbox。Explorer 仅创建 `自由探索候审` draft Run。

## 每轮硬规则

1. 先读 context 和已有 rounds，禁止机械重复检索。
2. 每次外部检索追加 `shell/02_search/search_log.md`。API 失败/no hits 必须写 `degraded`，不得 silent zero。
3. 论文只有实际 fetch/ingest/hash 且读过相关段落后才是 `verified`；优先 MinerU Markdown。参数记忆只能是 `unverified_lead`。代码事实须给路径与可得 commit。
4. 主动找反证和混杂因素；清楚区分 fact / interpretation / hypothesis / proposal。
5. 用 `research_explorer_round complete` 提交 summary、非空 evidence（source/ref/finding/verification_status）、contradictions、uncertainties、next_focus；失败用规定 failure_class。不得把 agent_end 当完成。
6. 不修改 kernel Claim 状态、不 promote、不写 `shell/05_synthesis`、不改 Claim verdict；不改变 Idea/Question/Comparison 原文或状态。
7. 不运行 Run、shell 长实验或 SSH 实验，不修改实验代码，不猜命令/路径/结果。

## Finalize

最终报告必须列出覆盖范围、实际来源、degraded 来源、重复与未解问题、停止原因、下一步建议，并明确“不是 validated synthesis”。Idea/Question/Comparison 只生成短链接 stub。Experiment proposal 只能是 `{runs:[...]}`；Run 均为 `research_explorer` 创建的 draft、指标观测为空、人工逐条审核，绝不自动审核/授权/入 Outbox/执行。

Extension 的 scheduler 状态与 `.survey-tool/research-explorations.json` canonical registry 通过 `surveyctl exploration transition --expected-status` 做 CAS 同步；不得直接改任一 JSON。`stop` 只停止调度并保留成果，之后可进入 `finalizing`，不能 resume。Finalize 只接受 `finalizing`；同一 final/proposal hash 可幂等重试，不同内容必须重新由人明确处理，不能覆盖既有完成结果。
