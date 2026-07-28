# E005-R-001-qwen3vl-model-recovery-localdisk · Qwen3-VL本地盘模型恢复

- canonical_run_id: `E005-R-001-qwen3vl-model-recovery-localdisk`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
completed_passed

## 本轮目的
恢复服务器重启后丢失的Qwen3-VL-8B-Instruct本地snapshot，为真实attention采集提供可审计模型输入。

## 必要性 / 证据链位置
E-005单样本真实forward必须加载与E-004一致的Qwen3-VL基座；当前snapshot已验证缺失。

## 研究依据 / 被审计对象
远端find未发现Qwen3 snapshot；历史E004-R-004c证明server-local serial download可成功而NFS下载有I/O风险。

## 实现方式（简版）
使用huggingface_hub snapshot_download、hf-mirror、max_workers=1下载到server-local HF cache，并检查config和safetensors分片。

## 实现方式（详细版）
保持HF_HUB_DISABLE_XET=1，下载仅写/home/featurize/.cache/huggingface；记录snapshot path、weight file数、总字节和config SHA-256。

## 数据身份与构造
Qwen/Qwen3-VL-8B-Instruct官方模型snapshot；不含实验样本。

## 数据规模
单个8B模型snapshot。

## 模型、权重与关键配置
repo_id=Qwen/Qwen3-VL-8B-Instruct；server-local cache；max_workers=1；HF_ENDPOINT=https://hf-mirror.com。

## 变量、干预与对照
只恢复模型，不运行IPLoc-ID forward或产生head指标。

## 指标与计数规则
required config存在、safetensors分片数>0、权重总字节、config SHA-256。

## 完整性门槛 / no-silent-zero
snapshot_download正常退出；config.json与generation_config.json存在；至少一个safetensors文件。

## 观测结果摘要
模型恢复成功；tmux retained pane正常以exit status 0结束。snapshot完整性门禁通过。

## 局限与混杂因素
模型下载是基础设施恢复，不是科学run；snapshot位于易失本地盘，服务器再次重启仍可能丢失。

## 可支持的结论
Qwen3-VL基座已可用于后续真实attention smoke；不构成模型行为或localization-head结果。

## 不支持的结论 / Claim 边界
不支持任何localization-head或模型行为结论。

## 关键指标
16/16 files；4个safetensors；17,534,339,512 bytes；config SHA-256=5cd452860dc1e9c29dd71cc3cef7f39b338b7a40793f7a260655c2d3568f3661。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-001-qwen3vl-model-recovery-localdisk

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
/home/featurize/work/mechanism/scripts/e005/e005_r001_reload_model.sh

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-001-qwen3vl-model-recovery-localdisk/logs/download.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-001-qwen3vl-model-recovery-localdisk/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-001-qwen3vl-model-recovery-localdisk

### tmux session
e005_model_recovery

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-001-qwen3vl-model-recovery-localdisk
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-001-qwen3vl-model-recovery-localdisk/logs/download.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-001-qwen3vl-model-recovery-localdisk/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-001-qwen3vl-model-recovery-localdisk/metrics.json
- tmux_session: e005_model_recovery
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T13:54:01
- updated: 2026-07-24T14:21:05

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
