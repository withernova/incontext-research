# E005-R-004-lasot-iplocid-attention-pilot-n10 · 自有LaSOT/IPLoc-ID正负样本attention pilot n10

- canonical_run_id: `E005-R-004-lasot-iplocid-attention-pilot-n10`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed

## 本轮目的
尽早验证任务内跨样本repo-original localization-head选择频率，并比较positive/negative下reference/query视觉span。

## 必要性 / 证据链位置
R-002c只验证synthetic单样本；用户要求直接运行自有数据，正式discovery前需小pilot确认稳定性和运行成本。

## 研究依据 / 被审计对象
R-000适配器门禁、R-002c真实eager attention门禁、R-003c自有manifest完整性均通过。

## 实现方式（简版）
固定manifest前10 samples；每sample运行positive与same-class negative；每个prompt分别采集last text token到reference/query span，并按repo-original规则取top5。

## 实现方式（详细版）
bf16 eager、max_side=224、Qwen3-VL-8B+IPLoc-ID LoRA；40个attention records；仅首sample保存原始attention以限制存储。

## 数据身份与构造
LASOT_local_1shot_T2_n140_v2前10；本地确定性POIL reconstruction，非官方split；不使用COCO。

## 数据规模
10 samples × 2 target roles × 2 image spans=40 records。

## 模型、权重与关键配置
Qwen3-VL-8B-Instruct snapshot 0c351d + IPLoc-ID 1shot LoRA；eager bf16；max_side224。

## 变量、干预与对照
同一reference配positive和same-class negative；初始query严格为last input text token；reference/query分开；top_k=5。

## 指标与计数规则
每record shape/finite/grid gates、top5 head、跨样本及role条件选择频率、runtime和peak memory。

## 完整性门槛 / no-silent-zero
40 records；全部finite；36×32×1×V；grid匹配；eager；正常退出。

## 观测结果摘要
自有LaSOT/IPLoc-ID n10 eager-attention pilot正常完成；40/40 records全部通过shape、finite与grid门禁。

## 局限与混杂因素
n10工程pilot；固定前10非随机代表样本；低分辨率；attention不是因果；不能称正式1000样本复现。

## 可支持的结论
支持自有任务数据跨样本attention工程可扩展，并产生初步attention-derived频率候选；n10固定前缀、低分辨率、非官方split，不能称正式head discovery或因果结果。

## 不支持的结论 / Claim 边界
仅决定是否可扩展和如何冻结正式task-internal discovery/evaluation；不报告因果head。

## 关键指标
n=10; target conditions=20; records=40; top_k=5; runtime=9.779s（不含加载）; load=8.725s; peak allocated=17,914,594,304 bytes; peak reserved=18,192,793,600 bytes; overall top: L02H17=20/40, L04H03=19/40, L12H21=14/40; all_checks_pass=true。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-004-lasot-iplocid-attention-pilot-n10; /home/featurize/data/e002_manifests/LASOT_local_1shot_T2_n140_v2.json

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r004_lasot_attention_pilot.py --n 10 --max-side 224

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-004-lasot-iplocid-attention-pilot-n10/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-004-lasot-iplocid-attention-pilot-n10/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-004-lasot-iplocid-attention-pilot-n10

### tmux session
e005_lasot_pilot

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-004-lasot-iplocid-attention-pilot-n10
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-004-lasot-iplocid-attention-pilot-n10/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-004-lasot-iplocid-attention-pilot-n10/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-004-lasot-iplocid-attention-pilot-n10/metrics.json
- tmux_session: e005_lasot_pilot
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T15:21:13
- updated: 2026-07-24T15:22:34

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
