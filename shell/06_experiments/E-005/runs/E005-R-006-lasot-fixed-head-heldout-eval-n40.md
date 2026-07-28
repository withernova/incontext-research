# E005-R-006-lasot-fixed-head-heldout-eval-n40 · 固定discovery heads的LaSOT held-out grounding eval n40

- canonical_run_id: `E005-R-006-lasot-fixed-head-heldout-eval-n40`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed

## 本轮目的
在未参与head选择的40个自有任务样本上评估冻结top5 attention heads的bbox grounding。

## 必要性 / 证据链位置
R-005只产出discovery频率；必须分离selection和evaluation，防止在同一数据上重选并报告。

## 研究依据 / 被审计对象
R-005冻结top5=L02H17,L04H03,L12H21,L02H08,L08H12；indices100:139未用于selection。

## 实现方式（简版）
对held-out indices100:139运行positive/negative prompts；冻结top5；按repo-original sigma1、combined-map mean threshold和all-positive min/max生成矩形bbox。

## 实现方式（详细版）
主指标positive:query IoU；negative:query对另一同类实例bbox的IoU仅作通用物体关注诊断；reference span同时作为sanity diagnostic。

## 数据身份与构造
本地LaSOT/IPLoc-ID deterministic manifest indices100:139；非官方split；不使用COCO。

## 数据规模
40 samples、80 prompts、160 span records。

## 模型、权重与关键配置
Qwen3-VL-8B+IPLoc-ID LoRA；eager bf16；max_side224；fixed top_k5。

## 变量、干预与对照
heads在evaluation前冻结；不允许根据held-out结果重选；positive/negative和reference/query分组报告。

## 指标与计数规则
mIoU、median IoU、Recall@0.3/0.5/0.7；shape/finite/grid；runtime/memory。

## 完整性门槛 / no-silent-zero
160 records、全部门禁通过、fixed heads与R-005一致、正常退出。

## 观测结果摘要
冻结R-005 top5在held-out n40上完成；160/160门禁通过，但positive-query grounding很弱。

## 局限与混杂因素
bbox协议为repo-current矩形适配；低分辨率；non-official split；negative IoU不是负样本任务成功；attention非因果。

## 可支持的结论
当前last-text-token、overall-frequency top5与repo-current bbox组合不能在held-out自有IPLoc-ID数据上提供可靠bbox grounding。该负结果不否定其他query位置、role-specific heads、分辨率或attention组合，也不构成因果结论。

## 不支持的结论 / Claim 边界
只支持冻结attention heads的held-out grounding表现，不支持因果或identity-routing结论。

## 关键指标
fixed=L02H17,L04H03,L12H21,L02H08,L08H12; positive-query mIoU=0.03394, median=0, R@0.3=0.075, R@0.5=0, R@0.7=0；negative-query mIoU=0.00548；reference mIoU约0.00535；runtime=29.30s；peak reserved=18,274,582,528 bytes。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-006-lasot-fixed-head-heldout-eval-n40; /home/featurize/work/mechanism/explog/E-005/runs/E005-R-005-lasot-iplocid-attention-discovery-n100/analysis/summary.json; /home/featurize/data/e002_manifests/LASOT_local_1shot_T2_n140_v2.json

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r006_lasot_fixed_head_eval.py --start 100 --n 40 --top-k 5

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-006-lasot-fixed-head-heldout-eval-n40/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-006-lasot-fixed-head-heldout-eval-n40/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-006-lasot-fixed-head-heldout-eval-n40

### tmux session
e005_lasot_eval

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-006-lasot-fixed-head-heldout-eval-n40
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-006-lasot-fixed-head-heldout-eval-n40/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-006-lasot-fixed-head-heldout-eval-n40/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-006-lasot-fixed-head-heldout-eval-n40/metrics.json
- tmux_session: e005_lasot_eval
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T15:30:53
- updated: 2026-07-24T15:32:41

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
