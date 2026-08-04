# E006-R-009e-refcoco-specific-gt-aligned-head-discovery-viz-fresh200 · refcoco-specific-gt-aligned-head-discovery-viz-fresh200

- canonical_run_id: `E006-R-009e-refcoco-specific-gt-aligned-head-discovery-viz-fresh200`
- run_type: discovery
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-04T18:45:27
- approved_at: 2026-08-04T18:46:53
- execution_authorized_at: 2026-08-04T18:46:55
- execution_authorization_consumed_at: 2026-08-04T18:47:19
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
planned

## 本轮目的
利用R-009d已保存的原始prompt自然bbox-row全1152-head矩阵，在discovery侧显式寻找RefCOCO GT-aligned且相对IPLoc已知pool独特的heads；冻结后在原200 fresh confirmation上评估并可视化，检验是否比R-009d非GT Top5空间图更紧致、更目标对齐。

## 必要性 / 证据链位置
用户观察R-009d Top5可视化很差。R-009d score只优化image budget×concentration而不使用GT，可能漏掉真正RefCOCO target-aligned heads。需要区分selection-objective failure与RefCOCO需要独特head set，并以fresh confirmation及固定可视化判断。

## 研究依据 / 被审计对象
R-009d原prompt完成：999 discovery/200 confirmation全head artifacts，Top5 mass=.300/enrichment=1.992/pointing=.417但可视化不紧致；与R010 B→Q Top10重合8/10。R-009d结果文件保存discovery budget/entropy，confirmation保存GT矩阵；本run必须先审计discovery文件是否含GT metrics，若缺失则仅对原999 discovery做离线GT补算或同响应teacher replay，不重新生成/改prompt。

## 实现方式（简版）
冻结三套互斥/对照head set：(A) RefCOCO-oracle：discovery GT-alignment综合排名；(B) RefCOCO-specific：从A候选中排除预声明IPLoc pool及R009/R009d既有heads后排名；(C) shared：限制在R010 B→Q union内按同一GT score排名。所有选择只用discovery；200 confirmation仅评价。另保留R009d nonGT Top5、main4、random controls。

## 实现方式（详细版）
Discovery GT score预注册为z(mean enrichment)+z(pointing rate)+z(fractional mass)，三项等权；先要求mean image budget位于全head discovery中位数以上，避免近零budget条件归一化伪峰。所有z基于1152 heads。Specific exclusion union在运行前冻结：historical main4、R009 last Top5、R009d nonGT Top50、R010 B→Q correct/error Top50（若现有R010只可靠保存Top50即使用；不得看confirmation后增删）。每套冻结Top1/Top3/Top5/Top10。

## 数据身份与构造
严格复用R-009d原prompt运行的999 valid discovery与200 valid confirmation，样本身份和split不变。GT occupancy使用fractional cell occupancy及display-size转换。不得把confirmation用于阈值、head选择、TopK选择或可视化样本筛选。

## 数据规模
离线优先：999 discovery×1152与200 confirmation×1152。若R009d discovery缺GT arrays，允许用冻结natural responses做999 teacher replays以补全GT metrics，禁止重新natural generate；GPU执行需另行授权。可视化固定20个confirmation样本：按manifest confirmation顺序前20，不按效果选择。

## 模型、权重与关键配置
离线分析不加载模型。若补算必要：base Qwen3-VL-8B、R009d原始prompt/response、bf16 eager、max_side=640、原始bbox token p-1 rows；不加载IPLoc LoRA，不改变response。

## 变量、干预与对照
Headset=A oracle、B specific、C shared、D R009d nonGT Top5、E historical main4、F layer-matched random。TopK固定1/3/5/10。可视化对每个样本同一色标策略并同时提供individual heads及set aggregate；不以肉眼结果改变head set。

## 指标与计数规则
Fresh confirmation：mass/enrichment/pointing/S50/allhead percentile；每样本paired差值及image bootstrap B=10000。可视化质量量化：GT内/外attention ratio、pointing、top10%/top25% support fractional GT precision与recall、attention COM到GT中心距离、connected-component最大GT-overlap；明确是merged-token support非pixel segmentation。比较A/B/C相对D的paired CI。

## 完整性门槛 / no-silent-zero
1确认R009d split/hash及999/200身份；2 discovery/confirmation隔离；3 exclusion list推理前写manifest；4 discovery score/预算门槛固定；5 TopK不按confirmation挑；6 fixed first20可视化且全部输出；7同一样本/row/maps比较；8 allhead finite；9若specific候选不足10如实停止/缩小K，不放宽exclusion；10 attention结果非因果。

## 竞争假设与预期特征
若B specific在fresh confirmation和固定20图上显著优于D且与A接近，支持RefCOCO-specific spatial heads；若A好但B差、C好，支持共享pool而非独特heads；若A/B/C均不明显优于D，说明单head attention图本身不能提供干净定位或GT selection过拟合；若仅视觉更好而量化/CI不改善，报告presentation-only差异。

## 验收条件
冻结A/B/C各Top1/3/5/10及完整ranking；200 confirmation无重选；20×至少A/B/C/D aggregate对照图，另输出Top5 individual-head grid；head-set overlap heatmap/UpSet；paired bootstrap表；明确回答是否不同、是否fresh更好、是否只是视觉更好。

## 依赖的 Run / 证据
R-009d completed artifacts；R-010 B→Q Top50；R-009/R-009c frozen heads；R-005 main4。优先先做artifact audit，若需要GPU补算则审批后的执行授权只用于本canonical run。

## 观测结果摘要
（待补充）

## 局限与混杂因素
GT-guided discovery是oracle诊断，不是部署时无监督选头；specific由排除列表操作性定义，不等于机制独有；RefCOCO单图不同于IPLoc双图；20张固定图只作展示，统计以200为准；attention非因果且merged-token map不是segmentation。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
最多支持在固定RefCOCO discovery定义下存在/不存在相对已知IPLoc pool独特、并在fresh RefCOCO confirmation更GT-aligned的attention heads。不得称任务专属因果电路、不得由好看的图替代fresh统计、不得推广到identity binding。

## 关键指标
（待补充）

## Artifacts
（待补充）

## 审核入口
/home/featurize/work/mechanism/explog/E-006/E006-R-009d-refcoco-original-prompt-natural-output-row-audit-n20-1000-200/results; /home/featurize/work/mechanism/explog/E-006/E006-R-009d-refcoco-original-prompt-natural-output-row-audit-n20-1000-200/artifacts/checkpoint.json; /home/featurize/work/mechanism/explog/E-006/E006-R-010-outcome-stratified-allhead-discovery-sequence-split/analysis/summary.json; shell/06_experiments/E-006/runs/E006-R-009d-refcoco-original-prompt-natural-output-row-audit-n20-1000-200.md

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
20260728

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
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-009e-refcoco-specific-gt-aligned-head-discovery-viz-fresh200
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-009e-refcoco-specific-gt-aligned-head-discovery-viz-fresh200/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-009e-refcoco-specific-gt-aligned-head-discovery-viz-fresh200/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-009e-refcoco-specific-gt-aligned-head-discovery-viz-fresh200/metrics.json
- tmux_session: incontext-E-006-E006-R-009e-refcoco-specific-gt-aligned-head-discovery-viz-fresh200
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-04T18:45:27
- updated: 2026-08-04T18:47:19

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
