# E008-R-001-grounding-heads-query-image-role-audit-n140-640 · grounding heads query-image role audit n140 640

- workflow: v2 / ready_to_run / 等待执行授权
- review_status: approved
- group_id: 未分组
- execution_dispatch:  / 

## 1. 研究设计
### 研究问题
reference-grounding heads L15H13/L16H23/L18H15在自然query bbox生成p-1 rows上是否对query image形成可重复的空间定位attention，还是仅保留reference-side grounding角色？
### 本轮目的
比较reference-grounding heads在自然query bbox生成行上的Q→Q与Q→R attention，并以G→R定义性边和localization main4 Q→Q作对照，判断grounding heads是否跨角色参与query定位。
### 假设或比较预期
H1跨角色：G-head Q→Q对query GT有空间选择性且correct高于error；H2角色分工：G→R正常而G-head Q→Q弥散；H3部分共享：仅交集head L18H15跨两侧有效。
### 数据与主要变量
E003-R-004b positive n140 manifest与归档natural responses；primary accepted error35+correct76=n111；partial22 secondary；rejected7仅coverage。GT只用于生成后空间评价。

无干预；G-heads=[L15H13,L16H23,L18H15]；L-heads=[L18H15,L19H03,L22H00,L20H08]；边类型Q→Q[G]、Q→R[G]、G→R[G]、Q→Q[L]；按head单独报告。

## 2. 指标设计
复用E005/E006已定义的fractional GT mass、area-normalized enrichment、pointing、S50、retained-mass token-fIoU/AUC及sequence bootstrap；新增的是同一指标在Q→Q[G-heads]上的角色对照，不新增事后阈值。质量/富集指标回答是否落在query GT，S50/fIoU回答distributed support而非仅argmax，correct-error与Q→R/G→R/Q→Q[L]对照回答跨角色还是reference-only。
### Exact teacher-replay通过率 (`exact_replay_rate`)
- 公式：N_exact / N_total
- 含义：归档响应token、bbox p-1 row与双图span均精确对齐的样本比例
- 汇总与范围：micro ratio / R-000工程门禁与R-001完整性

### GT区域fractional attention mass (`fractional_gt_mass`)
- 公式：sum_j A_j * w_j，其中w_j为视觉token与GT bbox的fractional occupancy
- 含义：指定row/head在目标区域内分配的raw attention质量
- 汇总与范围：逐head样本中位数及sequence bootstrap / Q→Q[G]、Q→R[G]、G→R[G]、Q→Q[L]

### GT区域面积归一化富集 (`area_normalized_enrichment`)
- 公式：(sum_j A_j*w_j / sum_j A_j) / (sum_j w_j / N_visual)
- 含义：相对均匀视觉attention时目标区域获得的富集倍数
- 汇总与范围：逐head样本中位数及correct-error差 / 各视觉span内条件化attention

### Raw-attention pointing命中率 (`pointing_rate`)
- 公式：N[argmax_j A_j的token与GT bbox有fractional overlap] / N_eligible
- 含义：raw map峰值是否落入目标区域的样本比例
- 汇总与范围：逐head分子/分母、Wilson区间与sequence bootstrap差 / GT覆盖至少一个merged visual token的样本

### 累计质量fractional-token IoU AUC (`retained_mass_fiou_auc`)
- 公式：mean_{rho in {0.05,...,0.95}} fIoU(S_rho,GT)，S_rho为达到累计attention质量rho的最小token集合
- 含义：衡量distributed attention support与GT token区域在多阈值下的空间重合
- 汇总与范围：逐head样本中位数及sequence bootstrap / 各预注册edge的视觉span条件化raw attention

## 3. 代码架构
E-008 使用 mechanism/iplocid 的公共 role_audit_pipeline；配置只声明冻结head与n140范围，tools 仅激活Workspace声明的conda:IPLoc并调用公共CLI。source output 使用E-003 generated-texts并按query image path唯一匹配；Q→Q采用query GT/grid，Q→R/G→R采用reference GT/grid。
- 公共包：`mechanism/iplocid/iplocid`
- 入口：`iplocid.pipelines.role_audit_pipeline:main`
- 配置：`mechanism/iplocid/configs/e008/r001_role_audit_n140_640.yaml`
- Shell launcher：`mechanism/iplocid/tools/run_e008_r001.sh`
- 复用模块：mechanism/iplocid/iplocid/datasets/records.py, mechanism/iplocid/iplocid/models/qwen.py, mechanism/iplocid/iplocid/prompts/messages.py, mechanism/iplocid/iplocid/prompts/coordinates.py, mechanism/iplocid/iplocid/attention/spans.py, mechanism/iplocid/iplocid/attention/metrics.py, mechanism/iplocid/iplocid/inference/replay.py
- 新增模块：mechanism/iplocid/iplocid/pipelines/role_audit_pipeline.py
- 测试：mechanism/iplocid/tests/test_attention_spans.py, mechanism/iplocid/tests/test_attention_metrics.py, mechanism/iplocid/tests/test_role_audit_spec.py

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iplocid/tools/run_e008_r001.sh --manifest /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/explog/E-005/runs/E005-R-029c-original140-positive-targets-binding-640/manifests/E003_R004b_positive_targets_n140.json --source-output /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/explog/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128/results/LASOT_local_1shot_T2_n140_v2/generated_texts/e003_r004b_joint_n140.json --run-dir /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-008/E008-R-001-grounding-heads-query-image-role-audit-n140-640 --model-path /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct --lora-path /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iplocid/pretrained_weights/Qwen3-VL-8B-Instruct_1shot_iplocid --old-data-prefix /home/featurize/data/LaSOTTesting --new-data-prefix /defaultShare/archive/liuwenchu/data/LaSOTTesting --limit 140`
- commit: ``
- workspace: 02
- tmux: incontext-E-008-E008-R-001-grounding-heads-query-image-role-audit-n140-640
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-008/E008-R-001-grounding-heads-query-image-role-audit-n140-640/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-008/E008-R-001-grounding-heads-query-image-role-audit-n140-640/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
teacher replay、attention-derived、non-causal；L18H15为两类head交集；不能证明identity、共享电路或行为改善。

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "现有Q→Q主要审计localization main4；L15H13/L16H23在Q→Q上的空间质量尚未单独量化。",
  "evidence_basis": "E005 head_role_registry；E005-R-029c n140 640 exact replay；E006-R-005 Q→Q main4 audit；Q-004/Q-005。",
  "implementation_summary": "复用E003-R-004b positive n140 archived natural responses，exact teacher replay；同forward提取G-heads Q→Q、Q→R、G→R，以及L-heads Q→Q对照；输出逐head raw metrics和固定heatmaps。",
  "implementation_details": "主边为query bbox p-1 rows×G-heads→query visual keys；补充query bbox p-1×G-heads→reference keys；定义性reference bbox p-1×G-heads→reference keys；对照query bbox p-1×L-heads→query keys；不做任何activation或attention rewrite。",
  "model_config": "Qwen3-VL-8B-Instruct+原IPLoc-ID 1shot LoRA；bf16 eager；max_side=640；官方原prompt/processor/EOS；与E005-R-029c入口一致。",
  "metric_definition": "fractional GT mass、area-normalized enrichment、pointing、S50、retained-mass token-fIoU/AUC、correct-error差、sequence bootstrap；保存raw attention与共享色标heatmaps。",
  "integrity_gates": "R-000通过；140/140 records或显式失败；token/row/span唯一匹配；head集合冻结；all finite；不使用future；不按结果重选head；rejected不借bbox row。",
  "expected_outcome": "若G-heads Q→Q对query GT有空间选择性且correct高于error，支持跨角色query-localization signature；若G→R正常而Q→Q弥散，支持reference-only role division。",
  "acceptance_criteria": "完成全体预冻结样本与逐head指标/heatmaps；无论正负均报告；不得将attention-derived观察升级为causal或identity claim。",
  "claim_boundary": "最多支持/削弱grounding heads是否携带query-side localization signature；不证明causal head role、identity或Joint F1泛化。",
  "audit_paths": "shell/06_experiments/E-008/plan.md; shell/06_experiments/E-005/head_role_registry.md; shell/01_questions/Q-004.md; shell/01_questions/Q-005.md"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
