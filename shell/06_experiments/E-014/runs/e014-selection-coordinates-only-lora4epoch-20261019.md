# e014-selection-coordinates-only-lora4epoch-20261019 · 用户明确授权训练4epoch无画框版本：原始Reference/Query图像+文字Reference bbox及候选bbox列表，无任何叠加框或视觉编号，候选

- 父 Run：`e014-selection-fulltrain-gt-lora5epoch-20261019`
- 来源版本：2026-10-19T08:14:14
- 状态：failed
- Workspace：03

## 本次任务
用户明确授权训练4epoch无画框版本：原始Reference/Query图像+文字Reference bbox及候选bbox列表，无任何叠加框或视觉编号，候选编号仍在文字中。复用原8379条/3571源、同候选置换/729GT补框/答案/seed，仅改变输入呈现并删除颜色框线说明。fresh独立Qwen3VL8B NF4语言LoRA r8alpha16/globalbatch16/lr5e-5/vision4096/seed20260901，initialize/resume None，4epoch，每.5epoch保存，原loss门禁不变。不自动评测，不启Steward或短周期轮询；失败不自动重试。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 命令：set -euo pipefail; export IPLOC_PYTHON=/songzhengyue/miniconda3/envs/IPLoc/bin/python PYTHONPATH=. OMP_NUM_THREADS=1; mkdir /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019/payload; bash tools/run.sh configs/sft/candidate_selection_lora.py --cfg-options work_dir=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019/payload/training model.model_path=/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct train_dataloader.dataset.ann_file=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019/inputs/train.json train_dataloader.dataset.ann_file_sha256=9893487cc57f49473fca000a8b6f0af759843982abfeadf0328908e1e23be40f runner.max_epochs=4 runner.initialize_from=None runner.resume_from=None; /songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import json,hashlib;from pathlib import Path;p=Path("/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019/payload/training/metrics.json");m=json.loads(p.read_text());assert m["status"]=="passed";s={k:v for k,v in m.items() if isinstance(v,(str,int,float,bool)) or v is None};s.update(full_metrics_path=str(p),full_metrics_sha256=hashlib.sha256(p.read_bytes()).hexdigest());f=Path("/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019/metrics.json").open("x");json.dump(s,f,indent=2,allow_nan=False);f.close()'; echo SURVEY_TOOL_RUN_COMPLETE
- 代码版本：53ab7653602f62ffc1d5c9dadfbefccf7ad67474
- 随机种子：20260901
- 配置：configs/sft/candidate_selection_lora.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019/metrics.json

## 结果
尚无结果。

### Claim 边界
只训练，不宣称无框优于画框；需后续独立授权验证。同数据补GT信息保留但不显式标注GT，模型输入没有IoU/评分/类别。原训练/测试复用限制保持，Claim不改。

### 审核入口
.pi/analysis/e014/selection-sft/coordinates_only_data_audit.json
.pi/analysis/e014/selection-sft/coordinates_only_train_command.json

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
