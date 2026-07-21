# E-003 · 实验结果

## 运行汇总（survey-tool 管理）
| Run | Variant | Seed | 状态 | 指标 |
|---|---|---:|---|---|
| E003-R-004b-joint-f1-iou-local-lasot-n140-t128 | E003-R-004b-joint-f1-iou-local-lasot-n140-t128 | 0 | completed | {"dataset":{"records":280,"positive":140,"negative":140,"classes":70,"official_split":false},"identification":{"TP":133,"FN":7,"FP":4,"TN":136,"F1":0.9602888086642599,"positive_FN_rate":0.05,"negative_FP_rate":0.02857142857142857,"positive_acceptance_recall":0.95,"negative_rejection_rate":0.9714285714285714},"localization":{"positive_mIoU_all":0.5744756054731884,"positive_median_IoU_all":0.7413747310638428,"mIoU_given_identification_TP":0.5879642336622328,"median_IoU_given_identification_TP":0.7440859079360962,"among_identification_TP":{"n":133,"IoU_lt_0.1":{"n":35,"rate":0.2631578947368421},"IoU_lt_0.3":{"n":36,"rate":0.2706766917293233},"IoU_lt_0.5":{"n":44,"rate":0.3308270676691729},"IoU_lt_0.7":{"n":57,"rate":0.42857142857142855}}},"joint":{"0.3":{"TP":97,"FN":43,"FP":4,"TN":136,"F1":0.8049792531120332,"positive_joint_recall":0.6928571428571428,"positive_joint_failure_n":43,"positive_joint_failure_rate":0.30714285714285716,"accepted_but_below_threshold_n":36,"accepted_but_below_threshold_rate_among_identification_tp":0.2706766917293233,"F1_absolute_drop_vs_identification":0.1553095555522267},"0.5":{"TP":89,"FN":51,"FP":4,"TN":136,"F1":0.7639484978540773,"positive_joint_recall":0.6357142857142857,"positive_joint_failure_n":51,"positive_joint_failure_rate":0.3642857142857143,"accepted_but_below_threshold_n":44,"accepted_but_below_threshold_rate_among_identification_tp":0.3308270676691729,"F1_absolute_drop_vs_identification":0.19634031081018266},"0.7":{"TP":76,"FN":64,"FP":4,"TN":136,"F1":0.6909090909090909,"positive_joint_recall":0.5428571428571428,"positive_joint_failure_n":64,"positive_joint_failure_rate":0.4571428571428572,"accepted_but_below_threshold_n":57,"accepted_but_below_threshold_rate_among_identification_tp":0.42857142857142855,"F1_absolute_drop_vs_identification":0.269379717755169}},"visual_semantic_screen":{"denominator":"35 positive identification TP with IoU<0.1","single_reviewer_possible_wrong_instance":{"n":7,"rate_within_low_iou35":0.2,"rate_among_identification_tp":0.05263157894736842,"rate_among_all_positive":0.05},"status":"screening_only_not_confirmed_error_rate"},"boundaries":["Low-IoU is a localization-threshold failure, not automatically wrong-instance.","7/35 is single-reviewer possible wrong-instance screening, not confirmed prevalence.","Local deterministic LaSOT reconstruction, not official IPLoc-ID split.","Do not subtract F1 and mIoU."]} |
| E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20 | E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20 | 0 | failed | {"records_written":240,"finite_logits":true,"actual_role_mode_cells":12,"records_per_actual_cell":20,"traceback":true,"formal_analysis":false} |
| E003-R-001-data-rehydrate-local-lasot-n140 | E003-R-001-data-rehydrate-local-lasot-n140 |  | completed | {"samples": 140, "classes": 70, "positive": 140, "negative": 140, "missing": 0, "invalid_bbox": 0} |
| E003-R-002-joint-f1-n140-failed-env | E003-R-002-joint-f1-n140-failed-env |  | failed | {"valid_records": 0, "error": "torch.compiler.is_compiling missing", "post_error": "ZeroDivisionError"} |
| E003-R-003-torch-compat-smoke-local-lasot-n1 | E003-R-003-torch-compat-smoke-local-lasot-n1 |  | completed | {"records": 2, "TP": 1, "TN": 1, "FP": 0, "FN": 0, "status": "passed"} |
| E003-R-004-joint-f1-iou-local-lasot-n140 | E003-R-004-joint-f1-iou-local-lasot-n140 |  | aborted | {"max_new_tokens": 80, "approx_progress_samples": 9, "complete": false} |
| E003-R-005-forced-candidate-verifier-local-lasot-n20 | E003-R-005-forced-candidate-verifier-local-lasot-n20 |  | failed | {"valid_outputs": 0, "error": "ModuleNotFoundError: loc_dataset"} |
| E003-R-005b-forced-candidate-verifier-local-lasot-n20 | E003-R-005b-forced-candidate-verifier-local-lasot-n20 |  | aborted | {"scientific_outputs": 0, "parser_fallback_invalid": true} |
| E003-R-005c-forced-candidate-verifier-local-lasot-n20 | E003-R-005c-forced-candidate-verifier-local-lasot-n20 |  | aborted | {"scientific_outputs": 0, "candidate_in_assistant_history": false} |
| E003-R-005d-forced-candidate-verifier-local-lasot-n20 | E003-R-005d-forced-candidate-verifier-local-lasot-n20 |  | aborted | {"scientific_outputs": 0, "assistant_prefix": true, "unparsed_zero_gate_passed": false} |
| E003-R-006-rejection-linked-bbox-audit-n140 | E003-R-006-rejection-linked-bbox-audit-n140 | 20260720 | completed | {"integrity":{"records":280,"samples":140,"positive":140,"negative":140,"errors":0,"low_iou_tp_lt_0.1":35,"tp_iou_lt_0.5":44,"visualizations":35},"positive_localization_reused":{"all_positive_mIoU":0.5744756054731884,"all_positive_median_IoU":0.7413747310638428,"identification_TP_n":133,"identification_TP_mIoU":0.5879642336622328,"identification_TP_median_IoU":0.7440859079360962,"IoU_lt_0.1_n":35,"IoU_lt_0.1_rate_among_identification_TP":0.2631578947368421,"IoU_lt_0.5_n":44,"IoU_lt_0.5_rate_among_identification_TP":0.3308270676691729},"negative_candidate_behavior":{"n":140,"decision_no":136,"iou":{"n":140,"mean":0.5327230372931808,"median":0.6705576777458191,"q025":0.0,"q975":0.9761929392814637},"iou_ge_0.5":83,"no_and_iou_ge_0.5":82,"iou_ge_0.5_rate":0.5928571428571429,"no_and_iou_ge_0.5_rate_all_negative":0.5857142857142857,"no_given_iou_ge_0.5":0.9879518072289156},"visual_semantic_screen":{"possible_wrong_instance_n":7,"low_iou_visualized_n":35,"rate_within_low_iou":0.2,"rate_among_all_positive":0.05,"status":"single_reviewer_screening_only_not_confirmed"},"geometry_hypothesis":{"low_iou_n":35,"paired_negative_prediction_delta_rmse":0.03532782576802011,"paired_negative_prediction_p_lower":0.918008199180082,"supported":false},"boundaries":["Offline audit reuses R-004b; no model rerun.","Low IoU is not automatically wrong-instance.","7/35 is not a confirmed prevalence estimate."]} |
| E003-R-010-natural-same-image-instance-binding-logit-pilot-n7 | E003-R-010-natural-same-image-instance-binding-logit-pilot-n7 |  | completed_gate_failed | {"integrity":{"records":21,"samples":7,"modes_per_sample":3,"finite_logits":true,"visualizations":7},"replay_gate":{"expected_yes":7,"observed_yes":1,"observed_no":6,"pass":false},"noninterpretable_audit_only":{"target_yes":1,"wrong_yes":1,"background_yes":0,"binding_success":1,"mean_target_minus_wrong_margin":-0.7034040179,"bootstrap95":[-2.6439732143,1.1372767857]}} |
| E003-R-011-self-replayed-same-image-binding-logit-pilot-n7 | E003-R-011-self-replayed-same-image-binding-logit-pilot-n7 |  | aborted | {"scientific_records":0,"attempts":1,"traceback":true} |
| E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140 | E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140 | 20260721 | completed | {"integrity":{"records_280":true,"clusters_140":true,"one_positive_one_negative":true,"finite_iou":true,"tau0_equals_identification":true,"replicates_10000":true,"registered_points_reproduced":{"0.3":true,"0.5":true,"0.7":true}},"data":{"clusters":140,"records":280,"positive":140,"negative":140,"split":"local deterministic LaSOT reconstruction; not official"},"identification":{"TP":133,"TN":136,"FP":4,"FN":7,"F1":0.9602888086642599,"bootstrap95":[0.9347826086956522,0.9819494584837545]},"curve":{"thresholds":101,"range":[0.0,1.0],"step":0.01,"bootstrap_replicates":10000,"seed":20260721,"key_points":{"0.1":{"joint_f1":0.8099173553719008,"joint_f1_ci_low":0.752136766910553,"joint_f1_ci_high":0.8617886304855347,"positive_joint_recall":0.7,"accepted_below_n":35,"accepted_below_rate_all_positive":0.25,"f1_gap_vs_identification":0.15037145329235913,"f1_gap_ci_low":0.10321034491062164,"f1_gap_ci_high":0.20237819850444794},"0.3":{"joint_f1":0.8049792531120332,"joint_f1_ci_low":0.7467811107635498,"joint_f1_ci_high":0.8582996129989624,"positive_joint_recall":0.6928571428571428,"accepted_below_n":36,"accepted_below_rate_all_positive":0.2571428571428571,"f1_gap_vs_identification":0.1553095555522267,"f1_gap_ci_low":0.10732773374766112,"f1_gap_ci_high":0.20774872638285158},"0.5":{"joint_f1":0.7639484978540773,"joint_f1_ci_low":0.6995515823364258,"joint_f1_ci_high":0.8215767741203308,"positive_joint_recall":0.6357142857142857,"accepted_below_n":44,"accepted_below_rate_all_positive":0.3142857142857143,"f1_gap_vs_identification":0.19634031081018266,"f1_gap_ci_low":0.14256874956190585,"f1_gap_ci_high":0.25620538145303723},"0.7":{"joint_f1":0.6909090909090909,"joint_f1_ci_low":0.6161137223243713,"joint_f1_ci_high":0.7598253488540649,"positive_joint_recall":0.5428571428571428,"accepted_below_n":57,"accepted_below_rate_all_positive":0.40714285714285714,"f1_gap_vs_identification":0.269379717755169,"f1_gap_ci_low":0.20511268079280853,"f1_gap_ci_high":0.33917051553726196},"0.9":{"joint_f1":0.3728813559322034,"joint_f1_ci_low":0.28070175647735596,"joint_f1_ci_high":0.4615591421723363,"positive_joint_recall":0.2357142857142857,"accepted_below_n":100,"accepted_below_rate_all_positive":0.7142857142857143,"f1_gap_vs_identification":0.5874074527320565,"f1_gap_ci_low":0.4996568262577057,"f1_gap_ci_high":0.6783145070075989}},"bootstrap_npz_sha256":"c06388d78755322ecc41075c08a15ce77611226372b1a4b1a62d8897408a0e8f"},"offline_no_model_rerun":true,"scope":"local deterministic LaSOT reconstruction; evaluation coverage only"} |

## 结果摘要（survey-tool 管理）
（待登记）

## 对 Claims 的影响（survey-tool 管理）
（待人工判断；不会自动提升 Claim）

## 局限性（survey-tool 管理）
（待补充）

## 详细审计正文（canonical）
### 审计依据

论文将理想 POIL 定义为 positive 返回目标实例 bbox、negative rejection；方法又将生成 bbox 描述为 identification component 要验证的 candidate。已读取正文分别报告 localization mIoU 与 identification F1，但未报告要求二者在同一 positive sample 上同时成立的 `Yes && IoU>=tau` joint metric。[[personal2026]] §3.1.1 Personalized object identification and localization；[[personal2026]] §3.1.2 Evaluation metric for POIL；[[personal2026]] §3.3.1 Sequential generation of localization and identification；[[personal2026]] §4.1.2 Evaluation procedure。

这是 **joint-metric coverage gap**：不等于论文没有评测 localization，不等于 F1 计算错误，更不是研究不端指控。完整论证见 `evaluation_audit_rationale.md`。

### 数据身份

```text
manifest=/home/featurize/data/e002_manifests/LASOT_local_1shot_T2_n140_v2.json
local deterministic LaSOT POIL reconstruction
not the official IPLoc-ID split
140 samples / 70 classes / 140 positive + 140 same-class negative
```

reference=目标sequence首帧；positive=同sequence末帧；negative=另一同类sequence中间帧。该设置不等价于复现论文 Table 8。

### Joint metric

\[
TP_\tau=\mathbb{1}[y=1,\hat y=1,IoU(\hat B,B^*)\ge\tau].
\]

Positive Yes且IoU≥τ为TP；positive No或Yes但IoU<τ为FN；negative Yes为FP、No为TN。固定报告τ={0.3,0.5,0.7}。禁止把 identification F1 与 mIoU 直接相减。

### 主结果：E003-R-004b

完整性：280 records=140 positive+140 negative，无processor failure/traceback。完整错误率、mIoU、Joint分母与比例另见`detailed_metrics.md`。

| 口径 | TP | TN | FP | FN | F1 |
|---|---:|---:|---:|---:|---:|
| Identification-only | 133 | 136 | 4 | 7 | **0.9603** |
| Joint@IoU≥0.3 | 97 | 136 | 4 | 43 | **0.8050** |
| Joint@IoU≥0.5 | 89 | 136 | 4 | 51 | **0.7639** |
| Joint@IoU≥0.7 | 76 | 136 | 4 | 64 | **0.6909** |

133个 identification TP 中，IoU<0.1为35个（26.32%）、IoU<0.3为36个（27.07%）、IoU<0.5为44个（33.08%）、IoU<0.7为57个（42.86%）。全部140 positive的mIoU/median IoU为0.5745/0.7414；133个identification TP条件下为0.5880/0.7441。Identification positive FN=7/140（5.00%），negative FP=4/140（2.86%）。

Positive joint failure率为：IoU 0.3下43/140（30.71%）、0.5下51/140（36.43%）、0.7下64/140（45.71%）。低IoU率是定位阈值失败率，不等同wrong-instance确认率。

### E003-R-007：完整IoU阈值曲线与cluster bootstrap

离线复用R-004b，不重跑模型。以140个positive/negative pair为cluster做10,000次bootstrap（seed=20260721），在`τ=0.00..1.00`、步长0.01上计算Joint F1。`τ=0`严格复现Identification F1；0.3/0.5/0.7严格复现R-004b：

| 口径 | 点估计 | sample-clustered bootstrap 95% CI | 相对Identification F1的gap 95% CI |
|---|---:|---:|---:|
| Identification F1 | 0.9603 | [0.9348, 0.9819] | — |
| Joint F1@0.3 | 0.8050 | [0.7468, 0.8583] | [0.1073, 0.2077] |
| Joint F1@0.5 | 0.7639 | [0.6996, 0.8216] | [0.1426, 0.2562] |
| Joint F1@0.7 | 0.6909 | [0.6161, 0.7598] | [0.2051, 0.3392] |

三个预注册阈值下的paired F1 gap CI均不含0，支持当前本地split上的跨阈值joint-metric coverage gap。置信带是逐阈值pointwise percentile CI，不是simultaneous confidence band。曲线不能证明wrong-instance或任何机制。

审核入口：`artifacts/E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140/`。

### 分级结论

```text
已成立（正文覆盖）：component mIoU/F1 未覆盖同样本joint correctness。
已成立（本地实证）：identification F1=0.9603，而Joint F1@0.5=0.7639。
尚未成立（官方幅度）：官方split/checkpoint上同等幅度gap。
尚未成立（错误类型）：低IoU cases待coordinate/frame/annotation audit。
尚未成立（机制）：verifier忽略candidate或依赖background/category/container shortcut。
```

当前可说：在本地确定性重建 split 上，identification-only F1 明显高估 joint identification-localization success。

当前不可说：论文造假、F1虚假、论文没有定位评测、官方表格必有同幅度gap、verifier完全忽略candidate或存在某类shortcut。

### 失败链的重要性

R-002零records来自环境失败，不是零性能；R-004因80-token截断主动中止；R-005至R-005d依次暴露PYTHONPATH、bbox fallback parser、user-turn prefix和自由文本歧义问题；R-005e虽写出240条finite records，但post-output role gate错误且日志以AssertionError结束，无formal analysis，因此不得引用科学margin。

### E003-R-006：低IoU与paired rejected bbox审计

R-006复用R-004b的140 pairs，比较positive错误prediction与paired negative prediction/annotation的归一化bbox geometry，并加入同类swap、10,000次permutation/bootstrap及35张极低IoU三联图。

主假设未获支持：

```text
IoU<0.1 TP (n=35)
到paired negative prediction: RMSE=0.2880
到same-class control:          RMSE=0.2527
delta=+0.0353, paired-closer=0.400, p_lower=0.9180

到paired negative annotation: RMSE=0.2924
到same-class control:          RMSE=0.2772
delta=+0.0152, paired-closer=0.429, p_lower=0.6637
```

因此没有证据表明低IoU positive框在跨图像layout/scale geometry上特别接近其paired rejected bbox。该结果不能排除positive图像内部选中wrong same-class instance。

辅助观察：83/140 negative自然生成candidate对distractor annotation达到IoU≥0.5，其中82个最终回答No。这说明模型经常能先定位同类distractor再拒绝其identity；该现象与论文的sequential design相容，不是缺陷本身。它也表明positive低IoU失败不能简单解释为模型在所有query上都不会定位类别对象。

### 公开manifest双向reference覆盖审计

逐文件审计全部公开T2 manifests中同一query path的reference-switch结构：

- LaSOT train/test与VastTrack：同一query在distinct reference sets下复用为0；
- PDM：有query path重复，但reference set不变；
- GOT-10K：每个shot有3个query被不同reference复用，但都是“对自身sequence reference为positive、对无关类别reference为out-class negative”，属于跨类别query-level rejection，不是同图同类A/B candidate binding；
- LaSOT train另有28对reciprocal sequence-level negative edges，但A和B位于不同query images，没有固定`query(A,B)`或candidate A/B双框。

所以公开manifest没有显式构造/计分真实双向四格：`ref A/B × candidate A/B on the same query(A,B)`。这解释了为什么identification F1即使很高，也不能直接显露该cell的成功或失败：F1只接收到manifest定义的query-level positive/negative标签，没有“同一positive query中candidate选错另一个实例应判No”的监督/计分事件。该结论是评测覆盖判断，不证明模型一定失败，也不证明source frames没有额外实例。

### E003-R-010：自然同图wrong-instance logit pilot（replay gate failed；设计已废弃）

人工核验7个R-006自然wrong-instance failures，比较target GT、自然wrong-instance和matched background assistant-prefix candidates。工程产物完整：21 records、7×3、finite logits、7张可视化。

但关键replay gate失败：源R-004b中7/7自然输出为Yes；在当前环境中使用exact source wrong-instance prefix截至`?`，并评分真实leading-space token ` Yes`=7414 / ` No`=2308，只复现1/7 Yes。因此所有candidate counterfactual margin均不可作科学解释；R-010状态是`completed_gate_failed`，没有回答candidate-binding假设。

该审计还发现R-005e在literal trailing-space prefix后错误评分9454/2753 beginning-of-string tokens；R-005e logits不可引用，这一问题独立于其原有post-output assertion failure。

经设计复核，后续科学实验完全删除background candidate。R-010历史产物按审计要求保留，但不得继续作为设计模板或证据；R-011 attempt-001在0 scientific records处实现失败后已aborted且不重试。下一正式实验只保留真实`reference A/B × candidate A/B`双向四格。

### 下一证据

1. 对齐R-004b/current的模型snapshot、LoRA、Transformers、chat token IDs和image tensors，先通过exact-prefix replay；
2. replay通过后重新运行target/wrong-instance/background counterfactual；
3. 扩展positive图像内多实例annotation/人工taxonomy；
4. R-007 10,000次Joint F1 sample-clustered paired bootstrap；
5. 官方manifest/checkpoint下复算。

### 审核入口

```text
shell/06_experiments/E-003/evaluation_audit_rationale.md
shell/06_experiments/E-003/experiment_audit_notes.md
remote E003-R-004b/config/run.md
remote E003-R-004b/logs/run.log
remote E003-R-004b/analysis/joint_f1_iou.json
remote E003-R-004b/results/.../e003_r004b_joint_n140.json
```
