# E008-R-000d-grounding-heads-query-image-alignment-smoke-n4-tmux-guarded-runtime-retry-v2 · grounding heads query-image alignment smoke n4 tmux-guarded runtime retry v2

- workflow: v2 / running / 运行与监控
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-0e828a23d12e40efd4f443bf / running

## 1. 研究设计
### 研究问题
在tmux-guarded降级隔离下，同一n4公共iplocid exact replay能否完成R-000既定行/跨度工程门禁？
### 本轮目的
在R-000b相同的冻结n4科研规范下，使用已修复的canonical IPLoc运行时重试公共pipeline；唯一执行层变化为已接受的tmux-guarded隔离。
### 假设或比较预期
唯一隔离变化不应改变公共pipeline对冻结4样本的token、row、span、grid和attention finite工程结果；若失败则是新环境/实现故障而非科学反证。
### 数据与主要变量
E003-R-004b positive n140 manifest前4样本；E003 generated_texts按query image path唯一匹配；不修改manifest/response/head/指标。

G-heads=[L15H13,L16H23,L18H15]；L-heads=[L18H15,L19H03,L22H00,L20H08]；无attention/activation干预。

## 2. 指标设计
复用E-008 Experiment已登记exact_replay_rate、fractional_gt_mass、area_normalized_enrichment、pointing_rate和retained_mass_fiou_auc；本run只用它们验证对齐与finite，不解释组间科学差异。
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
公共包mechanism/iplocid/iplocid提供pipeline；configs/e008仅声明范围；tools/run_e008_r000.sh仅激活conda:IPLoc并调用公共CLI。tmux-guarded由survey-tool执行器强制审核快照、环境证明、固定command和allowlist路径。 本run仅替换已验证的运行时版本，科研样本/head/指标/提示词完全继承R-000b。
- 公共包：`mechanism/iplocid/iplocid`
- 入口：`iplocid.pipelines.role_audit_pipeline:main`
- 配置：`mechanism/iplocid/configs/e008/r000_alignment_smoke_n4.yaml`
- Shell launcher：`mechanism/iplocid/tools/run_e008_r000.sh`
- 复用模块：mechanism/iplocid/iplocid/datasets/records.py, mechanism/iplocid/iplocid/models/qwen.py, mechanism/iplocid/iplocid/prompts/messages.py, mechanism/iplocid/iplocid/prompts/coordinates.py, mechanism/iplocid/iplocid/attention/spans.py, mechanism/iplocid/iplocid/attention/metrics.py, mechanism/iplocid/iplocid/inference/replay.py
- 新增模块：mechanism/iplocid/iplocid/pipelines/role_audit_pipeline.py
- 测试：mechanism/iplocid/tests/test_attention_spans.py, mechanism/iplocid/tests/test_attention_metrics.py, mechanism/iplocid/tests/test_role_audit_spec.py

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iplocid/tools/run_e008_r000.sh --manifest /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/explog/E-005/runs/E005-R-029c-original140-positive-targets-binding-640/manifests/E003_R004b_positive_targets_n140.json --source-output /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/explog/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128/results/LASOT_local_1shot_T2_n140_v2/generated_texts/e003_r004b_joint_n140.json --run-dir /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-008/E008-R-000d-grounding-heads-query-image-alignment-smoke-n4-tmux-guarded-runtime-retry-v2 --model-path /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct --lora-path /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iplocid/pretrained_weights/Qwen3-VL-8B-Instruct_1shot_iplocid --old-data-prefix /home/featurize/data/LaSOTTesting --new-data-prefix /defaultShare/archive/liuwenchu/data/LaSOTTesting --limit 4`
- commit: ``
- workspace: 02
- tmux: incontext-E-008-E008-R-000d-grounding-heads-query-image-alignment-smoke-n4-tmux-guarded-runtime-retry-v2
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-008/E008-R-000d-grounding-heads-query-image-alignment-smoke-n4-tmux-guarded-runtime-retry-v2/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-008/E008-R-000d-grounding-heads-query-image-alignment-smoke-n4-tmux-guarded-runtime-retry-v2/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
tmux-guarded为人类接受的降级隔离：宿主可读目录不可被内核隐藏、网络不可强制隔离；n4无科学结论。 此为环境runtime retry，不产生额外科学变量。

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "R-000b在模型加载前因旧Transformers缺少Qwen3VL类失败，0 forward；当前IPLoc已验证torch 2.2.2+cu121、transformers 4.57.3、Qwen3VL class和pip check均通过。",
  "evidence_basis": "旧E008-R-000失败日志；E005-R-029c manifest；E003-R-004b generated_texts；公共iplocid tests。",
  "implementation_summary": "公共iplocid role_audit_pipeline以--limit 4运行exact teacher replay，按query image path匹配E003 archived output。",
  "implementation_details": "Q→Q使用query GT/grid，Q→R/G→R使用reference GT/grid；conda:IPLoc证明、固定tmux、allowlist写路径和已审核command继续强制。tmux-guarded不隐藏宿主可读目录且无法强制断网，已由人类接受。",
  "model_config": "Qwen3-VL-8B-Instruct+IPLoc-ID 1shot LoRA；conda:IPLoc；bf16 eager；max_side=640。",
  "metric_definition": "exact replay、row/span唯一匹配、finite、四种边的raw map及GT fractional metrics仅作工程审计。",
  "integrity_gates": "4/4 records或显式失败；模型/LoRA/manifest/source output本地存在；conda:IPLoc proof；public package tests；固定head和双图span；tmux-guarded路径allowlist。",
  "expected_outcome": "若4/4通过，说明公共pipeline与新环境可进入R-001审核；若失败，保留失败记录，不变更科研变量。",
  "acceptance_criteria": "4/4 token/row/span/grid/head/finite gate通过，生成summary、raw npz和显式failure records。",
  "claim_boundary": "仅支持公共pipeline工程正确性；不支持head role、identity、因果或行为结论。",
  "audit_paths": "shell/06_experiments/E-008/events.md; mechanism/iplocid/ARCHITECTURE_MIGRATION.md"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
