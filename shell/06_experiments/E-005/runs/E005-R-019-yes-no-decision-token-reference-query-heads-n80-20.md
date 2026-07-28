# E005-R-019-yes-no-decision-token-reference-query-heads-n80-20 · Yes/No decision-token reference/query attention heads n80+20

- canonical_run_id: `E005-R-019-yes-no-decision-token-reference-query-heads-n80-20`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
failed_control_flow_before_first_forward

## 本轮目的
分析最终身份判断Yes/No token的p-1 row分别关注reference/query哪些tokens和heads。

## 必要性 / 证据链位置
localization与identity decision需分离；用户要求重新按方法选择decision heads。

## 研究依据 / 被审计对象
assistant响应在bbox与判断问题后生成gold Yes/No；decision p-1 row可读取完整双图及teacher-forced bbox历史。

## 实现方式（简版）
positive gold Yes/negative gold No；decision p-1 row→reference/query spans分别repo排名；两condition pooled discovery，validation分condition/side。

## 实现方式（详细版）
字符offset+expanded processor regional exact match；记录每selected head对reference/query/other历史的raw attention budget；与三类head registry比较。

## 数据身份与构造
旧manifest0:79 discovery，每样本positive+negative；80:99 validation。

## 数据规模
160 discovery prompts；40 validation prompts×2 spans×2 head sets。

## 模型、权重与关键配置
Qwen3-VL+IPLoc-ID LoRA eager bf16 224 original prompt order。

## 变量、干预与对照
Yes/No gold；reference/query独立selection；all1152-head controls；condition frequency分开报告。

## 指标与计数规则
object GT enrichment/pointing/percentile；raw reference/query/other mass；head overlap。

## 完整性门槛 / no-silent-zero
decision regional exact match；p-1；span/grid/finite/budget sum；positive/negative分开质量。

## 观测结果摘要
首样本在forward前因dids赋值误落入单行if suite而UnboundLocalError；无排名、指标或科学输出。

## 局限与混杂因素
decision前已teacher-force query bbox；gold decision；post-hoc；attention非因果；正负target图不同。

## 可支持的结论
无科学结论；仅记录实现失败。

## 不支持的结论 / Claim 边界
identity-decision attention signature，不等于因果判别heads或纯视觉identity evidence。

## 关键指标
completed prompts=0；exit=1。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-019-yes-no-decision-token-reference-query-heads-n80-20

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r019_decision_token_heads.py

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-019-yes-no-decision-token-reference-query-heads-n80-20/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-019-yes-no-decision-token-reference-query-heads-n80-20/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-019-yes-no-decision-token-reference-query-heads-n80-20

### tmux session
e005_decision

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-019-yes-no-decision-token-reference-query-heads-n80-20
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-019-yes-no-decision-token-reference-query-heads-n80-20/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-019-yes-no-decision-token-reference-query-heads-n80-20/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-019-yes-no-decision-token-reference-query-heads-n80-20/metrics.json
- tmux_session: e005_decision
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T18:14:07
- updated: 2026-07-24T18:15:18

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
