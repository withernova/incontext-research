# E010-R-007-outcome-stratified-reference-query-head-core30-pointing-audit · 答对/答错分层的Reference与Query head前30%核心token命中统计

- workflow: v2 / analysis_pending / 结果分析
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-1e7a58d6828405681174dbc1 / completed

## 1. 研究设计
### 研究问题
在冻结 reference/query heads 的 R→R、Q→Q、Q→R 注意力图中，correct/error 的差异在完整 S30 token-grid IoU、S30 最大 4-邻域连通块 IoU 与最大块命中率上是否仍存在；最大 attention 连通块是否真正覆盖对应 GT，而不是仅由零散 token 接触造成 Core30Hit？
### 本轮目的
在保持 R-003/R-006 canonical frozen head sets、140 条既有自然 attention artifacts、自然 outcome 与三种 R→R/Q→Q/Q→R 读出不变的前提下，扩展离线空间评价，避免 Core30Hit 的“任意一个零散 token 接触 GT”饱和。新增完整 S30 与最大 4-邻域连通块的 binary token-grid IoU 及 hit，并以逐图字段和固定图直接审计主 attention 块是否覆盖 GT。
### 假设或比较预期
相比现有任一 S30 token 与 GT 相交的宽松 Core30Hit，最大 4-邻域块的 IoU/Hit 将更严格地惩罚零散小岛与宽支持集；Q→Q 的 correct/error 差异可能更清楚、减弱、消失或反向，R→R/Q→R 也完整报告。所有方向均可接受，新增指标不参与 head、样本、阈值或 outcome 重选。
### 数据与主要变量
只读复用 R-003/R-006 所核验的 R-001 140 条 natural positive attention artifacts、自然 response/IoU 标签、Reference/Query grids 与 fractional GT occupancy；不生成、不 teacher-force、不改自然判定。correct=positive 且 IoU≥0.7，error=positive 且 IoU<0.1；IoU∈[0.1,0.7)、nonpositive、缺失/不可解析均显式单列，绝不混入 correct/error。同步报告全140与 R-003 frozen 70 条 selection-held-out 子集。

冻结 R-003 actual Query heads：Top3 L20H15/L24H16/L25H10，Top5 加 L15H13/L21H10；冻结 R-006 actual Reference heads：Top3 L18H05/L20H12/L20H15，Top5 加 L20H08/L14H02。沿用同一自然 Query-bbox p−1 rows、同一 q_to_q/q_to_r arrays、同一 R→R/Q→Q/Q→R role→GT pairing、同一 outcome cutoffs、同一 all/heldout split、同一等权归一化 ensemble。运行前仍精确断言 R-003/R-006 summary SHA-256 和完整名单；绝不加载模型、重跑 generation、teacher-force、重选 heads/样本或改 S30=30% token-count 定义。

## 2. 指标设计
每 map 取 k=ceil(0.30×visual-token-count) 个 S30 token，按 attention 降序并以 flattened token index stable tie-break；G 为 occupancy>0 的二值 GT token mask。保留宽松 Core30Hit=1[S30∩G非空] 与 Top3/Top5 每图 hit-head count、any-hit、majority-hit。新增完整 S30 binary token-grid IoU=|S30∩G|/|S30∪G|。将 S30 以上下左右 4-邻接划分连通块，Cmax 为 token 数最大的块；并列时取块内最小 flattened token index 最小者。新增 Largest4NHit=1[Cmax∩G非空] 与 Largest4NIoU=|Cmax∩G|/|Cmax∪G|。逐图记录 S30/GT/Cmax sizes、S30/Cmax intersection 与 union token counts、IoUs；按 role×all/heldout×correct/error×单head/Top3/Top5 报 n、Core30Hit/Largest4NHit hits/rate，以及 S30IoU/Largest4NIoU mean、median、q25、q75。汇总图标注分母/命中；fixed panels 显示白=S30、橙=Cmax、绿=G。按 sequence bootstrap 输出 correct−error 差异的 95% CI；binary token-grid IoU 不等同像素IoU、fractional occupancy 或 strict argmax pointing。
## 3. 代码架构
最小扩展既有 mechanism/iplocid 的 outcome_stratified_core30 离线 pipeline：实现可单测的 4-邻域 connected-components 与确定性最大块选择；在单 head 与 ensemble map 处产生 S30/GT 的二值 token-grid overlap/union/IoU 和最大块字段；扩展 JSONL、summary aggregation、metrics、overview 和 fixed-case panels。固定图仍显示 attention heatmap，白色轮廓=S30、橙色轮廓=Cmax、绿色轮廓=G，并显示 S30IoU/Largest4NIoU、hit、token counts。只读复用 artifacts/occupancy，不修改 R-001/R-003/R-006，不复制或调用模型 runner。
- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `cd /defaultShare/archive/liuwenchu/projects/IPLoc && bash mechanism/iplocid/tools/run_e010_r007.sh`
- commit: `a5ba066`
- workspace: 02
- tmux: incontext-E-010-E010-R-007-outcome-stratified-reference-query-head-core30-pointing-audit
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-007-outcome-stratified-reference-query-head-core30-pointing-audit/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-007-outcome-stratified-reference-query-head-core30-pointing-audit/outputs
- Steward 摘要：```json
{
  "execution_completed_at": "2026-08-29T19:49:39",
  "evidence": {
    "log": "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-007-outcome-stratified-reference-query-head-core30-pointing-audit/logs/train.log",
    "artifact": "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-007-outcome-stratified-reference-query-head-core30-pointing-audit/metrics.json",
    "result_message": "managed execution exited 0; metrics parsed; human analysis required"
  },
  "note": "程序已结束，等待科研结果分析"
}
```

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
Managed execution exited successfully with 0 declared and 12 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

## 简短局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "R-003澄清了query/reference head的定义，R-006与用户选定T-003给出了可保留的GT监督reference固定名单，但现有结果没有用统一的30% token支持集，在自然预测正确与错误两组中分别报告逐head、逐图覆盖计数。缺少这张交叉表就无法判断总体效果是否主要由答对图片或少数head贡献。",
  "evidence_basis": "唯一冻结head authority为实际完成的上游summary：R-003 query Top3=L20H15,L24H16,L25H10；Top5加L15H13,L21H10。R-006 reference Top3=L18H05,L20H12,L20H15；Top5加L20H08,L14H02。此前R-007使用的reference集合错误，其结果无效。",
  "implementation_details": "预期修改远端仓库 /defaultShare/archive/liuwenchu/projects/IPLoc 的 mechanism/iplocid/iplocid/pipelines/outcome_stratified_core30.py、对应 tests/test_e010_r007.py，必要时 configs/e010_r007.json 和 launcher 中仅与输出 schema/版本有关的字段。新增测试至少覆盖：4-邻接（对角不连）、最大块选择、并列最小 token-index tie-break、IoU 分母/空集契约、S30 旧 stable tie-break 不变、canonical heads/hash assertion 不变。审批后由现有 tools/run_e010_r007.sh 经受管 executor 重跑。",
  "model_config": "不加载模型；严格复用R-003自然回答与attention artifacts。Reference heads唯一读取R-006实际完成summary.discovery.fixed_heads：Top3=L18H05,L20H12,L20H15，Top5=L18H05,L20H12,L20H15,L20H08,L14H02。Query heads唯一读取R-003实际完成summary.roles.query_heads.fixed_heads：Top3=L20H15,L24H16,L25H10，Top5=L20H15,L24H16,L25H10,L15H13,L21H10。运行前对R-003/R-006 summary SHA-256和上述完整名单作精确断言，禁止手工替换、重选或使用旧R-007错误名单。",
  "metric_definition": "定义：对每张非负有限 attention map，以降序 attention、flattened token index stable tie-break 取 k=ceil(0.30×visual-token-count) 个 S30 token；G 为同 grid 上 occupancy>0 的二值 GT token mask。保留 Core30Hit=1[S30∩G非空]。新增 S30IoU=|S30∩G|/|S30∪G|。在 S30 上按上下左右 4-邻接求连通块，取 token count 最大的 Cmax；若并列，以该块最小 flattened token index 最小者取胜。新增 Largest4NHit=1[Cmax∩G非空]，Largest4NIoU=|Cmax∩G|/|Cmax∪G|。每图还记录 s30_token_count、gt_token_count、s30_intersection_tokens、s30_union_tokens、largest4n_token_count、largest4n_fraction_of_s30、largest4n_intersection_tokens、largest4n_union_tokens。每个 role×cohort×outcome×head/ensemble 报 n、Core30Hit hits/rate、Largest4NHit hits/rate，以及 S30IoU/Largest4NIoU 的 mean、median、q25、q75；不把 binary token-grid IoU 与像素 IoU、fractional occupancy 或 strict argmax pointing 混同。",
  "integrity_gates": "G1 140 records、R-003/R-006 summary hash 和 canonical frozen exact-head assertion 不变；不符即停止。G2 每张 attention/GT grid shape、有限性、非负性、GT非空、S30 selected_token_count=k 均须通过。G3 Cmax 必须为 S30 的单一 4-connected component，最大 size 与并列最小 index 规则可由单元测试复算；每图 intersection≤各 mask size、union=sizeA+sizeB−intersection，IoU∈[0,1]。G4 输出 JSONL 的每个 map 有原/新增全部字段，summary 的分组 n 与逐图记录一致；固定图及汇总图存在。G5 旧 Core30Hit 输出可作为宽松对照保留，但不得覆盖/解释为新 IoU 输出，旧错误 reference-head 结果仍无效。",
  "expected_outcome": "该修订将产生比 Core30Hit 更不易饱和的空间贴合读出。允许 Largest4NIoU 很低、最大块未命中、组间无差/反向或所有角色仍饱和；结果只如实报告，不以任何结果改动冻结集合或阈值。",
  "acceptance_criteria": "审核通过并受管运行后：summary 写明 schema、上游 hashes、canonical heads、S30/4-neighborhood/tie-break 定义；per_image JSONL 对每个角色、单 head、Top3/5 含所有新增 token count、hit、IoU 字段；all 与 frozen heldout 各 role×outcome×head/ensemble 同时报 Core30Hit 与 Largest4NHit 的 n/hits/rate、S30IoU/Largest4NIoU 分布汇总；overview/fixed panels 可读取；focused test suite 通过；无 model load/new generation/head or sample reselection。",
  "claim_boundary": "仅为冻结 attention artifacts 上的离线、观察性、二值 token-grid 空间读出。S30IoU 与 Largest4NIoU 不等于像素分割 IoU、严格 argmax pointing 或模型实际定位准确率；correct/error 分层不证明 head 导致预测、identity matching/routing 或因果必要性。",
  "artifacts": "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-007-outcome-stratified-reference-query-head-core30-pointing-audit/metrics.json\n/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-007-outcome-stratified-reference-query-head-core30-pointing-audit/logs/train.log",
  "audit_paths": "inputs=R-001 records.json/artifacts；head authority=R-003 analysis/summary.json+manifests/subsets.json、R-006 analysis/summary.json；implementation=mechanism/iplocid/iplocid/pipelines/outcome_stratified_core30.py；tests=mechanism/iplocid/tests/test_e010_r007.py；new outputs=R-007 analysis/summary.json、analysis/per_image_core30.jsonl、metrics.json、visualizations/overview_all.png、overview_heldout.png、fixed_cases_correct.png、fixed_cases_error.png。"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
