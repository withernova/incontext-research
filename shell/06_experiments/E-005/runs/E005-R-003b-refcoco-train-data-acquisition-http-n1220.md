# E005-R-003b-refcoco-train-data-acquisition-http-n1220 · RefCOCO train数据获取HTTP恢复

- canonical_run_id: `E005-R-003b-refcoco-train-data-acquisition-http-n1220`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
aborted_by_user_scope_change

## 本轮目的
使用官方COCO CDN的HTTP端点恢复1220个固定RefCOCO图像分区。

## 必要性 / 证据链位置
R-003的HTTPS被代理证书hostname mismatch阻塞；不能关闭TLS验证。

## 研究依据 / 被审计对象
curl HTTP官方CDN返回200；HTTPS hostname mismatch。

## 实现方式（简版）
除source URL从HTTPS改为HTTP外，抽样、分区和完整性gate与R-003相同。

## 实现方式（详细版）
官方images.cocodataset.org；不禁用证书验证；失败attempt独立保留。

## 数据身份与构造
RefCOCO train第三方HF metadata、官方COCO CDN图像。

## 数据规模
1220 unique：20/1000/200。

## 模型、权重与关键配置
无模型。

## 变量、干预与对照
固定seed/revision/unique image；仅传输协议改变。

## 指标与计数规则
valid/failure/split counts/size/bbox/hash。

## 完整性门槛 / no-silent-zero
1220有效、0失败、20/1000/200。

## 观测结果摘要
用户决定E-005直接优先使用自有IPL oc-ID/LaSOT任务数据，RefCOCO下载已主动停止。

## 局限与混杂因素
作者精确subset未公开；第三方metadata；HTTP无传输加密但图像逐个解析与尺寸验证，metadata parquet有SHA-256。

## 可支持的结论
该run仅记录被终止的数据获取，不构成数据集或科学结果；已下载COCO数据不得混入后续自有数据pilot。

## 不支持的结论 / Claim 边界
仅支持数据pilot准备。

## 关键指标
停止时本地已有91个图像文件；最后完整进度50/1220 valid，0 failure；未生成完整manifest，不进入任何分析。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-003b-refcoco-train-data-acquisition-http-n1220

## 过程记录与补充细节
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
e005_r003_refcoco_acquire.py --n 1220 --seed 20260724

### 配置/超参数
（待补充）

### Seed
（待补充）

### 日志路径
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-003b-refcoco-train-data-acquisition-http-n1220/logs/acquire.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-003b-refcoco-train-data-acquisition-http-n1220/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-003b-refcoco-train-data-acquisition-http-n1220

### tmux session
e005_refcoco_acquire

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-005
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-003b-refcoco-train-data-acquisition-http-n1220
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-003b-refcoco-train-data-acquisition-http-n1220/logs/acquire.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-003b-refcoco-train-data-acquisition-http-n1220/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-003b-refcoco-train-data-acquisition-http-n1220/metrics.json
- tmux_session: e005_refcoco_acquire
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T14:40:22
- updated: 2026-07-24T15:13:55

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
