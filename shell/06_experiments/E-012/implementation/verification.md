# E-012 当前实现与检查

## 当前配置

- 加载用户明确指定的 `E-011/20260907T174853785543Z--focus-early-gt-mask-pipeline/adapter`。底座为原始 Qwen3-VL-8B-Instruct，BF16 + LoRA；不复现训练4bit路径，不恢复optimizer或GT-mask训练hook。
- `checkpoint_path` 支持训练根目录、具体checkpoint目录、adapter目录或None；自动解析adapter结构与保存的processor，严格核对底座和载入权重。None使用原始模型。
- 直接复用 `test_combined_lasot600_gotval_taoval_1shot_focus.json` 的原始帧对，共1766条。相对指定训练清单检查reference/query视频重叠后，按seed20260910选LaSOT/GOT10k/TAO各7/7/6条不同视频。
- config和Shell已加中文注释。早先生成的LaSOT20清单副本仅保留作准备过程记录，当前配置不会读取它，`manifest_preparation=None`。
- 全部1152个heads都参与，保留bbox-only CE、p−1行、query视觉列、真实A→AV梯度、绝对与signed分数；输出总排名与三个数据集单独排名。

## 实际检查

远端torch 2.8.0+cu128 / transformers 4.57.3；代码使用已有Config与注册器。

```bash
/defaultShare/archive/liuwenchu/miniconda3/envs/IPLoc/bin/python -m pytest -q tests/test_bbox_gradient_screen.py -p no:cacheprovider --basetemp /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/checks/pytest-bbox-gradient-v4
bash tools/run/e012_bbox_gradient_initial.sh --check-only
bash -n tools/run/e012_bbox_gradient_initial.sh
```

- CPU测试：**10 passed, 2 warnings in 22.34s**。新增测试覆盖真实PEFT adapter精确重载/输出一致性/梯度，checkpoint路径解析、底座不匹配拒绝，1766条清单抽20条，以及跨数据集配额、训练视频排除和训练清单哈希变动。
- 实际eval输入经checkpoint保存的processor预检：**20/20通过**，序列391–675 tokens，bbox 15–19 tokens。1766条eval记录与当前指定训练清单10522条在(dataset,视频目录名)上无重叠；选中20个视频也无训练重叠。
- 选中索引、各数据集配额及manifest/adapter哈希见 `eval_preflight.json`；代码同步哈希见 `source_hashes.json`。
- 警告来自既有torchvision image扩展和CPU测试的临时微型底座未保存config；PIL和实际checkpoint processor预检已通过。
- 本轮没有加载完整8B模型执行筛查。CPU adapter测试验证加载实现，实际目标adapter目前完成文件、结构、哈希和processor校验，正式运行才加载并逐张量验证。

## 结论边界

无训练视频重叠只相对于当前指定训练清单，不证明预训练未见或历史清单未变。20个eval样本参与选head，因此后续验证收益应使用另一批未参与筛查的样本。每域6–7条仅供探索性观察，不能确认跨域泛化提升。

BF16与训练4bit路径不同；真实8B反向显存待测。signed仅解释不重新归一化的指定概率边缩放；中央差分诊断不通过时不得声称方向已验证。

远端基线commit为 `0b1aac48a8f8d8d4aac9cb0936ef955fd6472bed`；E-012 新增文件已于 2026-09-11 提交为 `4411686f9205d55342c4856e79bedb83e80045ef`（main，未push）。现有probes.py等其他在途改动属于E-011 query-attention分支，未纳入本次提交。使用的论文参考为makelvlm2025，无Solid Run结果证据。

## 本次重新核验

本地与远端代码无缺失，前次Run修订停在changes_requested，尚未重新提交。本次统一预检/运行输入校验，并新增完整小型双图Qwen3-VL+LoRA测试，覆盖视觉输入、bbox预测行、参数状态恢复、梯度、中央差分和最终排名。10项CPU测试通过；完整8B模型仍未运行。实际检查原始输出另存pytest-bbox-gradient-v4.txt与eval-preflight-v4.json。

## 结果回登时的复核（2026-09-11）

按用户要求核验 R-001 远端产物并回登 survey-tool，未重跑 GPU。

- 远端 E-012 产物与本地镜像 SHA256 逐一一致：`summary.json` 00cf37ec…、`ranking.csv` 6be84c53…、`frozen_input.json` df4771e6…、`runtime.json` a7d5ca70…、`probe/records.json` 34bbeca9…（690条）；另核对 20条 `summary.json`/`frozen_input.json` 与旧 `selection.json`。
- 结构复核通过：690 records、索引唯一且与 `frozen_input.selected_indices` 完全一致、36×32=1152 heads、`prediction_rows=p_i−1` 无违例、数据集计数 300/90/300、排名单调、absolute=signed+正负分量在浮点误差内（最大相对误差 2.8e-8）。
- 日志核对：`logs/R-001-bbox-gradient-initial.log` 先完成 20/20，随后对已存在 `work_dir` 的重复调用抛 `FileExistsError`（保护逻辑，非科学失败），再以 690 条重跑至 `[BBOX_GRADIENT_DONE] samples=690`。
- 代码聚焦检查（commit `4411686` 内容）：`py_compile` 通过、`bash -n` 通过、`pytest -q tests/test_bbox_gradient_screen.py` 10 passed。
- 发现并修正的同步偏差：本地 `implementation/configs/head_screening/e012_bbox_gradient_initial.py` 与 `source_hashes.json` 早先记录不一致（673eb5a8… / 025070db…），两者都不等于实际执行的 2d19e849…。已用提交版本（2d19e849…，screening_counts 300/90/300、work_dir halffull）覆盖本地快照并重算 `source_hashes.json`，现本地快照与 committed 远端文件逐一致。
- 保留的未通过项：首样本 `finite_difference.sign_agreement=false`（relative_error=1.287289）；该诊断不阻断输出，`summary.status=completed` 不代表梯度方向已验证。
