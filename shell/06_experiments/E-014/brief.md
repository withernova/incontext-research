# E-014 · Experiment Brief

## 用户提出的目标
从原置信度 SFT step659 初始化，进行纯 GRPO。候选数量由模型自行决定，不固定三框或为了配额制造更多 GT 实例；按 Query bbox 中心横坐标从左到右输出，保留 Reference 同一实例置信度定义。使用同类别两实例的 Reference 切换与 AB/BA 位置交换训练，检验空间顺序、候选覆盖及按 score 选框是否改善。具体实现与训练预算记录在独立 Run；本实验不是仅修改 prompt 的单变量消融。

## 用户约束
用户已要求准备并执行训练，确认 SFT659、纯 GRPO、变长候选；不加 score CE、旧反事实偏好、SDS/Evidence reward，不附加“与置信度无关”措辞。不修改 E-013 默认行为或原始图像/清单。原 4000 条输入的身份、GT、split、review 字段不变，只在 E-014 派生清单迁移到注册的只读 dataset alias。所有新数据、缓存和产物写入 E-014 独立新 Run 目录，不覆盖失败结果，不自动重跑。具体 Run 的完整参数、奖励定义、数据规模、代码 SHA、发布/部署与执行门必须核查；Agent 不代替人类批准或授权。

## 来源
- kind: standalone
- source_ref: E-013
- evidence_refs: 
- claim_refs: 
- workspace_id: 03
