# 新增0.1补偿：75步最新快照

最新固定快照8rank共同完成1..75，4800rollout/1200G4组、4728合法；beta0/.6/.1实际配置和奖励重算通过，排除pending0。合法多框467/4800=9.7292%，raw509含42非法。1..25/26..50/51..75多框332/133/2，率20.75%/8.3125%/.125%。近20步2/1280=.15625%，近50步135/3200=4.21875%；最近多框73。51..75仅2条均合法collage正样本、低IoU非近重复、adv均负。原正/负最后多框35/34。前期增加之后多框几乎消失，但不是严格零；累计比例不能代表当前输出。不改参数或训练、未测试/模型评测、不持续监控、无Claim升级。

最近非零多框更新：[{"update": 73, "valid_multi": 2, "raw_multi": 2}]

分析Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis`。单seed训练日志观察，不是最终性能或因果结论。详见analysis.json与integrity_audit.json；完整只读source_snapshot及SHA在独立Run。
