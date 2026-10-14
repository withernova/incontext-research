# R-001-bbox-gradient-halffull · bbox 梯度初筛扩展：690 条三数据集 eval 样本（R-001 产物补充登记）

- workflow: v2 / code_planning / 代码方案
- review_status: draft
- group_id: 未分组
- execution_dispatch:  / 

## 1. 研究设计
### 研究问题
给定同一 checkpoint，在训练清单之外的 LaSOT/GOT10k/TAO bbox 预测中，query->query 注意力边的 bbox 梯度贡献如何排名，三个数据集排名是否一致？
### 本轮目的
把 R-001 的 20 条先导扩展为 690 条（LaSOT 300/GOT10k 90/TAO 300）再排名，检查候选 head 是否随样本量/数据集改变；本次只登记已有产物，不发起新计算。
### 假设或比较预期
扩样后仍可得到非零且有区分度的梯度贡献；若头部候选与 20 条先导大致一致，则可为后续独立样本验证提供候选，但不预设泛化提升。
### 数据与主要变量
复用 R-001 的 eval manifest /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-real-focus-data/manifests/test_combined_lasot600_gotval_taoval_1shot_focus.json（SHA256=48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b，1766条），按 seed20260910 分层抽 LaSOT 300/GOT10k 90/TAO 300。依据训练清单 train_only_1shot_focus_valid10522.json（SHA256=bd7037325096cc99097333090ec5d02f64dd9ce2922f04e0e4409d1d635bd6e7）检查 ref/query 视频目录名重叠；冻结审计 selected_train_sequence_overlap=0。

固定 checkpoint、eval manifest、训练清单哈希、配额 300/90/300、seed20260910、focus 协议、patch 上限 1024、bbox 字符串 token 范围；主筛查无干预，首样本仅做 ±0.02 概率边缩放的有限差分方向诊断。

## 2. 指标设计
见 Experiment 指标注册表：bbox_grad_abs_contrib_mean、bbox_grad_signed_contrib_mean、bbox_token_ce_mean、head_ranking_jaccard、finite_difference_sign_agreement；同时输出逐样本 records 与 ranking.csv。
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
复用 R-001 已登记实现：iploc_szy/head_screening/bbox_gradient.py 与 configs/head_screening/e012_bbox_gradient_initial.py；本次只改 screening_counts 与 work_dir，未新增模块，未提交新的代码版本。
- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy/tools/run/e012_bbox_gradient_initial.sh`
- commit: `4411686f9205d55342c4856e79bedb83e80045ef`
- workspace: 02
- tmux: incontext-E-012-R-001-bbox-gradient-halffull
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/logs/R-001-bbox-gradient-initial.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-001-bbox-gradient-halffull
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 5. 关键结果
### bbox_grad_abs_contrib_mean = 0.4672896169989869 (L26H25)
- 比较：L24H13=0.3478776931; L21H31=0.2833985985
- 差值：相对第2名 +0.1194119239
- 不确定性：std_absolute=0.216616；signed>0占比39.4%
- 产物：results/R-001-bbox-gradient-halffull/summary.json
- 解释：三数据集均第1，但只是absolute敏感度，且有限差分失败，不得据此增强该head

### head_ranking_jaccard = 0.666667 (Top-5, 20 vs 690)
- 比较：Top-10=0.818182
- 差值：—
- 不确定性：—
- 产物：results/R-001-bbox-gradient-halffull/comparison.json
- 解释：扩样后头部候选大致一致

### head_ranking_jaccard = 0.0 (旧固定5 head, Top-10)
- 比较：Top-50 交集=3
- 差值：—
- 不确定性：—
- 产物：results/R-001-bbox-gradient-halffull/comparison.json
- 解释：新旧排序明显不同；未做同预算因果对照，不能推出新方法更好

### finite_difference_sign_agreement = false
- 比较：要求为 true
- 差值：relative_error=1.287289
- 不确定性：—
- 产物：results/R-001-bbox-gradient-halffull/comparison.json finite_difference
- 解释：signed方向不可用于干预决策；absolute排名保留为未验证观察

## 6. 结果分析
本轮只登记已有产物，未重跑GPU。absolute贡献排名在扩样后仍稳定地由L26H25/L24H13领先，说明该指标在690条上非退化且有数据集间一致性；但有限差分失败意味着 signed/方向不可用，absolute排名也尚未排除实现与BF16数值问题，不能作为head必要/因果证据。20条是690条子集且样本比例改变（35/35/30→43.5/13.0/43.5），两轮一致性只支持扩样稳定，不构成独立重复。旧固定head取自不同step(1482)、不同选择阶段与评价口径，交集为0只能说明排序不同，缺少同checkpoint/同输入/同预算的因果对照。未做生成IoU/Acc、head干预、随机/旧head对照与留出样本验证。

## 简短局限
eval样本已参与head discovery，不能作为独立泛化验证集；本轮无不同seed、bootstrap CI或留出复验；BF16+LoRA与训练4bit路径不同；各数据集样本量不平衡且未等权；执行时源代码commit不在冻结产物中；有限差分失败原因（BF16/步长/扰动路径/实现）未定位。

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "model_config": "Qwen3-VL-8B-Instruct BF16 底座 + 用户指定 E-011 step1973 LoRA adapter（同 checkpoint 的 adapter_processor）；eager attention，device_map=auto，vision patch cap 1024，focus 协议，坐标尺度 1000。",
  "claim_boundary": "仅登记固定 checkpoint 与未出现在指定训练清单中的 eval 视频上的 query->bbox 边局部敏感度排名与三数据集探索性比较；不推进 Claim、Solid 或执行授权。",
  "artifacts": "远端 /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-001-bbox-gradient-halffull/{summary.json,ranking.csv,frozen_input.json,runtime.json,probe/records.json,probe/sample_*.npz}；本地镜像 shell/06_experiments/E-012/results/R-001-bbox-gradient-halffull/（summary.json sha256=00cf37ec…, ranking.csv=6be84c53…, frozen_input.json=df4771e6…, runtime.json=a7d5ca70…, records.json=34bbeca91e…）",
  "audit_paths": "shell/06_experiments/E-012/result.md；results/R-001-bbox-gradient-halffull/{comparison.json,provenance.json,records.json,summary.json,ranking.csv}；日志 /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/logs/R-001-bbox-gradient-initial.log"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
