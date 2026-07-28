# E005-R-023-reference-binding-frequency-fiou-matched35x2 · reference target-binding four-state frequency plus token-fIoU curves matched35x2

- canonical_run_id: `E005-R-023-reference-binding-frequency-fiou-matched35x2`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed_integrity_directional_frequency_not_statistically_stable

## 本轮目的
检验correct自然定位是否比accepted-low-IoU error更常出现reference-grounding heads与natural-bbox query-localization heads共同绑定reference GT；并在实际merged-token coverage允许时补充fractional-token IoU曲线。

## 必要性 / 证据链位置
R-022d已显示query侧自然bbox attention precision与定位正确性强相关，但尚不能回答自然bbox-stage对reference target的回看是否和prompt-stage reference grounding一致。该实验直接判别Q-004 routing mismatch与正常角色分工。

## 研究依据 / 被审计对象
继承R-022d在任何attention结果前冻结的35 error/35 geometry-matched correct pairs；冻结R-014 query-localization heads和R-016/R-014 reference-grounding有效heads；未按R-023 outcomes重选样本、heads或阈值。

## 实现方式（简版）
同一teacher-replayed forward提取两图：Q→R=归档自然bbox token p的p-1 rows×localization heads→reference visual keys；G→R=prompt reference bbox token p的p-1 rows×grounding heads→reference keys。每样本输出一张3-panel图并保存raw逐样本metrics/curves。

## 实现方式（详细版）
Q→R heads=L18H15,L19H03,L22H00,L20H08；G→R heads=L15H13,L16H23,L18H15。严格hit要求GT density enrichment>1、raw argmax token与reference GT有fractional overlap、GT any-overlap coverage>=2。四状态(H_G,H_QR)：11 target-consistent；10 grounding-hit/Q→R-miss routing-mismatch；01 grounding-miss/Q→R-hit；00双方miss。曲线先将reference-span raw nonnegative attention归一化，按rho=.05:.05:.95选择达到累计mass的最小token集合，再与GT cell fractional occupancy计算fIoU；统计不使用插值/平滑。

## 数据身份与构造
E003-R-004b本地确定性LaSOT reconstruction，非官方IPLoc split。error=positive TP/自然Yes/IoU<.1，correct候选=positive TP/自然Yes/IoU>=.7；Hungarian匹配特征为reference/query log bbox area fraction与log aspect ratio的标准化L1，并给same-class固定-0.5 cost偏好。35 pairs中same-class仅1。

## 数据规模
35 matched pairs；70 forwards；70 one-inference figures。实际reference GT any-overlap merged-token coverage：all median4，<=1为10/70，2-3为22/70，>=4为38/70；error median3，correct median4。query GT median4，>=4为49/70。

## 模型、权重与关键配置
Qwen3-VL-8B-Instruct persistent repacked 10-shard权重 + IPLoc-ID LoRA；eager attention、bf16、max_side=224、offline local-only；归档自然输出源生成max_side=640。

## 变量、干预与对照
seed=20260724；pairs/heads/strict-hit/rho grid在结果前冻结；raw unsmoothed maps用于统计；Gaussian sigma1和panel min-max仅用于空间可视化；coverage>=4为curve主子集，>=2为敏感性。

## 指标与计数规则
主指标：00/01/10/11 counts/frequencies及Wilson95；conditional binding=P(Q→R hit|G→R hit,coverage>=2)。补充matched McNemar exact、paired bootstrap 10k、conditional paired-cluster bootstrap 10k。曲线指标为merged-token fractional IoU和rho范围归一化AUC；它不是pixel segmentation。

## 完整性门槛 / no-silent-zero
workflow exit0；70/70 records；70/70 figures；records checkpoint、summary、visual manifest存在；exact region-constrained token subsequence唯一匹配；p-1 autoregressive alignment；all raw enrichment/mass/coverage finite；最终WORKFLOW_DONE后状态才置completed_passed_integrity。

## 观测结果摘要
All样本：target-consistent 11为error 7/35=20.0% [Wilson .100,.359]、correct 15/35=42.9% [.280,.591]；routing-mismatch 10为error17/35=48.6%、correct16/35=45.7%。coverage>=4：11 error4/17=23.5%、correct11/21=52.4%；10 error11/17=64.7%、correct10/21=47.6%。conditional binding error7/24=29.2% [.149,.492]、correct15/31=48.4% [.320,.652]。方向支持correct更常target-consistent，但matched统计未稳定排除0。

## 局限与混杂因素
attention-derived且非因果；Q→R与G→R使用不同rows/head sets，不能称同一circuit；224 replay并非原640 hidden-state复现；多为cross-class geometry matching；严格hit依赖coarse merged grid；coverage筛选会减少paired n；fIoU是token support而非像素segmentation；LaSOT未完整标注其他同类实例，不能确认wrong-instance或identity selectivity；多项secondary analyses未做multiplicity claim。

## 可支持的结论
可安全结论：correct组target-consistent attention signature频率更高，且高coverage子集Q→R fractional-token fIoU AUC更高；但四状态matched CI多跨0、McNemar p>.05，故频率证据为方向性/探索性而非统计稳定确认。G→R curve无组差，差异更集中在natural bbox-stage Q→R signature。

## 不支持的结论 / Claim 边界
不得声称reference-localization binding causal circuit、identity-selective retrieval、confirmed wrong-instance、模型先认对再框错或consistency训练必然提升Joint F1。当前状态investigating/inference_only；需更大same-class matched集、自然非GT probe和行为reranking/因果干预。

## 关键指标
consistent11 all correct-error=+0.2286, paired bootstrap95=[0,.4286], McNemar exact p=.0768 (error-only4/correct-only12); both coverage>=2 diff=.1923 CI[-.0769,.4615], p=.2668; both>=4 diff=.2667 CI[-.0667,.6000], p=.2891. mismatch10 all correct-error=-.0286 CI[-.2857,.2286], p=1.0; >=4=-.2000 CI[-.5333,.1333], p=.4531. conditional correct-error=.1922 paired-cluster CI[-.0729,.4462]. Q→R fIoU AUC >=4: error median=.05595, correct=.10023, paired n15 median diff=.06795 CI[.03305,.08989]; >=2 diff=.03811 CI[-.00781,.07245]. G→R AUC >=4 diff=-.00236 CI[-.04975,.07821].

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-023-reference-binding-frequency-fiou-matched35x2/analysis/summary.json; /home/featurize/work/mechanism/explog/E-005/runs/E005-R-023-reference-binding-frequency-fiou-matched35x2/analysis/posthoc_matched_statistics.json; /home/featurize/work/mechanism/explog/E-005/runs/E005-R-023-reference-binding-frequency-fiou-matched35x2/artifacts/records_checkpoint.json; /home/featurize/work/mechanism/explog/E-005/runs/E005-R-023-reference-binding-frequency-fiou-matched35x2/manifests/visualization_manifest.json; /home/featurize/work/mechanism/explog/E-005/runs/E005-R-023-reference-binding-frequency-fiou-matched35x2/visualizations; /home/featurize/work/mechanism/explog/E-005/e005_binding_workflow.log; /home/featurize/work/mechanism/explog/E-005/runs/E005-R-022d-correct-vs-error-natural-query-attention-matched35x2/analysis/token_coverage_audit.json

## 过程记录与补充细节
Poststats首次系统Python尝试因scipy缺失而失败且未写产物；随后使用与实验相同PYTHONPATH成功执行。posthoc_matched_statistics.json明确标注offline frozen-record analysis，无样本/head/threshold重选。

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_binding_workflow.sh

### 配置/超参数
（待补充）

### Seed
20260724

### 日志路径
/home/featurize/work/mechanism/explog/E-005/e005_binding_workflow.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-023-reference-binding-frequency-fiou-matched35x2/visualizations

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-023-reference-binding-frequency-fiou-matched35x2

### tmux session
e005_binding_workflow

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-023-reference-binding-frequency-fiou-matched35x2
- log_file: /home/featurize/work/mechanism/explog/E-005/e005_binding_workflow.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-023-reference-binding-frequency-fiou-matched35x2/visualizations
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-023-reference-binding-frequency-fiou-matched35x2/metrics.json
- tmux_session: e005_binding_workflow
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-28T13:02:59
- updated: 2026-07-28T13:44:18

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
