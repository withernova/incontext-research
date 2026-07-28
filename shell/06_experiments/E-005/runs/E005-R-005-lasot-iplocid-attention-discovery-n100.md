# E005-R-005-lasot-iplocid-attention-discovery-n100 · 自有LaSOT/IPLoc-ID attention discovery n100

- canonical_run_id: `E005-R-005-lasot-iplocid-attention-discovery-n100`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed

## 本轮目的
在任务内discovery split统计稳定attention-derived head频率与positive/negative、reference/query差异。

## 必要性 / 证据链位置
R-004 n10门禁通过且运行成本低；继续使用GPU执行不与evaluation复用的较大discovery。

## 研究依据 / 被审计对象
R-004 40/40 gates通过，top候选出现重复且峰值显存18.19GB。

## 实现方式（简版）
冻结manifest indices 0:100为discovery；每sample positive/negative，每prompt reference/query span，repo-original top5。

## 实现方式（详细版）
eager bf16 max_side224；400 records；indices100:140保留为独立evaluation，不在本run选head。

## 数据身份与构造
本地LaSOT deterministic POIL reconstruction；discovery indices0-99；不使用COCO。

## 数据规模
100 samples、200 target prompts、400 span records；evaluation40 samples保留。

## 模型、权重与关键配置
Qwen3-VL-8B+IPLoc-ID LoRA，eager bf16，224。

## 变量、干预与对照
固定连续split；positive/same-class negative；reference/query分开；last text token query；top_k5。

## 指标与计数规则
shape/finite/grid gates；总体与四role频率；runtime/memory。

## 完整性门槛 / no-silent-zero
400 records、全gate通过、正常退出。

## 观测结果摘要
自有LaSOT/IPLoc-ID discovery n100完成；400/400 span records全部通过门禁。

## 局限与混杂因素
非官方split；224低分辨率；单次固定split；attention非因果；n100不是论文1000样本复现。

## 可支持的结论
得到固定task-internal discovery split上的attention-derived候选频率；不是因果证据、非官方split、低分辨率，尚需indices100:140独立evaluation且不得重选。

## 不支持的结论 / Claim 边界
只产出task-internal attention-derived discovery候选；后续必须在indices100:140独立评估且不得重选。

## 关键指标
n=100; prompts=200; records=400; runtime=87.423s; load=6.655s; peak allocated=17,923,809,792 bytes; reserved=18,272,485,376 bytes; top frequencies: L02H17=216/400, L04H03=178/400, L12H21=135/400, L02H08=100/400, L08H12=97/400。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-005-lasot-iplocid-attention-discovery-n100; /home/featurize/data/e002_manifests/LASOT_local_1shot_T2_n140_v2.json

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r005_lasot_attention_discovery.py --start 0 --n 100 --max-side 224

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-005-lasot-iplocid-attention-discovery-n100/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-005-lasot-iplocid-attention-discovery-n100/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-005-lasot-iplocid-attention-discovery-n100

### tmux session
e005_lasot_discovery

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-005-lasot-iplocid-attention-discovery-n100
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-005-lasot-iplocid-attention-discovery-n100/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-005-lasot-iplocid-attention-discovery-n100/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-005-lasot-iplocid-attention-discovery-n100/metrics.json
- tmux_session: e005_lasot_discovery
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T15:23:27
- updated: 2026-07-24T15:26:02

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
