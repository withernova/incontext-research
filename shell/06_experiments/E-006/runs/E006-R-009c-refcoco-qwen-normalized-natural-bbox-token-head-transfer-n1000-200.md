# E006-R-009c-refcoco-qwen-normalized-natural-bbox-token-head-transfer-n1000-200 · refcoco-qwen-normalized-natural-bbox-token-head-transfer-n1000-200

- canonical_run_id: `E006-R-009c-refcoco-qwen-normalized-natural-bbox-token-head-transfer-n1000-200`
- run_type: hypothesis_test
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-04T16:02:57
- approved_at: 2026-08-04T16:04:06
- execution_authorized_at: 2026-08-04T16:04:09
- execution_authorization_consumed_at: 2026-08-04T17:25:21
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
completed

## 本轮目的
修复R-009b已观测到的坐标契约不匹配：显式接受base Qwen自然输出的0–1000归一化bbox，在完全相同的RefCOCO image-disjoint 20/1000/200 manifest上，以自然bbox token p-1 rows和R-010非GT方法选head，检验fresh GT定位及其与既有IPLoc-ID bbox heads的重合。

## 必要性 / 证据链位置
R-009b的20/20输出均具有四个数，但按display-pixel parser为0/20；示例[227,342,831,945]对应Qwen原生0–1000坐标。R-009b因此没有进入选头，不能回答用户提出的bbox-token head overlap问题。R-009c只修正已定位的坐标解释，不改变自然生成、row alignment、split或主要selection metric。

## 研究依据 / 被审计对象
R-009 completed negative last-token control；R-009b GATE_STOP pilot parse=0/20且原始responses显示0–1000格式；R-006验证row p预测p+1；R-010定义bbox p-1 row和score=mean image budget×(1-mean normalized entropy)。对照固定为IPLoc main4、R-009 last-token Top5及R-010 B→Q correct/error/mix Top10。

## 实现方式（简版）
复用R-007b 1220 manifest。base Qwen3-VL自然生成仅含[x1,y1,x2,y2]；parser读取首个合法四元组并要求0<=x1<x2<=1000、0<=y1<y2<=1000，然后仅为behavior/GT评价换算display bbox=[x/1000*W,y/1000*H]。teacher replay及token exact matching始终匹配未经改写的原始natural response；每个原始bbox token p取row p-1，按bbox rows均值提取全1152 heads。

## 实现方式（详细版）
Primary prompt使用与IPLoc/Qwen原生约定一致的0–1000 normalized-coordinate措辞，do_sample=False,max_new_tokens=64。natural response不得改写、四舍五入、GT替换或重新解码成pixel token串。apply_chat_template后在assistant response字符区间提取首个完整方括号bbox对应IDs，在image span结束后连续唯一匹配；0/多匹配硬失败。保存raw normalized bbox、display bbox、display/original尺寸、scale、token positions、p-1 rows和全head矩阵。

## 数据身份与构造
严格复用R-007b frozen_manifest.jsonl及其SHA-256；pilot20、discovery1000、confirmation200，1220 distinct image_id，split overlap=0。GT RefCOCO bbox只用于confirmation evaluation及自然behavior metadata，不进入discovery selection。

## 数据规模
20 pilot gate；通过后1000 discovery+200 confirmation。最多1220 natural generations+1220 teacher replays，逐样本checkpoint。pilot要求normalized parse>=18/20且exact replay>=18/20；否则GATE_STOP。

## 模型、权重与关键配置
base Qwen3-VL-8B-Instruct，无IPLoc LoRA；bf16 eager output_attentions=True；max_side=640最长边限制；single RTX4090 24GB，max_memory={0:22GiB}并允许CPU offload；36 layers×32 heads。

## 变量、干预与对照
Primary row=natural normalized-bbox token p-1；同一teacher replay额外保存exact last-input row作为within-task control。Primary selection=R-010 non-GT budget×(1-entropy)。R-009 repo-style selection仅作预声明附录，不能根据confirmation切换primary。10组layer-matched random controls，seed=20260728。

## 指标与计数规则
Confirmation primary：frozen bbox Top5/Top10的GT fractional mass、area-normalized enrichment、S50、pointing、all-head percentile及B=10000 image bootstrap CI；与10组layer-matched random controls及R-009 last-token Top5在同bbox rows上的表现比较。Overlap：对IPLoc main4、R-009 Top5、R-010 B→Q correct/error/mix Top10分别报告Top5/Top10 intersection和Jaccard；对完整可用ranking另报Spearman。报告natural normalized parse rate、replay exact rate、natural bbox mIoU。

## 完整性门槛 / no-silent-zero
1 manifest path/hash与R-009b一致；2 pilot normalized parse及exact replay均>=18/20；3 natural response/raw normalized values原样保存；4 只将坐标转换用于几何评价，不改teacher token串；5 bbox token连续唯一匹配且p-1；6 discovery selection不读GT；7 confirmation不重选；8 all1152 finite；9 confirmation必须200/200有效，否则GATE_STOP并列失败；10 comparison heads在推理前冻结入manifest；11 S50饱和时不得单独作为成功证据。

## 竞争假设与预期特征
A: bbox rows显著优于last/random且与IPLoc/R-010重合→支持跨任务共享bbox-stage candidate pool；B: 优于controls但重合低→task/prompt-specific bbox heads；C: 不优于controls→RefCOCO正对照继续失败；D: 重合高但fresh GT差→仅ID overlap而非功能共享。所有mixed结果保留。

## 验收条件
pilot gate通过；1000 discovery与200 frozen confirmation完成；Top5/10与full rankings归档；random-control及bootstrap统计；head-overlap矩阵/heatmap或UpSet；预冻结confirmation前20张attention可视化；明确A/B/C/D判定。若gate stop则只报告失败，不扩大claim。

## 依赖的 Run / 证据
R-007b GATE_PASS manifest；R-009 completed；R-009b immutable GATE_STOP；R-006 row alignment；R-010 rankings；R-005 main4。单GPU约束：必须等当前R-014c结束后才能执行，不得并发。

## 观测结果摘要
exit=0,GATE_PASS；pilot parse/replay=20/20；1000 discovery+200 confirmation。显式normalized-bbox prompt下Top5=L04H29,L14H04,L09H14,L23H30,L22H04；mass=.3007,enrichment=2.0053,pointing=.423,allhead percentile=.6939，natural mIoU=.8657。与R010 B→Q correct/error/mix Top10分别重合8/7/8，和historical main4 Top10重合0。

## 局限与混杂因素
normalized-coordinate prompt与LocalizationHeads原LLaVA设置不同；base Qwen RefCOCO行为质量可能限制attention评价；RefCOCO单图expression grounding不同于IPLoc双图identity binding；head重合不等于功能、identity selectivity或因果共享；attention-derived非因果；作者精确RefCOCO样本IDs仍未公开。

## 可支持的结论
仅是显式0–1000 bbox输出指令下的task-format control。prompt相对R-009增加了bbox格式和坐标约束，可能激活专门的bbox-generation行为；不得解释为原始R-009 prompt、IPLoc SFT自然任务设定或共享因果电路的证据。

## 不支持的结论 / Claim 边界
最多支持Qwen自然normalized bbox生成阶段在本地image-disjoint RefCOCO split上是否产生fresh GT-localizing candidate heads及其ID overlap。不得声称原论文复现、共享因果电路、identity binding或视觉reference-content reading。

## 关键指标
{"exit_code":0,"gate":"GATE_PASS","pilot_parse":20,"pilot_exact_replay":20,"n_discovery":1000,"n_confirmation":200,"frozen_top5":["L04H29","L14H04","L09H14","L23H30","L22H04"],"gt_mass":0.3007064193,"enrichment":2.0052698536,"pointing":0.423,"allhead_percentile":0.6938932292,"natural_miou":0.8657095573,"r010_correct_top10_overlap":8,"r010_error_top10_overlap":7,"r010_mix_top10_overlap":8,"main4_top10_overlap":0,"n_visualizations":20}

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-006/runs/E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200.md; shell/06_experiments/E-006/runs/E006-R-009b-refcoco-natural-bbox-token-head-transfer-n1000-200.md; shell/06_experiments/E-006/runs/E006-R-010-outcome-stratified-allhead-discovery-sequence-split.md; /home/featurize/work/mechanism/explog/E-006/E006-R-007b-refcoco-train2014-recovery-integrity-gate-n1220/manifests/frozen_manifest.jsonl

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
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-009c-refcoco-qwen-normalized-natural-bbox-token-head-transfer-n1000-200
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-009c-refcoco-qwen-normalized-natural-bbox-token-head-transfer-n1000-200/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-009c-refcoco-qwen-normalized-natural-bbox-token-head-transfer-n1000-200/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-009c-refcoco-qwen-normalized-natural-bbox-token-head-transfer-n1000-200/metrics.json
- tmux_session: incontext-E-006-E006-R-009c-refcoco-qwen-normalized-natural-bbox-token-head-transfer-n1000-200
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-04T16:02:57
- updated: 2026-08-04T17:46:57

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
