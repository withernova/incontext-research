# E003-R-006-rejection-linked-bbox-audit-n140 · E003-R-006-rejection-linked-bbox-audit-n140

- canonical_run_id: `E003-R-006-rejection-linked-bbox-audit-n140`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed

## 本轮目的
审计低IoU positive identification TP的错误候选框是否与配对应拒绝negative query的生成框/annotation呈系统性归一化几何接近。

## 必要性 / 证据链位置
Joint F1只证明定位与decision不共现；该离线配对审计检验错误框是否具有rejection-linked结构，而非随机定位噪声。

## 研究依据 / 被审计对象
E003-R-004b中133个identification TP有44个IoU<0.5、35个IoU<0.1；每个sample天然配对positive与same-class negative。

## 实现方式（简版）
复用R-004b自然输出，比较positive prediction与paired negative prediction/annotation的单位画布geometry，并以same-class swap与class-stratified permutation作对照。

## 实现方式（详细版）
attempt-001因整数化pred_bbox复算小框IoU失败，失败log单独保留；attempt-002从raw text重解析浮点0–1000 bbox并映射pixel。其余为四框geometry、n140/TP/低IoU分层、10k permutation/bootstrap和三联图。

## 数据身份与构造
R-004b 280 records + local deterministic LaSOT manifest；140 paired samples/70 classes；非官方split。

## 数据规模
140 sample clusters；140 positive+140 same-class negative；预期133 identification TP，低IoU数量由raw outputs重算。

## 模型、权重与关键配置
offline analysis only；不重跑模型；source=Qwen3-VL-8B+IPLoc-ID 1-shot LoRA自然生成outputs。

## 变量、干预与对照
paired negative prediction/annotation vs同类别另一sample negative；10k类内permutation；同时做all-positive连续分析以缓解outcome-conditioned selection。

## 指标与计数规则
低IoU率以133个positive identification TP为分母；possible-wrong-instance以35个IoU<0.1可视化为初筛分母，严禁称确认错误率。negative candidate IoU以140 negative annotations为参照。

## 完整性门槛 / no-silent-zero
280 records/140 pairs；roles/paths与bbox合法；raw浮点bbox重算IoU与source差<=0.002且在0.1/0.5阈值的集合归属完全一致；visualization count等于source IoU<0.1 TP；无traceback。

## 观测结果摘要
离线复用R-004b：140 pairs/280 records。133个positive identification TP中IoU<0.1为35(26.32%)、IoU<0.5为44(33.08%)；35例均有support+positive-query可视化。单人初筛possible wrong-instance=7/35(20%)，仅为screening，不是确认错误率。Negative candidate mIoU=0.5327；83/140(59.29%) IoU>=0.5，其中82/83(98.80%)最终No。跨图paired rejected-box geometry假设不支持。

## 局限与混杂因素
7例为单人视觉初筛；无第二实例正式bbox/track ID；low-IoU不等于identity confusion；跨图normalized geometry只表示layout/scale。

## 可支持的结论
支持低IoU accepted positives数量与negative localization/rejection可分离的行为观察；不支持wrong-instance总体比例或verifier忽略candidate。

## 不支持的结论 / Claim 边界
不能据此证明identity confusion不存在：跨图像geometry不是视觉/身份相似度；不能证明verifier忽略candidate、不能外推官方split。positive图像内wrong-instance需要多实例annotation或人工semantic audit。

## 关键指标
{"integrity":{"records":280,"samples":140,"positive":140,"negative":140,"errors":0,"low_iou_tp_lt_0.1":35,"tp_iou_lt_0.5":44,"visualizations":35},"positive_localization_reused":{"all_positive_mIoU":0.5744756054731884,"all_positive_median_IoU":0.7413747310638428,"identification_TP_n":133,"identification_TP_mIoU":0.5879642336622328,"identification_TP_median_IoU":0.7440859079360962,"IoU_lt_0.1_n":35,"IoU_lt_0.1_rate_among_identification_TP":0.2631578947368421,"IoU_lt_0.5_n":44,"IoU_lt_0.5_rate_among_identification_TP":0.3308270676691729},"negative_candidate_behavior":{"n":140,"decision_no":136,"iou":{"n":140,"mean":0.5327230372931808,"median":0.6705576777458191,"q025":0.0,"q975":0.9761929392814637},"iou_ge_0.5":83,"no_and_iou_ge_0.5":82,"iou_ge_0.5_rate":0.5928571428571429,"no_and_iou_ge_0.5_rate_all_negative":0.5857142857142857,"no_given_iou_ge_0.5":0.9879518072289156},"visual_semantic_screen":{"possible_wrong_instance_n":7,"low_iou_visualized_n":35,"rate_within_low_iou":0.2,"rate_among_all_positive":0.05,"status":"single_reviewer_screening_only_not_confirmed"},"geometry_hypothesis":{"low_iou_n":35,"paired_negative_prediction_delta_rmse":0.03532782576802011,"paired_negative_prediction_p_lower":0.918008199180082,"supported":false},"boundaries":["Offline audit reuses R-004b; no model rerun.","Low IoU is not automatically wrong-instance.","7/35 is not a confirmed prevalence estimate."]}

## 审核入口
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-006-rejection-linked-bbox-audit-n140/{config,logs,analysis,results,visualizations}; local shell/06_experiments/E-003/artifacts/E003-R-006-support-positive-low-iou/

## 过程记录与补充细节
attempt-001/002失败log保留；attempt-003 completed。关键反证：paired并未更近，不能只报negative候选高IoU辅助发现。local artifacts=shell/06_experiments/E-003/artifacts/E003-R-006-rejection-linked-bbox-audit-n140/。

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
bash /home/featurize/work/mechanism/explog/E-003/runs/E003-R-006-rejection-linked-bbox-audit-n140/config/launch.sh

### 配置/超参数
（待补充）

### Seed
20260720

### 日志路径
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-006-rejection-linked-bbox-audit-n140/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-006-rejection-linked-bbox-audit-n140

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-006-rejection-linked-bbox-audit-n140

### tmux session
e003_r006

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-003
- run_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-006-rejection-linked-bbox-audit-n140
- log_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-006-rejection-linked-bbox-audit-n140/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-006-rejection-linked-bbox-audit-n140
- metrics_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-006-rejection-linked-bbox-audit-n140/metrics.json
- tmux_session: e003_r006
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-21T01:01:17
- updated: 2026-07-21T14:56:27

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
