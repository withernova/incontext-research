# E-012：E-009 2 个阶段选头稳定性（query）

初步观察：在同一批 686 条有效 query 样本上，step 83 与 step 1153 的全局 Top-10 保留 9 个 head（Jaccard=0.8182）；L20H17 退出、L19H03 进入。Top-5 / Top-50 Jaccard 分别为 0.6667 / 0.8519，说明全局高频集合在这两个阶段较稳定。逐样本 Top-10 平均 Jaccard 只有 0.4257，因此这种稳定性不能扩展为每张样本都使用相同 head。分数据集 Top-10 Jaccard 为 LaSOT=0.8182、GOT10k=0.8182、TAO=0.6667。

bbox token CE 从 0.882647 上升至 1.084499；这是 teacher-forced 损失，不能直接解释为定位 IoU 下降。reference 尚未纳入此初步报告，后续仍需检验两个视觉角色各自的跨阶段稳定性。

四个 checkpoint 完整复制并逐文件验证 SHA-256；复用现有入口，对每个 checkpoint 重新计算梯度。

| step | 角色 | 样本数 | bbox CE | Top-10 |
|---:|---|---:|---:|---|
| 83 | query | 686 | 0.882647 | L23H30, L23H13, L21H10, L20H15, L21H08, L21H11, L17H04, L18H15, L20H17, L22H04 |
| 1153 | query | 686 | 1.084499 | L23H30, L21H10, L23H13, L21H11, L21H08, L20H15, L22H04, L17H04, L19H03, L18H15 |

| 阶段比较 | query Top-10 Jaccard |
|---|---:|
| 83 → 1153 | 0.8182 |

query Top-10 并集的入选次数：

| head | 83 | 1153 |
|---|---:|---:|
| L17H04 | 331 | 281 |
| L18H15 | 330 | 268 |
| L19H03 | 219 | 274 |
| L20H15 | 366 | 344 |
| L20H17 | 325 | 239 |
| L21H08 | 347 | 401 |
| L21H10 | 426 | 468 |
| L21H11 | 341 | 407 |
| L22H04 | 251 | 316 |
| L23H13 | 484 | 462 |
| L23H30 | 485 | 498 |

检查：本报告纳入的 2 组均全部完成；query 每组 686 条（LaSOT 296 / GOT10k 90 / TAO 300），reference 完整分析的目标为每组 690 条（300 / 90 / 300）。样本身份、排除规则、checkpoint 哈希、36×32 频率矩阵与逐样本记录一致，首样本前向一致性检查通过。

固定参数：逐样本梯度 Top-50、空间 Top-10、视觉 mass 中位数门控、熵与 2×fIoU、累计 mass=0.5、全局 Top-10；seed=20260910；BF16 底座、eager attention。

结论边界：固定样本与算法下的跨 checkpoint 选头稳定性；不是因果、定位精度或独立留出泛化证据。引用 run 使用另一条 E-011 训练轨迹，不属于本次 E-009 阶段序列。

显式参考：gradient-gated-spatial-frequency-r001-v2；reference-gradient-gated-spatial-frequency-r001-v1。没有使用额外 Solid run（任务提供的列表为空）。

更完整的 Top-5/10/50、逐样本 Jaccard 和分数据集比较见 preliminary_83_1153_query_comparison.json。
