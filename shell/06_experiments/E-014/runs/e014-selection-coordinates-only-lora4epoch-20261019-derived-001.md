# e014-selection-coordinates-only-lora4epoch-20261019-derived-001 · 用户明确要求评测当前无框原图+文字bbox选择器的step1310 checkpoint。固定原1766候选数据，与已有画框版本对照；使用exact_insta

- 父 Run：`e014-selection-coordinates-only-lora4epoch-20261019`
- 来源版本：2026-10-19T08:50:56
- 状态：running
- Workspace：03

## 本次任务
用户明确要求评测当前无框原图+文字bbox选择器的step1310 checkpoint。固定原1766候选数据，与已有画框版本对照；使用exact_instance但不draw-boxes，greedy16/EOS seed20260901 vision4096。仅评测明确指定step1310，不挑其他checkpoint。尚未授权停止父训练；检查checkpoint完整性和GPU占用后决定能否安全执行，不挤占正在训练资源。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 命令：test ! -e /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json && test ! -L /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json && PYTHONPATH=. OMP_NUM_THREADS=1 /songzhengyue/miniconda3/envs/IPLoc/bin/python -m torch.distributed.run --standalone --nproc_per_node=8 tools/evaluate_candidate_vqa.py --manifest /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-score04-step200-eval1766-20261015T152856Z/inputs/manifest.json --manifest-sha256 8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d --predictions /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-score04-step200-eval1766-20261015T152856Z/payload/evaluation/predictions.jsonl --predictions-sha256 1a864fdce10f300ec53ddf2945b7e2d063c74280d7a750207dcff99a7ff76129 --model-path /defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct --output-dir /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/payload --expected-samples 1766 --expected-multi 791 --seed 20260901 --max-new-tokens 16 --vision-max-patch-tokens 4096 --prompt-variant exact_instance --selector-checkpoint /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019/payload/training/checkpoints/samples_00020947_step_001310 && cp /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/payload/metrics.json /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json && echo SURVEY_TOOL_RUN_COMPLETE
- 代码版本：53ab7653602f62ffc1d5c9dadfbefccf7ad67474
- 随机种子：20260901
- 配置：tools/evaluate_candidate_vqa.py (existing no-config CLI)
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json

## 结果
尚无结果。

### Claim 边界
只评测用户指定1310，不选择其它checkpoint；同测试已反复探索，不是无偏测试。与画框step2095训练预算不同，warmup不同，不能单独归因无框。父训练中止1374/2096不是4epoch完成。

### 审核入口
.pi/analysis/e014/selection-sft/coordinates_only_step1310_eval_audit.json

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
