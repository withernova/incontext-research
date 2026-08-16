# E007-R-008-reference-head-guided-two-pass-reference-masking-gate-n20 · reference head引导的两遍reference遮罩自然生成门禁

- canonical_run_id: `E007-R-008-reference-head-guided-two-pass-reference-masking-gate-n20`
- group_id: （未分组 / 待整理）
- run_type: training_free_input_counterfactual_gate
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-12T15:42:59
- approved_at: 2026-08-12T15:52:57
- approved_by: human
- execution_authorized_at: 2026-08-12T15:52:59
- execution_authorized_by: human
- execution_authorization_consumed_at: 2026-08-12T16:05:37
- execution_dispatch_id: 
- execution_dispatch_latest_status: 
- legacy_registry_ids: （无）

> 已分组 Run 位于 `runs/<group-id>/<run-id>.md`；未分组 Run 位于 `runs/<run-id>.md`。
> Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
draft

## 本轮目的
先用原图前向计算reference-grounding heads在reference图上的自然空间分布，再按该分布遮住reference图的其余区域，让模型第二遍从头处理遮罩后的reference与未改动query并自然生成bbox。比较真实head遮罩、prompt bbox遮罩、旋转/背景遮罩和删除遮罩，检验reference heads选出的内容是否比等预算空间对照更能保留或改善query定位。

## 必要性 / 证据链位置
R-007发现matched correspondence优于same-class mismatch/background，且Q→R reference-GT mass与IoU相关，但H2没有稳定传到同head Q→Q/IoU；R-006c的whole-residual注入又属于过宽的分布外干预。当前缺口是：reference heads自然选出的图像内容，经一个可观察的training-free两遍接口重新输入后，是否对query-side定位具有相对特异的信息价值。

## 研究依据 / 被审计对象
内部证据：reference-grounding heads固定为L15H13,L16H23,L18H15；query-localization main4固定为L18H15,L19H03,L22H00,L20H08。R-007中matched-background rank-AUC差+.2074 CI[.1759,.2383]、matched-mismatched差+.0569 CI[.0172,.0960]，H1 Q→R mass与IoU rho=.3662 CI[.1863,.5251]，但H2↔H3/IoU CI跨0。外部相邻依据仅限PerSAM用reference foreground local features生成query confidence map并引导后续attention [[persam2023]] §3.2；本run不是PerSAM复现。

## 实现方式（简版）
复用R-006b/c在任何本run结果前已固定的10 error+10 correct、sequence-unique positives。第一遍在原始prompt的reference bbox各token p-1 rows提取3个reference-grounding heads到reference visual span的raw attention，跨row/head求和后在reference span内归一化，取承载累计50%质量的最小稳定token集合S50。把merged-token cells映射回已resize到max_side640的reference RGB块；第二遍保持query、prompt、reference bbox坐标、解码协议不变，仅按预注册条件对reference像素做neutral-fill遮罩并从头自然生成。

## 实现方式（详细版）
第一遍只构造mask，不读取query GT或第二遍结果。S50按attention降序、token index升序打破并列；记录grid、每head map、selected count/mass和pixel rectangles。neutral fill为该resize后reference RGB全图逐通道均值，禁止LaMa或调色。七个第二遍条件：(1) identity_original原图重跑；(2) refhead_keep仅保留S50；(3) bbox_keep保留与S50等数量、按reference prompt bbox fractional occupancy降序再按到bbox中心距离/index稳定选择的cells；(4) r180_keep保留S50在同一非方形grid上的180°位置；(5) background_keep保留与S50等数量、bbox外按到bbox边界距离/index选择的cells；(6) refhead_drop只neutral-fill S50、其余原样；(7) background_drop删除条件5的等数量cells。所有条件均重建processor输入、KV cache并逐token自然生成；不得把第一次KV传入第二次。第二遍另teacher-replay其自然bbox rows，报告main4 Q→R/Q→Q GT alignment，但不得用这些attention选择条件。

## 数据身份与构造
严格继承E007-R-006b/c frozen_design.json的20个phaseB indices=[15,22,23,25,27,33,35,39,42,43,0,2,4,5,7,8,9,10,11,12]，即10个历史accepted localization error和10个historical correct positive，sequence unique。样本、分组和顺序在R-007结果前已经固定；GT只用于运行后IoU和attention alignment，不参与refhead mask。

## 数据规模
20个第一遍mask forward；第二遍20×7=140次独立greedy natural generation；对可解析自然bbox结果做最多140次teacher replay attention审计。固定8套可视化=4 error+4 correct，按frozen index顺序各取前4，不按结果选择。sequence bootstrap B=10000，seed=20260812。该n20只决定是否值得创建独立n140 follow-up，不直接形成论文确认性结论。

## 模型、权重与关键配置
Qwen3-VL-8B-Instruct+原IPLoc-ID 1shot LoRA，bf16 eager，max_side=640，原prompt/processor/EOS，greedy do_sample=False、max_new_tokens=128；单RTX4090、22GiB+CPU offload。source heads=L15H13,L16H23,L18H15；audit target heads=L18H15,L19H03,L22H00,L20H08；seed=20260812。

## 变量、干预与对照
干预层级是输入像素，不是hidden activation。唯一变量是reference image mask；query image、prompt文字、reference bbox文本、模型、解码均固定。identity检验两遍框架；bbox_keep控制显式prompt bbox已经提供的位置；r180/background keep控制selected count与遮罩强度；refhead_drop相对background_drop检验删除reference-head区域是否更有害。所有keep条件selected-token-count逐样本严格相等，drop条件亦严格相等。

## 指标与计数规则
Primary：每个condition相对identity的sequence-paired mean/median IoU delta；refhead_keep相对bbox_keep/r180_keep/background_keep的paired IoU差；refhead_drop相对background_drop的pairedIoU差（预期更负）。Secondary：mIoU、IoU≥.3/.5/.7、parse/Yes、error rescue(identity<.1且condition≥.3)、correct retention(identity≥.7且condition≥.7)、damage(identity≥.7且condition<.3)，以及第二遍main4聚合Q→R reference-GT mass/fIoU-AUC、Q→Q query-GT mass/fIoU-AUC。所有CI按sequence bootstrap 10000次；n20不报告完整Identification/Joint F1。

## 完整性门槛 / no-silent-zero
启动前hash并持久化R-006b/c frozen design、n140 manifest、source outputs、模型与LoRA；20 indices和10/10分组必须exact。第一遍reference bbox rows连续唯一匹配；三head maps finite且reference-span conditional mass=1；S50 selected_mass≥.5且去掉最后token后<.5；token-grid/pixel rectangle非方形映射覆盖无重叠/越界。每样本七条件除reference RGB外的input_ids、query pixels、image_grid_thw、prompt和解码配置一致；identity natural tokens须与原归档20/20 exact，否则GATE_STOP。keep四条件selected count严格一致，drop两条件严格一致；每条件独立KV且无第一次cache；140原子generation records；attention replay失败显式记录，不能默认为零；8套图、summary、metrics、manifest、exit0齐全。

## 竞争假设与预期特征
若reference heads选出的内容有超出显式bbox位置与一般遮罩的定位价值，refhead_keep应比r180/background keep更少损伤或更常rescue，并最好也优于bbox_keep；同时删除S50应比删除等量background更有害。若refhead_keep只等于bbox_keep，说明主要是prompt bbox位置而非head额外筛选；若所有keep同样下降，是大面积像素遮罩/OOD效应；若background/r180更好，则削弱reference-head内容重要性；若只改变Q→R/Q→Q而行为不变，则仍不能称行为利用。

## 验收条件
完整性PASS后，升级到独立n140的探索性门槛必须同时满足：(a) refhead_keep−background_keep paired mean IoU>0且95% sequence bootstrap CI下界>0；(b) refhead_keep−r180_keep方向>0；(c) refhead_drop−background_drop方向<0；(d) refhead_keep的rescue>damage。bbox_keep仅作解释分流：若refhead_keep−bbox_keep CI>0则支持head筛选有额外价值；若CI跨0/≤0则最多支持bbox区域内容而非reference-head特异性。任一(a–d)失败则停止该pixel-mask family或改记mixed/null，禁止换S50阈值/fill/head/sample。

## 依赖的 Run / 证据
依赖R-006b/c frozen n20、E005 reference/query head registry、原n140 manifest/source outputs和模型资产。远程服务器在本run规划时connection refused，执行前必须重新核验host/GPU/路径；连接失败不得消费授权或伪造smoke。正式执行需要本run人类审核通过、单独执行授权以及终端明确执行指令。

## 观测结果摘要
（待补充）

## 局限与混杂因素
hard neutral-fill pixel mask明显OOD且会改变低层视觉统计；reference bbox已经显式给出，故bbox_keep是不可缺少的强对照；source attention可能主要反映坐标绑定而非object identity；两遍系统证明的是外部training-free使用价值，不证明原模型自然因果路径；n20极端分层且positive-only；teacher replay attention与自然生成行为不可混作同一独立证据。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
最多支持/削弱：冻结reference-grounding heads在原图第一遍选出的reference像素区域，经training-free第二遍重新输入后，是否比等数量bbox/旋转/background区域更能保留或改善该n20的自然query定位。不证明identity理解、QR match唯一性、自然模型原本使用该mask、跨模型泛化或完整Joint F1改善。

## Artifacts
（待补充）

## 审核入口
前序设计=shell/06_experiments/E-005/head_role_registry.md与E007-R-007 run note；冻结样本=/home/featurize/work/mechanism/explog/E-007/E007-R-006b-synchronous-counterfactual-prefix-residual-conditioning-gate-n4-20/manifests/frozen_design.json；预期产物=/home/featurize/work/mechanism/explog/E-007/E007-R-008-reference-head-guided-two-pass-reference-masking-gate-n20。

## 过程记录与补充细节
（待补充）

## 指标观测
（尚无结构化观测）

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
### 自动审核快照
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
20260812

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
- project_dir: /home/featurize/work/mechanism/E-007
- run_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-008-reference-head-guided-two-pass-reference-masking-gate-n20
- log_file: /home/featurize/work/mechanism/explog/E-007/E007-R-008-reference-head-guided-two-pass-reference-masking-gate-n20/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-008-reference-head-guided-two-pass-reference-masking-gate-n20/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-007/E007-R-008-reference-head-guided-two-pass-reference-masking-gate-n20/metrics.json
- tmux_session: incontext-E-007-E007-R-008-reference-head-guided-two-pass-reference-masking-gate-n20
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 Steward/Watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-12T15:42:59
- updated: 2026-08-12T16:05:37

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
