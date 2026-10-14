# GRPO 跨层源码审查

状态：本分支源码核对已记录；不是 GPU/PEFT 运行通过，不是科研收益结论。基线 `1622e5f64a70239d02145f017cfd991cf8318e47`。路径相对 `code-repositories/03/iploc-szy`。

## 已穿透的链路

`config/branch → rl.branch_config 或 run_symmetric_grpo → preflight/data/symmetric_data → policy → sampling → task/rewards → core → trainer → checkpoint/observer`。

当前 RL 的 20 个 Python 文件均已全文读取（包含四个声明/兼容文件）；不是只根据导入名称判定。数据准备协调器和冻结 E-014 Shell 在前轮已读。测试定义仍待集中核对，未运行。

## 配方与预算

- E-013 confidence：共同父配置声明 G=4、seed=11451、lr=5e-5、epochs=2、96 新 token、NF4、max_pixels=262144、beta=.04/clip=.2。三框配方覆盖 lr=8e-5、epochs=3、192 新 token。
- `multi3` 与 `multi3_rank` 的排序参数实际上同为 .5/.1/.1。见 A015；旧名称不构成 rank 消融。
- rank-CF 子配方同时改了 nproc=2（父为4）和 CF weight/beta=.1。即使 epoch 覆盖相同，更新次数/每次全局 batch 不同。不能把历史差异只归因 CF。
- E-014 三配置共享 `symmetric_candidate_grpo`；multi_v2 只改 prompt_variant。min/cap5 再改 reward 和 observer，不是单一系数干预。
- E-013 branch loader 仅支持 new、2/4 ranks、指定 parent checkpoint；不支持任意恢复。E-014 当前协调器恢复 CLI 仍仅100，不从 source 中的通用 restore() 函数推断已经支持150/200/800。

## 模型、seed 与 anchor

`_initialize_policy` 在 load_policy 前设置 random/Torch/CUDA 公共 seed。模型装载后以 seed+LOCAL_RANK 设置采样 RNG。这与 A007 的普通 SFT 初始化顺序不同，不能把 A007 泛化到这里。

policy 和 anchor 从同一 adapter_path 装入；基座共享，anchor 不是禁用 adapter 的裸 base。加载器显式只允许 `.policy.` 的 LoRA 参数可训练；optimizer 在该集合上构造。重放 anchor 使用 no_grad，随后切回 policy。dropout 全部设为0。非重入 gradient checkpointing、NCCL/DDP 与 rank 布局仍依赖已绑定环境及 PEFT/Transformers 实际版本，未验证其运行行为。

## prompt、GT 与数据

`prepare_prompt` 只把 Reference 图和其 bbox、Query 图放入生成条件。target_box/distractor_box/coverage_boxes 留在 reward 侧；score 选框不读 GT。CF 才有明确版本化的 GT 派生 score 修正，E-014 冻结 CF weight=0。

原始单位为正/负两个 prompt；collage 单位为两个不同 Reference 的正 prompt。每个 prompt 独立标准化，不跨条件或 rank 混 reward。data 校验相同 identity/query_source_group 不得配为两个实例；symmetric_data 核对同一 source 集合的 AB/BA 反转及相关标注/图像哈希。不能仅凭同类别断言重复实例，也不能由标注门禁证明原图真实身份无误。

E-014 coverage 是两个人工拼接源实例的额外覆盖目标，不是一个 Reference 的双 GT。原始单目标行没有 coverage_boxes，不制造第二 GT。

## 采样与 log-probability

- fresh GenerationConfig：T=1、top_p=1、top_k=0、单序列抽样；不继承 checkpoint warper。EOS 从模型/processor 明确取得。
- EOS 后裁断，EOS 本身留在 generated_ids/loss；文本排除最后 EOS，其他特殊 token 保留供 strict parser 拒绝。截断未 EOS 单独标 invalid。
- replay 先清 rope_deltas；不使用 cache。仅输出 completion predictors 的 logits，但完整 ids/image condition 保留。
- logits 的 t-1 预测 token t；prompt 不进目标。单条无 padding；批量 core 入口用 bool completion_mask 排除 padding，并在 exp 前抹除 padding 的无效值。
- old_log_probs detach；optimizer 更新前检查 current/old allclose(atol=.02,rtol=.002)。这是误差门禁，不是精确概率等式或完整环境一致性的证明。

## loss 与更新

同 prompt 组的优势为 `(R-mean(R))/(population_std(R)+1e-6)`。默认 float32；G至少2且有限。全同 reward 得到零优势。

ratio=`exp(current-old.detach())`；KL 样本估计为 `exp(anchor.detach()-current)-(anchor.detach()-current)-1`。surrogate 为 ratio×A 与 clip 到[.8,1.2]的较小项。每条 completion 先 token mean，再 G 等权、pair 条件等权、DDP rank 等权。不是 score CE、prompt CE 或 token 级 advantage。

每个 pair 只有一次 AdamW step，不做多轮 PPO。所有条件采样/replay/backward 后才裁剪并更新。DDP no_sync 包含前向和反向，只有最后一个条件最后一个 completion 同步。AdamW 只显式传 lr，其 betas/eps/weight_decay 使用库默认；零 advantage 不保证零更新，因为 KL/optimizer state/weight decay 仍可能有作用。

CF positive/negative loss 只取三个 numeric score span 的 logp sum，anchor detach。被换的只有两个 score 字符串，全部 score 的条件概率仍受前文改变影响。这不是独立的逐 score 分类器，也不是 GT bbox 改写。

## reward 与 parser

- single：正样本 selected IoU−Brier，负样本−score²；target_present 与 GT 条件明确校验。
- E-013：strict 恰好3个完整 bbox-score，GT只做IoU/Brier/rank/已标注distractor/coverage。Brier和duplication均为均值；coverage将前两个固定槽与左右实例匹配。
- E-014：至少1个完整 bbox-score，不硬截候选数；score最大、最早tie选框。最大 Brier、最大重复 pair、rank margin、中心横坐标逆序率。coverage为不同预测到两实例的一对一最佳 balanced/min 分配，缺框为0。
- min/cap5 的数量项仅 `count_weight*max(0,raw_answer_openings-5)`。未完成/非法输出也读原始严格 `<answer>` openings；这不是对任意拼写的语义框数计数，不应扩大“不能逃逸”措辞的含义。合法数1–5无直接数量奖惩，192 token/EOS和其他项仍可影响数量。
- 没有源码证据证明上述 reward 保证多框、不同真实实例或防坍缩。max-Brier/min-coverage 的激励与模型实际探索、KL和EOS竞争必须看真实数据，不由代码公式推出收益。

## 保存、恢复与成功边界

- 中间 checkpoint 只保存 policy 和 optimizer.steps；缺 rank RNG。最终只记录 rank0 CPU Torch RNG，也不能当作完整 sampling replay state。
- policy_resume 校验来源 snapshot/config/manifest/prompt/文件哈希、world size、预算、AdamW groups/moments、LoRA 模式、policy keys/shape/finite 和逐张量复制。anchor 前后 digest 必须相同；明确 exact_sampling_replay=false。
- 保存未采用显式完成 marker 的事务 checkpoint，故目录存在不代表完整。外部读取要检查实际文件/状态/来源，不能靠目录名猜 saved step。
- E-014 segment 有 zero-valid-rollouts fail gate；E-013 非CF路径没有相同门禁，完成预算不等于产生有效任务输出。CF weight>0 则至少需要一个 eligible pair。这里记录契约差异，不自动把所有训练协议机械统一。
- group observer只读reward/adv：主严格胜率在混合组等权，ties另报，空mixed=null。跨rank合充分统计量，不平均rank rate。pending组不进入完成窗；optimizer和日志flush后end_update。中断summary显式pending/error。

## 尚未验证

实际权重/数据、PEFT切换/量化/DDP执行、显存、真实gradient/optimizer更新、版本 API、完全确定性、恢复回放、指标和训练收益均未运行验证。没有更新 Run 状态、恢复训练或读取远端结果。
