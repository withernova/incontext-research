# E005-R-028-r023-matched35x2-same-resolution-640 · matched35x2 same-resolution640 attention and visualization

- canonical_run_id: `E005-R-028-r023-matched35x2-same-resolution-640`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed_integrity

## 本轮目的
复核旧R023的224 replay方向在640下是否保持。

## 必要性 / 证据链位置
消除归档640自然输出到224 replay的分辨率混杂。

## 研究依据 / 被审计对象
冻结35 error+35 matched correct、冻结heads与自然输出。

## 实现方式（简版）
70标准eager forwards、70图、224-vs640配对审计。

## 实现方式（详细版）
G→R/Q→R exact p-1 alignment；双4090。

## 数据身份与构造
accepted-positive localization error35与matched correct35。

## 数据规模
70 records/70 figures/35 pairs

## 模型、权重与关键配置
Qwen3-VL-8B+IPLoc LoRA bf16 max_side640 eager

## 变量、干预与对照
pairs/heads/output冻结；主要变量为224→640

## 指标与计数规则
strict hit,target mass,enrichment,fIoU,paired resolution stability

## 完整性门槛 / no-silent-zero
70/70 records,70/70 figures,finite,exit0

## 观测结果摘要
640 state11 error9/35=25.7%,correct13/35=37.1%,paired diff CI[-11.43,34.29]pp；conditional9/33 vs13/33。Q→R mass paired median correct-error=.03230 CI[.00604,.08811]；G→R=.00286 CI[-.04268,.03979]。coverage224→640 median4→6；state stable39/70。

## 局限与混杂因素
attention非因果；teacher replay；mostly cross-class matching

## 可支持的结论
correct的Q→R raw target mass更高；离散state方向相同但不稳定且分辨率敏感。

## 不支持的结论 / Claim 边界
只支持attention-derived关联，不证明identity/causal influence。

## 关键指标
（待补充）

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-028-r023-matched35x2-same-resolution-640; shell/06_experiments/E-005/dual_gpu_640_core_results.md

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r028_A_640.sh

### 配置/超参数
（待补充）

### Seed
20260728

### 日志路径
/home/featurize/work/mechanism/explog/E-005/e005_original_640_workflow.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-028-r023-matched35x2-same-resolution-640/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-028-r023-matched35x2-same-resolution-640

### tmux session
（待补充）

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-028-r023-matched35x2-same-resolution-640
- log_file: /home/featurize/work/mechanism/explog/E-005/e005_original_640_workflow.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-028-r023-matched35x2-same-resolution-640/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-028-r023-matched35x2-same-resolution-640/metrics.json
- tmux_session: incontext-E-005-E005-R-028-r023-matched35x2-same-resolution-640
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-28T22:20:42
- updated: 2026-07-28T22:21:10

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
