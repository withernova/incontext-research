# e015-qwen2-selector-e014data-20261026 · 用户明确要求先用E014丰富选择数据替换当前VQA阶段数据，诊断提升幅度，之后再解决数据来源。原样使用E014冻结21552行/8203 source_inde

- 父 Run：`e015-three-dataset-eval-20261026`
- 来源版本：2026-10-26T15:15:01
- 状态：failed
- Workspace：03

## 本次任务
用户明确要求先用E014丰富选择数据替换当前VQA阶段数据，诊断提升幅度，之后再解决数据来源。原样使用E014冻结21552行/8203 source_index（SHA6d2a9b4f...），全部1参考图，不重建/删改标签或过滤重合；审计与当前评测的源视频/图像重合并披露。Qwen2官方base fresh独立LoRA，保留E015选择器lr5e-5/global16/4epochs/warmup.03/clip.3/seed20260901/末1/4衰减到.1，因此总5388步。保留E014原prompt/候选/编号监督，不加载旧Qwen3 adapter，不重训proposal。固定父联合评测的1/2/4shot共每shot1289条manifest及proposal，重新VQA后和当前selector逐数据集/总体/宏平均对比，报告mIoU/Acc50及mIoU差值。仅诊断，可能含测试来源重合，不能据此声称干净泛化或单因素数据规模因果。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户明确要求先用E014丰富选择数据替换当前VQA阶段数据，诊断提升幅度，之后再解决数据来源。原样使用E014冻结21552行/8203 source_index（SHA6d2a9b4f...），全部1参考图，不重建/删改标签或过滤重合；审计与当前评测的源视频/图像重合并披露。Qwen2官方base fresh独立LoRA，保留E015选择器lr5e-5/global16/4epochs/warmup.03/clip.3/seed20260901/末1/4衰减到.1，因此总5388步。保留E014原prompt/候选/编号监督，不加载旧Qwen3 adapter，不重训proposal。固定父联合评测的1/2/4shot共每shot1289条manifest及proposal，重新VQA后和当前selector逐数据集/总体/宏平均对比，报告mIoU/Acc50及mIoU差值。仅诊断，可能含测试来源重合，不能据此声称干净泛化或单因素数据规模因果。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014data-20261026/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'4306fda8d72439a3f2a900f2e7835b37e10776085935d5de8fe4cf7c413694aa'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：28c72afff503650316e37039c5931f2587b62b45
- 随机种子：20260901
- 配置：configs/experiments/E-015/selector.py + tools/evaluate_candidate_vqa.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014data-20261026/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014data-20261026/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014data-20261026/metrics.json

## 结果
尚无结果。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
