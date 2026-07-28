# E005-R-014-unseen-sequence-dual-span-confirmation-n70 · unseen-sequence frozen-head dual-span confirmation n70

- canonical_run_id: `E005-R-014-unseen-sequence-dual-span-confirmation-n70`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed_confirmatory_gates

## 本轮目的
在完全未使用LaSOT sequences上确认预冻结coordinate-query heads是否同时定位reference/query GT。

## 必要性 / 证据链位置
R-011c/R-012b为post-hoc recovery；需要sequence-disjoint confirmation。

## 研究依据 / 被审计对象
R-013提供70 classes×1 unseen sequence，旧数据sequence overlap=0。

## 实现方式（简版）
不重选heads；main4=L18H15,L19H03,L22H00,L20H08，negative control=L24H27；全部70对双span GT审核。

## 实现方式（详细版）
teacher-forced gold query bbox；唯一token子序列；p-1 coordinate prediction rows；前10固定sequence双侧turbo图。

## 数据身份与构造
LASOT_unseen_sequence_positive_n70；first/last valid frames；70 classes。

## 数据规模
70 pairs,140 span maps；main4+1 control；20组固定图。

## 模型、权重与关键配置
Qwen3-VL+IPLoc-ID LoRA eager bf16 224。

## 变量、干预与对照
heads/query/metrics/gates运行前冻结；all1152-head matched control；L24H27负面对照。

## 指标与计数规则
双侧median enrichment、pointing vs all-head、median percentile；control enrichment<1。

## 完整性门槛 / no-silent-zero
sequence overlap0；exact coordinate tokens；span/grid/finite；reference/query各四项confirmatory gates。

## 观测结果摘要
完全未使用70 sequences上预冻结main4双span确认通过；reference/query各4/4 gates，L24H27负面对照双侧低于1。

## 局限与混杂因素
teacher-forced、非官方split、固定first/last、attention非因果、224。

## 可支持的结论
L18H15,L19H03,L22H00,L20H08的teacher-forced coordinate-prediction attention localization signature在新sequence双span复现，query强于reference；支持共通空间选择性，不证明identity matching或因果共同作用。

## 不支持的结论 / Claim 边界
确认attention localization signature的跨sequence复现，不证明identity matching或因果作用。

## 关键指标
reference main4 median enrichment=2.668, percentile=.944, pointing=.229 vs all-head .030, combined enrichment=1.764/pointing=.229；query main4 median=7.646, percentile=.975, pointing=.464 vs .087, combined=4.274/pointing=.586；control ref=.098/query=.077；sequence overlap=0。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-014-unseen-sequence-dual-span-confirmation-n70; /home/featurize/data/e005_manifests/LASOT_unseen_sequence_positive_n70.json

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r014_unseen_confirm.py n70

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-014-unseen-sequence-dual-span-confirmation-n70/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-014-unseen-sequence-dual-span-confirmation-n70/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-014-unseen-sequence-dual-span-confirmation-n70

### tmux session
e005_unseen_confirm

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-014-unseen-sequence-dual-span-confirmation-n70
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-014-unseen-sequence-dual-span-confirmation-n70/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-014-unseen-sequence-dual-span-confirmation-n70/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-014-unseen-sequence-dual-span-confirmation-n70/metrics.json
- tmux_session: e005_unseen_confirm
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T16:41:59
- updated: 2026-07-24T16:44:19

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
