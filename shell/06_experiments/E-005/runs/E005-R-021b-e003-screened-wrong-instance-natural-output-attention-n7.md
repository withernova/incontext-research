# E005-R-021b-e003-screened-wrong-instance-natural-output-attention-n7 · E003 screened wrong-instance attention visualization recovery n7

- canonical_run_id: `E005-R-021b-e003-screened-wrong-instance-natural-output-attention-n7`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed_replay_gate

## 本轮目的
修正R-021绘图contract后完成7个自然错误attention图及replay gate。

## 必要性 / 证据链位置
R-021 attention后绘图失败，无完整产物。

## 研究依据 / 被审计对象
只修正object_rows_panel返回值使用；协议和heads不变。

## 实现方式（简版）
归档自然bbox/Yes p-1与GT query-object rows，7张ref|query图。

## 实现方式（详细版）
green GT/red prediction；224 replay Yes-No margin。

## 数据身份与构造
IDs22,23,42,43,93,94,138 screening-only。

## 数据规模
7 prompts。

## 模型、权重与关键配置
Qwen3-VL+LoRA eager bf16 224。

## 变量、干预与对照
冻结三组heads。

## 指标与计数规则
7/7 replay gate+visualization。

## 完整性门槛 / no-silent-zero
source/exact alignment/p-1/figure count/replay。

## 观测结果摘要
七个E003 accepted-low-IoU possible-wrong-instance初筛样本已完成归档自然输出attention重放和统一可视化；224下7/7仍偏好Yes。

## 局限与混杂因素
224 vs source640；非确认wrong-instance；non-causal。

## 可支持的结论
通过resolution-reduced replay可作为自然错误attention诊断；仍不确认wrong-instance类别，不支持因果解释；尚缺matched-correct定量比较。

## 不支持的结论 / Claim 边界
replay失败则仅诊断；通过也非因果/错误类型确认。

## 关键指标
figures=7; replay=7/7; Yes-No margins: ID22=6.875,23=5.5,42=2.0,43=1.375,93=4.875,94=8.375,138=3.875；archived IoU除93=.091外其余0。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-021b-e003-screened-wrong-instance-natural-output-attention-n7

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r021b_e003_error_attention.py

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-021b-e003-screened-wrong-instance-natural-output-attention-n7/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-021b-e003-screened-wrong-instance-natural-output-attention-n7/visualizations

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-021b-e003-screened-wrong-instance-natural-output-attention-n7

### tmux session
e005_e003_errors_b

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-021b-e003-screened-wrong-instance-natural-output-attention-n7
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-021b-e003-screened-wrong-instance-natural-output-attention-n7/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-021b-e003-screened-wrong-instance-natural-output-attention-n7/visualizations
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-021b-e003-screened-wrong-instance-natural-output-attention-n7/metrics.json
- tmux_session: e005_e003_errors_b
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T20:52:47
- updated: 2026-07-24T20:53:44

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
