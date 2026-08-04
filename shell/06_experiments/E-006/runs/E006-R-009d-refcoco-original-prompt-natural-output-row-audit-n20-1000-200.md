# E006-R-009d-refcoco-original-prompt-natural-output-row-audit-n20-1000-200 · refcoco-original-prompt-natural-output-row-audit-n20-1000-200

- canonical_run_id: `E006-R-009d-refcoco-original-prompt-natural-output-row-audit-n20-1000-200`
- run_type: hypothesis_test
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-04T17:47:36
- approved_at: 2026-08-04T17:48:24
- execution_authorized_at: 2026-08-04T17:48:30
- execution_authorization_consumed_at: 2026-08-04T17:49:08
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
completed

## 本轮目的
在RefCOCO上严格复用R-009原始prompt和chat template，不追加bbox格式/坐标指令；就事论事审计base Qwen自然输出是否产生可定义的bbox token rows。若自然bbox覆盖率达到预注册门槛，再以其p-1 rows冻结选head并与R-009 last heads、R-009c explicit-prompt heads及IPLoc B→Q heads比较；否则按任务契约不可定义停止。

## 必要性 / 证据链位置
R-009c因显式加入0–1000 bbox输出指令而成为task-format control，不能回答原始prompt下bbox-token rows。用户要求保持目前模型/原始prompt设定。R-009d用于区分：原prompt自然产生bbox-stage信号，还是bbox rows仅在额外bbox instruction后才可定义。

## 研究依据 / 被审计对象
R-009原prompt=`Locate the region described as: {expression}.`，仅last-input attention，fresh spatial control为负。R-009c显式bbox prompt下natural mIoU=.866且与R-010 B→Q Top10高重合，但存在prompt confound。R-006规定token p使用row p-1；R-009c验证normalized bbox原始response可exact replay。

## 实现方式（简版）
严格复用R-009 manifest、processor、resize(max_side=640)、base Qwen权重和user message。对每样本先保存exact last-input row，再用同一未修改prompt do_sample=False自然生成最多128 tokens。分类输出：valid normalized bbox、valid display-pixel bbox、other-four-number、non-bbox、empty；只对方括号内合法四元组建立bbox token p-1 rows，绝不追加指令、改写response或GT replay。

## 实现方式（详细版）
Frozen prompt byte string必须与R-009 runner一致：`Locate the region described as: {expression}.`；message只有image+该text；apply_chat_template(add_generation_prompt=True)完全相同。自然生成仅增加generate调用，不改输入。bbox parser先保存raw四元组：若全部0–1000且有效，按Qwen normalized解释；仅当坐标明确落在display W/H且response含pixel语义时才另标pixel，不能按更高IoU二选一。teacher replay匹配原始response首个完整合法bbox字符区间，continuous exact regional match唯一，否则失败。

## 数据身份与构造
严格复用R-007b frozen_manifest.jsonl和其20 pilot/1000 discovery/200 confirmation顺序与image-disjoint split；1220 distinct image_id。不得从R-009c response复用或筛选。GT只用于confirmation空间评价与自然behavior metadata，不用于parse类型选择或discovery head selection。

## 数据规模
Stage A pilot=20。若valid natural bbox>=18/20且exact replay>=18/20，进入1000 discovery+200 confirmation。若不满足，GATE_STOP_ORIGINAL_PROMPT_NO_BBOX_ROWS，保存全部20自然输出和类别，仅做last-row一致性核验；不得通过改prompt继续。若pilot通过但后续valid率低于95%，停止并完整报告coverage。

## 模型、权重与关键配置
base Qwen3-VL-8B-Instruct，无IPLoc LoRA；与R-009相同local model、bf16、eager attention、max_side=640、single RTX4090 max_memory={0:22GiB}+CPU offload；do_sample=False,max_new_tokens=128。

## 变量、干预与对照
唯一任务prompt为R-009原始prompt。row控制：exact last-input row；条件允许时自然bbox token p-1 row。Primary不是强制要求一定选出bbox heads，而是自然bbox-row definability/coverage。若进入head discovery，selection固定为R-010非GT budget×(1-entropy)，repo-style仅附录。

## 指标与计数规则
Stage A：valid normalized bbox rate、valid pixel bbox rate、non-bbox/other/empty rate、exact replay rate，附20条原始response。进入Stage B后：confirmation frozen Top5/10 GT mass/enrichment/pointing/S50/allhead percentile、10组layer-matched random controls、natural mIoU和bootstrap CI。Overlap固定比较R-009 Top5、R-009c Top5/10、historical main4、R-010 B→Q correct/error/mix Top10。

## 完整性门槛 / no-silent-zero
1 prompt string SHA-256与R-009逐字验证；2 model/processor/image resize与R-009一致；3 natural response原样保存；4 不追加bbox instruction；5 parser类型不按GT/IoU决策；6 pilot valid bbox及exact replay均>=18/20才可选head；7 token连续唯一匹配及p-1；8 discovery不读GT；9 confirmation不重选；10 all1152 finite；11任何gate stop都不得转用R-009c prompt。

## 竞争假设与预期特征
H1 原prompt高覆盖自然bbox且bbox-row heads优于controls→原任务下存在bbox-stage spatial candidates；H2 原prompt高覆盖但heads不优于controls→bbox输出存在但当前selection无正对照；H3 原prompt低覆盖/无bbox→bbox rows在原任务契约下不可定义，R-009c差异归因于显式bbox instruction条件；H4空间有效但head overlap低→task-specific candidates。

## 验收条件
无论通过或停止都必须保存prompt hash、20 pilot raw outputs、分类表和last-input row audit。仅当pilot gate通过才允许产生1000/200 frozen-head结果、random controls、overlap图和20 confirmation visualizations。不得把低coverage subset事后当总体。

## 依赖的 Run / 证据
R-007b manifest；R-009原始runner/prompt；R-006 row alignment；R-009c仅作prompt-format对照；R-010 rankings。当前GPU已释放，仍需审核批准及单独执行授权。

## 观测结果摘要
exit=0,GATE_PASS；原始R-009 prompt逐字复用，无bbox instruction。pilot parse/replay=20/20；discovery valid=999/1000；confirmation valid=200/200。Top5=L04H29,L14H04,L09H14,L22H04,L23H30；mass=.3002,enrichment=1.9921,pointing=.417,allhead percentile=.6874；natural mIoU=.8621。与R010 B→Q correct/error/mix Top10重合8/7/8，与historical main4 Top10重合0。

## 局限与混杂因素
原始R-009 prompt未要求结构化输出，因此自然bbox可能不可用；low coverage是任务契约结果而非模型空间能力普遍否定。RefCOCO单图不同于IPLoc双图identity binding；base Qwen不同于IPLoc LoRA；attention非因果；精确论文subset未知。

## 可支持的结论
原始短prompt下自然bbox rows可定义，显式R-009c bbox instruction不是必要条件。非GT budget×(1-entropy)候选在fresh数据上有中等空间信号且与R010 B→Q pool高度重合，但可视化不紧致、非极端all-head排名；不能据此否定存在RefCOCO-specific更强GT-aligned heads，也不能称共享因果电路。

## 不支持的结论 / Claim 边界
只判断R-009原始prompt下自然bbox token rows是否可定义，以及在预注册高覆盖前提下候选heads是否fresh GT-localizing/与既有heads重合。不得用R-009c替代、不得推广为Qwen普遍无/有空间信息、不得声称共享因果电路。

## 关键指标
{"exit_code":0,"gate":"GATE_PASS","pilot_parse":20,"pilot_exact_replay":20,"n_discovery_valid":999,"n_discovery_failed":1,"n_confirmation_valid":200,"n_confirmation_failed":0,"frozen_top5":["L04H29","L14H04","L09H14","L22H04","L23H30"],"gt_mass":0.3002157836,"enrichment":1.9921328703,"pointing":0.417,"allhead_percentile":0.6873741319,"natural_miou":0.8621494281,"r010_correct_top10_overlap":8,"r010_error_top10_overlap":7,"r010_mix_top10_overlap":8,"main4_top10_overlap":0}

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-006/runs/E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200.md; shell/06_experiments/E-006/runs/E006-R-009c-refcoco-qwen-normalized-natural-bbox-token-head-transfer-n1000-200.md; /home/featurize/work/mechanism/explog/E-006/E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200/config/runner.py; /home/featurize/work/mechanism/explog/E-006/E006-R-007b-refcoco-train2014-recovery-integrity-gate-n1220/manifests/frozen_manifest.jsonl

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
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-009d-refcoco-original-prompt-natural-output-row-audit-n20-1000-200
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-009d-refcoco-original-prompt-natural-output-row-audit-n20-1000-200/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-009d-refcoco-original-prompt-natural-output-row-audit-n20-1000-200/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-009d-refcoco-original-prompt-natural-output-row-audit-n20-1000-200/metrics.json
- tmux_session: incontext-E-006-E006-R-009d-refcoco-original-prompt-natural-output-row-audit-n20-1000-200
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-04T17:47:36
- updated: 2026-08-04T18:44:45

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
