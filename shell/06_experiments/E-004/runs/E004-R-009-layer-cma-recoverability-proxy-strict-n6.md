# E004-R-009-layer-cma-recoverability-proxy-strict-n6 · E004-R-009-layer-cma-recoverability-proxy-strict-n6

- canonical_run_id: `E004-R-009-layer-cma-recoverability-proxy-strict-n6`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_gate_passed

## 本轮目的
在逐head扫描前测试full-layer source→base activation patch能否恢复gold-token perplexity gap。

## 必要性 / 证据链位置
若整层patch都不可恢复，则不应进行1152-head扫描。

## 研究依据 / 被审计对象
参照Mechanisms论文source→base CMA，但当前为proxy feasibility pilot。

## 实现方式（简版）
6 strict pairs×36 layers；source full pre-o_proj activation patch到base全部对齐序列位置。

## 实现方式（详细版）
（待补充）

## 数据身份与构造
R-008的6个strict neutral-fill proxy pairs；216 records。

## 数据规模
（待补充）

## 模型、权重与关键配置
（待补充）

## 变量、干预与对照
（待补充）

## 指标与计数规则
teacher-forced gold Yes/No PPL；MF=(Pbase-Ppatched)/(Pbase-Psource)。

## 完整性门槛 / no-silent-zero
216/216；finite；至少一层mean MF>0且positive rate>=0.5；L18 positive=6/6。

## 观测结果摘要
（待补充）

## 局限与混杂因素
neutral-fill、deepstack-uncontrolled、all-sequence positions、无discovery/eval split。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
layer-level recoverability proxy；不是per-head或identity-routing结果。

## 关键指标
（待补充）

## 审核入口
/home/featurize/work/mechanism/explog/E-004/runs/E004-R-009-layer-cma-recoverability-proxy-strict-n6/logs; /home/featurize/work/mechanism/explog/E-004/runs/E004-R-009-layer-cma-recoverability-proxy-strict-n6/results; /home/featurize/work/mechanism/explog/E-004/runs/E004-R-009-layer-cma-recoverability-proxy-strict-n6/analysis; shell/06_experiments/E-004/runs/E004-R-009-layer-cma-recoverability-proxy-strict-n6.md

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
/home/featurize/work/mechanism/explog/E-004/runs/E004-R-009-layer-cma-recoverability-proxy-strict-n6/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-004/runs/E004-R-009-layer-cma-recoverability-proxy-strict-n6

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-004/runs/E004-R-009-layer-cma-recoverability-proxy-strict-n6

### tmux session
e004_cma_layer_gate

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-004
- run_dir: /home/featurize/work/mechanism/explog/E-004/runs/E004-R-009-layer-cma-recoverability-proxy-strict-n6
- log_file: /home/featurize/work/mechanism/explog/E-004/runs/E004-R-009-layer-cma-recoverability-proxy-strict-n6/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-004/runs/E004-R-009-layer-cma-recoverability-proxy-strict-n6
- metrics_file: /home/featurize/work/mechanism/explog/E-004/runs/E004-R-009-layer-cma-recoverability-proxy-strict-n6/metrics.json
- tmux_session: e004_cma_layer_gate
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-20T22:30:50
- updated: 2026-07-20T22:30:50

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
