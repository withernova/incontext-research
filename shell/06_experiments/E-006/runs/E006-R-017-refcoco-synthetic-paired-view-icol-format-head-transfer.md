# E006-R-017-refcoco-synthetic-paired-view-icol-format-head-transfer · refcoco-synthetic-paired-view-icol-format-head-transfer

- canonical_run_id: `E006-R-017-refcoco-synthetic-paired-view-icol-format-head-transfer`
- run_type: hypothesis_test
- review_status: pending_review
- review_round: 1
- submitted_for_review_at: 2026-08-04T19:22:20
- approved_at: 
- execution_authorized_at: 
- execution_authorization_consumed_at: 
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
planned

## 本轮目的
将同一批RefCOCO样本构造成reference-crop/query-view双图输入，并严格调用官方IPLoc build_messages形成image→label→reference bbox→query image→label格式；在控制数据不变时比较原R009d单图prompt与ICOL-format对bbox-stage定位head排名、fresh空间质量和head-set迁移的影响。

## 必要性 / 证据链位置
R009d/R009e与ICOL同时改变数据、prompt、单/双图和权重，不能解释head差异来自哪里。用户建议将RefCOCO包装成ICOL格式。本run作为synthetic paired-view bridge control，先隔离任务接口和双图上下文效应。

## 研究依据 / 被审计对象
R009d原始单图prompt自然bbox mIoU=.862；R009e在fresh200上oracle/shared/specific Top5均能强GT对齐。官方IPLoc build_messages simple mode为reference image+`<ref>{element}</ref>`、reference normalized bbox、query image+同label；IPLoc论文将该重复序列视为missing query bbox completion。RefCOCO无真实跨图同实例pair，故只能构造synthetic control。

## 实现方式（简版）
每个RefCOCO原图I和GT B生成reference view Ir与query view Iq：Ir为含目标的扩展偏移crop后resize并做确定性轻度photometric变换；Iq为完整图的identity或HFlip并同步变换B。用官方build_messages(simple mode)输入Ir、Br、Iq。Primary label arm为RefCOCO expression；secondary为COCO category（从冻结source metadata category_id映射，不可从expression猜）。

## 实现方式（详细版）
几何候选由selection_hash确定：reference crop expansion∈{1.5,1.8,2.1}，中心offset∈{±0.15 box_w,±0.15 box_h}，边界clip；query transform∈{identity,hflip}。按hash顺序选择首个满足normalized bbox IoU(Br,Bq)<=.20且center distance>=.20的组合；无组合则geometry_excluded。photometric仅reference：固定brightness/contrast/color系数∈[.85,1.15]，不使用随机运行态采样。保存变换矩阵、crop、display sizes、Br/Bq。

## 数据身份与构造
严格复用R007b image-disjoint manifest。先离线构造1220并运行geometry gate；不按模型结果筛选。模型阶段保持pilot20/discovery1000/confirmation200身份；geometry_excluded必须在执行前报告，若任一split保留率<90%则GATE_STOP并不通过放宽阈值补样本。

## 数据规模
Stage0离线1220 geometry manifest和固定20图preview。Stage1每arm pilot20自然生成。仅当parse>=18/20且exact replay>=18/20才进入该arm 1000 discovery+200 confirmation；两arm分别过gate，不以一臂替代另一臂。

## 模型、权重与关键配置
Primary base Qwen3-VL-8B-Instruct，bf16 eager，max_side=640，do_sample=False,max_new_tokens=128；不加载IPLoc LoRA，以隔离prompt/format effect。后续LoRA 2×2 extension不属于本run，需新run审批。

## 变量、干预与对照
Arm S=原R009d单图expression（复用已完成artifact，不重跑）；Arm IE=synthetic ICOL-format+expression；Arm IC=synthetic ICOL-format+COCO category。相同base model、sample identities、query view和bbox p-1定义。IE与IC唯一差异为element文本。另做reference-blank ablation只作为后续新run，本run不加入以避免扩大范围。

## 指标与计数规则
行为：parse、natural mIoU、bbox equivariance。Attention：在discovery分别冻结(1)GT-oracle Top1/3/5/10，(2)nonGT budget×(1-entropy) Top1/3/5/10；fresh confirmation评价Q→Q mass/enrichment/pointing/support precision-recall/COM。对双图另评价同bbox rows的Q→R。报告与R009e oracle/specific/shared、historical main4、R010 B→Q Top10的Jaccard/rank Spearman和cross-evaluation矩阵。

## 完整性门槛 / no-silent-zero
1必须调用官方vlm_build_messages.build_messages而非手写近似；2 apply_chat_template后的role修复/hash保存；3 source manifest和category映射hash；4所有transform由selection_hash确定；5geometry gate先于推理；6自然response原样保存且不GT replay；7bbox exact continuous unique match、row p-1；8discovery/confirmation隔离；9TopK在discovery冻结；10固定confirmation前20可视化，不挑图；11单图与双图map只能比较query keys上的Q→Q。

## 竞争假设与预期特征
若IE/IC heads均向ICOL shared/main4迁移而与S下降，支持双图ICOL格式驱动head重排；若IE≈S而IC迁移，支持label语义/表达式驱动；若IE/IC均≈S，支持bbox-stage空间pool跨格式稳定；若IC行为失败但IE成功，只能说明base Qwen依赖expression，不能否定LoRA下ICOL格式。

## 验收条件
1220 geometry manifest完整且各split>=90%；每通过arm完成1000/200、全1152 finite、冻结heads、cross-eval表和固定20套图。必须同时报告行为和attention，不允许仅因图好看挑head。若pilot/gate失败，保留为任务接口结果且不改prompt。

## 依赖的 Run / 证据
R007b manifest与COCO images；R009d/R009e artifacts；官方/home/featurize/work/mechanism/iplocid/iplocid/vlm_build_messages.py；RefCOCO source metadata category_id及COCO category mapping。执行前需审核批准和单次授权。

## 观测结果摘要
（待补充）

## 局限与混杂因素
reference/query来自同一原图，存在像素与背景相关，不能代表真实跨帧identity matching；expression arm可直接语言定位；category arm仍可能是类别定位；无negative rejection；base Qwen不是IPLoc LoRA；attention非因果；格式对齐不等于ICOL benchmark。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
只判断在固定RefCOCO图像上，将单图expression prompt改为synthetic双图ICOL message格式是否改变bbox-stage attention head ranking/空间质量。不得声称真实personalized identity binding、数据集专属电路、IPLoc SFT机制或真实ICOL性能。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-006/runs/E006-R-009d-refcoco-original-prompt-natural-output-row-audit-n20-1000-200.md; shell/06_experiments/E-006/runs/E006-R-009e-refcoco-specific-gt-aligned-head-discovery-viz-fresh200.md; /home/featurize/work/mechanism/iplocid/iplocid/vlm_build_messages.py; /home/featurize/work/mechanism/explog/E-006/E006-R-007b-refcoco-train2014-recovery-integrity-gate-n1220/manifests/frozen_manifest.jsonl

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
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-017-refcoco-synthetic-paired-view-icol-format-head-transfer
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-017-refcoco-synthetic-paired-view-icol-format-head-transfer/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-017-refcoco-synthetic-paired-view-icol-format-head-transfer/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-017-refcoco-synthetic-paired-view-icol-format-head-transfer/metrics.json
- tmux_session: incontext-E-006-E006-R-017-refcoco-synthetic-paired-view-icol-format-head-transfer
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-04T19:22:19
- updated: 2026-08-04T19:22:20

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
