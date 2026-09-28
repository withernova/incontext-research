# E-012 新 Run 草案：R-001 Top-10 整头 attention 置零

此文件是可审阅的方案草案，未注册正式 Run、未修改审批或执行授权。正式 Run ID 未分配；不得据文件名推断为 R-004 等编号。可引用 Solid Run：无。R-001 是用户指定的待核实选头来源，当前任务证据白名单为空，未读取其结果或冻结输入。

## 问题与结论边界

暂停本次任务的串联路径分析，直接检验：固定 R-001 的 Top-10 heads 后，联合或逐头抹除其贡献，是否改变模型自由生成的 bbox。该消融是 E-012 的诊断步骤，不改写 canonical objective 或 Claim。

拟按 `bbox_grad_abs_contrib_mean` 选 Top-10，对应现有 ranking schema 中的 `absolute`，以 layer/head 升序打破平分。这一排序口径尚待 R-001 显式参考核实；不使用 signed 梯度方向。head 编号均为零基 query-head 编号，不能当作 KV-head 编号。

大幅退化说明这些 heads 在指定模型、输入和干预下有因果贡献，不证明跨层串联，也不证明对定位具有特异性。影响小不等于 head 无用；随机对照用于判断相对于同层一般 head 移除是否更敏感。选头样本上重测仅是样本内诊断，不能宣称泛化。

## 干预与条件

仅针对 Qwen3-VL 文本 self-attention。在 eager attention 的 softmax/dropout 之后，将指定 query head 的全部 query rows × 全部 key columns 置为 0，不重新归一化；使用原 GQA value 展开重算该 head 的 A@V，再交给原 o_proj。视觉编码器不接受这一干预。

覆盖 prefill 的所有文本序列位置以及每一步 cached decode；每个条件重新生成、重新创建 cache，不复用基线 KV cache。选中 head 输出必须是有限精确零；未选中 head 在当前调用中的 attention/output 不直接改写，后续层发生变化是允许的因果传播。

| 条件 | 数量 | heads |
|---|---:|---|
| baseline | 1 | 无干预，原 eager forward/generate |
| top10_joint | 1 | 10 个候选同时置零 |
| single_LxxHxx | 10 | 每次仅置零 1 个候选 |
| random_seed_* | 3 | 每层数量匹配 Top-10，排除全部候选，无放回抽样 |

随机 seeds：20260912、20260913、20260914。总计 15 个报告条件。每个样本额外运行一次空 hook，与原基线核对 bbox logits 和生成 token；此检查不作为第 16 个处理组。

## 固定输入与预算

模型维度拟为 36 层 × 32 query heads；代码会与真实模型配置比对。模型、LoRA、processor、评估 manifest 和图像处理参数必须由冻结 runtime config 明确提供，不从相邻实验或旧代码路径自动补齐。当前这些值及 Top-10 列表尚未核实，配置保持空值并拒绝运行。

建议先导 3 条（每数据集 1 条），之后固定 60 条（LaSOT/GOT10k/TAO 各 20 条）。这是建议预算，不是已经冻结的样本：每轮必须显式提供样本文件，独立输出目录；不能根据先导效果更换 heads 或挑样本。若沿用 R-001 子集，应在允许读取的原冻结索引上核对包含关系，不能按其他 Run 的样本推断。代码不会随机补足数量。

batch=1，greedy、num_beams=1、use_cache=True、max_new_tokens=128；完整 teacher-forced 序列及 prompt+生成预算均不超过 2048 tokens，超过直接失败。eager BF16 和固定 LoRA 由 runtime config 指定，实际 dtype 以冻结配置为准。60 条预算为 960 次 generation 调用及 960 次独立 teacher-forced forward（含空 hook 检查），生成调用内部含多个 token steps；当前无法可靠估计 GPU 用时与显存。

## 指标与统计

以下为本 Run 草案提出的指标，尚未写入 canonical metric definitions。

- 主要观察：每样本 `ΔIoU = IoU(intervention, annotation GT) − IoU(baseline, annotation GT)`，负值表示退化；保存逐样本配对值，按全体样本等权和各数据集分别汇总。
- 辅助：原始 IoU、bbox 改变率、输出文本改变率、无效输出率；两侧 bbox 都有效时计算 `sum(abs(box − baseline_box)) / (4 × coordinate_scale)`，并报告有效配对数量。
- 已有 CE 辅助诊断：完整 teacher-forced 回答中 bbox token（含标点）的平均 CE，以及相对基线差值；不把 teacher-forced argmax 拼接当成自由生成预测。
- 无效 bbox、多框、越界、退化框或未遇 EOS 的长度截断：保留原文和截断标志，bbox 记无效，IoU 记 0 并保留在完整样本分母；不裁剪、不修复、不静默丢弃。
- annotation GT 必须预先变换到与 prompt 相同的 0–1000 xyxy 坐标。不能拿量化后的 GT 文本反解值替代原 annotation，也不能在结果出来后换坐标约定。

本轮报告影响量，不设置事后“有效”阈值或进行显著性宣称。3 个随机组分别报告，不把随机组当独立数据样本。若正式 Run 需要成功/失败阈值，应在提交时冻结。

## 冻结文件接口

入口配置：`implementation/configs/head_screening/e012_top10_head_ablation.py`。

必须补齐：`heads`（排名顺序的 10 个 `[layer, head]`）、`ranking_path/sha256`、`runtime_config/sha256`、`input_manifest_sha256`、`samples_path/sha256`、新的 `output_dir`。ranking 必须是完整、排序一致的 `iploc-szy.bbox-gradient-ranking/v1` 文件，显式 heads 必须等于该文件前 10 个。

runtime config 使用现有 IPLoc 的 `model`、`checkpoint_path`、`screen_dataloader`、`head_screening.probe` 接口。不会采用其 work_dir、head_circuit.paths 或旧 eval_selection 来决定本次输出、heads、样本。LoRA 加载复用现有精确权重核对，记录 adapter 文件哈希；整个底座权重尚未逐文件哈希。

样本文件格式如下（示意 ID/索引/坐标不能直接当真实样本）：

```json
{
  "schema": "iploc-szy.head-ablation-samples/v1",
  "coordinate_scale": 1000,
  "target_box_source": "annotation",
  "samples": [
    {
      "dataset_index": 0,
      "dataset": "LaSOT",
      "sample_id": "REPLACE_WITH_VERIFIED_SAMPLE_ID",
      "target_box": [100, 100, 200, 200]
    }
  ]
}
```

运行时核对 manifest 内容哈希、样本索引/ID/dataset、坐标范围、模型维度、两张图的 token-grid、bbox supervision。样本 annotation 到 normalized GT 的导出准确性仍须在来源冻结时核实。

## 执行与检查

本地镜像缺少完整 IPLoc 包、PyTorch 和 Transformers。三个新增实现文件需按相同相对路径放入经确认的完整代码仓库；本任务尚未进行远程同步。

```bash
# 完整仓库根目录，填完所有冻结字段后先做静态输入检查。
bash tools/run/e012_top10_head_ablation.sh --validate-only

# 独立新输出目录；仅在正式 Run 的执行流程完成后运行。
bash tools/run/e012_top10_head_ablation.sh
```

`--validate-only` 核对排名、显式 heads、样本、runtime config 的内容哈希及输入格式，不加载模型，不创建输出目录；其通过不代表 runtime、图像或 GPU 检查通过。

启动后保存 resolved_plan、排名/样本/runtime config 原始快照与 checkpoint 信息。每样本每条件增量写 records，包含生成 token/文本、GT/预测框、CE、两图 token 数与 grid、干预 attention 元素数量、prefill/decode 调用计数和审计。异常写 failure，已有输出目录拒绝覆盖；不存在静默断点续跑。

运行正确性门槛：每个文本层每次 forward 都被拦截；每个选中 head 必须覆盖一次 prefill 和全部 decode 调用；selected A@V 精确为 0；空 hook 下 bbox logits 与生成 tokens 复现基线；15 条件 × N 样本完整才发布 completed summary。

## 尚未解决

1. R-001 不在当前结果证据白名单；真实排名、Top-10、模型/数据来源和样本文件待显式参考或用户提供。
2. 未在真实依赖或 GPU 模型环境做集成验证。尤其需验证当前 collator 的回答起点：代码只接受 `<|im_start|>assistant\n` 边界，未知格式会明确报错。
3. 整头干预覆盖全部位置和模态 keys，若破坏通用语言/格式能力，也会影响 bbox。必须同时看无效输出和随机对照。
4. SHA256 验证冻结文件的一致性，不自动证明人工导出的 GT/head 来源正确或底座模型权重未变。

本次本地检查详见 `implementation/top10_head_ablation_verification.md`。
