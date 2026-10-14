# R-011-query-keepset-large-pruning · 只留选中注意力头的大幅裁剪曲线

- workflow: v2 / ready_to_run / 等待执行授权
- review_status: approved
- group_id: 未分组
- execution_dispatch:  / 
- spec_drift_fields（批准后有改动）：command, conclusion_scope, log_path, output_dir, tmux_session

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
把选定集合之外的注意力头整体移除后，模型自由生成的定位性能是否守住？在三份保留名单（旧固定组、双角色筛查组、二者并集）与同规模随机保留集合之间，是否存在稳定差异？

## 2. 目的
直接比较「只留少数注意力头」与「随机也只留同样多个」在同一删除比例下的定位性能差异，用来判断被选中的头是否真的承载定位能力，而不是让结论继续依赖交叉熵敏感度。

## 3. 方法（干预 · 对照 · 指标与判定规则）
干预（细删）：对指定文本 query head，只把 bbox 坐标预测行（四个坐标字段的 p-1 行）× 该图像角色视觉 token 的注意力边置零，不重归一化；上下文行、文本边、残差与 MLP 保持原样。本轮角色只做 query 图像。所有条件（含随机对照）用同一种删法。条件=基线；只留保留集合的读出通路；同规模随机保留集合 3 组；删除规模 5%/10%/20% 各两条线——优先保住保留集合 vs 纯随机。三份保留名单（旧固定组 5、双角色筛查组 5、并集 10）各跑一遍，必须在同一删除规模下对齐比较。指标：自由生成 bbox 的 mIoU 变化为主；teacher-forced argmax 框的 IoU 变化为确定性辅助轴；teacher-forced 坐标 CE 变化只作机制诊断。判定：只有保留集合在同规模随机之上、且在某删除规模下 mIoU 不显著低于基线，才称该集合的 bbox 读出通路足以维持定位；两条线无差异则说明当前选头没有挑出承重 head。

**干预与对照**：保留名单（旧固定组 / 双角色筛查组 / 并集）× 删除规模（只留保留集合 / 5% / 10% / 20%）× 是否优先保住保留集合；对照为同层、同数量随机保留集合 3 组；全部条件共用细删口径

**指标计划**：主指标：自由生成 bbox 的 mIoU 变化（invalid 框记 0 并单独报 invalid 率）；确定性辅助轴：teacher-forced argmax 框的 IoU 变化；机制诊断：teacher-forced 坐标 token 平均 CE 变化。汇总：逐样本配对差、样本等权均值、按 sequence/共享图像 component 聚类的 bootstrap 95% CI、正负方向比例。

**判定门槛 / no-silent-zero**：基线空 hook parity；细删只在 bbox 坐标预测行 × query 图像视觉键上生效，逐条审计实际干预的行数、边数与移除的注意力质量（生成阶段必须能证明确实干预了该干预的行，否则细删会静默退化为没删或全删）；单独报告格式跑偏样本比例与实际干预行数为 0 的样本比例；三份保留名单与并集规模一致性校验；保留集合与随机对照的层分布对齐；生成轴与 teacher-forced 轴同时落盘。

**验收判定**：判定规则（事先冻结）：以配对样本 ΔmIoU 的 cluster-bootstrap 95% CI 为准。「守住」= CI 下界 > −0.01（即下降不超过 1 个 mIoU 点）；「崩」= CI 上界 < −0.01；介于两者之间记为未决。某档位要算支持「保留集合足够承载定位」，必须同时满足：该档位保留集合守住，且同档位随机对照不满足守住条件。全部档位都守不住，或保留集合与随机对照无差异，都记为不支持。

### 已注册指标定义
- **bbox梯度绝对贡献（逐head样本均值）** (`bbox_grad_abs_contrib_mean`)：C_lh = mean_n sum_{p,j in query} |A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]|；teacher-forced bbox token平均CE对指定query->query视觉注意力边的局部敏感度绝对量；只表示当前输入下的敏感度大小，不是因果必要性，也不是增强方向证据；每条边先取绝对值，再按样本求和，最后样本等权平均；不除以视觉token数 / Qwen3-VL-8B+LoRA、36层x32 query heads=1152 heads；20条先导与690条扩展两轮eval子集
- **bbox梯度signed贡献（逐head样本均值）** (`bbox_grad_signed_contrib_mean`)：S_lh = mean_n sum_{p,j in query} A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]；对post-softmax指定边做不重归一化乘法缩放时的一阶CE导数方向；本轮有限差分与反传符号不一致，方向暂不可用于增强/抑制决策；样本等权平均 / 同上1152 heads；20条与690条两轮eval子集
- **平均bbox token CE** (`bbox_token_ce_mean`)：mean_n mean_i CE(logits[p_i-1], token[p_i])；teacher-forced query bbox片段（含标点）平均交叉熵，仅表示损失量级，不是IoU或定位准确率；样本等权平均 / 690条（LaSOT 300/GOT10k 90/TAO 300）与20条先导
- **头部排名集合Jaccard** (`head_ranking_jaccard`)：|A∩B|/|A∪B|；不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升；对固定Top-k集合直接计算 / 20条vs690条、690条对旧固定5 head；Top-5/Top-10/Top-50
- **有限差分与反传符号一致** (`finite_difference_sign_agreement`)：sign(central_difference) == sign(signed_derivative)；首样本指定边±epsilon缩放的中央差分是否与反传signed导数同号；本轮为false，说明梯度方向链路校验未通过；首样本单一诊断，不参与排名 / 690条run首样本dataset_index=0 L24H25，epsilon=0.02

## 4. 详细实现细节
数据与规模：主样本集 180 条（每数据集 60），实现正确性先跑 60 条 pilot。代码：新增 configs/experiments/E-012/analysis/ 下的细删 keep-set config 与 tools/run/analysis/e012/ 对应 launcher，以及细删收集模块；head 列表不另写，只引用已冻结的 experiments/E-012/inputs/old_new_union10_heads_v1.json（sha256 19153e28f4cd4cfdd2c806dfd0de5f48b00c58b7f8860fa0b7b62a653f2a80b9，key=candidate_heads，group=old_e009_fixed5 / new_r006_query5）。teacher-forced 侧按 bbox 坐标行定位，复用 head_circuit.py 的 rows×query_span 口径与 collator 的字符区间到 token 区间对齐。自由生成侧的行选择用前缀规则：助手答案格式由本仓库 format_box 生成（[x1,y1,x2,y2]，紧凑无空格，助手轮不含其它文字），从助手输出的第一个 [ 到配对的 ] 之间的每一行都算坐标行并施加细删，] 之后停止；已定【放宽口径】：逗号等分隔 token 所在行同样计入（比严格只算数字字符略宽，需在结果中报告多计入的行数）；格式跑偏（无 [、多组括号、数字段不足四个）时停止干预并记 invalid，另报实际干预行数为 0 的样本比例；只认助手输出第一组括号，避免复述参考框被误算。生成协议沿用同类消融：greedy，max_new_tokens=128，vision_max_patch_tokens=1024，eager。模型沿用同一条 union10 消融的 checkpoint（E-009 step741）。环境与命令：conda:IPLoc，bash tools/run/analysis/e012/<launcher>.sh，先 --inspect 再执行。

**数据规模**：主样本集 150 条（LaSOT/GOT10k/TAO 各 50），取自 R-001 冻结索引并沿用同一退化样本排除项；按配置先跑同参数 pilot 验证实现，再扩到 150 条。删除规模按每层等量移除 2/3/6 个 head（合计 72/108/216，即 6.25%/9.375%/18.75%），另加只留保留集合的极端档（并集则移除 1142 个 head，单组移除 1147 个）。随机对照每个规模 3 个 seed（20260912/13/14），bootstrap seed 20260914、1000 次。条件总数 49：baseline 1 + keep_only 3 + 同层同数量随机保留集合 9 + protected 27 + random 9；150×49≈7350 次生成。若 GPU 预算不足，只允许在开跑前下调随机 seed 组数，不得下调删除档位，也不得看结果后调整。

**实现摘要**：细删收集模块已实现并提交 5a2c794：keepset_pruning.py 含 49 条条件表、生成阶段前缀规则、逐条干预审计与配对 bootstrap 汇总；离线校验通过（10 个聚焦单测 + 69 个目录契约测试 + --validate-only）；尚未在 GPU 上运行。

- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy/tools/run/analysis/e012/e012_r011_query_keepset_pruning_step741.sh`
- commit: `5a2c7943ff770a1e159ab0b0a52209da2cada4f2`
- workspace: 02
- tmux: incontext-E-012-R-011-query-keepset-large-pruning
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-011-query-keepset-large-pruning/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/r011-query-keepset-pruning-step741-v1
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
细删只覆盖「把定位信息写进 bbox 坐标字」这一步读出，上下文行与其它通路未动，因此守住只说明读出受控，不说明这些 head 是承载定位的核心；本轮结论与既有整头置零对照（旧五头 vs 新五头、并集十头、CE–IoU 探针）口径不同，不可直接比较；生成阶段行选择已冻结为「首个 [ 到配对 ] 之间全部行」的放宽口径，比严格只算数字字符略宽，且格式跑偏样本会被记为 invalid，因此必须同时报告多计入的行数与 invalid 比例；覆盖范围仅 query 角色名单；候选筛选在另一 checkpoint 上完成（step247 选头、step741 评测），名次可能漂移；自由生成 mIoU 有运行间噪声，条件数约 40 且样本 180，单档位只靠 3 个随机 seed 估计随机臂波动。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "necessity": "现在没有任何实验说明选定注意力头在最终定位指标上是否承重；这是把「选头方法是否有效」变成可判定问题、并为后续裁剪方案提供依据的唯一证据缺口。",
  "implementation_summary": "细删收集模块已实现并提交 5a2c794：keepset_pruning.py 含 49 条条件表、生成阶段前缀规则、逐条干预审计与配对 bootstrap 汇总；离线校验通过（10 个聚焦单测 + 69 个目录契约测试 + --validate-only）；尚未在 GPU 上运行。",
  "implementation_details": "数据与规模：主样本集 180 条（每数据集 60），实现正确性先跑 60 条 pilot。代码：新增 configs/experiments/E-012/analysis/ 下的细删 keep-set config 与 tools/run/analysis/e012/ 对应 launcher，以及细删收集模块；head 列表不另写，只引用已冻结的 experiments/E-012/inputs/old_new_union10_heads_v1.json（sha256 19153e28f4cd4cfdd2c806dfd0de5f48b00c58b7f8860fa0b7b62a653f2a80b9，key=candidate_heads，group=old_e009_fixed5 / new_r006_query5）。teacher-forced 侧按 bbox 坐标行定位，复用 head_circuit.py 的 rows×query_span 口径与 collator 的字符区间到 token 区间对齐。自由生成侧的行选择用前缀规则：助手答案格式由本仓库 format_box 生成（[x1,y1,x2,y2]，紧凑无空格，助手轮不含其它文字），从助手输出的第一个 [ 到配对的 ] 之间的每一行都算坐标行并施加细删，] 之后停止；已定【放宽口径】：逗号等分隔 token 所在行同样计入（比严格只算数字字符略宽，需在结果中报告多计入的行数）；格式跑偏（无 [、多组括号、数字段不足四个）时停止干预并记 invalid，另报实际干预行数为 0 的样本比例；只认助手输出第一组括号，避免复述参考框被误算。生成协议沿用同类消融：greedy，max_new_tokens=128，vision_max_patch_tokens=1024，eager。模型沿用同一条 union10 消融的 checkpoint（E-009 step741）。环境与命令：conda:IPLoc，bash tools/run/analysis/e012/<launcher>.sh，先 --inspect 再执行。",
  "metric_plan": "主指标：自由生成 bbox 的 mIoU 变化（invalid 框记 0 并单独报 invalid 率）；确定性辅助轴：teacher-forced argmax 框的 IoU 变化；机制诊断：teacher-forced 坐标 token 平均 CE 变化。汇总：逐样本配对差、样本等权均值、按 sequence/共享图像 component 聚类的 bootstrap 95% CI、正负方向比例。",
  "data_scale": "主样本集 150 条（LaSOT/GOT10k/TAO 各 50），取自 R-001 冻结索引并沿用同一退化样本排除项；按配置先跑同参数 pilot 验证实现，再扩到 150 条。删除规模按每层等量移除 2/3/6 个 head（合计 72/108/216，即 6.25%/9.375%/18.75%），另加只留保留集合的极端档（并集则移除 1142 个 head，单组移除 1147 个）。随机对照每个规模 3 个 seed（20260912/13/14），bootstrap seed 20260914、1000 次。条件总数 49：baseline 1 + keep_only 3 + 同层同数量随机保留集合 9 + protected 27 + random 9；150×49≈7350 次生成。若 GPU 预算不足，只允许在开跑前下调随机 seed 组数，不得下调删除档位，也不得看结果后调整。",
  "variables_controls": "保留名单（旧固定组 / 双角色筛查组 / 并集）× 删除规模（只留保留集合 / 5% / 10% / 20%）× 是否优先保住保留集合；对照为同层、同数量随机保留集合 3 组；全部条件共用细删口径",
  "integrity_gates": "基线空 hook parity；细删只在 bbox 坐标预测行 × query 图像视觉键上生效，逐条审计实际干预的行数、边数与移除的注意力质量（生成阶段必须能证明确实干预了该干预的行，否则细删会静默退化为没删或全删）；单独报告格式跑偏样本比例与实际干预行数为 0 的样本比例；三份保留名单与并集规模一致性校验；保留集合与随机对照的层分布对齐；生成轴与 teacher-forced 轴同时落盘。",
  "acceptance_criteria": "判定规则（事先冻结）：以配对样本 ΔmIoU 的 cluster-bootstrap 95% CI 为准。「守住」= CI 下界 > −0.01（即下降不超过 1 个 mIoU 点）；「崩」= CI 上界 < −0.01；介于两者之间记为未决。某档位要算支持「保留集合足够承载定位」，必须同时满足：该档位保留集合守住，且同档位随机对照不满足守住条件。全部档位都守不住，或保留集合与随机对照无差异，都记为不支持。",
  "conclusion_scope": "（中途读数，非冻结判定）在 E-009 step741、细删口径下，剔除约 99% 的 head 时，筛选出的保留集合（尤其双角色筛查组与并集）保留的定位性能显著高于同规模随机保留集合，且双角色筛查优于旧的注意力几何筛选；不构成「性能无损」，不构成整头必要性，也不构成跨 checkpoint/跨协议泛化。TAO 与 GOT10k 剩余样本未跑。",
  "claim_boundary": "最多支持「在固定模型、固定样本、细删干预下，该保留集合的 bbox 读出通路足以维持定位性能」；不构成整头必要性，不构成「这些是决定定位性能的核心 head」，也不构成跨 checkpoint 或跨协议泛化。"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
