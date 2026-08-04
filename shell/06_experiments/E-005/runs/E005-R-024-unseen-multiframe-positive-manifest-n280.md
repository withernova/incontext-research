# E005-R-024-unseen-multiframe-positive-manifest-n280 · unseen70 multiframe4 positive-only n280 manifest

- canonical_run_id: `E005-R-024-unseen-multiframe-positive-manifest-n280`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed_integrity

## 本轮目的
扩大核心binding discrepancy验证样本，每个未用于旧开发manifest的sequence均匀采4个query时间点。

## 必要性 / 证据链位置
R-023仅35x2且matched频率统计不稳定，需要更大样本与sequence-cluster统计。

## 研究依据 / 被审计对象
LaSOT真实帧与groundtruth；旧manifest明确排除210 sequences。

## 实现方式（简版）
70 unseen sequences×query fractions .25/.5/.75/1.0；reference first valid；nearest distinct valid frame。

## 实现方式（详细版）
bbox裁剪与合法性检查；每sequence query去重；positive-only。

## 数据身份与构造
local deterministic LaSOT reconstruction；非官方IPLoc split；与旧0-139 sequence overlap=0，但与R-014 unseen70 overlap=70。

## 数据规模
280 rows/70 sequences/70 classes/4 queries per sequence。

## 模型、权重与关键配置
none manifest-only

## 变量、干预与对照
fractions frozen=.25,.5,.75,1.0

## 指标与计数规则
manifest integrity counts

## 完整性门槛 / no-silent-zero
rows280 sequences70 classes70 old overlap0 all bbox/image valid

## 观测结果摘要
280 rows,70 sequences,70 classes,old overlap0,R014 overlap70,positive-only。

## 局限与混杂因素
同sequence四query相关；需sequence cluster bootstrap；不是独立于R014的新sequence集。

## 可支持的结论
仅数据扩展产物。

## 不支持的结论 / Claim 边界
不代表280个独立sequence或官方benchmark。

## 关键指标
（待补充）

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-024-unseen-multiframe-positive-manifest-n280; /home/featurize/data/e005_manifests/LASOT_unseen70_multiframe4_positive_n280.json

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r024_build_multiframe280.py

### 配置/超参数
（待补充）

### Seed
20260728

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-024-unseen-multiframe-positive-manifest-n280/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-024-unseen-multiframe-positive-manifest-n280/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-024-unseen-multiframe-positive-manifest-n280

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
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-024-unseen-multiframe-positive-manifest-n280
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-024-unseen-multiframe-positive-manifest-n280/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-024-unseen-multiframe-positive-manifest-n280/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-024-unseen-multiframe-positive-manifest-n280/metrics.json
- tmux_session: incontext-E-005-E005-R-024-unseen-multiframe-positive-manifest-n280
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-28T20:13:24
- updated: 2026-07-28T20:13:24

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
