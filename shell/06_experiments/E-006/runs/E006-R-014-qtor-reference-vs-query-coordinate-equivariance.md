# E006-R-014-qtor-reference-vs-query-coordinate-equivariance · QtoR reference tracking versus query-coordinate copy transform audit

- canonical_run_id: `E006-R-014-qtor-reference-vs-query-coordinate-equivariance`
- run_type: hypothesis_test
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-03T17:55:31
- approved_at: 2026-08-03T18:45:00
- execution_authorized_at: 2026-08-03T19:02:26
- execution_authorization_consumed_at: 2026-08-03T19:02:26
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
planned

## 本轮目的
直接检验同一forward中query-stage heads在reference上的Q→R注意力，是否只是把Q→Q在query图像上的归一化空间分布复制/迁移到reference，而不是跟随reference当前对象位置。交付物以E005/E006风格attention heatmap为核心。

## 必要性 / 证据链位置
R012只构建了R_t与Q_t→R几何可分的样本，并未运行模型或产生attention图，不能回答用户提出的query-head空间迁移问题。本run才是该问题的直接注意力审计。

## 研究依据 / 被审计对象
R011 held-out heads；R012 separability；R013 behavior gate。

## 实现方式（简版）
固定历史query main4 heads；对固定6 correct+6 error，在identity、REF-only与QUERY-only的HFlip/VFlip/R180条件下自然生成并teacher-force replay；每个replay从同一forward同时提取Q→R和Q→Q，直接可视化并比较Q→R、投影Q→Q、R_t和Q_t→R。BOTH仅作附录control。

## 实现方式（详细版）
Primary heads预先冻结为L18H15,L19H03,L22H00,L20H08，不从transform结果重选。attention rows为各transform条件自然输出bbox token的exact p-1 rows；若自然输出不可解析则保留失败，不用identity bbox替代。Q→R keys为current reference span，Q→Q keys为current query span，二者来自同一个teacher-forced replay forward。对每head及main4 aggregate，将target-image-conditional Q→Q map按归一化token-grid坐标投影到reference grid，和Q→R比较Pearson/Spearman、JSD、center-of-mass distance、peak displacement；同时计算Q→R在R_t、R_0、Q_t→R上的fractional target mass及S50 H/L。REF-only用于判断Q→R是否随reference对象移动；QUERY-only用于判断Q→R是否随Q→Q/query坐标移动；BOTH不承担主区分。固定可视化每sample×condition包含：reference clean/transformed+绿色R_t+洋红Q_t→R；四个per-head Q→R turbo overlays；Q→R aggregate；query clean/transformed+绿色Q_t+红色natural prediction；四个同head Q→Q overlays；Q→Q aggregate；projected-Q→Q-on-reference；Q→R减projected-Q→Q差异图。display按panel min-max，正式指标用raw conditional attention。

## 数据身份与构造
R012 confirmation fresh sequences中按sequence hash冻结6个natural localization-correct与6个localization-error；identity、REF-only H/V/R180、QUERY-only H/V/R180为primary；BOTH H/V/R180为appendix。R_t=current transformed reference GT，R_0=original reference GT，Q_t→R=current query GT按归一化坐标投影到reference。

## 数据规模
固定12 sequences；primary 12×7=84 conditions（identity+3 REF-only+3 QUERY-only）；appendix BOTH为12×3=36，合计最多120个natural generations与对应teacher replays。所有失败仍计入manifest。

## 模型、权重与关键配置
Qwen3-VL-8B-Instruct + IPLoc-ID LoRA；本地ext4 verified cache；bf16；eager attention；dual RTX4090；max_side=640最长边上限。

## 变量、干预与对照
主自变量：REF-only vs QUERY-only，HFlip/VFlip/R180；identity paired baseline。主对照：同一forward、同一head、同一bbox p-1 rows下Q→R与Q→Q。冻结historical main4，不按结果选head/transform/sample。BOTH仅equivariance appendix。

## 指标与计数规则
每head及aggregate报告：P_QR(R_t), P_QR(R_0), P_QR(Q_t→R), Δ_ref-copy=P_QR(R_t)-P_QR(Q_t→R), S50 H/L三候选；Q→R vs normalized-grid projected Q→Q的Pearson、Spearman、JSD、COM距离、peak距离；REF-only与QUERY-only位移方向；按sequence paired bootstrap B=10000。GT overlap称spatial alignment，不称activation。

## 完整性门槛 / no-silent-zero
exact bbox token match必须唯一；row p-1、两个image spans、non-square grid、merge order、finite attention全部审计；同条件Q→R/Q→Q必须来自同一forward；120 conditions完整或逐项列失败；不使用identity archived bbox冒充transform输出；不从transform数据重选head；per-head与aggregate图数、manifest数一致。

## 竞争假设与预期特征
若Q→R主要跟projected Q→Q，QUERY-only时随query/Q→Q移动且REF-only不跟R_t，支持coordinate-copy spatial signature；若REF-only跟R_t且QUERY-only仍留在R_0并与projected Q→Q分离，支持reference-tracking spatial signature；若两者兼有则mixed；CI跨0或各head不一致则inconclusive。

## 验收条件
完整交付全部H/V/R180与fixed 6+6 attention panels及raw metrics；不挑最好图。只有behavior-stable subset进入正常机制主分析，behavior-changed单列OOD diagnostic。

## 依赖的 Run / 证据
R006 alignment gate passed；R012 geometry gate passed。执行前需要R013提供每个transform的natural output；head选择不再阻塞于未授权R011，primary使用在transform前已冻结的historical query main4，R011稳定heads未来仅可作为预注册secondary。

## 观测结果摘要
（待补充）

## 局限与混杂因素
attention-derived、非因果；Q→R与Q→Q是不同target spans，map相似不等于信息被字面复制；flip可能OOD；reference tracking也不证明identity understanding；自然bbox row与行为耦合。

## 可支持的结论
只判定冻结query heads的空间签名更符合reference tracking、query-coordinate/Q→Q map copying、mixed或inconclusive，并提供直观heatmaps。

## 不支持的结论 / Claim 边界
不得表述为模型单独理解/不理解reference、identity-selective binding或因果机制；“直接迁移”只能在同forward map similarity与独立transform位移共同支持时称coordinate-copy spatial signature。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-006/followup_validity_and_equivariance_plan.md#r-014

## 过程记录与补充细节
（待补充）

## Run 审核
### 用户补充要求
（待补充）
### 用户疑问
（待补充）
### Agent 完善说明
已按用户澄清重写：R012的框图不是目标结果；目标是E005/E006式同forward Q→R/Q→Q注意力热图和独立REF-only/QUERY-only干预。冻结main4避免事后选head，加入projected Q→Q-on-reference及差异图，直接检验空间迁移假设。
### Agent 对疑问的回应
请确认：1）primary固定historical query main4；2）固定6 correct+6 error；3）identity+REF-only/QUERY-only H/V/R180为primary，BOTH仅附录；4）每个条件必须先自然生成，再以该条件输出teacher replay提取bbox p-1 attention。
### 本次执行授权备注
Retry under current explicit user request to complete R-013/R-014 after attempt-001 failed before model load/scientific records due implementation assertion selecting repeated sequence rows; attempt-001 preserved, scope unchanged, selection corrected to unique sequences.

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
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-014-qtor-reference-vs-query-coordinate-equivariance
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-014-qtor-reference-vs-query-coordinate-equivariance/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-014-qtor-reference-vs-query-coordinate-equivariance/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-014-qtor-reference-vs-query-coordinate-equivariance/metrics.json
- tmux_session: incontext-E-006-E006-R-014-qtor-reference-vs-query-coordinate-equivariance
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-03T14:54:20
- updated: 2026-08-03T19:02:26

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
