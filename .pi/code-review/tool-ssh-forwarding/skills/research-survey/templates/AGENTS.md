# AGENTS.md — <项目名>

> 本项目遵循 **research-survey** skill（全局：`~/.pi/agent/skills/research-survey`）。
> 行动前请先阅读其 SKILL.md，并遵守其中的反幻觉硬规则与项目约定（中文模板 C1、MinerU 优先 C2）。

## 项目输入（固定以下信息）
- **代码仓库路径：** `<待研究的代码仓库路径>`
- **种子论文：**（arXiv id / DOI / 本地路径）
  - <seed 1>
  - <seed 2>
- **想法（草稿）：**
  - <若干句；随研究进展迭代>
- **领域：** <例如 open-vocabulary detection / IVLOD>
- **目标会议：** <例如 CVPR / ICCV / arXiv preprint>
- **API 联系邮箱：** <你的邮箱，供 OpenAlex/Unpaywall/CrossRef 使用>

## 约束 / 备注
- <任何具体约束：backbone 为 X、必须用数据集 Y、仅单机 等>

## 工作流
- 始终从 `state.md` 恢复进度。
- 声明（claims）存于 `kernel/claims.md`；只有 `validated` 的声明才能进入综合（synthesis）。
- 引用格式 `[[citekey]] §小节`。绝不允许引用未实际抓取过的论文。
- 论文内容问答：**优先读取同名目录下 MinerU 抽取的 `.md`（含图像与公式）**；否则对 PDF 做 `read`/pdf-converter 抽取。
- 使用 `~/.pi/agent/skills/research-survey/scripts/` 下的脚本。
- 实验代码以当前 Workspace 绑定为准，不以研究 Publish 快照或上述调研输入代替。遵守 skill C3：未登记开发仓库或 `mode=auto` 时自动从远端 origin/分支建立项目内绑定，不要求人工填写。每次本地修改前先 `surveyctl code prepare`，自动提交并推送远端代码，再同步本机；本地审阅及提交后立即 `surveyctl code publish --commit <完整SHA>`。默认不测试/构建/smoke，只有用户明确要求时执行；未测试不阻断交付，必须标注‘未测试’，不得编造证据。同步或审阅失败仍停止。自动 push 仅限绑定的私人代码仓库和分支，不授权 Survey Tool 推送、服务器部署或正式 Run。不得强推、SSH patch 回退或部署 latest。