# e015-multishot-data-preparation-r4-20261021 · 只修正PIL尺寸读取属性，保持所有数据、采样、排除和哈希审计定义，继续完成已授权E015数据准备。

- 父 Run：`e015-multishot-data-preparation-r3-20261021`
- 来源版本：2026-10-21T19:11:38
- 状态：failed
- Workspace：03

## 本次任务
只修正PIL尺寸读取属性，保持所有数据、采样、排除和哈希审计定义，继续完成已授权E015数据准备。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：CPU清单构造，复用已有FOCUS均匀采样器和GOT原视频分组；固定测试集Query/GT，保留共同有效子集和排除原因；对旧GRPO4000条生成独立四参考帧映射，不改原始数据。无模型调用。 首次val.json路径错误保留failed；本Run改读实际validation.json。 r2仅SHA预检失败未执行；r3保持相同脚本与输入。 r3在第一张图尺寸读取处失败，无科学产物；r4修正.size属性。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r4-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'5c40a5de370422295225572af2f6650d5b8615b7d10df51d3533c6a922e9a085'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：7843661fbe581da3917ff9468cdae370be9b24a0
- 随机种子：20260901
- 配置：tools/prepare_focus_datasets.py + tools/prepare_candidate_selection.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r4-20261021/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r4-20261021/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r4-20261021/metrics.json

## 结果
尚无结果。

### Claim 边界
仅输入完整性与来源审计，不代表训练能力或性能。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
