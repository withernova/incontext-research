# e015-qwen2-cleanvqa-e014-proposals1766-20261027 · 用户明确要求使用新的Qwen2 VQA评测E014原始proposal，固定1766条1shot/791多框，报告score/VQA/Oracle及旧VQA配对

- 父 Run：`e015-qwen2-selector-e014clean-20261026`
- 来源版本：2026-10-27T10:39:10
- 状态：failed
- Workspace：03

## 本次任务
用户明确要求使用新的Qwen2 VQA评测E014原始proposal，固定1766条1shot/791多框，报告score/VQA/Oracle及旧VQA配对；另报排除18原视频重合后的1748条。等现有完整GRPO及其评测成功结束且8卡空闲后执行，不中断训练。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户要求新的Qwen2 VQA评测E014原proposal。固定旧1766查询(LaSOT600/GOT180/TAO986)、1shot、791多框、原候选及顺序，复用Qwen2 clean VQA4172步checkpoint；BF16/SDPA、4副本×2GPU、layer_split10、exact_instance原图坐标prompt、greedy16/EOS/4096patches/seed20260901，与旧Qwen3 step4041同输入对照。预检发现18条LaSOT原视频与新VQA训练重合，图像路径/内容SHA无重合，因此报告全1766及排除18条后的1748，另报多框及分数据集，不能称旧全集无污染。全部候选仍评测，只在统计中显式分组。当前完整GRPO占8卡，本次受管任务仅CPU事件等待指定训练及其既定评测exit0、GPU无compute进程；48h上限，父失败/用户停止时不启动，不中断或恢复父训练。推理只复用tools/evaluate_candidate_vqa.py，无共享源码变更；任务局部audit.py只核验来源与配对汇总，wait_for_training.py只管理本次资源等待。固定已部署SHA，不降低分辨率或量化，不生成新proposal，不重训VQA。18视频重合、旧探索集及生成器曝光边界保留，不作为当前E015作者划分结果，不升级Claim。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-proposals1766-20261027/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'d663c684a85d091c7b4628709d0aa766b1a62c30f1d1541bfb56e8597775002c'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：0e02d856ae30837eb60b511e8303cb50a50d1c26
- 随机种子：20260901
- 配置：tools/evaluate_candidate_vqa.py direct CLI: Qwen2 clean VQA4172 on frozen E0141766 proposals; exact command in plan.json
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-proposals1766-20261027/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-proposals1766-20261027/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-proposals1766-20261027/metrics.json

## 结果
尚无结果。

### Claim 边界
旧探索候选诊断；不代表当前E015作者划分，不隔离模型/训练规模/更新预算因果；排除已知视频重合仍非全部近重复保证，不升级Claim。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-proposals1766-20261027/payload/evaluation/predictions.jsonl
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-proposals1766-20261027/payload/evaluation/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-proposals1766-20261027/payload/comparison.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-proposals1766-20261027/resource_gate_passed.json

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
