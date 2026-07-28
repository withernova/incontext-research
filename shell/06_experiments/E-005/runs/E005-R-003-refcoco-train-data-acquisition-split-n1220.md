# E005-R-003-refcoco-train-data-acquisition-split-n1220 · RefCOCO train数据获取与固定分区

- canonical_run_id: `E005-R-003-refcoco-train-data-acquisition-split-n1220`
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 这是该 Run 的完整研究记录。工作台优先展示目的、实现、数据、结果和结论；执行细节仅用于复现与监控。

## 状态
aborted_network_protocol

## 本轮目的
恢复paper-native RefCOCO train数据路径，并预先固定pilot/discovery/evaluation独立图像分区。

## 必要性 / 证据链位置
LaSOT丢失且E-005论文原生协议使用RefCOCO train；正式head discovery必须避免synthetic identity leakage与选择/评估复用。

## 研究依据 / 被审计对象
官方LocalizationHeads README声明RefCOCO train随机1000样本；公开仓库未提供具体subset。HF jxu124/refcoco train含42404 rows。

## 实现方式（简版）
固定HF revision获取train parquet；按unique image去重，以seed 20260724抽取1220图并从COCO官方CDN下载；划分20 pilot/1000 discovery/200 evaluation。

## 实现方式（详细版）
每图固定首个ref row与首条caption；逐图验证尺寸和bbox；分区前完成抽样，禁止后续按结果重选。

## 数据身份与构造
RefCOCO UNC train metadata经jxu124/refcoco第三方HF parquet；图像来自images.cocodataset.org。不是论文作者公开的精确1000 subset。

## 数据规模
1220 unique images：pilot20、discovery1000、evaluation200。

## 模型、权重与关键配置
无模型；pyarrow17独立e005_site。

## 变量、干预与对照
unique image partition避免同图跨split泄漏；固定seed和HF revision。

## 指标与计数规则
下载/尺寸/bbox有效数、unique images、各partition数量、parquet SHA-256。

## 完整性门槛 / no-silent-zero
1220/1220有效；0 failure；20/1000/200；所有路径存在、尺寸匹配、bbox合法。

## 观测结果摘要
下载在首个HTTPS请求处阻塞；检查确认代理返回的TLS证书主机名不匹配。主动终止，无有效图像。

## 局限与混杂因素
第三方HF重打包；不能声称与论文作者未公开subset完全相同。

## 可支持的结论
网络协议问题，不是数据无效；不采用关闭TLS验证，改用官方CDN HTTP并另建R-003b。

## 不支持的结论 / Claim 边界
通过后仅表示可启动paper-native数据pilot；正式结果必须保留subset重构边界。

## 关键指标
0/1220；HTTPS curl证书hostname mismatch；HTTP官方COCO CDN HEAD=200。

## 审核入口
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-003-refcoco-train-data-acquisition-split-n1220; /home/featurize/work/mechanism/explog/E-005/data/refcoco_hf/data/train-00000-of-00001-94431d5f4bd5b93f.parquet

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
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-003-refcoco-train-data-acquisition-split-n1220/logs/acquire.log

### 产物目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-003-refcoco-train-data-acquisition-split-n1220/results

### 真实产物根目录
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-003-refcoco-train-data-acquisition-split-n1220

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
- run_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-003-refcoco-train-data-acquisition-split-n1220
- log_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-003-refcoco-train-data-acquisition-split-n1220/logs/acquire.log
- output_dir: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-003-refcoco-train-data-acquisition-split-n1220/results
- metrics_file: /home/featurize/work/mechanism/explog/E-005/runs/E005-R-003-refcoco-train-data-acquisition-split-n1220/metrics.json
- tmux_session: e005_refcoco_acquire
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-07-24T14:38:53
- updated: 2026-07-24T14:40:19

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
