# E006-R-017b-refcoco-synthetic-icol-format-within-lora-head-transfer · refcoco-synthetic-icol-format-within-lora-head-transfer

- canonical_run_id: `E006-R-017b-refcoco-synthetic-icol-format-within-lora-head-transfer`
- run_type: hypothesis_test
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-04T19:30:32
- approved_at: 2026-08-04T19:38:27
- execution_authorized_at: 2026-08-04T19:38:29
- execution_authorization_consumed_at: 2026-08-04T19:38:54
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
completed

## 本轮目的
固定同一IPLoc-ID LoRA权重和同一RefCOCO样本，比较LoRA单图expression prompt与synthetic reference/query双图ICOL格式，判断prompt/双图上下文是否重排bbox-stage定位heads。

## 必要性 / 证据链位置
R017原base-only草案不能控制RefCOCO-vs-ICOL的模型权重差异。按用户反馈，新canonical run要求所有primary arms加载同一个IPLoc-ID LoRA，并加入LoRA单图control；原R017保持未执行并由本run取代。

## 研究依据 / 被审计对象
R009d/R009e为base Qwen单图RefCOCO；E005/E006 ICOL主实验为Qwen3-VL+IPLoc-ID LoRA双图prompt。官方build_messages构造reference image+label、reference bbox、query image+label。必须在LoRA内部比较才能隔离format effect。

## 实现方式（简版）
同一LoRA-loaded模型实例运行三臂：LS=单图`Locate the region described as: {expression}.`；LIE=synthetic paired-view官方ICOL格式，element=expression；LIC=同格式，element=COCO category。三臂各自自然生成、解析自然bbox、exact replay并分析bbox token p-1 rows。

## 实现方式（详细版）
模型先AutoModel加载base，再PeftModel.from_pretrained加载`/home/featurize/work/mechanism/iplocid/pretrained_weights/Qwen3-VL-8B-Instruct_1shot_iplocid`，记录active adapter、adapter config和权重hash。LIE/LIC必须调用官方vlm_build_messages.build_messages(simple mode)，不得手写近似。LS message只有query image+原prompt。

## 数据身份与构造
严格复用R007b 20/1000/200 image-disjoint manifest。每样本从同一原图构造reference目标crop和query identity/HFlip view；hash确定crop expansion/offset、query transform和轻度reference photometric参数。geometry gate要求normalized Br/Bq IoU<=.20且center distance>=.20；各split保留率<90%则停止。category必须来自冻结category_id映射，不从expression猜。

## 数据规模
Stage0 1220 geometry gate+固定20 preview。三臂各pilot20；各臂parse与exact replay均>=18/20才进入1000 discovery+200 confirmation。单臂失败不由其他臂替代，不修改prompt。

## 模型、权重与关键配置
所有primary arms同一base Qwen3-VL-8B-Instruct+IPLoc-ID 1shot LoRA，bf16 eager，max_side=640，do_sample=False,max_new_tokens=128，single RTX4090 max_memory={0:22GiB}+CPU offload；一次load顺序执行三臂。

## 变量、干预与对照
LS vs LIE：同LoRA、同expression、同sample，改变单图到双图ICOL结构（同时增加reference view+bbox，故是format bundle effect）；LIE vs LIC：仅element从expression改为category。既有base R009e仅secondary，不进入primary归因。

## 指标与计数规则
每臂行为parse/mIoU/输出类型；discovery分别冻结GT-oracle与nonGT budget×(1-entropy) Top1/3/5/10；fresh confirmation评价query-key Q→Q mass/enrichment/pointing/top10/25 support precision-recall/COM。双图臂另评价Q→R。报告LS/LIE/LIC rank Spearman、TopK Jaccard、headset cross-evaluation；secondary与R009e/main4/R010比较。

## 完整性门槛 / no-silent-zero
同一模型实例且LoRA active；LS prompt hash；LIE/LIC官方builder hash；manifest/category/transform hash；geometry先于推理；自然response不改写；bbox exact unique match及p-1；discovery/confirmation隔离；confirmation不选head；fixed first20 visualization；三臂query maps只在Q→Q同口径比较。

## 竞争假设与预期特征
LS已向ICOL pool迁移→LoRA/SFT权重是重要因素；LS与base类似但LIE/LIC迁移→双图ICOL format bundle是重要因素；LS≈LIE而LIC变化→label semantics重要；三臂接近→LoRA下bbox-stage spatial pool跨格式稳定。

## 验收条件
geometry各split>=90%；每个通过臂完成1000/200、all1152 finite、frozen TopK、cross-eval和固定20图；先报告within-LoRA结论，再报告base secondary。失败臂原样保留。

## 依赖的 Run / 证据
R007b manifest/COCO assets；官方IPLoc build_messages；IPLoc-ID LoRA；R009e/R010仅secondary comparison。审核批准与一次执行授权后方可运行。

## 观测结果摘要
Stage0 immutable geometry gate stopped before model inference: pilot valid=13/20 (.650), discovery=607/1000 (.607), confirmation=121/200 (.605), below preregistered >=.90 each split. Gate constraints were normalized Br/Bq IoU<=.20 and center distance>=.20. No model load, LoRA load, natural generation, head selection, or scientific attention result occurred.

## 局限与混杂因素
同源paired views共享像素/背景，非真实跨帧identity；LS可能对LoRA为OOD；LS→LIE同时改变图像数、reference bbox和prompt序列，不能进一步拆分；category可能退化为类别定位；attention非因果。

## 可支持的结论
当前deterministic crop+identity/HFlip candidate family无法在>=90% RefCOCO samples上同时满足严格coordinate-copy separability。不能据此判断LoRA、ICOL-format行为或head迁移。阈值未放宽、样本未替换；需新run重新设计paired-view geometry后再审核。

## 不支持的结论 / Claim 边界
仅判断固定IPLoc-ID LoRA下，RefCOCO单图expression与synthetic ICOL-format bundle是否改变bbox-stageattention heads。不得声称真实ICOL identity binding、数据集专属或因果电路。

## 关键指标
{"gate":"GATE_STOP_GEOMETRY_RETENTION_LT90","pilot_valid":13,"pilot_n":20,"discovery_valid":607,"discovery_n":1000,"confirmation_valid":121,"confirmation_n":200,"model_inference_started":false,"lora_loaded":false,"natural_generations":0}

## Artifacts
（待补充）

## 审核入口
/home/featurize/work/mechanism/iplocid/iplocid/vlm_build_messages.py; /home/featurize/work/mechanism/iplocid/pretrained_weights/Qwen3-VL-8B-Instruct_1shot_iplocid; shell/06_experiments/E-006/runs/E006-R-009e-refcoco-specific-gt-aligned-head-discovery-viz-fresh200.md; shell/06_experiments/E-006/runs/E006-R-017-refcoco-synthetic-paired-view-icol-format-head-transfer.md

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
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-017b-refcoco-synthetic-icol-format-within-lora-head-transfer
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-017b-refcoco-synthetic-icol-format-within-lora-head-transfer/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-017b-refcoco-synthetic-icol-format-within-lora-head-transfer/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-017b-refcoco-synthetic-icol-format-within-lora-head-transfer/metrics.json
- tmux_session: incontext-E-006-E006-R-017b-refcoco-synthetic-icol-format-within-lora-head-transfer
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-04T19:30:32
- updated: 2026-08-04T19:41:14

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
