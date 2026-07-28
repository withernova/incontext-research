# E005-R-022-correct-vs-error-natural-query-attention-matched35x2 · correct vs error natural query localization attention matched35x2

- canonical_run_id: `E005-R-022-correct-vs-error-natural-query-attention-matched35x2`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
failed_missing_manifest_before_first_forward

## 本轮目的
检验自然bbox rows的冻结query-localization heads在定位正确样本中是否比accepted-low-IoU错误样本更精准，并生成逐inference可视化。

## 必要性 / 证据链位置
验证Q-004 mismatch是否与定位成败相关，是一致性方法idea成立前的关键判别实验。

## 研究依据 / 被审计对象
E003-R-004b归档自然输出；冻结R-014 query-localization heads；不在结果上选样本/heads。

## 实现方式（简版）
35 positive TP Yes IoU<.1 errors vs 35 positive TP Yes IoU>=.7 correct；attention forward前Hungarian几何匹配；70张一inference一图。

## 实现方式（详细版）
匹配特征=reference/query log area fraction+log aspect ratio标准化L1并给予same-class固定偏好；natural bbox p-1；raw unsmoothed统计，Gaussian仅可视化。

## 数据身份与构造
本地确定性LaSOT reconstruction，非官方split；error不自动等于wrong-instance。

## 数据规模
35 matched pairs/70 prompts/70 figures。

## 模型、权重与关键配置
Qwen3-VL-8B+IPLoc-ID LoRA eager bf16 max_side224；原自然生成640。

## 变量、干预与对照
heads=L18H15,L19H03,L22H00,L20H08；correct matching冻结在attention前；seed=20260724。

## 指标与计数规则
GT enrichment/mass/pointing/peak distance；pred enrichment；candidate-lock log ratio；group median bootstrap CI；IoU-enrichment rank corr。

## 完整性门槛 / no-silent-zero
exact source Yes/bbox token regional match；p-1 alignment；70 records/figures；raw metrics finite；replay记录。

## 观测结果摘要
服务器重启后/home/featurize/data/e002_manifests路径缺失，读取manifest即FileNotFoundError；0 forward/0 figures/0 scientific records。

## 局限与混杂因素
224 replay vs 640 generation；cross-class matching可能存在；attention非因果；correct pred/GT高度重叠导致candidate-lock不独立。

## 可支持的结论
无科学结论；R-022b使用R-004b归档的同内容manifest恢复。

## 不支持的结论 / Claim 边界
只判定query attention precision与自然定位成功的相关signature；不确认wrong-instance、identity binding或因果性能作用。

## 关键指标
forwards=0; figures=0; exit=1

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-022-correct-vs-error-natural-query-attention-matched35x2

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r022_correct_vs_error_query_attention.py

### 配置/超参数
（待补充）

### Seed
20260724

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-022-correct-vs-error-natural-query-attention-matched35x2/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-022-correct-vs-error-natural-query-attention-matched35x2/visualizations

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-022-correct-vs-error-natural-query-attention-matched35x2

### tmux session
e005_query_compare

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-022-correct-vs-error-natural-query-attention-matched35x2
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-022-correct-vs-error-natural-query-attention-matched35x2/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-022-correct-vs-error-natural-query-attention-matched35x2/visualizations
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-022-correct-vs-error-natural-query-attention-matched35x2/metrics.json
- tmux_session: e005_query_compare
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-28T10:11:43
- updated: 2026-07-28T10:14:19

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
