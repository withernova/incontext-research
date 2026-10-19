# e014-step150-vs200-paired-analysis-20261016 · 用户要求分析step150结果为何与预期不同；离线比较同轮step200的1766条prediction，分解候选质量和score选择，不重新推理。

- 父 Run：`e014-discovery-score04-step150-eval1766-20261015T161128Z`
- 来源版本：2026-10-16T00:12:54
- 状态：ready_to_run
- Workspace：03

## 本次任务
用户要求分析step150结果为何与预期不同；离线比较同轮step200的1766条prediction，分解候选质量和score选择，不重新推理。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：本地离线读取两次明确引用评测的metrics和predictions；不重新推理。分析脚本与输入存于 /home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/.pi/analysis/e014/step150-vs200
- 命令：<PI_STEWARD_PREPARE_RUNTIME_COMMAND>
- 随机种子：20260901
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-step150-vs200-paired-analysis-20261016/logs/run.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-step150-vs200-paired-analysis-20261016/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-step150-vs200-paired-analysis-20261016/metrics.json

## 结果
尚无结果。

### 分析
同轮1766条逐dataset_index/id/dataset/target对齐。step150 Selected .6932669712 Oracle .7263236003 多框263/1766；step200 Selected .6916960158 Oracle .7573992982 多框791/1766。single→multi n528 Selected .6204368738→.5962361197 Oracle .6204368738→.7192414999；multi→multi n260 Selected .5840363228→.6465473505。Oracle命中但Selected失败67→133；150多框全零score84/263，失败中top tie29/67。最后50步候选覆盖改善但整体选框持平，不能断言显著退化或奖励因果。未做图像人工复核、显著性检验；未测试，无Solid/Claim提升。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/.pi/analysis/e014/step150-vs200/analysis.json
/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/.pi/analysis/e014/step150-vs200/report.md

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
