# E005-R-027-binding-discrepancy-unseen-multiframe-n280-640 · same-resolution binding discrepancy n280 max_side640

- canonical_run_id: `E005-R-027-binding-discrepancy-unseen-multiframe-n280-640`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed_integrity

## 本轮目的
在更大样本上验证accepted localization errors是否具有更大的G→R与Q→R reference-target attention discrepancy。

## 必要性 / 证据链位置
扩大R-023 pilot并消除640生成到224 replay分辨率混杂。

## 研究依据 / 被审计对象
R-023冻结heads与p-1对齐；R-026自然输出；不预选组别。

## 实现方式（简版）
对可对齐自然bbox输出进行640 teacher replay；计算target mass logit gap、JSD、coverage、IoU与sequence-cluster bootstrap。

## 实现方式（详细版）
max_side640；双RTX4090；串行workflow仅在R-025 smoke通过后推进。

## 数据身份与构造
R-024：70 old-development-disjoint sequences×4 query frames，positive-only；重用R014 sequences；非官方split。

## 数据规模
n280/70 sequence clusters

## 模型、权重与关键配置
persistent Qwen3-VL-8B+IPLoc LoRA bf16 dual RTX4090 max_side640

## 变量、干预与对照
frozen heads/thresholds；sequence-cluster bootstrap；不自动降分辨率

## 指标与计数规则
R026: natural IoU/groups；R027: absolute logit target-mass gap error-vs-correct、Spearman IoU、cluster bootstrap

## 完整性门槛 / no-silent-zero
R026 exactly280 outputs；R027 records+unalignable=280, records>=200, finite, bootstrap>=9500

## 观测结果摘要
280/280 aligned; error48 correct177 middle45 rejected10. Primary absolute-gap median error1.567 vs correct1.304, difference+.263, sequence-cluster CI[-.348,.987]. Spearman vs IoU rho=-.0374,p=.576,n225. coverage median8 tokens, ge4=248/280.

## 局限与混杂因素
positive-only；四query/sequence相关；R014 sequence reuse；attention非因果；论文未披露max_side

## 可支持的结论
同分辨率扩大验证未稳定支持absolute target-mass logit discrepancy与定位IoU关系；方向性中位数差异CI跨0且连续相关近0。

## 不支持的结论 / Claim 边界
只验证定位错误相关binding discrepancy，不证明identity或因果。

## 关键指标
（待补充）

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-027-binding-discrepancy-unseen-multiframe-n280-640

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_n280_640_workflow.sh

### 配置/超参数
（待补充）

### Seed
20260728

### 日志路径
/home/featurize/work/mechanism/explog/E-005/e005_n280_640_workflow.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-027-binding-discrepancy-unseen-multiframe-n280-640/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-027-binding-discrepancy-unseen-multiframe-n280-640

### tmux session
e005_n280_640

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-027-binding-discrepancy-unseen-multiframe-n280-640
- log_file: /home/featurize/work/mechanism/explog/E-005/e005_n280_640_workflow.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-027-binding-discrepancy-unseen-multiframe-n280-640/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-027-binding-discrepancy-unseen-multiframe-n280-640/metrics.json
- tmux_session: e005_n280_640
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-28T20:16:41
- updated: 2026-07-28T21:01:08

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
