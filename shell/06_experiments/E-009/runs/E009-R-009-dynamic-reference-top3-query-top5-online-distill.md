# E009-R-009-dynamic-reference-top3-query-top5-online-distill · 动态 Reference Top-3 到 Query Top-5 在线蒸馏（探索性扩展）

- workflow: v2 / code_planning / 代码方案
- review_status: draft
- group_id: 未分组
- execution_dispatch:  / 

## 1. 研究设计
### 研究问题
固定 head ID 下，使用当前模型在线 Reference Top-3 stop-gradient teacher 蒸馏 Query Top-5，能否把跨图 attention 对齐转化为 held-out 自然生成定位增益？
### 本轮目的
独立检验固定 head ID、当前模型在线 Reference teacher、stop-gradient target 的单向蒸馏是否改善自然生成定位；该 Run 是 R008 之外的探索性扩展，不替代其离线固定 correct/cyclic_roll/gt_mask 四臂。
### 假设或比较预期
在线单向蒸馏会降低 teacher-student KL并提高student对Reference目标区域的读取；只有该机制变化同时带来held-out自然生成IoU改善时才支持性能假设。
### 数据与主要变量
训练使用过滤后的 train_only_1shot_focus_valid10522.json（10522条，SHA-256=bd7037325096cc99097333090ec5d02f64dd9ce2922f04e0e4409d1d635bd6e7）。held-out 自然生成评估使用 combined manifest 1766条（LaSOT 600、GOT10k 180、TAO 986）。valid96 已参与 head 发现，只用于开发诊断。

固定 Reference/Query head ID、训练 manifest、父 checkpoint和动态单向 stop-gradient 定义。与 continued-SFT baseline/step1729作事后自然生成比较；由于没有同 Run cyclic_roll/gt_mask 控制且评估 vision token cap=4096，不得冒充 R008 预注册四臂检验。

## 2. 指标设计
combined test自然生成per-dataset mIoU为效果证据；valid96全-head probe、KL/mass/S50和12个错误案例热图仅作开发机制解释。
## 3. 代码架构
复用R008 selected-attention与auxiliary loss接口，新增dynamic_teacher treatment和独立launcher；不调用FixedTeacherStore，不读取teacher_manifest。
- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `bash tools/run/run_e009_dynamic_reference_query_distill.sh`
- commit: ``
- workspace: 02
- tmux: incontext-E-009-E009-R-009-dynamic-reference-top3-query-top5-online-distill
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-dynamic-reference-query-online-distill/train-lr4e-5.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-R-009-dynamic-reference-top3-query-top5-online-distill/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
机制诊断显示蒸馏被真实优化：valid96 Teacher→Student KL 从 0.7776 降至 0.1713，Student object mass 从 0.00701 升至 0.00927，Student S50-fIoU 从 0.1479 升至 0.2956；Teacher S50-fIoU 从 0.2637 微降至 0.2598。dynamic final Reference Top-5 被多个原 student heads 占据，原 teacher L20H20/L14H23 跌出 Top-5，支持共享参数下 teacher 功能漂移。逐样本 attention 指标与 IoU delta 的 Spearman 相关均不显著；错误案例说明更低 KL 不充分保证 Query 候选实例选择正确。

## 简短局限
单 seed；heads由valid96和单一父轨迹筛选；teacher与student共享LoRA参数；valid96不是独立效果证据；attention来自GT bbox teacher-forced rows而非自由生成因果轨迹；combined评估vision_max_patch_tokens=4096，与后续拟统一的1024配置不同；无dynamic专属roll/GT-mask对照。

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "R008 预注册的是离线冻结 teacher，无法回答 teacher 随当前模型更新时的行为；因此必须单独记录 dynamic teacher，避免把在线共同漂移误报为 fixed-correct 结果。",
  "evidence_basis": "继承 Solid R007 固定 heads：Reference Top-3=[L20H15,L20H20,L14H23]，Query Top-5=[L21H10,L17H04,L17H07,L24H16,L18H15]。训练与诊断产物来自独立 dynamic branch；不读取离线 teacher artifact。",
  "implementation_summary": "同一次当前模型 forward 捕获固定 Reference Top-3 与 Query Top-5 selected attention；Reference shape/span/object targets 在 auxiliary loss 前 detach，Query student 保持可微。仅训练语言 decoder LoRA，父 adapter 为 step1729；lr=4e-5，3 epochs，4 GPU，per-rank batch1，gradient accumulation16，global batch64，gradient checkpointing use_reentrant=False。",
  "implementation_details": "正式轨迹从 step1729 干净初始化，不从先前 lr=1e-5 尝试 resume；完成495个 optimizer steps。teacher target 分支无直接 auxiliary gradient，但 teacher heads 可经 SFT、共享上游参数和 student 路径间接漂移，因此结果不能解释成冻结老师监督。",
  "model_config": "Qwen3-VL-8B-Instruct + NF4 QLoRA；可训练21,823,488参数（0.433840%），visual encoder与原始8B权重冻结；父 checkpoint=samples_00110607_step_001729，final checkpoint=samples_00031566_step_000494。",
  "metric_definition": "主结果为 combined test 及 LaSOT/GOT10k/TAO 的自然生成 mIoU与 paired delta。valid96 的 teacher-student KL、reference object mass、S50-fIoU、head ranking和错误样本热图只作 teacher-forced、post-hoc、非因果机制诊断。",
  "integrity_gates": "正式训练495/495完成、final checkpoint完整、finite_grad_fraction=1.0、adapter_delta_norm=5.4528；4-GPU one-step smoke 无 DDP ready-twice；combined 1766/1766与valid96 96/96全部解析；诊断对两个 checkpoint 均保存96份全-head maps。",
  "expected_outcome": "若在线蒸馏既降低 teacher-student KL，又在 held-out per-dataset IoU 上稳定优于父 checkpoint和continued-SFT，才支持继续研究 dynamic reference-reading 辅助训练；仅 alignment 改善而自然生成无增益则不支持性能假设。",
  "acceptance_criteria": "工程完整性已满足；科学性能假设要求 combined/per-dataset 自然生成稳定改善。实际 combined mIoU 下降，故性能假设不支持；valid96改善不能覆盖 held-out负结果。",
  "conclusion_scope": "在固定step1729、固定heads、单seed与当前QLoRA实现下，在线stop-gradient dynamic teacher显著增强attention集合对齐，但未转化为combined held-out自然定位增益。该结果不等价于R008 fixed-correct，不判断fixed teacher、cyclic_roll或GT-mask。",
  "claim_boundary": "可支持：dynamic训练显著提高固定集合的teacher-student attention对齐，但在当前单seed combined test上未改善自然定位，并伴随head ranking漂移。不可支持：Reference信息无用、attention对齐必然无效、fixed teacher无效、单head具有因果作用或跨seed/官方benchmark泛化。",
  "artifacts": "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/branches/20260902T123511662352Z--E009-dynamic-reference-top3-query-top5-online-distill/checkpoints/samples_00031566_step_000494; /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/branches/20260902T123511662352Z--E009-dynamic-reference-top3-query-top5-online-distill/diagnostics/valid96_attention/summary.json; /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/branches/20260902T123511662352Z--E009-dynamic-reference-top3-query-top5-online-distill/diagnostics/valid96_attention/per_sample.csv; /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/branches/20260902T123511662352Z--E009-dynamic-reference-top3-query-top5-online-distill/diagnostics/valid96_attention/per_head_summary.csv",
  "audit_paths": "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/branches/20260902T123511662352Z--E009-dynamic-reference-top3-query-top5-online-distill/run_manifest.json; /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/branches/20260902T123511662352Z--E009-dynamic-reference-top3-query-top5-online-distill/checkpoints/samples_00031566_step_000494; /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/branches/20260902T123511662352Z--E009-dynamic-reference-top3-query-top5-online-distill/diagnostics/valid96_attention/{summary.json,per_sample.csv,per_head_summary.csv,*_per_head.png}; /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/branches/20260902T153749921589Z--focus-qwen3vl8b-1shot-nf4-ddp4-ft-correct-459/evaluation/{metrics.json,predictions.jsonl}; /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-dynamic-reference-query-online-distill/train-lr4e-5.log"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
