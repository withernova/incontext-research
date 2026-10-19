# e014-selection-lora-resume72-total5epochs-20261018 · 用户明确要求有Oracle提升空间则累计训练5epoch。已有1766结果LoRA69.9607% vs Oracle75.7399%，多框62.9412% v

- 父 Run：`e014-drawn-selection-lora-sft1epoch-20261018-r2`
- 来源版本：2026-10-18T16:42:26
- 状态：failed
- Workspace：03

## 本次任务
用户明确要求有Oracle提升空间则累计训练5epoch。已有1766结果LoRA69.9607% vs Oracle75.7399%，多框62.9412% vs75.8440%。从已保存step72恢复独立选择LoRA及AdamW/scheduler，保持1152条数据/SHA、globalbatch16/lr5e-5/seed20260901/NF4/LoRA/编号EOS目标不变；runner.max_epochs=5，累计360更新，额外288更新/4epoch。复用runner.resume_from，不是重新训练5epoch。每.5epoch保存，原固定批次诊断门禁保留（本段baseline为step72模型）；无额外评测或自动选测试最优checkpoint。旧gate_failed记录及模型保留。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 命令：set -euo pipefail; cd /defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/iploc-szy; export IPLOC_PYTHON=/songzhengyue/miniconda3/envs/IPLoc/bin/python PYTHONPATH=. OMP_NUM_THREADS=1; mkdir /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-resume72-total5epochs-20261018/payload; bash tools/run.sh configs/sft/candidate_selection_lora.py --cfg-options work_dir=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-resume72-total5epochs-20261018/payload/training model.model_path=/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct train_dataloader.dataset.ann_file=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/payload/selection_data/train.json train_dataloader.dataset.ann_file_sha256=89dda90ab573b0305bf02f5e0c302c59812b6438428008e8a95f1a0009481403 runner.max_epochs=5 runner.resume_from=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018-r2/payload/training/checkpoints/samples_00001152_step_000072; cp /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-resume72-total5epochs-20261018/payload/training/metrics.json /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-resume72-total5epochs-20261018/metrics.json; echo SURVEY_TOOL_RUN_COMPLETE
- 代码版本：53ab7653602f62ffc1d5c9dadfbefccf7ad67474
- 随机种子：20260901
- 配置：configs/sft/candidate_selection_lora.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-resume72-total5epochs-20261018/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-resume72-total5epochs-20261018/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-resume72-total5epochs-20261018/metrics.json

## 结果
累计5epoch/360更新完成：step72恢复后新增288更新/4608样本呈现，累计5760。exit0，metrics.status=passed，原固定批次loss门禁通过；模型和8个新checkpoint完整。

### 分析
实际history73..360连续且全部loss有限/finite_grad_fraction1/lr5e-5；累计history前72项与父训练完全一致。8个checkpoint108/144/180/216/252/288/324/360均核trainer_state步数、samples、scheduler、504 AdamW状态、adapter配置及SHA；最终adapter与step360哈希一致。固定8训练样本CE从恢复模型step72的0.048288823978509754降至0.000032193263558522034；adapter_delta_norm相对step72为2.826792710906639。本段训练3174.548s（约52.91min）。数据SHA及模型NF4/LoRA/seed/快照53ab765与批准配置一致。续训前36/末36步平均loss0.134879/0.001158仅描述训练，不替代验证。

### 局限
当前仅验收训练事实，未执行step360内部验证或1766测试。低训练loss不能证明泛化或Oracle差距缩小；过拟合尚未排除。恢复重播种非精确RNG replay；名义warmup18但全续训实际lr5e-5。父1epoch gate_failed历史不改，Claim不改。

### Claim 边界
训练数据来源没有新增评测原视频重叠，但固定生成器过去曾见部分同源视频，不能宣称整链无泄漏泛化。无TAO训练来源，属选择器诊断。保持GRPO停止。

### 审核入口
.pi/analysis/e014/selection-sft/train_total5_final_audit.json

### 过程记录
训练真实exit0，360步/288新增更新及全部产物验收通过，metrics.status=passed。管理收尾受工具缺陷阻塞：managed_execution.py MAX_OUTPUT=65536，读取90760字节有效JSON被截断，complete报metrics JSON invalid。另存59046字节无损metrics.compact.json并通过canonical update登记后，complete仍读取原执行绑定文件而失败；已将canonical metrics恢复原路径，副本保留作证据，不改原指标/命令/批准快照/退出码，不修工具或扩大本任务。将管理dispatch/队列按external_dependency失败暂停，不能称训练失败或科学gate_failed。完整训练模型可供后续授权评测。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
