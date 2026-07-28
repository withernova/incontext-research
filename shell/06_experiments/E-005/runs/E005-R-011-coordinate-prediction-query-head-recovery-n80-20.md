# E005-R-011-coordinate-prediction-query-head-recovery-n80-20 · teacher-forced coordinate-prediction query head recovery n80+20

- canonical_run_id: `E005-R-011-coordinate-prediction-query-head-recovery-n80-20`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
failed_alignment_gate

## 本轮目的
纠正newline query：从实际预测gold bbox坐标token的前一位置attention rows发现并审核定位heads。

## 必要性 / 证据链位置
R-010/R-010b确认last token是newline且产生系统性边缘模式。

## 研究依据 / 被审计对象
真实生成格式为[bbox], Do all these boxes have the same object? Yes/No；自回归row t预测token t+1。

## 实现方式（简版）
indices0:79 positive query上按每个gold bbox token前一row的均值运行repo-original top5频率发现；冻结heads后在80:99做GT enrichment/all-head control/turbo图。

## 实现方式（详细版）
teacher-forced完整gold answer；offset mapping严格定位bbox字符覆盖tokens；off-by-one为p-1；双图span严格审计。

## 数据身份与构造
local deterministic LaSOT/IPLoc-ID positive query；discovery0:79，internal validation80:99。

## 数据规模
80 discovery+20 validation；10组turbo图。

## 模型、权重与关键配置
Qwen3-VL+IPLoc-ID LoRA eager bf16 224。

## 变量、干预与对照
GT只用于teacher-forced query定义和validation评分，不用于repo selection ranking；固定split；all1152-head matched control。

## 指标与计数规则
repo selection frequency；GT enrichment；pointing；all-head percentile；combined map。

## 完整性门槛 / no-silent-zero
chat prefix、token offset、p-1 alignment、span/grid/finite；三项head-quality gates。

## 观测结果摘要
首次运行在首样本processor/tokenizer完整ID比较门禁失败；multimodal processor会展开image_pad，因此该比较定义不成立。

## 局限与混杂因素
post-hoc recovery；teacher-forced exposure；已有indices；非confirmatory；attention非因果。

## 可支持的结论
无科学输出；不是模型或span失败。R-011b改为在展开后input_ids中唯一精确匹配gold bbox token子序列。

## 不支持的结论 / Claim 边界
仅判断coordinate-prediction query是否能恢复合理定位heads；通过后仍需新未使用序列确认。

## 关键指标
0 discovery samples；exit1；ValueError processor/tokenizer id mismatch。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-011-coordinate-prediction-query-head-recovery-n80-20; /home/featurize/data/e002_manifests/LASOT_local_1shot_T2_n140_v2.json

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r011_coord_query_recovery.py --disc-n80 --val20

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-011-coordinate-prediction-query-head-recovery-n80-20/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-011-coordinate-prediction-query-head-recovery-n80-20/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-011-coordinate-prediction-query-head-recovery-n80-20

### tmux session
e005_coord_recovery

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-011-coordinate-prediction-query-head-recovery-n80-20
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-011-coordinate-prediction-query-head-recovery-n80-20/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-011-coordinate-prediction-query-head-recovery-n80-20/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-011-coordinate-prediction-query-head-recovery-n80-20/metrics.json
- tmux_session: e005_coord_recovery
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T16:17:11
- updated: 2026-07-24T16:18:56

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
