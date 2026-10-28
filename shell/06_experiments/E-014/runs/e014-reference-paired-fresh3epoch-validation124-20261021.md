# e014-reference-paired-fresh3epoch-validation124-20261021 · 用户已明确要求运行成对监督对照。真实359train pairs导出718行A/B监督，fresh同seed LoRA/3epochs135更新2160呈现，最

- 父 Run：`e014-real-reference-pairs-preparation-r2-20261021`
- 来源版本：2026-10-21T01:09:35
- 状态：failed
- Workspace：03

## 本次任务
用户已明确要求运行成对监督对照。真实359train pairs导出718行A/B监督，fresh同seed LoRA/3epochs135更新2160呈现，最终124条/62pairs验证并统计双题均正确、换Reference选择变化；与A-only同预算。等待控制arm释放GPU后执行，记录编号分布混杂，复用已部署共享训练评测入口，不额外确认。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户明确执行配对方向。真实接受359train/62validation pairs，129/23视频隔离。此arm=paired，每pair各Reference A/B两行；两arm各718行、fresh原始Qwen3VL8B独立LoRA，初始化/训练seed20260901，NF4/r8alpha16/无框exact_instance/编号EOS/8GPU/globalbatch16/lr5e-5/warmup.05/clip.3。各3epoch=135更新、2160实际呈现（目标样本2154，modulo补齐6）。只最终checkpoint samples_00002154_step_000135评测124条/62pair，BF16SDPA/greedy16/EOS/vision4096，保存双题均正确与换Reference选项变化。A-only与配对的编号分布不同，是已记录混杂，不将差异单独归因Reference机制。固定等待前一任务释放GPU，文件事件驱动48h上限，无短周期轮询、无自动重跑。科学门禁原样。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-paired-fresh3epoch-validation124-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'a7f121fe0ebd7ed925af43ca3b97df5584ccba066a0c6ece92255a15a678c852'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：7caae090351c9c71ce65fd8c98a0bbbbb1825bc6
- 随机种子：20260901
- 配置：configs/sft/candidate_selection_lora.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-paired-fresh3epoch-validation124-20261021/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-paired-fresh3epoch-validation124-20261021/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-paired-fresh3epoch-validation124-20261021/metrics.json

## 结果
尚无结果。

### Claim 边界
仅生成，绝不补GT/混组/选择SFT或测试集生成，不自动恢复任何旧训练。指标仅描述训练候选而非泛化。legacy evaluator不记录逐例EOS标记；EOS停止默认生效但不是显式终止审计，后续入库需声明限制。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
