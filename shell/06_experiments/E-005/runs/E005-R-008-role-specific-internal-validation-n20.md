# E005-R-008-role-specific-internal-validation-n20 · post-hoc role-specific internal validation n20

- canonical_run_id: `E005-R-008-role-specific-internal-validation-n20`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed

## 本轮目的
判断positive-query role-specific heads能否在未参与该选择的discovery内部20样本改善grounding。

## 必要性 / 证据链位置
R-006 overall heads失败；R-007b已用indices0:79固定role-specific heads。

## 研究依据 / 被审计对象
R-007b fixed=L02H17,L04H03,L12H21,L23H28,L21H23。

## 实现方式（简版）
在indices80:99运行固定head bbox评估；协议与R-006相同。

## 实现方式（详细版）
这是post-hoc内部recovery diagnostic，不是confirmatory held-out；100:139不复用。

## 数据身份与构造
manifest indices80:99。

## 数据规模
20 samples、40 prompts、80 span records。

## 模型、权重与关键配置
Qwen3-VL+LoRA eager bf16 224。

## 变量、干预与对照
heads冻结；不重选。

## 指标与计数规则
IoU与Recall。

## 完整性门槛 / no-silent-zero
80 records全gate通过。

## 观测结果摘要
post-hoc role-specific内部验证完成；相对R-006数值提高但绝对grounding仍弱，且negative-query同样提高。

## 局限与混杂因素
post-hoc；小n；非官方split；attention非因果。

## 可支持的结论
role-specific选择未恢复可靠定位，且对negative另一实例的attention更高；更符合通用物体/区域关注而非可靠reference-conditioned identity grounding。仅post-hoc诊断，不覆盖R-006 confirmatory负结果，也非因果证据。

## 不支持的结论 / Claim 边界
只能诊断role mixing是否可能解释R-006失败，不能成为新的confirmatory结果。

## 关键指标
positive-query mIoU=0.07452, median=0.04384, R@0.3/0.5/0.7=0/0/0；negative-query mIoU=0.08579, median=0.05870, R@0.3=0.05；80/80 gates通过。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-008-role-specific-internal-validation-n20; /home/featurize/work/mechanism/explog/E-005/runs/E005-R-007b-positive-query-role-specific-selection-n80/analysis/summary.json

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
fixed-head eval --start80 --n20

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-008-role-specific-internal-validation-n20/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-008-role-specific-internal-validation-n20/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-008-role-specific-internal-validation-n20

### tmux session
e005_internal_val

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-008-role-specific-internal-validation-n20
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-008-role-specific-internal-validation-n20/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-008-role-specific-internal-validation-n20/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-008-role-specific-internal-validation-n20/metrics.json
- tmux_session: e005_internal_val
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T15:35:37
- updated: 2026-07-24T15:37:00

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
