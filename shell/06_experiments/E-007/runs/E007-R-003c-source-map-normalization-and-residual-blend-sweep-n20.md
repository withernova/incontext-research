# E007-R-003c-source-map-normalization-and-residual-blend-sweep-n20 · source-map-normalization-and-residual-blend-sweep-n20

- canonical_run_id: `E007-R-003c-source-map-normalization-and-residual-blend-sweep-n20`
- run_type: post_null_algorithm_screening
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-04T22:44:35
- approved_at: 2026-08-04T22:45:59
- execution_authorized_at: 2026-08-04T22:46:01
- execution_authorization_consumed_at: 2026-08-04T22:48:22
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
draft

## 本轮目的
在已冻结n20 positives上系统比较source-map聚合、温度归一化、稀疏化及partial residual transplant，检验R-003b近零结果是否由“逐source-head L1后算术平均 + 100% shape replacement”过强或不合适造成。

## 必要性 / 证据链位置
R-003b证明现有rewrite可执行但matched mIoU较baseline低0.00173、无rescue；该结果只否定当前单一归一化/全替换方案，不穷尽更平滑、置信度加权或head-preserving的植入。先在旧n20作明确标注的算法筛选，可避免直接在fresh大样本上任意试参。

## 研究依据 / 被审计对象
继承R-002v工程gate与R-003b完整160次自然生成；现有source aggregate先对各source head/row做L1再平均，target reference shape被100%替换，可能抹除target自身有用结构。

## 实现方式（简版）
复用R-001冻结10 error+10 correct，但重新prompt-forward保存未归一化source attention。对每个样本独立自然生成baseline、identity、当前full-L1，以及预注册的聚合/温度/稀疏/残差变体和三类controls。该run只做旧样本算法screening；可选winner必须按固定规则自动产生，不能人工看图挑参。

## 实现方式（详细版）
所有变体仍位于decoder eager attention softmax后/dropout前/A@V前；只改Q→R reference-span，保留target V。source maps：A=current arithmetic mean of per-head L1 maps；B=raw-mass-weighted（先对所有source head×bbox-row raw attention求和再一次L1）；C=entropy-confidence-weighted per-head maps，w=max(0,1-H/logN)，权重全0则GATE_STOP；D=geometric opinion pool exp(mean(log(S+1e-8)))后L1；E/F=对A作temperature power gamma=.5/2后L1；G=top25%-mass sparse（保留达到累计质量.25的最少tokens后L1，ties按token index）；H/I/J=target-source residual shape (1-lambda)T+lambda*A，lambda=.25/.5/.75，T为当前row/head自身conditional Q→R shape。full条件lambda=1。每步alpha保持不变、非R不变；bbox闭括号后关闭。controls=R180(A)、cyclic mismatched(A)、uniform_bbox。条件顺序按sample hash循环旋转。

## 数据身份与构造
严格复用R-001冻结20个sequence-unique positives及分层，GT仅作生成后IoU评价；不得换样本。每个source map必须仅由该样本prompt-stage reference bbox p-1 rows生成。

## 数据规模
n=20 positives；14 conditions=280次独立greedy generation：baseline、identity、A current、B raw-weighted、C entropy-weighted、D geometric、E gamma.5、F gamma2、G top25mass、H/I/J residual lambda .25/.5/.75、R180、mismatched、uniform_bbox（实际共15 conditions=300；以conditions.json机器清单为准且启动前冻结）。

## 模型、权重与关键配置
与R-003b完全一致：Qwen3-VL-8B-Instruct+同一IPLoc-ID LoRA，bf16 eager，max_side640，max_memory={0:"22GiB",cpu:"120GiB"}，官方原prompt，greedy/do_sample=False，max_new_tokens128，同processor/EOS。seed=20260805。

## 变量、干预与对照
算法family只改变source probability construction或source/target residual mixing；主对照baseline/identity/current-A；特异性controls R180、mismatched、uniform_bbox。禁止同时改变heads、window、prompt、alpha budget或V。

## 指标与计数规则
每condition报告parse、Yes、mIoU/median IoU、IoU>=.3/.5/.7、paired delta vs baseline、rescue/newly-broken；按error/correct strata分别报告。自动筛选score采用冻结字典序：(1) rescue@.3-newly_broken最大；(2) mean paired delta IoU最大；(3) median delta最大；(4) condition名。另报对R180/mismatched/uniform_bbox差值。筛选score只用于提出候选，不作科学显著性。

## 完整性门槛 / no-silent-zero
baseline/identity 20/20 token exact；15-condition清单与run id一一对应；300条或显式失败；每rewrite命中且finite；shape-only mass与row-sum误差<=5e-5；所有分布sum=1/nonnegative；raw/normalized maps与公式参数持久化；online parser无future token；无GT/归档bbox借用。任何实现失败保留attempt并停止。

## 竞争假设与预期特征
若partial residual或替代aggregate优于current，说明原null可能部分来自植入强度/归一化选择；若所有变体仍近零且controls相当，则进一步支持该source-map family缺乏自然行为作用。

## 验收条件
这是算法筛选而非确认。最多冻结Top-3候选进入fresh run；候选资格要求相对baseline mean delta>0、rescue@.3>newly-broken、parse/Yes各下降<=1，并且不劣于current-A。若不足3个，仅带入合格者；若0个，后续大run仍可作为经人工批准的null mapping audit，但不得称winner confirmation。

## 依赖的 Run / 证据
R-002v工程通过；R-003b完整性通过且科学upgrade失败。该run需单独审核与一次性执行授权。

## 观测结果摘要
（待补充）

## 局限与混杂因素
在已观察过行为的旧n20上多方案调参，严重探索性且有选择偏差；positive-only，不能计算完整F1；不能把best point estimate当新证据。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
最多用于选择预注册mapping候选并判断当前full-L1是否明显过强；不支持泛化改善、完整Joint F1、identity理解或唯一电路。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
E007-R-001 source artifacts; E007-R-002v raw A/A@V; E007-R-003b records/summary; shell/06_experiments/_legacy/codespace/e007/runner_002v_003b.py

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
- run_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-003c-source-map-normalization-and-residual-blend-sweep-n20
- log_file: /home/featurize/work/mechanism/explog/E-007/E007-R-003c-source-map-normalization-and-residual-blend-sweep-n20/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-003c-source-map-normalization-and-residual-blend-sweep-n20/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-007/E007-R-003c-source-map-normalization-and-residual-blend-sweep-n20/metrics.json
- tmux_session: incontext-E-007-E007-R-003c-source-map-normalization-and-residual-blend-sweep-n20
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-04T22:44:35
- updated: 2026-08-04T22:48:22

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
