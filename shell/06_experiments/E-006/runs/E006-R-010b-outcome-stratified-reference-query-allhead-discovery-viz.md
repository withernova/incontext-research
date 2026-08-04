# E006-R-010b-outcome-stratified-reference-query-allhead-discovery-viz · correct error balanced-mix by reference-query role all-head discovery and visualization

- canonical_run_id: `E006-R-010b-outcome-stratified-reference-query-allhead-discovery-viz`
- run_type: discovery
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-03T15:17:11
- approved_at: 2026-08-03T18:01:43
- execution_authorized_at: 2026-08-03T18:01:45
- execution_authorization_consumed_at: 
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
planned

## 本轮目的
比较localization-correct、localization-error和组等权balanced-mix在reference/query各角色上的全head身份、排名、budget与GT alignment。

## 必要性 / 证据链位置
落实用户对R010的新增授权备注：检验固定main4是否遗漏error-specific heads，并用图表展示C/E/M及reference/query负责heads是否变化。

## 研究依据 / 被审计对象
E003自然行为分组；E005/E006角色定义；R006 exact last-token gate。

## 实现方式（简版）
sequence-disjoint discovery；C/E/M三组；G→R、Q→R、Q→Q及terminal T→R/T→Q分开做全1152-head discovery。

## 实现方式（详细版）
M对C/E组等权；先用非GT repo-compatible image budget+spatial entropy+frequency发现并冻结Top5/完整ranking，再用GT mass和S50 H/M/C/CG/L评估；固定6 correct+6 error可视化。

## 数据身份与构造
positive natural-Yes：correct IoU>=.7、error IoU<.1；middle/rejected不进入主discovery；按sequence冻结split和聚类。

## 数据规模
执行前报告每组sequence/frame数；任一组sequence不足则停止扩数据。

## 模型、权重与关键配置
Qwen3-VL-8B+IPLoc-ID LoRA，bf16 eager，max_side640。

## 变量、干预与对照
stratum C/E/M × role G→R/Q→R/Q→Q/T→R/T→Q；M组等权；不按GT或transform结果重选。

## 指标与计数规则
full-sequence image budget、entropy/component、selection frequency/rank；GT mass与S50 H/M/C/CG/L；Top-set Jaccard/UpSet/rank correlations。

## 完整性门槛 / no-silent-zero
sequence overlap0；全1152 finite；C/E/M和roles分开；head discovery不依赖GT；固定样本不挑最好。

## 竞争假设与预期特征
区分shared-head strength-change、outcome-specific candidate routing和pooled-mix masking；最终稳定性由R011决定。

## 验收条件
交付C/E/M Top5表、UpSet、Jaccard热图、rank scatter、layer×head差分热图、role矩阵和固定样本多panel可视化。

## 依赖的 Run / 证据
R006；现有sequence-aware natural outputs；不依赖R007-R009。

## 观测结果摘要
（待补充）

## 局限与混杂因素
discovery observational；本run本身不能确认outcome-specific routing。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
只产生候选head/ranking；必须fresh confirmation；不称causal head。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-006/followup_validity_and_equivariance_plan.md#r-010--correcterrorbalanced-mix--referencequery-全-head-discovery重点修订

## 过程记录与补充细节
（待补充）

## Run 审核
### 用户补充要求
（待补充）
### 用户疑问
（待补充）
### Agent 完善说明
旧R010已approved且review workflow禁止直接改稿，故不篡改旧记录；根据用户新增要求建立R010b。R010b新增C/E/M三组、G→R/Q→R/Q→Q/T→R/T→Q多角色、非GT发现与GT评估分离，以及Top5表、UpSet/Jaccard/rank/layer/role图和固定6+6样本heatmaps。旧R010不在本轮执行。
### Agent 对疑问的回应
请确认：balanced-mix采用correct/error组等权；固定可视化为6 correct+6 error；批准后以R010b替代旧R010执行。
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
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-010b-outcome-stratified-reference-query-allhead-discovery-viz
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-010b-outcome-stratified-reference-query-allhead-discovery-viz/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-010b-outcome-stratified-reference-query-allhead-discovery-viz/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-010b-outcome-stratified-reference-query-allhead-discovery-viz/metrics.json
- tmux_session: incontext-E-006-E006-R-010b-outcome-stratified-reference-query-allhead-discovery-viz
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-03T15:17:11
- updated: 2026-08-03T18:01:45

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
