# e014-step800-variable-candidates-eval1766-8gpu · step800原1766样本八卡变长候选评测

- workflow: v2 / analysis_pending / 结果分析
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-f9173ab253fcabc1a668ae05 / completed

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
checkpoint800在原1766查询上的定位、候选覆盖和score选框表现如何？

## 2. 目的
用户要求先暂停训练，评测step800及原1766样本；不重训、不自动恢复、不做全项目重构。

**假设或预期**：描述性诊断，不预设改善、不构造因果比较。

## 3. 方法（干预 · 对照 · 指标与判定规则）
单checkpoint全样本八卡只读greedy评测，冻结E014协议，复用已有统一评测入口。

**干预与对照**：E014变长候选；按Query bbox中心从左到右，无regardless of confidence，不固定3框；Reference同实例置信度定义；最高score/tie earliest选框。greedy、192 new tokens、4096 vision patch tokens。GT仅事后指标/Oracle，不进入Query生成提示或选框。

**指标计划**：记录selected/first/oracle、格式/数量/顺序/重复及selected-box AP；完整覆盖和原始输出先于科学解释。

**指标计算定义**：selected/first/oracle meanIoU、IoU阈值命中率、候选数/格式/重复/顺序/nonfirst选择；AP50/AP50-95为最终单选框单GT AP，分别报告valid-GT子集和legacy全部query分母；按dataset分组。

**判定门槛 / no-silent-zero**：原manifest SHA一致、1766样本；全部图像存在registered alias；源Git clean且指定SHA部署；8GPU空闲，无停止他人进程；共享合并检查完整index/unique ID；评测前后清单/checkpoint文件SHA不变；独占新payload不覆盖旧产物。

**验收判定**：真实launcher exit0及E014_EVALUATION_COMPLETE；1766唯一样本全覆盖、world_size8；192/4096/greedy参数吻合；原生predictions/metrics及Root metrics.json完整；源文件SHA保持，不影响暂停训练产物。

**预期特征**：获得step800在原测试集上的定位、候选和score诊断；不预设收益。

## 4. 详细实现细节
Config指定checkpoint800、adapter/policy、test_dataloader、8卡、greedy192/4096。仅小修共享checkpoint loader显式policy布局、固定评测checkpoint、E14空assistant占位和合并覆盖检查；E013旧默认不变。薄shell仅元数据准备、只读alias迁移、调用torchrun及现有AP统计。审阅eb3c91173216593f通过，提交已publish；当前未deploy，未执行模型。

**数据身份与构造**：原E009 test_combined_lasot600_gotval_taoval_1shot_focus.json，SHA48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b；只派生image_path到现有mechanism/dataset只读alias，身份/GT/split/来源不变；原数据、checkpoint不改。

**数据规模**：全部1766：LaSOT600/GOT10k180/TAO986；无subset或新split；8rank按indices[rank::8]，应221*6+220*2。

**模型与关键配置**：原Qwen3-VL-8B-Instruct基座，NF4/bfloat16/sdpa；只加载resume-100/grpo/checkpoints/step_000800/adapter/policy；LoRA r/alpha/dropout/targets由该只读adapter config确定。不加载其他GRPO checkpoint。

**代码架构**：共享tools/evaluate.py/模型wrapper/dataset/evaluator；配置表达实验差异、shell薄入口；不另建模型推理/分片/合并框架。

**实现摘要**：复用tools/evaluate.py、E014现有dataset/evaluator及现有AP助手，无新Python评测协调器。

- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试路径（不代表已执行）：（未登记，可留空）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `bash tools/run/analysis/e014/e014_step800_eval1766_8gpu.sh`
- commit: `379df3997cab28c14c64d5dbc11dc64f0ac51e5f`
- workspace: 03
- tmux: e014-step800-eval1766
- log: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-step800-variable-candidates-eval1766-8gpu/managed_console.log
- output: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-step800-variable-candidates-eval1766-8gpu/outputs
- Steward 摘要：```json
{
  "execution_completed_at": "2026-10-12T12:53:53",
  "evidence": {
    "log": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-step800-variable-candidates-eval1766-8gpu/managed_console.log",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-step800-variable-candidates-eval1766-8gpu/metrics.json",
    "result_message": "managed execution exited 0; metrics parsed; human analysis required"
  },
  "note": "程序已结束，等待科研结果分析"
}
```

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
Managed execution exited successfully with 0 declared and 43 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

## 简短局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "necessity": "训练已按用户意图暂停，step800已核验完整。需要独立评测授权和输出，不能借用训练attempt授权。",
  "evidence_basis": "已核验checkpoint optimizer steps=800、504state、policy配置与权重非空；各rank最终805/806，未保存步数后续重算；8卡已无计算进程；原清单SHA及1766覆盖已核验。",
  "implementation_summary": "复用tools/evaluate.py、E014现有dataset/evaluator及现有AP助手，无新Python评测协调器。",
  "implementation_details": "Config指定checkpoint800、adapter/policy、test_dataloader、8卡、greedy192/4096。仅小修共享checkpoint loader显式policy布局、固定评测checkpoint、E14空assistant占位和合并覆盖检查；E013旧默认不变。薄shell仅元数据准备、只读alias迁移、调用torchrun及现有AP统计。审阅eb3c91173216593f通过，提交已publish；当前未deploy，未执行模型。",
  "model_config": "原Qwen3-VL-8B-Instruct基座，NF4/bfloat16/sdpa；只加载resume-100/grpo/checkpoints/step_000800/adapter/policy；LoRA r/alpha/dropout/targets由该只读adapter config确定。不加载其他GRPO checkpoint。",
  "metric_plan": "记录selected/first/oracle、格式/数量/顺序/重复及selected-box AP；完整覆盖和原始输出先于科学解释。",
  "data_definition": "原E009 test_combined_lasot600_gotval_taoval_1shot_focus.json，SHA48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b；只派生image_path到现有mechanism/dataset只读alias，身份/GT/split/来源不变；原数据、checkpoint不改。",
  "data_scale": "全部1766：LaSOT600/GOT10k180/TAO986；无subset或新split；8rank按indices[rank::8]，应221*6+220*2。",
  "variables_controls": "E014变长候选；按Query bbox中心从左到右，无regardless of confidence，不固定3框；Reference同实例置信度定义；最高score/tie earliest选框。greedy、192 new tokens、4096 vision patch tokens。GT仅事后指标/Oracle，不进入Query生成提示或选框。",
  "metric_definition": "selected/first/oracle meanIoU、IoU阈值命中率、候选数/格式/重复/顺序/nonfirst选择；AP50/AP50-95为最终单选框单GT AP，分别报告valid-GT子集和legacy全部query分母；按dataset分组。",
  "integrity_gates": "原manifest SHA一致、1766样本；全部图像存在registered alias；源Git clean且指定SHA部署；8GPU空闲，无停止他人进程；共享合并检查完整index/unique ID；评测前后清单/checkpoint文件SHA不变；独占新payload不覆盖旧产物。",
  "expected_outcome": "获得step800在原测试集上的定位、候选和score诊断；不预设收益。",
  "acceptance_criteria": "真实launcher exit0及E014_EVALUATION_COMPLETE；1766唯一样本全覆盖、world_size8；192/4096/greedy参数吻合；原生predictions/metrics及Root metrics.json完整；源文件SHA保持，不影响暂停训练产物。",
  "claim_boundary": "不证明空间顺序/Reference机制因果收益，不把本次checkpoint评测当独立调参后验证；不将主动暂停记为1500步训练完成。",
  "artifacts": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-step800-variable-candidates-eval1766-8gpu/metrics.json\n/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-step800-variable-candidates-eval1766-8gpu/managed_console.log",
  "audit_paths": "docs/e014_step800_evaluation.md; payload/inputs.json; payload/evaluation/predictions.jsonl; payload/evaluation/metrics.json; metrics.json; 原训练resume-100产物保留"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
