# e014-historical-balanced-vqa-lora4epoch-20261019 · 用户授权用新收集历史候选训练VQA4epoch。fresh独立无框原图+文字bbox选择LoRA，不继承旧1310权重，不做自动评测。先构造原生合格组（精确框/

- 父 Run：`e014-historical-three-source-train8367-generation-20261019`
- 来源版本：2026-10-19T20:25:15
- 状态：failed
- Workspace：03

## 本次任务
用户授权用新收集历史候选训练VQA4epoch。fresh独立无框原图+文字bbox选择LoRA，不继承旧1310权重，不做自动评测。先构造原生合格组（精确框/集合去重，保留来源），补少量oldstep200无好框时跨来源好框+真实错框互补组；所有来源均无好框时按既有规则训练专用补GT。K>=2/Oracle>=.5/gap>.05。分层均衡静态清单：三数据集各相同曝光量，至少覆盖所有可用独立图像对一次；dataset内每源曝光差<=1，每次选择一组与一个编号置换。固定seed20260901，清单冻结后训练4遍（不是每epoch动态重采样），不按候选或rotation数量增加原样本权重；实际epoch行数/更新数在数据验收后登记。复用现有dataset/runner与NF4r8alpha16/globalbatch16/lr5e-5/vision4096/.5epoch存档/原loss门禁。只训练，不恢复旧Run，不自动retry或扩预算。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 命令：set -euo pipefail; export IPLOC_PYTHON=/songzhengyue/miniconda3/envs/IPLoc/bin/python PYTHONPATH=. OMP_NUM_THREADS=1; mkdir /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-balanced-vqa-lora4epoch-20261019/payload; bash tools/run.sh configs/sft/candidate_selection_lora.py --cfg-options work_dir=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-balanced-vqa-lora4epoch-20261019/payload/training model.model_path=/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct train_dataloader.dataset.ann_file=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-balanced-vqa-lora4epoch-20261019/inputs/train.json train_dataloader.dataset.ann_file_sha256=6d2a9b4fcd6825736aa3534afd6b2de895da4f45352d79246ef11125cd2ffc21 runner.max_epochs=4 runner.initialize_from=None runner.resume_from=None; /songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import json,hashlib;from pathlib import Path;p=Path("/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-balanced-vqa-lora4epoch-20261019/payload/training/metrics.json");m=json.loads(p.read_text());assert m["status"]=="passed";s={k:v for k,v in m.items() if isinstance(v,(str,int,float,bool)) or v is None};s.update(full_metrics_path=str(p),full_metrics_sha256=hashlib.sha256(p.read_bytes()).hexdigest());f=Path("/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-balanced-vqa-lora4epoch-20261019/metrics.json").open("x");json.dump(s,f,indent=2,allow_nan=False);f.close()'; echo SURVEY_TOOL_RUN_COMPLETE
- 代码版本：53ab7653602f62ffc1d5c9dadfbefccf7ad67474
- 随机种子：20260901
- 配置：configs/sft/candidate_selection_lora.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-balanced-vqa-lora4epoch-20261019/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-balanced-vqa-lora4epoch-20261019/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-balanced-vqa-lora4epoch-20261019/metrics.json

## 结果
尚无结果。

### Claim 边界
不自动评测/恢复旧训练。比旧训练集与预算同时变化，不是单变量；数据集曝光均衡非独立样本均衡。静态清单重复四遍且池非全部组被采样，不能称每epoch动态采样。legacy原始生成不存EOS标记，保留此限制；不声称全部都是VQA难例。

### 审核入口
.pi/analysis/e014/historical-candidate-sources-20261019/balanced_training_data_audit.json
.pi/analysis/e014/historical-candidate-sources-20261019/balanced_train_command.json

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
