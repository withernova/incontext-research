# E010-R-003-natural-query-bbox-dual-span-head-discovery-stability · 自然Query-bbox双图Query/Reference head无GT发现与稳定性复核

- workflow: v2 / failed / 运行失败
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-5fb6dbf618ffe284e2331997 / failed

## 1. 研究设计
### 研究问题
仅使用模型自然生成Query bbox token的p−1 rows时，分别对Query和Reference image spans运行严格LocalizationHeads式无GT算法，能否找到显著且在独立20图重采样及selection-held-out序列上稳定有效的query heads与reference heads？
### 本轮目的
以模型自然生成的Query bbox token prediction rows为唯一query rows，分别读取其到Query image tokens和Reference image tokens的逐头注意力，使用同一套LocalizationHeads式无GT算法独立发现query heads与reference heads，并验证二者在20图重复抽样、较大子集和sequence-held-out样本上的显著性、稳定性与空间有效性。明确禁止使用Reference bbox token rows定义任何head。
### 假设或比较预期
query heads将呈现高inclusion probability、较高Top-k一致性和held-out Query GT定位；reference heads若真实存在，也应在n=20重复抽样中收敛且在held-out Reference GT上优于同层随机，否则应判为不稳定或稳定偏置头。
### 数据与主要变量
沿用旧R-001的140条IPLoc-ID positive自然回答及对应精确replay attention，按LaSOT sequence_cluster隔离。固定seed先划70 discovery/70 evaluation；evaluation在所有head名单、阈值和重采样规则冻结前不可用于选择。训练暴露未知，evaluation只能称selection-held-out sequences。

角色A query heads=Qbbox→Query；角色B reference heads=Qbbox→Reference。相同rows、相同样本、相同selection参数，唯一变化是image key span。控制包括同层随机Top3/5、image-attention-sum-only、entropy-only、all-head mean、per-image oracle；oracle只作上限不得进入固定名单。

## 2. 指标设计
主指标为n=20×100 inclusion/Jaccard/rank稳定性与held-out固定Top3/5相对同层随机的pointing/enrichment/S50 fIoU；n=40/56为样本量曲线；query/reference使用完全相同参数且独立排名。
## 3. 代码架构
新增只读artifact审计与严格论文entropy/resampling分析入口，输出双角色selection manifests、subset manifests、metrics和逐头可视化；不得调用Reference bbox rows或旧G→R分支。
- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `cd /defaultShare/archive/liuwenchu/projects/IPLoc && PYTHON_BIN=/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python3.9 bash mechanism/iplocid/tools/run_e010_r003_trial_batch.sh`
- commit: ``
- workspace: 02
- tmux: incontext-E-010-E010-R-003-natural-query-bbox-dual-span-head-discovery-stability
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-003-natural-query-bbox-dual-span-head-discovery-stability/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-003-natural-query-bbox-dual-span-head-discovery-stability/outputs
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
  "necessity": "E-005/E-010历史记录混用了Reference GT bbox rows→Reference、自然Query bbox rows→Reference、teacher-forced Query bbox rows及GT-conditioned visual rows，导致‘reference head’术语与用户目标不一致。必须以唯一rows定义重建两批head，才能判断固定少数head是否真实存在并为后续跨span偏差检验提供冻结名单。",
  "evidence_basis": "LocalizationHeads论文以image-attention sum、connected-component spatial entropy和跨样本selection frequency无GT发现固定heads；GT仅用于发现后的空间验证。E010旧R-001已保存140条自然bbox replay的Q→Q/Q→R全头张量，但其entropy采用residual-mass而非论文二值连通域面积，且56图leave-one-fold不能直接回答每次20图是否换head。本Run按用户新定义与论文公式重做。",
  "implementation_summary": "计划复用旧R-001的140条自然回答、精确bbox-token对齐与全头attention artifacts，优先纯离线分析；先核验artifact来自相同自然Query bbox rows及双图span。新增严格论文版二值连通域面积entropy、确定性20图重采样、双角色独立排名和冻结held-out验证，不加载模型，除非artifact契约核验失败且另行审核。",
  "implementation_details": "唯一attention row集合：自然生成Query bbox从左方括号到首个右方括号的全部token positions之p−1 rows，逐head在这些rows上求预注册平均；同一rows分别截取Query image span得到Qbbox→Q map、截取Reference image span得到Qbbox→R map。query heads仅由Qbbox→Q discovery maps选出；reference heads仅由Qbbox→R discovery maps选出。发现阶段不读取GT。对每个角色独立执行：排除层0/1；按跨discovery样本平均image-attention sum及论文最大曲率阈值筛选；map按自身均值二值化；8邻域连通域；按component token count计算entropy；每图低熵Top10；按selection frequency固定Top3/Top5。不得用GT、自然IoU或correct/error重选head。",
  "model_config": "冻结Qwen3-VL-8B-Instruct + IPLoc-ID LoRA、max_side=640及旧R-001自然回答/replay artifacts；不重新自然生成、不teacher-force GT bbox。必须记录模型、LoRA、manifest、自然输出和artifact manifest哈希。",
  "metric_definition": "稳定性：100次n=20重采样的head inclusion probability、Top3/Top5相对70图基准与两两Jaccard分布、完整rank Spearman、selection-frequency置信区间；显著性：相对同层随机的selection-frequency集中度、held-out pointing、GT area-normalized enrichment、target mass、S50 fractional-token IoU和至少一头/多数头覆盖；角色关系：query/reference Top-k overlap和rank correlation。GT指标仅在名单冻结后计算。",
  "integrity_gates": "G1 所有map必须由同一自然Query bbox p−1 rows生成，禁止Reference bbox rows、GT Query bbox teacher forcing或GT-conditioned rows；G2 双image spans与token grids逐样本精确核验，row/span契约哈希保存；G3 discovery/evaluation sequence零重叠；G4严格使用二值连通域token-count entropy并以单元测试对手算例验证；G5 n=20抽样seed和100个subset IDs预先物化；G6 GT、correct/error、自然IoU不得进入发现；G7负结果不得通过改阈值、改rows或改head数挽救。",
  "expected_outcome": "分别给出query heads与reference heads是否存在少数显著高频核心、每次20图会不会换名单、随样本量增加是否收敛，以及冻结名单能否在selection-held-out图上定位各自目标。允许出现query heads稳定有效而reference heads稳定但无效，或reference heads完全不稳定等负面结果。",
  "acceptance_criteria": "140条rows/spans契约全通过且零静默失败；70/70 sequence隔离；query/reference两套严格论文式发现结果齐全；n=20/40/56各100次稳定性结果及inclusion/Jaccard/rank表齐全；冻结Top3/5对同层随机与held-out GT指标齐全；至少保存12张query-head Q→Q和12张reference-head Q→R逐头热图；完整结果、配置、subset manifest与哈希可追溯。",
  "claim_boundary": "只回答自然生成Query bbox rows下，Qbbox→Query与Qbbox→Reference两批固定heads的无GT发现显著性、20图/更大样本稳定性和selection-held-out空间有效性；不使用或支持Reference bbox→Reference head概念，不证明这些head为任务必要电路。"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
