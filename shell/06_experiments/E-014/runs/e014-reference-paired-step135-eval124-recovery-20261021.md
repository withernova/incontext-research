# e014-reference-paired-step135-eval124-recovery-20261021 · 补完用户已授权的paired组124条/62pair最终评测。原135步训练完成且passed，但一次性收尾脚本误将fresh空字符串判错导致未评测。只复用原最

- 父 Run：`e014-reference-paired-fresh3epoch-validation124-20261021`
- 来源版本：2026-10-21T13:37:00
- 状态：failed
- Workspace：03

## 本次任务
补完用户已授权的paired组124条/62pair最终评测。原135步训练完成且passed，但一次性收尾脚本误将fresh空字符串判错导致未评测。只复用原最终checkpoint，不重训、不改科学参数或旧失败记录；新独立评测Run。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：补完用户已授权的paired组124条/62pair最终评测。原135步训练完成且passed，但一次性收尾脚本误将fresh空字符串判错导致未评测。只复用原最终checkpoint，不重训、不改科学参数或旧失败记录；新独立评测Run。 原始训练adapterSHA=3783e74afefff97fc67728d42213e3f960c1e474cda97e3961d3c597cc8b5c4f；验证manifest/predictions SHA沿原命令，seed20260901/BF16SDPA/greedy16/EOS/vision4096/8GPU/exact_instance双全图/原候选保持。只有一次性输入验收脚本兼容实际空字符串，并分别读取旧训练与新评测目录；仓库源码和部署SHA未变。A-only答案位置分布混杂及23视频相关性限制保留。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-paired-step135-eval124-recovery-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'de719ad29dd7b2a0318d476e31c2d5b277dbbfc35c7f8f9119d88ece6f32c2e3'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：7caae090351c9c71ce65fd8c98a0bbbbb1825bc6
- 随机种子：20260901
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-paired-step135-eval124-recovery-20261021/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-paired-step135-eval124-recovery-20261021/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-paired-step135-eval124-recovery-20261021/metrics.json

## 结果
尚无结果。

### Claim 边界
仅生成，绝不补GT/混组/选择SFT或测试集生成，不自动恢复任何旧训练。指标仅描述训练候选而非泛化。legacy evaluator不记录逐例EOS标记；EOS停止默认生效但不是显式终止审计，后续入库需声明限制。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
