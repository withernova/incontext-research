# E-011 · baseline-验证

- status: planned
- kind: standalone
- source_ref: 
- claim_refs: 
- priority: medium
- created: 2026-09-04T13:50:54
- updated: 2026-09-04T13:50:54

## 实验目标
在train数据集上对IPLoc的baseline进行评估的复现

## 假设
（待补充）

## 成功标准
- （待补充）

## 失败/证伪标准
- （待补充）

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

## 人类预授权的自动审核策略
```json
{
  "enabled": false,
  "auto_review_on_create": false,
  "auto_approve_threshold": 85,
  "auto_authorize_execution": false,
  "auto_authorize_threshold": 95,
  "policy_version": "run-review-score/v1",
  "notes": ""
}
```

> 默认关闭。策略只能由人类通过专用 Experiment UI/API 显式保存；自动审核不会执行命令，也不会修改 Claim verdict。

## 人类配置的 Execution Outbox 策略
```json
{
  "enabled": false,
  "auto_queue_on_authorize": false,
  "auto_deliver_on_pi_live": false,
  "claim_lease_minutes": 30,
  "max_delivery_attempts": 5,
  "notes": ""
}
```

> 自动排队不执行命令；自动派发仅向实时绑定的协调 pi 发送 Prompt，收到 Prompt 不代表 claim/ACK。

## 自由笔记（Obsidian）
这里可补充研究设计推演；工作台更新结构化方案时不会覆盖本节。
