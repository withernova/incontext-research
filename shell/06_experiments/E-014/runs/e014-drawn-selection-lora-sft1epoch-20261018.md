# e014-drawn-selection-lora-sft1epoch-20261018 · 用户已授权独立选择LoRA训练。本训练Run只在数据父Run成功且train/validation分组、候选及渲染/标签哈希验收后启动。原始Qwen3-VL-8

- 父 Run：`e014-selection-sft-data-step200-20261018`
- 来源版本：2026-10-18T12:36:10
- 状态：failed
- Workspace：03

## 本次任务
用户已授权独立选择LoRA训练。本训练Run只在数据父Run成功且train/validation分组、候选及渲染/标签哈希验收后启动。原始Qwen3-VL-8B-Instruct新LoRA r8/alpha16/dropout0、语言层、无SFT659或GRPO权重初始化，NF4，初始化/数据seed20260901；只监督画框VQA答案编号及EOS。读取父Run过滤并均衡编号的train.json，验证组不训练；小预算1 epoch、lr5e-5、global batch16（8GPU×1×accum2）、warmup5%、clipnorm.3、vision4096，每.5epoch保存。按实际样本数计算更新次数，不用1766测试集选步数。先启动核验，不自动延长/恢复GRPO；内部验证后再判断是否有效。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 命令：set -euo pipefail; cd /defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/iploc-szy; export IPLOC_PYTHON=/songzhengyue/miniconda3/envs/IPLoc/bin/python PYTHONPATH=. OMP_NUM_THREADS=1; mkdir /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018/payload; bash tools/run.sh configs/sft/candidate_selection_lora.py --cfg-options work_dir=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018/payload/training model.model_path=/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct train_dataloader.dataset.ann_file=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/payload/selection_data/train.json train_dataloader.dataset.ann_file_sha256=89dda90ab573b0305bf02f5e0c302c59812b6438428008e8a95f1a0009481403; cp /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018/payload/training/metrics.json /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018/metrics.json; echo SURVEY_TOOL_RUN_COMPLETE
- 代码版本：a45d11a9c1ebe9953e7f4522eb463cef9650db02
- 随机种子：20260901
- 配置：configs/sft/candidate_selection_lora.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018/metrics.json

## 结果
尚无结果。

### Claim 边界
训练数据来源没有新增评测原视频重叠，但固定生成器过去曾见部分同源视频，不能宣称整链无泄漏泛化。无TAO训练来源，属选择器诊断。保持GRPO停止。

### 审核入口
.pi/analysis/e014/selection-sft/data_integrity_audit.json
.pi/analysis/e014/selection-sft/train_command.json

### 过程记录
单次受管launch成功；首次continue被当前会话review门禁拒绝，未启动；补充空diff审阅31ee653c5faa49f0通过（实现仍a45d11a、原review5292ddffff035b69）后continue返回started/trusted config加载警告，status确认running/tmux alive，未重复启动。实际launch快照核fresh initialize_from/resume_from均null、LoRA配置、seed、1epoch及train SHA通过；证据.pi/analysis/e014/selection-sft/train_launch_snapshot.json与train_command.json。启动观察仅出现launch/train snapshots，暂无首更新证据，不能宣称loss/梯度已验收。指定回调包装器PID170350等待现有Run exit文件，事件.pi/steward-signals/d8f0c3cf-24f0-45e5-a460-2c4f7f61c004.json；不sleep/模型轮询，不重启。Steward重新绑定训练Run并启动30min监控，无自动修复。回调后核首更新、finite loss/gradient、72updates、非零adapter_delta/完整checkpoint/稳定metrics再complete；失败则fail暂停，不重试。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
