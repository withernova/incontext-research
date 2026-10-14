# R-006 Query 五头整头 attention 置零消融（E-009 step741 baseline）

日期：2026-09-15。新实验诊断；未修改审批、Claim、Run 授权或其它治理状态。

## 设置

| 项 | 值 |
|---|---|
| 被消融模型 | `E-009/.../checkpoints/samples_00047403_step_000741`（与 `baseline-eval-741-new-ft` 同一 checkpoint；adapter sha256 `68eb3fab…e711`） |
| head 集合 | R-006 `attempt-001/frozen_heads.json` → `E_null_calibrated` Top-5：`L24H13, L23H30, L26H20, L21H11, L23H13`（文件 sha256 `0a87d700…8bf2`） |
| 干预 | `WholeHeadZeroHook`：所选文本 query head 的全部 rows×keys 的 post-softmax attention 置零，**不重归一化**，A@V 精确为零；其它 head 输出不变 |
| 条件 | baseline、五头联合、逐头单消融、3 组同层同数量随机头（seed 20260912/13/14） |
| 样本 | R-001 冻结索引中的 60 条：LaSOT 20 / GOT10k 20 / TAO 20（与 E-012 先前整头消融同一批） |
| 生成 | greedy，max_new_tokens=128，`vision_max_patch_tokens=1024`，eager attention |
| 产物 | 远程 `experiments/E-012/r006-query5-whole-head-ablation-step741-v1/`；`records.json` sha256 `6b265321…3df3`，`summary.json` sha256 `0fd30062…c255` |
| 实现 commit | `iploc-szy` `7d75820`（新增 `frozen_head_set` / `checkpoint_override` 与本次配置、launcher；`code_change_review` review_id `a5ab8f5513b635b2` passed） |
| 完整性 | 600/600 条空 hook teacher-forced parity 通过；无截断、无 invalid output |

## 结果（60 条，配对差 = 干预 − baseline）

| 条件 | mIoU | 配对 ΔIoU 均值 | 95% CI | 逐样本变好比例 | teacher-forced bbox CE Δ |
|---|---:|---:|---|---:|---:|
| baseline | 0.6678 | 0 | — | — | 0 |
| **五头联合** | **0.6268** | **−0.0409** | [−0.0969, +0.0221] | 22% | **+0.119** |
| L24H13 | 0.6582 | −0.0096 | [−0.0378, +0.0307] | 30% | +0.056 |
| L23H30 | 0.6969 | +0.0292 | [−0.0235, +0.0896] | 37% | +0.013 |
| L26H20 | 0.6684 | +0.0007 | [−0.0258, +0.0402] | 33% | +0.038 |
| L21H11 | 0.6996 | +0.0318 | [−0.0072, +0.0835] | 47% | +0.002 |
| L23H13 | 0.6864 | +0.0186 | [−0.0125, +0.0615] | 42% | −0.009 |
| random 20260912 | 0.6399 | −0.0278 | [−0.0603, −0.0002] | 37% | +0.074 |
| random 20260913 | 0.6704 | +0.0026 | [−0.0200, +0.0374] | 38% | +0.069 |
| random 20260914 | 0.6649 | −0.0028 | [−0.0281, +0.0350] | 22% | +0.080 |

**五头联合 − 三组随机头均值：ΔIoU = −0.0316，95% CI [−0.0761, +0.0185]，60 条中 63% 为负。**

分数据集（五头联合）：GOT10k 0.8001→0.7398（ΔIoU −0.0603，CI [−0.0999, −0.0218]；该数据集随机对照也在 −0.010 ~ −0.016）；LaSOT 0.5671→0.5556（−0.0115，CI 跨 0）；TAO 0.6362→0.5852（−0.0510，CI 跨 0）。

## 判断

1. **不是灾难性损失。** 五头 attention 全部置零后自然生成 mIoU 从 0.6678 降到 0.6268（相对 −6.1%），无 invalid output、无截断；相对降幅与同层随机 5 头对照同量级（联合 − 随机均值 CI 跨 0）。
2. **五个头各自都不是必要的。** 逐头单独置零的配对 ΔIoU 都在 ±0.04 内且多数为正（L23H30 +0.029、L21H11 +0.032、L23H13 +0.019），说明单个头可被其余 head 补偿；只有联合移除才出现一致的正向损害。
3. **损害有信号但样本量不足。** n=60 的配对 CI 较宽；GOT10k 子集上联合屏蔽的下降（−6.0 pp）明显超过该数据集随机对照，是最支持的证据；TAO 方向一致但区间跨 0，LaSOT 几乎无变化。
4. teacher-forced bbox CE 对联合干预的敏感度（+0.119 nats）高于任何随机对照（+0.069 ~ +0.080），与 IoU 结论方向一致；但逐头 CE 变化（−0.009 ~ +0.056）与逐头 IoU 变化并不一一对应。

## 边界

- 这是**整头**置零，不是"只清零 bbox 生成行→Reference keys"或"→Query keys"的路径级消融；后者的问题不同，需要按边构造干预。
- 在 step741 上执行，而 head 是在 step247 上按 e012 局部敏感度+目标偏好筛出；跨 checkpoint 的结论只适用于该固定模型。
- 60 条先导、`vision_max_patch_tokens=1024` 的 mIoU（0.668）低于官方评估协议（0.709），因此绝对值不能与 `baseline-eval-741-new-ft` 的 0.709 直接并列；配对差在本协议内有效。
- 未做多重比较校正；未在派生 step494 或 step247 上重复。
