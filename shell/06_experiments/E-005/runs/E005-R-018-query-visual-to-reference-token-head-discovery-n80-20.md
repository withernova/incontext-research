# E005-R-018-query-visual-to-reference-token-head-discovery-n80-20 · query visual rows to reference token retrieval heads n80+20

- canonical_run_id: `E005-R-018-query-visual-to-reference-token-head-discovery-n80-20`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed_spatial_gate_no_identity_selectivity

## 本轮目的
在原始prompt中发现query视觉tokens读取reference对象区域的heads，作为reference编码/调用分析。

## 必要性 / 证据链位置
output bbox row→reference keys的repo排名失败；reference使用可能发生在visual-to-visual交互。

## 研究依据 / 被审计对象
因果顺序允许后出现的query visual rows读取先前reference keys；保持原prompt顺序。

## 实现方式（简版）
positive query-object merged rows加权平均→reference keys形成每head二维图；repo方法0:79发现；80:99 positive/negative及all/background-row controls。

## 实现方式（详细版）
discovery不使用reference GT；query-object rows由query GT定义。negative为同reference+same-class other-sequence query；全query/background rows作controls。

## 数据身份与构造
旧manifest 0:79 discovery positive；80:99 validation positive+same-class negative。

## 数据规模
80 discovery；20×2 conditions×3 row modes；1152 heads。

## 模型、权重与关键配置
Qwen3-VL+IPLoc-ID LoRA eager bf16 224 original prompt order。

## 变量、干预与对照
object/all/background query rows；positive/negative；reference GT仅validation。

## 指标与计数规则
reference GT enrichment/pointing/percentile/raw mass；positive-negative paired delta；与A/C heads overlap。

## 完整性门槛 / no-silent-zero
span/grid/row nonempty/finite；positive-object GT质量及object>background。

## 观测结果摘要
query-object visual rows→reference keys发现独立cross-image heads，4/4空间门禁通过且与A/C Top5零重合；但positive-vs-same-class-negative paired差异不稳定，不能称identity-selective。

## 局限与混杂因素
query-object rows由GT选取；post-hoc；negative不同sequence；attention非因果且不揭示编码内容。

## 可支持的结论
支持一组不同于output localization heads的object-row-conditioned cross-image reference-region retrieval signature；不支持正负身份选择性、reference内容编码类型或因果使用。

## 不支持的结论 / Claim 边界
发现cross-image reference-region retrieval signature，不等于reference identity encoding或因果使用。

## 关键指标
heads=L17H00,L07H22,L11H03,L02H05,L09H18；positive object median enr=2.768,pctl=.862,point=.25 vs all-head .085,combined enr=2.565/point=.20；positive background enr=.760/point=.04；negative object enr=2.295/point=.18；与reference-grounding/query-localization Top5 intersection均为空。L11H03单头GT失败(.404/0)。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-018-query-visual-to-reference-token-head-discovery-n80-20

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r018_cross_image_reference_retrieval.py

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-018-query-visual-to-reference-token-head-discovery-n80-20/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-018-query-visual-to-reference-token-head-discovery-n80-20/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-018-query-visual-to-reference-token-head-discovery-n80-20

### tmux session
e005_cross_image

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-018-query-visual-to-reference-token-head-discovery-n80-20
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-018-query-visual-to-reference-token-head-discovery-n80-20/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-018-query-visual-to-reference-token-head-discovery-n80-20/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-018-query-visual-to-reference-token-head-discovery-n80-20/metrics.json
- tmux_session: e005_cross_image
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T17:26:12
- updated: 2026-07-24T17:28:37

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
