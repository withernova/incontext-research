# e015-iploc144-qwen2-4shot-restart-20261023 · IPLoc官方144修正划分后Qwen2四参考帧重新训练

- canonical_run_id: `e015-iploc144-qwen2-4shot-restart-20261023`
- group_id: （未分组 / 待整理）
- run_type: （待分类）
- review_status: draft
- review_round: 0
- submitted_for_review_at: 
- approved_at: 
- approved_by: 
- execution_authorized_at: 
- execution_authorized_by: 
- execution_authorization_consumed_at: 
- execution_dispatch_id: 
- execution_dispatch_latest_status: 
- legacy_registry_ids: （无）

> 已分组 Run 位于 `runs/<group-id>/<run-id>.md`；未分组 Run 位于 `runs/<run-id>.md`。
> Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
draft

## 本轮目的
修正数据泄漏与近邻参考帧采样后重新启动自有SFT→GRPO多框score→VQA，使用作者发布144条评测。

## 必要性 / 证据链位置
旧E015训练与官方测试有68相同Query，旧adapter不复用；用户明确授权修正并重启。

## 研究依据 / 被审计对象
（待补充）

## 实现方式（简版）
（待补充）

## 实现方式（详细版）
修正后独立重启：官方IPLoc commit27682bc2的LaSOT144条1/2/4shot逐条保留；训练LaSOT排除官方全部36类别，剩余真实原始类别补集（非声称FOCUS35/35）；GOT/TAO仅原train来源并保留旧holdout源视频保护。训练参考索引i*(N//4)，Query=N-1，TAO按标注目标时间线，异常样本剔除不挪动帧。GRPO双方身份按测试类别及源视频排除，整正负对及ABBA关联组过滤。旧E015有68个测试Query污染，SFT和selector均从官方Qwen2基础权重fresh LoRA启动，不复用旧adapter。复用已发布28c72aff代码、双卡×4副本及图像缓存。原SFT4epoch/global64/lr2e-4和GRPO400步奖励/score/prompt不变；GRPO后先官方144各shot评测并保存proposal，再独立VQA训练评测。新iploc144指标命名空间，无旧1728基线。任何数据审计或训练错误停止；输入脚本和来源SHA完整记录。此为自有方法在作者公开评测清单上的训练适配，不是FOCUS完整复现。 此登记缺少workflow_version，启动前被工具拒绝，未执行数据或GPU任务；仅有上传inputs。被独立restart-r2 Run替代，不再执行。

## 数据身份与构造
（待补充）

## 数据规模
（待补充）

## 模型、权重与关键配置
（待补充）

## 变量、干预与对照
（待补充）

## 指标与计数规则
（待补充）

## 完整性门槛 / no-silent-zero
（待补充）

## 竞争假设与预期特征
（待补充）

## 验收条件
（待补充）

## 依赖的 Run / 证据
（待补充）

## 观测结果摘要
（待补充）

## 局限与混杂因素
（待补充）

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
（待补充）

## Artifacts
（待补充）

## 审核入口
（待补充）

## 过程记录与补充细节
（待补充）

## 指标观测
（尚无结构化观测）

## 辅助指标（尚未注册）
（无）

> 辅助指标来自成功运行的 metrics.json，但尚未在 Experiment 注册；可用于诊断和后续判断，不自动成为主指标或 Claim 证据。

## Run 审核
### 用户补充要求
（待补充）
### 用户疑问
（待补充）
### Agent 完善说明
（待补充）
### Agent 对疑问的回应
（待补充）
### 本次执行授权备注
（待补充）
### 自动审核快照
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
03

### Git commit / branch
28c72afff503650316e37039c5931f2587b62b45

### 运行命令
（待补充）

### 配置/超参数
configs/experiments/E-015/{sft,grpo,selector,evaluate}.py

### Seed
11451

### 日志路径
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-20261023/managed_console.log

### 产物目录
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-20261023/outputs

### 真实产物根目录
（待补充）

### tmux session
（待补充）

</details>

## 解析后的执行环境
- server: 03 · SZY-IPLoc
- ssh_host: SZY-3090
- workspace: 03
- remote_repo: /defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/iploc-szy
- remote_data_root: /defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/dataset
- project_dir: /defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/iploc-szy
- run_dir: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-20261023
- log_file: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-20261023/managed_console.log
- output_dir: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-20261023/outputs
- metrics_file: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-20261023/metrics.json
- tmux_session: incontext-E-015-e015-iploc144-qwen2-4shot-restart-20261023
- launcher: ssh SZY-3090
- environment_activation: conda:IPLoc
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 Steward/Watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: codex
- created: 2026-10-23T20:48:34
- updated: 2026-10-23T20:50:22

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
