# incontext — 研究项目

> 由 survey-tool 导出。配合 [research-survey](https://) skill 使用。

## 概况
- state: E002_PLANNING · iteration: 1
- 论文: 6 · 声明: 1 · Idea: 3
- 目标会议/领域: 见 INTAKE.md / AGENTS.md

## 论文
- [[detpoinc2026]] DetPO: In-Context Learning with Multi-Modal LLMs for Few-Shot Object Detection (2026)
- [[focusfor2026]] FOCUS: Forcing In-Context Object Localization through Visual Support Constraints and Policy Optimization (2026)
- [[mechanis2026]] Mechanisms of Object Localization in Vision-Language Models (2026)
- [[personal2026]] Personalized Object Identification and Localization via In-Context Inference with Vision-Language Models (2026)
- [[teaching2024]] Teaching VLMs to Localize Specific Objects from In-context Examples (2024)
- [[prompthu2026]] PromptHub: Enhancing Multi-Prompt Visual In-Context Learning with Locality-Aware Fusion, Concentration and Alignment (2026-03-19 2026-03-19)

## 目录结构
```
kernel/        真相层：claims.md, citations.md, review_log.md
shell/         工作层：00_idea/, 01_repo/, 02_search/, 03_evidence/papers/, 04_review/, 05_synthesis/
papers/        Zotero 同步的 PDF + MinerU 抽取产物（.md + images/）
state.md       状态机
INTAKE.md      项目输入表
AGENTS.md      agent 指令
.survey-tool/  survey-tool 的 UI 状态（compares/branches/paper-state）— pi 不读
```

## 使用
1. clone 本仓库
2. 用 pi + research-survey skill：`pi` 打开后读 AGENTS.md / state.md 继续调研
3. 或用 survey-tool 可视化：`survey`

## 数据层契约
研究内容（kernel/shell）为规范工件；.survey-tool/ 仅为前端状态。详见 survey-tool/DATA_CONTRACT.md。
