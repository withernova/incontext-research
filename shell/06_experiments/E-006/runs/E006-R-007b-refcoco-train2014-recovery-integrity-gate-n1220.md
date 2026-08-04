# E006-R-007b-refcoco-train2014-recovery-integrity-gate-n1220 · refcoco-train2014-recovery-integrity-gate-n1220

- canonical_run_id: `E006-R-007b-refcoco-train2014-recovery-integrity-gate-n1220`
- run_type: data_gate
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-03T22:01:41
- approved_at: 2026-08-04T12:53:59
- execution_authorized_at: 2026-08-04T12:54:05
- execution_authorization_consumed_at: 2026-08-04T14:39:30
- legacy_registry_ids: （无）

> `canonical_run_id` 同时是 registry 主键、canonical note 文件名与默认远端产物目录名，不要再把它塞入 variant 或 notes。
> 新 Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
completed

## 本轮目的
验证用户新提供的COCO train2014像素与重新获取的jxu124/refcoco metadata，构建可供已批准R-009直接消费的20/1000/200冻结manifest。

## 必要性 / 证据链位置
旧R-007已在当时资产缺失时GATE_STOP，不能事后覆盖为通过。当前train2014.zip与HF metadata是在其后获得的新资产，必须独立canonical recovery gate验证hash、解码、尺寸、bbox、expression以及image_id跨split隔离。

## 研究依据 / 被审计对象
现有train2014.zip size=13,510,573,713 bytes、SHA256=ede4087e640bddba550e090eae701092534b554b42b05ac33f0300b984b31775、unzip test通过、解压JPG=82,783；jxu124/refcoco metadata split rows为42404/3811/1975/1810，image_path明确指向coco/train2014。

## 实现方式（简版）
只读扫描已解压train2014与HF Arrow metadata；从RefCOCO train按sha256(seed:image_id:ref_id:ann_id)确定性选择1220 expression samples，优先每image一条，按COCO image_id分组得到pilot20/discovery1000/confirmation200；逐条PIL decode、实际尺寸、bbox和expression验证。

## 实现方式（详细版）
通过datasets本地cache读取train split，不联网；真实图路径由image_id映射为/home/featurize/data/train2014/COCO_train2014_<12digit>.jpg，不使用HF带expression suffix的file_name。先按image_id分组，对每个image确定性选择一条合法expression；哈希排序后前20 pilot、后1000 discovery、后200 confirmation，三者image_id严格不交叉。记录metadata cache文件相对路径/size/SHA256、ZIP hash、图片总数、每条sample IDs/text/bbox/width/height/path/file size。

## 数据身份与构造
jxu124/refcoco当前本地cache的train split，expression sample为单位；像素是官方COCO train2014解压目录。1220不是论文公开的精确sample IDs，也不是论文明示的unique-image要求；image_id隔离是本地防泄漏设计。

## 数据规模
RefCOCO train全42404行做metadata合法性扫描；冻结1220 expression samples=20 pilot+1000 discovery+200 confirmation，对应1220 distinct COCO image_id；逐条解码1220张图。

## 模型、权重与关键配置
无模型forward；Python datasets/PIL/json/hashlib；seed=20260724；只读输入，输出仅写新run目录。

## 变量、干预与对照
split grouping key=COCO image_id；路径由image_id canonical mapping；bbox按metadata xyxy解释并验证0<=x1<x2<=W、0<=y1<y2<=H；expression取首个非空sentence.raw/sent并保留sent_id。

## 指标与计数规则
train rows/unique image IDs；COCO JPG总数；selected/valid/missing/decode-failed/size-mismatch/bbox-invalid/expression-invalid；pilot/discovery/confirmation样本数和image_id交集；ZIP与metadata文件SHA256。

## 完整性门槛 / no-silent-zero
1) train2014 JPG严格82783；2) ZIP SHA256与已核验值一致；3) 1220/1220图片存在且PIL verify/load成功；4) raw_image_info宽高与实际一致；5) bbox与expression全部合法；6) split counts=20/1000/200；7)任意两split image_id overlap=0；8) 0 silent missing；9) 不联网；10) 不覆盖旧R-007。

## 竞争假设与预期特征
若全部通过则解除R-009的数据依赖阻塞；任何缺图、尺寸/bbox异常或split泄漏均GATE_STOP并列出具体样本。

## 验收条件
GATE_PASS；manifest.jsonl 1220行；split_summary与hash manifest完整；PIL decode 1220/1220；overlap=0；明确本地split非论文精确subset。

## 依赖的 Run / 证据
用户提供/home/featurize/data/train2014.zip及其解压目录；/home/featurize/data/refcoco_hf_download本地metadata cache；旧R-007 gate-stop记录保持不变。

## 观测结果摘要
GATE_PASS；COCO train2014 JPG=82783；RefCOCO train metadata=42404；冻结1220个distinct image_id（pilot20/discovery1000/confirmation200）；1220/1220 PIL decode与尺寸验证通过；split overlap=0。

## 局限与混杂因素
HF dataset revision当前未显式pin到commit；作者LocalizationHeads精确1000 IDs/采样单位未公开；只验证数据资产，不是方法结果。

## 可支持的结论
仅证明当前COCO/RefCOCO资产完整以及本地image-disjoint manifest可供R-009使用；不是LocalizationHeads精确公开subset复现。

## 不支持的结论 / Claim 边界
只支持当前RefCOCO/COCO资产完整和本地anti-leakage manifest可运行；不支持exact-paper replication或任何模型结论。

## 关键指标
{"gate":"GATE_PASS","coco_jpg_count":82783,"metadata_rows":42404,"selected":1220,"decode_valid":1220,"decode_failed":0,"split_counts":{"pilot":20,"discovery":1000,"confirmation":200},"split_image_overlap":0}

## Artifacts
（待补充）

## 审核入口
shell/06_experiments/E-006/runs/E006-R-007-refcoco-coco-frozen-manifest-integrity-gate-n1220.md; /home/featurize/data/refcoco_hf_download/output/dataset_summary.json; /home/featurize/data/coco2014/logs/final.log

## 过程记录与补充细节
（待补充）

## Run 审核
### 用户补充要求
（待补充）
### 用户疑问
（待补充）
### Agent 完善说明
（待补充）
### Agent 对疑问的回应
（待补充）
### 本次执行授权备注
（待补充）

<details><summary>执行与复现信息</summary>

### Workspace
W-01

### Git commit / branch
（待补充）

### 运行命令
（待补充）

### 配置/超参数
（待补充）

### Seed
20260724

### 日志路径
（待补充）

### 产物目录
（待补充）

### 真实产物根目录
（待补充）

### tmux session
（待补充）

</details>

## 解析后的执行环境
- server: M-01 · feturize
- ssh_host: featurize
- workspace: W-01
- remote_repo: /home/featurize/work/mechanism/Rex-Omni
- remote_data_root: /home/featurize/data
- project_dir: /home/featurize/work/mechanism/E-006
- run_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-007b-refcoco-train2014-recovery-integrity-gate-n1220
- log_file: /home/featurize/work/mechanism/explog/E-006/E006-R-007b-refcoco-train2014-recovery-integrity-gate-n1220/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-006/E006-R-007b-refcoco-train2014-recovery-integrity-gate-n1220/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-006/E006-R-007b-refcoco-train2014-recovery-integrity-gate-n1220/metrics.json
- tmux_session: incontext-E-006-E006-R-007b-refcoco-train2014-recovery-integrity-gate-n1220
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-03T22:01:41
- updated: 2026-08-04T15:14:44

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
