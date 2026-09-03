# E010-R-008-full-lasot-natural-replay-grounding-query-role-audit-n1400-640 · 完整LaSOT自然重放的E008 grounding/query角色审计（n=1400，640）

- workflow: v2 / awaiting_review / 等待审核
- review_status: pending_review
- group_id: 未分组
- execution_dispatch:  / 

## 1. 研究设计
### 研究问题
在完整LaSOT 1400条自然Query bbox生成与exact replay中，R-003 Query Top-5的Q→Q/Q→R及R-006冻结Reference Top-5的R→R（均使用相同自然Query-bbox p−1 rows）在correct/error之间是否稳定分离，并相对层匹配随机和all-head mean如何？
### 本轮目的
将已完成的完整LaSOT Q→Q/Q→R Query-head审计补全为用户定义的R→R：同一自然Query bbox p−1 rows到Reference image tokens，但使用R-006冻结Reference Top-5。
### 假设或比较预期
若R-007的Query-head信号可推广，则evaluation 700条中冻结Top-5在Q→Q或Q→R的空间指标及correct−error差异将优于层匹配随机与all-head mean；若无优势或差异不稳，则完整数据不支持该冻结Query-head readout。
### 数据与主要变量
完整LaSOT n=1400（70类×20）；每类deterministic hash 10 evaluation/10 discovery，evaluation=700为主。已完成natural JSONL与exact replay per-image基础产物将作为不可变输入；不重跑生成，不使用Reference bbox token rows。correct=positive且natural IoU≥0.7；error=positive且natural IoU<0.1；middle/nonpositive/unparsed/replay failure分列。

三类读出均固定同一自然Query bbox p−1 rows：Q→Q=R-003 Query Top-5到Query span/Query GT；Q→R=同Query Top-5到Reference span/Reference GT；R→R=R-006冻结Reference Top-5(L18H05,L20H12,L20H15,L20H08,L14H02)到Reference span/Reference GT。无Reference-bbox rows、无GT参与自然生成/heads重选。各readout仅和其同层组成匹配random及all-head mean比较。

## 2. 指标设计
每个单head与Top-5等权归一化ensemble，在Q→Q/Q→R/R→R报告pointing、fractional mass、enrichment、S50 fIoU、Core30Hit、S30IoU、Largest4NHit、Largest4NIoU；evaluation-700 primary sequence bootstrap correct−error 95% CI，all1400仅描述性；补充R→R相对random/all-head。
## 3. 代码架构
入口=mechanism/iplocid/iplocid/pipelines/full_lasot_role_audit.py；config=mechanism/iplocid/configs/e010_r008.json；launcher=mechanism/iplocid/tools/run_e010_r008_full_lasot.sh；tests=mechanism/iplocid/tests/test_e010_r008.py。最小扩展是在既有natural Query rows的exact-replay中增加R-006冻结Reference Top-5的R→R。
- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `cd /defaultShare/archive/liuwenchu/projects/IPLoc && bash mechanism/iplocid/tools/run_e010_r008_full_lasot.sh`
- commit: ``
- workspace: 02
- tmux: incontext-E-010-E010-R-008-full-lasot-natural-replay-grounding-query-role-audit-n1400-640
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-008-full-lasot-natural-replay-grounding-query-role-audit-n1400-640/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-008-full-lasot-natural-replay-grounding-query-role-audit-n1400-640/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
（可留空；如有明显的数据、模型或比较限制，请简短记录。）

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "R-007仅在既有140条artifact上离线统计，无法回答其冻结Query-head readout能否在完整LaSOT自然生成与严格exact replay中复现，也无法以700条evaluation为主要推断单位。",
  "evidence_basis": "R-007 canonical定义outcome、S30/最大4邻域指标和同层随机/all-head对照；R-003 actual Query Top-5是唯一head authority。",
  "implementation_summary": "复用已完成R-008的1400 natural response与精确replay行/双图span契约；仅重新执行replay空间评分，新增R→R分支。该分支把R-006固定Reference Top-5应用于同一自然Query-bbox p−1 rows和Reference span，绝不构造Reference bbox rows。",
  "implementation_details": "远端pipeline full_lasot_role_audit.py schema升级为v2，READOUTS明确q_to_q/q_to_r/r_to_r；config精确记录R-006 authority；每readout独立同层随机种子。输出summary保留row_contract和两套冻结head名单。",
  "model_config": "Qwen3-VL-8B-Instruct加IPLoc-ID LoRA，既有IPLoc prompt/processor，bf16 eager attention，max_side=640；自然阶段贪婪生成，replay使用同一完整自然response。",
  "metric_definition": "attention map在目标span内归一化。pointing为argmax落入fractional occupancy；mass为attention×occupancy和；enrichment为mass除occupancy平均面积；S50 fIoU为累计50%质量support与fractional occupancy的token-grid IoU。S30取ceil(30% token)且attention降序/flattened index稳定并列规则；Core30Hit为S30与二值GT相交；S30IoU为二值交并比；Largest4N为S30最大上下左右连通块，块大小并列时取最小flattened index，报告其Hit/IoU。correct−error以sequence bootstrap 95% CI。",
  "integrity_gates": "精确断言R-006 discovery.fixed_heads[5]等于配置Reference Top-5；READOUTS必须包含r_to_r且target=reference；所有readout使用同一natural Query-bbox p−1 replay rows；禁止Reference-bbox rows；1400 natural与1400 replay产物不变、70×20与10/10 split不变、per-image replay/分母守恒。",
  "expected_outcome": "允许Q→Q或Q→R在correct−error、随机对照或all-head比较上支持、无差或反向；不以结果修改heads、cutoff、split或指标。",
  "acceptance_criteria": "审核后运行时交付1400 manifest/split哈希、natural JSONL、exact replay failure表、per-image JSONL/maps、evaluation与all1400的Q→Q/Q→R×head/Top-5结果、layer-matched random/all-head对照、bootstrap CI和固定可视化。",
  "claim_boundary": "仅评估完整LaSOT上冻结Query-head attention readout与自然outcome的观察性空间关联；不证明因果必要性、identity routing、reference grounding或训练外泛化。",
  "audit_paths": "pipeline=/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iplocid/iplocid/pipelines/full_lasot_role_audit.py；config=/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iplocid/configs/e010_r008.json；R006-authority=/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-006-gt-supervised-reference-head-stability-heldout-audit/analysis/summary.json；base-natural=/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-008-full-lasot-natural-replay-grounding-query-role-audit-n1400-640/outputs/natural_records.jsonl；tests=/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iplocid/tests/test_e010_r008.py"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
