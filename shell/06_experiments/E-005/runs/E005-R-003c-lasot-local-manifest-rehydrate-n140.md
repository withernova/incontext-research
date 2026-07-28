# E005-R-003c-lasot-local-manifest-rehydrate-n140 · 自有LaSOT/IPLoc-ID任务数据恢复

- canonical_run_id: `E005-R-003c-lasot-local-manifest-rehydrate-n140`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed

## 本轮目的
恢复E-005任务内主数据manifest，后续直接在reference+positive/negative query协议上做attention head pilot。

## 必要性 / 证据链位置
用户决定停止RefCOCO路线，优先使用自有IPL oc-ID/LaSOT数据；服务器重启后data symlink和manifest丢失。

## 研究依据 / 被审计对象
持久化/home/featurize/LaSOTTesting现有280 sequences、685360 jpg、280 annotations、49GB；沿用已审计E003-R-001确定性重建规则。

## 实现方式（简版）
重建/home/featurize/data/LaSOTTesting symlink并运行审计过的manifest构造器；reference=目标首帧、positive=目标末帧、negative=同类另一sequence中帧。

## 实现方式（详细版）
脚本快照归档到本run；仅将RUN输出路径重定向到E-005，manifest路径保持LASOT_local_1shot_T2_n140_v2.json。

## 数据身份与构造
本地LaSOTTesting确定性POIL reconstruction，非官方IPL oc-ID split。

## 数据规模
目标140 samples/70 classes，140 positive+140 same-class negative，420图像引用。

## 模型、权重与关键配置
无模型，数据完整性gate。

## 变量、干预与对照
确定性排序；每类最多两个directed samples；不使用COCO数据。

## 指标与计数规则
samples/classes/positive/negative/missing/invalid_bbox。

## 完整性门槛 / no-silent-zero
140/70/140/140，missing=0，invalid_bbox=0。

## 观测结果摘要
自有LaSOT/IPLoc-ID任务manifest恢复成功；完整性门禁全部通过。

## 局限与混杂因素
非作者官方split；首/末/中帧是本地确定性近似。

## 可支持的结论
现在可直接启动自有任务数据的E-005小pilot；manifest仍是本地确定性reconstruction，非官方split。

## 不支持的结论 / Claim 边界
只支持自有任务数据链恢复；通过后启动独立pilot，不能称官方复现。

## 关键指标
samples=140; classes=70; positive=140; same-class negative=140; image references=420; missing=0; invalid_bbox=0; skipped=0。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-003c-lasot-local-manifest-rehydrate-n140; /home/featurize/LaSOTTesting; /home/featurize/data/e002_manifests/LASOT_local_1shot_T2_n140_v2.json

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-003c-lasot-local-manifest-rehydrate-n140/config/rehydrate_manifest.py

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-003c-lasot-local-manifest-rehydrate-n140/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-003c-lasot-local-manifest-rehydrate-n140/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-003c-lasot-local-manifest-rehydrate-n140

### tmux session
e005_lasot_rehydrate

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-003c-lasot-local-manifest-rehydrate-n140
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-003c-lasot-local-manifest-rehydrate-n140/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-003c-lasot-local-manifest-rehydrate-n140/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-003c-lasot-local-manifest-rehydrate-n140/metrics.json
- tmux_session: e005_lasot_rehydrate
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T15:15:18
- updated: 2026-07-24T15:15:48

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
