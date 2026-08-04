# E006-R-005-simple-top50-support-components-positive-extremes-n111-640 · fixed top50 support per-head GtoR QtoR QtoQ

- canonical_run_id: `E006-R-005-simple-top50-support-components-positive-extremes-n111-640`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed_integrity_inference_only

## 本轮目的
用直观support hit、majority和4邻域components比较error/correct。

## 必要性 / 证据链位置
替代难解释的discrepancy/连续阈值堆叠。

## 研究依据 / 被审计对象
E003原始positive archived natural outputs；冻结E005 heads。

## 实现方式（简版）
每个head先在目标image span内条件归一化，再按attention降序取累计质量达到>=.5的最小merged-token集合S50；在grid上做4邻域components。注意不是取数量前50%的tokens，也不是全序列attention的50%。

## 实现方式（详细版）
对bbox文本全部精确token位置使用p-1 rows并逐key均值；G→R用reference bbox rows/reference keys，Q→R用natural-query bbox rows/reference keys，Q→Q用natural-query bbox rows/query keys。令p_i=max(a_i,0)/sum_image max(a_j,0)，k*=min{k:sum_{j<=k}p_(j)>=.5}，stable降序；最后token导致selected mass可>.5。GT用merged-cell fractional occupancy。4-neighbor仅上下左右；largest按token数，平局取扫描序首个。

## 数据身份与构造
positive natural Yes；IoU<.1 error35；IoU>=.7 correct76。

## 数据规模
111 forwards,1221 head maps,111 figures

## 模型、权重与关键配置
Qwen3-VL-8B+IPLoc-ID LoRA bf16 eager max_side640 dual4090

## 变量、干预与对照
固定support mass=.5、4-neighbor、逐head、冻结heads/行为组/max_side640；不扫描threshold。图像grid token数median220、range84-300；最常见11x20为94/111。条件归一化排除目标图像外tokens，故不衡量目标图像的全局attention预算。

## 指标与计数规则
S50=承载>=50%目标图像内条件attention的最小高权token集合（非token数量前50%）。H=任一S50 token与GT fractional overlap>0；M=sum_i p_i*occupancy_i>.5，使用全部image-span而非仅S50；C=S50的4邻域components；CG=与GT相交components；L=最大token-count component与GT相交。保存k*、selected_mass、GT mass/grid/coverage/mask。

## 完整性门槛 / no-silent-zero
111/111 forwards and figures; exact p-1 rows; image spans/grids validated; exit0

## 观测结果摘要
G→R 3-head all-hit error34/35 vs correct76/76，hit饱和；至少一head majority 8.6% vs31.6%。Q→R mean hit-heads 2.51 vs3.22，diff+.709 CI[.086,1.329]；4/4 hit45.7% vs71.1%；largest-component-hit heads1.74 vs2.51，diff+.770 CI[.071,1.460]；至少一head majority仅2.9% vs6.6%。Q→R k* median error→correct：L18H15 9→12.5，L19H03 6→17，L22H00 35→38，L20H08 6→12，因此不能称correct support更集中。Q→Q hit-heads1→4，仅sanity check。

## 局限与混杂因素
attention-derived non-causal；teacher replay；local split；merged-token非pixel segmentation；50%是固定可解释阈值而非论文标准；image-span条件归一化不测全局budget；H任意overlap易受bbox大小/碎片化影响；C受grid与k*影响；largest component按token数且并列有扫描顺序；Q→R不证明identity。

## 可支持的结论
可说：correct中更多Q→R heads的S50及最大component触及reference GT；G→R hit在两组近乎普遍。不可说：多数全局attention落GT、correct更集中、error无grounding、head具有因果/identity选择性。

## 不支持的结论 / Claim 边界
Top50中的50%是target-image-conditional mass。Q→R majority极少，故主结论是spatial support overlap的一致性差异，不是majority attention或global reference use。Q→Q与IoU分组定义耦合，只作sanity check。

## 关键指标
{"n_error":35,"n_correct":76,"forwards":111,"figures":111,"head_maps":1221,"support_mass":0.5,"connectivity":4,"grid_tokens_median":220,"grid_tokens_min":84,"grid_tokens_max":300,"gtr_all3_hit_error":0.9714285714,"gtr_all3_hit_correct":1.0,"qtr_mean_hit_heads_error":2.5142857143,"qtr_mean_hit_heads_correct":3.2236842105,"qtr_mean_hit_heads_diff":0.7093984962,"qtr_mean_hit_heads_ci95":[0.0857048872,1.3289473684],"qtr_all4_hit_error":0.4571428571,"qtr_all4_hit_correct":0.7105263158,"qtr_largest_mean_heads_error":1.7428571429,"qtr_largest_mean_heads_correct":2.5131578947,"qtr_majority_any_error":0.0285714286,"qtr_majority_any_correct":0.0657894737,"qtq_mean_hit_heads_error":1.0,"qtq_mean_hit_heads_correct":4.0}

## 审核入口
canonical: shell/06_experiments/E-006/runs/E006-R-005-simple-top50-support-components-positive-extremes-n111-640.md；组会详解: shell/06_experiments/E-006/top50_support_group_meeting_guide.md；结果: shell/06_experiments/E-006/result.md；remote analysis/summary.json,poststats.json,support_selection_details.json；visualizations/*.png；local previews/statistics: shell/06_experiments/E-006/visualizations/R-005/

## 过程记录与补充细节
组会重点：50%是目标image-span内条件质量，不是全局attention。S50是最小集合，selected mass因离散最后一个token通常略超.5。多数attention(M)用全部image-span的fractional GT mass，和S50 hit(H)是不同问题。完整公式、伪代码、220-token例子、逐head k*和不可支持表述已归档到group-meeting guide。

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e006_simple_support_audit.py

### 配置/超参数
（待补充）

### Seed
20260728

### 日志路径
/home/featurize/work/mechanism/explog/E-006/e006_r005.log

### 产物目录
/home/featurize/work/mechanism/explog/E-006/runs/E006-R-005-simple-top50-support-components-positive-extremes-n111-640/analysis

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-006/runs/E006-R-005-simple-top50-support-components-positive-extremes-n111-640

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
- run_dir: /home/featurize/work/mechanism/explog/E-006/runs/E006-R-005-simple-top50-support-components-positive-extremes-n111-640
- log_file: /home/featurize/work/mechanism/explog/E-006/e006_r005.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/runs/E006-R-005-simple-top50-support-components-positive-extremes-n111-640/analysis
- metrics_file: /home/featurize/work/mechanism/explog/E-006/runs/E006-R-005-simple-top50-support-components-positive-extremes-n111-640/metrics.json
- tmux_session: incontext-E-006-E006-R-005-simple-top50-support-components-positive-extremes-n111-640
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-28T23:37:58
- updated: 2026-07-28T23:51:04

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
