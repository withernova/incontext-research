# e014-cover-min-cap5-step150-eval1766-8gpu · 最新min覆盖/cap5分支step150、multi_v2、原1766八卡评测

- workflow: v2 / failed / 运行失败
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-ec48ad5e7a2cda73110568a3 / failed

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
min覆盖/cap5训练step150是否仍仅单框，其Selected/Oracle与定位如何？

## 2. 目的
用户要求暂停最新训练并测试该分支step150，先核查真实候选数和定位结果，再讨论更明确奖励，不自动改reward或恢复训练。

**假设或预期**：奖励改变可能增加有效多框，未验证；训练实际合法多框已迅速减少，结果可能仍单框，不补造/过滤输出。

## 3. 方法（干预 · 对照 · 指标与判定规则）
本分支CP150、原1766、8卡greedy192/4096/multi_v2独立只读评测，共享入口，不额外训练/模型探针。

**干预与对照**：实际prompt=multi_v2，SHAc6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba，multiple distinct/不同实例/两行模板/左到右/Reference同实例score；不固定候选数。greedy192、4096visionpatch、seed20260901、8replicas原设置。GT只事后IoU/Oracle，不进Query输入或score选框。

**指标计划**：原始框数与候选质量优先，Selected/Oracle/First和IoU命中/score AP；对照不同更新量仅探索描述。结合mixed分母/条件窗，null不视0。

**指标计算定义**：先raw answer数/parsed候选分布/合法率/重复/空间顺序，再First/Selected/Oracle mIoU/OracleGap/nonfirst及IoU阈值/score选中单框AP(有效GT1756与全部1766口径)。训练窗口只旁证：1–50 validmulti63/3200/mixed16/800/q33.854%/mean差-.111861；51–100无multi或mixed，q=null；101–150 multi1/3200/mixed1/q0/mean差-.910046。

**判定门槛 / no-silent-zero**：CP归属当前新分支且saved_step150/min/cap5/multi_v2/hash；原manifestSHA及1766、registered readonly images；Gitclean/指定SHAdeploy/原condaIPLoc/8GPU idle不杀其他任务；payload独占不覆盖；全部index/unique ID/world8/source SHA前后；实际prompt/config一致。

**验收判定**：真实exit0/完成标记/metrics；1766完整唯一覆盖/world8/CP150本分支/multi_v2/c6f28d...实际prompt、greedy192/4096；原始/选中输出及输入来源hash齐全；paused训练/旧Run产物保持。

**预期特征**：获得CP150的真实多框与定位/选择表现，不预设改善，不把框数多当收益。

## 4. 详细实现细节
新profile绑定本min/cap5训练payload/grpo/checkpoints/step_000150、variantmulti_v2和新独占输出。preflight源步数/prompt/hash，inputs记录training_reward且config核验min/cap5；post检查实际prompt_example/resolved/CP/参数/indices/ID/source hash。newcfg+2shell块3.9AST、2bash-n/model-free inspect/diff通过，5核心eval/trainer/reward/observer byte未改，无测试套件/模型。

**数据身份与构造**：原E009 test_combined_lasot600_gotval_taoval_1shot_focus.json，SHA48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b，唯一变化image_path注册alias；原图/GT/身份/来源/split保持。

**数据规模**：全部1766，LaSOT600/GOT10k180/TAO986；8rank indices[rank::8]应221*6+220*2，不抽样/新split。

**模型与关键配置**：Qwen3-VL-8B-Instruct NF4/bfloat16/SDPA，加载e014-multi-v2-cover-min-cap5-sft659-puregrpo-seed11451/payload/grpo/checkpoints/step_000150/adapter/policy，LoRA配置来自该adapter；不是旧分支200/800，未使用151–154更新。

**代码架构**：只profile/config/薄shell，共享tools/evaluate.py、E14 dataset/evaluator、checkpointing与AP；训练core/reward/observer未改。

**实现摘要**：只4文件：固定profile/config/薄shell/文档；复用tools/evaluate.py和原E14 evaluator/shared准备+AP。review68b1b85f9a38debd通过，提交并publishc646ba12265b11d1144cf97e3780370848a46f61，未deploy/模型执行。

- 公共包：`iploc_szy`
- 入口：`tools.evaluate:main`
- 配置：`configs/experiments/E-014/evaluation/e014_cover_min_cap5_step150_eval1766.py`
- Shell launcher：`tools/run/analysis/e014/e014_cover_min_cap5_step150_eval1766_8gpu.sh`
- 复用模块：tools/evaluate.py, iploc_szy/evaluation/e014.py, iploc_szy/prompting/e014.py, iploc_szy/checkpointing.py, tools/run/analysis/e014/e014_step800_eval1766_8gpu.sh, tools/analysis/run_e013_multi_candidate.py
- 新增模块：（待登记）
- 测试路径（不代表已执行）：（未登记，可留空）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `bash tools/run/analysis/e014/e014_cover_min_cap5_step150_eval1766_8gpu.sh`
- commit: `c646ba12265b11d1144cf97e3780370848a46f61`
- workspace: 03
- tmux: e014-min-cap5-step150-eval
- log: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-cover-min-cap5-step150-eval1766-8gpu/managed_console.log
- output: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-cover-min-cap5-step150-eval1766-8gpu/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
测试集已多次看，仅探索诊断；旧800/200与本150预算不同不单因素归因reward。退化GT需valid分母；AP最终单框单GT不完整检测AP；192预算可能截断；mixed组少且有条件选择偏差，新观测未出现高q而multi下降，不据此称纯Exploration瓶颈。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "necessity": "此前multi_v2 200全部1766greedy单框。新min/cap5训练诊断也显示multi率下降，需要只读CP150正式诊断输出；不能把训练reward统计当测试定位结果。",
  "evidence_basis": "已managed fail主动暂停(nonretryable/authorization)，仅SIGTERM唯一核验coordinator78445和自有workers；8卡无compute PID，真实payload.exit_code130，各rank末153–154。CP150 optimizer.steps150/504state，policy964byte/87368144byte权重/175012555byte optimizer完整；snapshot确认为multi_v2/c6f28d...、min coverage/cap5超额.05/新权重。",
  "implementation_summary": "只4文件：固定profile/config/薄shell/文档；复用tools/evaluate.py和原E14 evaluator/shared准备+AP。review68b1b85f9a38debd通过，提交并publishc646ba12265b11d1144cf97e3780370848a46f61，未deploy/模型执行。",
  "implementation_details": "新profile绑定本min/cap5训练payload/grpo/checkpoints/step_000150、variantmulti_v2和新独占输出。preflight源步数/prompt/hash，inputs记录training_reward且config核验min/cap5；post检查实际prompt_example/resolved/CP/参数/indices/ID/source hash。newcfg+2shell块3.9AST、2bash-n/model-free inspect/diff通过，5核心eval/trainer/reward/observer byte未改，无测试套件/模型。",
  "model_config": "Qwen3-VL-8B-Instruct NF4/bfloat16/SDPA，加载e014-multi-v2-cover-min-cap5-sft659-puregrpo-seed11451/payload/grpo/checkpoints/step_000150/adapter/policy，LoRA配置来自该adapter；不是旧分支200/800，未使用151–154更新。",
  "metric_plan": "原始框数与候选质量优先，Selected/Oracle/First和IoU命中/score AP；对照不同更新量仅探索描述。结合mixed分母/条件窗，null不视0。",
  "data_definition": "原E009 test_combined_lasot600_gotval_taoval_1shot_focus.json，SHA48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b，唯一变化image_path注册alias；原图/GT/身份/来源/split保持。",
  "data_scale": "全部1766，LaSOT600/GOT10k180/TAO986；8rank indices[rank::8]应221*6+220*2，不抽样/新split。",
  "variables_controls": "实际prompt=multi_v2，SHAc6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba，multiple distinct/不同实例/两行模板/左到右/Reference同实例score；不固定候选数。greedy192、4096visionpatch、seed20260901、8replicas原设置。GT只事后IoU/Oracle，不进Query输入或score选框。",
  "metric_definition": "先raw answer数/parsed候选分布/合法率/重复/空间顺序，再First/Selected/Oracle mIoU/OracleGap/nonfirst及IoU阈值/score选中单框AP(有效GT1756与全部1766口径)。训练窗口只旁证：1–50 validmulti63/3200/mixed16/800/q33.854%/mean差-.111861；51–100无multi或mixed，q=null；101–150 multi1/3200/mixed1/q0/mean差-.910046。",
  "integrity_gates": "CP归属当前新分支且saved_step150/min/cap5/multi_v2/hash；原manifestSHA及1766、registered readonly images；Gitclean/指定SHAdeploy/原condaIPLoc/8GPU idle不杀其他任务；payload独占不覆盖；全部index/unique ID/world8/source SHA前后；实际prompt/config一致。",
  "expected_outcome": "获得CP150的真实多框与定位/选择表现，不预设改善，不把框数多当收益。",
  "acceptance_criteria": "真实exit0/完成标记/metrics；1766完整唯一覆盖/world8/CP150本分支/multi_v2/c6f28d...实际prompt、greedy192/4096；原始/选中输出及输入来源hash齐全；paused训练/旧Run产物保持。",
  "claim_boundary": "工程complete不等于收益。保留raw输出再解释单框/多框；无因果Claim/独立确认集，不自动变框数奖励，不自动评测其他CP/重跑/resume。",
  "audit_paths": "docs/e014_cover_min_cap5_step150_evaluation.md; payload/inputs.json; payload/manifest.json; payload/evaluation/predictions.jsonl; payload/evaluation/metrics.json; payload/logs/config_snapshots; metrics.json; local shell/06_experiments/E-014/visualizations/cover-min-cap5-step150-20261012/training_window_audit.json及原窗口/SHA"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
