# R-013-qwen3vl-wrong-class-object-token-replacement-n27

- 状态：completed
- 性质：wrong-class donor content probe（positive-only）
- 远端目录：`/home/featurize/work/mechanism/explog/E-002/runs/R-013-qwen3vl-wrong-class-object-token-replacement-n27/`
- 目的：用另一类别 large-object donor 替换 positive query object tokens，测试 identity-destroying content 是否令 Yes→No。
- 数据：large/rich n=27 positives；donor=下一不同 element sample 的 positive image，单独编码、不加入 prompt。
- 结果：baseline TP=27/F1=1；wrong-full TP=25/FN=2/F1=0.962；center50 TP=26/FN=1/F1=0.981；center25 TP=27；positive shuffle TP=27。
- 支持：wrong-class full replacement仅造成有限 FN，未显示强 identity-detail constraint。
- 局限：positive-only；pooler-only、deepstack 未改；bbox proxy；donor 与目标的低层统计未匹配。
- 审核：`config/run.md`、`logs/run.log`、`analysis/summary.json`、`hook_records_head`、`donor_manifest`。
