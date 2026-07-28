# E005-R-010-frozen-head-gt-concentration-viz-audit-n40 · 冻结论文方法heads的GT concentration与可视化审计

- canonical_run_id: `E005-R-010-frozen-head-gt-concentration-viz-audit-n40`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_failed_quality_gate

## 本轮目的
在进入prompt attention-budget分析前，先验证repo方法找到的heads是否把高attention集中在GT附近，并提供未按结果挑选的可视化供人工审核。

## 必要性 / 证据链位置
用户要求重排主链：head quality gate必须先于图像token/prompt attention机制分析；bbox mIoU可能受后处理影响，需直接审计attention map。

## 研究依据 / 被审计对象
R-005冻结top5；R-006 bbox读出弱但未直接测GT attention concentration。

## 实现方式（简版）
对indices100:139 positive query逐head测GT soft mass/enrichment、argmax pointing、GT距离，并与同prompt全部1152 heads比较；前10固定样本输出六panel heatmap。

## 实现方式（详细版）
五个冻结heads+sigma1 combined；GT overlap按矩形grid cell与bbox面积精确加权；可视化样本按index固定，不按结果挑选。

## 数据身份与构造
自有LaSOT/IPLoc-ID local deterministic indices100:139 positive query；不使用COCO。

## 数据规模
40 samples×5 selected heads；同prompt 1152-head controls；10组六panel图。

## 模型、权重与关键配置
Qwen3-VL-8B+IPLoc-ID LoRA；last input token；eager bf16；224。

## 变量、干预与对照
heads来自R-005且冻结；GT不参与head selection；all-head same-prompt matched control；fixed visualization indices。

## 指标与计数规则
GT soft mass、GT area-normalized enrichment、pointing hit、argmax normalized distance、all-head percentile。

## 完整性门槛 / no-silent-zero
selected median enrichment>1；median all-head percentile>=0.75；selected pointing rate>all-head control；40 records finite和shape通过。

## 观测结果摘要
冻结repo-method top5的直接GT concentration审计完成；40/40工程门禁通过，但3项head-quality gates全部失败，已生成10组固定样本heatmaps。

## 局限与混杂因素
已暴露R-006 set用于方法审计而非新confirmatory结果；last-token only；低分辨率；attention非因果。

## 可支持的结论
当前last-input-token + repo-original selection在本任务上选出的heads不合理：其GT attention密度低于按面积均匀基线，且位于全部heads的低分位，argmax从未落入GT。不能据此推进这些heads上的prompt attention机制结论；需先修正query位置/选择协议。

## 不支持的结论 / Claim 边界
只有quality gate通过才推进attention-budget主分析；失败则说明当前论文代码移植未找到优质定位heads，需修正query定义或方法。

## 关键指标
selected head-sample n=200；median GT enrichment=0.107；mean=0.197；pointing hit=0/200；median all-head percentile=0.0924；all-head control pointing=0.0502；combined median enrichment=0.114；combined pointing=0/40；quality gates=0/3。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-010-frozen-head-gt-concentration-viz-audit-n40; /home/featurize/work/mechanism/explog/E-005/runs/E005-R-005-lasot-iplocid-attention-discovery-n100/analysis/summary.json; /home/featurize/data/e002_manifests/LASOT_local_1shot_T2_n140_v2.json

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r010_head_gt_audit.py --start100 --n40 --viz-n10

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-010-frozen-head-gt-concentration-viz-audit-n40/logs/run.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-010-frozen-head-gt-concentration-viz-audit-n40/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-010-frozen-head-gt-concentration-viz-audit-n40

### tmux session
e005_gt_audit

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-010-frozen-head-gt-concentration-viz-audit-n40
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-010-frozen-head-gt-concentration-viz-audit-n40/logs/run.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-010-frozen-head-gt-concentration-viz-audit-n40/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-010-frozen-head-gt-concentration-viz-audit-n40/metrics.json
- tmux_session: e005_gt_audit
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T16:03:14
- updated: 2026-07-24T16:04:52

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
