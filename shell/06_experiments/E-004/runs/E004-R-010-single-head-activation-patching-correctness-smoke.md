# E004-R-010-single-head-activation-patching-correctness-smoke · E004-R-010-single-head-activation-patching-correctness-smoke

- canonical_run_id: `E004-R-010-single-head-activation-patching-correctness-smoke`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed

## 本轮目的
验证source→base单head pre-o_proj activation patch的切片和确定性。

## 必要性 / 证据链位置
完整per-head CMA前必须确认head slice和full-layer等价关系。

## 研究依据 / 被审计对象
R-009通过后的implementation correctness gate。

## 实现方式（简版）
s0_RA_CA的L18/H0；比较source/base repeat、no-op、full patch、single-head repeat、32 slices patch。

## 实现方式（详细版）
（待补充）

## 数据身份与构造
单个strict neutral-fill proxy pair；engineering smoke。

## 数据规模
（待补充）

## 模型、权重与关键配置
（待补充）

## 变量、干预与对照
（待补充）

## 指标与计数规则
full-vocabularylogit max abs diff、finite、PPL/MF仅作诊断。

## 完整性门槛 / no-silent-zero
全部repeat/no-op/all-slices-vs-full diff=0；finite=true。

## 观测结果摘要
（待补充）

## 局限与混杂因素
单pair；all positions；neutral-fill；H0未被科学选择。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
仅证明single-head hook正确；H0 MF不构成head证据。

## 关键指标
（待补充）

## 审核入口
/home/featurize/work/mechanism/explog/E-004/runs/E004-R-010-single-head-activation-patching-correctness-smoke/logs; /home/featurize/work/mechanism/explog/E-004/runs/E004-R-010-single-head-activation-patching-correctness-smoke/results; /home/featurize/work/mechanism/explog/E-004/runs/E004-R-010-single-head-activation-patching-correctness-smoke/analysis; shell/06_experiments/E-004/runs/E004-R-010-single-head-activation-patching-correctness-smoke.md

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
（待补充）

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-004/runs/E004-R-010-single-head-activation-patching-correctness-smoke/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-004/runs/E004-R-010-single-head-activation-patching-correctness-smoke

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-004/runs/E004-R-010-single-head-activation-patching-correctness-smoke

### tmux session
e004_head_patch_smoke

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-004
- run_dir: /home/featurize/work/mechanism/explog/E-004/runs/E004-R-010-single-head-activation-patching-correctness-smoke
- log_file: /home/featurize/work/mechanism/explog/E-004/runs/E004-R-010-single-head-activation-patching-correctness-smoke/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-004/runs/E004-R-010-single-head-activation-patching-correctness-smoke
- metrics_file: /home/featurize/work/mechanism/explog/E-004/runs/E004-R-010-single-head-activation-patching-correctness-smoke/metrics.json
- tmux_session: e004_head_patch_smoke
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-20T22:30:51
- updated: 2026-07-20T22:30:51

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
