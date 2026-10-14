# reference-gradient-gated-spatial-frequency-r001-v1 · reference 图像：梯度候选与空间频率选头

- workflow: v2 / code_planning / 代码方案
- review_status: draft
- group_id: 未分组
- execution_dispatch:  / 

## 1. 研究设计
### 研究问题
在 bbox 预测行到 reference 图像 token 的边上，梯度敏感度结合空间集中和跨样本频率后会选择哪些 head，并与 query-image 选择有何差异？
### 本轮目的
在同一冻结样本上，为 bbox 预测行到 reference 图像 token 的 attention 边选择稳定 head，并与 query-image 选择结果比较视觉角色差异。
### 假设或比较预期
若 reference 与 query 视觉角色由不同 head 支持，reference Top-10 与 query Top-10 将仅部分重合并向更早层偏移。
### 数据与主要变量
复用 R-001-bbox-gradient-halffull 固定的690个三数据集 eval 索引、checkpoint和manifest；所有样本均有有效 reference GT。

固定 gradient_top_m=50、每样本 spatial_top_m=10、visual_mass_quantile=0.5、fIoU 权重=2、总体 top_k=10；reference visual span 和 reference GT 是唯一视觉角色变化。

## 2. 指标设计
将总体与分数据集 head 入选频率作为未注册的探索性结果；与 query-image Top-10 的集合重合仅作诊断。
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
入口为 iploc_szy.head_screening.reference_gradient_gated_spatial_frequency；复用 bbox_gradient、head_circuit、metrics 和 R-001 provenance 解析。
- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy/tools/run/e012_reference_gradient_gated_spatial_frequency.sh`
- commit: `0a01c54bddd1e54094c941d963f8a42165d1213f`
- workspace: 02
- tmux: incontext-E-012-reference-gradient-gated-spatial-frequency-r001-v1
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/logs/reference-gradient-gated-spatial-frequency-r001-v1.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/reference-gradient-gated-spatial-frequency-r001-v1
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
Top-10：L21H10、L21H18、L17H04、L18H05、L20H15、L17H07、L20H18、L17H24、L17H27、L18H15；前两名频率为422/690和409/690。与 query-image Top-10 仅重合 L21H10、L21H18，Jaccard=2/18=0.111；reference 排名更多集中在L17–L21，query 排名主要为L20–L23。reference 集合还包含旧 E-009 fixed-5 中的 L21H10、L17H04、L17H07、L18H15。

## 简短局限
仍是同一冻结样本上的选择统计，没有独立留出或因果消融；reference/query Top-10 的差异不能自动归因于 head 的语义功能。

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "query-image 空间选头与旧 E-009 固定 head 的重合有限；需要独立检验 reference 图像注意力是否对应另一批稳定 head。",
  "implementation_summary": "每个样本重新计算 reference-image 边的 |A·dL/dA|，取 Top-50 后按 reference GT 的视觉质量门控、空间熵、累计50% attention质量连通域 IoU 和样本频率选 Top-10。",
  "implementation_details": "teacher-forced bbox prediction rows；post-softmax eager attention；梯度与 reference attention map 在同次前向/反向中采集，不复用 query-image 逐样本梯度产物，不改写模型输出。",
  "model_config": "Qwen3-VL-8B-Instruct BF16底座加 E-011 step1973 LoRA；eager attention、focus 协议、坐标0–1000。",
  "metric_definition": "主输出为每个 head 的入选次数与频率。空间质量定义与 query run 一致，但 attention key span 与 GT 均替换为 reference image。",
  "integrity_gates": "R-001 frozen_input、summary 和 manifest 哈希匹配；690条 reference GT 在运行前均验证为正面积；每层真实 attention map 与梯度齐全；reference token span 与 merged grid 一致。",
  "expected_outcome": "得到可与 query-image Top-10 对照的 reference stable head 集合，检验两类视觉角色是否分离。",
  "acceptance_criteria": "690条全部完成，summary 与 records 均为 completed，overall 与三个数据集频率图存在。",
  "conclusion_scope": "在固定 step1973、690条样本与指定评分规则下，reference-image 空间频率选择得到上述 Top-10，并与 query 选择存在低重合；不能据此推出视觉角色的因果分工。",
  "claim_boundary": "仅登记固定输入和评分规则下的 reference-image 选头频率；不修改 Claim，不证明 reference 路由因果性、生成性能或普遍泛化。",
  "artifacts": "summary.json、records.json、resolved_plan.json 和四张频率图位于远端 output_dir；summary sha256=b835bf0a05d49c88d7766381baa848d2bcf5120cb71f171d78919391e7a2a2bf。",
  "audit_paths": "远端 /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/reference-gradient-gated-spatial-frequency-r001-v1/{resolved_plan.json,summary.json,records.json,frequency_all.png,frequency_LaSOT.png,frequency_GOT10k.png,frequency_TAO.png}；summary sha256=b835bf0a05d49c88d7766381baa848d2bcf5120cb71f171d78919391e7a2a2bf"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
