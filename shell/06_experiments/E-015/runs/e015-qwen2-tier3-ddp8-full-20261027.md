# e015-qwen2-tier3-ddp8-full-20261027 · 用户在8卡DDP短测完成4步并核验无OOM记录后，明确要求进行完整训练。新的独立Run从同一SFT636 adapter重新初始化GRPO，8进程×1GPU，4

- 父 Run：`e015-qwen2-tier3-grpo-20261027`
- 来源版本：2026-10-27T14:33:54
- 状态：failed
- Workspace：03

## 本次任务
用户在8卡DDP短测完成4步并核验无OOM记录后，明确要求进行完整训练。新的独立Run从同一SFT636 adapter重新初始化GRPO，8进程×1GPU，4shot/G4/三档奖励/拼接mean覆盖最高0.1均沿用已停止tier3父Run；devices_per_replica=1、layer_split=None，400更新、warmup_ratio0.01(4步)、lr1e-5/beta0/seed11451/4096patches/192token、每50步保存。8卡每步64rollouts，400步共3200rank-pairs/25600rollouts，为旧4副本400步总采样量两倍；已向用户说明，不声称等采样量或纯加速对照。旧18步和短测4步无checkpoint，不继承其权重；不重训SFT/VQA。逐组及每步记录原图/拼接分组多框率、框数分布、Oracle/Selected IoU与命中、覆盖未选中、奖励/优势、各卡峰值及LoRA一致性。完成后既有入口顺序执行三数据集固定1289查询的1/2/4shot proposal与clean VQA4172评测，推理维持BF16/4副本×2GPU，84项独立tier3_ddp8指标。保留LaSOT作者划分/GOT验证类别重合等原边界。复用已发布部署0e02d856ae30837eb60b511e8303cb50a50d1c26，不改共享源码；Run脚本沿原冻结调度快照，仅改训练启动/验收rank数与指标前缀，差异保存runner_delta.patch；算法和评测入口复用现有实现。失败保留现场，不自行降低shot、分辨率或更换奖励。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户在8卡DDP短测完成4步并核验无OOM记录后，明确要求进行完整训练。新的独立Run从同一SFT636 adapter重新初始化GRPO，8进程×1GPU，4shot/G4/三档奖励/拼接mean覆盖最高0.1均沿用已停止tier3父Run；devices_per_replica=1、layer_split=None，400更新、warmup_ratio0.01(4步)、lr1e-5/beta0/seed11451/4096patches/192token、每50步保存。8卡每步64rollouts，400步共3200rank-pairs/25600rollouts，为旧4副本400步总采样量两倍；已向用户说明，不声称等采样量或纯加速对照。旧18步和短测4步无checkpoint，不继承其权重；不重训SFT/VQA。逐组及每步记录原图/拼接分组多框率、框数分布、Oracle/Selected IoU与命中、覆盖未选中、奖励/优势、各卡峰值及LoRA一致性。完成后既有入口顺序执行三数据集固定1289查询的1/2/4shot proposal与clean VQA4172评测，推理维持BF16/4副本×2GPU，84项独立tier3_ddp8指标。保留LaSOT作者划分/GOT验证类别重合等原边界。复用已发布部署0e02d856ae30837eb60b511e8303cb50a50d1c26，不改共享源码；Run脚本沿原冻结调度快照，仅改训练启动/验收rank数与指标前缀，差异保存runner_delta.patch；算法和评测入口复用现有实现。失败保留现场，不自行降低shot、分辨率或更换奖励。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-tier3-ddp8-full-20261027/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'b7496dd8785c0f491e48d4a7a9b123fc3f195d4006e8584cfff35ce255cfe996'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：0e02d856ae30837eb60b511e8303cb50a50d1c26
- 随机种子：11451
- 配置：configs/experiments/E-015/grpo.py: launch.nproc_per_node=8, grpo.devices_per_replica=1, layer_split=None, max_steps=400; existing evaluate.py / candidate VQA CLI
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-tier3-ddp8-full-20261027/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-tier3-ddp8-full-20261027/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-tier3-ddp8-full-20261027/metrics.json

## 结果
尚无结果。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
