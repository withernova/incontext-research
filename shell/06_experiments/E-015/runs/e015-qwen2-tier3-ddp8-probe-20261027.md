# e015-qwen2-tier3-ddp8-probe-20261027 · 用户明确要求试8卡单副本DDP能否运行，并授权直接停止当前4x2训练；父Run完成18步后终止、无checkpoint、日志保留。独立8步能力短测，从同SFT6

- 父 Run：`e015-qwen2-tier3-grpo-20261027`
- 来源版本：2026-10-27T14:33:54
- 状态：failed
- Workspace：03

## 本次任务
用户明确要求试8卡单副本DDP能否运行，并授权直接停止当前4x2训练；父Run完成18步后终止、无checkpoint、日志保留。独立8步能力短测，从同SFT636初始化，原GRPO4shot数据/三档mean覆盖.1奖励/G4/seed11451/4096patches/192completion/1e-5保持；devices_per_replica1/layer_splitNone/torchrun8。warmup_ratio=.5在8步短测中保持原4次warmup；fresh8卡更新有效batch为原两倍，8步处理64rank-pairs与原4x2的16步同量，不宣称优化轨迹等价。每步记录多框率等既有统计与LoRA八副本一致性/逐卡峰值，外层采集实际完成更新时间，4→8更新测postwarmup吞吐。无评测/正式400步继承，不修改共享代码，复用已部署0e02d856ae30837eb60b511e8303cb50a50d1c26。若OOM真实报告不压低shot/分辨率冒充通过。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户明确要求试8卡单副本DDP能否运行，并授权直接停止当前4x2训练；父Run完成18步后终止、无checkpoint、日志保留。独立8步能力短测，从同SFT636初始化，原GRPO4shot数据/三档mean覆盖.1奖励/G4/seed11451/4096patches/192completion/1e-5保持；devices_per_replica1/layer_splitNone/torchrun8。warmup_ratio=.5在8步短测中保持原4次warmup；fresh8卡更新有效batch为原两倍，8步处理64rank-pairs与原4x2的16步同量，不宣称优化轨迹等价。每步记录多框率等既有统计与LoRA八副本一致性/逐卡峰值，外层采集实际完成更新时间，4→8更新测postwarmup吞吐。无评测/正式400步继承，不修改共享代码，复用已部署0e02d856ae30837eb60b511e8303cb50a50d1c26。若OOM真实报告不压低shot/分辨率冒充通过。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-tier3-ddp8-probe-20261027/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'d7b911a2f67b5239b4f66889146aaadc21d4647045055d88bd1923d75f36bf97'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：0e02d856ae30837eb60b511e8303cb50a50d1c26
- 随机种子：11451
- 配置：configs/experiments/E-015/grpo.py overrides launch.nproc_per_node8, devices_per_replica1, layer_splitNone, max_steps8
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-tier3-ddp8-probe-20261027/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-tier3-ddp8-probe-20261027/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-tier3-ddp8-probe-20261027/metrics.json

## 结果
尚无结果。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
