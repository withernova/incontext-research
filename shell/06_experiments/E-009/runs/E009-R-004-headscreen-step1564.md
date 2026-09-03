# E009-R-004-headscreen-step1564 · 训练后段 checkpoint 1564 的固定样本 head screening

- workflow: v2 / research_design / 研究设计
- review_status: changes_requested
- group_id: 未分组
- execution_dispatch:  / 

## 1. 研究设计
### 研究问题
父训练轨迹在 step 1564 保存的 LoRA checkpoint，是否在同一冻结样本集上产生可与相邻后段 checkpoint 直接比较的 query/reference Top-3 与 Top-5 attention head 集合？
### 本轮目的
只对 step 1564 做一次不更新参数的 teacher-forced head screening；与另外四个后段 checkpoint 保持数据、seed、probe 和 finder 完全一致，用于后续判断找到的 head 是否随训练后段稳定。
### 假设或比较预期
若训练后段已形成稳定的 attention head 排序，则相邻 checkpoints 的 query/reference Top-3 与 Top-5 集合应保持较高重合；否则集合会持续替换。
### 数据与主要变量
/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-real-focus-data/manifests/val_lasot_posthoc_fixed100_1shot_focus.json；固定 100 行、target_role=positive-image、prompt_protocol=focus。该 manifest 用于 head 发现/核验，预留 combined test 不参与。

五条计划 Run 中唯一变化是 parent_checkpoint；本 Run 固定 step=1564。manifest、100 个样本身份、seed=20260901、row contract、excluded layers、Top-k、finder reward 与 artifact dtype 全部一致。

## 2. 指标设计
本 Run 只产生可比较的固定 Top-k 集合和完整性字段；最终稳定性不由单 Run 判定，而由五条 completed 输出经 analyze_head_stability.py 汇总。
## 3. 代码架构
复用 configs/sft/e009_qwen3vl8b_1shot_branch.py、tools/run/run_e009_branch.sh 和现有 probe/finder；新增 tools/analyze_head_stability.py 仅做离线集合一致性核验与汇总，不修改训练器。
- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `bash tools/run/run_e009_branch.sh branch.action=head_screen named_run.parent_checkpoint=/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/checkpoints/samples_00100073_step_001564 named_run.run_name=head-stability-step1564`
- commit: ``
- workspace: 02
- tmux: incontext-E-009-E009-R-004-headscreen-step1564
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-R-004-headscreen-step1564/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-R-004-headscreen-step1564/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
teacher-forced attention 排序是描述性、非因果诊断；reference T003 在发现中使用 GT；单一 100 行 manifest 不能证明预留测试集泛化。

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "单个 checkpoint 的 head 集合无法区分稳定结构与偶然排序；必须沿同一可信父训练轨迹对多个相邻后段 checkpoint 做同协议测量。",
  "evidence_basis": "只读文件核验确认 /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/checkpoints/samples_00100073_step_001564/adapter 下存在 adapter_config.json 与非空 adapter_model.safetensors；当前没有 Solid Run，因此这里只作为可执行输入定位，不作为效果证据。",
  "implementation_summary": "复用 E-009 branch 的 standalone head_screen 动作，加载该 checkpoint 的 adapter，在冻结的 100 行验证 manifest 上一次性采集全部样本；不恢复优化器、不训练、不读取预留测试集。",
  "implementation_details": "4 个 rank 各处理固定索引切片；probe 使用 teacher_forced_query_bbox_pminus1/v1 row contract，临时 eager attention，仅保存 float16 attention map；finder 同时输出无 GT 的 query R003 集合与使用 reference GT reward 的 T003 reference 集合。跨 checkpoint 稳定性由 tools/analyze_head_stability.py 离线核验样本身份和参数一致后汇总，不能使用单次运行的 stable_candidate。",
  "model_config": "Qwen3-VL-8B-Instruct + 父训练轨迹 step 1564 的 NF4 LoRA adapter；4 GPU DDP 仅用于并行采集；正常模型保持 SDPA，probe forward 临时切 eager attention。",
  "metric_definition": "每个 Run 输出 query R003 Top-3/Top-5 与 reference T003 Top-3/Top-5、完整 ranking 和 100 条 probe records。五条 Run 完成后报告相邻 checkpoint Jaccard、相对首 checkpoint 的 exact-match fraction、全 checkpoint 交集/并集和逐 head 出现频率；query 与 reference 分开报告。",
  "integrity_gates": "运行前 adapter_config.json、adapter_model.safetensors、trainer_state.pt 与 100 行 manifest 均存在；运行后 status=completed、records=100、failures 为空、所有样本身份与另外四条 Run 一致、schema/row contract/head shape/finder parameters 完全相同、Top-3/Top-5 均为唯一合法 head。任一失败则该 checkpoint 不进入稳定性汇总。",
  "expected_outcome": "得到该 checkpoint 的两类 Top-3/Top-5 集合和完整 ranking，为后续跨 checkpoint 比较提供一个等协议观测点；本 Run 自身不预设其一定稳定。",
  "acceptance_criteria": "standalone screening 正常完成且 100/100 records 有效；输出 latest.json 可被 analyze_head_stability.py 与其余四条 Run 一起通过 comparability gate。",
  "claim_boundary": "只允许判断同一父训练轨迹后五个 checkpoint 在固定验证样本上的 attention head 集合稳定性；不得声称这些 head 具有因果功能、对测试集稳定，或自动决定最佳 checkpoint。",
  "audit_paths": "configs/sft/e009_qwen3vl8b_1shot_branch.py; tools/analyze_head_stability.py; tests/test_analyze_head_stability.py; head_screening/latest.json"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
