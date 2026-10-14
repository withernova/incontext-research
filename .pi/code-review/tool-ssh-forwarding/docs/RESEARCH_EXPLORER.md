# Research Explorer（自由研究探索器）

Research Explorer 对真实存在的 Experiment、Idea、Question 或 Comparison 做有 deadline/轮次上限的自由探索。它是 proposal 生成器，不是 `research-survey` 的 Claim 审核或 validated synthesis，也不是 Experiment Steward 的远程执行监控器。

## 使用

```bash
/explore start --project-root /absolute/project --target-type idea --target-id I-001 --duration-minutes 30 --max-rounds 5 --interval-minutes 1
/explore pause
/explore resume
/explore status
/explore stop
```

浏览器“自由探索”只生成并复制上述协调命令；不会声称已经启动 terminal pi。Extension 每轮先调用 `surveyctl exploration context`，用 followUp 注入任务，并等待 `research_explorer_round complete|fail`。deadline 在暂停期间继续流逝；重启 pi 后显式暂停，不自动恢复。

每次关键状态迁移先通过 `surveyctl exploration transition <id> --status ... --expected-status ...` 对 canonical registry 做原子 CAS，成功后才更新本地 scheduler。`stop` 保留成果并可继续 finalize，但不能恢复轮次；completed/completed_with_warnings 是终态。Finalize 对相同 final/proposal hash 幂等，不同 hash 明确拒绝；中途已经写出文件但 registry 未完成时可用完全相同输入安全恢复。

## 文件与状态

- canonical：`shell/07_explorations/<id>/session.md`、`rounds/round-N.md`、`final.md`、`proposal.json`
- public registry：`.survey-tool/research-explorations.json`，只存身份、预算、状态、路径和 hash
- scheduler：`.pi/research-explorer-state.json`、`.pi/research-explorer-events.jsonl`，不存 Prompt、消息或凭据

每轮 evidence 的 verification_status 仅允许 `verified|partial|unverified_lead|degraded`。检索必须写 `shell/02_search/search_log.md`；论文只有实际获取、摄取、哈希并读过相关段落后才可 verified。

Experiment finalize 只创建 `exploration-candidates` 中的 draft Runs，`created_by=research_explorer`，不触发自动审核、授权、Outbox 或执行。其他目标只得到链接 stub，不改原文/状态。最终报告必须写清覆盖范围、实际和 degraded 来源、重复/未解问题、停止原因与建议，并始终标明不是 validated synthesis。
