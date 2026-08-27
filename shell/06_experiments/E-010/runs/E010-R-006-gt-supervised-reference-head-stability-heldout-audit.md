# E010-R-006-gt-supervised-reference-head-stability-heldout-audit · GT监督Reference head跨图稳定性与冻结held-out审计

- workflow: v2 / failed / 运行失败
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-16abb20df46e7a3656df99a5 / failed

## 1. 研究设计
### 研究问题
在R-005已证明逐图GT oracle存在的自然Qbbox→Reference maps中，GT监督的逐图空间评分能否跨70条R-003 discovery sequences收敛为一组固定Top3/5 reference heads，并在严格序列不重叠的70条held-out sequences上优于同层随机与all-head mean？
### 本轮目的
把GT限定为离线诊断监督：区分“oracle信号逐图存在但动态路由、无法固定化”与“现有无GT entropy代理错配但GT频率可恢复固定reference heads”。不修改R-005的无GT结论，也不把GT-IoU纳入可部署selector。
### 假设或比较预期
若discovery逐图GT-top-k head ID的频率集中、固定Top3/5在held-out优于同层随机，则固定化在监督诊断下可行而R-005失败主要是无GT代理失配；若频率分散且冻结held-out不优于随机，则reference空间信号主要为逐图动态，不能压缩为少数固定heads。
### 数据与主要变量
仅复用R-001 records/artifacts与R-003 manifests/subsets.json；discovery和evaluation各70条LaSOT sequence records且sequence overlap=0，训练暴露仍未知。仅审计自然生成Query bbox p−1 rows到Reference visual token span的1152-head q_to_r maps。

发现变量是GT监督逐图head rank；评估变量是冻结GT-frequency Top3/5 vs layer-matched random vs all-head mean vs per-image GT oracle。R-003 sequence split、自然row/span、grid和空间指标保持不变。GT允许进入discovery和评估，但严禁进入held-out固定head重选；correct/error、自然IoU不进入head ranking。

## 2. 指标设计
复用R-005/R-003的pointing、enrichment、target mass、S50 fIoU及sequence-bootstrap，新增GT-discovery频率稳定性；这样只改变监督可见性，而不改变输入、row、grid或评分定义。
## 3. 代码架构
审批后在IPLoc现有attention analysis模块新增只读离线pipeline，复用R-005 artifact reader、空间评分与R-003 split；不复制模型runner，不修改R-003/R-005 artifacts。
- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `cd /defaultShare/archive/liuwenchu/projects/IPLoc && mechanism/iplocid/tools/run_e010_r006_gt_iou_maxhit_trial.sh`
- commit: ``
- workspace: 02
- tmux: incontext-E-010-E010-R-006-gt-supervised-reference-head-stability-heldout-audit
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-006-gt-supervised-reference-head-stability-heldout-audit/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-006-gt-supervised-reference-head-stability-heldout-audit/outputs
- Steward 摘要：```json
{
  "execution_completed_at": "2026-08-27T15:06:22",
  "evidence": {
    "log": "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-006-gt-supervised-reference-head-stability-heldout-audit/logs/train.log",
    "artifact": "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-006-gt-supervised-reference-head-stability-heldout-audit/metrics.json",
    "result_message": "managed execution exited 0; metrics parsed; human analysis required"
  },
  "note": "程序已结束，等待科研结果分析"
}
```

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
（可留空；如有明显的数据、模型或比较限制，请简短记录。）

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "R-005显示70条evaluation中单图GT oracle pointing=0.671而无GT Top10对oracle召回=0，说明强单图信号与无GT筛选失配；但R-005没有检验GT监督的oracle/near-oracle head是否跨图稳定，故不能判断固定化是否根本不可行。",
  "evidence_basis": "R-005 analysis/summary.json：GT oracle、Top10 candidate recall、routing统计；R-003 manifests/subsets.json定义的70/70 sequence-disjoint split与自然Qbbox→Reference artifacts。",
  "implementation_summary": "已实现并受管完成纯离线 GT-supervised stability pipeline。读取 R-001 的 140 个 q_to_r artifacts 与 R-003 的哈希锁定 70/70 sequence-disjoint split；不加载模型、不重跑生成、不改写既有 artifact。discovery 的 GT 空间排序仅用 Reference occupancy；按 Top1 频率冻结 Top3/5 后，在 evaluation 70 条上禁止重选。",
  "implementation_details": "代码：公共空间指标 iplocid.attention.metrics（normalize_nonnegative、fractional_mass、area_normalized_enrichment、pointing_hit、retained_mass_support、fractional_token_iou）；R-006 pipeline=iplocid.pipelines.gt_supervised_reference_stability；配置=mechanism/iplocid/configs/e010_r006.json；薄启动=mechanism/iplocid/tools/run_e010_r006.sh；可视化后处理=mechanism/iplocid/tools/render_e010_r006_attention_overlays.py。单图排序按 S50 fIoU 降序、enrichment 降序、target mass 降序、head ID 升序。Top1 frequency 在 discovery 70 条确定冻结集合。Top3/5 分别为 L18H05,L20H12,L20H15 与加 L20H08,L14H02。随机对照逐层匹配冻结集合的 layer composition，seed=20260828、100 repeats；差异按70条sequence有放回bootstrap=2000。",
  "model_config": "不加载模型；仅读取由R-001中Qwen3-VL-8B-Instruct + IPLoc-ID LoRA自然生成过程保存的attention artifacts与记录。",
  "metric_definition": "对非负 attention map A 归一化 P=A/sum(A)。pointing=1[argmax(P) 落入 fractional Reference-GT occupancy]；mass=sum(P*G)；enrichment=mass/mean(G)；S50 fIoU=取最小 top-P token support 使累计质量>=0.5，再与 fractional G 计算 token-grid IoU。GT rank 使用 (S50 fIoU,enrichment,mass,-head_id) 字典序。稳定性：Top10 pairwise Jaccard=|Ti∩Tj|/|Ti∪Tj|；effective head count=1/sum_h(F(h)/70)^2。held-out 对冻结聚合 map、层匹配随机均值、1152-head mean、逐图GT oracle统一评分；报告 fixed-random paired sequence-bootstrap 95% CI。",
  "integrity_gates": "正式运行核验：140 records；discovery=70、evaluation=70、sequence overlap=0；R-003 summary/subsets/row-span contract 哈希一致；自然Qbbox rows、token grid、artifact非负有限和 Reference occupancy 均通过；no_model_load=true；gt_used_in_discovery=true；heldout_reselection=false；outcome_used_in_ranking=false；failures=0。实现前 py_compile 通过；140-record smoke 通过（含12张诊断图）；受管正式运行 exit=0、metrics稳定、completion marker存在。可视化为运行后只读后处理，manifest 声明 metrics_or_heads_changed=false。",
  "expected_outcome": "给出GT监督固定化是否可能的判别：A频率集中且held-out超过随机，说明R-005无GT代理失配；B频率分散或held-out无优势，支持动态/不可固定化；C discovery集中但held-out衰减，提示选择集特异。任何情形都不证明身份选择或因果必要性。",
  "acceptance_criteria": "140条输入契约通过；discovery/evaluation各70条及零sequence overlap；逐图GT ranking、频率/集中度/Jaccard原始记录齐全；冻结Top3/5及其层匹配随机名单可追溯；held-out各方法全部空间指标和bootstrap CI齐全；至少12个固定统一色标案例；明确GT监督边界。",
  "conclusion_scope": "该Run只支持：在冻结R-003自然Qbbox→Reference attention artifacts上，GT空间监督频率能构建一个在sequence-disjoint held-out上优于层匹配随机的固定Top3/5 readout ensemble。不能支持：GT-free selector可部署、模型利用GT、identity binding、任何head的因果必要性、训练外泛化。",
  "claim_boundary": "仅回答GT监督的空间oracle/near-oracle head能否跨sequence固定化；不能把结果外推为LocalizationHeads无GT方法有效、模型依赖这些heads、或模型完成identity binding。"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
