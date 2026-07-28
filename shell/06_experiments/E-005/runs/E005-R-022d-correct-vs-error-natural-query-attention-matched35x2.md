# E005-R-022d-correct-vs-error-natural-query-attention-matched35x2 · R-022c summary-shadow recovery matched35x2

- canonical_run_id: `E005-R-022d-correct-vs-error-natural-query-attention-matched35x2`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_with_one_resolution_reduced_replay_failure

## 本轮目的
原协议重跑正确vs错误query attention比较并生成完整raw summary。

## 必要性 / 证据链位置
R-022c全部forward完成但summary变量遮蔽失败，raw records未持久化。

## 研究依据 / 被审计对象
唯一代码改动是bootdiff seed从被遮蔽的a.seed改为预注册常量20260724。

## 实现方式（简版）
与R-022c相同35x2 matching/heads/metrics/figures。

## 实现方式（详细版）
natural bbox p-1；raw unsmoothed statistics；70 one-inference figures。

## 数据身份与构造
R-004b archived local LaSOT reconstruction。

## 数据规模
35 pairs/70 prompts。

## 模型、权重与关键配置
persistent Qwen3-VL 10 shards+IPLoc LoRA eager bf16 224。

## 变量、干预与对照
same frozen heads/rule/seed=20260724。

## 指标与计数规则
same as R-022c。

## 完整性门槛 / no-silent-zero
70 records/figures；summary+visual manifest；finite；70/70 replay。

## 观测结果摘要
70/70 forwards与70 figures完成；summary/manifests存在。correct相对error有更高GT enrichment/mass/pointing和更低peak distance；candidate-lock error显著更高。ID70 horse error在224 replay中Yes-No margin=-0.625，故replay为69/70，不能标completed_passed_integrity。

## 局限与混杂因素
224 replay；attention non-causal；mostly cross-class matching。

## 可支持的结论
支持224 resolution-reduced archived-response replay中自然bbox localization attention precision与定位成败相关；attention非因果、mostly cross-class geometry matching、1个replay失败需全样本与exclude-ID70敏感性并列。

## 不支持的结论 / Claim 边界
association only。

## 关键指标
GT enrichment median error=1.549 correct=14.501 diff=-12.952 CI[-16.544,-9.225]; GT mass=.0174 vs .2240; pointing median=0 vs1; peak-distance=.1752 vs0; candidate-lock=2.1399 vs-.0010 diff=2.1409 CI[1.5493,2.9277]; replay=69/70; figures=70

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-022d-correct-vs-error-natural-query-attention-matched35x2

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
R022 script seed-shadow fixed

### 配置/超参数
（待补充）

### Seed
20260724

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-022d-correct-vs-error-natural-query-attention-matched35x2/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-022d-correct-vs-error-natural-query-attention-matched35x2/visualizations

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-022d-correct-vs-error-natural-query-attention-matched35x2

### tmux session
e005_query_compare_d

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-022d-correct-vs-error-natural-query-attention-matched35x2
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-022d-correct-vs-error-natural-query-attention-matched35x2/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-022d-correct-vs-error-natural-query-attention-matched35x2/visualizations
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-022d-correct-vs-error-natural-query-attention-matched35x2/metrics.json
- tmux_session: e005_query_compare_d
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-28T12:22:11
- updated: 2026-07-28T13:00:55

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
