# E003-R-010-natural-same-image-instance-binding-logit-pilot-n7 · E003-R-010-natural-same-image-instance-binding-logit-pilot-n7

- canonical_run_id: `E003-R-010-natural-same-image-instance-binding-logit-pilot-n7`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_gate_failed

## 本轮目的
在自然同图多实例positive cases中，固定reference/query，仅将assistant-prefix candidate从正确target切换到同类wrong instance，检验Yes-No margin是否执行candidate-bound identity verification。

## 必要性 / 证据链位置
公开POIL manifests的negative均为另一query image；query-level F1未显式覆盖图像含reference target但candidate落到同图distractor的冲突cell。

## 研究依据 / 被审计对象
R-006的35个IoU<0.1 positive identification TP可视化中人工初筛7例，natural generated bbox清楚覆盖同图另一同类实例；所有自然输出均为Yes且target IoU<0.1。

## 实现方式（简版）
固定原reference/query messages，将candidate作为assistant autoregressive prefix；比较target GT、自然wrong-instance框与matched background的next-token Yes/No logits。

## 实现方式（详细版）
不生成自由文本，不使用PN_interpreter；保存human selection reason、raw/pixel/VLM bbox、IoUs、prefix、token ids和逐样本margin。

## 数据身份与构造
local deterministic LaSOT reconstruction；从R-006 outcome-selected 7 cases/5 classes：cattle×2, elephant×2, person, pig, zebra；每例reference A、同sequence positive query(A+B)、target GT A、人工核验natural wrong-instance bbox B。非官方split。

## 数据规模
7 sample clusters；3 forced-candidate modes；21 records；5 classes；selection seed不适用，deterministic IDs=[22,23,42,43,93,94,138]。

## 模型、权重与关键配置
Qwen3-VL-8B-Instruct complete offline snapshot + IPLoc-ID 1-shot LoRA；max_side=640；assistant autoregressive prefix；teacher-forced one-token Yes/No logits。

## 变量、干预与对照
固定reference/query pixels与prompt；target_gt=A；wrong_instance_natural=B（R-004b自然错误框，人工核验覆盖同类非target）；background_matched_size为同尺寸角落control。主比较target_gt minus wrong_instance_natural margin；background为destructive control。

## 指标与计数规则
主指标每样本margin(Yes-No,target)-margin(Yes-No,wrong)及其bootstrap CI；四项binding accuracy：target应Yes、wrong应No；辅助candidate flip、target-vs-background、pair-normalized Yes probability。

## 完整性门槛 / no-silent-zero
Engineering PASS: 21/21, 7 per mode, finite, no traceback, formal summary and visualizations. Scientific FAIL: exact natural-prefix replay expected 7/7 Yes but observed 1/7 Yes. Run status completed_gate_failed；不得引用counterfactual scientific metrics。

## 观测结果摘要
工程完整性通过：21 records、7×3 modes、finite logits、7个人工核验wrong-instance案例和7张可视化。科学replay gate失败：R-004b这7例自然输出均为Yes，但使用其exact wrong-instance prefix截至?并正确评分leading-space Yes/No tokens后，仅1/7偏好Yes、6/7偏好No。因此target/wrong/background counterfactual margin不可作为candidate-binding证据。

## 局限与混杂因素
n7 outcome-selected、单人视觉标签、prefix exposure shift、local deterministic split；最关键是R-004b自然Yes与当前exact-prefix teacher-forced logits不一致。

## 可支持的结论
本run只确定forced-prefix评测链当前不能复现自然decision，尚不能回答同图candidate-binding。必须先对齐R-004b与当前模型snapshot/LoRA/transformers/chat tokens/image preprocessing，并通过exact-prefix replay。

## 不支持的结论 / Claim 边界
不能把1/7 binding success、target/wrong margin或全No倾向解释为verifier失效；replay gate失败优先。也不能外推官方split。

## 关键指标
{"integrity":{"records":21,"samples":7,"modes_per_sample":3,"finite_logits":true,"visualizations":7},"replay_gate":{"expected_yes":7,"observed_yes":1,"observed_no":6,"pass":false},"noninterpretable_audit_only":{"target_yes":1,"wrong_yes":1,"background_yes":0,"binding_success":1,"mean_target_minus_wrong_margin":-0.7034040179,"bootstrap95":[-2.6439732143,1.1372767857]}}

## 审核入口
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-010-natural-same-image-instance-binding-logit-pilot-n7/{config,logs,results,analysis,manifests,visualizations}

## 过程记录与补充细节
Attempts 001-003为环境/path失败；004/005为token-boundary实现无效；006为有效reserialized-prefix sensitivity；007 exact natural prefix触发replay gate failed。修正：prefix结束于?后应评分leading-space Yes=7414/No=2308；R-005e的9454/2753结果不可引用。

<details><summary>执行与复现信息</summary>

### Workspace
（待补充）

### Git commit / branch
（待补充）

### 运行命令
bash /home/featurize/work/mechanism/explog/E-003/runs/E003-R-010-natural-same-image-instance-binding-logit-pilot-n7/config/launch.sh

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-010-natural-same-image-instance-binding-logit-pilot-n7/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-010-natural-same-image-instance-binding-logit-pilot-n7

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-010-natural-same-image-instance-binding-logit-pilot-n7

### tmux session
e003_r010

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-003
- run_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-010-natural-same-image-instance-binding-logit-pilot-n7
- log_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-010-natural-same-image-instance-binding-logit-pilot-n7/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-010-natural-same-image-instance-binding-logit-pilot-n7
- metrics_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-010-natural-same-image-instance-binding-logit-pilot-n7/metrics.json
- tmux_session: e003_r010
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-21T12:02:42
- updated: 2026-07-21T13:02:31

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
