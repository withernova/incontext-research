# E003-R-004-joint-f1-iou-local-lasot-n140

- 状态：aborted_early / superseded
- 性质：主实验的提前中止尝试。
- 远端目录：`/home/featurize/work/mechanism/explog/E-003/runs/E003-R-004-joint-f1-iou-local-lasot-n140/`
- 数据/模型：计划同 R-004b；max_new_tokens=80。
- 中止原因：约9/140时观察到部分输出在 `Do all these boxes...` 截断，未生成最终 Yes/No；继续会污染 identification 指标。
- 结果：无完整 outputs/analysis，不得引用任何科学指标。
- 后继：由 `E003-R-004b-joint-f1-iou-local-lasot-n140-t128` 取代。
- 审核：`config/run.md`、`logs/run.log` 中 `[ABORTED_EARLY]`。
