# E-011 事件日志

> 本文件只保留单行摘要；完整 details 保存在工具内部的 experiment-events.jsonl 中。
> 需要展开某条事件时运行：`python3 /home/zhengyuesong/Tools/survey-tool/surveyctl.py --project <proj> experiment event-detail <E-ID> <EVENT-ID>`。

- 2026-09-08T15:34:18+08:00 · discovery · 远程勘察未启动：SSH 连接在执行前因远端端口转发失败而退出，未读取或修改远程仓库、数据或环境。 · run=- · detail=evt-20d13f82ad7f
- 2026-09-08T15:37:00+08:00 · discovery · 已核验 IPLoc 基线入口与可干预位置：评估脚本使用 Qwen2-VL 生成边界框；当前实现未暴露 attention hook，query head 的概率改写需新增显式 hook。 · run=- · detail=evt-c33ea8febd30
- 2026-09-08T15:38:10+08:00 · handoff · Agent 已提交勘察结果与待确认表单 · run=- · detail=evt-da0a88867b5c
- 2026-09-08T15:51:57 · run_organization · 1: microtask · run=1 · detail=evt-2f517492595f
- 2026-09-08T15:53:56+08:00 · run_rekey · Run registry 已从 1 迁移为 canonical ID E011-R-001-query-attention-gt-alignment-smoke · run=E011-R-001-query-attention-gt-alignment-smoke · detail=evt-7baee743026e
- 2026-09-08T15:54:27+08:00 · run_update · 已将占位 Run 重新登记为 query attention→GT 对齐机制 smoke 草稿；所有未验证的 head、生成行、GT token-grid 规则与样本规模均明确保留为待审核项。 · run=E011-R-001-query-attention-gt-alignment-smoke · detail=evt-1583ccb66d44
