# e014-reward-constraint-solver-20261016 · 用户授权继续完成奖励自动求解：本地合成约束求解、反例迭代与G=4优势模拟。继承现有未提交模拟程序继续开发，不读取训练产物，不部署或训练。

- 父 Run：`e014-reward-order-simulation-20261016`
- 来源版本：2026-10-16T01:02:25
- 状态：ready_to_run
- Workspace：03

## 本次任务
用户授权继续完成奖励自动求解：本地合成约束求解、反例迭代与G=4优势模拟。继承现有未提交模拟程序继续开发，不读取训练产物，不部署或训练。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：延续同一奖励模拟开发任务的未提交工作树，基线1c47c7305c695151df81d46019143028e01752ad；新增tools/solve_candidate_rewards.py并复用tools/simulate_candidate_rewards.py，README补直接CLI。SciPy仅安装/tmp/e014-reward-solver-deps。实际命令：PYTHONPATH=/tmp/e014-reward-solver-deps python3 tools/solve_candidate_rewards.py --output /home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/.pi/analysis/e014/e014-reward-constraint-solver-20261016/full-rule-comparison。本地模拟退出0；不伪称远端Managed执行完成。专用code_change_review工具不可用，未提交/发布。
- 命令：<PI_STEWARD_PREPARE_RUNTIME_COMMAND>
- 随机种子：11451
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reward-constraint-solver-20261016/logs/run.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reward-constraint-solver-20261016/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reward-constraint-solver-20261016/metrics.json

## 结果
尚无结果。

### 分析
本地自动求解完成：46141条搜索约束、90972条留出约束(seed20261016，10000个初始1–6框合成回答)。smooth_binary和smooth_taper在公开函数族/系数边界内无解，保存不可约冲突；hard_binary权重H .34375/Oracle .05/Selected .4041666667/score .2020833333通过受控偏序，留出违反0，全局五档仅4/10。hard_tier权重L .65/Oracle .05/Selected .15/score .15，辅助C .05/D -.02/O -.02；留出违反0，五档10/10，解析相邻全档差下界.21。G4模拟使用总体std+1e-6，发现但选错可因组内其他回答更好获得负优势。未改变训练或部署，未证明训练收益。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/.pi/analysis/e014/e014-reward-constraint-solver-20261016/full-rule-comparison/results.json
/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/.pi/analysis/e014/e014-reward-constraint-solver-20261016/full-rule-comparison/report.md
/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/.pi/analysis/e014/e014-reward-constraint-solver-20261016/full-rule-comparison/hard_binary_examples.csv
/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/.pi/analysis/e014/e014-reward-constraint-solver-20261016/full-rule-comparison/hard_tier_examples.csv

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
