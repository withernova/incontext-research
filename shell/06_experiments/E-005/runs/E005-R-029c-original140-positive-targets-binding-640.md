# E005-R-029c-original140-positive-targets-binding-640 · original E003 positive n140 same-resolution640 binding audit

- canonical_run_id: `E005-R-029c-original140-positive-targets-binding-640`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed_integrity

## 本轮目的
在原始positive数据上检验G→R/Q→R discrepancy与自然定位IoU关系。

## 必要性 / 证据链位置
避免仅依赖扩充n280或旧224 replay。

## 研究依据 / 被审计对象
E003-R004b冻结manifest与归档640自然输出。

## 实现方式（简版）
140/140 exact archived-output replay；sequence-cluster统计。

## 实现方式（详细版）
标准eager640；冻结grounding/localization heads；raw target mass。

## 数据身份与构造
positive target n140；error35/correct76/partial22/FN7。

## 数据规模
140 records,0 unalignable

## 模型、权重与关键配置
Qwen3-VL-8B+IPLoc LoRA bf16 max_side640 eager

## 变量、干预与对照
自然输出、heads、阈值冻结

## 指标与计数规则
D_abs=abs(logit P_GtoR-logit P_QtoR); strict hit; target mass; Spearman IoU

## 完整性门槛 / no-silent-zero
140/140 aligned,finite,exit0

## 观测结果摘要
n140：error35/correct76/partial22/FN7。D_abs medians2.1006 vs1.5269，diff+.5737，cluster CI[-.2216,1.4190]；Spearman rho=-.1860,p=.05067,n111；coverage median9,>=4 121/140。

## 局限与混杂因素
teacher replay；attention非因果；本地重建split

## 可支持的结论
discrepancy方向性但CI跨0；结合R033，最强error signature为Q→Q localization collapse而非G→R grounding消失。

## 不支持的结论 / Claim 边界
discrepancy只有方向性，CI跨0；不证明机制。

## 关键指标
（待补充）

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-029c-original140-positive-targets-binding-640; shell/06_experiments/E-005/dual_gpu_640_core_results.md

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r029c_r030c_B_640.sh

### 配置/超参数
（待补充）

### Seed
20260728

### 日志路径
/home/featurize/work/mechanism/explog/E-005/e005_original140_640_recovery_c.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-029c-original140-positive-targets-binding-640/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-029c-original140-positive-targets-binding-640

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
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-029c-original140-positive-targets-binding-640
- log_file: /home/featurize/work/mechanism/explog/E-005/e005_original140_640_recovery_c.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-029c-original140-positive-targets-binding-640/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-029c-original140-positive-targets-binding-640/metrics.json
- tmux_session: incontext-E-005-E005-R-029c-original140-positive-targets-binding-640
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-28T22:20:42
- updated: 2026-07-28T22:21:10

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
