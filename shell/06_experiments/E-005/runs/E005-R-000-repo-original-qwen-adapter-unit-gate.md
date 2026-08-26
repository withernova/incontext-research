# E005-R-000-repo-original-qwen-adapter-unit-gate · repo-original Qwen适配单元门禁

- canonical_run_id: `E005-R-000-repo-original-qwen-adapter-unit-gate`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed

## 本轮目的
验证不改上游代码的Qwen3-VL最小适配层是否严格保持官方analyze行为，并正确处理动态矩形grid和双图视觉span。

## 必要性 / 证据链位置
在真实Qwen attention采集前排除selection逻辑漂移、span错位和静默reshape错误。

## 研究依据 / 被审计对象
LocalizationHeads官方仓库commit 9ffe219；用户确认采用repo-original参数。

## 实现方式（简版）
方形grid与上游逐项比对；新增矩形grid与Qwen双图span严格映射；模型collector输出保持[L,H,1,V]。

## 实现方式（详细版）
上游快照零修改。analyze_rect仅把P×P推广到HxW，其chord threshold、ReLU(A-2mean)、attention-mass entropy、bottom-row filter、layer>1和fallback均复制上游行为。qwen_spans按image_token连续run与image_grid_thw/spatial_merge_size做一一对齐，不一致直接失败。

## 数据身份与构造
确定性合成attention tensors与合成Qwen input_ids/image_grid_thw；不含真实图像或科学样本。

## 数据规模
5个CPU单元测试；方形、矩形、双图、fake model collector、错误输入各一类。

## 模型、权重与关键配置
无真实模型；fake collector contract。依赖远端torch2.2.2、scipy1.11.4。官方逻辑参数保持。

## 变量、干预与对照
核心对照为adapter square output == upstream analyze.py output；错误span必须hard fail。

## 指标与计数规则
测试通过数；方形selected records完全相等；attention extraction tensor完全相等；upstream源码hash完整性。

## 完整性门槛 / no-silent-zero
5/5 tests；py_compile；上游hash清单不变；禁止模型/科学结论。

## 观测结果摘要
（待补充）

## 局限与混杂因素
仅工程单元测试；没有真实Qwen forward、显存测试、attention结果或head ranking。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
只支持适配实现的工程正确性，不支持存在localization heads或任何因果机制结论。

## 关键指标
（待补充）

## 审核入口
shell/06_experiments/_legacy/codespace/e005_adapter; shell/06_experiments/_legacy/codespace/LocalizationHeads_upstream_sha256.txt; /home/featurize/work/mechanism/explog/E-005/runs/E005-R-000-repo-original-qwen-adapter-unit-gate

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
PYTHONNOUSERSITE=1 PYTHONPATH=env/lama_site:env/e004_site:third_party/LocalizationHeads:scripts/e005/adapter python scripts/e005/adapter/test_repo_compat.py

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-000-repo-original-qwen-adapter-unit-gate/logs/test.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-000-repo-original-qwen-adapter-unit-gate/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-000-repo-original-qwen-adapter-unit-gate

### tmux session
（待补充）

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-000-repo-original-qwen-adapter-unit-gate
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-000-repo-original-qwen-adapter-unit-gate/logs/test.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-000-repo-original-qwen-adapter-unit-gate/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-000-repo-original-qwen-adapter-unit-gate/metrics.json
- tmux_session: incontext-E-005-E005-R-000-repo-original-qwen-adapter-unit-gate
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T13:53:11
- updated: 2026-07-24T13:53:11

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
