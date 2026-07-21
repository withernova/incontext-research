# E004-R-008-source-base-object-removal-proxy-gate-n4 · E004-R-008-source-base-object-removal-proxy-gate-n4

- canonical_run_id: `E004-R-008-source-base-object-removal-proxy-gate-n4`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_gate_passed

## 本轮目的
构造object-present source与neutral-fill object-removed base并筛选行为及token对齐pair。

## 必要性 / 证据链位置
source→base CMA要求可定义的行为gap与严格序列/grid对齐。

## 研究依据 / 被审计对象
论文object-removed control/CMA设计的工程proxy。

## 实现方式（简版）
候选bbox加8% padding后neutral canvas fill；重新计算gold Yes/No margin并核验张量对齐。

## 实现方式（详细版）
（待补充）

## 数据身份与构造
4 synthetic quartets、16 candidate conditions；6 strict source-correct/base-wrong pairs。

## 数据规模
（待补充）

## 模型、权重与关键配置
（待补充）

## 变量、干预与对照
（待补充）

## 指标与计数规则
source/base aligned margin、行为正确性、input_ids/attention_mask/image_grid_thw equality。

## 完整性门槛 / no-silent-zero
16/16 aligned；8 broad gap；6 strict pairs。

## 观测结果摘要
（待补充）

## 局限与混杂因素
neutral rectangle不是LaMa；可能引入missing-region cue；synthetic gate原本失败。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
controlled object-removal proxy gate，不是CMA或identity证据。

## 关键指标
（待补充）

## 审核入口
/home/featurize/work/mechanism/explog/E-004/runs/E004-R-008-source-base-object-removal-proxy-gate-n4/logs; /home/featurize/work/mechanism/explog/E-004/runs/E004-R-008-source-base-object-removal-proxy-gate-n4/results; /home/featurize/work/mechanism/explog/E-004/runs/E004-R-008-source-base-object-removal-proxy-gate-n4/analysis; shell/06_experiments/E-004/runs/E004-R-008-source-base-object-removal-proxy-gate-n4.md

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
/home/featurize/work/mechanism/explog/E-004/runs/E004-R-008-source-base-object-removal-proxy-gate-n4/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-004/runs/E004-R-008-source-base-object-removal-proxy-gate-n4

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-004/runs/E004-R-008-source-base-object-removal-proxy-gate-n4

### tmux session
e004_cma_pair_gate

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-004
- run_dir: /home/featurize/work/mechanism/explog/E-004/runs/E004-R-008-source-base-object-removal-proxy-gate-n4
- log_file: /home/featurize/work/mechanism/explog/E-004/runs/E004-R-008-source-base-object-removal-proxy-gate-n4/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-004/runs/E004-R-008-source-base-object-removal-proxy-gate-n4
- metrics_file: /home/featurize/work/mechanism/explog/E-004/runs/E004-R-008-source-base-object-removal-proxy-gate-n4/metrics.json
- tmux_session: e004_cma_pair_gate
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-20T22:30:50
- updated: 2026-07-20T22:30:50

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
