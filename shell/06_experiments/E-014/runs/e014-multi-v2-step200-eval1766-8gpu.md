# e014-multi-v2-step200-eval1766-8gpu · multi_v2本分支step200、原1766样本八卡评测

- workflow: v2 / analysis_pending / 结果分析
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-860e5ea171b6067c17c7a52b / completed

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
multi_v2训练step200在原1766查询上是否真实输出更多不同候选，其定位和score选择表现如何？

## 2. 目的
用户要求暂停当前multi_v2训练并评测step200；只读单checkpoint原1766样本八卡评测，不自动恢复训练。

**假设或预期**：多候选文案可能减少单框输出，效果未验证；允许保持单框、重复或截断作为真实结果，不补造候选。

## 3. 方法（干预 · 对照 · 指标与判定规则）
独立只读CP200，E14 variantmulti_v2，冻结原1766、8卡greedy192/4096，优先核查输出数量，再分析定位/Oracle与score。

**干预与对照**：新multi_v2完整prompt SHA c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba：multiple distinct/尽量枚举不同实例/不重复/两行模板；左到右、Reference同实例score保持；不固定2或3、不加regardless of confidence。greedy192new tokens/4096vision patch tokens/8卡与旧评测同设置；GT仅事后IoU/Oracle，不进入Query输入或score选框。

**指标计划**：原始answer数/合法率/候选直方图/重复/空间顺序；First/Selected/Oracle与逐样本差距；IoU命中/score/selected-box AP。先完整覆盖核验，后探索性解释。

**指标计算定义**：原始answer数/候选数量/格式/重复/顺序优先；Selected/First/Oracle mIoU、OracleGap、selected_nonfirst与nonfirst_acc/样本数、IoU阈值命中及dataset分组；existing AP25/50/75/AP50-95分别valid-GT与全部query口径，为最终单选框单GT AP，不是完整检测AP。

**判定门槛 / no-silent-zero**：source train snapshot为multi_v2且hashc6f28d...、optimizer.saved_step200、正确分支；原manifest SHA及1766；全部图像registered alias；源Git clean/指定SHA部署；8GPU空闲不停止其他任务；独占payload拒绝覆盖；原始/源文件SHA前后一致；实际eval snapshot prompt/config检查；完整indices/unique IDs。

**验收判定**：真实exit0及完成标记；1766唯一样本全覆盖、world_size8、CP200/variantmulti_v2/c6f28d...实际prompt一致；greedy192/4096；原始/选中预测、native metrics、Root metrics.json及来源hash完整；暂停训练产物不变。

**预期特征**：获得新训练200步是否真实输出多个不同候选及其定位/score表现，不预设改善。

## 4. 详细实现细节
复用tools/evaluate.py、E14 dataset/evaluator、旧shell准备和AP统计。新profile绑定本multi_v2训练payload/grpo/checkpoints/step_000200、prompt_variant=multi_v2和新Run输出。评测前校验源optimizer步数/prompt variant/hash；评测后校验实际prompt_example/resolved参数、1766indices/unique IDs、source hashes；旧profile默认仍v1_step800。Python3.9 config/2shell块AST、2bash-n、两profile model-free inspect、diff-check通过，无测试套件或模型验证。

**数据身份与构造**：原E009 test_combined_lasot600_gotval_taoval_1shot_focus.json，SHA48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b；仅派生image_path到现有注册只读aliases，原图/清单/标签/GT/身份/split/来源保持。

**数据规模**：全部1766：LaSOT600/GOT10k180/TAO986；不抽样、不新split；8rank按indices[rank::8]覆盖，应221*6+220*2。

**模型与关键配置**：原Qwen3-VL-8B-Instruct，NF4/bfloat16/sdpa；只加载e014-multi-v2-symmetric-sft659-puregrpo-seed11451/payload/grpo/checkpoints/step_000200/adapter/policy。LoRA r/alpha/dropout/targets由此adapter只读config确定；不是旧step800或SFT adapter。

**代码架构**：共享tools/evaluate.py和既有models/checkpointing/E14 dataset/evaluator；只有薄config/shell profile，旧默认不变，没有新推理/分片/合并核心。

**实现摘要**：仅4文件config/薄shell/文档和共享shell profile；不改训练核心，不新建Python评测协调器。审阅1c278cc95a88446f通过，提交/发布a8ac7768142d0707b9380cc7d03f137c2c6c7ee6；未部署、未模型执行。

- 公共包：`iploc_szy`
- 入口：`tools.evaluate:main`
- 配置：`configs/experiments/E-014/evaluation/e014_multi_v2_step200_eval1766.py`
- Shell launcher：`tools/run/analysis/e014/e014_multi_v2_step200_eval1766_8gpu.sh`
- 复用模块：tools/evaluate.py, iploc_szy/evaluation/e014.py, iploc_szy/prompting/e014.py, iploc_szy/checkpointing.py, tools/run/analysis/e014/e014_step800_eval1766_8gpu.sh, tools/analysis/run_e013_multi_candidate.py
- 新增模块：（待登记）
- 测试路径（不代表已执行）：（未登记，可留空）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `bash tools/run/analysis/e014/e014_multi_v2_step200_eval1766_8gpu.sh`
- commit: `a8ac7768142d0707b9380cc7d03f137c2c6c7ee6`
- workspace: 03
- tmux: e014-multi-v2-step200-eval
- log: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-step200-eval1766-8gpu/managed_console.log
- output: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-step200-eval1766-8gpu/outputs
- Steward 摘要：```json
{
  "execution_completed_at": "2026-10-12T16:56:41",
  "evidence": {
    "log": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-step200-eval1766-8gpu/managed_console.log",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-step200-eval1766-8gpu/metrics.json",
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
  "necessity": "旧v1 step800全1766只有一框；本次检查multi_v2新训练step200的真实候选数/多样性、定位和score选框，不以prompt指令代替效果证据。",
  "evidence_basis": "已managed fail(authorization/主动暂停)释放训练attempt，仅SIGTERM已核验唯一coordinator56409并清理自有workers；GPU无compute PID，payload.exit_code130，各rank末204。CP200 optimizer.steps200/504state，policy config964bytes/weights87368144bytes/optimizer175012555bytes；实际训练prompt_variant=multi_v2、SHA c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba。",
  "implementation_summary": "仅4文件config/薄shell/文档和共享shell profile；不改训练核心，不新建Python评测协调器。审阅1c278cc95a88446f通过，提交/发布a8ac7768142d0707b9380cc7d03f137c2c6c7ee6；未部署、未模型执行。",
  "implementation_details": "复用tools/evaluate.py、E14 dataset/evaluator、旧shell准备和AP统计。新profile绑定本multi_v2训练payload/grpo/checkpoints/step_000200、prompt_variant=multi_v2和新Run输出。评测前校验源optimizer步数/prompt variant/hash；评测后校验实际prompt_example/resolved参数、1766indices/unique IDs、source hashes；旧profile默认仍v1_step800。Python3.9 config/2shell块AST、2bash-n、两profile model-free inspect、diff-check通过，无测试套件或模型验证。",
  "model_config": "原Qwen3-VL-8B-Instruct，NF4/bfloat16/sdpa；只加载e014-multi-v2-symmetric-sft659-puregrpo-seed11451/payload/grpo/checkpoints/step_000200/adapter/policy。LoRA r/alpha/dropout/targets由此adapter只读config确定；不是旧step800或SFT adapter。",
  "metric_plan": "原始answer数/合法率/候选直方图/重复/空间顺序；First/Selected/Oracle与逐样本差距；IoU命中/score/selected-box AP。先完整覆盖核验，后探索性解释。",
  "data_definition": "原E009 test_combined_lasot600_gotval_taoval_1shot_focus.json，SHA48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b；仅派生image_path到现有注册只读aliases，原图/清单/标签/GT/身份/split/来源保持。",
  "data_scale": "全部1766：LaSOT600/GOT10k180/TAO986；不抽样、不新split；8rank按indices[rank::8]覆盖，应221*6+220*2。",
  "variables_controls": "新multi_v2完整prompt SHA c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba：multiple distinct/尽量枚举不同实例/不重复/两行模板；左到右、Reference同实例score保持；不固定2或3、不加regardless of confidence。greedy192new tokens/4096vision patch tokens/8卡与旧评测同设置；GT仅事后IoU/Oracle，不进入Query输入或score选框。",
  "metric_definition": "原始answer数/候选数量/格式/重复/顺序优先；Selected/First/Oracle mIoU、OracleGap、selected_nonfirst与nonfirst_acc/样本数、IoU阈值命中及dataset分组；existing AP25/50/75/AP50-95分别valid-GT与全部query口径，为最终单选框单GT AP，不是完整检测AP。",
  "integrity_gates": "source train snapshot为multi_v2且hashc6f28d...、optimizer.saved_step200、正确分支；原manifest SHA及1766；全部图像registered alias；源Git clean/指定SHA部署；8GPU空闲不停止其他任务；独占payload拒绝覆盖；原始/源文件SHA前后一致；实际eval snapshot prompt/config检查；完整indices/unique IDs。",
  "expected_outcome": "获得新训练200步是否真实输出多个不同候选及其定位/score表现，不预设改善。",
  "acceptance_criteria": "真实exit0及完成标记；1766唯一样本全覆盖、world_size8、CP200/variantmulti_v2/c6f28d...实际prompt一致；greedy192/4096；原始/选中预测、native metrics、Root metrics.json及来源hash完整；暂停训练产物不变。",
  "claim_boundary": "不宣称prompt收益、Reference机制或confidence排序成功；需候选数/多样性和有选择难度的逐样本证据。不将主动暂停当训练1500完成，不自动resume或其他checkpoint评测。",
  "artifacts": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-step200-eval1766-8gpu/metrics.json\n/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-step200-eval1766-8gpu/managed_console.log",
  "audit_paths": "docs/e014_multi_v2_step200_evaluation.md; payload/inputs.json; payload/manifest.json; payload/logs/config_snapshots; payload/evaluation/predictions.jsonl; payload/evaluation/metrics.json; metrics.json; 原训练payload完整保留"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
