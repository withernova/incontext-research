# E005-R-011b-coordinate-prediction-query-head-recovery-n80-20 · teacher-forced coordinate-prediction query recovery（唯一子序列对齐修复）

- canonical_run_id: `E005-R-011b-coordinate-prediction-query-head-recovery-n80-20`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
failed_metadata_index

## 本轮目的
纠正newline query，从预测gold bbox坐标tokens的前一位置attention rows发现并验证定位heads。

## 必要性 / 证据链位置
R-011因错误比较plain tokenizer与multimodal processor完整IDs而在0样本失败。

## 研究依据 / 被审计对象
修复为在视觉token展开后的processor input_ids中唯一、连续、精确匹配bbox token子序列。

## 实现方式（简版）
indices0:79 discovery；冻结repo top5频率heads；indices80:99 GT concentration/all-head control/turbo可视化。

## 实现方式（详细版）
完整teacher-forced gold answer；bbox子序列必须唯一匹配；每个坐标token使用p-1预测row并取均值；无heuristic fallback。

## 数据身份与构造
LaSOT/IPLoc-ID local deterministic positive queries；0:79/80:99。

## 数据规模
80 discovery+20 internal validation；10组turbo可视化。

## 模型、权重与关键配置
Qwen3-VL-8B+IPLoc-ID LoRA eager bf16 max_side224。

## 变量、干预与对照
repo-original selection；GT不参与head ranking；all1152 heads matched control。

## 指标与计数规则
selection frequency、GT enrichment、pointing、all-head percentile、combined map。

## 完整性门槛 / no-silent-zero
唯一bbox token子序列；p-1 alignment；双图span/grid/finite；三项quality gates。

## 观测结果摘要
唯一bbox子序列对齐和首样本前向已通过，但metadata错误地用展开后position索引plain IDs，触发IndexError。

## 局限与混杂因素
post-hoc recovery；teacher-forced；validation已暴露；非confirmatory；attention非因果。

## 可支持的结论
仅metadata索引bug；不否定coordinate-query定义。R-011c直接从coord_ids记录token文本。

## 不支持的结论 / Claim 边界
只判断坐标预测query能否恢复合理定位heads；若通过仍需新数据确认。

## 关键指标
0完成的discovery records；exit1；无selection frequency或科学输出。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-011b-coordinate-prediction-query-head-recovery-n80-20; /home/featurize/data/e002_manifests/LASOT_local_1shot_T2_n140_v2.json

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r011b_coord_query_recovery.py --disc-n80 --val20

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-011b-coordinate-prediction-query-head-recovery-n80-20/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-011b-coordinate-prediction-query-head-recovery-n80-20/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-011b-coordinate-prediction-query-head-recovery-n80-20

### tmux session
e005_coord_recovery_b

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-011b-coordinate-prediction-query-head-recovery-n80-20
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-011b-coordinate-prediction-query-head-recovery-n80-20/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-011b-coordinate-prediction-query-head-recovery-n80-20/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-011b-coordinate-prediction-query-head-recovery-n80-20/metrics.json
- tmux_session: e005_coord_recovery_b
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T16:24:43
- updated: 2026-07-24T16:26:33

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
