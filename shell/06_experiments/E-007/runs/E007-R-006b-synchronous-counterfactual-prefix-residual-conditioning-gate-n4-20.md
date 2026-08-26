# E007-R-006b-synchronous-counterfactual-prefix-residual-conditioning-gate-n4-20 · synchronous-counterfactual-prefix-residual-conditioning-gate-n4-20

- canonical_run_id: `E007-R-006b-synchronous-counterfactual-prefix-residual-conditioning-gate-n4-20`
- run_type: recovery_staged_causal_intervention_engineering_then_natural_pilot
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-04T23:36:17
- approved_at: 2026-08-04T23:37:14
- execution_authorized_at: 2026-08-04T23:37:16
- execution_authorization_consumed_at: 2026-08-04T23:40:15
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
draft

## 本轮目的
修复R-006的mismatched donor轨迹长度缺陷：在每个target生成步，以同一target已生成prefix对matched/mismatched/background辅助分支同步计算L16H23 reference-span context，再注入主分支layer17 residual，测试后续Q→R/Q→Q与自然bbox行为。

## 必要性 / 证据链位置
R-006在任何Phase A记录产生前，于donor baseline cache step66耗尽而硬失败。自然donor轨迹长度不同使相对step缓存无法定义完整control；同步target-prefix counterfactual forward可消除cache不足和donor EOS后padding。

## 研究依据 / 被审计对象
R-006失败日志明确为donor_missing_step_66，非CUDA或核心matched公式错误。R-006实现已验证模型可加载，但未形成Phase A结果。R-003c无合格shape候选，不影响该独立residual-stream原语。

## 实现方式（简版）
改用显式逐token双分支解码。每一步先对auxiliary branch输入“其自身reference prompt + 相同target query + target截至当前的已生成token prefix”，捕获L16H23的bbox-inside/background c_t与gate；随后主分支使用原matched prompt及同prefix，在layer17当前最后row注入该c_t。主分支argmax token成为下一步，并同步追加到所有aux branches。先n4工程gate，通过后才执行冻结n20。

## 实现方式（详细版）
matched aux=原reference image+bbox；mismatched aux=冻结cyclic donor reference image+其真实prompt bbox，但保留recipient target query和任务文本结构；background aux=matched prompt但取reference视觉span中fractional bbox occupancy==0的tokens。所有aux与main在相对生成step t共享完全相同的target生成token prefix；各分支维护独立KV cache、position/cache_position和视觉prompt长度，不跨分支复制KV。aux只提供c_t,g_t，不提供token/logits/V/output vector之外信息。c_t=sum inside A*V于L16H23，隔离H23 slice后经原o_proj；main layer17注入x+lambda*g*RMS(x)/(RMS(c)+1e-6)c。主分支在有效bbox闭括号后停止注入并继续正常EOS；aux不自行生成、不以其logits停止，因此无donor EOS/padding。greedy手写decode必须先通过与model.generate的baseline token/logit逐步一致gate。

## 数据身份与构造
Phase A复用R-002v冻结n4；Phase B复用R-001冻结20 positives。mismatched donor按冻结indices cyclic +1，donor sequence必须不同；recipient target image/query不变。GT只用于生成后IoU与attention overlap。

## 数据规模
Phase 0 decode gate n2：手写cached greedy baseline vs官方generate。Phase A n4×5=20 natural generations：baseline、identity0、matched.25、mismatched.25、background.25。Phase B仅A通过：n20×11=220 generations，baseline、identity0及三source types×lambda{.1,.25,.5}。总行为generation上限242（含decode gate n2）；aux forwards不计独立行为generation但逐step审计。

## 模型、权重与关键配置
与R-006/R-003b相同模型、LoRA、bf16 eager、max_side640、22GiB+CPU offload、官方原prompt、greedy、max_new_tokens128、同EOS/processor；seed20260805。单GPU串行，禁止与其他run并发。

## 变量、干预与对照
固定L16H23→layer17 input，audit heads L18H15/L19H03/L20H08/L22H00；只变source type和lambda。baseline/identity；matched/mismatched/background。禁止依据gate结果换head/layer/lambda。

## 指标与计数规则
Phase0：baseline generated token逐步exact及selected logits max_abs（允许同一bf16路径0）。PhaseA：identity exact、hook recovery、delta residual、至少一个downstream head的Q→R和Q→Q同时变化；保存每step aux prefix hash/c/g、main x/xprime、downstream maps。PhaseB同R-006：paired mIoU delta、IoU thresholds、parse/Yes、rescue/newly-damaged、matched-vs-controls，探索性sequence bootstrap。

## 完整性门槛 / no-silent-zero
Phase0 n2 tokens exact，否则停止；每step三分支target text prefix token IDs完全相同；aux不采样、不向main复制KV/logits；donor sequence不同；branch prompt/reference/bbox hashes持久化；inside/background不重叠；原o_proj hash不变；identity tokens/logits exact；hook removal exact；仅layer17当前row改变；finite/RMS/gate审计；在线bbox window未来无泄漏；Phase0/A失败均不进入B。

## 竞争假设与预期特征
先判断同步counterfactual实现是否可靠并能让reference residual同时改变下游Q→R/Q→Q；行为上matched需优于mismatched/background才有有限reference-specific信号。null或controls等效则停止。

## 验收条件
Phase0 PASS=2/2 official-generate token exact且逐步selected-logit一致。PhaseA PASS=4/4 identity exact、hook recovery exact、matched residual非零，且每样本至少一个冻结downstream head Q→R和Q→Q max_abs>1e-7，全部prefix/hash gate通过。PhaseB exploratory upgrade=至少一个预注册lambda matched mean IoU delta>0、rescue>damage，并同时优于同lambda mismatched/background；否则mixed/null。

## 依赖的 Run / 证据
R-006保留exit1/traceback为失败attempt，不覆盖。R-006b需新的人工批准与一次性执行授权；不得沿用R-006已消费授权。

## 观测结果摘要
（待补充）

## 局限与混杂因素
双分支prompt的reference视觉token长度/绝对位置可因donor几何不同而变化；mismatched仍同时改变reference内容和bbox/container；手写decode增加工程复杂度和计算量；positive-only无法完整F1；n20仅探索。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
最多支持在相同target生成prefix条件下，counterfactual reference-head residual对后续视觉路由及该n20自然定位的有限因果影响；不证明identity semantics、唯一电路、跨数据泛化或Joint F1改善。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
E007-R-006 logs/exit.code/train.log; shell/06_experiments/_legacy/codespace/e007/runner_006.py; E007-R-002v engineering artifacts; E007-R-001 frozen manifest

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
- run_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-006b-synchronous-counterfactual-prefix-residual-conditioning-gate-n4-20
- log_file: /home/featurize/work/mechanism/explog/E-007/E007-R-006b-synchronous-counterfactual-prefix-residual-conditioning-gate-n4-20/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-006b-synchronous-counterfactual-prefix-residual-conditioning-gate-n4-20/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-007/E007-R-006b-synchronous-counterfactual-prefix-residual-conditioning-gate-n4-20/metrics.json
- tmux_session: incontext-E-007-E007-R-006b-synchronous-counterfactual-prefix-residual-conditioning-gate-n4-20
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-04T23:36:17
- updated: 2026-08-04T23:40:15

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
