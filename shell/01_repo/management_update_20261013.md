# Agent 管理约定与入口导航更新

## 本次范围

用户先要求管理型修复，再强调 AGENTS.md 应鼓励良好管理，并要求规则给必要重构留下空间。本次优先完善项目与仓库两层 AGENTS，同时补充现有导航工具。不是对 27 项审查问题的批量修复，也不是全仓审查完成。

- 项目 `AGENTS.md`：项目层职责、合理例外与历史/权限边界；不复制仓库操作细则。
- 仓库 `code-repositories/03/iploc-szy/AGENTS.md`：少猜、少找、少复制；默认复用而非禁止重构。允许有目的地移动、合并、拆分；只按真实调用需要保留兼容，内部引用可同批迁移。小任务不强制框架化、逐文件审批或新增管理文档。
- 参数、共享能力、Run 事实分别归属配置、职责模块与 Run 记录。只有超出本次授权的接口/科学变化或不明所有权才请求确认；不重复批准已明确授权的小改动。
- `tools/audit_entrypoints.py` 继续是单一源码导航工具，没有新增 runner、worker 或配置体系。
- `tools/run/README.md` 是目录入口；Shell 顶部生成 Config/Code/forward/trace 注释。两份原索引增加相对链接和代码入口。
- `--source-only --trace PATH` 可从 Shell 或 Config 查链路；读取 WORKERS literal、analysis.entrypoint、literal -m 和明确 re-export。不导入核心包，不执行配置或 Shell，不把源码关系当历史执行事实。
- `--source-only --check-navigation` 只检查导航漂移，不证明输入/依赖/模型或任务可运行。过滤/项目视图不能覆盖全量导航。

## 版本与并发边界

初始 HEAD 为 `1622e5f64a70239d02145f017cfd991cf8318e47`，工作区干净。本次编辑期间，同一 checkout 的另一任务创建：

1. `16d1b0841ae780858efc01c3d30d135d35453f04`：保存本轮导航工具首版，标题为 docs: checkpoint user source navigation changes before sync。
2. `69f786a3db89177cea11178714f560ce5760d36c`：独立奖励变体任务，包含 reward/task/config/test/doc 及三份导航。

发现后核对变更路径，保留这两个提交，不 reset/rebase/stash，也不将奖励实现纳入本次修复。本轮剩余管理 diff 固定对照 69f786a；两次代码审阅 `86dd4ca1fea5767e` 均 passing/current，无 blocking 或 warnings。精确 98 个任务文件提交为：

`3c7ed5cdcde16c096b65021935002074f8080e51`

项目根 AGENTS.md 与本说明/state 不属于代码 Git clone，未夹入代码提交。本轮未连接远端或调用自动同步/push/deploy；不代表其他任务的发布或执行状态。

## 实际静态证据

- 当前源码导航枚举 130 Config / 88 Shell。比原审查基线多出的奖励配置来自并发提交，不是本任务新科学方案。
- source-only 导航生成与漂移检查成功；实际查询 SFT 快捷入口与 chain-rule analyze 入口，能找到 alias/canonical 配置、worker 与 analysis function。
- 88 Shell 去除本工具拥有的导航注释后，其余字节逐文件与 69f786a 完全相同；88 `bash -n` 均退出 0。不能据此说 A016 的路径计算问题已修复。
- 1608 个生成的 Markdown 相对链接均指向仓库内现存文件。只证明路径存在，不证明内容或执行语义。
- 导航工具与 test_config_migration 两个 Python 文件通过标准库 Python 3.9 AST 解析。
- `git diff --check` 退出 0；当前管理 diff 没有核心包或 recipe 参数变化。
- 测试定义已补注释 roundtrip、导航漂移、alias/re-export、trace 与过滤防覆盖，**未执行测试**。没有构建、import/smoke、模型、实验或服务器验证。

第一次生成实际拒绝无 shebang 的 sourced helper `tools/run/_common.sh`；在第一处写入之前停止。随后补充只对该 helper 在文件头放纯注释的支持，保留原主体，重新生成成功。一次读取假定存在的旧 r011 Shell 返回 ENOENT；真实旧目录没有该 alias，因此测试定义改用确实存在的 bbox-gradient alias，不登记为缺失入口。

## 保持与剩余事项

本轮只增加管理约定和源码可发现性；未搬动源码目录、删除归档、改接口、算法、训练参数、历史 Run 或产物。不把所有旧路径永久冻结，也不在本轮自动实施大规模迁移。

全仓审查仍保留原 `1622e5f` 基线，findings 已有 27 项；其余语义覆盖与最终要求审计未完成。当前新 HEAD 不是全仓已通过审查的版本。27 项中的科学/运行问题仍按各自触发条件处理，未自动修复或重跑。
