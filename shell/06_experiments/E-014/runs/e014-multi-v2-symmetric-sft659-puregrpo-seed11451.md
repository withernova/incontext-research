# e014-multi-v2-symmetric-sft659-puregrpo-seed11451 · multi_v2多实例枚举、两行模板、原SFT659独立纯GRPO

- workflow: v2 / failed / 运行失败
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-1b18d1e9199ce4ca1add2b4e / failed

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
在保持原E014 GRPO设置时，multiple distinct、更多不同实例枚举和两行模板能否使模型实际输出更多不同候选？

## 2. 目的
用户要求采用确认的新prompt立即开独立新训练。fresh从原SFT659初始化policy/固定anchor；不恢复step800、不覆盖旧分支或评测。

**假设或预期**：加强枚举文案可能减少单框输出；效果未验证，可能保持单框或增加重复/截断。

## 3. 方法（干预 · 对照 · 指标与判定规则）
独立fresh SFT659纯GRPO，仅选择multi_v2 prompt；沿用现有数据与奖励。候选数量变长、不凑固定框数、不增加GT；不自动评测。

**干预与对照**：只在原E014配置新增prompt_variant=multi_v2；原数据构造算法/seed、奖励权重与归约、GRPO算法和预算不变。fresh模型/AdamW/step0，不继承旧GRPO。旧分支曾中断并重新设种子，不能声称新旧为完全匹配随机轨迹的prompt单变量因果对照。

**指标计划**：先核验实际prompt与首步训练；全程记录原始rollout及候选数量/合法率/重复/覆盖。完成后单独授权匹配评测，再分析候选及score作用。

**指标计算定义**：训练原始rollout逐候选score/IoU/数量、selected位置、reward分量、空间逆序/覆盖/重复及梯度；工程metrics为1500steps/8rank/CF0/valid_rollouts，不替代科学收益。后续独立授权评测关注candidate_count/合法率/重复/First-Selected-Oracle/IoU命中。

**判定门槛 / no-silent-zero**：原source SHA固定；原SFT659与基座、clean Git/指定部署SHA；8GPU无compute PID且<64MiB，不停止他人任务；至少20GiB空闲；独占新payload；数据四格/图像SHA及源字段保留；promptVariant/hash核验；纯GRPO CF0；零有效回答不得完成；真实exit和1500/8rank覆盖。

**验收判定**：真实完整1500更新、world_size8、CF0、valid_rollouts>0、最终adapter/optimizer/原始rollout/data/config SHA、exit0及完成标记。实际prompt须multi_v2及SHA c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba；候选多样性是后续分析指标，不把文本指令当效果证据。

**预期特征**：新文案鼓励多实例枚举；不预设会增加有效不同候选或改善定位/漏定位。

## 4. 详细实现细节
multi_v2实际文本SHA c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba，Output multiple distinct...、Include as many different instances...、Do not repeat...、两行模板；Query结尾Predict multiple BBOX candidates。保留Reference同实例score定义/左到右/两位小数，不添加regardless of confidence。训练输入与快照、恢复校验、现有评测dataset一致传variant；v1默认SHA保持，不允许v1 checkpoint无声换prompt续训。9 Python3.9 AST、字符串全文/哈希、8训练算法helper AST、bash-n/diff检查通过，测试定义未运行。

**数据身份与构造**：原E013 overnight-train-2k/trainable_pairs.json SHA017bd2a64d1cb80dbb62152bf20a7fafada72a88cea4f5f3f88be152d1bb2130；只派生迁移两个图像路径字段，原图/身份/GT/split/review/来源不改。1000同类别不同身份来源源对，AB/BA×两Reference的两实例拼图，不为第三实例补造GT。

**数据规模**：原正2000+审核负2000输入；1000源对×四格=4000对称输入；共8000输入、4000两输入单元，8GPU每epoch500更新，3epoch1500，group4完整预算96000生成回答。

**模型与关键配置**：Qwen3-VL-8B-Instruct；原samples_00042136_step_000659/adapter初始化policy与固定anchor。8卡NF4 DDP、lr8e-5、group4、seed11451、epochs3、192new tokens、max_pixels262144、beta.04、clip.2、gradnorm1、每50步保存。无e014_resume。

**代码架构**：通过可选variant复用prompt/messages、prepare_prompt、trainer/采样/重放/optimizer、数据builder及E14 evaluator；新增薄config/shell，不新增训练Python协调器，不全项目重构。

**实现摘要**：复用原E014 coordinator/data/reward/GRPO核心，只增加可选prompt_variant=multi_v2与薄shell/config。审阅c19acecc35fb927a通过，精确提交并发布2ccee4cfb98d0ae4d9c1e1cc7e052f6d21fe44bc；未部署、未模型执行。

- 公共包：`iploc_szy`
- 入口：`tools.run_e014_grpo:main`
- 配置：`configs/experiments/E-014/training/e014_multi_v2_symmetric_grpo.py`
- Shell launcher：`tools/run/train/e014_multi_v2_symmetric_grpo.sh`
- 复用模块：iploc_szy/rl/trainer.py, iploc_szy/rl/core.py, iploc_szy/rl/data.py, iploc_szy/rl/policy.py, iploc_szy/rl/sampling.py, iploc_szy/rl/e014.py, iploc_szy/prompting/e014.py, tools/data/build_e014_symmetric_candidates.py, tools/run_e014_grpo.py
- 新增模块：（待登记）
- 测试路径（不代表已执行）：tests/test_e014_multi_v2_prompt.py

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `bash tools/run/train/e014_multi_v2_symmetric_grpo.sh`
- commit: `2ccee4cfb98d0ae4d9c1e1cc7e052f6d21fe44bc`
- workspace: 03
- tmux: e014-multi-v2-grpo
- log: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-symmetric-sft659-puregrpo-seed11451/managed_console.log
- output: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-symmetric-sft659-puregrpo-seed11451/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
192token可能限制/截断更长回答；两个格式示例不是固定两个输出，parser仍允许至少一个完整pair。奖励不硬性强迫更多框。合成两实例不等于自然同图消歧；其他对象未完整标注。不自动评测/重启；已有测试集多次查看；缺匹配随机轨迹/多seed，不能直接判定prompt因果收益。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "necessity": "旧step800评测1766条原始输出均只有一个answer-score pair，First/Selected/Oracle mIoU均0.700190580357638；新指令旨在鼓励多个不同实例枚举，不预设效果。",
  "evidence_basis": "旧评测已真实exit0、完成标记、两次稳定metrics及managed completed/analysis_pending；原始1766完整index/unique ID、8rank覆盖、raw文本均一组pair已复核。实际输入prompt与v1冻结SHA15181c...逐字一致，没有切回旧prompt或截取第一个框。",
  "implementation_summary": "复用原E014 coordinator/data/reward/GRPO核心，只增加可选prompt_variant=multi_v2与薄shell/config。审阅c19acecc35fb927a通过，精确提交并发布2ccee4cfb98d0ae4d9c1e1cc7e052f6d21fe44bc；未部署、未模型执行。",
  "implementation_details": "multi_v2实际文本SHA c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba，Output multiple distinct...、Include as many different instances...、Do not repeat...、两行模板；Query结尾Predict multiple BBOX candidates。保留Reference同实例score定义/左到右/两位小数，不添加regardless of confidence。训练输入与快照、恢复校验、现有评测dataset一致传variant；v1默认SHA保持，不允许v1 checkpoint无声换prompt续训。9 Python3.9 AST、字符串全文/哈希、8训练算法helper AST、bash-n/diff检查通过，测试定义未运行。",
  "model_config": "Qwen3-VL-8B-Instruct；原samples_00042136_step_000659/adapter初始化policy与固定anchor。8卡NF4 DDP、lr8e-5、group4、seed11451、epochs3、192new tokens、max_pixels262144、beta.04、clip.2、gradnorm1、每50步保存。无e014_resume。",
  "metric_plan": "先核验实际prompt与首步训练；全程记录原始rollout及候选数量/合法率/重复/覆盖。完成后单独授权匹配评测，再分析候选及score作用。",
  "data_definition": "原E013 overnight-train-2k/trainable_pairs.json SHA017bd2a64d1cb80dbb62152bf20a7fafada72a88cea4f5f3f88be152d1bb2130；只派生迁移两个图像路径字段，原图/身份/GT/split/review/来源不改。1000同类别不同身份来源源对，AB/BA×两Reference的两实例拼图，不为第三实例补造GT。",
  "data_scale": "原正2000+审核负2000输入；1000源对×四格=4000对称输入；共8000输入、4000两输入单元，8GPU每epoch500更新，3epoch1500，group4完整预算96000生成回答。",
  "variables_controls": "只在原E014配置新增prompt_variant=multi_v2；原数据构造算法/seed、奖励权重与归约、GRPO算法和预算不变。fresh模型/AdamW/step0，不继承旧GRPO。旧分支曾中断并重新设种子，不能声称新旧为完全匹配随机轨迹的prompt单变量因果对照。",
  "metric_definition": "训练原始rollout逐候选score/IoU/数量、selected位置、reward分量、空间逆序/覆盖/重复及梯度；工程metrics为1500steps/8rank/CF0/valid_rollouts，不替代科学收益。后续独立授权评测关注candidate_count/合法率/重复/First-Selected-Oracle/IoU命中。",
  "integrity_gates": "原source SHA固定；原SFT659与基座、clean Git/指定部署SHA；8GPU无compute PID且<64MiB，不停止他人任务；至少20GiB空闲；独占新payload；数据四格/图像SHA及源字段保留；promptVariant/hash核验；纯GRPO CF0；零有效回答不得完成；真实exit和1500/8rank覆盖。",
  "expected_outcome": "新文案鼓励多实例枚举；不预设会增加有效不同候选或改善定位/漏定位。",
  "acceptance_criteria": "真实完整1500更新、world_size8、CF0、valid_rollouts>0、最终adapter/optimizer/原始rollout/data/config SHA、exit0及完成标记。实际prompt须multi_v2及SHA c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba；候选多样性是后续分析指标，不把文本指令当效果证据。",
  "claim_boundary": "训练工程完成不证明候选多样性、score排序、Reference机制、泛化或漏检改善；不升级Claim。新框数量仍需真实输出核查。",
  "audit_paths": "docs/e014_multi_v2_training.md; payload/plan.json; payload/implementation.json; payload/trainer_config.json; payload/grpo/config_snapshot.json; payload/grpo/rollouts-rank*.jsonl; payload/grpo/checkpoints; payload/grpo/completed.json; payload/grpo/e014_valid_rollouts.json; metrics.json"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
