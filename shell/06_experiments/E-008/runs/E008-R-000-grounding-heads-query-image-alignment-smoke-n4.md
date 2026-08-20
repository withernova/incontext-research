# E008-R-000-grounding-heads-query-image-alignment-smoke-n4 · grounding heads query-image alignment smoke n4

- workflow: v2 / failed / 运行失败
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-91529d76a769a0d13ebf37aa / running

## 1. 研究设计
### 研究问题
能否在Qwen3-VL/IPLoc-ID的640 exact teacher replay中，无歧义地提取query bbox p-1 rows上的G-head Q→Q/Q→R以及reference bbox rows上的G→R，并与L-head Q→Q对齐？
### 本轮目的
验证G-heads在query bbox p-1 rows上的Q→Q、Q→R与定义性G→R span提取、token对齐、grid映射和exact teacher replay。
### 假设或比较预期
若实现正确，4/4样本应满足归档token exact、bbox p-1 row与双图visual span唯一匹配、非方形merged grid正确、所有预注册head/edge attention finite；否则R-001不得启动。
### 数据与主要变量
E003-R-004b positive archived replay，预冻结2 correct+2 error，不按结果选样本。

无干预；G-heads固定[L15H13,L16H23,L18H15]；L-heads固定[L18H15,L19H03,L22H00,L20H08]；Q→Q/Q→R/G→R span固定。

## 2. 指标设计
复用E005/E006的row alignment、visual-span conditional mass、GT fractional coverage与finite审计；不新增科学指标。复用这些指标是因为R-000只验证被测attention边是否准确对应自然bbox生成row和正确图像span，避免把错位或空span误认为head角色。
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
R-000 与R-001共用 mechanism/iplocid 的 role_audit_pipeline；R-000只通过--limit 4固定2 correct+2 error工程样本。配置只声明冻结head和n4范围，launcher仅激活Workspace conda:IPLoc并调用公共CLI。source output 使用E-003 generated-texts按query image path唯一匹配；Q→Q采用query GT/grid，Q→R/G→R采用reference GT/grid。
- 公共包：`mechanism/iplocid/iplocid`
- 入口：`iplocid.pipelines.role_audit_pipeline:main`
- 配置：`mechanism/iplocid/configs/e008/r000_alignment_smoke_n4.yaml`
- Shell launcher：`mechanism/iplocid/tools/run_e008_r000.sh`
- 复用模块：mechanism/iplocid/iplocid/datasets/records.py, mechanism/iplocid/iplocid/models/qwen.py, mechanism/iplocid/iplocid/prompts/messages.py, mechanism/iplocid/iplocid/prompts/coordinates.py, mechanism/iplocid/iplocid/attention/spans.py, mechanism/iplocid/iplocid/attention/metrics.py, mechanism/iplocid/iplocid/inference/replay.py
- 新增模块：mechanism/iplocid/iplocid/pipelines/role_audit_pipeline.py
- 测试：mechanism/iplocid/tests/test_attention_spans.py, mechanism/iplocid/tests/test_attention_metrics.py, mechanism/iplocid/tests/test_role_audit_spec.py

> codespace 只建议保存可读 Shell；科研逻辑进入公共包的 Pipeline、Hook、Adapter 或 Metric。

## 4. 运行与 Experiment Steward
- command: `bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iplocid/tools/run_e008_r000.sh --manifest /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/explog/E-005/runs/E005-R-029c-original140-positive-targets-binding-640/manifests/E003_R004b_positive_targets_n140.json --source-output /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/explog/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128/results/LASOT_local_1shot_T2_n140_v2/generated_texts/e003_r004b_joint_n140.json --run-dir /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-008/E008-R-000-grounding-heads-query-image-alignment-smoke-n4 --model-path /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct --lora-path /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iplocid/pretrained_weights/Qwen3-VL-8B-Instruct_1shot_iplocid --old-data-prefix /home/featurize/data/LaSOTTesting --new-data-prefix /defaultShare/archive/liuwenchu/data/LaSOTTesting --limit 4`
- commit: ``
- workspace: 02
- tmux: incontext-E-008-E008-R-000-grounding-heads-query-image-alignment-smoke-n4
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-008/E008-R-000-grounding-heads-query-image-alignment-smoke-n4/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-008/E008-R-000-grounding-heads-query-image-alignment-smoke-n4/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
n4工程gate；不支持head role、localization或causal结论。

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "在n140观测前排除row/span/head映射错误；该run不产生科学结论。",
  "evidence_basis": "E005-R-029c 640 exact replay入口；E005 head_role_registry；E006-R-005 Q→Q main4 audit。",
  "implementation_summary": "固定2 correct+2 error，复用归档natural response做exact teacher replay；提取G-heads=L15H13,L16H23,L18H15在Q→Q、Q→R、G→R三条边，以及L-heads在Q→Q对照。",
  "implementation_details": "无模型干预；query bbox p-1 rows→query/reference visual keys；reference bbox p-1 rows→reference keys；验证visual span、merged-token occupancy、非方形grid、row alignment、finite和future-free。",
  "model_config": "Qwen3-VL-8B-Instruct+原IPLoc-ID 1shot LoRA；bf16 eager；max_side=640；原prompt/processor/EOS；exact teacher replay。",
  "metric_definition": "row/span alignment、token exact、visual span conditional mass、finite、raw mass及GT coverage仅作工程审计。",
  "integrity_gates": "4/4 exact replay；row/token/span唯一匹配；grid映射正确；all finite；不读future；head集合不可变；失败显式保留。",
  "expected_outcome": "工程通过后允许R-001；任一关键gate失败则停止并新建修复run。",
  "acceptance_criteria": "所有预注册工程gate通过并生成可机器读取审计记录和固定图。",
  "claim_boundary": "仅支持实现与对齐正确性，不支持科学Finding/Claim。",
  "audit_paths": "shell/06_experiments/E-008/plan.md; shell/06_experiments/E-005/head_role_registry.md"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
