# e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451 · 用户要求发布部署后立即启动本次已实现的0.2多框奖励独立训练。以已发布部署的69f786a3db89177cea11178714f560ce5760d36c为准

- 父 Run：`e014-multi-v2-cover-min-cap5-sft659-puregrpo-seed11451`
- 来源版本：2026-10-12T20:47:30
- 状态：failed
- Workspace：03

## 本次任务
用户要求发布部署后立即启动本次已实现的0.2多框奖励独立训练。以已发布部署的69f786a3db89177cea11178714f560ce5760d36c为准，使用configs/experiments/E-014/training/e014_multi_v2_cover_min_cap5_multi_bonus_grpo.py；从原SFT659 fresh初始化policy及固定anchor，不恢复或启动父Run命令，不覆盖旧结果。除settings.trainer.reward.multi_bonus_weight=0.2和独立输出名外，继承父min覆盖/cap5、multi_v2、纯GRPO、seed11451、8GPU、数据及采样优化设置。奖励仅对实际collage正样本且有双GT、整条输出合法EOS终止、2..5框且至少一对IoU<=0.9时整条加一次0.2；原惩罚不变。保留task_total与实际multi_bonus日志。当前已公布配置预算3epoch/1500更新，每50存checkpoint和组统计，前100比较使用1..50及51..100窗口，不声称100自动停训。本请求授权此新奖励配置受管启动，不继承父结果或Solid标签。实际运行命令应为bash tools/run.sh configs/experiments/E-014/training/e014_multi_v2_cover_min_cap5_multi_bonus_grpo.py。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 命令：bash tools/run.sh configs/experiments/E-014/training/e014_multi_v2_cover_min_cap5_multi_bonus_grpo.py
- 代码版本：69f786a3db89177cea11178714f560ce5760d36c
- 随机种子：11451
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451/logs/run.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451/metrics.json

## 结果
尚无结果。

### Claim 边界
主诊断高且multi率下降支持Exploration瓶颈假设，但不能单独确定主要原因或排除Reward Design。该Run不自动validated Claim，不输出因果结论；工程complete不等于收益。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
