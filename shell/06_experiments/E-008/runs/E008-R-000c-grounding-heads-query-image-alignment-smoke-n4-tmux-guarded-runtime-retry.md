# E008-R-000c-grounding-heads-query-image-alignment-smoke-n4-tmux-guarded-runtime-retry · grounding heads query-image alignment smoke n4 tmux-guarded runtime retry

- canonical_run_id: `E008-R-000c-grounding-heads-query-image-alignment-smoke-n4-tmux-guarded-runtime-retry`
- group_id: （未分组 / 待整理）
- run_type: engineering_gate
- review_status: draft
- review_round: 0
- submitted_for_review_at: 
- approved_at: 
- approved_by: 
- execution_authorized_at: 
- execution_authorized_by: 
- execution_authorization_consumed_at: 
- execution_dispatch_id: 
- execution_dispatch_latest_status: 
- legacy_registry_ids: （无）

> 已分组 Run 位于 `runs/<group-id>/<run-id>.md`；未分组 Run 位于 `runs/<run-id>.md`。
> Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
draft

## 本轮目的
在与R-000b相同的n4、冻结head、manifest、归档输出、模型和LoRA下重试公共pipeline；唯一新增前提是已记录的canonical IPLoc runtime修复。

## 必要性 / 证据链位置
R-000b在任何模型forward前因transformers版本缺少Qwen3VL类而失败；该环境现已修复并通过Qwen3 class、CUDA与pip check gate。

## 研究依据 / 被审计对象
旧E008-R-000失败日志；E005-R-029c manifest；E003-R-004b generated_texts；公共iplocid tests。

## 实现方式（简版）
公共iplocid role_audit_pipeline以--limit 4运行exact teacher replay，按query image path匹配E003 archived output。

## 实现方式（详细版）
Q→Q使用query GT/grid，Q→R/G→R使用reference GT/grid；conda:IPLoc证明、固定tmux、allowlist写路径和已审核command继续强制。tmux-guarded不隐藏宿主可读目录且无法强制断网，已由人类接受。

## 数据身份与构造
E003-R-004b positive n140 manifest前4样本；E003 generated_texts按query image path唯一匹配；不修改manifest/response/head/指标。

## 数据规模
n=4 exact teacher replay；不产生n140科学结论。

## 模型、权重与关键配置
Qwen3-VL-8B-Instruct+IPLoc-ID 1shot LoRA；conda:IPLoc；bf16 eager；max_side=640。

## 变量、干预与对照
G-heads=[L15H13,L16H23,L18H15]；L-heads=[L18H15,L19H03,L22H00,L20H08]；无attention/activation干预。

## 指标与计数规则
exact replay、row/span唯一匹配、finite、四种边的raw map及GT fractional metrics仅作工程审计。

## 完整性门槛 / no-silent-zero
4/4 records或显式失败；模型/LoRA/manifest/source output本地存在；conda:IPLoc proof；public package tests；固定head和双图span；tmux-guarded路径allowlist。

## 竞争假设与预期特征
若4/4通过，说明公共pipeline与新环境可进入R-001审核；若失败，保留失败记录，不变更科研变量。

## 验收条件
4/4 token/row/span/grid/head/finite gate通过，生成summary、raw npz和显式failure records。

## 依赖的 Run / 证据
E005-R-029c；E003-R-004b；旧E008-R-000失败日志；mechanism/iplocid公共包。

## 观测结果摘要
（待补充）

## 局限与混杂因素
tmux-guarded为人类接受的降级隔离：宿主可读目录不可被内核隐藏、网络不可强制隔离；n4无科学结论。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
仅支持公共pipeline工程正确性；不支持head role、identity、因果或行为结论。

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-008/events.md; mechanism/iplocid/ARCHITECTURE_MIGRATION.md

## 过程记录与补充细节
Replacement of R-000b after retryable pre-model runtime failure. User explicitly directed immediate execution after the recorded environment repair; scientific variables remain frozen.

## 指标观测
（尚无结构化观测）

## Run 审核
### 用户补充要求
（待补充）
### 用户疑问
（待补充）
### Agent 完善说明
（待补充）
### Agent 对疑问的回应
（待补充）
### 本次执行授权备注
（待补充）
### 自动审核快照
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
02

### Git commit / branch
（待补充）

### 运行命令
bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iplocid/tools/run_e008_r000.sh --manifest /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/explog/E-005/runs/E005-R-029c-original140-positive-targets-binding-640/manifests/E003_R004b_positive_targets_n140.json --source-output /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/explog/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128/results/LASOT_local_1shot_T2_n140_v2/generated_texts/e003_r004b_joint_n140.json --run-dir /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-008/E008-R-000c-grounding-heads-query-image-alignment-smoke-n4-tmux-guarded-runtime-retry --model-path /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct --lora-path /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iplocid/pretrained_weights/Qwen3-VL-8B-Instruct_1shot_iplocid --old-data-prefix /home/featurize/data/LaSOTTesting --new-data-prefix /defaultShare/archive/liuwenchu/data/LaSOTTesting --limit 4

### 配置/超参数
/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iplocid/configs/e008/r000_alignment_smoke_n4.yaml

### Seed
20260819

### 日志路径
/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-008/E008-R-000c-grounding-heads-query-image-alignment-smoke-n4-tmux-guarded-runtime-retry/logs/train.log

### 产物目录
/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-008/E008-R-000c-grounding-heads-query-image-alignment-smoke-n4-tmux-guarded-runtime-retry/outputs

### 真实产物根目录
/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-008/E008-R-000c-grounding-heads-query-image-alignment-smoke-n4-tmux-guarded-runtime-retry

### tmux session
incontext-E-008-E008-R-000c-grounding-heads-query-image-alignment-smoke-n4-tmux-guarded-runtime-retry

</details>

## 解析后的执行环境
- server: 02 · lwc-IPLoc
- ssh_host: NKU-LWC
- workspace: 02
- remote_repo: /defaultShare/archive/liuwenchu/projects/IPLoc
- remote_data_root: /defaultShare/archive/liuwenchu/data/LaSOTTesting
- project_dir: /defaultShare/archive/liuwenchu/projects/IPLoc/E-008
- run_dir: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-008/E008-R-000c-grounding-heads-query-image-alignment-smoke-n4-tmux-guarded-runtime-retry
- log_file: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-008/E008-R-000c-grounding-heads-query-image-alignment-smoke-n4-tmux-guarded-runtime-retry/logs/train.log
- output_dir: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-008/E008-R-000c-grounding-heads-query-image-alignment-smoke-n4-tmux-guarded-runtime-retry/outputs
- metrics_file: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-008/E008-R-000c-grounding-heads-query-image-alignment-smoke-n4-tmux-guarded-runtime-retry/metrics.json
- tmux_session: incontext-E-008-E008-R-000c-grounding-heads-query-image-alignment-smoke-n4-tmux-guarded-runtime-retry
- launcher: ssh NKU-LWC
- environment_activation: conda:IPLoc
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 Steward/Watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-19T16:20:18
- updated: 2026-08-19T16:20:18

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
