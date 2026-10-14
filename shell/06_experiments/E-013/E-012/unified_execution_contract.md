# E-012：R-004–R-010 统一启动、日志与产物合同

> 状态：实现规范，不是执行授权。适用当前双角色新主线；历史 E-012 Run 保留原样，不追溯改写其产物。

## 1. 唯一启动链

所有可由脚本启动的 R-004–R-010 必须使用：

```text
tools/run/e012_dual_role_analysis.sh
  → Python config
  → tools/launch.py
  → tools/analyze.py
  → analysis.entrypoint
```

要求：

- Shell 只接受一个可选 config 路径和 `--inspect`；
- checkpoint、manifest、样本、head、阈值、seed、输出目录都必须写在 Python config；
- 不允许每个 Run 新写一套含硬编码日志路径的 Shell；
- 不允许 launcher 使用 `tee -a` 把多次运行混入同一个 Experiment 级日志；
- 不允许绕过 `tools/launch.py` 直接运行 Python module 作为正式命令；
- `--inspect` 只打印解析后的 worker 命令，不创建 output directory。

R-004 默认 config：

```text
configs/head_screening/e012_contribution_calculation_check.py
```

R-005–R-010 后续各增加一个薄 config，均复用同一 Shell、launch action 和公共 worker；不得复制公共执行逻辑。

## 2. 目录与日志

每个 canonical Run 使用自己的新 `work_dir`，已有目录拒绝覆盖：

```text
experiments/E-012/<canonical-run-id>/
├── logs/
│   ├── console-<uuid>.log
│   └── config_snapshots/
│       └── analyze-<uuid>/
│           ├── resolved.json
│           ├── provenance.json
│           ├── 00-<config>.py ...
│           └── prompt_implementation.py
├── status.json
├── input_manifest.json
├── records.jsonl
├── integrity.json
└── summary.json
```

职责：

- `tools/launch.py`：创建全新的 `work_dir`、`logs/console-<uuid>.log`，同步输出到终端与日志；
- `tools/analyze.py`：调用 `save_snapshot()`，原子写 `status.json`，统一记录 running/completed/failed；
- analysis entrypoint：写科学 records、integrity、summary；不能自行决定另一套日志根目录；
- traceback 写入 `status.json` 和 console log；失败不得写科学 completed summary。

## 3. Config 必填字段

每个 config 至少包含：

```python
launch = dict(action="analyze", nproc_per_node=1)
work_dir = ".../experiments/E-012/<canonical-run-id>"
analysis = dict(
    run_id="<canonical-run-id>",
    entrypoint="python.module:function",
    metric_contract=dict(
        schema="e012.dual-role-head-metrics/v1",
        sha256="bab83a1f...",
    ),
    required_parameters=dict(...),
)
```

`required_parameters` 中尚未冻结的值保持 `None`。worker 必须先调用 `validate_analysis_contract()`；存在任何 `None` 就 fail closed。不得在 worker、Shell 或环境变量中补隐式默认。

敏感路径或凭据不得写入日志；模型、数据和 checkpoint 路径是实验 provenance，可写 config snapshot，但不得从环境变量偷偷覆盖。

## 4. Run 对应关系

| Run | config | entrypoint 状态 |
|---|---|---|
| R-004 | `e012_contribution_calculation_check.py` | 当前仅 scaffold；参数冻结且模型 hook 实现前明确拒绝运行 |
| R-005 | 待 implementation planning | 必须复用公共 worker |
| R-006 | 待 implementation planning | 与 R-005 同入口，通过 config 的 `visual_role` 切换 |
| R-007 | 待 implementation planning | 只读冻结 candidates，复用公共 worker |
| R-008 | 待 implementation planning | 复用公共 worker和指标模块 |
| R-009 | 条件触发后设计 | 不提前创建独立 launcher |
| R-010 | 条件触发后设计 | 不提前创建独立 launcher |

## 5. 当前已实现与未实现

已实现：

- `tools/launch.py` 的单进程 `analyze` action；
- `tools/analyze.py` 的 config 加载、snapshot、统一 status 与异常记录；
- 一个公共 Shell；
- R-004 fail-closed config scaffold；
- `dual_role_metrics.py` 的纯指标原语和合同校验。

未实现：

- 真实 Qwen forward/backward hooks；
- manifest split builder；
- R-004 科学 records；
- R-005–R-010 entrypoints/configs；
- 任何 GPU 执行。

因此当前只能做静态解析、`--inspect` 和 CPU 测试；不得把 scaffold 当作 implementation-ready。
