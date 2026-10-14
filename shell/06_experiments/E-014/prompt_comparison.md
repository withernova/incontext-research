# E-014：变长候选 prompt 与当前常用 prompt 的完整对照

## 1. 当前版本与范围

用户随后确认：从原置信度 SFT step659 开始，先做纯 GRPO；不固定三框，不为凑配额堆砌实例，让模型自行发现潜在候选。因此，本实验当前文本为 `prompt_e014_variable.txt`。先前的 `prompt_e014.txt` 是已被此版本替代的固定三框草案，仅保留历史，不作为启动文本。

本次“当前常用 prompt”特指 E-013 rank-cf 及最近分析使用的三候选实例协议 `focus_multi3_instances_v1`，不是单框 SFT prompt，也不是旧拼图空间排序 prompt。

常用文本的源码基线为 commit `d7b6b12782e465954f021420876c71796b785122`。E-014 实现提交为 `560d94028d031127dfa7faf816be87518244c032`，代码审阅 `eb7c47b4db2202fb` 通过。工程审阅不批准科研设计或执行。目前没有运行模型、测试或数据生成，没有启动训练。

## 2. 改动原则

保留跨帧 FOCUS 任务、Reference 同一实例的置信度定义、bbox-score 标签、score 范围和两位小数。只修改空间顺序与用户要求的候选数量约束：

1. `Output exactly 3 candidate bounding boxes ...` 改成 `Output candidate bounding boxes ...`。
2. 插入 `List candidates in left-to-right order by box center in the query.`。
3. 输出模板从三行改为一行，作为每个候选的模板，不暗示恰好三个。
4. Query 结尾指令删除 `exactly 3`，不另写候选数量配额。

不添加 `regardless of confidence`。原 prompt 已明确要求 `each score should indicate confidence that the candidate is the same instance as the reference target.`，该句逐字保留。

## 3. 当前常用 prompt 全文

与 `prompt_current.txt` 一致：

```text
Locate the same object across the sequence of frames shown below. Your goal is to identify the target object consistently using the visual context provided.

For the first T-1 frames, the bounding box of the object is already provided. Use this information and the visual context to predict where the same object appears in the final frame.

Output exactly 3 candidate bounding boxes for the last frame, each followed by a confidence score indicating how confident you are that the box correctly localizes the same target object. Consider different instances in the query that resemble the reference target; each score should indicate confidence that the candidate is the same instance as the reference target. The score must be a single number between 0.0 and 1.0, written with two decimal places.

Use the following format, one candidate per line:
<answer>[x_min,y_min,x_max,y_max]</answer><score>confidence</score>
<answer>[x_min,y_min,x_max,y_max]</answer><score>confidence</score>
<answer>[x_min,y_min,x_max,y_max]</answer><score>confidence</score>
```

## 4. E-014 当前变长 prompt 全文

与 `prompt_e014_variable.txt` 一致：

```text
Locate the same object across the sequence of frames shown below. Your goal is to identify the target object consistently using the visual context provided.

For the first T-1 frames, the bounding box of the object is already provided. Use this information and the visual context to predict where the same object appears in the final frame.

Output candidate bounding boxes for the last frame, each followed by a confidence score indicating how confident you are that the box correctly localizes the same target object. Consider different instances in the query that resemble the reference target; each score should indicate confidence that the candidate is the same instance as the reference target. List candidates in left-to-right order by box center in the query. The score must be a single number between 0.0 and 1.0, written with two decimal places.

Use the following format, one candidate per line:
<answer>[x_min,y_min,x_max,y_max]</answer><score>confidence</score>
```

## 5. 完整差异清单

| 项目 | 当前常用 prompt / 协议 | E-014 当前版本 | 是否改变 |
|---|---|---|---|
| FOCUS 跨帧同一目标任务 | 利用前 T-1 帧标注定位最后一帧同一目标 | 原文保留 | 否 |
| Reference 视觉信息与 bbox 标注 | 原消息布局 | 原消息布局 | 否 |
| 候选枚举 | 考虑外观类似 Reference 的不同实例 | 原文保留，不用 GT 提供候选清单 | 否 |
| 候选数量 | 恰好 3 个 | 由模型决定，不设框数量上限 | **是** |
| 输出顺序 | 未规定空间顺序；也未明文要求按 score 降序 | 按 bbox 中心横坐标从左到右 | **是** |
| 顺序与置信度的额外关系说明 | 无 | 无，不添加附加措辞 | 否 |
| score 定义 | 对该框正确定位 Reference 同一实例的置信度 | 原文保留 | 否 |
| score 范围与精度 | 0.0–1.0，两位小数 | 原文保留 | 否 |
| 每个候选格式 | `<answer>[x_min,y_min,x_max,y_max]</answer><score>confidence</score>` | 原文保留 | 否 |
| 格式示例数量 | 三行 | 单个候选一行模板 | **是** |
| Query 结尾指令 | `Predict exactly 3 BBOX candidates ...` | `Predict BBOX candidates ...` | **是** |
| 最终选择 | 最大 score；并列时取最早输出 | 保留 | 否 |
| 生成预算 | 旧训练 192 new tokens | 同样 192 new tokens | 否 |
| 格式有效条件 | 三个完整合法 bbox-score pair，正常终止 | 至少一个完整合法 pair，正常终止，无额外文本 | **是** |
| 零框/空列表协议 | 无 | 不新增；负例可以输出低分候选 | 否 |
| 图片次序、坐标预处理、chat template | 原实现 | 原实现 | 否 |

不规定三个输出槽位分别对应哪张 GT。两个已知实例只是对称训练图上的标注，用于事后奖励；其他场景对象没有被补造标注。模型是否发现、列出候选，仍由自然生成决定。

不设框数量上限不等于无限生成：192-token 预算仍会限制实际输出。未终止或任何候选格式错误时整条无效，不截取前面的合法候选。空间中心并列允许非递减，不以 score 作空间并列排序依据；最终 score 并列选框仍按较早位置。

## 6. 完整消息布局

1-shot content 顺序仍为：完整任务文本、Reference 图像、`Frame 1 BBOX: <既有 Reference bbox>`、Query 图像、Query 结尾指令。Reference bbox 是输入，Query GT 不加入消息。没有候选 GT、类别名、正反样本标签或新增示范回答。

旧结尾：

```text
Frame 2 is the final frame. Predict exactly 3 BBOX candidates and a confidence score for each.
```

新结尾：

```text
Frame 2 is the final frame. Predict BBOX candidates and a confidence score for each.
```

## 7. 实现与训练设计入口

- 唯一 prompt / messages / parser：`iploc_szy/prompting/e014.py`。
- 变长 reward：`iploc_szy/rl/e014.py`。
- 对称数据及校验：`tools/data/build_e014_symmetric_candidates.py`、`iploc_szy/rl/e014_data.py`。
- 训练配置：`configs/experiments/E-014/training/e014_variable_symmetric_grpo.py`。
- 入口：`tools/run/train/e014_variable_symmetric_grpo.sh`，复用共享 GRPO core。
- 评测 Dataset / Evaluator：`iploc_szy/evaluation/e014.py`，同一 prompt，未运行评测。
- 完整参数、奖励公式、预算、科学限制及启动门禁：代码仓库 `docs/e014_variable_symmetric_grpo.md`。

训练设计为 SFT659、纯 GRPO、1000 个真实同类别不同实例源对，每对两个布局×两个 Reference；保留 4000 条原 train 输入，加 4000 条对称输入。8 卡、group_size=4、8e-5、3 epoch，共 1500 optimizer steps。新增空间权重 0.1 是初始设计，不是调优结果。

变长输出要求适配归约。E-014 校准惩罚取最坏候选 Brier，重复惩罚取最强重复对，以免被新增低分候选稀释。覆盖采用所有候选到已知两实例的一对一匹配，不固定输出槽位。这些是与旧 GRPO 不同的训练定义，须在具体 Run 的审核快照中明确，不能称为仅修改 prompt 的单变量消融。

## 8. 快照与验证边界

UTF-8 文件均无末尾换行：

- `prompt_current.txt` SHA-256：`aedf418504b67d6a29216e08a052d996f9e4ae2a0eb5e1e2c392cbf3cca6730a`。
- 当前 `prompt_e014_variable.txt` SHA-256：`15181cde16e9cc85e6c01877dcae6a740eedf33d7010fa4af0d2fce790428d04`。
- 历史固定三框草案 `prompt_e014.txt` SHA-256：`01f783504fd793eb8746b274b1a43728d6101ff0b886fc0bdf7fc39927226b86`。

只完成 Python 3.9 AST、shell 语法、diff 静态检查和工程审阅。提供了测试文件但未执行；未做 import、模型启动、CPU/GPU 测试或数据生成。准备好的配置不等于已运行训练，工程审阅不等于研究假设成立。
