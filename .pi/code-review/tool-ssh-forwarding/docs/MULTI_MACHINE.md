# 多机器同步

建议把“工具”和“科研项目”分开同步：

```text
survey-tool GitHub 仓库     → 同步工具源码、skill、steward
每个 research project 仓库 → 同步 kernel/、shell/、state.md、index/
每台机器本地              → config.json、.pi/、.survey-tool/、日志和远程产物
```

新机器：

```bash
git clone git@github.com:withernova/survey-tool.git
cd survey-tool
cp config.example.json config.json
# 修改 projects_root / projects / skill_dir
./scripts/install-pi-components.sh
python3 server.py
```

日常升级：

```bash
cd survey-tool
git pull --ff-only
```

注意：

- 不同步包含绝对路径的 `config.json`；每台机器各自维护。
- 不同步 steward 当前队列、运行日志、SSH 配置、Zotero 数据库、checkpoint 或远程 artifacts。
- 新机器只安装 `experiment-steward`；旧 Watchdog 文件可被兼容读取，但旧扩展不得与新扩展同时安装。
- 安装脚本同时链接 `research-explorer` skill/extension。Explorer scheduler 是 project-local；迁移项目时保留 canonical `shell/07_explorations/` 和 registry，重启后不会自动恢复轮次。
- 科研项目的 canonical Markdown 才是跨机器研究事实；提交前先保存 UI 编辑，换机器前 push，开始工作前 `git pull --ff-only`。
- 同一科研项目不要在两台机器同时修改同一 canonical Markdown；若发生冲突，人工合并，不用 `.survey-tool/*.json` 覆盖 canonical 内容。
- pi 组件使用符号链接安装；更新工具仓库后不需要再次复制代码，必要时在 pi 中 `/reload`。

从现有机器搬到新机器（含 macOS）可以用脚本一次完成，见 [MAC_MIGRATION.md](MAC_MIGRATION.md)：

```bash
bash scripts/migrate-machine.sh --source-host <源机器别名> --dry-run
```
