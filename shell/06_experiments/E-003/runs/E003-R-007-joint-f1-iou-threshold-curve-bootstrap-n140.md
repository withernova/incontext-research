# E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140 · E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140

- canonical_run_id: `E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed

## 本轮目的
在完整IoU阈值范围内审计identification-only F1与joint correctness的解耦，并量化sample-clustered不确定性。

## 必要性 / 证据链位置
仅报告IoU=0.3/0.5/0.7可能受到阈值选择质疑；完整曲线与cluster bootstrap可检验coverage gap是否跨阈值稳定。

## 研究依据 / 被审计对象
复用completed E003-R-004b的280条per-record自然输出，不重跑模型。

## 实现方式（简版）
τ=0.00至1.00、步长0.01计算Joint F1、positive joint recall、accepted-but-below-threshold与failure composition；以140个positive/negative pair为cluster做10,000次bootstrap。

## 实现方式（详细版）
每次bootstrap按sample ID有放回抽取140个cluster，positive与negative共同重采样；固定seed=20260721；保存全部点估计与percentile 95% CI。

## 数据身份与构造
E003-R-004b outputs；local deterministic LaSOT reconstruction；140 clusters=140 positive+140 same-class negative；非官方split。

## 数据规模
140 sample clusters；280 records；101个IoU阈值；10,000 bootstrap replicates。

## 模型、权重与关键配置
offline analysis only；source模型为Qwen3-VL-8B-Instruct + IPLoc-ID 1-shot LoRA；不加载或重跑模型。

## 变量、干预与对照
同一批outputs跨全部阈值；identification F1作为水平reference；cluster重采样保持positive/negative配对。

## 指标与计数规则
Joint@τ：positive仅Yes且IoU>=τ为TP；positive No或Yes但IoU<τ为FN；negative Yes=FP、No=TN；F1=2TP/(2TP+FP+FN)。mIoU与F1不相减。

## 完整性门槛 / no-silent-zero
通过：280 records；140完整positive/negative clusters；finite IoU；τ=0严格等于identification；τ=0.3/0.5/0.7严格复现R-004b；10,000 replicates。attempt-001字段索引失败在任何科学summary前结束，日志单独保留。

## 观测结果摘要
离线n140曲线完成。Identification F1=0.9603 [0.9348,0.9819]。Joint F1@0.3=0.8050 [0.7468,0.8583]、@0.5=0.7639 [0.6996,0.8216]、@0.7=0.6909 [0.6161,0.7598]。对应F1 gap的cluster-bootstrap 95% CI为[0.1073,0.2077]、[0.1426,0.2562]、[0.2051,0.3392]，均不含0。101阈值点，10,000 replicates。

## 局限与混杂因素
本地deterministic LaSOT reconstruction，非官方split；置信区间为140 paired clusters经验分布上的pointwise percentile CI，不是simultaneous confidence band；曲线不证明wrong-instance或机制。

## 可支持的结论
支持本地split上identification-only F1相对Joint F1的跨阈值coverage gap，且预注册0.3/0.5/0.7 gap bootstrap CI均不含0。

## 不支持的结论 / Claim 边界
支持本地split上identification F1相对Joint F1的跨阈值coverage gap；不支持官方幅度、identity confusion或verifier忽略candidate。

## 关键指标
{"integrity":{"records_280":true,"clusters_140":true,"one_positive_one_negative":true,"finite_iou":true,"tau0_equals_identification":true,"replicates_10000":true,"registered_points_reproduced":{"0.3":true,"0.5":true,"0.7":true}},"data":{"clusters":140,"records":280,"positive":140,"negative":140,"split":"local deterministic LaSOT reconstruction; not official"},"identification":{"TP":133,"TN":136,"FP":4,"FN":7,"F1":0.9602888086642599,"bootstrap95":[0.9347826086956522,0.9819494584837545]},"curve":{"thresholds":101,"range":[0.0,1.0],"step":0.01,"bootstrap_replicates":10000,"seed":20260721,"key_points":{"0.1":{"joint_f1":0.8099173553719008,"joint_f1_ci_low":0.752136766910553,"joint_f1_ci_high":0.8617886304855347,"positive_joint_recall":0.7,"accepted_below_n":35,"accepted_below_rate_all_positive":0.25,"f1_gap_vs_identification":0.15037145329235913,"f1_gap_ci_low":0.10321034491062164,"f1_gap_ci_high":0.20237819850444794},"0.3":{"joint_f1":0.8049792531120332,"joint_f1_ci_low":0.7467811107635498,"joint_f1_ci_high":0.8582996129989624,"positive_joint_recall":0.6928571428571428,"accepted_below_n":36,"accepted_below_rate_all_positive":0.2571428571428571,"f1_gap_vs_identification":0.1553095555522267,"f1_gap_ci_low":0.10732773374766112,"f1_gap_ci_high":0.20774872638285158},"0.5":{"joint_f1":0.7639484978540773,"joint_f1_ci_low":0.6995515823364258,"joint_f1_ci_high":0.8215767741203308,"positive_joint_recall":0.6357142857142857,"accepted_below_n":44,"accepted_below_rate_all_positive":0.3142857142857143,"f1_gap_vs_identification":0.19634031081018266,"f1_gap_ci_low":0.14256874956190585,"f1_gap_ci_high":0.25620538145303723},"0.7":{"joint_f1":0.6909090909090909,"joint_f1_ci_low":0.6161137223243713,"joint_f1_ci_high":0.7598253488540649,"positive_joint_recall":0.5428571428571428,"accepted_below_n":57,"accepted_below_rate_all_positive":0.40714285714285714,"f1_gap_vs_identification":0.269379717755169,"f1_gap_ci_low":0.20511268079280853,"f1_gap_ci_high":0.33917051553726196},"0.9":{"joint_f1":0.3728813559322034,"joint_f1_ci_low":0.28070175647735596,"joint_f1_ci_high":0.4615591421723363,"positive_joint_recall":0.2357142857142857,"accepted_below_n":100,"accepted_below_rate_all_positive":0.7142857142857143,"f1_gap_vs_identification":0.5874074527320565,"f1_gap_ci_low":0.4996568262577057,"f1_gap_ci_high":0.6783145070075989}},"bootstrap_npz_sha256":"c06388d78755322ecc41075c08a15ce77611226372b1a4b1a62d8897408a0e8f"},"offline_no_model_rerun":true,"scope":"local deterministic LaSOT reconstruction; evaluation coverage only"}

## 审核入口
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140/config/run.md；logs/run.log；logs/attempt-001-failed-cluster-field-index.log；analysis/summary.{json,md}；results/threshold_curve.{csv,json}；results/bootstrap_replicates.npz；visualizations/manifest.json；local shell/06_experiments/E-003/artifacts/E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140/

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
PYTHONNOUSERSITE=1 bash /home/featurize/work/mechanism/explog/E-003/runs/E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140/config/launch.sh

### 配置/超参数
（待补充）

### Seed
20260721

### 日志路径
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140

### tmux session
e003_r007

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-003
- run_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140
- log_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140
- metrics_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140/metrics.json
- tmux_session: e003_r007
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-21T16:24:31
- updated: 2026-07-21T16:28:58

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
