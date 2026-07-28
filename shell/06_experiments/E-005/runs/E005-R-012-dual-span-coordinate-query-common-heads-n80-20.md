# E005-R-012-dual-span-coordinate-query-common-heads-n80-20 · dual-span coordinate-query shared localization heads n80+20

- canonical_run_id: `E005-R-012-dual-span-coordinate-query-common-heads-n80-20`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_mixed_quality

## 本轮目的
检验bbox坐标预测阶段是否有同时作用于reference与query GT的共通attention heads。

## 必要性 / 证据链位置
用户要求对reference/query都进行同样计算，并分析head共通性。

## 研究依据 / 被审计对象
R-011c coordinate-query在query GT质量门禁3/3通过。

## 实现方式（简版）
同一forward的coordinate prediction rows分别截取reference/query spans；0:79分别发现，冻结reference-specific/query-specific/shared三套top5；80:99交叉GT审核。

## 实现方式（详细版）
shared按min(reference count,query count)优先、总频率tie-break冻结；每套heads在两个span都评估；shared输出双角色turbo图。

## 数据身份与构造
positive query local deterministic split 0:79 discovery/80:99 internal validation。

## 数据规模
80 discovery×2 spans；20 validation×2 spans×3 head sets；20组图。

## 模型、权重与关键配置
Qwen3-VL+LoRA eager bf16 224；teacher-forced gold bbox p-1 rows。

## 变量、干预与对照
同query rows和同forward；GT不参与ranking；all1152-head matched controls。

## 指标与计数规则
top5/top20 overlap Jaccard；selection frequency；双span GT enrichment、pointing、all-head percentile。

## 完整性门槛 / no-silent-zero
唯一coord subsequence、span/grid/finite；shared heads在reference/query各自三项quality gate。

## 观测结果摘要
reference/query独立frequency top5重叠弱；frequency-intersection shared set双侧quality失败，但query-derived整组跨span通过，需区分频率共现与GT有效性。

## 局限与混杂因素
post-hoc、teacher-forced、已有data、reference attention是在预测query bbox阶段、attention非因果。

## 可支持的结论
repo selection frequency不能直接定义共同有效heads。query-derived五头作为整体在双span有GT选择性，但reference较弱，且L24H27单头双侧差；仅attention signature，不是因果共同作用。

## 不支持的结论 / Claim 边界
共通仅指双span attention localization signature，不等同因果共同作用或identity routing。

## 关键指标
top5 overlap仅L24H27,Jaccard=.111；top20 overlap=4,Jaccard=.111；reference-specific set在reference median enrichment=.212失败；frequency-shared reference/query median=.151/.157失败；query-specific跨reference median=1.760,pctl=.907,pointing=.11>.024；跨query median=7.965,pctl=.973,pointing=.27>.070。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-012-dual-span-coordinate-query-common-heads-n80-20

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r012_dual_span.py --disc80 --val20

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-012-dual-span-coordinate-query-common-heads-n80-20/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-012-dual-span-coordinate-query-common-heads-n80-20/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-012-dual-span-coordinate-query-common-heads-n80-20

### tmux session
e005_dual_span

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-012-dual-span-coordinate-query-common-heads-n80-20
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-012-dual-span-coordinate-query-common-heads-n80-20/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-012-dual-span-coordinate-query-common-heads-n80-20/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-012-dual-span-coordinate-query-common-heads-n80-20/metrics.json
- tmux_session: e005_dual_span
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T16:33:58
- updated: 2026-07-24T16:38:23

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
