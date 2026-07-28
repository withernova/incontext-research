# E005-R-013-unseen-sequence-positive-manifest-n70 · 完全未使用LaSOT sequences positive-only确认manifest n70

- canonical_run_id: `E005-R-013-unseen-sequence-positive-manifest-n70`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed

## 本轮目的
为coordinate-query双spanheads建立不与旧140条sequence重叠的新确认数据。

## 必要性 / 证据链位置
此前0:99为post-hoc recovery；需要新sequence confirmatory gate。

## 研究依据 / 被审计对象
280 local sequences中旧manifest使用210，剩余70且每类1条。

## 实现方式（简版）
排除旧manifest出现的全部sequence；每个未使用sequence取first/last valid frame作为reference/query。

## 实现方式（详细版）
不构造negative donor；独立positive-only schema；bbox裁剪和存在性hard gate。

## 数据身份与构造
70 classes×1 unseen sequence；reference first valid/query last valid。

## 数据规模
70 pairs,140 images。

## 模型、权重与关键配置
data-only。

## 变量、干预与对照
sequence overlap必须0。

## 指标与计数规则
counts/overlap/missing/invalid。

## 完整性门槛 / no-silent-zero
70 rows/classes；overlap0；140 images；bbox valid。

## 观测结果摘要
新sequence positive-only n70 manifest构建通过。

## 局限与混杂因素
deterministic、非官方split、first/last非随机。

## 可支持的结论
可用于预冻结coordinate-query heads的新sequence确认；非官方split。

## 不支持的结论 / Claim 边界
仅支持新sequence confirmation，不代表官方IPL oc-ID分布。

## 关键指标
rows=70,classes=70,images=140,old-used=210,new=70,overlap=0,missing=0,invalid=0。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-013-unseen-sequence-positive-manifest-n70; /home/featurize/data/e005_manifests/LASOT_unseen_sequence_positive_n70.json

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_build_unseen70.py

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-013-unseen-sequence-positive-manifest-n70/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-013-unseen-sequence-positive-manifest-n70/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-013-unseen-sequence-positive-manifest-n70

### tmux session
（待补充）

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-013-unseen-sequence-positive-manifest-n70
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-013-unseen-sequence-positive-manifest-n70/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-013-unseen-sequence-positive-manifest-n70/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-013-unseen-sequence-positive-manifest-n70/metrics.json
- tmux_session: incontext-E-005-E005-R-013-unseen-sequence-positive-manifest-n70
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T16:40:59
- updated: 2026-07-24T16:40:59

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
