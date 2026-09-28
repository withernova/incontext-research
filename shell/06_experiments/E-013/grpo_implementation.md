# E-013：同类别不同实例置信度 GRPO 实现

本次范围：按用户要求先提交已有代码，再实现 GRPO 并尝试构造数据。没有启动正式训练，没有修改 Survey Tool、Claim、Run 或授权状态。可用 Solid Run ID：无。

## 已有更改提交

实际代码仓库为 NKU-LWC 的 `/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy`。
提交 `01b83d8` 保存原有两项配置修改：E-013 SFT 的 epoch/seed，以及 branch 的 E-013 baseline 入口。新 GRPO 代码与这次提交分开。

## 新增代码

- `iploc_szy/rl/rewards.py`：严格 bbox/score 解析；正例 IoU 与 Brier 奖励；负例仅惩罚置信度，目标不存在时禁止使用干扰物框作为 GT；非法/截断输出单独处罚。
- `iploc_szy/rl/objective.py`：每输入 G 次采样的优势、clipped token GRPO、冻结参考 KL、prompt mask 与 EOS 对齐。
- `iploc_szy/rl/trainer.py`：单 GPU NF4 LoRA，policy 与初始化 SFT anchor 分开；每步同时处理正负 pair，两侧优势独立计算；关闭 dropout、重置 Qwen 位置缓存、核验 old-policy 重放、记录各输出与分项奖励。
- `iploc_szy/rl/data.py`：成对、核验、图像/身份/来源分组及双图 processor 校验。
- `tools/train/train_e013_grpo.py`、`configs/grpo/e013_confidence.json`：明确配置入口和不加载权重的 `--inspect`。路径待指定，参数是工程初值，默认 1 step。
- `tools/data/build_e013_pairs.py`：同 Query 的正/负 Reference 配对候选、核验模板、接触图、内容哈希及可训练清单。
- `docs/e013_grpo.md`、`tests/test_e013_grpo.py`、`tests/test_e013_grpo_tiny.py`：中文说明、奖励/数据/梯度测试及 CPU 微型 Qwen3-VL 双图集成检查。

代码借鉴已抓取的 Visual-RFT 固定版本 `2ffad63b25ddd79bfe25d3e046645401201c89d6` 的可验证奖励与分组采样结构，未复制其输出修补、类别提示或线性置信度奖励。原始源码及 SHA-256 在 `design_sources/`。

## 数据边界

只读取 E-013 SFT 记录明确指定的正例输入清单，未采用其他实验结果。源清单 10,534 条，SHA-256 为 `c607700075de7eba1b0dc8237a32eb1760d3864a4e320f01a41bce8aec94ba78`。

GOT-10k 类别来自 meta_info.ini；LaSOT 序列前缀仅用于类别候选；TAO 缺类别映射时跳过。GOT-10k 按原视频来源分组划分，并排除同来源 donor；其他数据按序列划分。不同视频仍不保证不同真实身份，所有负例必须核验同类、不同身份、目标确实缺失及视觉可判别性。

原正例曾用于 SFT，因此此次 validation/test 仅是 GRPO 阶段留出，不能宣称完全独立的泛化测试集。核验记录必须包含 reviewer/evidence，绑定候选内容 pair_id。未经核验输出空 trainable_pairs，训练拒绝使用。

## 检查及待办

最终 26 项测试通过，覆盖奖励、数据核验、来源分组、防泄漏、优势/梯度、CPU 随机初始化微型 Qwen3-VL 双图（生成/forward 对齐、policy 梯度更新、anchor 不变）。真实 processor 双图/坐标/视觉 token 检查通过，修正当前 Transformers 版本需要使用 size 参数的兼容问题；示例合计 504 个视觉 token。

真实 8B GPU forward/backward、NF4 内存与吞吐、校准效果及独立评测未运行。本实现不包含 DDP、自动恢复、多候选或同图 A/B 联合奖励。

## 实际数据构建结果

正式候选产物路径（远端）：`/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-013/same-class-confidence-candidates-v2`。

- 共 9,272 组候选：GOT-10k 8,601；LaSOT 671。
- 按来源分组划分：train 7,846，validation 687，test 739。
- 排除：11 条框异常，499 条缺类别，225 条同划分内无同类 donor，527 条无不同视频来源 donor。
- 24 张随机抽样接触图；核验模板、候选内容 ID、JSON 文件 SHA-256 已输出。
- **可训练记录 0**：未将“不同序列/视频”当作已确认不同身份与目标缺失。
- v1 仅按序列分组，接触图提示同来源风险，故保留为构建过程产物，不推荐使用；以 v2 为本次交付。

## 完成交付

- 新代码独立提交：`763e22116ffbd4e99cf5f26184b94e370d614dbd`，11 个新增文件；提交后工作树干净，未 push。
- 提交前 `git diff --cached --check` 通过。逐文件 SHA-256 存于代码仓库 `work_dirs/e013_delivery_sha256.json`。
- 候选摘要与 24 张核验图已复制到本地 `dataset_preview_v2/`。
- 未执行真实 8B/NF4 模型训练或 GPU smoke，未核验负例身份/目标缺失，未产生实验有效性结论。

## 协议修正（2026-09-22）

根据用户确认，训练协议固定为同类别不同实例的错配 Query，不构造同一 Query 内同时出现 A/B 的多目标样本。主训练数据要求正例与负例各 50%：正例是同实例 Reference→Query，负例是同类别不同实例 Reference→Query；负例不使用 Query 中物体框作为 GT，只要求置信度很低。正例奖励由 IoU 定位项和置信度项共同组成，负例仅使用低置信度项；正负样本共享同一组 GRPO 代码和冻结 SFT anchor。

GRPO 已接入现有 branch launcher，固定 4 GPU DDP。`--ckpt PATH` 会覆盖 `branch.source_profiles.e013_baseline.parent_checkpoint`，仍经过 named-run 父 checkpoint 校验。最新远端提交为 `38bde9a`。当前 trainable manifest 仍为空，正式训练会被 50/50 数据门禁拒绝，需先完成候选核验。

## 当前启动核验（2026-09-22，覆盖上文历史状态）

- 用户接受抽样可视化后按同类、跨来源规则扩大训练集；这不代表逐条人工确认身份。`E-013/overnight-train-2k/trainable_pairs.json` 已有 4,000 条记录，正负各 2,000，共 2,000 张不同 Query。
- 配置为 4 GPU、NF4 LoRA、group size 4、学习率 5e-5、2 epochs，每 epoch 500 次更新。每 50 步及 epoch 结束保存 adapter/optimizer；尚不支持自动恢复全部训练状态。
- 修复提交 `e2c1b92`：只投影 completion 所需 logits、非重入梯度检查点、关闭 dropout、固定无截断采样分布、无梯度重放使用未包装模型、梯度累积末次同步及中间保存。
- 26 项针对性测试通过，包含完整 logits 与裁剪 logits 等价性、梯度检查点下 policy 更新和 anchor 不变。
- 真实四卡短跑目录：`E-013/focus-confidence-sft/branches/20260921T172342561911Z--focus-confidence-grpo-ready-smoke/grpo`。已完成 2 步、64 条 rollout；四卡梯度范数一致且有限，504 个 adapter 参数张量改变，中间及最终保存成功。
- 正式训练已发出启动命令，目录：`E-013/focus-confidence-sft/branches/20260921T172801747698Z--focus-confidence-grpo-overnight-ready/grpo`。远端代码仓库控制台日志：`work_dirs/e013-92f2560670.txt`。以上路径均位于远端项目中，不能据此宣称正式训练完成或效果提升。
- 正式进程生成的配置快照已核实：epochs=2、learning_rate=5e-5、group_size=4、max_pixels=262144、max_new_tokens=96、save_every_steps=50，使用上述 4,000 条清单。短跑两次中间保存间隔约 66 秒，1,000 步粗估约 18 小时，仅作当前共享 GPU 下的耗时参考。
- 正式训练四个 rank 均已完成第 1 步（合计 32 条 rollout），梯度范数均为约 0.546573；交付时任务继续运行，尚未完成 2 epochs。
- 服务器四卡各有约 9 GB 其他任务显存占用；短跑通过只能证明当前启动、更新和保存链路可用，完整训练耗时与效果仍待运行观测。无 Solid 结果，本记录只报告工程核验，不更新 Claim 或治理状态。
