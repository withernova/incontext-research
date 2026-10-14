# e014-variable-symmetric-sft659-puregrpo-seed11451 · SFT659 变长候选与双向对称数据纯 GRPO

- workflow: v2 / failed / 运行失败
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-385d5800580660ab8ef4d5cb / failed
- spec_drift_fields（批准后有改动）：command, implementation_details, implementation_summary, log_path

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
模型自行决定候选数量时，空间顺序与 Reference/位置双向对称训练能否减轻首位偏向，同时保留定位和实例覆盖？

## 2. 目的
从未经过 GRPO 的原置信度 SFT659 新开纯 GRPO 分支，让模型自然发掘潜在实例并按左到右输出，由 score 选择目标。当前 Run 执行训练与完整日志采集，不自动运行已查看测试集评测。

## 3. 方法（干预 · 对照 · 指标与判定规则）
新变长 prompt；保留原正负输入并混合两实例 AB/BA × 两 Reference 的四格数据；使用选框 IoU、最坏候选 Brier、两两 score 排序、空间逆序、最强重复对、错误实例高分及一对一覆盖奖励。没有 score CE、旧反事实偏好、SDS/Evidence reward。该 Run 同时改变候选数量、数据和部分 reward 归约，不是 prompt 单变量消融。

**干预与对照**：无新增 matched baseline Run；初始化固定SFT659，不继承旧GRPO。原始输入身份和标签保留；对称两个方向完整覆盖；原始/对称两输入单元1:1。新增归约与空间奖励须单独记录；单次训练不能隔离每项干预贡献。

**指标计划**：训练记录每条rollout的候选数、score/IoU、selected位置、总reward和全部分量、空间逆序率、覆盖、重复、advantage/梯度；每步checkpoint。后续独立评测再报告SelectedIoU、OracleIoU、OracleGap、NonFirstAcc及条件n；IoU和score并列都选最早。当前不自动评测。

**判定门槛 / no-silent-zero**：原清单SHA固定；迁移只改两个图像路径字段；数据四格覆盖和生成图像SHA核验；step659 adapter固定；代码干净、SHA一致；八卡无占用；输出目录不存在；纯GRPO cf权重0；全程零有效回答禁止完成；真实exit_code与completed步数/卡数核验；失败保留，不自动重启。

**验收判定**：工程：完成1500更新、8卡、cf_pairs0、至少一条有效回答、最终adapter与原始rollout/配置/数据SHA完整、真实exit0。科学：训练本身不判定；后续独立匹配评测需单独设计。

## 4. 详细实现细节
原SFT659 policy+anchor初始化保持不变，再仅恢复step100 policy adapter、AdamW及固定数据/epoch进度；验证所有policy tensor、optimizer结构/矩、文件和数据/config/prompt SHA，并验证anchor摘要不变。源payload和data只读，新resume-100独占写入；first new update101、remaining1400、目标累计1500。checkpoint无rank RNG，按原seed+rank重设种子，exact_sampling_replay=false，未保存101–119更新重新计算。保留同一纯GRPO科学方案、8卡/seed/超参/原始数据，不自动评测，不补造旧退出码。用户明确授权撤回服务器单个E013 SDS shell修改，已安全归档后仅git restore该文件，其他源文件不变。

**数据身份与构造**：原输入 SHA 017bd2a64d1cb80dbb62152bf20a7fafada72a88cea4f5f3f88be152d1bb2130；只在 Run/data 派生清单迁移 query_image/reference_image 的旧路径前缀，其他字段逐值保留。仅 train 正例构造同类别、不同身份和来源的两实例拼图；AB/BA 各两个 Reference；不为其他物体补标，不伪造拼图负例。

**数据规模**：原 train 正例2000+已审核负例2000；1000源对×2布局×2 Reference=4000对称输入；合计8000输入、4000两输入单元，每轮500更新、3轮1500更新、group4共96000生成回答（完整运行时）。

**模型与关键配置**：Qwen3-VL-8B-Instruct，原 SFT samples_00042136_step_000659/adapter；8卡NF4 DDP；lr8e-5，epochs3，group_size4，seed11451，max_new_tokens192，max_pixels262144，beta0.04，clip0.2，max_grad_norm1，每50步保存。

**代码架构**：公共包iploc_szy；复用rl.trainer/core/policy/sampling/data与旧拼图renderer，E014 prompt/reward/数据校验/evaluator为隔离增量；专属数据协调器与shell入口；不复制训练循环或改变E013默认值。

**实现摘要**：Step100续训实现已审阅9dd6edde88bdd839、提交/发布/部署6cef1bac0218c67c029e194b1100750316b65ae1；4文件Python3.9 AST、算法helpers一致、bash-n、diff-check通过。测试定义未运行，尚无实际恢复或GPU更新证据。

- 公共包：`iploc_szy`
- 入口：`tools.run_e014_grpo:main`
- 配置：`configs/experiments/E-014/training/e014_variable_symmetric_grpo.py`
- Shell launcher：`tools/run/train/e014_variable_symmetric_grpo.sh`
- 复用模块：iploc_szy/rl/trainer.py, iploc_szy/rl/core.py, iploc_szy/rl/policy.py, iploc_szy/rl/sampling.py, iploc_szy/rl/data.py, tools/data/build_e013_counterfactual_collages.py
- 新增模块：iploc_szy/prompting/e014.py, iploc_szy/rl/e014.py, iploc_szy/rl/e014_data.py, iploc_szy/evaluation/e014.py, tools/data/build_e014_symmetric_candidates.py, tools/run_e014_grpo.py
- 测试路径（不代表已执行）：tests/test_e014_variable_candidates.py

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `bash tools/run/train/e014_variable_symmetric_grpo.sh --run-id e014-variable-symmetric-sft659-puregrpo-seed11451 --resume-step 100`
- commit: `6cef1bac0218c67c029e194b1100750316b65ae1`
- workspace: 03
- tmux: e014-variable-symmetric-grpo
- log: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-variable-symmetric-sft659-puregrpo-seed11451/resume-100-console.log
- output: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-variable-symmetric-sft659-puregrpo-seed11451/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
合成两图拼接不等于自然同图消歧；未对其他物体完整标注。192token限制实际候选数；零框协议未新增。max Brier和重复归约避免各自数量稀释但不保证整个reward无捷径；二元Brier与连续IoU排序仍可能冲突。无matched baseline、独立评测或多seed，不作效果Claim。代码未测试、未做import启动验证；尚未发布/部署或启动。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "implementation_summary": "Step100续训实现已审阅9dd6edde88bdd839、提交/发布/部署6cef1bac0218c67c029e194b1100750316b65ae1；4文件Python3.9 AST、算法helpers一致、bash-n、diff-check通过。测试定义未运行，尚无实际恢复或GPU更新证据。",
  "implementation_details": "原SFT659 policy+anchor初始化保持不变，再仅恢复step100 policy adapter、AdamW及固定数据/epoch进度；验证所有policy tensor、optimizer结构/矩、文件和数据/config/prompt SHA，并验证anchor摘要不变。源payload和data只读，新resume-100独占写入；first new update101、remaining1400、目标累计1500。checkpoint无rank RNG，按原seed+rank重设种子，exact_sampling_replay=false，未保存101–119更新重新计算。保留同一纯GRPO科学方案、8卡/seed/超参/原始数据，不自动评测，不补造旧退出码。用户明确授权撤回服务器单个E013 SDS shell修改，已安全归档后仅git restore该文件，其他源文件不变。",
  "model_config": "Qwen3-VL-8B-Instruct，原 SFT samples_00042136_step_000659/adapter；8卡NF4 DDP；lr8e-5，epochs3，group_size4，seed11451，max_new_tokens192，max_pixels262144，beta0.04，clip0.2，max_grad_norm1，每50步保存。",
  "metric_plan": "训练记录每条rollout的候选数、score/IoU、selected位置、总reward和全部分量、空间逆序率、覆盖、重复、advantage/梯度；每步checkpoint。后续独立评测再报告SelectedIoU、OracleIoU、OracleGap、NonFirstAcc及条件n；IoU和score并列都选最早。当前不自动评测。",
  "data_definition": "原输入 SHA 017bd2a64d1cb80dbb62152bf20a7fafada72a88cea4f5f3f88be152d1bb2130；只在 Run/data 派生清单迁移 query_image/reference_image 的旧路径前缀，其他字段逐值保留。仅 train 正例构造同类别、不同身份和来源的两实例拼图；AB/BA 各两个 Reference；不为其他物体补标，不伪造拼图负例。",
  "data_scale": "原 train 正例2000+已审核负例2000；1000源对×2布局×2 Reference=4000对称输入；合计8000输入、4000两输入单元，每轮500更新、3轮1500更新、group4共96000生成回答（完整运行时）。",
  "variables_controls": "无新增 matched baseline Run；初始化固定SFT659，不继承旧GRPO。原始输入身份和标签保留；对称两个方向完整覆盖；原始/对称两输入单元1:1。新增归约与空间奖励须单独记录；单次训练不能隔离每项干预贡献。",
  "integrity_gates": "原清单SHA固定；迁移只改两个图像路径字段；数据四格覆盖和生成图像SHA核验；step659 adapter固定；代码干净、SHA一致；八卡无占用；输出目录不存在；纯GRPO cf权重0；全程零有效回答禁止完成；真实exit_code与completed步数/卡数核验；失败保留，不自动重启。",
  "acceptance_criteria": "工程：完成1500更新、8卡、cf_pairs0、至少一条有效回答、最终adapter与原始rollout/配置/数据SHA完整、真实exit0。科学：训练本身不判定；后续独立匹配评测需单独设计。",
  "claim_boundary": "工程完成只表示规定训练覆盖及有效产物，不证明选框收益、reference机制、泛化或新颖性；不升级Claim。",
  "artifacts": "原payload/及managed_console.log保留只读；新增resume-100-console.log; resume-100/plan.json; resume-100/implementation.json; resume-100/trainer_config.json; resume-100/training.log; resume-100/grpo/config_snapshot.json; resume-100/grpo/resume-evidence-rank*.json; resume-100/grpo/rollouts-rank*.jsonl; resume-100/grpo/checkpoints/; resume-100/grpo/completed.json; resume-100/grpo/e014_valid_rollouts.json; resume-100/exit_code.txt; resume-100/status.json; metrics.json仅工程完成",
  "audit_paths": "shell/06_experiments/E-014/prompt_comparison.md; docs/e014_variable_symmetric_grpo.md; code_review eb7c47b4db2202fb; commit560d94028d031127dfa7faf816be87518244c032"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
