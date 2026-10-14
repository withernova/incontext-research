# gradient-gated-spatial-frequency-r001-v2 · query 图像：梯度候选与空间频率选头

- workflow: v2 / code_planning / 代码方案
- review_status: draft
- group_id: 未分组
- execution_dispatch:  / 

## 1. 研究设计
### 研究问题
在 bbox 预测行到 query 图像 token 的边上，梯度敏感度结合空间集中和跨样本频率后会选择哪些 head？
### 本轮目的
在 R-001 的冻结样本上，为 bbox 预测行到 query 图像 token 的 attention 边重新选择稳定的定位 head。比较梯度敏感度筛选与空间质量和跨样本频率筛选后的排序差异。
### 假设或比较预期
若高梯度 head 还稳定关注 query GT 区域，空间频率筛选将保留其中一部分并引入更稳定的空间 head。
### 数据与主要变量
复用 R-001-bbox-gradient-halffull 固定的 690 个三数据集 eval 索引和同一 checkpoint/manifest；4条 LaSOT 全零 query GT 不可计算空间 IoU，按预先声明规则排除，实际分析686条。

固定 gradient_top_m=50、每样本 spatial_top_m=10、visual_mass_quantile=0.5、fIoU 权重=2、总体 top_k=10；不进行模型干预或生成评测。

## 2. 指标设计
将总体与分数据集 head 入选频率作为未注册的探索性结果；与 R-001 纯梯度 Top-10 的集合重合仅作诊断。
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
入口为 iploc_szy.head_screening.gradient_gated_spatial_frequency；复用 bbox_gradient、head_circuit、metrics 和 R-001 provenance 解析。
- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy/tools/run/e012_gradient_gated_spatial_frequency.sh`
- commit: `0a01c54bddd1e54094c941d963f8a42165d1213f`
- workspace: 02
- tmux: incontext-E-012-gradient-gated-spatial-frequency-r001-v2
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/logs/gradient-gated-spatial-frequency-r001-v2.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/gradient-gated-spatial-frequency-r001-v2
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
Top-10：L23H13、L23H30、L21H08、L21H11、L22H04、L20H17、L20H16、L21H18、L20H08、L21H10；前两名频率为506/686和468/686。相对 R-001 原梯度 Top-10 重合 L21H11、L23H13、L23H30，Jaccard=3/17=0.176；说明加入 query 空间质量和跨样本频率后排序显著变化，但仍属于同一冻结样本上的选择诊断。

## 简短局限
选择和统计共用同一冻结样本，不能给出留出泛化或因果必要性结论；4条全零 query GT 被排除。

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "R-001 的梯度绝对贡献只反映局部敏感度，无法区分注意力是否集中在 query GT 区域，也没有跨样本空间稳定性筛选。",
  "implementation_summary": "逐样本取 query 边梯度 Top-50，再以视觉质量门控、归一化空间熵、累计 50% attention 质量连通域与 query GT 的分数 token IoU 排序；每样本保留10个 head，按频率取总体 Top-10。",
  "implementation_details": "teacher-forced bbox prediction rows；post-softmax eager attention，仅采集不改写输出；视觉质量分数=1-归一化熵+2×support50 fIoU；视觉质量门槛为候选 visual mass 中位数。",
  "model_config": "Qwen3-VL-8B-Instruct BF16底座加 E-011 step1973 LoRA；eager attention、focus 协议、坐标0–1000。",
  "metric_definition": "主输出为每个 head 入选每样本 Top-10 的次数与频率。空间质量使用归一化熵和累计 attention 质量50%支持集中包含全局峰值的四邻接连通分量，与 GT token 分数占据率的 IoU。",
  "integrity_gates": "R-001 frozen_input、summary、manifest 与 probe records 哈希匹配；每层均捕获真实 attention；query token span 与 merged grid 一致；无效 GT 在运行前枚举并写入摘要。",
  "expected_outcome": "形成与纯梯度 Top-10 可直接比较的 query 空间稳定 head 集合，不预设其具有更强因果效应。",
  "acceptance_criteria": "686条全部完成，summary 与 records 均为 completed，overall 与三个数据集频率图存在。",
  "conclusion_scope": "在固定 step1973、686条有效样本与指定评分规则下，query-image 空间频率选择得到上述稳定 Top-10；不能据此推出因果定位作用。",
  "claim_boundary": "仅登记固定输入和评分规则下的 query-image 选头频率；不修改 Claim，不证明定位因果性、生成性能或普遍泛化。",
  "artifacts": "summary.json、records.json、resolved_plan.json 和四张频率图位于远端 output_dir；summary sha256=cc76ff624e85382ee300f75082ff6c0f0fa894ea7697ecc3b743d92008b9e99a。",
  "audit_paths": "远端 /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/gradient-gated-spatial-frequency-r001-v2/{resolved_plan.json,summary.json,records.json,frequency_all.png,frequency_LaSOT.png,frequency_GOT10k.png,frequency_TAO.png}；summary sha256=cc76ff624e85382ee300f75082ff6c0f0fa894ea7697ecc3b743d92008b9e99a"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
