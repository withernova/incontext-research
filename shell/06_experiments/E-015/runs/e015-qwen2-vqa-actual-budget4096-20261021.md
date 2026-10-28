# e015-qwen2-vqa-actual-budget4096-20261021 · 修正Qwen2真实图像预算并补测输入grid；保留全部历史证据，继续独立E015正式pipeline。

- 父 Run：`e015-qwen2-vqa-ddp4x2-capability-20261021`
- 来源版本：2026-10-21T20:26:08
- 状态：failed
- Workspace：03

## 本次任务
修正Qwen2真实图像预算并补测输入grid；保留全部历史证据，继续独立E015正式pipeline。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：校正实际视觉预算：Qwen2Fast的legacy min/max_pixels覆盖size导致之前测试实际每图10764/4784 rawpatch，不能声称4096；原SFT/selector更新和恢复事实保留但预算解释纠正。共享helper同时作用SFT/GRPO/eval；真实处理器CPU回归重现旧bug，检查5图实际grid≤4096并验证Qwen3像素输出不变。随后复用已训练短程selector，仅重跑8例五图VQA，检查真实grid和严格编号EOS；不报告合成候选mIoU为性能。正式SFT首次更新将验证校正后预算。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-vqa-actual-budget4096-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'d288eb72b204afb934cd015b5ff8a801113cde53209e4e26365061e445a97e14'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：7c1b73e18f6f31f5d6d656f7480eb7f5f6829a93
- 随机种子：11451
- 配置：tools/evaluate_candidate_vqa.py --model-family qwen2_vl --devices-per-replica 2
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-vqa-actual-budget4096-20261021/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-vqa-actual-budget4096-20261021/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-vqa-actual-budget4096-20261021/metrics.json

## 结果
尚无结果。

### Claim 边界
仅八视频短程工程能力，非正式性能或GRPO能力。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
