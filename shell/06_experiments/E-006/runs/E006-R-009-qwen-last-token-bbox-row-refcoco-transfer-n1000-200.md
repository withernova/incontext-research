# E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200 · Qwen RefCOCO exact-last-token first-step bbox-row parity

- canonical_run_id: `E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200`
- run_type: adapter_validation
- review_status: approved
- review_round: 2
- submitted_for_review_at: 2026-08-03T15:17:11
- approved_at: 2026-08-03T15:22:10
- execution_authorized_at: 2026-08-03T15:22:12
- execution_authorization_consumed_at: 2026-08-04T14:53:41
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
completed

## 本轮目的
在标准单图RefCOCO上检查Qwen exact last-token discovery能否找到在fresh images上靠近GT的heads。

## 必要性 / 证据链位置
提供Qwen-only外部空间正对照；不验证IPLoc-ID identity或Q→R。

## 研究依据 / 被审计对象
R006 row gate；LocalizationHeads公开的last-token selection思路；R007本地RefCOCO manifest。

## 实现方式（简版）
base Qwen3-VL；pilot20；discovery1000按repo-style budget+spatial entropy发现Top5；confirmation200冻结评估。

## 实现方式（详细版）
last-token为primary；bbox p-1仅在稳定可实现时作附录，不再并行膨胀为主实验；固定20张heatmaps。

## 数据身份与构造
R007 RefCOCO expression samples，按COCO image_id跨split隔离。

## 数据规模
20 pilot / 1000 discovery / 200 confirmation。

## 模型、权重与关键配置
base Qwen3-VL-8B-Instruct，单图RefCOCO prompt，bf16 eager；不运行LLaVA，IPLoc-ID LoRA默认不纳入。

## 变量、干预与对照
confirmation不重选；layer-matched random heads×10 frozen seeds；all-head control。

## 指标与计数规则
Top5 IDs/frequency；GT conditional mass；S50 H/M/L；all-head percentile；固定heatmaps。

## 完整性门槛 / no-silent-zero
R006和R007通过；200/200 confirmation；image/span/token finite；head set预冻结。

## 竞争假设与预期特征
若优于controls，支持Qwen last-token在RefCOCO的空间正对照；若失败则该external control不成立。

## 验收条件
完整报告成功或失败；R009不阻塞R010当前IPLoc-ID主线。

## 依赖的 Run / 证据
R006、R007；明确不再依赖已取消R008。

## 观测结果摘要
exit=0,GATE_PASS；20 pilot/1000 discovery/200 fresh confirmation，0 failure。repo-style last-token冻结Top5=L25H08,L27H31,L29H01,L09H14,L26H29；confirmation fractional mass=.04559,enrichment=.22279,pointing=.070,all-head percentile=.0701；10组layer-matched random controls整体更高，S50=.985但controls=.965–1.0而饱和。

## 局限与混杂因素
单图referring-expression grounding不同于双图identity binding。

## 可支持的结论
LocalizationHeads公共仓库的last-token budget+spatial-entropy思路迁移到base Qwen3-VL及本地image-disjoint RefCOCO subset后未建立空间正对照；不是原论文LLaVA/私有精确subset的否定，也不支持Qwen普遍无空间信息。

## 不支持的结论 / Claim 边界
不支持IPLoc-ID identity、Q→R binding或因果。

## 关键指标
{"exit_code":0,"gate":"GATE_PASS","n_pilot":20,"n_discovery":1000,"n_confirmation":200,"n_failures":0,"frozen_heads":["L25H08","L27H31","L29H01","L09H14","L26H29"],"fractional_mass":0.0455898327,"enrichment":0.2227863209,"s50":0.985,"pointing":0.07,"allhead_percentile":0.0701128472}

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-006/followup_validity_and_equivariance_plan.md#r-009

## 过程记录与补充细节
（待补充）

## Run 审核
### 用户补充要求
（待补充）
### 用户疑问
没太看懂这个实验是要干什么
### Agent 完善说明
已将实验简化并解释：它只问Qwen last-token方法在标准RefCOCO上能否找到fresh-image GT-localizing heads，是可选外部空间正对照，不是IPLoc-ID机制实验。LLaVA与IPLoc-ID LoRA已移出primary，bbox-row降为可选附录。
### Agent 对疑问的回应
请决定：保留该Qwen-only RefCOCO外部正对照，还是也取消并直接进入R-010？
### 本次执行授权备注
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
（待补充）

### 配置/超参数
（待补充）

### Seed
20260728

### 日志路径
（待补充）

### 产物目录
（待补充）

### 真实产物根目录
（待补充）

### tmux session
（待补充）

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-006
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200/metrics.json
- tmux_session: incontext-E-006-E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-03T14:54:20
- updated: 2026-08-04T15:39:47

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
