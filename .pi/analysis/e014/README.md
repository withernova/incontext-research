# E-014 本地分析辅助文件

已完成的日志分析、离线扫描及快照报告的本地辅助文件统一归入本目录。2026-10-15 按用户指定服务器路径，另外将13个已结束分析 Run 目录移至 `/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/`，并通过官方接口更新当前 Run 产物、日志与指标路径。训练、checkpoint 和评测目录保持原位；Run ID、执行命令及原文件内容保留。

服务器迁移映射与完整性校验见 [服务器归档记录](server_directory_migration_20261015.json)，登记路径更新见 [Run 引用更新记录](server_canonical_reference_updates_20261015.json)。服务器索引在 `E-014/analysis/README.md`。

| 子目录 | 内容 |
|---|---|
| [e014-current-multibox](e014-current-multibox/) | 最初新奖励多框与定位分析 |
| [e014-explore06-multibox](e014-explore06-multibox/) | 探索0.6快照 |
| [e014-latest-training](e014-latest-training/) | 最初新奖励训练快照 |
| [e014-multibox-collapse](e014-multibox-collapse/) | 最初新奖励收缩诊断 |
| [e014-beta0-multibox](e014-beta0-multibox/) | KL为0的早期比较及失败记录 |
| [e014-bonus01-multibox](e014-bonus01-multibox/) | 额外0.1的53步分析 |
| [e014-bonus01-latest](e014-bonus01-latest/) | 额外0.1的75步分析 |
| [e014-bonus01-diagnosis](e014-bonus01-diagnosis/) | 额外0.1奖励与组内优势诊断 |
| [e014-multibox-bonus-sweep](e014-multibox-bonus-sweep/) | 0.1/0.2/0.3/0.5离线扫描 |
| [e014-bonus05-current](e014-bonus05-current/) | 额外0.5本次18步快照 |
| [e014-bonus05-latest](e014-bonus05-latest/) | 额外0.5最新377步快照 |
| [e014-bonus05-step350-eval](e014-bonus05-step350-eval/) | step350首次目录preflight失败记录 |
| [e014-bonus05-step350-eval-r2](e014-bonus05-step350-eval-r2/) | step350修正版评测参数与启动审计 |

本地移动前后路径与逐文件SHA见 [本地归档记录](directory_migration_20261015.json)。历史脚本、报告和执行命令原文保留，其中分析 Run 的旧绝对路径对应服务器迁移映射，不可直接当作重跑入口。
