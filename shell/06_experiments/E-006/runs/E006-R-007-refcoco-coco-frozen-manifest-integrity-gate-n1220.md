# E006-R-007-refcoco-coco-frozen-manifest-integrity-gate-n1220 · RefCOCO primary and optional filtered COCO-val proxy manifest gate

- canonical_run_id: `E006-R-007-refcoco-coco-frozen-manifest-integrity-gate-n1220`
- run_type: data_gate
- review_status: approved
- review_round: 2
- submitted_for_review_at: 2026-08-03T15:17:11
- approved_at: 2026-08-03T15:21:31
- execution_authorized_at: 2026-08-03T15:21:43
- execution_authorization_consumed_at: 2026-08-03T15:47:35
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
completed

## 本轮目的
使用服务器现有完整COCO资产构建RefCOCO expression-sample冻结manifest，不再下载COCO。

## 必要性 / 证据链位置
为可选Qwen-only RefCOCO外部空间正对照提供anti-leakage数据；纠正此前把1220误写成unique images。

## 研究依据 / 被审计对象
LocalizationHeads README仅声明RefCOCO train的1000 data samples，未公开sample IDs或unique-image要求。

## 实现方式（简版）
只读定位/home/featurize/data现有COCO；映射RefCOCO metadata；20/1000/200 expression samples按COCO image_id group split。

## 实现方式（详细版）
记录实际COCO路径/年份/图数和RefCOCO revision/hash；优先每image抽一条expression；若split内复用image则按image聚类且绝不跨split。

## 数据身份与构造
RefCOCO UNC train referring-expression samples + 用户已下载到服务器data目录的COCO images；n单位为expression sample。

## 数据规模
20 pilot + 1000 discovery + 200 confirmation = 1220 RefCOCO samples；不是原论文规定的1220 unique images。

## 模型、权重与关键配置
无模型；本run为只读数据gate，不联网下载。

## 变量、干预与对照
seed/revision冻结；split grouping key=COCO image_id；image_id跨split overlap=0。

## 指标与计数规则
sample/ref/ann/image IDs、valid/missing、image decode/size、bbox、expression、split image overlap、每图expression数。

## 完整性门槛 / no-silent-zero
1220/1220合法；所有本地图可解码；bbox/expression合法；三split image_id overlap=0；0 silent missing。

## 竞争假设与预期特征
得到可审计Qwen RefCOCO manifest；unique-image是本地防泄漏约束而非论文明示规则。

## 验收条件
若现有COCO缺所需年份/图片则报告缺口并停止，不自动下载。

## 依赖的 Run / 证据
服务器/home/featurize/data现有COCO；RefCOCO metadata。

## 观测结果摘要
原授权只读gate已完成并按预注册停止：GATE_STOP MISSING_REFCOCO_METADATA,MISSING_COCO2014_IMAGES；当时未下载/解包。之后用户另行授权获得metadata并提供train2014.zip，但这些新资产不能追写为原run通过。

## 局限与混杂因素
作者精确1000 subset与采样单位未公开；本地group split不是exact-paper split。

## 可支持的结论
该run仅证明执行当时资产不足；不是当前数据完整性结论。当前新资产必须用新canonical recovery gate验证。

## 不支持的结论 / Claim 边界
只支持数据完整性和anti-leakage，不构成方法复现。

## 关键指标
{"gate":"GATE_STOP","read_only":true,"network_downloads":0,"files_extracted":0,"blockers":["MISSING_REFCOCO_METADATA","MISSING_COCO2014_IMAGES"]}

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-006/followup_validity_and_equivariance_plan.md#r-007

## 过程记录与补充细节
（待补充）

## Run 审核
### 用户补充要求
我已经在服务器的 data 下面下载了完整的 coco 数据集了
### 用户疑问
什么叫 uniqueimage，是原论文的吗
### Agent 完善说明
已采纳：不再下载COCO；将n1220明确改为RefCOCO expression samples。unique-image不是公开原文要求，而是防同一COCO图像跨discovery/confirmation泄漏的本地设计；实现改为按image_id group split。
### Agent 对疑问的回应
请确认：是否同意保留20/1000/200 samples并以image_id跨split不重叠作为本地防泄漏约束？
### 本次执行授权备注
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
20260724

### 日志路径
（待补充）

### 产物目录
（待补充）

### 真实产物根目录
（待补充）

### tmux session
（待补充）

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-006
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-007-refcoco-coco-frozen-manifest-integrity-gate-n1220
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-007-refcoco-coco-frozen-manifest-integrity-gate-n1220/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-007-refcoco-coco-frozen-manifest-integrity-gate-n1220/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-007-refcoco-coco-frozen-manifest-integrity-gate-n1220/metrics.json
- tmux_session: incontext-E-006-E006-R-007-refcoco-coco-frozen-manifest-integrity-gate-n1220
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-03T14:54:20
- updated: 2026-08-03T22:01:13

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
