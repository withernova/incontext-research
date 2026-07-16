# R-012-qwen3vl-large-object-token-identity-transfer-n27

- 状态：completed
- 性质：reference-token replacement / contamination pilot
- 远端目录：`/home/featurize/work/mechanism/explog/E-002/runs/R-012-qwen3vl-large-object-token-identity-transfer-n27/`
- 目的：把 reference object embeddings 写入 same-class negative query object slots，测试 reference-like evidence 是否诱导 FP。
- 数据：large/rich LaSOT n=27 balanced POIL。
- 干预：post-merge pooler tokens；full/center50/center25 replacement；按归一化网格近邻配对；query-self shuffle 为 control。
- 结果：baseline F1=0.915/FPR=0.185；full replacement=0.806/0.481；center50=0.915/0.185；center25=0.947/0.111；query shuffle=0.982/0.037。
- Box shift（new FP）：full n=11，面积比1.161、中心位移101.2/1000、IoU(base,new)=0.544；center50 n=5，1.059/7.1/0.922；center25 n=1，1.030/1.1/0.969。
- 关键 caveat：source/destination 数可严重不平衡并重复 stamping（例 sample 9: 20→154）。因此不能称为干净 identity transfer。
- 审核：`analysis/summary.json`、`analysis/r012_container_box_shift_on_fp.{json,md}`、`visualizations/token_transform_effects_with_support/`。
