# 迁移到 Mac（或任意新机器）

目标：把 **survey-tool 工具 + 科研项目 + 本机状态**从当前机器搬到 Mac，使研究管理、UI、pi 工作流
在源机器关机（例如实验室停电）期间继续可用。设计前提见 [MULTI_MACHINE.md](MULTI_MACHINE.md)：
canonical Markdown 是跨机器事实，`config.json` / `~/.pi` / SSH / Zotero 每台机器各自维护。

脚本：`scripts/migrate-machine.sh`（在**新机器**上运行，通过 ssh 从源机器**拉取**）。

## 0. 先决条件（在新机器上）

- 能免密 ssh 到源机器：`ssh <源机器别名> true` 无提示通过
  （别名写在新机器 `~/.ssh/config`；本仓库不参与，脚本也不会修改你的 ssh 配置）
- 若该别名的 ssh 配置里带 `RemoteForward` / `LocalForward`（很常见），本机相应端口被占时
  连接会直接失败。脚本对所有 ssh/scp/rsync 默认加 `ClearAllForwardings=yes` 规避，
  自测时可以用 `ssh -o ClearAllForwardings=yes <别名> true` 复现同样的行为。
- 有 `rsync`、`python3`、`curl`（macOS 自带；`rsync` 为 openrsync 也可用）
- Python：工具**只用标准库**，macOS 自带 `python3` 即可（静态检查未发现 3.10+ 语法/标准库依赖）；
  想更省心可 `brew install python@3.12`。不需要 `pip install` 任何东西。
- 磁盘：默认要 **~1.1GB**（项目，不含 `.publish` 与 `research_tmp`）+ ~200MB（工具）。

源机器侧要求：**先停掉 survey-tool 服务**再迁移，避免 `.survey-tool/*.sqlite3` 出现半写状态
（脚本检测到源上仍有 `server.py` 进程会直接拒绝，除非显式 `--allow-running-server`）。

## 1. 取脚本并预演

先在**源机器**上确认脚本是最新版（否则会用到旧版而报莫名其妙的错，例如 macOS bash 3.2 下的
`SOURCE_HOST\xef: unbound variable`）。注意：scp 可能覆盖到别的位置或静默失败，因此先用 `cat` 重定向，
并核对校验和 / 版本号：

```bash
# 在新机器上
rm -f ~/migrate-machine.sh
ssh <源机器别名> 'cat ~/Tools/survey-tool/scripts/migrate-machine.sh' > ~/migrate-machine.sh

# 校验（源机器上：shasum -a 256 ~/Tools/survey-tool/scripts/migrate-machine.sh）
shasum -a 256 ~/migrate-machine.sh
grep -c ClearAllForwardings ~/migrate-machine.sh     # 最新版 = 3（旧版 = 0）

# 跑起来第一行会打印版本号，一眼看出是不是旧文件：
bash ~/migrate-machine.sh --source-host <源机器别名> --dry-run | head -1
# ==> 阶段 0/7 · 预检（migrate-machine.sh 2026-10-01，bash3.2 安全版）
```

更稳的做法：不落盘，直接跑源机器上的最新版（脚本无自引用路径，支持 `bash -s`；内部 ssh/rsync 已用 `-n -T` 保护 stdin 与 PTY）：

```bash
ssh <源机器别名> 'cat ~/Tools/survey-tool/scripts/migrate-machine.sh' \
  | bash -s -- --source-host <源机器别名> --dry-run
```

`--dry-run` 不写任何文件（rsync `-n`），用于确认源/目标路径与排除项。

## 2. 正式迁移

```bash
bash ~/migrate-machine.sh --source-host <源机器别名> \
  --dest-root "$HOME" \
  --emit-ssh-config
```

脚本分 7 个阶段，每步都有输出：

| 阶段 | 内容 |
|---|---|
| 0 预检 | 依赖、ssh 连通、源路径、源服务是否仍在运行 |
| 1 工具仓库 | rsync `survey-tool/`（**含 `.git`**，所以未 push 的提交也随之过去；`config.json` 除外） |
| 2 config.json | 生成新机器专属 `config.json`（路径指向新机器；继承 `github_repo`/`github_branch`/`freeze_legacy_writes`，不继承路径） |
| 3 科研项目 | rsync 项目目录（默认排除 `.publish/`、`research_tmp/`、`__pycache__`、`codespace`） |
| 4 pi | 拷 `~/.pi/agent/settings.json`、`multi-workspace.json`（清空 Windows 专属 `/mnt/...` 路径）；按需装 skills/extensions 软链 |
| 5 ssh 建议 | 生成 `<dest-root>/.ssh/config.survey-tool-suggested`（按 servers.json 里的 ssh_host 解析出 HostName/User/Port/IdentityFile），**只生成不安装** |
| 6 校验 | 两侧 `.survey-tool/{runs,experiments,workspaces,servers}.json` 的 sha256 与 sqlite 大小逐项对比，失败即退出 |
| 7 健康检查 | 在新机器上启动服务器并请求 `/api/v2/health`，然后关掉 |

常用选项：

```text
--with-publish-mirror    连 .publish 一起拷（默认不拷；UI 里也能重新同步）
--with-research-tmp      连 E-009/research_tmp 一起拷（约 400MB 的代码 clone）
--with-pi-sessions       连 ~/.pi/agent/sessions（agent 历史）一起拷
--no-pi-state            不拷 pi 的 settings / multi-workspace
--skip-pi-components     不执行 scripts/install-pi-components.sh
--skip-smoke-test        跳过健康检查
--transport MODE         auto（默认）/ rsync / tar；auto 在本机 rsync 是 openrsync 时自动改用 tar
--port N                 新机器端口（默认沿用源的 port）
--no-verify              跳过校验（不建议）
--allow-running-server   源机器仍在跑服务时也继续（自行承担 sqlite 风险）
--local-source           源就是本机：自检/预演/先打包
```

### 传输方式（`--transport`）

- `rsync`：默认优先。注意 rsync 的协议数据**走 ssh 的 stdin**，所以给 rsync 的 `-e ssh`
  绝不能加 `-n`（脚本已区分处理：控制用的 ssh 用 `-n -T`，rsync 的 `-e` 只用 `-T`）。
- `tar`：在源端打包、本地解包（`ssh … 'tar -cf - …' | tar -xf -`），排除项由源端 tar 应用。
  macOS 自带的 `/usr/bin/rsync` 是 **openrsync**，与远端 GNU rsync 3.x 握手会直接断流
  （`connection unexpectedly closed (0 bytes received)` / `unexpected end of file`）；
  `auto` 检测到 openrsync 会自动切到 tar，无需 Homebrew。
- 想用真正的 GNU rsync（可选、更快）：`brew install rsync` 后重跑，`auto` 会重新选 rsync。

## 3. 新机器上的人工后续（脚本故意不代做）

1. **SSH 私钥**：脚本**不拷私钥**。新机器要准备自己的密钥，并把公钥加到远端服务器
   `authorized_keys`（或用同一把密钥，但那是安全决定，请自己权衡）。
2. **ssh 配置**：把 `~/.ssh/config.survey-tool-suggested` 的内容合并进 `~/.ssh/config`
   （注意：`Include` 若写进某个具名 `Host` 块内，只对该主机生效）。
3. **GitHub**：`git` 身份与 `gh auth login` 需要在新机器上重做（发布 snapshot 用）；
   用来推送 `.publish` 的 key 也要就位。
4. **Zotero**：如用论文库，把 `~/.pi/agent/multi-workspace.json` 的 `workspaces.zotero.path`
   指向新机器的 Zotero 数据目录（脚本已把 Windows 专属路径清空）。
5. **pi**：在新机器上重新登录，并在 pi 里 `/reload` 让 skills/extensions 软链生效。
6. **Workspace 复核**：UI → Workspace 页确认 `remote_repo` / `remote_data_root` / 实验输出根仍是远端真实路径。
7. **`.publish`**：需要镜像就 `git clone <snapshot remote> .publish`（历史上它只是快照，可从 GitHub 重建）。

## 4. 停电/切换场景的推荐顺序

```text
源机器：UI 里保存所有编辑（canonical Markdown 落盘）→ 停掉 survey-tool 服务
新机器：跑本脚本（会校验两侧状态一致性）
验证：  UI 能打开、Workspace 页面正确、需要的话 `git push` 一次 snapshot
然后源机器可以安全关机；恢复供电后按 MULTI_MACHINE.md 的纪律 pull/push 合并内容
```

同一项目的 canonical Markdown **不要**两台机器同时改；`.survey-tool/*.json` 是每机器 UI 状态，
不要用其中一台的状态文件去覆盖另一台的 canonical 内容。

## 5. 排错

| 现象 | 处理 |
|---|---|
| `无法免密 ssh 到源机器` | 先在新机器 `ssh <别名> true` 调试；检查别名、端口、密钥、known_hosts |
| 阶段 0 报"源机器上 survey-tool 仍在运行" | 在源机器停掉服务，或用 `--allow-running-server` 承担风险 |
| 阶段 6 出现 `DIFF .survey-tool/...` | 源侧仍在写入（服务没停干净）。停服后重跑；**校验失败时不要删除源数据** |
| 阶段 7 健康检查失败 | 看 `/tmp/survey-tool-migrate-smoke.log`；常见是端口被占（换 `--port`）或 python 太老 |
| `rsync: connection unexpectedly closed (0 bytes received)` / `protocol incompatibility` | （a）旧版脚本给 rsync 的 `-e` 加了 `-n`，把协议流接到 /dev/null → 用新版；（b）本机 rsync 是 openrsync 与远端 GNU rsync 不兼容 → 用 `--transport tar` 或 `brew install rsync` |
| 脚本打印到 `源机器：...` 之后就静默结束 | 你用的是带管道（`ssh ... \| bash -s`）的**旧版**脚本：ssh 默认会把 stdin 转发给远端，于是把管道里的脚本正文吃掉了。新版已给 scp/ssh/rsync 加 `-n -T`（并改用 `ssh cat` 代替 scp）。改用新版，或改成落盘执行 `bash ~/migrate-machine.sh ...` |
| `bash: line 1: #!/usr/bin/env: No such file or directory` | 你本地那份脚本被加了 BOM（编辑器/剪贴板常见）或是 CRLF。用 `ssh <别名> 'cat .../migrate-machine.sh' > ~/migrate-machine.sh` 重取，或直接用管道模式（`ssh ... \| bash -s --`） |
| `Refusing to replace existing deprecated non-symlink: .../extensions/experiment-watchdog` | 新机器上已经有真实的旧扩展（不是软链），安装器故意拒绕替换。新版脚本此时**只告警不中断**：按提示 `mv` 移开旧目录，再单独执行 `PI_AGENT_DIR=~/.pi/agent <dest-tool>/scripts/install-pi-components.sh` 即可 |
| macOS 上 rsync 报不支持的参数 | 脚本只用 `-a`（`--dry-run` 时加 `-n -i`）；如 openrsync 仍报错，用 `SURVEY_TOOL_RSYNC_ARGS='--protocol=29'` 追加参数 |
| ssh 报 `Address already in use` / `Could not request local forwarding` | 你 `~/.ssh/config` 里该别名带了 RemoteForward/LocalForward 且端口被占。脚本对所有 ssh/scp/rsync 默认加 `ClearAllForwardings=yes`（不改你的配置）；确实需要转发时用 `SURVEY_TOOL_KEEP_FORWARDS=1` 关掉这个行为 |
| 报 `SOURCE_HOST\xef...: unbound variable` | 你跑的是旧版脚本（macOS bash 3.2 把 `$VAR` 后多字节字符的首字节吞进变量名）。先看首行版本号：应为 `migrate-machine.sh 2026-10-01`；再 `grep -c ClearAllForwardings`（应 = 3）；或直接用 `ssh <别名> 'cat .../migrate-machine.sh' \| bash -s -- ...` 跑最新版 |
| 健康检查后端口仍被占 | 脚本会 kill 自己启动的服务器；若输出 `健康检查服务器未退出`，按提示的 PID 手动 kill |
| 脚本报“源机器上 survey-tool 仍在运行” | 先在源机器停服（`kill <PID>`），确认 `pgrep -af server.py` 为空再跑 |
