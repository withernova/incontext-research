# E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20 · E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20

- canonical_run_id: `E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20`
- legacy_registry_ids: R-011

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
failed

## 本轮目的
在 forced assistant candidate prefix 后比较 next-token Yes/No logits，测试 verifier 对 candidate region 的响应。

## 必要性 / 证据链位置
Joint F1只能证明输出口径解耦，不能判断final verifier是否读取candidate；forced-candidate用于诊断p(A|x,B,Q)对B的响应。

## 研究依据 / 被审计对象
论文按p(A|x,B,Q)描述identification，bbox是待验证candidate。[[personal2026]] §3.3.1。

## 实现方式（简版）
20 positive + 20 same-class negative；每个target六种candidate modes；记录Yes-No margin与two-token normalized probability。

## 实现方式（详细版）
candidate+question插入assistant autoregressive history；不用自由文本parser或PN_interpreter bbox fallback。实际输出写出后，role-specific integrity assertion实现错误导致traceback。

## 数据身份与构造
同一manifest前20samples；每个reference共享positive与same-class negative target；每target六candidate modes；本地reconstruction非官方split。

## 数据规模
前20 manifest samples；240 records；实际12个role/mode cell各20条；logits全部finite。

## 模型、权重与关键配置
同R-004b模型/LoRA/offline snapshot；assistant autoregressive forced prefix；single-token Yes/No IDs现场记录；不自由生成decision。

## 变量、干预与对照
固定reference/query，只改变candidate：generated、annotated target/distractor、shifted、background matched-size、contracted50%、expanded150%。

## 指标与计数规则
M=logit(Yes)-logit(No)；yes_pair_probability仅在Yes/No两token间归一化。计划paired mode margins/flip rates；不是calibrated full-vocabulary probability。

## 完整性门槛 / no-silent-zero
240 records；20 per actual role/mode cell；positive用annotated_target、negative用annotated_distractor；all logits finite；traceback=0；formal analysis exists。该run最后两项失败。

## 观测结果摘要
写出240条finite records，但日志末尾AssertionError；没有正式analysis summary。失败来自gate错误要求positive-image/annotated_distractor，实际positive mode为annotated_target。

## 局限与混杂因素
forced prefix exposure shift；n20；candidate boxes是bbox proxy；日志末尾AssertionError且无formal analysis。

## 可支持的结论
failed_post_output_integrity_assertion / analysis incomplete；不得将初步margin作为正式科学结果。修复后必须使用新canonical run ID。

## 不支持的结论 / Claim 边界
当前run不得引用科学margin；只能支持实现已写出240 finite records并暴露role-specific gate bug。修复必须新run ID。

## 关键指标
{"records_written":240,"finite_logits":true,"actual_role_mode_cells":12,"records_per_actual_cell":20,"traceback":true,"formal_analysis":false}

## 审核入口
config/run.md；logs/run.log；results/forced_candidate_outputs.json；analysis缺失。

## 过程记录与补充细节
canonical_run_id=E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20；registry自动ID仅为工具映射。prefix-conditioned verifier probe；存在exposure shift；yes_pair_probability不是全词表校准概率。local_note=shell/06_experiments/E-003/runs/E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20.md。

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
bash /home/featurize/work/mechanism/scripts/e002/e002_r018_forced_candidate_verifier.sh

### 配置/超参数
（待补充）

### Seed
0

### 日志路径
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20

### tmux session
（待补充）

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-003
- run_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20
- log_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20
- metrics_file: /home/featurize/work/mechanism/explog/E-003/runs/E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20/metrics.json
- tmux_session: incontext-E-003-E003-R-005e-forced-candidate-logit-verifier-local-lasot-n20
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-20T17:16:20+08:00
- updated: 2026-07-20T17:43:37

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
