# R-001-bbox-gradient-initial · bbox 梯度初筛：指定 checkpoint 与三数据集 eval 样本

- workflow: v2 / awaiting_review / 等待审核
- review_status: pending_review
- group_id: 未分组
- execution_dispatch:  / 

## 1. 研究设计
### 研究问题
给定 checkpoint 在未见视频的 bbox 预测中依赖哪些 query→bbox 注意力边？这些 head 的梯度排名在 LaSOT、GOT10k 和 TAO 样本上是否一致？
### 本轮目的
使用指定训练 checkpoint，在三个数据集训练清单之外的视频上计算 bbox 梯度贡献并排名。比较总排名与分数据集排名，初步观察候选注意力头是否依赖某一数据集。
### 假设或比较预期
在训练清单未出现的视频上仍可得到非零且有区分度的梯度贡献；不同数据集排名的一致性可为后续独立样本验证提供候选，但不预设泛化提升。
### 数据与主要变量
直接复用已有 eval manifest：/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-real-focus-data/manifests/test_combined_lasot600_gotval_taoval_1shot_focus.json；SHA256=48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b。1766条记录，LaSOT=600、GOT10k=180、TAO=986。对照该 checkpoint 配置指向的当前训练清单 /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-real-focus-data/manifests/train_only_1shot_focus_valid10522.json（10522条；SHA256=bd7037325096cc99097333090ec5d02f64dd9ce2922f04e0e4409d1d635bd6e7），以(dataset,视频目录名)检查reference和query序列，当前1766条eval记录均无训练视频重叠；运行时重新检查训练清单哈希和重叠。

运行前固定指定checkpoint、原始eval清单、训练清单哈希、分层配额7/7/6、seed20260910、focus协议、patch上限1024和bbox字符串token范围。每个视频最多一条，reference/query都与训练视频做重叠检查。主筛查没有干预；首样本的小幅指定边缩放仅作方向诊断。

## 2. 指标设计
C_lh=mean_sample sum_{p,j∈query}|A_lh[p−1,j]·dL_bbox/dA_lh[p−1,j]|，L_bbox为每样本bbox token平均CE。同时输出signed、正/负贡献、分数标准差、signed为正的样本比例、平均bbox CE；总排名与三数据集各自排名使用同一公式。首样本报告前向误差及中央差分方向/相对误差。各数据集仅6–7条，排名比较为探索性观察。
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
继续复用Config、注册器、Qwen3VLNative、IPLocManifestDataset、Qwen3VLSFTCollator。公共bbox_gradient模块增加LoRA检查/加载与分层eval选样；不修改训练包。原lasot_screen_manifest工具保留但当前config中manifest_preparation=None，不再生成新清单；config和薄Shell均有中文注释。
- 公共包：`mechanism/iploc-szy/iploc_szy/head_screening`
- 入口：`iploc_szy.head_screening.bbox_gradient:main`
- 配置：`mechanism/iploc-szy/configs/head_screening/e012_bbox_gradient_initial.py`
- Shell launcher：`mechanism/iploc-szy/tools/run/e012_bbox_gradient_initial.sh`
- 复用模块：mechanism/iploc-szy/iploc_szy/config.py, mechanism/iploc-szy/iploc_szy/registry.py, mechanism/iploc-szy/iploc_szy/models/qwen3vl_native.py, mechanism/iploc-szy/iploc_szy/datasets/iploc.py, mechanism/iploc-szy/iploc_szy/datasets/collator.py, mechanism/iploc-szy/iploc_szy/head_screening/probes.py
- 新增模块：mechanism/iploc-szy/iploc_szy/head_screening/bbox_gradient.py, mechanism/iploc-szy/iploc_szy/head_screening/lasot_screen_manifest.py
- 测试：mechanism/iploc-szy/tests/test_bbox_gradient_screen.py

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy/tools/run/e012_bbox_gradient_initial.sh`
- commit: ``
- workspace: 02
- tmux: incontext-E-012-R-001-bbox-gradient-initial
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/logs/R-001-bbox-gradient-initial.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-001-bbox-gradient-initial
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 5. 关键结果
### bbox_grad_abs_contrib_mean = 0.44119940996170043 (L26H25)
- 比较：L21H31=0.2949101964; L24H13=0.2927374447
- 差值：相对第2名 +0.1462892136
- 不确定性：std_absolute=0.126357
- 产物：results/R-001-bbox-gradient-initial/summary.json
- 解释：仅20条LaSOT/GOT10k/TAO 7/7/6探索性排名，样本量小

### head_ranking_jaccard = 0.666667 (Top-5, 20 vs 690)
- 比较：Top-10=0.818182
- 差值：—
- 不确定性：20条是690条子集
- 产物：results/R-001-bbox-gradient-halffull/comparison.json
- 解释：扩样后候选大致一致，非独立重复

## 6. 结果分析
本轮为探索性初筛，仅用于产生后续候选；各域样本仅6-7条，不能确认跨域泛化或稳定性。结果为attention×V路径上的局部敏感度，不是因果必要性，也不是生成IoU/Acc。690条扩展见R-001-bbox-gradient-halffull登记。

## 简短局限
与当前指定训练清单在视频目录标识上无重叠，不证明预训练未见过这些视频；20条eval样本实际参与选head，后续验证定位收益必须另用未参与筛查的样本；BF16与训练4bit路径不同；有限差分方向校验未通过。

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "已有公共探针只提取注意力图，使用 inference_mode 且不计算 bbox 专用损失；缺少经过真实 attention×V 路径的梯度排名。",
  "evidence_basis": "显式参考 [[makelvlm2025]] §2式（16）–（17）；用户本轮明确指定checkpoint目录，并要求使用已有eval样本。该目录仅用于定位/加载模型和核对输入配置，没有使用其训练结果或其他Run结论。Solid Run：无。",
  "implementation_summary": "在现有框架的注册器和Config上增加可配置checkpoint加载、已有manifest子集筛查及中文注释。加载已有LoRA结构与权重，逐张量检查加载一致性，复用adapter保存的processor；不恢复optimizer或训练干预。",
  "implementation_details": "保留bbox-only CE、p−1预测行、真实post-softmax A→AV梯度hook与逐边绝对值聚合。checkpoint_path支持训练目录/具体checkpoint/adapter目录或None，验证adapter底座匹配及权重完全加载；保存adapter配置和权重哈希。已有manifest可大于samples，按eval_selection配额选取训练清单之外的不同视频；--check-only仅处理实际选中20条，--prepare-only在复用模式拒绝。输出全体20样本排名和LaSOT/GOT10k/TAO各自排名。首样本仍保留原生前向一致性与±0.02概率边缩放中央差分诊断；不加载GT-mask训练hook，不更新参数。 预检与正式采集统一调用encode_sample，对bbox位置排序/唯一性/p−1有效性、监督label一致性、两张图像、query范围和merged网格做同一套校验。",
  "model_config": "完整底座为 /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct；checkpoint_path=/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-011/20260907T174853785543Z--focus-early-gt-mask-pipeline，加载该目录最终adapter。支持具体checkpoint目录或直接adapter目录，None使用原始模型；不自动选择latest。36层×32 query heads，8 KV heads；BF16底座+LoRA、eager、device_map=auto，拒绝CPU/disk offload。本次不复现训练时4bit量化数值路径。",
  "metric_definition": "absolute贡献越大表示当前输入下指定边对bbox CE越敏感；signed>0表示后softmax指定边局部放大会提高loss，signed<0表示会降低loss。样本先独立mean CE再等权聚合，不能先平均梯度再取绝对值。方向只对应不重归一化的概率边缩放；不等价于logits干预方向或完整head因果贡献。",
  "integrity_gates": "checkpoint存在且为LoRA，adapter底座路径匹配，全部saved tensor逐一加载一致；训练清单哈希匹配且选中reference/query均无训练视频重叠；配额恰好7/7/6且20个不同视频。继承完整bbox/p−1/token-grid/有限梯度/36层覆盖校验、2048序列预算、拒绝输出目录覆盖和拒绝部分成功排名。前向一致性必须通过；中央差分方向单独报告，失败不得声称方向验证通过。",
  "expected_outcome": "得到1152个(layer,head)的完整排名及逐样本分数，选出后续候选；不预先声称任何head已被验证有效或有害。",
  "acceptance_criteria": "聚焦CPU测试10项通过（含LoRA权重精确重载及梯度、已有大清单子集、视频排重与分层配额、完整双图Qwen3-VL+LoRA采集/反向/落盘/排名），真实checkpoint processor预检20/20通过，Shell语法和本地/远端内容哈希一致。正式运行要求20/20完整结果、全36层有限分数和原生前向一致；中央差分诊断单独解释。",
  "claim_boundary": "仅支持固定checkpoint与未出现在指定当前训练清单中的eval视频上的query→bbox边局部敏感度排名，以及三数据集的探索性比较；不能据同一批选head样本宣称泛化收益。signed只对应不重归一化的概率边缩放；不修改Claim。",
  "artifacts": "远端 /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-001-bbox-gradient-initial/{summary.json,ranking.csv,frozen_input.json,runtime.json,probe/records.json}；本地镜像 shell/06_experiments/E-012/results/R-001-bbox-gradient-initial/；实现代码 git commit 4411686f9205d55342c4856e79bedb83e80045ef（提交于 R-001-bbox-gradient-halffull 登记时；本 Run 处于待审核，规范字段暂不可改）",
  "audit_paths": "shell/06_experiments/E-012/result.md；results/R-001-bbox-gradient-initial/{summary.json,frozen_input.json}；implementation/{verification.md,source_hashes.json,pytest-bbox-gradient-v4.txt,eval-preflight-v4.json}"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
