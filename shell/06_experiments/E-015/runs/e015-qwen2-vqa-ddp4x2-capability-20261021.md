# e015-qwen2-vqa-ddp4x2-capability-20261021 · 修正两卡副本早期同步的设备编号，只补跑五图VQA，所有已通过训练阶段不重复；继续E015。

- 父 Run：`e015-qwen2-selector-ddp4x2-capability-20261021`
- 来源版本：2026-10-21T20:16:36
- 状态：failed
- Workspace：03

## 本次任务
修正两卡副本早期同步的设备编号，只补跑五图VQA，所有已通过训练阶段不重复；继续E015。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：只补测八例五图VQA及早期barrier修复；复用父Run已通过selector2步adapter并绑定SHA，原SFT1/2/4shot及恢复哈希再次验证但不重训。前次VQA初始barrier猜错GPU导致模型初始化卡住，SIGTERM仅停止自身torchrun后真实exit1已failed保留。明确barrier设备修复后四rank分别独占01/23/45/67。合成候选仅验证工程，不报告mIoU。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-vqa-ddp4x2-capability-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'86fe9206454825b4bb58bc115715b0f2bff38cc82e926a8ad4e52c007eb657f8'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：53a880b3a7c48b767f6646d6a54fb0e655a624a1
- 随机种子：11451
- 配置：tools/evaluate_candidate_vqa.py --model-family qwen2_vl --devices-per-replica 2
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-vqa-ddp4x2-capability-20261021/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-vqa-ddp4x2-capability-20261021/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-vqa-ddp4x2-capability-20261021/metrics.json

## 结果
尚无结果。

### Claim 边界
仅八视频短程工程能力，非正式性能或GRPO能力。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
