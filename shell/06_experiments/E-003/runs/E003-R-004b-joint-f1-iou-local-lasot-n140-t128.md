# E003-R-004b-joint-f1-iou-local-lasot-n140-t128 · E003-R-004b-joint-f1-iou-local-lasot-n140-t128

- canonical_run_id: `E003-R-004b-joint-f1-iou-local-lasot-n140-t128`
- legacy_registry_ids: R-010

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed

## 本轮目的
审计 identification-only F1 与 joint identification-localization correctness 的耦合。

## 必要性 / 证据链位置
论文任务定义要求positive既接受又返回目标实例位置；分别报告F1与mIoU不能验证同一sample联合成功，因此需在per-sample outputs上补Joint F1。

## 研究依据 / 被审计对象
论文将POIL理想映射定义为positive→目标bbox、negative→rejection，并将bbox称为identification component要验证的candidate；正文评测分别报告mIoU/F1，未报告Yes&&IoU阈值联合指标。证据：[[personal2026]] §3.1.1、§3.1.2、§3.3.1、§4.1.2。

## 实现方式（简版）
在同一批140 positive与140 same-class negative上计算 identification F1 及 Joint F1@IoU=0.3/0.5/0.7。

## 实现方式（详细版）
Qwen3-VL-8B-Instruct + IPLoc-ID 1-shot LoRA；offline local snapshot；max_side=640；max_new_tokens=128；Torch compatibility shim；无 token intervention。

## 数据身份与构造
manifest=/home/featurize/data/e002_manifests/LASOT_local_1shot_T2_n140_v2.json；local deterministic reconstruction，非官方split。reference=目标sequence首帧；positive=同sequence末帧；negative=另一同类sequence中间帧。

## 数据规模
local deterministic LaSOT POIL reconstruction；140 samples/70 classes；280 records=140 positive+140 negative；非官方 split。

## 模型、权重与关键配置
Qwen3-VL-8B-Instruct + IPLoc-ID 1-shot LoRA；max_side=640；max_new_tokens=128；torch2.2.2+cu121/transformers4.57.3/peft0.18.0；offline snapshot；is_compiling compatibility shim。

## 变量、干预与对照
无token intervention。同一280 records同时计算identification-only与Joint@IoU={0.3,0.5,0.7}，避免跨run比较；positive/negative保持配对。

## 指标与计数规则
Identification按query-level Yes/No。mIoU仅在140 positive上计算；另报133 identification TP条件mIoU。Joint@tau：positive仅Yes且IoU>=tau为TP；positive No或Yes且IoU<tau均为FN；negative按Yes=FP/No=TN。错误比例分开报告，不把低IoU等同wrong-instance。

## 完整性门槛 / no-silent-zero
exactly 280 records=140 positive+140 negative；processor failure=0；traceback=0；每条decision与bbox/parser字段可审计。任何gate失败不得计算主结果。

## 观测结果摘要
280 records完整。Identification: TP/TN/FP/FN=133/136/4/7，F1=0.9603；positive FN率5.00%，negative FP率2.86%。Positive mIoU(all)=0.5745、median=0.7414；在133个identification TP中mIoU=0.5880、median=0.7441。Joint F1@0.3/0.5/0.7=0.8050/0.7639/0.6909；positive joint failure=43/140(30.71%)、51/140(36.43%)、64/140(45.71%)。Yes但IoU未达阈值=36/133(27.07%)、44/133(33.08%)、57/133(42.86%)。

## 局限与混杂因素
本地deterministic LaSOT reconstruction，非官方split；低IoU包含wrong-instance、part/container/background/scale/coordinate等多种可能；7/35仅单人视觉初筛，不是确认wrong-instance错误率；禁止F1与mIoU直接相减。

## 可支持的结论
支持本地split上的joint-metric coverage gap：identification-only F1不能代表同一样本定位与decision联合正确。不能外推官方幅度或据低IoU证明identity confusion。

## 不支持的结论 / Claim 边界
支持本地setting的metric-level decoupling和joint-metric coverage gap；不支持官方Table8同幅度、不支持F1算错/论文造假、不支持background/category/container shortcut或verifier忽略candidate。

## 关键指标
{"dataset":{"records":280,"positive":140,"negative":140,"classes":70,"official_split":false},"identification":{"TP":133,"FN":7,"FP":4,"TN":136,"F1":0.9602888086642599,"positive_FN_rate":0.05,"negative_FP_rate":0.02857142857142857,"positive_acceptance_recall":0.95,"negative_rejection_rate":0.9714285714285714},"localization":{"positive_mIoU_all":0.5744756054731884,"positive_median_IoU_all":0.7413747310638428,"mIoU_given_identification_TP":0.5879642336622328,"median_IoU_given_identification_TP":0.7440859079360962,"among_identification_TP":{"n":133,"IoU_lt_0.1":{"n":35,"rate":0.2631578947368421},"IoU_lt_0.3":{"n":36,"rate":0.2706766917293233},"IoU_lt_0.5":{"n":44,"rate":0.3308270676691729},"IoU_lt_0.7":{"n":57,"rate":0.42857142857142855}}},"joint":{"0.3":{"TP":97,"FN":43,"FP":4,"TN":136,"F1":0.8049792531120332,"positive_joint_recall":0.6928571428571428,"positive_joint_failure_n":43,"positive_joint_failure_rate":0.30714285714285716,"accepted_but_below_threshold_n":36,"accepted_but_below_threshold_rate_among_identification_tp":0.2706766917293233,"F1_absolute_drop_vs_identification":0.1553095555522267},"0.5":{"TP":89,"FN":51,"FP":4,"TN":136,"F1":0.7639484978540773,"positive_joint_recall":0.6357142857142857,"positive_joint_failure_n":51,"positive_joint_failure_rate":0.3642857142857143,"accepted_but_below_threshold_n":44,"accepted_but_below_threshold_rate_among_identification_tp":0.3308270676691729,"F1_absolute_drop_vs_identification":0.19634031081018266},"0.7":{"TP":76,"FN":64,"FP":4,"TN":136,"F1":0.6909090909090909,"positive_joint_recall":0.5428571428571428,"positive_joint_failure_n":64,"positive_joint_failure_rate":0.4571428571428572,"accepted_but_below_threshold_n":57,"accepted_but_below_threshold_rate_among_identification_tp":0.42857142857142855,"F1_absolute_drop_vs_identification":0.269379717755169}},"visual_semantic_screen":{"denominator":"35 positive identification TP with IoU<0.1","single_reviewer_possible_wrong_instance":{"n":7,"rate_within_low_iou35":0.2,"rate_among_identification_tp":0.05263157894736842,"rate_among_all_positive":0.05},"status":"screening_only_not_confirmed_error_rate"},"boundaries":["Low-IoU is a localization-threshold failure, not automatically wrong-instance.","7/35 is single-reviewer possible wrong-instance screening, not confirmed prevalence.","Local deterministic LaSOT reconstruction, not official IPLoc-ID split.","Do not subtract F1 and mIoU."]}

## 审核入口
config/run.md；logs/run.log；analysis/joint_f1_iou.{json,md}；results/LASOT_local_1shot_T2_n140_v2/generated_texts/e003_r004b_joint_n140.json；local evaluation_audit_rationale.md。

## 过程记录与补充细节
canonical_run_id=E003-R-004b-joint-f1-iou-local-lasot-n140-t128；registry 自动ID仅为工具映射。local_note=shell/06_experiments/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128.md；analysis=analysis/joint_f1_iou.{json,md}；outputs=generated_texts/e003_r004b_joint_n140.json。

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
bash /home/featurize/work/mechanism/scripts/e002/e003_r004_joint_f1_n140.sh (t128 configuration)

### 配置/超参数
（待补充）

### Seed
0

### 日志路径
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128

### tmux session
（待补充）

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-003
- run_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128
- log_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128
- metrics_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128/metrics.json
- tmux_session: incontext-E-003-E003-R-004b-joint-f1-iou-local-lasot-n140-t128
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-20T17:16:20+08:00
- updated: 2026-07-21T14:53:58

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
