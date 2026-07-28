# E005-R-016-original-order-reference-grounding-vs-query-localization-heads-n80-20 · original-order reference-grounding vs query-localization heads n80+20

- canonical_run_id: `E005-R-016-original-order-reference-grounding-vs-query-localization-heads-n80-20`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed_stage_quality

## 本轮目的
在真实prompt图像顺序和同一次forward中比较reference理解阶段与query定位阶段的heads/layers。

## 必要性 / 证据链位置
R-015交换support/target，只测试方向对称定位，不回答原始prompt中模型如何分别处理reference/query。

## 研究依据 / 被审计对象
原prompt结构为reference image→reference bbox user text→query image→assistant query bbox；两个坐标子序列可区域唯一对齐。

## 实现方式（简版）
A=reference bbox token p-1 rows→reference span；B=query bbox token p-1 rows→query span；同forward分别repo排名并冻结验证。

## 实现方式（详细版）
原始顺序不改；reference坐标匹配限制在两image spans之间，query限制在第二span之后；两阶段分别top5/top20及shared conservative排名。

## 数据身份与构造
旧开发indices0:79 discovery/80:99 validation positive。

## 数据规模
80 discovery×2 stages；20 validation×2 stages×3 sets；固定双角色图。

## 模型、权重与关键配置
Qwen3-VL+IPLoc-ID LoRA eager bf16 224。

## 变量、干预与对照
同一forward/原顺序；stage-specific p-1 rows；GT不参与ranking；all1152-head controls。

## 指标与计数规则
GT enrichment/pointing/percentile；top5/top20 exact overlap和shared双侧质量。

## 完整性门槛 / no-silent-zero
reference/query coordinate区域唯一匹配；span/grid/finite hard fail；各自GT质量门禁。

## 观测结果摘要
原始顺序同forward A-vs-C完成：reference/query frequency top5仅重合L18H15，但GT有效中层heads大量跨阶段迁移；reference top5含L10H29/L04H29伪阳性。

## 局限与混杂因素
reference bbox为teacher-forced user输入，后续bbox token可见更早bbox tokens；post-hoc；attention非因果。

## 可支持的结论
支持阶段frequency排序不同，不支持两套完全分离有效circuits；reference user-bbox grounding与query output localization均有共享中层GT-effective heads。post-hoc/non-causal。

## 不支持的结论 / Claim 边界
比较原始prompt中阶段特异attention localization signatures，不等同reference语义理解或因果identity routing。

## 关键指标
ref own median enrichment=2.728,pctl=.904,pointing=.24 vs .070；query own=7.965,.973,.27 vs .070；top5 Jaccard=.111/top20=.379；shared set双侧质量通过。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-016-original-order-reference-grounding-vs-query-localization-heads-n80-20

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r016_original_order_stage_heads.py

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-016-original-order-reference-grounding-vs-query-localization-heads-n80-20/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-016-original-order-reference-grounding-vs-query-localization-heads-n80-20/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-016-original-order-reference-grounding-vs-query-localization-heads-n80-20

### tmux session
e005_stage_heads

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-016-original-order-reference-grounding-vs-query-localization-heads-n80-20
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-016-original-order-reference-grounding-vs-query-localization-heads-n80-20/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-016-original-order-reference-grounding-vs-query-localization-heads-n80-20/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-016-original-order-reference-grounding-vs-query-localization-heads-n80-20/metrics.json
- tmux_session: e005_stage_heads
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T17:12:22
- updated: 2026-07-24T17:19:12

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
