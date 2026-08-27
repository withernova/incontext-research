# E010-R-005-per-image-nogt-selection-vs-gt-oracle-reference-head-audit · 自然Qbbox→Reference逐图无GT选头与GT-oracle误差分解

- workflow: v2 / analysis_pending / 结果分析
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-c731f87351460754fe654f0c / completed

## 1. 研究设计
### 研究问题
在自然Query bbox生成的相同p−1 rows与Qbbox→Reference全头attention maps中，LocalizationHeads式逐图无GT选头能否找回GT oracle证明存在的Reference-responsive head？固定名单失败主要来自动态head routing、无GT候选过滤/排序失配，还是Reference空间信号弱？
### 本轮目的
在不重跑模型、不改写R-003、不让GT进入无GT选头的前提下，分解固定Qbbox→Reference head失败：比较逐图无GT Top-k、同层随机、all-head mean与事后GT oracle；区分候选过滤、候选内排序和跨样本固定化三个环节。
### 假设或比较预期
若GT oracle高而逐图无GT Top10召回/排序低，则无GT准则遗漏Reference-responsive信号；若逐图无GT高但head ID不集中，则有效head动态变化；若GT监督以外的oracle优势也不稳定，则固定Reference spatial head路线应停止。
### 数据与主要变量
仅使用R-003的70条selection-held-out LaSOT sequence records、自然生成Query bbox p−1 rows及Qbbox→Reference 1152-head attention artifacts；不从R-003 discovery或其他数据补样本。每条同时需要Reference GT、Reference token grid、row/span契约与自然输出身份。训练暴露未知，样本只能称selection-held-out。

主变量为head选择方式：逐图严格无GT Top1/3/5/10 vs layer-matched random vs all-head mean vs GT oracle上限；附加分解为Top10候选召回与候选内rank。GT只在选择结束后评分；correct/error、自然IoU、对象大小和grid coverage仅作预注册分层解释，不进入选头。

## 2. 指标设计
以逐图无GT Top1/3/5/10的空间评分与Top10候选召回为主，GT oracle为上限，同层随机为主对照，head-ID集中度/Jaccard为动态routing诊断；所有比较按70条sequence bootstrap置信区间报告。
## 3. 代码架构
在IPLoc现有attention analysis模块新增只读per-image Qbbox→Reference selector/oracle audit入口；复用R-003 artifact reader与空间指标，不复制runner或重载模型。实现完成前不得启动；本次登记不涉及代码修改。
- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `cd /defaultShare/archive/liuwenchu/projects/IPLoc && mechanism/iplocid/tools/run_e010_r005.sh`
- commit: ``
- workspace: 02
- tmux: incontext-E-010-E010-R-005-per-image-nogt-selection-vs-gt-oracle-reference-head-audit
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-005-per-image-nogt-selection-vs-gt-oracle-reference-head-audit/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-005-per-image-nogt-selection-vs-gt-oracle-reference-head-audit/outputs
- Steward 摘要：```json
{
  "execution_completed_at": "2026-08-27T13:22:25",
  "evidence": {
    "log": "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-005-per-image-nogt-selection-vs-gt-oracle-reference-head-audit/logs/train.log",
    "artifact": "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-005-per-image-nogt-selection-vs-gt-oracle-reference-head-audit/metrics.json",
    "result_message": "managed execution exited 0; metrics parsed; human analysis required"
  },
  "note": "程序已结束，等待科研结果分析"
}
```

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
Managed execution exited successfully with 0 declared and 4 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

## 简短局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "Q-006记录显示：R-003的固定Qbbox→Reference heads在70条selection-held-out样本上空间有效性很低，而旧R-001的per-image GT oracle在同类maps中可读出部分Reference-responsive单头信号。仅看固定名单无法区分“信号不存在”“head随样本变化”与“LocalizationHeads无GT准则漏选”。R-004仅审计冻结query heads跨span偏差，不能替代该误差分解。",
  "evidence_basis": "Q-006 §已有证据与边界、§当前关键缺口、§建议实验1；[[localizationheads2025]] §4.1–4.2的无GT候选/频率思路。R-003已生成artifact summary但其completion受metrics declaration contract阻断，因此本Run必须先独立核验artifact契约，不能将历史数值直接升级为结论。",
  "implementation_summary": "纯离线读取R-003自然Query bbox p−1 rows与Qbbox→Reference全头maps。对70条selection-held-out记录逐图重跑严格LocalizationHeads式无GT选择，产生Top1/3/5/10及head-level特征；冻结选择结果后以Reference GT做空间评分，并与同层随机、all-head mean和事后GT oracle比较。不得重新生成、teacher-force或训练校准模型。",
  "implementation_details": "每条样本：复用R-003层排除、image-attention threshold、按自身均值二值化、8邻域component-token-count entropy与排序参数；无GT阶段输出Top1、Top3/5等权map、Top10集合、完整rank及budget/entropy。随后才计算pointing、area-normalized enrichment、target mass、S50 fIoU，并记录Top10是否包含oracle/有效head、oracle在无GT排名的位置和候选内排序损失。随机对照按入选head层匹配、固定seed并保存抽样清单。",
  "model_config": "不加载模型；冻结R-003所用Qwen3-VL-8B-Instruct + IPLoc-ID LoRA产生的自然回答和attention artifacts。运行前核验artifact、自然输出、rows/spans、token grids、manifest与Reference GT的哈希/契约。",
  "metric_definition": "主指标：Top1/3/5 pointing rate、area-normalized enrichment、target mass、S50 fIoU；Top10至少一头/多数head的pointing-hit；Top10对GT-oracle或预定义有效head集合的候选召回；oracle head rank与Top1/3/5相对Top10的损失；head ID inclusion probability、pairwise Jaccard、集中度和effective head count。所有主要效应报告相对同层随机的sequence bootstrap CI。",
  "integrity_gates": "G1 R-003全头artifact、自然回答、70 IDs、rows/spans、token-grid与Reference GT契约/哈希均须通过，否则dependency_stop；G2 无GT选择阶段严禁读取GT、自然IoU、correct/error或任何空间评分；G3 所有70条均输出完整结果，空map/coverage不足/解析失败单列而不删除；G4 随机头层匹配、seed和名单持久化；G5 oracle仅作事后上限，不得进入固定名单或部署选择；G6 本Run不得改成GT监督固定head discovery或无GT校准。",
  "expected_outcome": "可判别四类结果：(1) Top10召回高但Top1/3/5低，候选过滤可用而熵/排序失配；(2) 逐图无GT优于固定名单但head ID低集中，sample-specific dynamic routing；(3) 无GT低而oracle经随机极值校正仍高，当前准则漏选单图信号；(4) 无GT和oracle均近随机，自然Qbbox rows的Reference空间信号弱。任何结果均不证明身份选择性或因果必要性。",
  "acceptance_criteria": "70条输入契约均核验或明确dependency_stop；每条的无GT/随机/all-head/oracle原始指标和head名单齐全；Top1/3/5/10及Top10候选召回/候选内排序汇总和sequence bootstrap CI齐全；head集中度/Jaccard分析齐全；至少12个统一色标案例展示无GT Top-k、oracle、Reference GT和Top10候选；失败样本完整清单、配置与随机seed可追溯。",
  "claim_boundary": "只回答自然Query bbox rows下Qbbox→Reference attention中，严格无GT逐图选择相对GT oracle、随机和固定化的误差来源；不改变R-003/R-004结论，不证明模型完全未使用Reference、不证明身份匹配，也不证明任何head为因果必要电路。",
  "artifacts": "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-005-per-image-nogt-selection-vs-gt-oracle-reference-head-audit/metrics.json\n/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-005-per-image-nogt-selection-vs-gt-oracle-reference-head-audit/logs/train.log",
  "audit_paths": "shell/01_questions/Q-006.md；shell/06_experiments/E-010/runs/E010-R-003-natural-query-bbox-dual-span-head-discovery-stability.md；shell/06_experiments/E-010/runs/E010-R-004-frozen-query-head-reference-span-bias-audit.md；R-003 artifact manifest、records、全头Qbbox→Reference maps与analysis summary（执行前定位并核验）。"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
