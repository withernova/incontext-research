# E005-R-010b-turbo-visualization-and-query-token-audit-n10 · R-010可视化配色修正与query-token审计

- canonical_run_id: `E005-R-010b-turbo-visualization-and-query-token-audit-n10`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed

## 本轮目的
按用户审核意见将attention图改为蓝低红高的turbo渐变，并确认系统性边缘关注是否源自错误query token。

## 必要性 / 证据链位置
旧图自制绿色配色不利于判读；全部边缘模式提示query位置可能错误。

## 研究依据 / 被审计对象
token审计显示last input token=id198 newline，位于im_start assistant之后。

## 实现方式（简版）
固定indices100:109和同一冻结top5重新前向并输出turbo heatmaps；归档query/span/grid-order审计。

## 实现方式（详细版）
每图每head独立min-max显示；蓝低、青黄中、红高；绿色GT；不改变科学metric。

## 数据身份与构造
indices100:109 positive query，固定非结果挑选。

## 数据规模
10 samples，60 panels。

## 模型、权重与关键配置
Qwen3-VL+LoRA eager bf16 224；last newline query，仅复现诊断。

## 变量、干预与对照
heads/样本/GT与R-010一致，仅更换colormap。

## 指标与计数规则
沿用R-010 GT concentration；本run主输出为可视化与query token provenance。

## 完整性门槛 / no-silent-zero
10图输出；span/grid/finite通过；query token明确解码。

## 观测结果摘要
query token审计和turbo重绘完成；确认旧query是assistant generation-prompt后的newline token，10组蓝低红高热图已生成。

## 局限与混杂因素
per-panel minmax用于看空间峰值，不用于跨head比较绝对attention；旧query已知不具决策语义。

## 可支持的结论
系统性边缘attention最可能来自选择了格式newline query；尚不能将其解释为模型定位机制。span与row-major grid reshape暂无错误证据。

## 不支持的结论 / Claim 边界
该run用于证明旧边缘图来自newline-query流程并改善人工审核，不把它当新head发现。

## 关键指标
query id=198 decoded newline；image role/span/grid-order gates通过；10 images/60 panels；重绘科学metric与R-010一致且quality gate失败。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-010b-turbo-visualization-and-query-token-audit-n10

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r010b_turbo.py --start100 --n10

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-010b-turbo-visualization-and-query-token-audit-n10/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-010b-turbo-visualization-and-query-token-audit-n10/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-010b-turbo-visualization-and-query-token-audit-n10

### tmux session
e005_turbo_viz

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-010b-turbo-visualization-and-query-token-audit-n10
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-010b-turbo-visualization-and-query-token-audit-n10/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-010b-turbo-visualization-and-query-token-audit-n10/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-010b-turbo-visualization-and-query-token-audit-n10/metrics.json
- tmux_session: e005_turbo_viz
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T16:11:17
- updated: 2026-07-24T16:12:53

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
