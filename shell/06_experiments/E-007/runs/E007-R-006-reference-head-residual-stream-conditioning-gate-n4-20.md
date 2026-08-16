# E007-R-006-reference-head-residual-stream-conditioning-gate-n4-20 · reference-head-residual-stream-conditioning-gate-n4-20

- canonical_run_id: `E007-R-006-reference-head-residual-stream-conditioning-gate-n4-20`
- run_type: staged_causal_intervention_engineering_then_natural_pilot
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-04T23:16:57
- approved_at: 2026-08-04T23:17:51
- execution_authorized_at: 2026-08-04T23:17:53
- execution_authorization_consumed_at: 2026-08-04T23:21:54
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
draft

## 本轮目的
测试reference-grounding head从reference span读出的A@V贡献，经原o_proj映射并注入后续层query/bbox row residual后，能否同时因果改变下游query heads的Q→R与Q→Q，并在通过工程gate后评估自然bbox行为。

## 必要性 / 证据链位置
R-003b/R-003c只重写target head的Q→R probability shape，不改变query vector或Q→Q。该run实施不同的residual-stream conditioning原语，直接测试reference-head输出能否作为后续整体视觉路由的条件变量。

## 研究依据 / 被审计对象
冻结reference-grounding head含L16H23，冻结query-localization heads含L18H15/L19H03/L20H08/L22H00。R-002v证明eager attention和在线bbox window hooks可审计；现有shape-transplant自然pilot近零，不能外推否定residual-stream注入。

## 实现方式（简版）
使用单一预冻结链L16H23→layer17 input，避免多head/多层叠加归因。当前生成row在L16计算reference-bbox-only context，隔离该head slice并经原始attention o_proj回到residual维度；在进入layer17前仅对同一row做RMS-matched additive injection。先n4工程gate；仅通过后在冻结n20 positives上运行baseline、lambda0 identity、matched/mismatched/background × lambda{.1,.25,.5}。

## 实现方式（详细版）
在L16 eager attention softmax后得到A和V，仅取reference visual span中fractional bbox occupancy>0的tokens：u_t=sum_{j in B_R}A[L16,H23,t,j]V[L16,H23,j]。构造concat head tensor，仅H23 slice=u_t，其余head slice=0，经该层原始o_proj得到c_t。gate g_t=sum_{j in B_R}A[t,j]；注入layer17输入的当前最后row：xprime=x+lambda*g_t*RMS(x)/(RMS(c_t)+1e-6)*c_t。matched使用当前forward实时c_t；background使用同一head、同一row、reference图像bbox外tokens的context并以其自身mass为gate；mismatched使用预先由cyclic donor baseline自然轨迹按相对生成step缓存的bbox-only c_t/g_t，donor不足step则该case-condition硬失败，不做last-value padding。只在first-generated prediction row到在线parser首次检测有效bbox闭括号期间注入；闭括号后关闭。不得注入source output vector以外的任意新投影；这里使用的是reference head经原o_proj的隔离贡献，不是E007 shape transplant。

## 数据身份与构造
Phase A复用R-002v冻结n4；Phase B复用R-001/R-003b冻结20个sequence-unique positives（10 archived localization-error+10 correct），不得换样本。cyclic mismatched donor在启动前按冻结index排序偏移1写入manifest；GT仅用于生成后IoU与Q→Q overlap评价。

## 数据规模
Phase A：n4×5条件=20 generation（baseline、identity lambda0、matched .25、mismatched .25、background .25）并做baseline teacher replay审计。Phase B仅在A通过后：n20×11条件=220 generation（baseline、identity、matched/mismatched/background各lambda .1/.25/.5）。总上限240次自然生成；每condition独立greedy generation。

## 模型、权重与关键配置
与R-003b相同Qwen3-VL-8B-Instruct+IPLoc-ID LoRA、bf16 eager、max_side640、max_memory={0:"22GiB",cpu:"120GiB"}、官方原prompt、greedy/do_sample=False、max_new_tokens128、同processor/EOS；seed=20260805。

## 变量、干预与对照
固定source site L16H23与injection site layer17 input；固定下游audit heads L18H15,L19H03,L20H08,L22H00。变量仅source type matched/mismatched/background及lambda .1/.25/.5。baseline和lambda0 identity为controls；禁止按n4效果更换head/layer、加入多head组合或改变gate/window。

## 指标与计数规则
Phase A工程primary：注入row residual max_abs/RMS变化、hook removal recovery、identity token/logit exact、matched导致至少一个冻结downstream head的Q→R和Q→Q均发生非零变化；持久化L16 A/V/u/c、layer17 x/xprime及下游attention before/after。Phase B行为primary为matched各lambda相对baseline paired mIoU delta；secondary IoU>=.3/.5/.7、parse/Yes、rescue/partial/unchanged/newly-damaged、matched-vs-mismatched/background、下游Q→R mass和target-image-conditional Q→Q fractional-GT overlap变化。n20只报探索性paired bootstrap CI，不选最佳lambda作确认。

## 完整性门槛 / no-silent-zero
公式位置与tensor slice单元测试；identity lambda0 tokens/logits exact；hook移除恢复baseline；只有当前最后row改变且非目标rows/layer16输入不变；原o_proj权重hash不变；matched c_t确由当前row bbox内reference tokens生成；background bbox occupancy与matched不重叠；mismatched donor sequence不同且step完整；所有c/x finite、RMS比例有界并逐row记录；在线window无future bbox；240记录上限且Phase A失败则Phase B不启动。

## 竞争假设与预期特征
若工程gate通过，说明reference-head residual direction能同时改变后续Q→R/Q→Q；若matched进一步优于mismatched/background并改善自然IoU，支持有限的reference-conditioned downstream routing贡献。若只改变attention而行为null，说明计算影响不足以改善定位；若controls同样有效则不具reference内容特异性。

## 验收条件
Phase A PASS：identity logits max_abs=0、hook recovery max_abs=0（相同bf16路径）、matched residual非零、至少一个冻结downstream head同时Q→R与Q→Q max_abs>1e-7、所有完整性gate通过。Phase B科学upgrade仅当至少一个预注册lambda的matched mean paired IoU delta>0、rescue>newly-damaged，且matched点估计同时优于同lambda mismatched与background；n20不要求CI>0且不得称确认。否则记mixed/null并停止扩样。

## 依赖的 Run / 证据
独立于R-003c结果，但不得与其同GPU并行；R-003c完成后方可启动。需要本run单独人工批准和单独一次性执行授权。

## 观测结果摘要
（待补充）

## 局限与混杂因素
positive-only n20不能估计完整Identification/Joint F1；mismatched使用donor baseline trajectory而matched为实时context，控制不完全对称；显式reference bbox决定inside context，正向也可能是container routing而非identity reading；RMS注入是分布外干预。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
最多支持L16H23的reference-span projected contribution在注入layer17 residual后可因果改变冻结downstream heads整体视觉路由，并可能影响该模型该n20的自然定位；不证明identity理解、唯一/共享电路、训练可行性或泛化Joint F1改善。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
codespace/e007/runner_002v_003b.py; E007-R-002v raw A/A@V figures; E007-R-003b records; E007-R-001 frozen n20 manifest

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
20260805

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
- project_dir: /home/featurize/work/mechanism/E-007
- run_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-006-reference-head-residual-stream-conditioning-gate-n4-20
- log_file: /home/featurize/work/mechanism/explog/E-007/E007-R-006-reference-head-residual-stream-conditioning-gate-n4-20/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-006-reference-head-residual-stream-conditioning-gate-n4-20/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-007/E007-R-006-reference-head-residual-stream-conditioning-gate-n4-20/metrics.json
- tmux_session: incontext-E-007-E007-R-006-reference-head-residual-stream-conditioning-gate-n4-20
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-04T23:16:57
- updated: 2026-08-04T23:21:54

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
