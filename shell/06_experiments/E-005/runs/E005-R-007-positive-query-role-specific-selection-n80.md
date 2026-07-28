# E005-R-007-positive-query-role-specific-selection-n80 · R-006后post-hoc positive-query role-specific selection

- canonical_run_id: `E005-R-007-positive-query-role-specific-selection-n80`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
failed_schema_key

## 本轮目的
诊断总体四role频率混合是否导致R-006 grounding失败。

## 必要性 / 证据链位置
R-006 frozen overall heads失败；不能在已暴露held-out上重选，故仅拆分原discovery indices0:79选择并保留80:99内部验证。

## 研究依据 / 被审计对象
R-006 positive-query mIoU=0.03394；R-005保存每record top5。

## 实现方式（简版）
离线过滤R-005 indices0:79的positive:query records，按top5出现频率固定5 heads。

## 实现方式（详细版）
不加载模型；indices80:99不参与选择；100:139已暴露，明确禁止作为新confirmatory held-out。

## 数据身份与构造
R-005 discovery records；selection indices0:79。

## 数据规模
80 positive-query records。

## 模型、权重与关键配置
离线分析。

## 变量、干预与对照
只用positive-query role；top_k5；split先于本诊断运行固定。

## 指标与计数规则
head selection frequency。

## 完整性门槛 / no-silent-zero
80 records且输出5 fixed heads。

## 观测结果摘要
离线脚本预期global_index，但R-005 records字段为sample_index，运行失败。

## 局限与混杂因素
R-006后post-hoc recovery diagnostic；非预注册confirmatory。

## 可支持的结论
纯schema错误，保留失败run并在R-007b显式兼容sample_index。

## 不支持的结论 / Claim 边界
只为indices80:99内部诊断提供固定候选，不能修正或覆盖R-006负结果。

## 关键指标
KeyError: global_index；模型未加载；无科学输出。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-007-positive-query-role-specific-selection-n80; /home/featurize/work/mechanism/explog/E-005/runs/E005-R-005-lasot-iplocid-attention-discovery-n100/results/attention_records.json

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r007_role_specific_select.py --train-end 80 --top-k 5

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-007-positive-query-role-specific-selection-n80/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-007-positive-query-role-specific-selection-n80/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-007-positive-query-role-specific-selection-n80

### tmux session
e005_role_select

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-007-positive-query-role-specific-selection-n80
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-007-positive-query-role-specific-selection-n80/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-007-positive-query-role-specific-selection-n80/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-007-positive-query-role-specific-selection-n80/metrics.json
- tmux_session: e005_role_select
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T15:33:23
- updated: 2026-07-24T15:33:40

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
