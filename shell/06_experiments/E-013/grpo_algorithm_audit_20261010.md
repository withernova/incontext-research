# E-013 GRPO 算法与实现审查（2026-10-10）

审查版本：`9d42d2be43464988cde879857a9d31864cf49851`。本次只读审查代码仓库，执行本地 CPU 合成检查；未修改训练源码、实验配置或治理状态，未连接服务器或启动真实训练。

重新读取 canonical E-013 与 Workspace 03：目标仍为探索多框输出及置信度选择是否有益，planned/draft，绑定本地 Git 仓库。canonical plan 的假设、成功/失败标准、变量对照、主指标尚未填写。本次可用 Solid Run ID：无；显式结果引用：无。因此下文是代码与合成输入审查，不能用于判定历史 Run 的实际配置或效果。

## 结论

核心损失与采样逻辑在本次检查范围内没有发现符号、token shift、anchor 更新或梯度缩放错误。但发现一个确定的实验配置问题：目前普通 multi3 与 multi3_rank 的有效训练设置和奖励设置相同；不能据此形成排序奖励的开关消融。另有置信度校准与排序目标冲突，以及若干必须明确记录的 GRPO 变体选择。

## 实现来源

仓库 `docs/e013_grpo.md:37–42` 明确说明：参考 Visual-RFT 的可验证奖励与分组采样，项目内独立实现，不依赖 TRL。

- [Visual-RFT 入口，固定 commit 2ffad63b25ddd79bfe25d3e046645401201c89d6](https://github.com/Liuziyu77/Visual-RFT/blob/2ffad63b25ddd79bfe25d3e046645401201c89d6/src/virft/src/open_r1/grpo.py)
- [同版本实际 Qwen2VL GRPO trainer](https://github.com/Liuziyu77/Visual-RFT/blob/2ffad63b25ddd79bfe25d3e046645401201c89d6/src/virft/src/open_r1/trainer/grpo_trainer.py)
- [TRL v0.15.2 trainer，对照版本](https://github.com/huggingface/trl/blob/v0.15.2/trl/trainer/grpo_trainer.py)
- [TRL 官方 GRPO 说明，读取日期 2026-10-10](https://huggingface.co/docs/trl/grpo_trainer)

上述源码和文档已实际获取并记录 SHA-256，见附带检查 JSON。Visual-RFT 页面经浏览工具获取失败后，使用其固定 commit 的 raw 文件成功读取。没有把“参考过仓库”视为实现正确的证明；没有声称直接继承官方 trainer。本次没有摄取原始论文 PDF，不将论文内容当作独立核验依据。

## 发现与影响

### 1. 高优先级：multi3 与 multi3_rank 实际没有形成排序开关对照

- `configs/experiments/E-013/training/e013_multi3_branch.py:10–12` 没有显式配置排序权重，其说明只列定位、Brier、重复惩罚。
- `iploc_szy/rl/multi_candidate.py:24` 的 `rank_weight` 默认值是 `0.5`。
- `e013_multi3_rank_branch.py:9–12` 显式配置的是相同的默认值：`0.5 / 0.1 / 0.1`。
- 通过实际 `load_experiment_config` 展开、再补齐 reward 函数默认值，验证二者的 trainer 设置、有效 reward、进程数、输入清单定义、初始 checkpoint 定义全部相同。运行名称、说明和输出目录可以不同，但不构成训练干预。

建议修复：在无排序对照中显式设 `rank_weight=0.0`，在排序处理组显式设 `0.5`；所有奖励项均物化到配置快照，添加“有效配置差异”检查。该建议改变实验语义，本次讨论审查没有直接修改配置。只对当前代码成立，不能反推旧 Run 的执行状态。

### 2. 中优先级：排序奖励可能以降低校准质量为代价提高总奖励

`multi_candidate.py:58–72` 的 Brier 目标是 `IoU≥0.5` 的二元正确性；排序项则按连续 IoU 差要求分数至少拉开 margin。两个框均正确但 IoU 不同时，两项目标可能冲突。

合成反例，固定候选 IoU 为 `[1.0, 0.6, 0.0]`，选中的框保持不变，使用当前默认奖励：

| 三个分数 | Brier（越低越好） | 总奖励（越高越好） |
|---|---:|---:|
| `[1.00, 1.00, 0.00]` | 0 | 0.9833333333 |
| `[1.00, 0.90, 0.00]` | 0.0033333333 | 0.9966666667 |

该反例不代表模型已失去校准，而是证明“总奖励提高 ⇒ 概率更准确”不成立。需先约定 score 是框正确概率、预期 IoU 还是排序分数。若保留混合目标，应分别报告选中框定位表现、候选覆盖、Brier/校准、负例高分误认，并做 reward 项消融。

### 3. 需要说明的算法选择：一次采样只做一次更新

`trainer.py:116–124` 每个 pair 采样、反向累计后只执行一次 optimizer.step；`trainer.py:523–550` 要求更新前 current 与 old 重放一致。因此正常情形下 ratio≈1，clip 分支通常不激活。数据 epochs 增加意味着重新采样，不是对同一组 rollout 做多个 policy iteration。

这是允许的单次更新 GRPO 形式；Visual-RFT 该版本和 TRL v0.15.2 也使用单次更新形式，TRL 官方文档也说明 μ=1 的退化关系。它不是公式错误，但不能把 `clip=0.2` 当作实际参数更新幅度的硬保证。应记录 KL、ratio/clip fraction、梯度范数和更新幅度，另行验证学习率。

### 4. 与所参考版本不完全一致，必须固定规格

- `objective.py:6–11` 使用总体标准差（`unbiased=False`）和 epsilon `1e-6`；所查 Visual-RFT 与 TRL v0.15.2 使用默认样本标准差与 `1e-4`。G=4、奖励 `[0,1,2,3]` 时，本实现优势幅度约为对照的 `1.154789` 倍。属于明确的变体差异，不能宣称数值复现上游；小方差下 epsilon 差异更值得注意。
- 当前按每个 completion 的 token 均值，再平均 group/pair；这符合早期 GRPO 的序列平均方式。不同 completion 长度的每-token 权重不同；现代 TRL 另有 DAPO/Dr.GRPO 等选项。对三框与单框比较必须固定并说明归一化。
- 开启 counterfactual 时，实际目标为 GRPO 加 score-token preference auxiliary loss，并非单一 GRPO。应单独报告其权重与触发比例。

### 5. 可复现性和观测仍有缺口

- `docs/e013_grpo.md:31` 仍描述早期 eval-only、无 DDP、多候选等状态；当前源码已经 train-mode 重放、关闭 Dropout，并支持这些功能。应更新文档，避免据旧文档描述论文方法。
- 当前日志含 reward、advantage、长度、loss、梯度范数、counterfactual 状态，但不独立记录 KL、ratio、clip fraction 和熵。监控总 loss 不能解释策略漂移。
- GRPO 不支持精确 resume；最终 checkpoint 仅保存 rank 0 CPU torch RNG，缺少各 rank CUDA/Python RNG 与数据游标。不要将重新加载 adapter 称为严格续训。
- 当前依赖声明没有固定 torch/transformers/peft 版本；真实 GPU、NF4、attention backend 和 CUDA 组合需要单独记录与验证。

## 本次实际执行的检查

环境：既有临时 CPU 环境 `/tmp/iploc-cpu-check`，torch 2.8.0+cpu、transformers 4.57.3、peft 0.17.1；只使用随机初始化微型 Qwen3-VL、合成图片 tensor 和临时目录，不读取模型权重、训练数据或历史产物。

1. 现有聚焦测试：53 passed，退出码 0。覆盖 objective、正负样本/奖励、微型双图 Qwen、counterfactual、multi-reward 和 orchestration。一个随机模型保存时缺少模型配置来源的 PEFT 警告。
2. 独立标量 oracle：正、负、零 advantage 及上下 clip 区域的 loss/解析梯度核对通过。
3. 多 token cached generate 与 uncached teacher-forced replay：3 个固定 seed、每个 8 token，最大 logprob 绝对差 `4.76837158203125e-07`。
4. 实际两进程 Gloo DDP（非 mock），与同一全局合成 batch 的串行梯度/参数更新对照：2 个 optimizer step 通过，梯度最大差 `3.725290298461914e-09`。包含两条件梯度累积、policy/anchor 切换、counterfactual 的两个带梯度 forward、非重入 checkpointing；anchor 参数保持不变。首次受限环境不允许本地通信，允许回环通信后检查通过。
5. 实际配置解析器的有效参数等价检查，以及排序/校准反例均可重复。

复现脚本及机器结果位于同目录 `grpo_algorithm_audit_20261010/`。脚本引用本次审查的本地仓库与临时 Python 环境；执行前核对 commit。CPU 两进程结果不替代 NCCL、CUDA、真实量化权重与真实 processor 验证。

## 建议的严谨性验收顺序

1. 先修复/显式冻结 reward 配置；保证每个消融仅改变声明的变量，快照包括函数默认值、数据 hash、commit、完整依赖版本和初始化来源。
2. 冻结算法规格：优势标准差/epsilon、token reduction、KL、采样分布、更新次数、optimizer 参数、counterfactual 辅助项；将 loss 与梯度 oracle、有效配置差异检查纳入持续检查。
3. 对已发布的固定 SHA 进行真实 CUDA/NF4 小规模验证：完整 rollout logprob 一致、anchor 不变、单卡/多卡等效、梯度有限、更新可观测，记录实际 deployed SHA。按既有授权流程执行。
4. 在事先约定的独立评测与随机种子上分别检查定位、选择、校准、拒识和格式有效率。根据 canonical 尚缺的目标、主指标和对照补齐设计；不用训练 reward 或通过测试数量代替实验有效性。

优先级最高的是修复排序消融的有效配置，并明确 score 的含义；无需仅为了与外部框架一致就整体替换现有 trainer。
