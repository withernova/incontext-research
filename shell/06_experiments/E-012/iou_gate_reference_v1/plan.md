# E-012：reference 连通域 IoU 硬门槛试验

- 产物 ID：`reference-gradient-spatial-iou050-r001-v1`
- 用户要求：在 reference 选头中增加 IoU 约束；启动前改为 **IoU ≥ 0.5**。
- 来源：`reference-gradient-gated-spatial-frequency-r001-v1`；summary SHA-256 `b835bf0a05d49c88d7766381baa848d2bcf5120cb71f171d78919391e7a2a2bf`；records SHA-256 `5396b7692789ad69a25a7e327e977629509bae0c1fefaa5466b64040f1b70e65`。
- 模型与数据：同 R-001 的 step1973 LoRA、690 个固定样本（LaSOT 300 / GOT10k 90 / TAO 300）、同一 manifest 与 focus 协议。此轮无需训练或重新反传梯度。

## 固定规则

1. 逐样本直接复用原 reference run 的梯度 Top-50 与分数；重新采集 bbox 预测行到 reference 图像 token 的平均 attention map。
2. 按 attention 从高到低取累计质量达到 50% 的最小支持集，按真实合并后 token 网格计算四邻接连通域。
3. 仅根据 attention 质量选最大分量，同质量按空间索引定序；禁止根据与 GT 的重合程度选择分量。
4. 复用 GT 分数 token 占据率。设 C 为选定分量、g_j 为 GT 对 token 的占据率，I=sum_{j∈C} g_j，IoU=I/(|C|+sum_j g_j-I)。要求 IoU ≥ 0.5。
5. 保留原候选视觉 attention 总质量中位数门槛；达标后按 IoU 降序、梯度绝对贡献降序、熵升序定序，每样本最多10个。允许少选或零入选。
6. frequency 分母为全部有效 reference 样本；零入选样本保留。按入选次数选总体 Top-10，同频率按层和 head 编号定序。

## 对照、输出与检查

- 在同次前向的候选图上复算旧规则（峰值分量、1−熵+2×IoU、选满10个），排除重新采集数值变化造成的比较偏差。
- 保存所有候选平均 attention map、GT token 占据率、逐样本选择与诊断指标，便于离线复核。
- 输出总体/分数据集36×32频率图、各样本入选数量分布、旧/新集合比较与固定样本可视化。
- 聚焦测试：最大质量分量不能由 GT 决定；左上角高质量小分量不能被大面积低质量分量掩盖；GT 分数 IoU；阈值边界；零入选；IoU优先排序；无效输入。
- 首样本捕获前后 bbox logits 一致，原梯度候选与样本身份匹配，所有入选条目满足 IoU≥0.5，计数与频率矩阵完全一致。

## 结论边界

本轮改变了连通域规则、IoU门槛、排序与不补满策略，比较只能归于整套规则变化。通过门槛后的 IoU 上升是筛选规则的直接结果，不证明独立定位改善。此轮复用发现集，未做独立留出或因果消融，也不修改审批、Claim、Solid 或执行授权状态。
