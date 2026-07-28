# E005-R-009-prompt-image-token-attention-budget-n20 · prompt图像token多query attention-budget audit n20

- canonical_run_id: `E005-R-009-prompt-image-token-attention-budget-n20`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
aborted_by_user_protocol_reorder

## 本轮目的
回到核心问题：测量模型在IPLoc-ID prompt中对reference/query图像tokens和其他prompt区域的attention分配与正负选择性。

## 必要性 / 证据链位置
R-006/R-008说明bbox readout失败，但不能回答图像token是否被低配或缺乏身份选择性。

## 研究依据 / 被审计对象
用户重申目标为图像token attention机制；R-002c证实eager full attention可行。

## 实现方式（简版）
对20 paired positive/negative prompts采集完整36层attention；分析post-query suffix、last token和query-image-token rows到五类prompt key区域的mass与uniform enrichment。

## 实现方式（详细版）
key groups=reference image、query image、reference前text/special、两图间text/special、query后text/special；paired positive-negative delta；不做bbox选头。

## 数据身份与构造
LaSOT/IPLoc-ID local deterministic indices0:19；不使用COCO。

## 数据规模
20 samples、40 prompts、3 query groups×5 key groups×36×32。

## 模型、权重与关键配置
Qwen3-VL-8B+IPLoc-ID LoRA；eager bf16；224。

## 变量、干预与对照
positive与same-class negative共享reference；严格span gate；raw mass和按causal uniform期望enrichment同时报告。

## 指标与计数规则
attention mass、uniform enrichment、layer profile、paired positive-negative delta。

## 完整性门槛 / no-silent-zero
40 prompts；36×32 full QK finite；双图span匹配；exit0。

## 观测结果摘要
用户明确要求先验证论文方法找到的heads是否在GT附近并进行可视化；attention-budget阶段主动停止。

## 局限与混杂因素
attention不是value contribution或因果；初始text分组按位置而非语义token；低分辨率非官方split。

## 可支持的结论
无科学输出；attention-budget保留为head-quality gate通过后的后续阶段。

## 不支持的结论 / Claim 边界
只描述prompt-level attention allocation与选择性，不把低attention直接等同信息未使用。

## 关键指标
停止时仍在模型加载；KeyboardInterrupt；0有效prompt结果。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-009-prompt-image-token-attention-budget-n20; /home/featurize/data/e002_manifests/LASOT_local_1shot_T2_n140_v2.json

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r009_attention_budget.py --start0 --n20

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-009-prompt-image-token-attention-budget-n20/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-009-prompt-image-token-attention-budget-n20/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-009-prompt-image-token-attention-budget-n20

### tmux session
e005_attention_budget

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-009-prompt-image-token-attention-budget-n20
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-009-prompt-image-token-attention-budget-n20/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-009-prompt-image-token-attention-budget-n20/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-009-prompt-image-token-attention-budget-n20/metrics.json
- tmux_session: e005_attention_budget
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T16:00:35
- updated: 2026-07-24T16:01:14

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
