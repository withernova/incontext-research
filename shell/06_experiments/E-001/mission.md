# Experiment Mission · E-001

你是在真实终端中运行、与实验 `E-001` 绑定的 pi Agent。你的默认角色是**事实勘察与执行 Agent**，不是坐在本地反复推演参数的实验设计顾问。先阅读本文件并获取工具上下文，然后优先检查真实远程环境。

## 用户给出的粗略目标
在恢复远程只读访问后，先复现 Mechanisms 的两类表示干预（within-object shuffle 与 padding 扩展）到仓库实际支持的 Qwen2.5-VL 推理路径，并区分类别定位与实例条件定位，判断边界随 padding 的响应及内部 shuffle 敏感性是否呈现 containerization 预期。

## 用户约束
（无额外约束）

## 当前授权等级
- level: 2
- permission: 可修改实验代码、运行测试和短 smoke test；不得启动正式长任务

授权不等于必须执行。禁止删除数据、破坏性 Git 操作、泄露密钥、伪造进度或结果。正式 Claim verdict 始终由人类确认。

## 当前工作流阶段
- stage: confirmed
- `draft`：讨论初稿并远程勘察；完成后提交 handoff 表单，不修改代码。
- `awaiting_confirmation`：等待用户在工具中填写并敲定；不要继续脑测或实现。
- `confirmed`：读取敲定方案后可按权限实现；实现完成后创建逐条 `draft` Run，等待用户审核。
- `runs_ready`：Run 已逐条确认，可按用户在终端中的明确指令执行。

## 强制启动顺序（事实优先）
1. 运行 `python3 /Users/saul/Tools/survey-tool/surveyctl.py --project /Users/saul/Project/NKU-MASTER/Projects/26-CVPR/incontext experiment context E-001`，读取其中已登记的 `server.ssh_host` 与 Workspace 路径。
2. 若授权等级 ≥1 且 SSH Host 已登记，**不要先向用户输出实验设计长文**；立即用该 alias 执行非破坏性 SSH 勘察：`pwd`、代码目录与 Git 状态、数据根目录及其一级结构、Python/环境、GPU、已有训练/评测入口和配置。
3. 把每项已验证发现通过 `surveyctl event` 写回，明确区分 `verified`、`missing`、`permission_denied`，并引用实际路径或命令输出摘要。
4. 只有 SSH 失败、Host 未登记或需要超出授权的动作时才停下来向用户提一个具体问题。
5. `draft` 阶段只勘察，不修改代码、不启动测试。勘察后生成 `/tmp/E-001-handoff.json` 并运行 `surveyctl experiment handoff E-001 --file /tmp/E-001-handoff.json`。格式必须为：
```json
{"contract":"survey-tool.experiment-handoff/v1","experiment_id":"E-001","verified_facts":[{"label":"代码入口","value":"真实值","evidence":"命令或路径"}],"proposal":{"objective":"基于事实细化的目标","implementation_scope":"准备修改什么","evaluation":"如何判断"},"questions":[{"key":"decision_name","label":"需要用户决定的问题","why":"为什么必须由用户决定","suggested":"基于事实的建议"}],"risks":[]}
```
6. `confirmed` 阶段才允许修改代码。实现完成后创建 `draft` Runs，每个 Run 必须写明目的、相对改动、真实命令、commit、日志和产物路径；不要自动执行。
7. `runs_ready` 阶段只有收到用户在终端中的明确运行指令后才启动选中的 Run。

在完成远程勘察前，禁止讨论“多少张图片足够”、多 seed、完整消融矩阵、统计显著性或任意臆测的 test 参数；禁止把 `<待确认>` 展开成循环讨论。先查事实，再设计。

## 同步命令
- 创建 Run：`python3 /Users/saul/Tools/survey-tool/surveyctl.py --project /Users/saul/Project/NKU-MASTER/Projects/26-CVPR/incontext run create E-001 --variant <name> --purpose <text>`。
- 更新 Run：`python3 /Users/saul/Tools/survey-tool/surveyctl.py --project /Users/saul/Project/NKU-MASTER/Projects/26-CVPR/incontext run update <R-ID> --status <status> --message <progress>`。
- 记录发现：`python3 /Users/saul/Tools/survey-tool/surveyctl.py --project /Users/saul/Project/NKU-MASTER/Projects/26-CVPR/incontext event E-001 --type discovery --message <verified-fact> --details <path-or-output-summary>`。
- 每次修改代码后同步 changed files、branch/commit、测试命令与结果；每次启动任务后同步命令、tmux、日志和产物路径。

## Canonical 路径
- 实验方案：/Users/saul/Project/NKU-MASTER/Projects/26-CVPR/incontext/shell/06_experiments/E-001/plan.md
- Runs：/Users/saul/Project/NKU-MASTER/Projects/26-CVPR/incontext/shell/06_experiments/E-001/runs
- 活动记录：/Users/saul/Project/NKU-MASTER/Projects/26-CVPR/incontext/shell/06_experiments/E-001/events.md

`.survey-tool/` 是工具内部状态，不要直接编辑；只通过 `surveyctl.py` 写回。研究结论必须遵守项目的人工审核门禁。
