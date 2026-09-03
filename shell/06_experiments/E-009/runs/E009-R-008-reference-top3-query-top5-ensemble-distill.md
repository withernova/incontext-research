# E009-R-008-reference-top3-query-top5-ensemble-distill · Reference Top-3 教师到 Query Top-5 集合的跨图注意力蒸馏

- workflow: v2 / code_planning / 代码方案
- review_status: draft
- group_id: 未分组
- execution_dispatch:  / 

## 1. 研究设计
### 研究问题
将 R007 的 Reference Top-3 在 BQ 预测行对 reference visual span 的等权平均分布，蒸馏给 Query Top-5 的集合级 student attention，是否能在保持 Query localization 的同时提升 held-out 自然生成 BQ 的定位表现？
### 本轮目的
从同一 step1729 父 checkpoint 出发，比较普通 continued-SFT、正确 Reference Top-3 教师蒸馏、空间滚动的伪教师以及直接 GT-mask 监督，检验 Query Top-5 集合读取正确 reference 目标区域是否改善自然生成的 query bbox，而不是只产生额外正则化或普通框监督效果。
### 假设或比较预期
正确且冻结的 Reference Top-3 ensemble teacher 会使 Query Top-5 student ensemble 在生成 BQ 时增加对 reference 目标区域的有效读取，并使自然生成 query bbox IoU 相对普通 SFT 与空间滚动 teacher 改善；若改善只在 GT-mask 组出现，则不支持 Reference Head 特有知识蒸馏。
### 数据与主要变量
训练使用 train_only_1shot_focus.json，10534 条，SHA-256=c607700075de7eba1b0dc8237a32eb1760d3864a4e320f01a41bce8aec94ba78。valid96 仅用于实现完整性与开发诊断，因为它已参与 R007 head 选择，不作独立效果证据。最终主评估使用 val_lasot_posthoc_test600_1shot_focus.json，600 条，SHA-256=1cc952ffb23aa841b01737dd2989521ec56222651d97a3666a762e84ba7ce74a；补充评估使用 combined test 中 GOT10k-val 180 与 TAO-val 986，按数据集分别报告，sample-weighted combined 仅作次要汇总。

四臂固定父 checkpoint 及其文件哈希、训练 manifest/hash、seed=20260901、样本顺序、图像预处理、token-grid、global batch、optimizer、学习率、训练终点与评估解码。唯一处理差异为 auxiliary target：无 teacher、正确 Top-3 ensemble、同 grid 空间滚动 teacher、GT-mask teacher。正确与伪 teacher 使用完全相同 loss 形式和权重；测试集在四臂训练及 checkpoint 固定前不得访问。

## 2. 指标设计
主结论基于 held-out 自然生成 query bbox 的 per-dataset IoU 与 paired delta；attention KL/mass 和 teacher-forced IoU 仅解释机制与训练完整性。四臂共享同一父 checkpoint、数据与预算，GT-mask 和空间滚动 teacher 分别控制标签区域监督与普通注意力正则化。
## 3. 代码架构
复用现有 Qwen3VLLoRADDP、SFTLoRARunner、Qwen3VLSFTCollator、checkpointing 和 LocalizationEvaluator。新增通用 attention-distillation 模块：离线 teacher artifact builder、按 sample_id/token-grid 读取器、仅计算 selected query rows 对全部可见 keys 的精确 softmax slice、集合损失与指标；通过 runner 可选 auxiliary-loss 接口接入，不复制 SFT runner。新增一个 E009 config 和薄 launcher，四臂由显式 treatment 配置依次产生独立子目录。
- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `bash tools/run/run_e009_reference_query_ensemble_distill.sh`
- commit: ``
- workspace: 02
- tmux: incontext-E-009-E009-R-008-reference-top3-query-top5-ensemble-distill
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-R-008-reference-top3-query-top5-ensemble-distill/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-R-008-reference-top3-query-top5-ensemble-distill/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
单 seed、head 由 valid96 和单一父轨迹筛选；Reference Top-3 的选择使用 GT reward；LoRA q/k/v/o projection 为跨 heads 共享的低秩参数，因此损失虽读取指定 head，更新并非物理隔离于这些 heads。attention alignment 不等于信息流或因果作用；跨数据集测试也不是 IPLoc/FOCUS 官方协议。

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "Solid Run E009-R-007 只在固定 valid96 和同一训练轨迹最后五个 checkpoint 上给出了描述性稳定的 head 集合，尚未检验这些 heads 能否通过训练改变跨图读取，也未证明该变化对 Query localization 有因果或泛化作用。",
  "evidence_basis": "唯一结果依据为 Solid Run E009-R-007-head-stability-last5：Query Top-5=[L21H10,L17H04,L17H07,L24H16,L18H15]，Reference Top-3=[L20H15,L20H20,L14H23]。该结果仅覆盖固定 valid96、单父训练轨迹后段 checkpoint；不把 attempt-001、其他 Run、因果性、跨 seed 或测试集泛化作为已知证据。",
  "implementation_summary": "先用固定 step1729 父模型为每个训练样本离线生成 teacher：三个 Reference Head 各自在 BQ 的 p-1 行上提取到 reference visual span 的注意力，逐 head 做 span 内归一化后等权平均。训练时五个 Query Head 用相同行和 span 构成等权 student ensemble，并优化集合级 KL、reference-span mass 匹配和 reference-object mass 匹配；teacher 全程 stop-gradient。四个训练臂从相同父 checkpoint 重启并使用相同样本顺序与预算。",
  "implementation_details": "固定 H_R={L20H15,L20H20,L14H23}，H_Q={L21H10,L17H04,L17H07,L24H16,L18H15}。对每个 head 先平均全部 query bbox token 的 p-1 rows，再在 reference token span 内归一化；T_R=(1/3)sum_h p_h，S_Q=(1/5)sum_q p_q，L_shape=KL(T_R||S_Q)。另以三个教师 raw maps 的均值定义 reference-span 与 reference-GT-object mass，student 用五个 raw maps 的均值匹配，L_ref=L_shape+SmoothL1(m_span_Q,m_span_R)+SmoothL1(m_obj_Q,m_obj_R)，主处理组 L_total=L_SFT+0.1*L_ref。四臂为 A 普通 continued-SFT；B 正确固定 teacher；C 对 teacher map 在原 token-grid 做 seeded nonzero cyclic roll，保持 mass、grid 与熵但破坏目标位置；D 用归一化 reference bbox occupancy 替换 teacher shape、其余训练预算一致。第一版不加 Q→Q preservation loss，只记录其变化。teacher 必须离线预计算并按 sample_id、bbox rows、reference span、token-grid 一一匹配；不得在线共同漂移。",
  "model_config": "Qwen3-VL-8B-Instruct + NF4 QLoRA + 4-GPU DDP；父 adapter 固定为 E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/checkpoints/samples_00110607_step_001729。语言侧 LoRA target modules 保持现状，不训练 visual encoder。新增可微的选定 head/row attention slice 提取，主 forward 保持 SDPA；禁止为主训练保存全部 layer×head×sequence² attention。",
  "metric_definition": "主指标为自然逐 token 生成 BQ 的 per-dataset mean IoU、bbox parse rate、IoU@0.25/0.5/0.75，以及相对普通 SFT 的同样本 paired IoU delta；LaSOT、GOT10k、TAO 分开报告，按 sequence cluster bootstrap 95% CI，combined sample-weighted 值仅为次要。机制诊断为 Query Top-5 ensemble 的 Q→R teacher KL、reference-span mass、reference-object mass、Q→Q query-object mass，以及这些量相对父 checkpoint 的变化。teacher-forced bbox IoU 不作为主结果。",
  "integrity_gates": "运行前验证父 adapter/config/trainer_state、三个数据 manifest 及其 SHA-256；teacher 记录必须 10534/10534、sample_id 唯一、bbox rows 与 reference span 合法、token-grid 精确一致、数值有限。四臂必须从同一父 hash 开始且配置除 treatment 字段外完全一致。训练中 total/SFT/shape/mass losses 与 gradients 全部有限；selected attention slices 必须在同一 batch 上通过全 eager attention 的数值对照。任何臂失败不得用其他臂替代。所有臂 checkpoint 固定前不得读取 test600 或 combined test 输出。",
  "expected_outcome": "若正确 teacher 使自然生成 query IoU 优于普通 SFT 和空间滚动 teacher，同时 Q→R alignment 改善且 Q→Q 未明显崩塌，则结果支持继续研究 reference-reading 辅助训练。若 GT-mask 与正确 teacher 相当或更好，只能支持区域监督而不能支持 Reference Head 特有知识；若滚动 teacher 同样改善，则收益更可能来自正则化。",
  "acceptance_criteria": "工程完整性要求 teacher 10534/10534、四臂均到达相同训练终点、自然生成评估无缺失且审计字段齐全。机制假设只有在正确 teacher 相对普通 SFT 与滚动 teacher 的 paired IoU delta 方向为正、Q→R KL/mass 按预注册方向改变且 GT-mask 对照不能完全解释收益时才获得支持；否则记为不支持或证据不足，不因单个数据集或 teacher-forced 指标事后改写结论。",
  "claim_boundary": "只允许判断从固定 step1729 出发时，R007 指定的 Reference Top-3 平均 attention teacher 对 Query Top-5 student ensemble 的辅助训练是否改变自然 query localization，并通过同 Run 对照区分正确空间 teacher、伪 teacher 与 GT-mask supervision。不得声称复制了 head 参数、形成了通用跨图匹配能力、证明单个 head 因果、跨 seed 稳定或复现官方 benchmark。",
  "audit_paths": "planned: configs/sft/e009_qwen3vl8b_reference_query_ensemble_distill.py; iploc_szy/attention_distillation/; tools/precompute_e009_reference_teacher.py; tools/run/run_e009_reference_query_ensemble_distill.sh; tests/test_attention_distillation.py; tests/test_e009_distillation_suite.py"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
