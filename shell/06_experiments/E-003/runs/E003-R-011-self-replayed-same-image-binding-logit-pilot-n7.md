# E003-R-011-self-replayed-same-image-binding-logit-pilot-n7 · E003-R-011-self-replayed-same-image-binding-logit-pilot-n7

- canonical_run_id: `E003-R-011-self-replayed-same-image-binding-logit-pilot-n7`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
aborted

## 本轮目的
在同一次模型加载中先重做自然generation并保存decision-step logits/token IDs，再验证exact-prefix teacher-forced replay，gate通过后才比较target/wrong/background candidates。

## 必要性 / 证据链位置
R-010无法复现历史R-004b自然Yes；必须消除跨run模型/环境差异并证明generation-to-replay一致性，才能科学解释candidate counterfactual。

## 研究依据 / 被审计对象
R-010工程完整但exact historical prefix replay仅1/7 Yes；R-005e另有decision token boundary错误。R-011改为same-load self-replay。

## 实现方式（简版）
（待补充）

## 实现方式（详细版）
（待补充）

## 数据身份与构造
沿用7个人工核验自然同图wrong-instance案例 IDs=[22,23,42,43,93,94,138]；local deterministic LaSOT reconstruction，非官方split。

## 数据规模
7 sample clusters；每例1次自然generation、1次exact-prefix replay、3个candidate modes；counterfactual结果仅在逐例replay与natural-case eligibility gate通过时纳入。

## 模型、权重与关键配置
Qwen3-VL-8B-Instruct offline snapshot + IPLoc-ID 1-shot LoRA；torch2.2.2/transformers4.57.3/peft0.18.0；max_side640；greedy generation。

## 变量、干预与对照
同一次load固定messages/images；自然generate保存tokens/scores；exact token-prefix replay；target_gt、wrong_instance_natural、background_matched_size。

## 指标与计数规则
首要gate：generation decision和replay decision一致、Yes-No margin差在容差内、prefix token IDs精确一致；其次为eligible样本target-minus-wrong margin与binding success。

## 完整性门槛 / no-silent-zero
FAILED before scientific records；保存traceback。

## 观测结果摘要
attempt-001在任何scientific record前失败：return_dict_in_generate sequence按multimodal processor input length错误trim，解码乱码且找不到Yes/No token。研究设计复核后，单reference target/wrong/background路线废弃，不再重试。

## 局限与混杂因素
实现错误；且原单向背景设计已被双向reference-switch四格替代。

## 可支持的结论
仅记录实现失败；不支持任何candidate-binding结论。

## 不支持的结论 / Claim 边界
不得把乱码或missing token解释为模型行为。

## 关键指标
{"scientific_records":0,"attempts":1,"traceback":true}

## 审核入口
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-011-self-replayed-same-image-binding-logit-pilot-n7/{config,logs,results,analysis,manifests,visualizations}

## 过程记录与补充细节
User review removed background candidate entirely. Future main experiment: real ref A/B × candidate A/B, no background. R-011 preserved as aborted historical run.

<details><summary>执行与复现信息</summary>

### Workspace
（待补充）

### Git commit / branch
（待补充）

### 运行命令
bash /home/featurize/work/mechanism/explog/E-003/runs/E003-R-011-self-replayed-same-image-binding-logit-pilot-n7/config/launch.sh

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-011-self-replayed-same-image-binding-logit-pilot-n7/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-011-self-replayed-same-image-binding-logit-pilot-n7

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-011-self-replayed-same-image-binding-logit-pilot-n7

### tmux session
e003_r011

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-003
- run_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-011-self-replayed-same-image-binding-logit-pilot-n7
- log_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-011-self-replayed-same-image-binding-logit-pilot-n7/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-011-self-replayed-same-image-binding-logit-pilot-n7
- metrics_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-011-self-replayed-same-image-binding-logit-pilot-n7/metrics.json
- tmux_session: e003_r011
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-21T13:14:44
- updated: 2026-07-21T13:40:20

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
