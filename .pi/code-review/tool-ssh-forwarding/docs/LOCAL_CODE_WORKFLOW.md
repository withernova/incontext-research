# 本地代码开发与服务器执行

## 结论

实验代码默认放在 Survey Tool 登记的研究项目内，用独立 Git clone 编辑。不是 Survey Tool 源码仓库的子目录。服务器保留数据、权重、日志和执行环境。私人代码仓库默认：改前远端 commit/push、本机快进同步；改后本机审阅、commit/push。默认不测试，仅用户明确要求时执行。只部署指定 commit，不自动部署或启动实验。

```text
<研究项目>/
  kernel/                           # 研究记录
  shell/                            # 研究文档
  code-repositories/<Workspace-ID>/<仓库名>/  # 独立 Git clone
```

例如：`/Users/saul/Projects/incontext/code-repositories/03/iploc-szy/`。同一 Workspace 的 Experiments 共用该代码绑定；不把一个 Experiment 放进另一个 Experiment。

代码仓库示例：<https://github.com/withernova/iploc-szy>。它不是研究项目 `.publish` 快照。

## 绑定

**默认自动绑定，不需要手填仓库、分支或本机路径。** Workspace 已登记 Server 和 `remote_repo` 即可。首次本地代码任务执行 `code prepare`：

1. 检查没有活动 Run；只读读取远端仓库的 `origin` 和当前分支，不猜 `main`。
2. 自动登记 `mode=local-git, storage=project`，计算项目内路径；远端 origin 用 SSH 时，本机首次 clone 也用 SSH。
3. 继续执行改前 checkpoint/push、首次克隆或快进同步，返回真实 `local_repo`。

未填写 `code_development` 或选择 `mode=auto` 均使用这个默认流程。网页默认选项为「自动绑定本地仓库」。生成任务 prompt 或保存 auto 选项不连接服务器、不 clone、不 push。已登记的 local-git 绑定不覆盖；发现失败、路径冲突或登记期间 Workspace/Server 变化时停止，不覆盖文件或其他配置。绑定登记成功但后续同步失败时，保留登记结果，修复 blocker 后重新 prepare。

显式 `mode=remote` 保留旧远程开发流程。用户明确要求本地编辑时，可直接执行 `code prepare` 自动转换，无需先编辑表单。绑定改变后需重新核对 Run 的执行授权；不会自动继承旧快照。

需要手动覆盖发现结果时，在 **Server / Workspace 绑定 → 编辑 Workspace → 实验代码开发仓库** 中选择「手动指定本地 Git 仓库」。填写：

1. GitHub HTTPS URL。
2. 已确认的分支。工具不猜默认分支。
3. 「代码存放位置」选「项目内独立目录」（新绑定默认）。工具计算只读路径，无需填写本机绝对路径。旧绑定可保留「已有外部目录」。
4. 高级设置中的远程代码目录，以及相应允许写入、只读和禁止路径。

「本机」是 Survey Tool 服务所在机器，不是浏览器所在机器。URL、分支、模式及 `storage=project|external` 存于 Workspace。项目内路径按当前研究项目位置计算；换机器或移动项目后不会沿用旧机器的绝对路径。只有外部目录按主机和用户保存在 `.survey-tool/local-code-bindings.json`，换机器后需重新绑定。保存不创建目录、不 clone、不连接 SSH、不推送代码。Git 凭据仍由本机和服务器原有 Git/SSH 配置管理，不在表单填写 token。自动发现记录 `transport=ssh|https`，保留 origin 的传输方式；网页仍显示不含凭据的标准 GitHub HTTPS 仓库标识。

已有 clone 必须使用匹配的 `origin`（GitHub HTTPS 或 `git@github.com:owner/repo.git`）和绑定分支。项目内目标目录不存在时，首次 `code prepare` 先确认服务器空闲、策略与仓库状态，再克隆绑定分支到该目录。它不搬动已有外部 clone。目录或任一代码路径组件是软链接、已有非 Git 目录或 origin 不匹配时停止，不覆盖。

外部目录缺失时仍需用户先按授权创建。工具不自动换 origin、checkout 或配置凭据。首次 clone 失败可能留下已预留的空目录或不完整目录；错误输出不暴露 Git stderr，也不会自动删除该目录，需核对后再处理。

## 修改前自动同步

代码任务 prompt 要求 Agent 在第一处编辑前自动执行：

```bash
python3 <tool>/surveyctl.py --project <project> code prepare --workspace-id <W>
```

首次项目内克隆和后续同步都由此命令处理，适用于 Codex 和 pi。Herdr 受管代码任务在启动 Agent 前也执行此步骤。复制 prompt 的普通终端任务由 Agent 执行该命令；工具不能拦截任意外部编辑器的文件写入。

命令检查：

- 同一服务器仓库没有活动 Run 或已领取的 lease。
- 服务器 Linux `/proc` 未发现同用户进程占用仓库；观察失败则停止。此检查不能证明其他用户的任务或仓库外部导入代码均不存在。
- 两个目录都是准确的 Git worktree 根；不是 `.publish`。
- origin、分支匹配，没有未完成 Git 操作。本机必须干净，且不得有独有未发布 commit。
- 服务器仓库、Git 元数据及改动文件符合远程目录策略，包括符号链接解析。
- 远端代码改动可自动 checkpoint：包含修改、删除及未忽略的新代码文件。数据/输出目录、模型文件、软链接、子模块、二进制、大文件及疑似凭据会阻断，不会自动删除。凭据检查是有限的启发式检查，不保证发现所有秘密；正确设置 `.gitignore`。
- 远端 fetch 后仅允许快进；已有独有 commit 可发布，分叉停止。若远端落后且工作树改动阻止快进，则停止，不 stash 或自动解决冲突。

随后自动提交远端代码改动，使用固定 checkpoint 消息，并 push 到绑定的 origin 分支。已有未发布 commit 也会发布。远端没有改动且已同步时不创建空提交、不 push。再将本机 `merge --ff-only <SHA>` 到该已发布 SHA，复核两端实际 SHA。push 目标必须匹配绑定，禁止 force/mirror push。成功返回同步凭据，记录是否提交及推送。

这是私人代码仓库 `local-git` 的默认行为，不适用于 Survey Tool 自身或未绑定仓库。保存绑定本身仍不联网。服务器同步持有独占 Git 元数据锁；local-git 受管 launcher 持有同一文件的共享锁，运行期间不能同步代码。服务器必须提供 `flock`。外部编辑器或未使用此锁的启动器不受该锁控制。工具不 stash、reset、clean、rebase 或强推。ignore 的文件不被删除或同步；不要把未纳入 Git 的代码当作已部署实现。

两机同步不是原子事务，也不保证零冲突。并发编辑或分支变化仍可造成冲突。后续步骤失败时，远端可能已经提交或 push；不会回滚、删除提交或伪造成功凭据。检查实际状态后重新运行。GitHub 认证失败是 blocker，不是「没有更新」。

## 本地实现与审阅

读取真实代码仓库的 `AGENTS.md`。只改任务允许的代码文件。数据、权重、输出和凭据不进入代码提交。

**默认不运行测试、构建、smoke 或 import/启动检查，也不新增测试 Run。只有用户明确要求时执行。** 仓库默认测试约定不算本轮授权，不得通过委派其他 Agent 绕过该要求。

对当前 diff 调用 `code_change_review`，审阅通过后用精确任务文件 checkpoint commit。未测试可省略 `test_evidence`，不为缺少测试阻断代码交付、审阅或提交。必须如实标注“未测试”；审阅不证明程序可运行，也不允许编造通过结论。

Git 状态、路径与凭据检查、代码审阅仍保留。这是 Agent 任务提示规则，不会拦截任意外部程序。若用户的提交钩子会触发测试，应先报告，不擅自绕过或禁用钩子。

提交后立即自动发布到绑定分支，不另行询问 push：

```bash
python3 <tool>/surveyctl.py --project <project> code publish \
  --workspace-id <W> --commit <完整40位SHA>
```

只接受干净本机 HEAD 的完整 SHA，以及当前绑定的改前同步凭据。上游必须仍为基线或本次 SHA；上游变化则停止，不强推。发布前检查所有待推送提交中的文件版本，包含后来已删除的版本；疑似凭据或数据/输出会阻断。

路径分类不会因为目录名为 `data` 或 `datasets` 就拒绝其中的源码。允许 Python、Shell、JS/TS、C/C++ 等明确源码后缀，例如 `tools/data/build_e014_symmetric_candidates.py`。这不是整个目录的白名单：其中的 CSV、JSON、NPZ、Notebook 等非源码后缀仍会阻断；`weights`、`checkpoints`、`outputs`、`logs` 等产物目录不因此放行。源码仍受内容扫描、大小限制、软链接限制和 Workspace 路径策略约束，包括历史中后来被删除的版本。后缀与内容扫描均为启发式检查，不保证发现所有数据或凭据。

自动发布最多检查 100 个未发布提交、1000 个不同文件内容版本，每个文件不超过 1 MB；超过限额需人工处理。重试已经成功的相同 SHA 不重复 push。发布不更新服务器工作树，不启动 Run。失败时保留本地提交并报告。

**代码审阅通过不等于本地或 Linux/CUDA 运行验证通过。** 不要因 Mac 缺少 CUDA 而改实验环境或安装未授权依赖。

## 指定 commit 部署

本地审阅过的 commit 已由 `code publish` 发布。随后获得指定 Workspace 与完整 SHA 的部署授权：

```bash
python3 <tool>/surveyctl.py --project <project> code deploy \
  --workspace-id <W> --commit <完整40位SHA> \
  --confirmation 'DEPLOY CODE <W> <完整40位SHA>'
```

确认词用于防止误操作，不替代 Agent 对人类授权的核验。工具要求本机 HEAD 等于该 SHA、commit 已发布、服务器 HEAD 仍等于上次同步/部署的 SHA，且可以 fast-forward。部署不会运行训练或测试，也不会自动更新 Run 研究设计或授权。默认只更新现有远程 clone；独立部署 worktree、Git bundle 传输尚未实现。

只有用户明确要求时执行 Linux/CUDA 测试。记录 authored SHA、deployed SHA，以及实际执行的命令和退出码；没有执行时标注“未验证”。将真实部署 SHA 填入 Run `git_commit`，再按原有工作流获得执行授权。已授权 Run 的必要 preflight 与正式执行不属于自行增加的测试，门禁不变。local-git 受管 preflight 核对实际执行目录的 origin、分支、SHA 与干净状态；launcher 在创建产物前再次检查 SHA 和状态。不同 Run worktree 也必须满足同一绑定，不自动创建或部署它。

## 阻断与修复

- 本机脏仓库、两端分叉或远端包含不可自动发布的文件：停止并报告，不覆盖。普通远端代码改动和独有 commit 由改前步骤提交及发布。
- 运行中任务：先停止/完成任务或通过既有 repair 流程处理。不要边运行边同步代码。
- 改绑定后：重新 prepare；Workspace 仓库模式/URL/分支属于执行快照，变化不能继承旧执行授权。本机路径不改变服务器执行 authority。
- local-git 默认自动 push 只适用于绑定的私人代码仓库和分支；不扩大文件修改范围，也不授权服务器部署或 Run。未绑定的 remote 模式保持原授权规则。
- Git fetch/merge/commit/push 的 stderr 不返回网页或同步凭据，避免远端 URL/凭据泄露。认证排查应在各机器本地进行。

## Publish 与迁移

`code-repositories/` 及指向其内容的软链接不进入研究 Publish 快照。每个 clone 的 `.git` 保持独立，不用研究 snapshot 仓库承载代码版本。若已有 Publish 目标含该目录，发布会阻断并要求核对、移出旧代码，不自动删除。

项目内 clone 可随研究项目迁移，包括 `.git` 和尚未提交的代码。项目复制本身不是 push 或服务器部署。迁移后重新 `code prepare`；Git 凭据与服务器连接须在目标机器独立确认。

旧配置没有 `storage` 时保持 `external` 兼容模式；选择项目内存放并保存后才切换，不移动原目录。显式模式 `remote` 保留已有远程开发流程；未登记模式默认自动绑定，不再视为必须手动绑定。上述步骤不替代人工研究判断或 Claim verdict。
