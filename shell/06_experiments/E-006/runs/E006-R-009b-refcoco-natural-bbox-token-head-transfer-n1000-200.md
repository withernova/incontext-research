# E006-R-009b-refcoco-natural-bbox-token-head-transfer-n1000-200 · refcoco-natural-bbox-token-head-transfer-n1000-200

- canonical_run_id: `E006-R-009b-refcoco-natural-bbox-token-head-transfer-n1000-200`
- run_type: hypothesis_test
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-04T15:40:37
- approved_at: 2026-08-04T15:42:03
- execution_authorized_at: 2026-08-04T15:42:05
- execution_authorization_consumed_at: 2026-08-04T15:42:57
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
completed

## 本轮目的
在与R-009完全相同的RefCOCO image-disjoint 20/1000/200 manifest上，把primary row从last-input token改为模型自然生成bbox各token的p-1 rows，使用我们R-010的非GTbudget×(1-entropy)方法冻结选头，并检验其fresh GT localization及与既有IPLoc-ID bbox heads的重合。

## 必要性 / 证据链位置
R-009表明repo-style Qwen last-token选头在fresh RefCOCO上劣于random controls。需要区分Qwen无可迁移空间heads与定位信号只在bbox生成阶段形成。RefCOCO单图可提供外部任务正对照，并直接测试bbox-token selection能否恢复IPLoc-ID中发现的main4或R-010 B→Q ranking。

## 研究依据 / 被审计对象
R-009完成1000/200：last-token Top5=L25H08,L27H31,L29H01,L09H14,L26H29，enrichment=.223/allhead percentile=.070。IPLoc-ID historical main4=L18H15,L19H03,L22H00,L20H08；R-010定义bbox rows为每个自然bbox token p-1，非GT selection score=mean full-image budget×(1-mean normalized entropy)，并保留全1152 GT矩阵。

## 实现方式（简版）
base Qwen3-VL对每个RefCOCO样本真实自然生成一个bbox；严格解析该条件自己的bbox并teacher replay，连续唯一匹配bbox token IDs，提取所有bbox token p-1 rows→单图visual span的全1152 head矩阵。discovery1000只按非GT score冻结TopK=5/10；confirmation200评估GT mass/enrichment/S50/pointing/allhead percentile，并与random controls、R-009 last-token heads、IPLoc main4、R-010 B→Q correct/error/mix top rankings比较。

## 实现方式（详细版）
Prompt明确要求只输出像素坐标bbox `[x1,y1,x2,y2]`，坐标基于当前processor/display image尺寸；max_side=640。先natural generate max_new_tokens=64,do_sample=False；从natural response首个合法方括号bbox定位字符区间，在含assistant response的multimodal template IDs中做prompt-region constrained continuous exact match，0/多匹配硬失败；每个bbox token位置p使用attention row p-1，同一teacher forward按所有bbox rows取mean。不得gold-bbox replay替代natural parse failure。保存last-input矩阵作为同forward task control，但primary不据此重选。

## 数据身份与构造
严格复用R-007b frozen_manifest.jsonl及同一split：pilot20/discovery1000/confirmation200，1220 distinct COCO image_id。GT为RefCOCO bbox_xyxy；natural output与GT仅在confirmation评价，discovery selection不读取GT。

## 数据规模
20 pilot engineering/parse gate；通过后1000 discovery+200 confirmation。1220 natural generations+最多1220 teacher replays，顺序单样本checkpoint。若pilot parse<18/20则GATE_STOP并只报告prompt/parse失败，不用GT强制回放。

## 模型、权重与关键配置
base Qwen3-VL-8B-Instruct，不加载IPLoc LoRA；bf16 eager output_attentions=True；max_side=640；单RTX4090 24GB max_memory={0:22GiB}并允许CPU offload；all36×32 heads。

## 变量、干预与对照
主要对比row=last-input vs natural bbox-token p-1；同一image/expression/model/processor。bbox selection用R-010 score而非R-009 repo chord filter，以单独表格报告方法差异；另提供bbox-row上repo-style selection敏感性附录，但不得作为primary事后替换。

## 指标与计数规则
Primary：confirmation中bbox Top5聚合GT fractional mass/enrichment/S50/pointing/allhead percentile，对10个layer-matched random controls；并对R-009 frozen last-token Top5在bbox rows上同评。Head overlap：与IPLoc main4的Top5/Top10 Jaccard和rank intersection；与R-010 B→Q correct/error Top10分别Jaccard/Spearman（仅共同heads）及top-k overlap；与R-009 last Top5。报告discovery head frequency/score、natural parse rate、bbox IoU仅作behavior metadata。按image bootstrap B=10000。

## 完整性门槛 / no-silent-zero
1) R-007b manifest hash完全一致；2) pilot parse>=18/20；3)自然bbox不得用GT替代；4) exact token match唯一，p-1严格；5) discovery完全不读取GT；6) confirmation不得重选；7) all1152 finite；8) confirmation成功200/200，否则列失败并GATE_STOP；9)head overlap固定对照列表在结果前写manifest；10)S50与mass/enrichment分开解释。

## 竞争假设与预期特征
若bbox-row frozen heads显著优于last/random且与IPLoc main4/R-010 B→Q重合，支持跨任务共享bbox-stage localization heads；若优于controls但不重合，支持task/model-format特异bbox heads；若仍失败，说明当前非GT selection或base-Qwen RefCOCO prompt没有建立正对照。允许重合低但空间质量高、或重合高但fresh质量低的mixed结果。

## 验收条件
pilot gate明确；1000 discovery/200 confirmation完整；冻结Top5/Top10与random CI；生成head-overlap矩阵/UpSet或heatmap；至少20张预冻结confirmation可视化；给出shared / task-specific / failed-control / mixed判定。

## 依赖的 Run / 证据
R-007b GATE_PASS manifest；R-009 completed；R-006 exact row语义；R-010 summary中的B→Q rankings；R-005 frozen main4。不得与R-014c并发占用GPU。

## 观测结果摘要
Pilot gate按预注册停止：0/20 natural bbox通过pixel-coordinate parser。模型实际输出均为约0–1000的Qwen归一化坐标（例[227,342,831,945]），与prompt要求当前display pixel bounds不一致；因此未进入1000 discovery/200 confirmation，未选head。

## 局限与混杂因素
base Qwen未专门训练为bbox-only输出，parse/behavior可能成为瓶颈；RefCOCO单图表达定位不同于IPLoc双图identity binding；方法差异（R-010 score vs repo chord）需分栏；head ID重合不等于功能或因果等价；attention非因果。

## 可支持的结论
仅证明当前approved pixel-coordinate natural-prompt contract不适用于base Qwen输出格式；不能据此判断bbox-token heads的RefCOCO空间质量或与IPLoc heads重合。坐标格式改为Qwen 0–1000需新canonical run重新审核，不能在本run中静默修改parser。

## 不支持的结论 / Claim 边界
最多判断bbox-generation rows能否在Qwen RefCOCO上形成fresh GT-localizing candidate heads，以及候选ID是否与IPLoc bbox heads重合。不得声称因果共享电路、identity-selective机制或原论文复现。

## 关键指标
{"gate":"GATE_STOP","stage":"pilot","n_pilot":20,"parse_valid":0,"parse_rate":0.0,"discovery_started":false,"heads_selected":false}

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-006/runs/E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200.md; shell/06_experiments/E-006/runs/E006-R-010-outcome-stratified-allhead-discovery-sequence-split.md; /home/featurize/work/mechanism/explog/E-006/E006-R-007b-refcoco-train2014-recovery-integrity-gate-n1220/manifests/frozen_manifest.jsonl; /home/featurize/work/mechanism/explog/E-006/E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200/manifests/frozen_heads.json

## 过程记录与补充细节
（待补充）

## Run 审核
### 用户补充要求
（待补充）
### 用户疑问
（待补充）
### Agent 完善说明
（待补充）
### Agent 对疑问的回应
（待补充）
### 本次执行授权备注
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
（待补充）

### 配置/超参数
（待补充）

### Seed
20260728

### 日志路径
（待补充）

### 产物目录
（待补充）

### 真实产物根目录
（待补充）

### tmux session
（待补充）

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-006
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-009b-refcoco-natural-bbox-token-head-transfer-n1000-200
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-009b-refcoco-natural-bbox-token-head-transfer-n1000-200/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-009b-refcoco-natural-bbox-token-head-transfer-n1000-200/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-009b-refcoco-natural-bbox-token-head-transfer-n1000-200/metrics.json
- tmux_session: incontext-E-006-E006-R-009b-refcoco-natural-bbox-token-head-transfer-n1000-200
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-04T15:40:37
- updated: 2026-08-04T15:46:45

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
