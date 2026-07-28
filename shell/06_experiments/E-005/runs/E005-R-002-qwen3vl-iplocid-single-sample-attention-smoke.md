# E005-R-002-qwen3vl-iplocid-single-sample-attention-smoke · Qwen3-VL/IPLoc-ID单样本真实attention smoke

- canonical_run_id: `E005-R-002-qwen3vl-iplocid-single-sample-attention-smoke`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
failed_preflight

## 本轮目的
确认RTX3090 24GB上eager attention、IPLoc-ID LoRA、双图span与repo-original分析可以端到端运行。

## 必要性 / 证据链位置
正式跨样本head discovery前必须验证真实模型的attention shape、显存、finite和visual-grid映射。

## 研究依据 / 被审计对象
R-000适配门禁和R-001模型完整性门禁均通过；复用E004-R-006已审计synthetic manifest首样本。

## 实现方式（简版）
加载本地Qwen3-VL基座和IPLoc-ID LoRA，max_side=224，eager attention；分别提取最后输入token到reference/query图像span并运行repo-original分析。

## 实现方式（详细版）
严格offline；两次确定性forward分别提取双图span，保存attention tensor和metadata。使用合成double-panel query，仅做工程门禁。

## 数据身份与构造
E004-R-006 manifest首个airplane样本：reference A和synthetic query AB；无candidate prefix。

## 数据规模
1个prompt，2个image spans，2次forward。

## 模型、权重与关键配置
Qwen3-VL-8B-Instruct snapshot 0c351d + IPLoc-ID LoRA；bf16；device_map=auto；attn_implementation=eager；max_side=224。

## 变量、干预与对照
不比较处理组；reference与query使用同一prompt/同一模型设置；最后输入文本token作为query。

## 指标与计数规则
attention shape、finite、grid/span一致性、eager backend、peak allocated/reserved GPU memory、selected head count。

## 完整性门槛 / no-silent-zero
两图spans；36层×32heads×1 query；V=merged H×W；无NaN/Inf；eager；正常退出。

## 观测结果摘要
模型加载前失败：服务器重启后LaSOTTesting原始reference image缺失；synthetic query仍存在。

## 局限与混杂因素
synthetic query、单样本、低max_side；只验证工程可行性，不能发现稳定heads。

## 可支持的结论
这是输入数据恢复问题，不是eager attention或模型失败；保留本Run，不覆盖。

## 不支持的结论 / Claim 边界
通过仅允许进入小规模pilot；raw attention不是因果证据。

## 关键指标
0 model forwards；FileNotFoundError=reference /home/featurize/data/LaSOTTesting/airplane-1/img/00002788.jpg。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-002-qwen3vl-iplocid-single-sample-attention-smoke

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
/home/featurize/work/mechanism/scripts/e005/e005_r002_attention_smoke.py --max-side 224

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-002-qwen3vl-iplocid-single-sample-attention-smoke/logs/smoke.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-002-qwen3vl-iplocid-single-sample-attention-smoke/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-002-qwen3vl-iplocid-single-sample-attention-smoke

### tmux session
e005_attention_smoke

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-002-qwen3vl-iplocid-single-sample-attention-smoke
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-002-qwen3vl-iplocid-single-sample-attention-smoke/logs/smoke.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-002-qwen3vl-iplocid-single-sample-attention-smoke/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-002-qwen3vl-iplocid-single-sample-attention-smoke/metrics.json
- tmux_session: e005_attention_smoke
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T14:27:27
- updated: 2026-07-24T14:28:44

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
