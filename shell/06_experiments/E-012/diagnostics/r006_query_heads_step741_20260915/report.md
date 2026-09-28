# R-006 选头与 step741 正误分组复核

日期：2026-09-15。讨论与离线重统计；未启动模型 forward、训练或消融，未修改审批、Claim、Run 授权和治理状态。

## 结论

1. 远程 `R-006-redetermine-reference-heads/attempt-001` 实际按 **Query** 区域选头，名称和本地方案页不能代表实际执行配置。派生训练采用它的 `E_null_calibrated` 五头。
2. **当前证据不能判断屏蔽这些头是否造成灾难性性能损失。** 指定产物里没有这组头对应的屏蔽生成评估。
3. 将现存 baseline step741 的118条归档 attention 逐样本指标，与指定分支的自然预测重新对齐后，**没有得到正确组在 reference GT 上一致、稳定更集中的证据**。这只是可用 confirmation 子集的 GT teacher-forced attention；1766条全量、自然生成阶段 attention 的问题尚未完成。

## 1. 实际如何选 headset

### Query 五头

读取远程 R-006 的 `input_manifest.json`、`integrity.json`、运行配置快照、`summary.json`、`frozen_heads.json`，并对照实际筛选模块。配置与 integrity 均为 `target_role=query`；代码部分历史字段仍名为 `reference_abs_contribution`，此 run 实际求和的 keys 是 Query span。

- 模型：Qwen3-VL-8B 加载 step247 checkpoint；筛选配置为 BF16、eager。
- 样本：590条，LaSOT 300 / GOT10k 90 / TAO 200；Discovery 354、Calibration 118、Confirmation 118。归档审计报告跨 split component overlap=0、与训练集 sequence/image overlap=0。
- 扫描全部36×32=1152头，使用 teacher-forced bbox **坐标 token** 的预测行 `p-1`；不是按正误组分别选头。
- 每个样本、每个头计算 Query 视觉边的敏感度绝对总量：

  `C_h = Σ_(bbox coordinate rows p-1, Query keys j) |A_h[r,j] · ∂L_coord/∂A_h[r,j]|`。

- 分别用 attention 权重和绝对贡献权重计算目标偏好 `T_A`、`T_D`：先在 Query span 内归一化，得到 GT fractional occupancy 加权的质量 `m`；再计算 `T=clip((m−mean(g))/(max(g)−mean(g)),0,1)`。这里 `g` 是每个视觉 token 被 GT 覆盖的比例。
- Calibration 冻结阈值：`τ_C=0.01035146`（贡献的90%分位）、`τ_A=0.11241769`、`τ_D=0.13150728`。后两项来自三种 null 区域的 pooled 95%分位：`same_size_shifted`、`radial_matched`、`fixed_center`；不是这五个头的预测准确率门槛。
- 只有在至少50%的 Discovery 样本里同时达到三项阈值且指标有效的头，才进入 `E_null_calibrated` 候选池。
- 对这些候选按 `mean_n[(C_nh/max_h C_nh) · sqrt(T_A,n,h · T_D,n,h)]` 排序，取最多5个。它不是纯梯度 Top-5，也不是旧 `spatial_iou>=0.5` 筛法。
- Confirmation 仅检验冻结集合，没有重新排序；bootstrap 给确认分数区间，不是这次实际选择时另加的入选门槛。

| Head（代码索引） | 排名分数 | Discovery 达标率 | Confirmation 达标率 |
|---|---:|---:|---:|
| L24H13 | 0.31604 | 89.83% | 84.75% |
| L23H30 | 0.18161 | 95.48% | 90.68% |
| L26H20 | 0.16214 | 88.98% | 83.90% |
| L21H11 | 0.15331 | 96.33% | 93.22% |
| L23H13 | 0.13671 | 94.35% | 93.22% |

选择 seed=20260910；null/bootstrap seed=20260914；确认 bootstrap=1000次。已用归档候选达标率和 combined scores 重建 Top-5，与冻结文件一致。

### 派生训练如何使用

`R-006-query-r005-ref3-transfer-step247-3ep-v1/resolved_plan.json` 直接记录：

- Teacher reference heads：**L17H24、L17H27、L21H17**。
- Student query heads：**L24H13、L23H30、L26H20、L21H11、L23H13**，与上表完全相同。
- 蒸馏边：teacher 和 student 都取 **bbox预测行 p-1 → Reference image tokens**。Query head 的名称来自它原先在 Query 图像上的筛选角色，不表示派生训练只监督 Q→Q。
- 从 step247 初始化，重置 optimizer/epoch counters；10522条训练样本，3 epochs，学习率1e-4，attention 蒸馏系数0.1，seed=20260901。终点另记 step494；这不是 baseline 的 step741 checkpoint。
- Query 冻结文件实际 SHA-256 与派生计划记录一致。Teacher三头的来源按派生计划登记为 R-005；本任务未递归读取未点名的 R-005 产物，因此不将其来源筛选独立复核视为已完成。

## 2. 屏蔽是否会灾难性下降

**未知，需要对应的因果消融。** 筛选用的是当前 GT teacher-forced 输入附近的局部敏感度，整块置零是大幅干预；绝对贡献还丢掉了方向。所以上述选头分数不能推出性能降幅。

必须先明确“屏蔽”的边界，以下回答不同问题：

| 操作 | 可以检验什么 |
|---|---|
| 五头完整 attention 输出置零 | 这五头合起来对定位行为的必要程度 |
| 只清零 bbox生成行→Reference keys 的 attention | 这些头使用 Reference 的路径是否必要 |
| 只清零 bbox生成行→Query keys 的 attention | 这些头处理 Query 视觉信息的路径是否必要 |

对于边屏蔽，post-softmax 置零且不重归一化会移除该路径的输出贡献；重归一化还会同时放大剩余边，两者不能混成同一干预。整头屏蔽造成大降幅，也不能独自证明 Reference 检索路径是原因。

若后续执行，应分别在 baseline step741 与派生终点上冻结同样的输入、精度和生成设置，先验证空 hook 的行为一致，再比较原模型、五头联合屏蔽、逐头屏蔽及同层同数量随机头对照。用自然生成的 mIoU、Acc@0.5、parse rate 和逐样本配对变化回答问题；GT teacher-forced CE 只能补充诊断。当前任务没有预设“灾难性”的数值阈值，因此本报告不补造判定门槛。

## 3. 指定 step741 分支重新统计

### 数据与口径

自然预测来自用户指定的 `20260915T071307686259Z--baseline-eval-741-new-ft/evaluation/predictions.jsonl`：1766条唯一索引，正确1365条、错误401条（IoU≥0.5定义正确）；mIoU=0.708972、Acc@0.5=77.2933%，与分支 `metrics.json` 一致。

可复用的 attention 来自派生目录内 `attention_compare_step741_v1/baseline/records.json`，其 checkpoint 路径是 baseline step741，而非 distilled 模型。仅有118条 Confirmation；按 `dataset_index + sample_id + dataset` 匹配118/118，每条对应唯一 sequence/component，其中100正确、18错误。**缺少其余1648条 attention。**

这里重算的是归档逐样本指标的正误分组聚合，未重跑图像 forward，也没有原始 token maps 可重新检查峰值定义。记录标注 `teacher-forced bbox coordinate p-1 rows`，不是该自然预测实际生成时的 attention；图像 token 预算、重放量化等元数据不完整，不能声称和自然评估完全同设置。

5个 head 各自在 Reference span 内归一化后等权组成 ensemble，再按样本等权。GT mass 使用 token 与 GT 的 fractional occupancy；`log GT enrichment=log(conditional GT mass / GT area fraction)`。置信区间在两组内分别抽样10000次，seed=20260915；本子集每个 sequence/component 只有一条，因此此处样本 bootstrap 等价于该层级的 cluster bootstrap。均为未作多重比较校正的描述性区间。

| 指标（ensemble） | 正确 n=100 | 错误 n=18 | 正确−错误的95% CI |
|---|---:|---:|---:|
| Reference 内落入 GT 的 attention 占比 | 13.88% | 11.93% | −5.54～+8.18个百分点 |
| 面积校正的 log GT enrichment | 0.926 | 1.330 | −1.346～+0.504 |
| 归档峰值命中率 | 8.00% | 22.22% | −35.44～+4.44个百分点 |
| 全序列 attention 分给 Reference 的比例 | 0.416% | 1.916% | −2.898～−0.395个百分点 |
| Reference GT 面积占比 | 9.75% | 5.04% | −0.85～+8.86个百分点 |

**解释：** GT mass 的均值有小幅正差，但区间跨0；面积校正与峰值命中也不支持一致的正向差异。更多 Reference attention 本身不等于更准确：此子集中错误组反而有更高的 Reference attention 预算。两组 GT 面积和数据集组成不同，不能把未匹配的组差异当成因果证据。

### 逐 head 与分数据集

| Head | 正确组 GT mass | 错误组 GT mass | 差值95% CI（百分点） |
|---|---:|---:|---:|
| L24H13 | 8.77% | 8.96% | −8.82～+6.58 |
| L23H30 | 12.13% | 13.12% | −10.38～+6.96 |
| L26H20 | 3.41% | 5.85% | −8.29～+1.92 |
| L21H11 | 26.41% | 15.36% | +0.81～+19.65 |
| L23H13 | 18.69% | 16.38% | −6.87～+10.44 |

只有 L21H11 的该描述性区间不跨0；未校正多重比较，而且它仍是面积未匹配的 GT-mass 指标，不能事后称它已获独立机制确认。

- LaSOT：49正确/11错误，GT mass 12.70% / 9.06%，差值区间 −3.19～+9.14个百分点。
- TAO：33正确/7错误，15.87% / 16.45%，区间 −16.35～+12.08个百分点。
- GOT10k：18正确/0错误，无可估计的正误组差异。
- 将错误收紧到IoU<0.1（12条），或将正确收紧到IoU≥0.75（85条），ensemble GT mass 差值区间仍跨0。

## 4. 检查与证据范围

- Canonical 只读复核：当前 E-012 元数据与 envelope 的目标、状态及指标相符。远程实际 R-006 配置与本地 R-006 方案页存在上述角色差异，本报告以远程归档说明实际做法，未回写治理状态。
- 本任务可用 **Solid Run ID：无**。仅使用用户直接点名的 R-006、派生目录和指定 E-009 分支；未将其内容升级为 validated Claim。
- Query冻结文件与派生配置 hash 一致；归档候选与Top-5一致；attention文件与远程 integrity hash 一致；prediction下载前后hash一致；118条全部匹配且无重复；enrichment公式与ensemble线性聚合核查通过。
- 重算脚本完整执行通过；JSON/CSV可读性、计数与文件空白检查通过。当前目录未被 Git 识别为工作树，`git diff --check` / `git status` 不可用，因此未将 Git 检查列为通过项。
- 筛选代码读自当前远程工作树，未假称取得历史运行时的完整代码快照。实际选择与阈值另由归档配置、summary和frozen集合交叉验证。
- 最大未决项：精确到这五头的消融生成评估，以及全1766条、与实际自然生成一致的 Q→R attention 提取。这两个问题不能用当前118条统计代替。

## 产物与复现

- [统计结果](statistics.json)：总体、逐head、各数据集、阈值敏感性、输入hash。
- [逐样本连接表](joined_samples.csv)：118条自然预测IoU与Reference指标。
- [选头证据](selection_evidence.json)：阈值、五头排名/频率、蒸馏配置摘录与来源hash。
- [重算脚本](recompute.py)：只用NumPy和Python标准库；内置输入hash、身份和聚合检查。

原始输入分别为上述派生目录的 `attention_compare_step741_v1/baseline/records.json` 和指定分支的 `evaluation/predictions.jsonl`。当前下载副本位于 `/tmp/e012_r006_review/`。

```bash
python3 shell/06_experiments/E-012/diagnostics/r006_query_heads_step741_20260915/recompute.py \
  --attention /tmp/e012_r006_review/baseline_attention.json \
  --predictions /tmp/e012_r006_review/predictions.jsonl \
  --output shell/06_experiments/E-012/diagnostics/r006_query_heads_step741_20260915
```
