# e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766 · 用户要求暂停当前0.5额外补偿训练并评测其step350。父训练已主动停止，8rank完成380；评测本父Run保存payload/grpo/checkpoin

- 父 Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451`
- 来源版本：2026-10-15T08:29:34
- 状态：failed
- Workspace：03

## 本次任务
用户要求暂停当前0.5额外补偿训练并评测其step350。父训练已主动停止，8rank完成380；评测本父Run保存payload/grpo/checkpoints/step_000350，policy SHA2399a6db32649adc219f4e85f859dd052cbc634fe85571e5aee087ccdb235a84。独立原1766样本/8GPU/multi_v2/greedy192/vision4096/eval seed20260901，沿用score最高并列首选和原指标。只新增薄来源绑定及导航，复用explicit_binding Shell/worker及preflight（optimizer.steps350/来源SHA）；记录beta0/.6/.5真实源参数。评测后保持训练暂停、不覆盖产物、不自动恢复或重跑；按用户偏好只启动健康/配置核验，不持续监控日志。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户暂停当前0.5训练并评测step350：8rank实际最后380，唯一协调器SIGTERM及自有workers退出，8GPU idle；step350 policy/config/optimizer非空，policy SHA2399a6db32649adc219f4e85f859dd052cbc634fe85571e5aee087ccdb235a84，源actual trainer/snapshot beta0/.6探索/.5额外补偿/G4/promptmulti_v2 SHA核验。仓库code prepare两次fetch失败，未编辑或发布源码；参数任务使用现有Config接口的Run内薄参数绑定（outputs/evaluation_config.py），继承已部署原newreward step150配置仅覆盖checkpoint/work/input及真实.6/.5 reward期待。Runtime配置AST/继承比较通过，SHA145696a85f621ec163ca00d78e09c34fe282065769d82c7840158b8ee4ea9bd1，未测试/build/import-smoke；源码仍7bb09c762b4e6030fe870b34f9c1a119d7c81425，无新部署或源码改动。复用explicit_binding冻结prepare/worker/AP：原1766样本，8GPU，greedy192/vision4096/eval seed20260901；Shell preflight核验optimizer.steps350、source SHA/只读alias和空闲GPU，inputs记录8reward项/G4。只受管启动健康/一次配置核验，不持续日志监控，不自动恢复或重跑。Run根outputs作为canonical output，worker独占payload/evaluation，不能预建payload。
- 命令：env E014_EVAL_PROFILE=explicit_binding E014_EVAL_RUN=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766 E014_EVAL_CHECKPOINT=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451/payload/grpo/checkpoints/step_000350 E014_EVAL_CONFIG=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766/outputs/evaluation_config.py E014_EVAL_VARIANT=multi_v2 E014_EVAL_STEP=350 E014_EVAL_PROMPT_SHA=c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba bash tools/run/eval/e014/e014_step800_eval1766_8gpu.sh
- 代码版本：7bb09c762b4e6030fe870b34f9c1a119d7c81425
- 随机种子：20260901
- 配置：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766/outputs/evaluation_config.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766/metrics.json

## 结果
首次启动目录preflight exit1：将参数配置放到outputs违反必须空占位约定；无payload/inputs、无模型加载/预测/指标，失败目录保留。当前用户任务由独立修正版 e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2 继续首次实际评测，未重用失败目录。

### 结论范围
单checkpoint/单seed/已查看1766测试集诊断，不作为奖励系数因果或最终性能Claim；训练保持暂停。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
.pi/analysis/e014/e014-bonus05-step350-eval/runtime_config.py
.pi/analysis/e014/e014-bonus05-step350-eval/source_config_review.json

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
