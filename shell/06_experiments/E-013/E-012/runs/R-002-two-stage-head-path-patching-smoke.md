# R-002-two-stage-head-path-patching-smoke · 两阶段 head 协作：跨层路径 patching smoke

- workflow: v2 / awaiting_review / 等待审核
- review_status: pending_review
- group_id: 未分组
- execution_dispatch:  / 

## 1. 研究设计
### 研究问题
梯度敏感 head 与 A@V 可解码 head 是否通过跨层路径串联影响 bbox-token 预测？
### 本轮目的
比较上游注意力空间损坏、下游 clean 输出救回和 corrupt 输出损害迁移，区分两批 head 只是各自相关，还是存在方向明确的跨层中介关系。
### 假设或比较预期
若存在 U→D→bbox 路径，则翻转 U 的 query 视觉注意力会改变 D 的 A@V 并提高 bbox CE；把 clean D 输出 patch 回 corrupt run 应救回损失，把 corrupt D 输出注入 clean run应迁移损害，且均强于同层低分 head 对照。
### 数据与主要变量
复用 R-001-bbox-gradient-halffull/frozen_input.json 的 690 个固定索引及原 test_combined_lasot600_gotval_taoval_1shot_focus.json；运行时按数据集各取前4个冻结索引，避免只取排序靠前的LaSOT。

P1候选U={L21H31,L21H11}→D={L23H19,L23H02,L23H30,L23H31}；P2候选U={L23H19,L23H02,L23H30,L23H31}→D={L24H13,L26H25}。上游与下游均配置同层A/B低分head控制。U干预仅水平翻转query视觉网格注意力，保持每行query mass、注意力值集合和熵；D在A@V后、o_proj前按bbox prediction rows patch 128维单-head输出。

## 2. 指标设计
复用 bbox_token_ce_mean；新增 upstream_damage=L_corrupt−L_clean、rescue_effect=L_corrupt−L_rescue、rescue_fraction=rescue_effect/upstream_damage（仅 upstream_damage>1e-4 的样本定义）、transfer_effect=L_transfer−L_clean、downstream_relative_change=||D_corrupt−D_clean||/max(||D_clean||,1e-8)。同时报告 teacher-forced argmax bbox IoU 与中心变化；候选下游与同层低分控制使用相同公式。
### bbox梯度绝对贡献（逐head样本均值） (`bbox_grad_abs_contrib_mean`)
- 公式：C_lh = mean_n sum_{p,j in query} |A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]|
- 含义：teacher-forced bbox token平均CE对指定query->query视觉注意力边的局部敏感度绝对量；只表示当前输入下的敏感度大小，不是因果必要性，也不是增强方向证据
- 汇总与范围：每条边先取绝对值，再按样本求和，最后样本等权平均；不除以视觉token数 / Qwen3-VL-8B+LoRA、36层x32 query heads=1152 heads；20条先导与690条扩展两轮eval子集

### bbox梯度signed贡献（逐head样本均值） (`bbox_grad_signed_contrib_mean`)
- 公式：S_lh = mean_n sum_{p,j in query} A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]
- 含义：对post-softmax指定边做不重归一化乘法缩放时的一阶CE导数方向；本轮有限差分与反传符号不一致，方向暂不可用于增强/抑制决策
- 汇总与范围：样本等权平均 / 同上1152 heads；20条与690条两轮eval子集

### 平均bbox token CE (`bbox_token_ce_mean`)
- 公式：mean_n mean_i CE(logits[p_i-1], token[p_i])
- 含义：teacher-forced query bbox片段（含标点）平均交叉熵，仅表示损失量级，不是IoU或定位准确率
- 汇总与范围：样本等权平均 / 690条（LaSOT 300/GOT10k 90/TAO 300）与20条先导

### 头部排名集合Jaccard (`head_ranking_jaccard`)
- 公式：|A∩B|/|A∪B|
- 含义：不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升
- 汇总与范围：对固定Top-k集合直接计算 / 20条vs690条、690条对旧固定5 head；Top-5/Top-10/Top-50

### 有限差分与反传符号一致 (`finite_difference_sign_agreement`)
- 公式：sign(central_difference) == sign(signed_derivative)
- 含义：首样本指定边±epsilon缩放的中央差分是否与反传signed导数同号；本轮为false，说明梯度方向链路校验未通过
- 汇总与范围：首样本单一诊断，不参与排名 / 690条run首样本dataset_index=0 L24H25，epsilon=0.02

## 3. 代码架构
新增独立 iploc_szy/head_screening/head_circuit.py、configs/head_screening/e012_head_circuit_path_patching.py、tools/run/e012_head_circuit_path_patching.sh 和 tests/test_head_circuit.py；复用现有Config、dataset/collator、checkpoint加载、bbox probe行契约，不修改训练或E-011分支模块。
- 公共包：`mechanism/iploc-szy/iploc_szy/head_screening`
- 入口：`iploc_szy.head_screening.head_circuit:main`
- 配置：`mechanism/iploc-szy/configs/head_screening/e012_head_circuit_path_patching.py`
- Shell launcher：`mechanism/iploc-szy/tools/run/e012_head_circuit_path_patching.sh`
- 复用模块：iploc_szy/head_screening/bbox_gradient.py, iploc_szy/head_screening/probes.py, iploc_szy/config.py, iploc_szy/registry.py
- 新增模块：iploc_szy/head_screening/head_circuit.py
- 测试：tests/test_head_circuit.py

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy/tools/run/e012_head_circuit_path_patching.sh`
- commit: `5364dab1e150d437dbca1f4765cef2d8e20068b3`
- workspace: 02
- tmux: incontext-E-012-R-002-two-stage-head-path-patching-smoke
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/logs/R-002-two-stage-head-path-patching-smoke.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-002-two-stage-head-path-patching-smoke
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
空间翻转可能分布外；只patch bbox prediction rows；12条为机制smoke且参与过A/B discovery；head-to-head阴性不能排除MLP、residual或更早token中介。

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "A/B 排名仅中等相关且单 head steering 近零；现有证据不能判断“敏感但不可解码”和“可解码但不敏感”的 head 是否协作。",
  "implementation_summary": "独立config管理候选路径和后续细粒度head挑选；公共hook在同一次文本attention前向中按层完成上游空间翻转、下游A@V捕获/替换和firing审计。",
  "implementation_details": "每样本每路径先跑clean和candidate-U corrupt并缓存候选/控制D输出，再跑candidate-D rescue/transfer、control-D rescue/transfer、upstream-control corrupt；首样本额外做clean→clean与corrupt→corrupt identity patch。所有patch限定bbox p−1 prediction rows。",
  "model_config": "Qwen3-VL-8B-Instruct BF16底座 + E-011 step1973 LoRA；eager attention，device_map=auto，focus协议，坐标0–1000，vision patch cap 1024。",
  "metric_definition": "CE指标均为teacher-forced bbox token平均交叉熵。只在corrupt−clean>1e-4时定义逐样本rescue fraction，另报告不带筛选的effect均值，防止小分母制造比例。候选相对控制的rescue和transfer方向一致才视为串联线索。",
  "integrity_gates": "两图视觉span与merged grid一致；全部U层严格早于D层；水平翻转前后query mass、排序后注意力值与熵在容差内一致；每个配置head hook恰好触发；identity patch的bbox-row full-vocabulary logits与来源run在atol/rtol=0.002内一致；12/12且三数据集各4条，失败不输出部分科学summary。",
  "expected_outcome": "输出两条路径的逐样本条件CE、argmax框、下游输出变化、候选/控制rescue与transfer；不预设一定存在中介。",
  "acceptance_criteria": "py_compile、Shell语法和聚焦单元测试通过；首样本真实8B identity/mass-preservation gate通过；12条正式smoke完整输出。科学上若上游无正damage或候选下游不优于控制，则记录为该干预与读出下未支持，不扩大扫描。",
  "claim_boundary": "仅支持或削弱固定step1973、固定候选组、水平翻转干预和teacher-forced bbox读出下的跨层head-output中介假设；不证明语义身份电路、普遍因果充分性或泛化收益，不修改Claim。",
  "audit_paths": "remote commit 5364dab1e150d437dbca1f4765cef2d8e20068b3；review_id=b1c2307e82c9e1ff；tests/test_head_circuit.py；shell/06_experiments/E-012/implementation/"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
