# R-015-query-key-control · 正面对照：删查询图键是否崩塌

- workflow: v2 / code_planning / 代码方案
- review_status: draft
- group_id: 未分组
- execution_dispatch:  / 

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
用同一种细删刀法（全 head、不分组）把「所有行 → query 图像 key」或「bbox 坐标行 → query 图像 key」的注意力清零，定位性能是否显著崩塌？

## 2. 目的
这是机制自检而非新结论：R-013 显示删到 reference 图像 key 只掉 0.12，必须证明同一种删法砍在 query 图像通道上会显著崩塌，否则说明 span 取错或 prefill/解码覆盖不全，R-012/R-013 的结论必须撤回。

## 3. 方法（干预 · 对照 · 指标与判定规则）
干预：对全部 1152 个文本 query head，清零「来源行 → query 图像视觉 token」的注意力边，不重归一化。两组来源行：all（所有行，prefill+解码都干预）、target_rows（bbox 坐标预测行，生成时用括号前缀规则）。样本与 R-013 完全相同（LaSOT 50 + GOT10k 50），因此可与 R-013 逐样本配对，直接比较两个图像通道。指标：自由生成 mIoU 变化为主，teacher-forced argmax 框 IoU 为确定性辅助轴，CE 为机制诊断。判定阈值沿用事先冻结值。

**干预与对照**：来源行组（all / target_rows）× 靶子图像固定为 query 图像；与 R-013（靶子为 reference 图像）构成同一刀法的通道对照

**指标计划**：主指标：自由生成 bbox 的 mIoU 变化；确定性辅助轴：teacher-forced argmax 框 IoU；机制诊断：坐标 token CE；审计：实际干预行数与移除注意力质量（预期 query 图像 key 分到的注意力远高于 reference）。

**判定门槛 / no-silent-zero**：基线空 hook parity；逐条审计实际干预行数/边数/移除注意力质量；与 R-013 使用同一批样本索引与同一 checkpoint，保证可配对。

**验收判定**：预期「崩塌」= 配对 ΔmIoU 的 95% CI 上界 < −0.01（显著下降）。若该对照组同样不下降，则判定干预机制无效，须撤回 R-012/R-013 的解释并排查 span/覆盖问题。

### 已注册指标定义
- **bbox梯度绝对贡献（逐head样本均值）** (`bbox_grad_abs_contrib_mean`)：C_lh = mean_n sum_{p,j in query} |A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]|；teacher-forced bbox token平均CE对指定query->query视觉注意力边的局部敏感度绝对量；只表示当前输入下的敏感度大小，不是因果必要性，也不是增强方向证据；每条边先取绝对值，再按样本求和，最后样本等权平均；不除以视觉token数 / Qwen3-VL-8B+LoRA、36层x32 query heads=1152 heads；20条先导与690条扩展两轮eval子集
- **bbox梯度signed贡献（逐head样本均值）** (`bbox_grad_signed_contrib_mean`)：S_lh = mean_n sum_{p,j in query} A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]；对post-softmax指定边做不重归一化乘法缩放时的一阶CE导数方向；本轮有限差分与反传符号不一致，方向暂不可用于增强/抑制决策；样本等权平均 / 同上1152 heads；20条与690条两轮eval子集
- **平均bbox token CE** (`bbox_token_ce_mean`)：mean_n mean_i CE(logits[p_i-1], token[p_i])；teacher-forced query bbox片段（含标点）平均交叉熵，仅表示损失量级，不是IoU或定位准确率；样本等权平均 / 690条（LaSOT 300/GOT10k 90/TAO 300）与20条先导
- **头部排名集合Jaccard** (`head_ranking_jaccard`)：|A∩B|/|A∪B|；不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升；对固定Top-k集合直接计算 / 20条vs690条、690条对旧固定5 head；Top-5/Top-10/Top-50
- **有限差分与反传符号一致** (`finite_difference_sign_agreement`)：sign(central_difference) == sign(signed_derivative)；首样本指定边±epsilon缩放的中央差分是否与反传signed导数同号；本轮为false，说明梯度方向链路校验未通过；首样本单一诊断，不参与排名 / 690条run首样本dataset_index=0 L24H25，epsilon=0.02

## 4. 详细实现细节
复用已提交的 row_scope 机制（module 无改动）：configs/experiments/E-012/analysis/e012_r015_query_key_control_step741.py + launcher；image_role=query、row_scopes=[all, target_rows]、100 样本、3 条件。模型 E-009 step741。commit 755e2a5cc0f4ba6d5d988a766603d9a424308995。

**数据规模**：100 条（LaSOT 50 + GOT10k 50，与 R-013 同一批索引）；3 条件 × 100 = 300 次生成，约 15–25 分钟。

- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy/tools/run/analysis/e012/e012_r015_query_key_control_step741.sh`
- commit: `755e2a5cc0f4ba6d5d988a766603d9a424308995`
- workspace: 02
- tmux: incontext-E-012-R-015-query-key-control
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-015-query-key-control/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/r015-query-key-control-step741-v1
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
单一 checkpoint 与协议；只删到 query 图像视觉键这一侧；样本 LaSOT+GOT10k。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "necessity": "没有正面对照就无法区分「reference 通道本来就很细」与「我们的干预没打到点上」；这是本轮所有图像通道结论的有效性前提。",
  "implementation_details": "复用已提交的 row_scope 机制（module 无改动）：configs/experiments/E-012/analysis/e012_r015_query_key_control_step741.py + launcher；image_role=query、row_scopes=[all, target_rows]、100 样本、3 条件。模型 E-009 step741。commit 755e2a5cc0f4ba6d5d988a766603d9a424308995。",
  "metric_plan": "主指标：自由生成 bbox 的 mIoU 变化；确定性辅助轴：teacher-forced argmax 框 IoU；机制诊断：坐标 token CE；审计：实际干预行数与移除注意力质量（预期 query 图像 key 分到的注意力远高于 reference）。",
  "data_scale": "100 条（LaSOT 50 + GOT10k 50，与 R-013 同一批索引）；3 条件 × 100 = 300 次生成，约 15–25 分钟。",
  "variables_controls": "来源行组（all / target_rows）× 靶子图像固定为 query 图像；与 R-013（靶子为 reference 图像）构成同一刀法的通道对照",
  "integrity_gates": "基线空 hook parity；逐条审计实际干预行数/边数/移除注意力质量；与 R-013 使用同一批样本索引与同一 checkpoint，保证可配对。",
  "acceptance_criteria": "预期「崩塌」= 配对 ΔmIoU 的 95% CI 上界 < −0.01（显著下降）。若该对照组同样不下降，则判定干预机制无效，须撤回 R-012/R-013 的解释并排查 span/覆盖问题。",
  "claim_boundary": "只作为机制有效性对照；不构成新的科学结论，也不改变 R-013 的结论边界。"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
