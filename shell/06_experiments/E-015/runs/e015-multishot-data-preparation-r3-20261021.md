# e015-multishot-data-preparation-r3-20261021 · 前次仅预检因部署超时而未执行。部署完成后按完全相同的修正版输入进行一次数据准备。

- 父 Run：`e015-multishot-data-preparation-r2-20261021`
- 来源版本：2026-10-21T19:09:52
- 状态：failed
- Workspace：03

## 本次任务
前次仅预检因部署超时而未执行。部署完成后按完全相同的修正版输入进行一次数据准备。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：CPU清单构造，复用已有FOCUS均匀采样器和GOT原视频分组；固定测试集Query/GT，保留共同有效子集和排除原因；对旧GRPO4000条生成独立四参考帧映射，不改原始数据。无模型调用。 首次val.json路径错误保留failed；本Run改读实际validation.json。 r2仅SHA预检失败未执行；r3保持相同脚本与输入。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r3-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'4beada162ab053c69aa793cf2b2f2c095a3a0ad25ea49e9014433a149bae0c0f'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：7843661fbe581da3917ff9468cdae370be9b24a0
- 随机种子：20260901
- 配置：tools/prepare_focus_datasets.py + tools/prepare_candidate_selection.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r3-20261021/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r3-20261021/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r3-20261021/metrics.json

## 结果
尚无结果。

### Claim 边界
仅输入完整性与来源审计，不代表训练能力或性能。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
