# E-014 · 空间有序候选与 Reference 置信度

- status: planned
- kind: standalone
- source_ref: E-013
- claim_refs: 
- priority: medium
- created: 2026-10-11T14:05:35
- updated: 2026-10-11T15:27:09

## 实验目标
从原置信度 SFT step659 初始化，进行纯 GRPO。候选数量由模型自行决定，不固定三框或为了配额制造更多 GT 实例；按 Query bbox 中心横坐标从左到右输出，保留 Reference 同一实例置信度定义。使用同类别两实例的 Reference 切换与 AB/BA 位置交换训练，检验空间顺序、候选覆盖及按 score 选框是否改善。具体实现与训练预算记录在独立 Run；本实验不是仅修改 prompt 的单变量消融。

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
  "policy_version": "run-review-automation/v1",
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
