# E007-R-001-frozen-source-map-and-online-window-alignment-gate-n20 · frozen-source-map-and-online-window-alignment-gate-n20

- canonical_run_id: `E007-R-001-frozen-source-map-and-online-window-alignment-gate-n20`
- run_type: implementation_gate
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-04T20:44:51
- approved_at: 2026-08-04T20:46:37
- execution_authorized_at: 2026-08-04T20:46:38
- execution_authorization_consumed_at: 2026-08-04T20:57:36
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
planned

## 本轮目的
冻结source reference-grounding maps、target query heads和在线自然生成干预窗口；验证teacher-replay exact bbox rows与可在线实现的generation window之间的关系，避免使用未来bbox信息。

## 必要性 / 证据链位置
自然生成时不能预知未来bbox token位置。必须预先定义可因果在线触发的窗口，并确认source map在生成前已可由prompt计算。

## 研究依据 / 被审计对象
G→R定义为reference bbox input token p-1 rows→reference keys；这些rows位于prompt内，可在生成前缓存。Q→R bbox rows在自然输出后才精确可知。R006验证row t预测token t+1。

## 实现方式（简版）
n20 sequence-unique positives：缓存historical G→R source maps；冻结source heads L15H13,L16H23,L18H15，target main4 L18H15,L19H03,L22H00,L20H08。对自然生成记录first-step到首个完整bbox结束的online-causal window，并与事后exact bbox p-1 rows比较。

## 实现方式（详细版）
source map按每source head、reference bbox prompt rows平均，再跨source heads等权平均并normalize于reference span。Primary online window从first generated prediction row启用，到streaming parser检测首个合法bbox闭括号后关闭，包含JSON/格式token；exact-bbox-only仅teacher-forced diagnostic，不用于natural primary。保存每token/window state。

## 数据身份与构造
从E003-R-004b positives按sequence hash冻结10 localization-error+10 localization-correct，sequence unique；不按干预结果选择。使用原图、原prompt、原LoRA、原natural generation。

## 数据规模
n=20 baseline generation+teacher replay，不做科学transplant效果测试。

## 模型、权重与关键配置
原IPLoc-ID LoRA，bf16 eager，max_side=640，do_sample=False，原generation settings。

## 变量、干预与对照
source head maps per-head与aggregate；target main4；online window vs exact bbox rows；last-input/first-step alignment control。

## 指标与计数规则
source map finite/coverage/budget；online window长度；exact bbox rows被window覆盖率；window额外token数；parse/Yes；forward-generate first-step max diff。

## 完整性门槛 / no-silent-zero
20/20 source exact unique rows；20/20 two image spans；>=18/20 natural parse；所有exact bbox p-1 rows必须被online window覆盖；在线触发不读取未来tokens；source map只来自prompt；若不满足停止自然run并仅保留teacher-forced路线。

## 竞争假设与预期特征
online first-step→bbox-close覆盖exact bbox rows但包含额外格式rows；若覆盖失败，需新run设计state machine。

## 验收条件
冻结manifest、source/target lists、token/window逐样本审计和GATE_PASS/STOP。

## 依赖的 Run / 证据
E007-R-000必须通过；E003-R-004b outputs；E006-R-006。

## 观测结果摘要
（待补充）

## 局限与混杂因素
窗口比exact bbox rows宽；source map可能主要编码显式reference bbox/container。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
只建立自然生成干预的因果可执行性，不测试行为改善。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-005/dual_gpu_640_core_results.md; shell/06_experiments/E-006/runs/E006-R-006-exact-last-token-bbox-row-alignment-gate-n10-640.md

## 过程记录与补充细节
（待补充）

## Run 审核
### 用户补充要求
（待补充）
### 用户疑问
（待补充）
### Agent 完善说明
（待补充）
### Agent 对疑问的回应
（待补充）
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
20260804

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
- project_dir: /home/featurize/work/mechanism/E-007
- run_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-001-frozen-source-map-and-online-window-alignment-gate-n20
- log_file: /home/featurize/work/mechanism/explog/E-007/E007-R-001-frozen-source-map-and-online-window-alignment-gate-n20/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-001-frozen-source-map-and-online-window-alignment-gate-n20/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-007/E007-R-001-frozen-source-map-and-online-window-alignment-gate-n20/metrics.json
- tmux_session: incontext-E-007-E007-R-001-frozen-source-map-and-online-window-alignment-gate-n20
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-04T20:44:43
- updated: 2026-08-04T20:57:36

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
