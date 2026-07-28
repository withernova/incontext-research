# E005-R-017-original-order-three-channel-reference-use-heads-n80-20 · original-order three-channel reference grounding/retrieval/query localization n80+20

- canonical_run_id: `E005-R-017-original-order-three-channel-reference-use-heads-n80-20`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_mixed_reference_retrieval_gate_failed

## 本轮目的
在原始prompt同一次forward中区分reference框绑定、预测query时回看reference、query定位三类heads。

## 必要性 / 证据链位置
仅A-vs-C无法回答模型预测query时如何使用reference；用户怀疑reference有不同heads。

## 研究依据 / 被审计对象
R-016显示频率排名不同但GT有效heads高度迁移；需加入B=query bbox rows→reference span。

## 实现方式（简版）
A=reference bbox p-1→reference；B=query bbox p-1→reference；C=query bbox p-1→query；三通道独立repo排名和全3×3交叉GT审核。

## 实现方式（详细版）
同一原始顺序forward；A/B共享reference GT，B/C共享query-output rows；每通道冻结top5，计算top5/top20 overlap。

## 数据身份与构造
旧开发0:79 discovery/80:99 validation positive。

## 数据规模
80×3 discovery；20×3×3 validation；30固定图。

## 模型、权重与关键配置
Qwen3-VL+IPLoc-ID LoRA eager bf16 224。

## 变量、干预与对照
同forward；stage/spans唯一；all1152 heads controls；GT不排名。

## 指标与计数规则
各own-channel enrichment/pointing/percentile及3×3迁移；pairwise exact overlap。

## 完整性门槛 / no-silent-zero
坐标区域唯一、span/grid/finite；三通道own quality gates。

## 观测结果摘要
原始顺序同forward三通道完成：A reference-grounding和C query-localization各自质量通过；B query-output时回看reference的repo频率Top5 GT门禁0/3失败。query-localization heads迁移到B反而有弱reference GT浓度。

## 局限与混杂因素
teacher-forced input/output bbox；post-hoc；attention非因果；B的GT浓度只说明回看reference对象区域，不证明identity信息传递。

## 可支持的结论
原prompt中reference grounding和query localization频率排名不同；repo方法无法从B直接恢复有效reference-retrieval heads。现有证据不支持一套独立且GT定位良好的reference-retrieval top5；更像共享query-localization中层heads对reference对象有较弱回看。attention非因果，不证明identity use。

## 不支持的结论 / Claim 边界
区分原始推理阶段attention signatures，不证明独立或因果circuits。

## 关键指标
A own median enr=2.728,pctl=.904,point=.24>.070；B own=.212,.084,0<.0244；C own=7.965,.973,.27>.0698。A-vs-C top5仅L18H15,J=.111；B-vs-C仅L24H27,J=.111。C-heads on B: enr=1.760,pctl=.907,point=.11>.0244但 combined point=0。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-017-original-order-three-channel-reference-use-heads-n80-20

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r017_original_order_three_channel.py

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-017-original-order-three-channel-reference-use-heads-n80-20/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-017-original-order-three-channel-reference-use-heads-n80-20/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-017-original-order-three-channel-reference-use-heads-n80-20

### tmux session
e005_three_channel

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-017-original-order-three-channel-reference-use-heads-n80-20
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-017-original-order-three-channel-reference-use-heads-n80-20/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-017-original-order-three-channel-reference-use-heads-n80-20/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-017-original-order-three-channel-reference-use-heads-n80-20/metrics.json
- tmux_session: e005_three_channel
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T17:15:55
- updated: 2026-07-24T17:19:12

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
