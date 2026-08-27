# E010-R-004-frozen-query-head-reference-span-bias-audit · 冻结Query heads投向Reference图像的空间偏差与坐标复制审计

- workflow: v2 / analysis_pending / 结果分析
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-e57fc834344208913e9dbba8 / completed

## 1. 研究设计
### 研究问题
当仅由Qbbox→Query发现的冻结query heads在同一自然Query bbox rows下改看Reference image tokens时，其注意力是否系统偏离Reference目标，并更接近Query归一化坐标投影、固定边界/中心或随机分布？
### 本轮目的
冻结R-003仅由Qbbox→Query发现的query heads，在完全相同的自然Query bbox prediction rows上把key span切换到Reference image，测量其注意力是否相对R-003 reference heads表现出系统目标错位、Query坐标复制、固定位置/边界偏置或仅仅较弱的Reference目标信号。
### 假设或比较预期
若query heads是Query侧坐标定位专用头，其Qheads→Reference map可能更偏向projected Query位置或固定位置而非Reference GT；若它们是跨图共享目标头，则应接近Rheads→Reference并优先Reference GT。
### 数据与主要变量
只使用R-003的70条selection-held-out evaluation sequences；若R-003完整性或稳定性gate失败，本Run记录dependency stop而不把空结果记为零。每条同时需要Reference/Query GT、双图尺寸与token grid，GT仅用于本Run冻结后的偏差评价。

四格：Qheads→Q、Qheads→R（主项）、Rheads→R、Rheads→Q。Qheads→R内比较Reference GT vs projected-Query区域 vs center vs boundary；控制为同层随机heads、all-head mean及图像面积/GT coverage匹配。Reference GT和projected Query重叠高的歧义样本不进入候选胜负主分析，但仍保留raw指标。

## 2. 指标设计
主指标为held-out配对的Reference-GT minus projected-Query mass/enrichment偏差及bootstrap CI；辅以四候选距离、边界mass、Qheads→R与Rheads→R/同层随机差、统一色标四格可视化。
## 3. 代码架构
新增纯离线frozen-head cross-span bias分析入口，读取R-003 hashes和旧全头artifacts，生成四格raw maps、候选occupancy、paired metrics与可视化；不得重跑选择算法。
- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `PYTHON_BIN=/root/miniconda3/envs/DIGEO/bin/python bash mechanism/iplocid/tools/run_e010_r004.sh --config mechanism/iplocid/configs/e010_r004.json`
- commit: ``
- workspace: 02
- tmux: incontext-E-010-E010-R-004-frozen-query-head-reference-span-bias-audit
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-004-frozen-query-head-reference-span-bias-audit/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-004-frozen-query-head-reference-span-bias-audit/outputs
- Steward 摘要：```json
{
  "execution_completed_at": "2026-08-27T11:05:01",
  "evidence": {
    "log": "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-004-frozen-query-head-reference-span-bias-audit/logs/train.log",
    "artifact": "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-004-frozen-query-head-reference-span-bias-audit/metrics.json",
    "result_message": "managed execution exited 0; metrics parsed; human analysis required"
  },
  "note": "程序已结束，等待科研结果分析"
}
```

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
Managed execution exited successfully with 0 declared and 5 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

## 简短局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "用户特别关心‘让query head在reference image token的注意力是否有偏差’。旧实验只报告部分Q→R target mass或把G→R作为参照，无法区分query-head跨span后的四种解释：仍跟随Reference目标、复制Query归一化坐标、固定/边界位置偏置、或无结构噪声。必须冻结R-003两批名单后做同rows跨span配对比较。",
  "evidence_basis": "R-003将提供严格定义的query heads和reference heads及其selection-held-out集合。旧E010可视化提示旧Q→R自发现heads常聚焦Reference图边缘，但旧entropy实现和head定义不足以形成solid结论；本Run预注册位置候选与统计，避免看到热图后再解释。",
  "implementation_summary": "计划纯离线读取R-003冻结名单及同一自然bbox全头artifacts，不重选任何head。对每个held-out样本同时形成四个配对map：query heads→Query、query heads→Reference、reference heads→Reference、reference heads→Query；主比较聚焦query heads→Reference，其他三项作为定位上界、角色基线和交换对照。",
  "implementation_details": "所有map使用与R-003完全相同的自然Query bbox p−1 rows。query heads与reference heads分别读取R-003不可变selection manifest及SHA-256。每个head先保留raw map，再形成预注册Top3/Top5等权均值；禁止按held-out GT重新加权。将Query GT bbox按归一化坐标投影到Reference grid，形成四个预注册候选区域：Reference GT、projected Query GT、固定中心区域、边界带。另保留无候选的COM/argmax分布和热图。",
  "model_config": "完全复用R-003自然回答、rows和attention artifacts，不重新加载模型；query/reference head名单、Top3/5和所有selection参数由R-003哈希锁定。",
  "metric_definition": "主偏差分数：Qheads→R的mass/enrichment(Reference GT)减去mass/enrichment(projected Query region)，并同时报告二者各自绝对值；候选判别为argmax/COM到Reference GT、projected Query、center和boundary的归一化距离；边界偏置报告top/bottom/left/right带mass及COM分布。配对比较Qheads→R vs Rheads→R，及Qheads→R vs同层随机。空间map补充JSD、S50 fIoU和token-grid coverage。所有效应给sequence bootstrap CI，不只报命中率。",
  "integrity_gates": "G1 R-003 selection manifest/hash和70 held-out IDs必须匹配；G2禁止任何重新挑头、按GT加权或剔除不利样本；G3所有四格使用相同自然Query bbox rows；G4 projected Query区域必须按图像归一化坐标投影并记录Reference token-grid occupancy，不直接复制像素坐标；G5 Reference GT与projected区域IoU超过预注册阈值0.3者标记ambiguous并从候选胜负主分析排除但不删除；G6边界带固定为merged grid外圈20%且运行前冻结；G7逐样本图使用共同色标/同时给raw mass，避免独立min-max造成视觉误判。",
  "expected_outcome": "区分：A query heads跨到Reference仍优先Reference GT；B显著偏向projected Query位置，支持坐标复制；C显著偏向固定边界/中心，支持位置偏置；D无候选优势且接近随机，支持跨span失效。reference heads→Reference作为独立角色基线，而不是G→R。",
  "acceptance_criteria": "R-003依赖和hash核对；70条四格map和逐样本raw metrics齐全；Reference/projected/center/boundary四候选及ambiguity计数齐全；Top3/5、同层随机、all-head配对CI齐全；correct/error只作预注册分层；至少12张统一色标四格总览和每个query head投向Reference的逐头图；结论明确落入A/B/C/D或不确定。",
  "claim_boundary": "只判断R-003冻结query heads在Reference image tokens上的空间分布相对Reference目标、Query投影坐标和固定位置是否有系统偏差，并与R-003 reference heads/随机对照比较；不引入Reference bbox rows，不证明身份匹配或因果必要性。",
  "artifacts": "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-004-frozen-query-head-reference-span-bias-audit/metrics.json\n/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-004-frozen-query-head-reference-span-bias-audit/logs/train.log",
  "audit_paths": "R-003 selection manifest/held-out manifest；旧E010全头artifacts；新增bias candidate occupancy与统一色标可视化；用户原始定义（2026-08-26，逐字保留）：首先我们的实验都是去测量Query bbox token对query/reference image token的注意力，不存在找reference bbox对reference image token的。然后通过query bbox token对两个不同image的注意力经过算法可以得到两批head，一个是query head一个是reference head，指的是模型在生成query bbox token时，看了query/reference图像的哪些区域。所以我指的query head和reference head都是query bbox token对前面的图像的注意力。我现在想确定的是，这两个head是否显著且稳定，而让query head在reference image token的注意力是否有偏差？"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
