# E005-R-021-e003-screened-wrong-instance-natural-output-attention-n7 · E003 screened wrong-instance archived-natural-output attention n7

- canonical_run_id: `E005-R-021-e003-screened-wrong-instance-natural-output-attention-n7`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
failed_visualization_return_contract

## 本轮目的
分析E003-R-004b七个screening-only possible-wrong-instance accepted-low-IoU自然错误的三角色attention。

## 必要性 / 证据链位置
用户要求实际执行错误样本attention与可视化，而非仅登记plan。

## 研究依据 / 被审计对象
直接复用R-004b归档自然response、prediction与Yes；冻结R-018/R-014/R-019b heads。

## 实现方式（简版）
IDs22,23,42,43,93,94,138；archived bbox p-1、Yes p-1、GT query-object visual rows；ref|query四行统一图。

## 实现方式（详细版）
green GT/red archived prediction；224 eager attention；Yes-No next-token margin为resolution-reduced replay gate。

## 数据身份与构造
R-004b positive TP且IoU<.1；7例仅单人初筛possible wrong-instance。

## 数据规模
7 prompts/7 figures。

## 模型、权重与关键配置
Qwen3-VL+IPLoc-ID LoRA eager bf16 max_side224；源生成max_side640。

## 变量、干预与对照
冻结三组heads；不在错误集重选；归档自然文本原样teacher replay。

## 指标与计数规则
replay Yes-No margin；spatial visualization；后续可加matched-correct。

## 完整性门槛 / no-silent-zero
source role/confusion/IoU/Yes；exact regional bbox/decision token match；p-1；7/7 replay优先。

## 观测结果摘要
首样本attention已提取但保存图时object_rows_panel返回值被错误解包；无完整figure/summary。

## 局限与混杂因素
224 vs source640；筛选非确认wrong-instance；GT-conditioned retrieval；attention非因果。

## 可支持的结论
无科学结论；绘图contract错误，R-021b修复重跑。

## 不支持的结论 / Claim 边界
若replay失败仅工程诊断；通过也只描述attention signature，不确认错误类型或因果机制。

## 关键指标
completed figures=0; exit=1

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-021-e003-screened-wrong-instance-natural-output-attention-n7

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r021_e003_error_attention.py

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-021-e003-screened-wrong-instance-natural-output-attention-n7/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-021-e003-screened-wrong-instance-natural-output-attention-n7/visualizations

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-021-e003-screened-wrong-instance-natural-output-attention-n7

### tmux session
e005_e003_errors

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-021-e003-screened-wrong-instance-natural-output-attention-n7
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-021-e003-screened-wrong-instance-natural-output-attention-n7/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-021-e003-screened-wrong-instance-natural-output-attention-n7/visualizations
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-021-e003-screened-wrong-instance-natural-output-attention-n7/metrics.json
- tmux_session: e005_e003_errors
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T20:50:20
- updated: 2026-07-24T20:52:18

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
