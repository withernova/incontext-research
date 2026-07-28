# E005-R-015-reverse-reference-target-coordinate-head-discovery-n80-20 · reverse-direction reference-target coordinate-query head discovery n80+20

- canonical_run_id: `E005-R-015-reverse-reference-target-coordinate-head-discovery-n80-20`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed_quality_gate

## 本轮目的
用对称的reference bbox预测任务，按论文/repo方法独立发现reference localization heads并与query heads比较。

## 必要性 / 证据链位置
query-derived heads在reference可视化较弱；原R-012 reference频率仍使用query bbox rows，不是reference-target localization query。

## 研究依据 / 被审计对象
prompt audit确认reference bbox作为support文本；为避免读已暴露input坐标，交换support/target并teacher-force reference bbox输出。

## 实现方式（简版）
原query image+bbox作为support，原reference image作为target；读取reference bbox token p-1 rows到target span；0:79 repo排名，80:99冻结审核。

## 实现方式（详细版）
repo-original top5/chord/ReLU(attn-2mean)/mass entropy；GT不参与发现；与R-011c query top5/top20做exact和layer overlap。

## 数据身份与构造
旧开发manifest positive indices0:79 discovery/80:99 internal validation。

## 数据规模
80 discovery+20 validation；10固定reference-target turbo图。

## 模型、权重与关键配置
Qwen3-VL+IPLoc-ID LoRA eager bf16 224。

## 变量、干预与对照
reverse方向；exact coordinate subsequence；p-1；all1152 heads matched controls。

## 指标与计数规则
GT enrichment/pointing/all-head percentile；exact head及layer top5/top20 overlap。

## 完整性门槛 / no-silent-zero
alignment/span/grid/finite hard fail；三项head quality gate。

## 观测结果摘要
reverse reference-target独立发现通过：Top5=L16H23,L18H15,L17H07,L19H03,L24H27；聚合3/3质量门禁通过；与query top5精确交集3头，但L24H27为频率伪阳性。

## 局限与混杂因素
reverse prompt非deployment方向；teacher-forced；post-hoc exposed data；attention非因果。

## 可支持的结论
reference-target存在中层L16-L19定位heads；与query真正共同有效的精确heads为L18H15,L19H03。L24H27仅frequency overlap且GT失败。post-hoc reverse teacher-forced，attention非因果。

## 不支持的结论 / Claim 边界
发现reference-target attention localization signature及与query heads重合，不证明同一因果identity circuit。

## 关键指标
aggregate median enrichment=6.089, percentile=.948, pointing=.31 vs all-head .0717, combined enrichment=3.748/pointing=.35；exact top5 overlap={L18H15,L19H03,L24H27},Jaccard=.429；top20 overlap=11,Jaccard=.379；有效逐头L16H23=5.11/.50,L18H15=9.42/.30,L17H07=6.94/.40,L19H03=9.50/.35；L24H27=.075/0。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-015-reverse-reference-target-coordinate-head-discovery-n80-20

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r015_reference_target_discovery.py

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-015-reverse-reference-target-coordinate-head-discovery-n80-20/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-015-reverse-reference-target-coordinate-head-discovery-n80-20/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-015-reverse-reference-target-coordinate-head-discovery-n80-20

### tmux session
e005_ref_target

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-015-reverse-reference-target-coordinate-head-discovery-n80-20
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-015-reverse-reference-target-coordinate-head-discovery-n80-20/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-015-reverse-reference-target-coordinate-head-discovery-n80-20/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-015-reverse-reference-target-coordinate-head-discovery-n80-20/metrics.json
- tmux_session: e005_ref_target
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T17:02:00
- updated: 2026-07-24T17:04:01

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
