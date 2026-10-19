# e014-drawn-selection-lora-sft1epoch-20261018-r2 · 用户明确要求修正后直接运行。修复空localization_iou_thresholds与基类校验不兼容，使用53ab7653602f62ffc1d5c9dad

- 父 Run：`e014-drawn-selection-lora-sft1epoch-20261018`
- 来源版本：2026-10-18T14:51:00
- 状态：failed
- Workspace：03

## 本次任务
用户明确要求修正后直接运行。修复空localization_iou_thresholds与基类校验不兼容，使用53ab7653602f62ffc1d5c9dadfbefccf7ad67474；新独立Run保留旧失败记录，不覆盖或resume。复用已验收1152条选择SFT数据/SHA89dda90ab573b0305bf02f5e0c302c59812b6438428008e8a95f1a0009481403，fresh原始Qwen3-VL-8B-Instruct独立语言LoRA r8/alpha16/dropout0 NF4，1epoch/72更新/globalbatch16/lr5e-5/seed20260901，编号EOS监督。无新增评测、无延长；核真实更新及最终checkpoint与metrics。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：One config compatibility fix only. No code tests/import/smoke; AST3.9/diff static checks passed. User explicitly authorizes this corrected independent Run. No test evaluation or extension.
- 命令：set -euo pipefail; cd /defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/iploc-szy; export IPLOC_PYTHON=/songzhengyue/miniconda3/envs/IPLoc/bin/python PYTHONPATH=. OMP_NUM_THREADS=1; mkdir /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018-r2/payload; bash tools/run.sh configs/sft/candidate_selection_lora.py --cfg-options work_dir=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018-r2/payload/training model.model_path=/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct train_dataloader.dataset.ann_file=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/payload/selection_data/train.json train_dataloader.dataset.ann_file_sha256=89dda90ab573b0305bf02f5e0c302c59812b6438428008e8a95f1a0009481403; cp /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018-r2/payload/training/metrics.json /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018-r2/metrics.json; echo SURVEY_TOOL_RUN_COMPLETE
- 代码版本：53ab7653602f62ffc1d5c9dadfbefccf7ad67474
- 随机种子：20260901
- 配置：configs/sft/candidate_selection_lora.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018-r2/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018-r2/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018-r2/metrics.json

## 结果
已完成72/72更新及1152样本，step36/72和最终adapter已保存；最终固定小批次loss下降门禁未通过，进程exit1，Run保留failed而非completed。

### 分析
全部72步loss有限、finite_grad_fraction=1，adapter_delta_norm=2.736153869420579。训练更新耗时794.067s。固定8个训练样本before/after CE=0.007273048726347042/0.048288823978509754，原有loss_after<loss_before条件未满足，payload/training/metrics.json status=gate_failed，worker exit2→launcher exit1，根metrics复制未执行。前12/后12步平均训练loss0.455166/0.196551，但各步样本不同，不能用此推翻固定批次门禁，也不能声称泛化改善。初始化兼容问题已由完整训练验证解决；不更改门禁或自动重训。尚未内部验证或测试集评测。

### Claim 边界
训练数据来源没有新增评测原视频重叠，但固定生成器过去曾见部分同源视频，不能宣称整链无泄漏泛化。无TAO训练来源，属选择器诊断。保持GRPO停止。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018-r2/payload/training/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018-r2/payload/training/checkpoints/samples_00001152_step_000072/adapter

### 审核入口
.pi/analysis/e014/selection-sft/train_r2_final_audit.json

### 过程记录
终态核验覆盖此前启动观察：Run已退出而非仍running；所有更新完整、checkpoint哈希与最终adapter一致。managed scientific fail/nonretryable，接续核验任务failed/队列paused，监控stop；不再注册等待脚本。保留旧失败Run。用户授权修复直接运行已执行，不扩展评测或训练预算。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
