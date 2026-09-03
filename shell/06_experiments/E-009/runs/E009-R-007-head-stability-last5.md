# E009-R-007-head-stability-last5 · 训练后段最后五个 checkpoint 的单 Run head 稳定性核验

- workflow: v2 / awaiting_review / 等待审核
- review_status: pending_review
- group_id: 未分组
- execution_dispatch:  / 

## 1. 研究设计
### 研究问题
同一父训练轨迹最后五个保留 checkpoint（step 1400、1482、1564、1646、1729）在固定验证样本上的 query/reference Top-3 与 Top-5 attention head 集合是否稳定？
### 本轮目的
在一个 Run 内按训练顺序依次筛选五个 checkpoint；使用原 val100 中经审计保留的 96 条正面积样本，并在同一日志和产物根记录每次 heads 与最终稳定性。
### 假设或比较预期
若训练后段形成稳定的 attention head 排序，则相邻 checkpoint 的 query/reference Top-3 与 Top-5 应有较高 Jaccard，且部分 heads 在五个 checkpoint 中持续出现；否则集合会持续替换。
### 数据与主要变量
/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-real-focus-data/manifests/val_lasot_posthoc_valid96_1shot_focus.json；由原 fixed100 保序删除 source indices 40、41、58、61 得到，不补入新 sequence。audit=val_lasot_posthoc_valid96_1shot_focus.audit.json，output SHA-256=7c27581bd6e960e7933523cdeba7991e693e2078b1122dc5c8cfb1132d65cf47。

suite 内唯一变化是 parent checkpoint。valid96 样本身份/顺序、seed=20260901、row contract、excluded layers、Top-k、finder reward、artifact dtype 和代码快照固定；不补替代样本。

## 2. 指标设计
主输出为五个 checkpoint 在同一 valid96 上的固定 Top-3/Top-5 集合和稳定性汇总；attempt-001 的 96 个部分 records 因整轮 gate failed 不进入分析。
## 3. 代码架构
复用现有 checkpoint loader、HeadScreeningHook、probe/finder 和离线 analyzer；新增一个公共 suite CLI 与薄 shell launcher。一个 torchrun 管理五个顺序 screen，产物集中在 E009-R-007-head-stability-last5 下。
- 公共包：`.`
- 入口：``
- 配置：`configs/sft/e009_qwen3vl8b_1shot_branch.py`
- Shell launcher：`tools/run/run_e009_head_stability_suite.sh`
- 复用模块：iploc_szy/checkpointing.py, iploc_szy/head_screening/hooks.py, iploc_szy/head_screening/probes.py, iploc_szy/head_screening/finders.py, tools/analyze_head_stability.py
- 新增模块：tools/screen_head_stability_suite.py, tools/run/run_e009_head_stability_suite.sh, tools/filter_e009_valid_bbox_manifest.py
- 测试：tests/test_filter_e009_valid_bbox_manifest.py, tests/test_head_stability_suite.py, tests/test_analyze_head_stability.py, tests/test_branching.py, tests/test_head_screening.py

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `bash tools/run/run_e009_head_stability_suite.sh`
- commit: ``
- workspace: 02
- tmux: incontext-E-009-E009-R-007-head-stability-last5
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-R-007-head-stability-last5/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-R-007-head-stability-last5
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
有效结果来自 attempt-002-valid96；attempt-001 因零面积 bbox gate failed，不进入分析。Query Top-5 频次：L21H10=5/5，L17H04=5/5，L17H07=4/5，L24H16=4/5，L18H15=3/5（连续出现在最后三个 checkpoint），L20H15=3/5，L17H25=1/5；相邻集合平均 Jaccard=0.6667。Reference Top-5 频次：L20H15=5/5，L20H20=4/5，L14H23=4/5，L18H05=2/5，其余各 1/5；相邻集合平均 Jaccard=0.2946。Reference 最后两个 checkpoint 的 Top-3 集合均为 {L20H15,L20H20,L14H23}。用户据此明确选择后续实验 head：Query Top-5 为 [L21H10,L17H04,L17H07,L24H16,L18H15]；Reference Top-3 为 [L20H15,L20H20,L14H23]。这是基于固定 valid96、同一训练轨迹末五个 checkpoint 的描述性筛选决策，不代表因果重要性、跨 seed 稳定性或测试集泛化。

## 简短局限
只覆盖原 val100 中 96 条有正面积框的样本，四个无效框 sequence 被排除且未替换；结果不代表完整 val100。teacher-forced attention 非因果，reference T003 使用 GT，不能外推预留测试集。

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "单个 checkpoint 不能判断 head 是否稳定；五条独立 Run 又会分散日志、授权和汇总。一个顺序 suite 可在保持每个 checkpoint 独立子产物的同时，形成唯一审核、执行与结论单元。",
  "evidence_basis": "attempt-001 在 step1400 收集 96 条后因 source indices 40、41、58、61 的 query bbox 为零面积而 gate failed；无科学 head 输出。valid96 audit 固定删除这四条且不补样本，剩余 96 条归一化后 query/reference 框全部为正面积。当前没有 Solid Run。",
  "implementation_summary": "单次 torchrun 加载一次模型，按 step1400→1482→1564→1646→1729 依次替换 adapter；每次在同一 valid96 manifest 上 screening。失败的 attempt-001 原样保留，修订输出写入 attempt-002-valid96。",
  "implementation_details": "新增 filter_e009_valid_bbox_manifest.py 生成不可覆盖的 valid96 manifest/audit，记录 source/output SHA-256 和 dropped indices。suite 每完成一个 checkpoint 仍打印完整 query/reference Top-3/Top-5；attempt-002 独立目录避免覆盖失败产物。",
  "model_config": "Qwen3-VL-8B-Instruct + 同一父训练轨迹的五个 NF4 LoRA adapters；4 GPU torchrun。模型构建一次，五次只替换 adapter；正常模型保持 SDPA，每个 probe forward 临时切 eager attention。",
  "metric_definition": "每 checkpoint 记录 query/reference Top-3/Top-5 与 96 条 probe records；跨 checkpoint 报告相邻 Jaccard、相对首 checkpoint exact-match fraction、五 checkpoint 交集/并集及逐 head 出现频率。",
  "integrity_gates": "valid96 audit 必须 source_rows=100、output_rows=96、dropped=[40,41,58,61] 且所有归一化 query/reference 框正面积；每个 screen 必须 status=completed、records=96、failures 为空并打印四组 heads。汇总前五次样本身份、schema、row contract、head shape、finder 参数和 Top-k 必须完全一致。",
  "expected_outcome": "总日志按 step 列出五次 query/reference Top-3/Top-5，每次 records=96，并生成一个跨 checkpoint 稳定性 summary。",
  "acceptance_criteria": "五个 checkpoint 均完成 96/96 records；总日志含五条 HEAD_STABILITY_CHECKPOINT 和四条 HEAD_STABILITY_AGGREGATE；attempt-002 suite_manifest 为 completed，summary 通过 comparability gate。",
  "claim_boundary": "只允许判断最后五个 checkpoint 在固定 valid96 manifest 上的 attention head 集合稳定性；不得把 attempt-001 部分 records 当结果，不得声称完整 val100、测试集或因果 head 稳定。",
  "artifacts": "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-R-007-head-stability-last5/attempt-002-valid96/suite_manifest.json; /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-R-007-head-stability-last5/attempt-002-valid96/head_stability_summary.json",
  "audit_paths": "configs/sft/e009_qwen3vl8b_1shot_branch.py; tools/filter_e009_valid_bbox_manifest.py; tests/test_filter_e009_valid_bbox_manifest.py; val_lasot_posthoc_valid96_1shot_focus.audit.json; tools/screen_head_stability_suite.py; tools/analyze_head_stability.py; attempt-002-valid96/suite_manifest.json; attempt-002-valid96/head_stability_summary.json"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
