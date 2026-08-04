# E006-R-016-icol-last-token-row-stage-falsification · icol-last-token-row-stage-falsification

- canonical_run_id: `E006-R-016-icol-last-token-row-stage-falsification`
- run_type: hypothesis_test
- review_status: changes_requested
- review_round: 1
- submitted_for_review_at: 2026-08-03T20:44:19
- approved_at: 
- execution_authorized_at: 
- execution_authorization_consumed_at: 
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
planned

## 本轮目的
在现有ICOL/LaSOT图像上证伪“Qwen/IPLoc-ID的last input token天然不具空间定位信息”这一过强解释，并定位空间GT信号究竟在prompt末端、bbox生成轨迹还是任务格式改变后出现。

## 必要性 / 证据链位置
R-006已经证明Qwen exact last-input-token row与generate step0完全对齐，因此当前问题不是off-by-one。旧R-010显示last-token与bbox-row的head ranking/GT质量不同，但没有用同一图像、冻结样本和prompt/task对照回答：是Qwen本身不支持last-token定位，还是IPLoc双图prompt使最后token承担全局决策而定位只在bbox自回归阶段出现。RefCOCO像素仍在下载，先用现有ICOL做不依赖外部数据的反证。

## 研究依据 / 被审计对象
E006-R-006: 10/10 exact alignment且forward/generate max abs diff=0；E006-R-005: natural bbox p-1 main4在correct样本Q→Q 4/4 support hit、error为1/4；旧R-010: correct/error top10 Jaccard T→R=1,T→Q=.429,B→R=1,B→Q=.818，提示主要可能是row/stage质量差异而非完全不同head。

## 实现方式（简版）
冻结sequence-disjoint discovery/evaluation split，在相同LaSOT query图像上比较三种prompt：A原始IPLoc双图identity prompt；B单图显式类别定位prompt；C双图reference-conditioned但将末尾改为短定位指令。每种prompt从同一teacher-replay forward提取last-input row及完整bbox生成轨迹各token的p-1 rows，对reference/query spans做全1152-head无GT发现、held-out GT评估与冻结main4正对照。

## 实现方式（详细版）
以exact multimodal token IDs标记：L=最后输入token（亦为first generated token的预测row）；O=生成opening bracket的p-1 row，按R-006定义O与L是同一row，不重复计为独立证据；X1..Xk=每个自然bbox token的p-1 row；E=closing bracket的p-1 row；D=Yes/No decision token p-1 row。连续唯一匹配失败则该条件失败，不借用identity bbox。每个row family计算完整序列image budget、target-image conditional entropy、GT fractional mass/S50/pointing；discovery只用budget×(1-entropy)，GT仅用于held-out评价。绘制layer×generation-step GT-quality轨迹和固定样本heatmap。

## 数据身份与构造
优先复用E005-R-027 unseen70的70个sequence，每sequence固定1条positive query；按sequence做49 discovery/21 evaluation，禁止row级泄漏。三种prompt使用同一query像素和GT。A保留reference image+bbox与原始IPLoc问题；B仅query image并明确类别名，属于Qwen同图空间正对照而非identity任务；C保留双图与reference bbox但以短命令要求定位matching object，属于prompt-format诊断。自然输出失败/No/parse-failed全部保留；teacher replay只使用该条件自己的自然输出，另设gold-bbox replay为诊断上限并与natural分栏。

## 数据规模
70个sequence×3 prompts；自然生成最多210次；每条件至多2次replay（natural与gold）=420 forwards。先做冻结n=10 engineering gate；通过后49/21 sequence split全量。若单GPU时长过高，按预注册顺序只保留A/B两prompt，不得看结果后删条件，且需新run变更审批。

## 模型、权重与关键配置
Qwen3-VL-8B-Instruct + IPLoc-ID 1-shot LoRA；bf16；eager attention；output_attentions=True；max_side=640；单RTX4090 48GB max_memory={0:46GiB}；all 36×32=1152 heads；冻结main4=L18H15,L19H03,L22H00,L20H08作为外部正对照，不用于重选。

## 变量、干预与对照
主要自变量：prompt/task A/B/C与row stage L/X1..Xk/E/D；配对控制相同query image、GT、processor resolution、model/LoRA。区分full-sequence image budget和target-conditional spatial alignment。natural replay与gold replay分开，避免把事后GT行解释为自然机制。

## 指标与计数规则
Primary：held-out evaluation中每stage由discovery冻结Top-k heads的query-GT S50 hit、fractional mass/enrichment、pointing与all-head percentile；画随生成token step变化的median及sequence-bootstrap CI。Secondary：reference GT同指标、image budget、entropy、correct/error分组但不为其各自重选heads。Falsification contrast：B_last−A_last、C_last−A_last、A_bbox−A_last；按sequence paired bootstrap B=10000。

## 完整性门槛 / no-silent-zero
1) R-006 exact row语义不变，明确L与generate-step0为同一row；2) 70 sequence唯一且49/21不交叉；3) prompt A/B/C使用相同query像素/GT和max_side=640；4) token连续唯一匹配，0或多匹配硬失败；5) discovery不得读取GT，evaluation不得重选head；6) natural与gold replay严格分栏；7) full-budget与conditional alignment分栏；8) 若B单图last-token也失败，不据此断言所有模型/数据都失败；9) 不把attention解释为因果。

## 竞争假设与预期特征
若B单图last-token在held-out上有空间正对照而A没有，支持IPLoc prompt/task-stage mismatch而非Qwen普遍不能last-token定位；若A从L到bbox中间token出现突增，支持定位信息在自回归bbox生成期间形成；若A的L已存在高质量GT heads，则“last token不定位”的前提被证伪，旧失败更可能来自head selection/metric；若所有prompt/rows均失败，则当前attention提取或Qwen迁移有效性仍未建立。

## 验收条件
交付完整row-stage轨迹图、三prompt配对统计、held-out冻结Top-head表、固定样本heatmaps及全部失败；明确回答premise falsified / prompt-specific / generation-emergent / unresolved四选一或mixed。

## 依赖的 Run / 证据
依赖R-006 alignment gate、现有LaSOT unseen70 manifest、R-005 frozen main4和R-010 sequence split；不依赖RefCOCO下载完成。

## 观测结果摘要
（待补充）

## 局限与混杂因素
B单图类别定位不是identity-conditioned localization；C是prompt改写可能改变行为；teacher replay与attention均非因果；自然bbox token长度不同；LaSOT目标通常显著，可能高估单图正对照；结果不能替代RefCOCO外部迁移。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
最多判断last-token失败是否为Qwen普遍性质、IPLoc prompt/task特异现象、或bbox生成阶段现象。不得声称因果head、identity-selective机制、训练改进或LocalizationHeads官方复现。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-006/result.md; shell/06_experiments/E-006/runs/E006-R-006-exact-last-token-bbox-row-alignment-gate-n10-640.md; shell/06_experiments/E-006/runs/E006-R-010-outcome-stratified-allhead-discovery-sequence-split.md; shell/06_experiments/E-006/visualizations/R-014b/

## 过程记录与补充细节
（待补充）

## Run 审核
### 用户补充要求
改 prompt 的做法并不合理，因为这样破坏了模型的 sft 训练过程
### 用户疑问
可不可以只是针对 last token 或者其他不同的 token 进行检测呢
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
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-016-icol-last-token-row-stage-falsification
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-016-icol-last-token-row-stage-falsification/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-016-icol-last-token-row-stage-falsification/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-016-icol-last-token-row-stage-falsification/metrics.json
- tmux_session: incontext-E-006-E006-R-016-icol-last-token-row-stage-falsification
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-03T20:44:18
- updated: 2026-08-04T12:53:04

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
