# R-003-zero-query-attention-head-path-patching · 直接抹除 query attention 的两阶段 head 路径测试

- workflow: v2 / awaiting_review / 等待审核
- review_status: pending_review
- group_id: 未分组
- execution_dispatch:  / 

## 1. 研究设计
### 研究问题
直接移除候选上游 head 从 bbox 预测行到 query 视觉 token 的 attention 后，损失是否通过另一批下游 head 的 A@V 输出传播？
### 本轮目的
把 R-002 的保质量空间翻转改为更直接的必要性消融：将指定 query-visual attention edges 置零且不重归一化，再比较候选下游 clean rescue、corrupt transfer 与同层低分控制。
### 假设或比较预期
若候选上游 query-visual edges 是路径必要输入，置零后 bbox CE 应明显上升并强于同层控制；候选下游 clean A@V patch 应部分救回，corrupt A@V 应向 clean run 迁移损害。
### 数据与主要变量
复用 R-001-bbox-gradient-halffull/frozen_input.json 的固定690索引和同一三数据集manifest；按config顶部screening_counts从每个数据集的冻结索引依次选择，不重采样帧。

保持R-002两条路径和candidate/control head集合不变，仅将corruption_mode从horizontal_flip改为zero_query_attention。只把上游head的bbox p−1 rows×query visual keys置零；不重归一化，其他keys与heads不变。

## 2. 指标设计
沿用 R-002 的 upstream_damage、candidate/control rescue_effect、positive-damage aggregate rescue ratio、candidate/control transfer_effect 与 downstream_relative_change；新增 removed_query_attention_mass、remaining_query_mass（应为0）和 full-row sum drop。
### bbox梯度绝对贡献（逐head样本均值） (`bbox_grad_abs_contrib_mean`)
- 公式：C_lh = mean_n sum_{p,j in query} |A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]|
- 含义：teacher-forced bbox token平均CE对指定query->query视觉注意力边的局部敏感度绝对量；只表示当前输入下的敏感度大小，不是因果必要性，也不是增强方向证据
- 汇总与范围：每条边先取绝对值，再按样本求和，最后样本等权平均；不除以视觉token数 / Qwen3-VL-8B+LoRA、36层x32 query heads=1152 heads；20条先导与690条扩展两轮eval子集

### bbox梯度signed贡献（逐head样本均值） (`bbox_grad_signed_contrib_mean`)
- 公式：S_lh = mean_n sum_{p,j in query} A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]
- 含义：对post-softmax指定边做不重归一化乘法缩放时的一阶CE导数方向；本轮有限差分与反传符号不一致，方向暂不可用于增强/抑制决策
- 汇总与范围：样本等权平均 / 同上1152 heads；20条与690条两轮eval子集

### 平均bbox token CE (`bbox_token_ce_mean`)
- 公式：mean_n mean_i CE(logits[p_i-1], token[p_i])
- 含义：teacher-forced query bbox片段（含标点）平均交叉熵，仅表示损失量级，不是IoU或定位准确率
- 汇总与范围：样本等权平均 / 690条（LaSOT 300/GOT10k 90/TAO 300）与20条先导

### 头部排名集合Jaccard (`head_ranking_jaccard`)
- 公式：|A∩B|/|A∪B|
- 含义：不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升
- 汇总与范围：对固定Top-k集合直接计算 / 20条vs690条、690条对旧固定5 head；Top-5/Top-10/Top-50

### 有限差分与反传符号一致 (`finite_difference_sign_agreement`)
- 公式：sign(central_difference) == sign(signed_derivative)
- 含义：首样本指定边±epsilon缩放的中央差分是否与反传signed导数同号；本轮为false，说明梯度方向链路校验未通过
- 汇总与范围：首样本单一诊断，不参与排名 / 690条run首样本dataset_index=0 L24H25，epsilon=0.02

## 3. 代码架构
泛化现有head_circuit.CircuitHook支持显式corruption_mode，默认仍为horizontal_flip以保持R-002行为；新增独立e012_head_circuit_zero_attention.py config和launcher，扩展test验证zero block、移除质量及clean A@V恢复。
- 公共包：`mechanism/iploc-szy/iploc_szy/head_screening`
- 入口：`iploc_szy.head_screening.head_circuit:main`
- 配置：`mechanism/iploc-szy/configs/head_screening/e012_head_circuit_zero_attention.py`
- Shell launcher：`mechanism/iploc-szy/tools/run/e012_head_circuit_zero_attention.sh`
- 复用模块：iploc_szy/head_screening/head_circuit.py, iploc_szy/head_screening/bbox_gradient.py, iploc_szy/head_screening/probes.py
- 新增模块：（待登记）
- 测试：tests/test_head_circuit.py

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy/tools/run/e012_head_circuit_zero_attention.sh`
- commit: `7e11b2f3ba10247ff5b36027c2f4622732b1e12b`
- workspace: 02
- tmux: incontext-E-012-R-003-zero-query-attention-head-path-patching
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/logs/R-003-zero-query-attention-head-path-patching.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-003-zero-query-attention-head-path-patching
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
zero改变attention总质量和A@V幅值，可能是强分布外消融；60条仍来自A/B discovery集合；组级patch不能定位单个head；负结果不能排除MLP/residual或其它token rows。

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "R-002 的空间翻转对 P2 给出方向性中介信号，但它只破坏空间排列；需要直接移除信息通路，判断结果是否依赖这些 attention edges 的存在。",
  "implementation_summary": "用独立config管理样本配额和zero干预；复用R-002的path patching、数据、checkpoint和输出格式，不复制主执行模块。",
  "implementation_details": "zero模式在post-softmax attention、A@V之前把指定切片置零；重新计算A@V。每样本执行clean、candidate-U zero、control-U zero、candidate/control D rescue与transfer；identity gate不变。",
  "model_config": "Qwen3-VL-8B-Instruct BF16底座 + E-011 step1973 LoRA；eager attention，device_map=auto，focus协议，坐标0–1000，vision patch cap1024。",
  "metric_definition": "CE为teacher-forced bbox-token平均CE。zero不重归一化，因此removed mass本身是干预强度；结果必须同时报告candidate/control removed mass，不能只比较raw damage。rescue fraction仅在damage>1e-4时定义，主看effect与正damage样本总量比。",
  "integrity_gates": "两图/span/grid/层序/hook firing完整；zero后目标query block最大绝对值为0，full-row sum下降量与removed query mass在2e-5内一致；native/capture/identity logits在0.002容差内；样本计数严格等于config配额，失败不写completed summary。",
  "expected_outcome": "判断R-002方向性路径信号在更强的attention必要性消融下是否复现；不预设zero一定恶化，因为移除某些边也可能降低CE。",
  "acceptance_criteria": "默认60条完整输出；candidate/control均记录removed mass与damage；identity和zero完整性gate通过。若候选damage/rescue/transfer不优于按removed mass可比的control，则不支持该固定路径。",
  "claim_boundary": "只评价固定checkpoint、固定两组路径、bbox p−1 rows和不重归一化zero干预下的局部必要性与head-output中介；不证明完整生成电路或泛化提升。",
  "audit_paths": "remote commit 7e11b2f3ba10247ff5b36027c2f4622732b1e12b；review 74493a21b7f2aa9d；configs/head_screening/e012_head_circuit_zero_attention.py；tests/test_head_circuit.py"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
