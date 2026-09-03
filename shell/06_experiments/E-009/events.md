
## 2026-08-25T13:46:07+08:00 · discovery
- run: -
- message: 已核验：登记工作区根目录不是 Git 仓库；实际可用代码位于 mechanism/IPLoc、mechanism/iplocid 与 mechanism/Rex-Omni 子目录。

只读检查：根目录一级结构与三个项目子目录；iplocid 当前存在未提交改动，后续实现不得覆盖。

## 2026-08-25T13:46:07+08:00 · discovery
- run: -
- message: 已核验：机器有 4 张 RTX 3090（每张 24 GiB），勘察时至少两张基本空闲；共享盘仅剩约 5.9 TiB 且使用率 98%，本地系统盘约剩 770 GiB。

nvidia-smi 与 df -h 的只读摘要；仅表示勘察时快照，不保证执行时资源仍可用。

## 2026-08-25T13:46:07+08:00 · discovery
- run: -
- message: 已核验：系统 Python 与现有 Miniconda Python 均缺 torch、transformers、peft、accelerate、datasets 等训练依赖，当前环境不能直接启动 SFT。

分别对 /usr/bin/python3 与 /root/miniconda3/bin/python 做 import-spec/import 检查；未读取环境变量。

## 2026-08-25T13:46:07+08:00 · discovery
- run: -
- message: 已核验：Qwen3-VL-8B-Instruct 本地基础模型索引包含 10 个权重分片且无缺片；IPLoc-ID 目录另有两个约 87 MB 的 Qwen3-VL LoRA adapter，可作为配置参考。

模型 config 标识 qwen3_vl、36 层、hidden size 4096；adapter 为 rank 8，排除视觉模块并作用于语言侧投影层。

## 2026-08-25T13:46:08+08:00 · discovery
- run: -
- message: 已核验：IPLoc 与 IPLoc-ID 均未提供可用训练代码；Rex-Omni 提供 SFT 入口，但当前实现固定 Qwen2.5-VL 类与配套训练栈，不能直接当作 Qwen3-VL SFT 入口。

读取三个仓库 README、Rex-Omni/finetuning/train.py 与 requirements.txt；IPLoc-ID README 明确训练代码尚未发布。

## 2026-08-25T13:46:56 · run_organization
- run: E009-R-001-qwen3vl8b-lora-sft-capability-smoke
- message: E009-R-001-qwen3vl8b-lora-sft-capability-smoke: microtask

```json
{
  "time": "2026-08-25T13:46:56",
  "policy_version": "run-organization/v1",
  "action": "microtask",
  "group_id": "",
  "reason": "ambiguous",
  "task_id": "classify-f3a5055da574672ea581"
}
```

## 2026-08-25T13:46:56+08:00 · run_created
- run: E009-R-001-qwen3vl8b-lora-sft-capability-smoke
- message: Agent 创建 canonical Run E009-R-001-qwen3vl8b-lora-sft-capability-smoke · Qwen3-VL-8B 基础 LoRA 微调能力烟雾实验

## 2026-08-25T14:08:27 · execution_dispatch_enqueue
- run: E009-R-001-qwen3vl8b-lora-sft-capability-smoke
- message: E009-R-001-qwen3vl8b-lora-sft-capability-smoke outbox=queued

```json
{
  "dispatch_id": "dispatch-af1194c524865c4b9bad8a4f",
  "experiment_id": "E-009",
  "run_id": "E009-R-001-qwen3vl8b-lora-sft-capability-smoke",
  "status": "queued",
  "created_at": "2026-08-25T14:08:27",
  "updated_at": "2026-08-25T14:08:27",
  "authorization_timestamp": "2026-08-25T14:08:27.684827",
  "requested_route": "experiment_code_edit",
  "requested_agent": "codex",
  "requested_model": "sol",
  "delivery_attempts": 0,
  "claim_attempts": 0,
  "last_error": "",
  "history": [
    {
      "time": "2026-08-25T14:08:27",
      "type": "queued",
      "detail": "direct_steward"
    }
  ]
}
```

## 2026-08-25T14:08:27 · run_direct_steward
- run: E009-R-001-qwen3vl8b-lora-sft-capability-smoke
- message: E009-R-001-qwen3vl8b-lora-sft-capability-smoke: current snapshot sent directly to Steward

```json
{
  "dispatch_id": "dispatch-af1194c524865c4b9bad8a4f",
  "actor": "human:web-v2"
}
```

## 2026-08-25T14:12:24 · run_runtime_command_prepared
- run: E009-R-001-qwen3vl8b-lora-sft-capability-smoke
- message: E009-R-001-qwen3vl8b-lora-sft-capability-smoke: Pi resolved launch placeholders

```json
{
  "dispatch_id": "dispatch-af1194c524865c4b9bad8a4f",
  "consumer": "pi-steward"
}
```

## 2026-08-27T19:56:11+08:00 · discovery
- run: -
- message: 代码实现路由 Codex/gpt-5.6-sol 因额度耗尽不可用，按既定 fallback 由当前 pi 完成最小 launcher/config 实现；未改变 Run 审核或执行授权。

requested_route=experiment_code_edit; requested_agent=codex; requested_model=gpt-5.6-sol; actual_agent=pi; actual_model=pi; fallback_reason=Codex usage limit exhausted before implementation

## 2026-08-28T00:38:29+08:00 · discovery
- run: -
- message: 代码实现路由 Codex 未在规定时间内响应，按 fallback 由当前 pi 完成四卡切分配置修改；不改变 Run 审核或执行授权。

requested_route=experiment_code_edit; requested_agent=codex; requested_model=gpt-5.6-sol; actual_agent=pi; actual_model=pi; fallback_reason=agent_prompt_stalled

## 2026-08-28T01:59:53+08:00 · discovery
- run: -
- message: Codex 实现代理因远端补丁工具不可用而未能完成修改，按既定 fallback 由当前 pi 实现视觉 patch-token 上限；保留用户授权的受限诊断范围。

requested_route=experiment_code_edit; requested_agent=codex; requested_model=gpt-5.6-sol; actual_agent=pi; actual_model=pi; fallback_reason=agent blocked after unavailable remote patch tooling

## 2026-08-28T16:25:39+08:00 · discovery
- run: -
- message: 项目本地源码编译 FlashAttention 已在 RTX3090 完成 bf16 forward/backward kernel 验证；xformers.ops 因其版本约束仅接受 flash-attn<=2.8.2，当前 2.8.3.post1 不兼容。

runtime-site=/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/build/flash-attn-2.8.3.post1/runtime-site; flash_attn=2.8.3.post1; kernel_shape=(2,128,8,128); finite_forward_backward=true; xformers=0.0.32.post2 rejects flash-attn 2.8.3.post1

## 2026-08-28T16:59:29+08:00 · discovery
- run: -
- message: 显式 device-map 实现委派被代理交互阻塞，按既定 fallback 由当前 pi 完成最小 cfg 修改并执行用户授权的 smoke。

requested_route=experiment_code_edit; requested_agent=codex; requested_model=gpt-5.6-sol; actual_agent=pi; actual_model=pi; fallback_reason=agent blocked before edit

## 2026-09-01T16:27:29 · run_organization
- run: E009-R-002-headscreen-step1400
- message: E009-R-002-headscreen-step1400: microtask

```json
{
  "time": "2026-09-01T16:27:29",
  "policy_version": "run-organization/v1",
  "action": "microtask",
  "group_id": "",
  "reason": "ambiguous",
  "task_id": "classify-d513212b574ef9f63608"
}
```

## 2026-09-01T16:27:29+08:00 · run_created
- run: E009-R-002-headscreen-step1400
- message: Agent 创建 canonical Run E009-R-002-headscreen-step1400 · 训练后段 checkpoint 1400 的固定样本 head screening

## 2026-09-01T16:27:30 · run_organization
- run: E009-R-003-headscreen-step1482
- message: E009-R-003-headscreen-step1482: microtask

```json
{
  "time": "2026-09-01T16:27:29",
  "policy_version": "run-organization/v1",
  "action": "microtask",
  "group_id": "",
  "reason": "ambiguous",
  "task_id": "classify-785da322857c8f378eba"
}
```

## 2026-09-01T16:27:30+08:00 · run_created
- run: E009-R-003-headscreen-step1482
- message: Agent 创建 canonical Run E009-R-003-headscreen-step1482 · 训练后段 checkpoint 1482 的固定样本 head screening

## 2026-09-01T16:27:30 · run_organization
- run: E009-R-004-headscreen-step1564
- message: E009-R-004-headscreen-step1564: microtask

```json
{
  "time": "2026-09-01T16:27:30",
  "policy_version": "run-organization/v1",
  "action": "microtask",
  "group_id": "",
  "reason": "ambiguous",
  "task_id": "classify-a5be731292b73931ee91"
}
```

## 2026-09-01T16:27:30+08:00 · run_created
- run: E009-R-004-headscreen-step1564
- message: Agent 创建 canonical Run E009-R-004-headscreen-step1564 · 训练后段 checkpoint 1564 的固定样本 head screening

## 2026-09-01T16:27:30 · run_organization
- run: E009-R-005-headscreen-step1646
- message: E009-R-005-headscreen-step1646: microtask

```json
{
  "time": "2026-09-01T16:27:30",
  "policy_version": "run-organization/v1",
  "action": "microtask",
  "group_id": "",
  "reason": "ambiguous",
  "task_id": "classify-f311608b8c89cdcaa0a2"
}
```

## 2026-09-01T16:27:30+08:00 · run_created
- run: E009-R-005-headscreen-step1646
- message: Agent 创建 canonical Run E009-R-005-headscreen-step1646 · 训练后段 checkpoint 1646 的固定样本 head screening

## 2026-09-01T16:27:30 · run_organization
- run: E009-R-006-headscreen-step1729
- message: E009-R-006-headscreen-step1729: microtask

```json
{
  "time": "2026-09-01T16:27:30",
  "policy_version": "run-organization/v1",
  "action": "microtask",
  "group_id": "",
  "reason": "ambiguous",
  "task_id": "classify-73a0e4572fb02a98f1df"
}
```

## 2026-09-01T16:27:30+08:00 · run_created
- run: E009-R-006-headscreen-step1729
- message: Agent 创建 canonical Run E009-R-006-headscreen-step1729 · 训练后段 checkpoint 1729 的固定样本 head screening

## 2026-09-01T16:27:56 · run_workflow
- run: E009-R-002-headscreen-step1400
- message: E009-R-002-headscreen-step1400: implementation-ready → ready_for_review

```json
{
  "version": 2,
  "stage": "ready_for_review",
  "legacy": false,
  "step": 2,
  "total": 6,
  "label": "代码方案待审核"
}
```

## 2026-09-01T16:28:07 · run_workflow
- run: E009-R-003-headscreen-step1482
- message: E009-R-003-headscreen-step1482: implementation-ready → ready_for_review

```json
{
  "version": 2,
  "stage": "ready_for_review",
  "legacy": false,
  "step": 2,
  "total": 6,
  "label": "代码方案待审核"
}
```

## 2026-09-01T16:28:07 · run_workflow
- run: E009-R-004-headscreen-step1564
- message: E009-R-004-headscreen-step1564: implementation-ready → ready_for_review

```json
{
  "version": 2,
  "stage": "ready_for_review",
  "legacy": false,
  "step": 2,
  "total": 6,
  "label": "代码方案待审核"
}
```

## 2026-09-01T16:28:07 · run_workflow
- run: E009-R-005-headscreen-step1646
- message: E009-R-005-headscreen-step1646: implementation-ready → ready_for_review

```json
{
  "version": 2,
  "stage": "ready_for_review",
  "legacy": false,
  "step": 2,
  "total": 6,
  "label": "代码方案待审核"
}
```

## 2026-09-01T16:28:08 · run_workflow
- run: E009-R-006-headscreen-step1729
- message: E009-R-006-headscreen-step1729: implementation-ready → ready_for_review

```json
{
  "version": 2,
  "stage": "ready_for_review",
  "legacy": false,
  "step": 2,
  "total": 6,
  "label": "代码方案待审核"
}
```

## 2026-09-01T16:28:15+08:00 · run_review_submitted
- run: E009-R-002-headscreen-step1400
- message: 固定 100 样本的后段 checkpoint head screening 已完成代码方案与聚焦测试；仅提交人工审核，不执行。

## 2026-09-01T16:28:15+08:00 · run_review_submitted
- run: E009-R-003-headscreen-step1482
- message: 固定 100 样本的后段 checkpoint head screening 已完成代码方案与聚焦测试；仅提交人工审核，不执行。

## 2026-09-01T16:28:16+08:00 · run_review_submitted
- run: E009-R-004-headscreen-step1564
- message: 固定 100 样本的后段 checkpoint head screening 已完成代码方案与聚焦测试；仅提交人工审核，不执行。

## 2026-09-01T16:28:16+08:00 · run_review_submitted
- run: E009-R-005-headscreen-step1646
- message: 固定 100 样本的后段 checkpoint head screening 已完成代码方案与聚焦测试；仅提交人工审核，不执行。

## 2026-09-01T16:28:16+08:00 · run_review_submitted
- run: E009-R-006-headscreen-step1729
- message: 固定 100 样本的后段 checkpoint head screening 已完成代码方案与聚焦测试；仅提交人工审核，不执行。

## 2026-09-01T16:38:47 · run_workflow
- run: E009-R-002-headscreen-step1400
- message: E009-R-002-headscreen-step1400: reopen-design → research_design

```json
{
  "version": 2,
  "stage": "research_design",
  "legacy": false,
  "step": 1,
  "total": 6,
  "label": "研究设计"
}
```

## 2026-09-01T16:38:47 · run_workflow
- run: E009-R-003-headscreen-step1482
- message: E009-R-003-headscreen-step1482: reopen-design → research_design

```json
{
  "version": 2,
  "stage": "research_design",
  "legacy": false,
  "step": 1,
  "total": 6,
  "label": "研究设计"
}
```

## 2026-09-01T16:38:47 · run_workflow
- run: E009-R-004-headscreen-step1564
- message: E009-R-004-headscreen-step1564: reopen-design → research_design

```json
{
  "version": 2,
  "stage": "research_design",
  "legacy": false,
  "step": 1,
  "total": 6,
  "label": "研究设计"
}
```

## 2026-09-01T16:38:47 · run_workflow
- run: E009-R-005-headscreen-step1646
- message: E009-R-005-headscreen-step1646: reopen-design → research_design

```json
{
  "version": 2,
  "stage": "research_design",
  "legacy": false,
  "step": 1,
  "total": 6,
  "label": "研究设计"
}
```

## 2026-09-01T16:38:48 · run_workflow
- run: E009-R-006-headscreen-step1729
- message: E009-R-006-headscreen-step1729: reopen-design → research_design

```json
{
  "version": 2,
  "stage": "research_design",
  "legacy": false,
  "step": 1,
  "total": 6,
  "label": "研究设计"
}
```

## 2026-09-01T16:38:57+08:00 · run_update
- run: E009-R-003-headscreen-step1482
- message: 已从审核队列撤回，改由单一 checkpoint suite 管理。

## 2026-09-01T16:38:57+08:00 · run_update
- run: E009-R-004-headscreen-step1564
- message: 已从审核队列撤回，改由单一 checkpoint suite 管理。

## 2026-09-01T16:38:57+08:00 · run_update
- run: E009-R-005-headscreen-step1646
- message: 已从审核队列撤回，改由单一 checkpoint suite 管理。

## 2026-09-01T16:38:58+08:00 · run_update
- run: E009-R-006-headscreen-step1729
- message: 已从审核队列撤回，改由单一 checkpoint suite 管理。

## 2026-09-01T16:39:02+08:00 · run_rekey
- run: E009-R-002-head-stability-last5
- message: Run registry 已从 E009-R-002-headscreen-step1400 迁移为 canonical ID E009-R-002-head-stability-last5

legacy_registry_id=E009-R-002-headscreen-step1400

## 2026-09-01T16:50:43+08:00 · run_update
- run: E009-R-002-head-stability-last5
- message: 旧单-checkpoint 草案已取消，将新建唯一 suite Run。

## 2026-09-01T16:52:19 · run_organization
- run: E009-R-007-head-stability-last5
- message: E009-R-007-head-stability-last5: microtask

```json
{
  "time": "2026-09-01T16:52:18",
  "policy_version": "run-organization/v1",
  "action": "microtask",
  "group_id": "",
  "reason": "ambiguous",
  "task_id": "classify-a1f743573e6fa3caffed"
}
```

## 2026-09-01T16:52:19+08:00 · run_created
- run: E009-R-007-head-stability-last5
- message: Agent 创建 canonical Run E009-R-007-head-stability-last5 · 训练后段最后五个 checkpoint 的单 Run head 稳定性核验

## 2026-09-01T16:52:27 · run_workflow
- run: E009-R-007-head-stability-last5
- message: E009-R-007-head-stability-last5: implementation-ready → ready_for_review

```json
{
  "version": 2,
  "stage": "ready_for_review",
  "legacy": false,
  "step": 2,
  "total": 6,
  "label": "代码方案待审核"
}
```

## 2026-09-01T16:52:27+08:00 · run_review_submitted
- run: E009-R-007-head-stability-last5
- message: 已合并为单一 last5 checkpoint suite；五次 heads 与最终稳定性均记录在同一总日志和产物根，聚焦测试 17 passed。

## 2026-09-01T17:07:08 · run_workflow
- run: E009-R-007-head-stability-last5
- message: E009-R-007-head-stability-last5: reopen-design → research_design

```json
{
  "version": 2,
  "stage": "research_design",
  "legacy": false,
  "step": 1,
  "total": 6,
  "label": "研究设计"
}
```

## 2026-09-01T17:07:42+08:00 · run_update
- run: E009-R-007-head-stability-last5
- message: 已按用户决定改为保序 valid96，补充可追溯 audit、独立 attempt-002 和 n=96 完整性门禁。

## 2026-09-01T17:07:50 · run_workflow
- run: E009-R-007-head-stability-last5
- message: E009-R-007-head-stability-last5: confirm-design → code_planning

```json
{
  "version": 2,
  "stage": "code_planning",
  "legacy": false,
  "step": 2,
  "total": 6,
  "label": "代码方案"
}
```

## 2026-09-01T17:07:50 · run_workflow
- run: E009-R-007-head-stability-last5
- message: E009-R-007-head-stability-last5: implementation-ready → ready_for_review

```json
{
  "version": 2,
  "stage": "ready_for_review",
  "legacy": false,
  "step": 2,
  "total": 6,
  "label": "代码方案待审核"
}
```

## 2026-09-01T17:07:50+08:00 · run_review_submitted
- run: E009-R-007-head-stability-last5
- message: 已按用户确认改为原 val100 剩余 valid96；四条无效框有独立 audit，attempt-001 不入分析，attempt-002 待重新审核授权。

## 2026-09-01T19:03:19+08:00 · run_update
- run: E009-R-007-head-stability-last5
- message: 登记 attempt-002-valid96 的 head 稳定性结果及用户确认的后续 Query Top-5 / Reference Top-3 选择；未改变审核、授权或 Claim 状态。

## 2026-09-01T19:03:19+08:00 · head_selection_recorded
- run: E009-R-007-head-stability-last5
- message: 用户确认后续采用 Query Top-5 与 Reference Top-3 head 集合。

{"evidence_attempt":"attempt-002-valid96","query_top5":["L21H10","L17H04","L17H07","L24H16","L18H15"],"reference_top3":["L20H15","L20H20","L14H23"],"query_top5_occurrence":{"L21H10":"5/5","L17H04":"5/5","L17H07":"4/5","L24H16":"4/5","L18H15":"3/5"},"reference_top5_occurrence":{"L20H15":"5/5","L20H20":"4/5","L14H23":"4/5"},"decision_scope":"downstream head selection; descriptive valid96 evidence only"}

## 2026-09-01T20:10:13 · run_organization
- run: E009-R-008-reference-top3-query-top5-ensemble-distill
- message: E009-R-008-reference-top3-query-top5-ensemble-distill: microtask

```json
{
  "time": "2026-09-01T20:10:13",
  "policy_version": "run-organization/v1",
  "action": "microtask",
  "group_id": "",
  "reason": "ambiguous",
  "task_id": "classify-516d8a04010e4a49ea42"
}
```

## 2026-09-01T20:10:13+08:00 · run_created
- run: E009-R-008-reference-top3-query-top5-ensemble-distill
- message: Agent 创建 canonical Run E009-R-008-reference-top3-query-top5-ensemble-distill · Reference Top-3 教师到 Query Top-5 集合的跨图注意力蒸馏

## 2026-09-03T01:17:11 · run_organization
- run: E009-R-009-dynamic-reference-top3-query-top5-online-distill
- message: E009-R-009-dynamic-reference-top3-query-top5-online-distill: microtask

```json
{
  "time": "2026-09-03T01:17:11",
  "policy_version": "run-organization/v1",
  "action": "microtask",
  "group_id": "",
  "reason": "ambiguous",
  "task_id": "classify-955d70c9e3107e6883b9"
}
```

## 2026-09-03T01:17:11+08:00 · run_created
- run: E009-R-009-dynamic-reference-top3-query-top5-online-distill
- message: Agent 创建 canonical Run E009-R-009-dynamic-reference-top3-query-top5-online-distill · 动态 Reference Top-3 到 Query Top-5 在线蒸馏（探索性扩展）

## 2026-09-03T01:17:11+08:00 · run_update
- run: E009-R-009-dynamic-reference-top3-query-top5-online-distill
- message: 已汇总dynamic teacher训练、held-out评估、head漂移、valid96全-head诊断与错误案例可视化；独立于R008固定四臂登记。

## 2026-09-03T01:17:12+08:00 · discovery
- run: E009-R-009-dynamic-reference-top3-query-top5-online-distill
- message: Dynamic在线蒸馏显著降低Teacher→Student KL但未改善combined held-out自然定位，并出现Reference head排序漂移。

combined mIoU 0.689856，较step1729 -0.003611、较continued-SFT -0.004508；valid96 KL 0.7776→0.1713、student S50 0.1479→0.2956，但attention指标与IoU delta无显著Spearman相关。该探索性Run不替代R008离线fixed-correct。审计：dynamic branch diagnostics/valid96_attention/{summary.json,per_sample.csv,per_head_summary.csv,*_per_head.png}。

## 2026-09-03T01:17:42+08:00 · run_update
- run: E009-R-009-dynamic-reference-top3-query-top5-online-distill
- message: 复核并再次保存结果摘要与分析字段。
