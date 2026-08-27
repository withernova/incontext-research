
## 2026-08-26T14:30:59 · run_organization
- run: E010-R-001-fixed-head-stability-and-heldout-localization
- message: E010-R-001-fixed-head-stability-and-heldout-localization: microtask

```json
{
  "time": "2026-08-26T14:30:59",
  "policy_version": "run-organization/v1",
  "action": "microtask",
  "group_id": "",
  "reason": "ambiguous",
  "task_id": "classify-7355586398ece591a522"
}
```

## 2026-08-26T14:30:59+08:00 · run_created
- run: E010-R-001-fixed-head-stability-and-heldout-localization
- message: Agent 创建 canonical Run E010-R-001-fixed-head-stability-and-heldout-localization · IPLoc-ID固定注意力头稳定性与新样本定位检查

## 2026-08-26T14:32:02 · run_organization
- run: E010-R-002-identity-spatial-controls-and-head-necessity
- message: E010-R-002-identity-spatial-controls-and-head-necessity: microtask

```json
{
  "time": "2026-08-26T14:32:02",
  "policy_version": "run-organization/v1",
  "action": "microtask",
  "group_id": "",
  "reason": "ambiguous",
  "task_id": "classify-55839438566f7520c064"
}
```

## 2026-08-26T14:32:02+08:00 · run_created
- run: E010-R-002-identity-spatial-controls-and-head-necessity
- message: Agent 创建 canonical Run E010-R-002-identity-spatial-controls-and-head-necessity · IPLoc-ID身份与位置排除检查及注意力头必要性验证

## 2026-08-26T14:38:03+08:00 · discovery
- run: -
- message: 已核验IPLoc-ID主代码仓库与注意力公共模块。

仓库=/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iplocid；commit=9a53a24d4e345b4c75a8dee4f6769f93c3720377；现有公共模块包括iplocid/attention/{collector,spans,metrics,rewrite}.py、iplocid/inference/{generation,replay}.py、iplocid/pipelines/role_audit_pipeline.py；已有对应单元测试。

## 2026-08-26T14:38:03+08:00 · discovery
- run: -
- message: 已核验远端执行环境与数据边界，但发现当前仓库写入授权冲突。

工作区绑定主机可访问4张RTX3090；IPLoc环境位于/root/miniconda3，但非交互SSH未自动加入PATH。项目根AGENTS.md当前只授权E-008离线重渲染并明确禁止修改代码、模型推理和实验执行，因此本轮不能安全实施E-010代码，需先由人类更新该项目级指令。

## 2026-08-26T14:38:54+08:00 · run_update
- run: E010-R-001-fixed-head-stability-and-heldout-localization
- message: 已完成远端只读代码勘察并登记最小实现方案；受项目级AGENTS.md冲突阻塞，暂不实施或提交审核。

## 2026-08-26T14:38:54+08:00 · run_update
- run: E010-R-002-identity-spatial-controls-and-head-necessity
- message: 已完成远端只读代码勘察并登记Run 2最小实现方案；受项目级AGENTS.md冲突阻塞，暂不实施或提交审核。

## 2026-08-26T14:59:58+08:00 · discovery
- run: -
- message: experiment_code_edit请求路由Codex/sol不可用，按配置回退到pi。

requested_route=experiment_code_edit；requested_agent=codex；requested_model=sol；actual_agent=pi；fallback_reason=Codex返回sol model is not supported when using Codex with a ChatGPT account；未静默改用其他Codex模型。

## 2026-08-26T15:04:07+08:00 · run_update
- run: E010-R-001-fixed-head-stability-and-heldout-localization
- message: Run 1最小公共实现完成；聚焦测试18项通过，未运行模型。

## 2026-08-26T15:04:07+08:00 · run_update
- run: E010-R-002-identity-spatial-controls-and-head-necessity
- message: Run 2离线控制contract和最小启动入口完成；复用现有mass_zero，聚焦测试通过，未运行模型。

## 2026-08-26T15:04:14 · run_workflow
- run: E010-R-002-identity-spatial-controls-and-head-necessity
- message: E010-R-002-identity-spatial-controls-and-head-necessity: implementation-ready → ready_for_review

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

## 2026-08-26T15:04:14 · run_workflow
- run: E010-R-001-fixed-head-stability-and-heldout-localization
- message: E010-R-001-fixed-head-stability-and-heldout-localization: implementation-ready → ready_for_review

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

## 2026-08-26T15:04:27+08:00 · run_review_submitted
- run: E010-R-001-fixed-head-stability-and-heldout-localization
- message: Run 1研究设计和最小公共实现已完成；18项不加载模型的聚焦测试通过，配置保留必填占位符并会硬失败，未运行正式实验。请审核。

## 2026-08-26T15:04:27+08:00 · run_review_submitted
- run: E010-R-002-identity-spatial-controls-and-head-necessity
- message: Run 2研究设计和离线控制contract已完成；固定读取Run 1名单和哈希，复用现有带审计mass_zero，聚焦测试通过，未运行正式实验。请审核。

## 2026-08-26T15:14:49 · execution_dispatch_enqueue
- run: E010-R-001-fixed-head-stability-and-heldout-localization
- message: E010-R-001-fixed-head-stability-and-heldout-localization outbox=queued

```json
{
  "dispatch_id": "dispatch-410f5211cf4748d45bcdf89f",
  "experiment_id": "E-010",
  "run_id": "E010-R-001-fixed-head-stability-and-heldout-localization",
  "status": "queued",
  "created_at": "2026-08-26T15:14:49",
  "updated_at": "2026-08-26T15:14:49",
  "authorization_timestamp": "2026-08-26T15:14:49.358632",
  "requested_route": "experiment_code_edit",
  "requested_agent": "codex",
  "requested_model": "sol",
  "delivery_attempts": 0,
  "claim_attempts": 0,
  "last_error": "",
  "history": [
    {
      "time": "2026-08-26T15:14:49",
      "type": "queued",
      "detail": "direct_steward"
    }
  ]
}
```

## 2026-08-26T15:14:49 · run_direct_steward
- run: E010-R-001-fixed-head-stability-and-heldout-localization
- message: E010-R-001-fixed-head-stability-and-heldout-localization: current snapshot sent directly to Steward

```json
{
  "dispatch_id": "dispatch-410f5211cf4748d45bcdf89f",
  "actor": "human:web-v2"
}
```

## 2026-08-26T16:54:36 · run_organization
- run: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability
- message: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability: microtask

```json
{
  "time": "2026-08-26T16:54:36",
  "policy_version": "run-organization/v1",
  "action": "microtask",
  "group_id": "",
  "reason": "ambiguous",
  "task_id": "classify-26074d8cee318f9db26b"
}
```

## 2026-08-26T16:54:36+08:00 · run_created
- run: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability
- message: Agent 创建 canonical Run E010-R-003-natural-query-bbox-dual-span-head-discovery-stability · 自然Query-bbox双图Query/Reference head无GT发现与稳定性复核

## 2026-08-26T16:54:36 · run_organization
- run: E010-R-004-frozen-query-head-reference-span-bias-audit
- message: E010-R-004-frozen-query-head-reference-span-bias-audit: microtask

```json
{
  "time": "2026-08-26T16:54:36",
  "policy_version": "run-organization/v1",
  "action": "microtask",
  "group_id": "",
  "reason": "ambiguous",
  "task_id": "classify-51f6757698d6446422d4"
}
```

## 2026-08-26T16:54:36+08:00 · run_created
- run: E010-R-004-frozen-query-head-reference-span-bias-audit
- message: Agent 创建 canonical Run E010-R-004-frozen-query-head-reference-span-bias-audit · 冻结Query heads投向Reference图像的空间偏差与坐标复制审计

## 2026-08-26T17:20:43 · execution_dispatch_enqueue
- run: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability
- message: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability outbox=queued

```json
{
  "dispatch_id": "dispatch-d6f9d678acd005321b1297fc",
  "experiment_id": "E-010",
  "run_id": "E010-R-003-natural-query-bbox-dual-span-head-discovery-stability",
  "status": "queued",
  "created_at": "2026-08-26T17:20:43",
  "updated_at": "2026-08-26T17:20:43",
  "authorization_timestamp": "2026-08-26T17:20:43.205473",
  "requested_route": "experiment_code_edit",
  "requested_agent": "codex",
  "requested_model": "gpt-5.6-sol",
  "delivery_attempts": 0,
  "claim_attempts": 0,
  "last_error": "",
  "history": [
    {
      "time": "2026-08-26T17:20:43",
      "type": "queued",
      "detail": "direct_steward"
    }
  ]
}
```

## 2026-08-26T17:20:43 · run_direct_steward
- run: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability
- message: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability: current snapshot sent directly to Steward

```json
{
  "dispatch_id": "dispatch-d6f9d678acd005321b1297fc",
  "actor": "human:web-v2"
}
```

## 2026-08-26T17:27:56 · run_runtime_command_prepared
- run: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability
- message: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability: Pi resolved launch placeholders

```json
{
  "dispatch_id": "dispatch-d6f9d678acd005321b1297fc",
  "consumer": "pi-steward"
}
```

## 2026-08-27T10:57:16 · execution_dispatch_enqueue
- run: E010-R-004-frozen-query-head-reference-span-bias-audit
- message: E010-R-004-frozen-query-head-reference-span-bias-audit outbox=queued

```json
{
  "dispatch_id": "dispatch-e57fc834344208913e9dbba8",
  "experiment_id": "E-010",
  "run_id": "E010-R-004-frozen-query-head-reference-span-bias-audit",
  "status": "queued",
  "created_at": "2026-08-27T10:57:16",
  "updated_at": "2026-08-27T10:57:16",
  "authorization_timestamp": "2026-08-27T10:57:16.946435",
  "requested_route": "experiment_code_edit",
  "requested_agent": "codex",
  "requested_model": "gpt-5.6-sol",
  "delivery_attempts": 0,
  "claim_attempts": 0,
  "last_error": "",
  "history": [
    {
      "time": "2026-08-27T10:57:16",
      "type": "queued",
      "detail": "direct_steward"
    }
  ]
}
```

## 2026-08-27T10:57:16 · run_direct_steward
- run: E010-R-004-frozen-query-head-reference-span-bias-audit
- message: E010-R-004-frozen-query-head-reference-span-bias-audit: current snapshot sent directly to Steward

```json
{
  "dispatch_id": "dispatch-e57fc834344208913e9dbba8",
  "actor": "human:web-v2"
}
```

## 2026-08-27T11:03:12 · run_runtime_command_prepared
- run: E010-R-004-frozen-query-head-reference-span-bias-audit
- message: E010-R-004-frozen-query-head-reference-span-bias-audit: Pi resolved launch placeholders

```json
{
  "dispatch_id": "dispatch-e57fc834344208913e9dbba8",
  "consumer": "pi-steward"
}
```

## 2026-08-27T11:53:39+08:00 · question_registered
- run: -
- message: 登记 Q-006：已有 Reference bbox 先验时，为何自然 Query-bbox 生成仍难由固定 heads 定位 Reference；GT 辅助的 head 发现能揭示什么？

{"question_id":"Q-006","path":"shell/01_questions/Q-006.md","status":"investigating","evidence_boundary":"R-003 artifact observation plus R-001 per-image GT oracle; not validated","next_tests":["per-image no-GT selection vs GT oracle","discovery-GT supervised fixed-head held-out evaluation","no-GT selector calibration"]}

## 2026-08-27T11:57:35+08:00 · question_registration_restart_verified
- run: -
- message: Q-006 登记重启核验：问题文件、Questions 索引和原 question_registered 事件均已持久化；不重复创建问题，登记状态恢复为已完成。

{"question_id":"Q-006","question_path":"shell/01_questions/Q-006.md","index_path":"index/Questions.md","original_event_timestamp":"2026-08-27T11:53:39+08:00","idempotent_action":"verified-existing-registration","status":"investigating"}

## 2026-08-27T13:04:55 · run_organization
- run: E010-R-005-per-image-nogt-selection-vs-gt-oracle-reference-head-audit
- message: E010-R-005-per-image-nogt-selection-vs-gt-oracle-reference-head-audit: microtask

```json
{
  "time": "2026-08-27T13:04:55",
  "policy_version": "run-organization/v1",
  "action": "microtask",
  "group_id": "",
  "reason": "ambiguous",
  "task_id": "classify-68c41923cd2778622ae7"
}
```

## 2026-08-27T13:04:55+08:00 · run_created
- run: E010-R-005-per-image-nogt-selection-vs-gt-oracle-reference-head-audit
- message: Agent 创建 canonical Run E010-R-005-per-image-nogt-selection-vs-gt-oracle-reference-head-audit · 自然Qbbox→Reference逐图无GT选头与GT-oracle误差分解

## 2026-08-27T13:15:24 · execution_dispatch_enqueue
- run: E010-R-005-per-image-nogt-selection-vs-gt-oracle-reference-head-audit
- message: E010-R-005-per-image-nogt-selection-vs-gt-oracle-reference-head-audit outbox=queued

```json
{
  "dispatch_id": "dispatch-c731f87351460754fe654f0c",
  "experiment_id": "E-010",
  "run_id": "E010-R-005-per-image-nogt-selection-vs-gt-oracle-reference-head-audit",
  "status": "queued",
  "created_at": "2026-08-27T13:15:24",
  "updated_at": "2026-08-27T13:15:24",
  "authorization_timestamp": "2026-08-27T13:15:24.378316",
  "requested_route": "experiment_code_edit",
  "requested_agent": "codex",
  "requested_model": "gpt-5.6-sol",
  "delivery_attempts": 0,
  "claim_attempts": 0,
  "last_error": "",
  "history": [
    {
      "time": "2026-08-27T13:15:24",
      "type": "queued",
      "detail": "direct_steward"
    }
  ]
}
```

## 2026-08-27T13:15:24 · run_direct_steward
- run: E010-R-005-per-image-nogt-selection-vs-gt-oracle-reference-head-audit
- message: E010-R-005-per-image-nogt-selection-vs-gt-oracle-reference-head-audit: current snapshot sent directly to Steward

```json
{
  "dispatch_id": "dispatch-c731f87351460754fe654f0c",
  "actor": "human:web-v2"
}
```

## 2026-08-27T13:19:21 · run_runtime_command_prepared
- run: E010-R-005-per-image-nogt-selection-vs-gt-oracle-reference-head-audit
- message: E010-R-005-per-image-nogt-selection-vs-gt-oracle-reference-head-audit: Pi resolved launch placeholders

```json
{
  "dispatch_id": "dispatch-c731f87351460754fe654f0c",
  "consumer": "pi-steward"
}
```

## 2026-08-27T14:52:35 · execution_dispatch_enqueue
- run: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability
- message: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability outbox=queued

```json
{
  "dispatch_id": "dispatch-8a1e22d58277d27e55850467",
  "experiment_id": "E-010",
  "run_id": "E010-R-003-natural-query-bbox-dual-span-head-discovery-stability",
  "status": "queued",
  "created_at": "2026-08-27T14:52:35",
  "updated_at": "2026-08-27T14:52:35",
  "authorization_timestamp": "2026-08-27T14:52:35.680046",
  "requested_route": "experiment_code_edit",
  "requested_agent": "codex",
  "requested_model": "gpt-5.6-sol",
  "delivery_attempts": 0,
  "claim_attempts": 0,
  "last_error": "",
  "history": [
    {
      "time": "2026-08-27T14:52:35",
      "type": "queued",
      "detail": "restart_failed_execution"
    }
  ]
}
```

## 2026-08-27T14:52:35 · run_execution_restarted
- run: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability
- message: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability: failed attempt preserved; new authorization created

```json
{
  "prior_dispatch_id": "dispatch-d6f9d678acd005321b1297fc",
  "new_dispatch_id": "dispatch-8a1e22d58277d27e55850467",
  "actor": "human:web-v2"
}
```

## 2026-08-27T14:53:14 · execution_dispatch_enqueue
- run: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability
- message: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability outbox=queued

```json
{
  "dispatch_id": "dispatch-87b78d3ac4b3a44110b5e92d",
  "experiment_id": "E-010",
  "run_id": "E010-R-003-natural-query-bbox-dual-span-head-discovery-stability",
  "status": "queued",
  "created_at": "2026-08-27T14:53:14",
  "updated_at": "2026-08-27T14:53:14",
  "authorization_timestamp": "2026-08-27T14:53:14.275989",
  "requested_route": "experiment_code_edit",
  "requested_agent": "codex",
  "requested_model": "gpt-5.6-sol",
  "delivery_attempts": 0,
  "claim_attempts": 0,
  "last_error": "",
  "history": [
    {
      "time": "2026-08-27T14:53:14",
      "type": "queued",
      "detail": "direct_steward"
    }
  ]
}
```

## 2026-08-27T14:53:14 · run_direct_steward
- run: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability
- message: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability: current snapshot sent directly to Steward

```json
{
  "dispatch_id": "dispatch-87b78d3ac4b3a44110b5e92d",
  "actor": "human:web-v2"
}
```

## 2026-08-27T14:53:29 · execution_dispatch_enqueue
- run: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability
- message: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability outbox=queued

```json
{
  "dispatch_id": "dispatch-5fb6dbf618ffe284e2331997",
  "experiment_id": "E-010",
  "run_id": "E010-R-003-natural-query-bbox-dual-span-head-discovery-stability",
  "status": "queued",
  "created_at": "2026-08-27T14:53:29",
  "updated_at": "2026-08-27T14:53:29",
  "authorization_timestamp": "2026-08-27T14:53:29.245080",
  "requested_route": "experiment_code_edit",
  "requested_agent": "codex",
  "requested_model": "gpt-5.6-sol",
  "delivery_attempts": 0,
  "claim_attempts": 0,
  "last_error": "",
  "history": [
    {
      "time": "2026-08-27T14:53:29",
      "type": "queued",
      "detail": "direct_steward"
    }
  ]
}
```

## 2026-08-27T14:53:29 · run_direct_steward
- run: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability
- message: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability: current snapshot sent directly to Steward

```json
{
  "dispatch_id": "dispatch-5fb6dbf618ffe284e2331997",
  "actor": "human:web-v2"
}
```

## 2026-08-27T14:56:45 · run_runtime_command_prepared
- run: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability
- message: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability: Pi resolved launch placeholders

```json
{
  "dispatch_id": "dispatch-5fb6dbf618ffe284e2331997",
  "consumer": "pi-steward"
}
```

## 2026-08-27T14:57:08 · run_runtime_command_prepared
- run: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability
- message: E010-R-003-natural-query-bbox-dual-span-head-discovery-stability: Pi resolved launch placeholders

```json
{
  "dispatch_id": "dispatch-5fb6dbf618ffe284e2331997",
  "consumer": "pi-steward"
}
```

## 2026-08-27T14:59:52 · run_organization
- run: E010-R-006-gt-supervised-reference-head-stability-heldout-audit
- message: E010-R-006-gt-supervised-reference-head-stability-heldout-audit: microtask

```json
{
  "time": "2026-08-27T14:59:52",
  "policy_version": "run-organization/v1",
  "action": "microtask",
  "group_id": "",
  "reason": "ambiguous",
  "task_id": "classify-679b38ef33794d25e56b"
}
```

## 2026-08-27T14:59:52+08:00 · run_created
- run: E010-R-006-gt-supervised-reference-head-stability-heldout-audit
- message: Agent 创建 canonical Run E010-R-006-gt-supervised-reference-head-stability-heldout-audit · GT监督Reference head跨图稳定性与冻结held-out审计

## 2026-08-27T15:01:29 · execution_dispatch_enqueue
- run: E010-R-006-gt-supervised-reference-head-stability-heldout-audit
- message: E010-R-006-gt-supervised-reference-head-stability-heldout-audit outbox=queued

```json
{
  "dispatch_id": "dispatch-18ea3d9fba8632a4bc61dc54",
  "experiment_id": "E-010",
  "run_id": "E010-R-006-gt-supervised-reference-head-stability-heldout-audit",
  "status": "queued",
  "created_at": "2026-08-27T15:01:29",
  "updated_at": "2026-08-27T15:01:29",
  "authorization_timestamp": "2026-08-27T15:01:29.891656",
  "requested_route": "experiment_code_edit",
  "requested_agent": "codex",
  "requested_model": "gpt-5.6-sol",
  "delivery_attempts": 0,
  "claim_attempts": 0,
  "last_error": "",
  "history": [
    {
      "time": "2026-08-27T15:01:29",
      "type": "queued",
      "detail": "direct_steward"
    }
  ]
}
```

## 2026-08-27T15:01:29 · run_direct_steward
- run: E010-R-006-gt-supervised-reference-head-stability-heldout-audit
- message: E010-R-006-gt-supervised-reference-head-stability-heldout-audit: current snapshot sent directly to Steward

```json
{
  "dispatch_id": "dispatch-18ea3d9fba8632a4bc61dc54",
  "actor": "human:web-v2"
}
```

## 2026-08-27T15:04:17 · run_runtime_command_prepared
- run: E010-R-006-gt-supervised-reference-head-stability-heldout-audit
- message: E010-R-006-gt-supervised-reference-head-stability-heldout-audit: Pi resolved launch placeholders

```json
{
  "dispatch_id": "dispatch-18ea3d9fba8632a4bc61dc54",
  "consumer": "pi-steward"
}
```

## 2026-08-27T15:17:01+08:00 · run_update
- run: E010-R-006-gt-supervised-reference-head-stability-heldout-audit
- message: 补充完成R-006原图attention overlays与算法/实现/指标/完整性登记；为只读后处理，未改指标、冻结head或R-006完成状态。
