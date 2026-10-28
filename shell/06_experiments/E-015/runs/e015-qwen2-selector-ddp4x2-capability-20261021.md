# e015-qwen2-selector-ddp4x2-capability-20261021 · 修正选择器配置并仅补跑选择训练/五图推理，复核父Run已通过SFT阶段；继续用户授权E015完整任务。

- 父 Run：`e015-qwen2-sft-selector-ddp4x2-capability-20261021`
- 来源版本：2026-10-21T20:01:16
- 状态：failed
- Workspace：03

## 本次任务
修正选择器配置并仅补跑选择训练/五图推理，复核父Run已通过SFT阶段；继续用户授权E015完整任务。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：修复新selector配方的runner类型/基类阈值：SelectionSFTLoRARunner、(.5,)；独立Qwen2 LoRA，4×2，4shot，2次更新/global16，lr5e-5与正式阶段一致。只重跑selector训练与8例5图严格编号EOS VQA，原SFT1/2/4shot及恢复四臂不重跑，原passed metrics哈希及恢复连续性在本Run复核。原整Run因selector初始化错误failed不改写。合成GT+错误角框，不构成性能指标；无GRPO GPU结论。并执行源视频排除回归测试。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-ddp4x2-capability-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'5e5c3a57e57e388cdb3a1d30df82fcd6dbeab204eef84d61f88df0283c86343a'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：eb33603a193b05305f4994ef7e2d912e39a0ae48
- 随机种子：11451
- 配置：configs/experiments/E-015/selector.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-ddp4x2-capability-20261021/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-ddp4x2-capability-20261021/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-ddp4x2-capability-20261021/metrics.json

## 结果
尚无结果。

### Claim 边界
仅八视频短程工程能力，非正式性能或GRPO能力。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
