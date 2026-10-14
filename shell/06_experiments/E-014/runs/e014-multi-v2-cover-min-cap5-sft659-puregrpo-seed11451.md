# e014-multi-v2-cover-min-cap5-sft659-puregrpo-seed11451 · multi_v2 / min实例覆盖 / soft预算5 / 同组奖励诊断 / freshSFT659纯GRPO

- workflow: v2 / failed / 运行失败
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-49087b01fe0ef97c5e8a5730 / failed

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
新奖励下同prompt混合采样组是否更偏好多框，且多框探索是否仍随训练减少？

## 2. 目的
用户要求保留已讨论的min覆盖/软预算5及小幅权重方案，增加同采样组multi比single奖励更高的条件概率诊断，代码完成后创建Run等待人工批准。新独立freshSFT659，不自动恢复旧200/800。

**假设或预期**：min完整覆盖与轻量软预算可能改善有效多框的reward竞争。若mixed组胜率/正优势较高而multi率下降，探索不足得到更多支持，但不构成排除其他机制的因果证明。

## 3. 方法（干预 · 对照 · 指标与判定规则）
独立freshSFT659/multi_v2纯GRPO，固定数据/采样/损失；同时记录50更新窗的mix率、multi率与reward比较，不额外模型探针。

**干预与对照**：prompt保持multi_v2，SHAc6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba，变量框数/左到右/Reference同实例score。loc1、cal/neg1.1、rank.6/score margin.1/IoU差.1、dup.06/阈.9、order.12、distractor.6、coverage1/min、count_weight.05/soft_limit5。1–5无数量奖惩，>5每框-.05不硬拒绝；invalid仍强罚并扣raw超额。G4/T1/top_p1/top_k0/192tokens/max_pixels262144/lr8e-5/beta.04/clip.2/gradnorm1/seed11451/save50不变；CF0无CE。

**指标计划**：明确mixed组等权q主口径、strict>、tie与null；group/sample分母及条件窗口分层；保留pooled/best/mean差/正adv辅指标，不偷换指标定义。

**指标计算定义**：主诊断p_multi_reward_gt_single：对合法终止mixed组g，qg=sum_{multi i,single j}1[Ri>Rj]/(nM*nS)，再对mixed组等权平均。按采样组比较，绝不跨prompt/Reference/rank配对，actual total reward。空mixed分母null，strict>与tie分离。附mixed_groups/总groups/比较pairs、tie probability、mean组内multi-single reward差、best-multi vs best-single、pooled pair概率、multi实际正adv率、多框率(all/given-valid)、invalid、按original正/负和collage正分层、每50完成更新窗。

**判定门槛 / no-silent-zero**：冻结源manifest/alias/identity/GT/split/provenance；真实双源实例位置仅用于对称候选覆盖，不进入Query消息。独占payload拒绝覆盖，原checkpoint200/800只读。指定SHA部署/conda:IPLoc固定环境、8GPU idle、正式managed authorization。observer pending pre-update group不混入完成窗口，统计完整覆盖/rank/update校验，无mixed不静默0。

**验收判定**：工程：1500真实完成更新/8rank/CF0/valid>0/exit0/marker/metrics及独占产物；group统计覆盖24000组/96000rollouts、valid计数与训练一致、每ranklast_completed1500/pending0、概率可从充分统计量重算、无mixed=null。无论概率高低都保存真实结果，不为预期修改数据或重跑。

**预期特征**：判断观察到的mixed组多框是否通常获得更高reward/正adv，以及此支持是否伴随多框探索下降。不预设新奖励能解决塌缩。

## 4. 详细实现细节
仅共享E14 reward扩展mode min与count0默认；独立config显式新权重。stdlib group_statistics默认关闭，本Run window50启用，采样组优势计算后只读reward/adv，optimizer成功后记完成窗口。per-rank group/windows/summary独占日志，最终coordinator核验8rank/更新/group/rollout/valid后合并。7数值训练helper AST与6核心reward/policy/sampling/prompt字节核查不变；无包import/smoke/测试套件/模型/CUDA执行。

**数据身份与构造**：冻结原trainable_pairs.json SHA017bd2a64d1cb80dbb62152bf20a7fafada72a88cea4f5f3f88be152d1bb2130。原4000正负输入仅image路径派生到只读alias；1000同类不同身份/来源源对，AB/BA×ReferenceA/B生成4000对称正输入。只用真实源对象标注，其他对象不制造GT。

**数据规模**：8000输入/4000pair；原2000正+2000负；对称4000正。8rank500update/epoch×3=1500，2prompt/rank/update×4rollouts=64全局，完整96000生成。

**模型与关键配置**：Qwen3-VL-8B-Instruct/NF4doublequant/bfloat16/SDPA，8GPU DDP。policy与固定anchor均从原samples_00042136_step_000659/adapter加载，只有policyLoRA AdamW。不是200恢复、不可通过adapter_path偷换anchor。

**代码架构**：纯std只读observer在现有trainer可关闭接入，代码未改reward/adv/loss运算；现有coordinator最终merge充分统计量，config/shell保持薄入口，旧默认和原产物不变。

**实现摘要**：reward方案review d08d72b78a35e664/commit8604224b已发布；新增observer review3ddc36253af0b8c3通过，精确提交并发布f1806d2e269989d541dfdbf556a9af5b91e2290f，未部署/执行。

- 公共包：`iploc_szy`
- 入口：`tools.run_e014_grpo:main`
- 配置：`configs/experiments/E-014/training/e014_multi_v2_cover_min_cap5_grpo.py`
- Shell launcher：`tools/run/train/e014_multi_v2_cover_min_cap5_grpo.sh`
- 复用模块：iploc_szy/rl/trainer.py, iploc_szy/rl/core.py, iploc_szy/rl/e014.py, iploc_szy/rl/data.py, iploc_szy/rl/policy.py, iploc_szy/rl/sampling.py, iploc_szy/prompting/e014.py, tools/data/build_e014_symmetric_candidates.py
- 新增模块：iploc_szy/rl/group_statistics.py
- 测试路径（不代表已执行）：tests/test_e014_cover_min_cap5.py, tests/test_group_reward_statistics.py

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `bash tools/run/train/e014_multi_v2_cover_min_cap5_grpo.sh`
- commit: `f1806d2e269989d541dfdbf556a9af5b91e2290f`
- workspace: 03
- tmux: e014-cover-min-cap5-grpo
- log: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-sft659-puregrpo-seed11451/managed_console.log
- output: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-sft659-puregrpo-seed11451/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
多框不保证不同实例/真实覆盖。min coverage稀疏、增加cal/distractor惩罚可能保守。混合组条件有选择偏差，不能代表全single组反事实；需条件/时间窗/denominator。KL/EOS信用和token归约也可能影响。不存在独立pair CI；同组pair与跨epochprompt相关。新reward多项同时变化，不能单因素归因。旧测试集已看，仅探索诊断；不自动评测或恢复。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "necessity": "旧multi_v2 200的1766 greedy全部单框；前200随机rollout多框82/12800，50更新块74/5/2/1。需区分观测到的多框奖励竞争与探索消失，不凭多框率猜测奖励原因。",
  "evidence_basis": "用户接受已有方案继续，并明确提出P(Rmulti>Rsingle|同组出现两者)。coverage来自人工AB/BA拼接Query中两个不同源实例的已知框，不是同Reference双目标GT；原单GT输入不启用此项。所有旧Run已暂停/评测已完成、原产物只读保留。",
  "implementation_summary": "reward方案review d08d72b78a35e664/commit8604224b已发布；新增observer review3ddc36253af0b8c3通过，精确提交并发布f1806d2e269989d541dfdbf556a9af5b91e2290f，未部署/执行。",
  "implementation_details": "仅共享E14 reward扩展mode min与count0默认；独立config显式新权重。stdlib group_statistics默认关闭，本Run window50启用，采样组优势计算后只读reward/adv，optimizer成功后记完成窗口。per-rank group/windows/summary独占日志，最终coordinator核验8rank/更新/group/rollout/valid后合并。7数值训练helper AST与6核心reward/policy/sampling/prompt字节核查不变；无包import/smoke/测试套件/模型/CUDA执行。",
  "model_config": "Qwen3-VL-8B-Instruct/NF4doublequant/bfloat16/SDPA，8GPU DDP。policy与固定anchor均从原samples_00042136_step_000659/adapter加载，只有policyLoRA AdamW。不是200恢复、不可通过adapter_path偷换anchor。",
  "metric_plan": "明确mixed组等权q主口径、strict>、tie与null；group/sample分母及条件窗口分层；保留pooled/best/mean差/正adv辅指标，不偷换指标定义。",
  "data_definition": "冻结原trainable_pairs.json SHA017bd2a64d1cb80dbb62152bf20a7fafada72a88cea4f5f3f88be152d1bb2130。原4000正负输入仅image路径派生到只读alias；1000同类不同身份/来源源对，AB/BA×ReferenceA/B生成4000对称正输入。只用真实源对象标注，其他对象不制造GT。",
  "data_scale": "8000输入/4000pair；原2000正+2000负；对称4000正。8rank500update/epoch×3=1500，2prompt/rank/update×4rollouts=64全局，完整96000生成。",
  "variables_controls": "prompt保持multi_v2，SHAc6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba，变量框数/左到右/Reference同实例score。loc1、cal/neg1.1、rank.6/score margin.1/IoU差.1、dup.06/阈.9、order.12、distractor.6、coverage1/min、count_weight.05/soft_limit5。1–5无数量奖惩，>5每框-.05不硬拒绝；invalid仍强罚并扣raw超额。G4/T1/top_p1/top_k0/192tokens/max_pixels262144/lr8e-5/beta.04/clip.2/gradnorm1/seed11451/save50不变；CF0无CE。",
  "metric_definition": "主诊断p_multi_reward_gt_single：对合法终止mixed组g，qg=sum_{multi i,single j}1[Ri>Rj]/(nM*nS)，再对mixed组等权平均。按采样组比较，绝不跨prompt/Reference/rank配对，actual total reward。空mixed分母null，strict>与tie分离。附mixed_groups/总groups/比较pairs、tie probability、mean组内multi-single reward差、best-multi vs best-single、pooled pair概率、multi实际正adv率、多框率(all/given-valid)、invalid、按original正/负和collage正分层、每50完成更新窗。",
  "integrity_gates": "冻结源manifest/alias/identity/GT/split/provenance；真实双源实例位置仅用于对称候选覆盖，不进入Query消息。独占payload拒绝覆盖，原checkpoint200/800只读。指定SHA部署/conda:IPLoc固定环境、8GPU idle、正式managed authorization。observer pending pre-update group不混入完成窗口，统计完整覆盖/rank/update校验，无mixed不静默0。",
  "expected_outcome": "判断观察到的mixed组多框是否通常获得更高reward/正adv，以及此支持是否伴随多框探索下降。不预设新奖励能解决塌缩。",
  "acceptance_criteria": "工程：1500真实完成更新/8rank/CF0/valid>0/exit0/marker/metrics及独占产物；group统计覆盖24000组/96000rollouts、valid计数与训练一致、每ranklast_completed1500/pending0、概率可从充分统计量重算、无mixed=null。无论概率高低都保存真实结果，不为预期修改数据或重跑。",
  "claim_boundary": "主诊断高且multi率下降支持Exploration瓶颈假设，但不能单独确定主要原因或排除Reward Design。该Run不自动validated Claim，不输出因果结论；工程complete不等于收益。",
  "audit_paths": "docs/e014_multi_v2_cover_min_cap5_grpo.md; docs/e014_group_reward_statistics.md; payload/plan.json; payload/implementation.json; payload/grpo/config_snapshot.json; payload/grpo/rollouts-rank*.jsonl; payload/grpo/group-rewards-rank*.jsonl; payload/grpo/group-reward-windows-rank*.jsonl; payload/grpo/group-reward-summary-rank*.json; metrics.json"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
