# E005-R-034d-qr-continuous-threshold-curve-offline-640 · final frozen Q→R continuous threshold fIoU analysis

- canonical_run_id: `E005-R-034d-qr-continuous-threshold-curve-offline-640`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed_integrity_inference_only

## 本轮目的
检验strict hit是否遗漏Q→R distributed reference-target attention signal。

## 必要性 / 证据链位置
避免按单一argmax/enrichment阈值否定Q→R信息。

## 研究依据 / 被审计对象
冻结R027/R028/R029c per-record raw metrics与R028 fIoU curves。

## 实现方式（简版）
纯离线；固定7个τ、4个coverage、density-only/plus-pointing、ECDF/ROC、pair/cluster bootstrap B10000。

## 实现方式（详细版）
无最佳阈值选择；R028 pair、R027 sequence cluster；新增Spearman bootstrap CI。

## 数据身份与构造
R027 error48/correct177；R028 matched35x2；R029c error35/correct76；partial仅连续IoU关联。

## 数据规模
406 accepted-extreme records across analyses; no new forward

## 模型、权重与关键配置
offline saved max_side640 metrics

## 变量、干预与对照
samples/heads/outputs/threshold grid冻结；seed20260728

## 指标与计数规则
Q→R fractional target mass；enrichment threshold curves；pointing；ROC/AP；retained-mass merged-token fIoU AUC。

## 完整性门槛 / no-silent-zero
complete JSON,2 figures,B10000,exit0; no best cutoff

## 观测结果摘要
Q→R mass：R027 diff+.0384 CI[-.0054,.0853],AUC.645 CI[.522,.762],rho-IoU.259 CI[.114,.385]；R028 paired+.03230 CI[.00604,.08811],26/35正,sign p=.00599,AUC.617；R029c diff+.08133 CI[.02409,.11570],AUC.708 CI[.594,.812],rho.344 CI[.180,.494]。Enrichment/pointing不稳定。640 fIoU-AUC matched all n35 diff=.04848 CI[.00769,.07722],coverage>=4 n26=.05262 CI[.01333,.07992]。

## 局限与混杂因素
attention非因果；teacher replay；threshold CIs无多重校正；R027 multiframe cluster；fIoU仅R028。

## 可支持的结论
strict-hit会遗漏distributed Q→R budget；absolute target mass优于enrichment/pointing和D_abs，但只是中等行为关联，非因果。

## 不支持的结论 / Claim 边界
absolute Q→R mass含中等行为关联；不证明causal binding/identity selectivity；D_abs仍不稳定。

## 关键指标
（待补充）

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-034d-qr-continuous-threshold-curve-offline-640/analysis/detailed_statistics.json; shell/06_experiments/E-005/qr_continuous_curve_analysis_R034d.md; shell/06_experiments/E-005/visualizations/R-034d/

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
/tmp/e005_r034d_qr.py

### 配置/超参数
（待补充）

### Seed
20260728

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-034d-qr-continuous-threshold-curve-offline-640/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-034d-qr-continuous-threshold-curve-offline-640/analysis

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-034d-qr-continuous-threshold-curve-offline-640

### tmux session
（待补充）

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-034d-qr-continuous-threshold-curve-offline-640
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-034d-qr-continuous-threshold-curve-offline-640/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-034d-qr-continuous-threshold-curve-offline-640/analysis
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-034d-qr-continuous-threshold-curve-offline-640/metrics.json
- tmux_session: incontext-E-005-E005-R-034d-qr-continuous-threshold-curve-offline-640
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-28T23:12:15
- updated: 2026-07-28T23:12:15

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
