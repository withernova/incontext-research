# E007-R-007-natural-query-head-reference-correspondence-chain-audit-n140 · 自然query-head的reference读取、跨图对应与query定位链式审计

- canonical_run_id: `E007-R-007-natural-query-head-reference-correspondence-chain-audit-n140`
- group_id: （未分组 / 待整理）
- run_type: observational_mechanism_audit
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-12T12:01:16
- approved_at: 2026-08-12T12:02:21
- approved_by: human
- execution_authorized_at: 2026-08-12T12:02:23
- execution_authorized_by: human
- execution_authorization_consumed_at: 2026-08-12T12:16:45
- legacy_registry_ids: （无）

> 已分组 Run 位于 `runs/<group-id>/<run-id>.md`；未分组 Run 位于 `runs/<run-id>.md`。
> Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
draft

## 本轮目的
不做任何activation注入或attention改写，直接检验自然bbox生成row上的冻结query heads是否形成reference object→query object对应：先测同head Q→R reference读取，再测该head键子空间中的reference-object-conditioned query correspondence，最后关联同row Q→Q空间质量与自然bbox IoU。

## 必要性 / 证据链位置
R-006c证明whole-residual注入会改变下游attention但不能改善自然定位，且该干预绕过了待检验的自然reference理解路径。已有E005只分别报告Q→R/Q→Q或G→R-Q→R discrepancy，尚未在同一row、同一head、同一forward内构造PerSAM式reference-object→query-token correspondence并检验其与Q→Q和bbox错误的连续链条。

## 研究依据 / 被审计对象
内部证据：E005-R-029c n140同分辨率自然replay中G→R近乎保留而Q→Q是最强error signature；E005-R-034d表明Q→R target mass与行为有中等相关；E006-R-014c削弱直接prediction-coordinate copy。外部已抓取证据：PerSAM以reference foreground local features和test image逐位置cosine similarity构造confidence map并引导cross-attention [[persam2023]] §3.2；OSTrack指出缺少template-conditioned target awareness会限制search判别力 [[ostrack2022]] §1；MixFormer通过多层search↔template mixed attention形成target-specific search features [[mixformer2022]] §3.1。

## 实现方式（简版）
复用E003-R-004b冻结positive n140与归档自然responses，在max_side640做140/140 exact teacher replay。固定main4=L18H15,L19H03,L22H00,L20H08及其对应GQA KV groups，不重选head。每个自然bbox token p-1 row在同一forward同时提取Q→R、Q→Q和各main4层进入attention前的pre-RoPE K表示；用reference GT token局部特征与所有query visual tokens的cosine similarity构造PerSAM式correspondence map。

## 实现方式（详细版）
对每个head h@layer l，取该Q-head对应KV group的pre-RoPE key vectors。Primary matched correspondence S_h(q)=mean_{r∈B_R} cosine(k_r,k_q)，B_R/Q GT均按merged-token fractional occupancy>0选择；不将cosine事后调温或阈值化。Controls：(1) same-image background：从reference bbox外按到bbox边界距离、token index稳定排序取与B_R等数量tokens；(2) same-category mismatched：启动前按element和sequence冻结另一实例donor，使用donor在其自身原始matched forward中的reference-GT pre-RoPE K，与recipient query K比较；无合格same-class donor则GATE_STOP，不改成out-class。另计算natural bbox-row Q→R/Q→Q raw attention的GT mass、enrichment、pointing和retained-mass token-fIoU curve。所有向量只用于即时指标，持久化map/标量和固定可视化，不写全量hidden tensor。

## 数据身份与构造
严格继承E005-R-029c使用的E003-R-004b positive target n140、140个sequence clusters、原图/GT/归档自然输出；行为分层沿用error35、correct76、partial22、rejected7。Primary是有自然Yes且可唯一匹配bbox token的accepted error+correct n111；partial n22作为连续IoU secondary；rejected/FN不伪造bbox row，只报告coverage并排除row-chain primary。same-class donor在任何模型forward前按element、sequence和index稳定冻结。

## 数据规模
最多140次matched exact replay；不为mismatched另做混合prompt forward，donor reference K从其自身matched replay缓存，避免改变recipient自然query状态。4 frozen heads×3 correspondence sources matched/background/mismatched；固定12个可视化样本=6 correct+6 error，按index预冻结且sequence unique。bootstrap B=10000，seed=20260812。

## 模型、权重与关键配置
Qwen3-VL-8B-Instruct+原IPLoc-ID 1shot LoRA，bf16 eager，max_side=640，官方原prompt/processor，归档自然response exact teacher replay；单RTX4090，22GiB+CPU offload；36层、32Q heads、8KV heads、head_dim128；seed=20260812。

## 变量、干预与对照
无模型干预。冻结main4及对应KV group；变量为行为组correct/error/partial、layer/head和correspondence source matched/background/same-class-mismatched。matched与controls使用同一recipient query K；禁止按结果换head、层、representation、donor、温度、阈值或样本。G→R仅作prompt grounding covariate，不与query-head链混称同一head。

## 指标与计数规则
H1 reference read：同row/head Q→R的reference-GT fractional mass、area-normalized enrichment、pointing、S50/fIoU-AUC。H2 correspondence：primary为连续score在query GT cells相对非GT cells的fractional-weighted rank AUC（chance=.5），另报pointing、top-mass token-fIoU AUC；specificity=matched-background与matched-mismatched paired差。H3 query localization：同row/head Q→Q的query-GT mass/enrichment/pointing/fIoU-AUC及自然bbox IoU。链式分析报告H1↔H2、H2↔H3、H1/H2↔IoU的Spearman与sequence bootstrap CI；correct-error差；并以固定5-fold sequence-hash CV比较geometry-only、H1、H1+H2预测IoU/错误的增量。只称association/predictive chain，不称formal mediation或causal mechanism。

## 完整性门槛 / no-silent-zero
模型/LoRA/manifest/source-output路径和hash持久化；140 sequence unique且与R029c manifest hash一致；自然response token序列连续唯一匹配，p-1 row语义逐样本审计；reference/query span、非方形grid、merge order、Q-head→KV-group映射正确；matched/background token集合不重叠且background count与object count相等；same-class donor element相同、sequence/index不同且在forward前冻结；所有cosine/attention/map/指标finite；accepted primary覆盖必须=111，否则GATE_STOP而非静默缩样；140 records或显式失败；12套每head correspondence+Q→R+Q→Q图与manifest一致；不读取R-006c intervention records作为选择依据。

## 竞争假设与预期特征
若假设成立，correct组应表现为更高H1和matched H2，matched correspondence优于background/same-class mismatch；H2应与同head Q→Q及bbox IoU正相关，并在geometry-only之上提供跨验证增量。若H1好但H2/H3差，支持“看到了reference区域但未形成跨图匹配”；若H2无matched specificity而Q→Q仍好，更像query-only/category cue；若H1/H2均不预测H3/IoU，则该main4 correspondence假设被削弱。

## 验收条件
完整性PASS：140/140记录或可审计显式失败、primary accepted n111完整、所有donor/span/row/KV/finite/figure gate通过，生成per-sample records、summary、metrics和12套图。假设的探索性支持门槛预注册为：(a) aggregated-main4 matched H2 rank-AUC correct-error差的95% sequence bootstrap CI>0；(b) matched-minus-background与matched-minus-mismatched至少一项CI>0且另一项方向>0；(c) H2与Q→Q或bbox IoU的Spearman CI>0；三者需同时满足。未满足则记mixed/null；无论结果不得重选head或追加表示。

## 依赖的 Run / 证据
依赖E005-R-029c的n140 manifest、归档自然输出和已验证640 replay入口；依赖已抓取文献笔记[[persam2023]]、[[ostrack2022]]、[[mixformer2022]]作设计依据。R-006c只作为停止residual family的前序负结果，不作为样本/指标选择数据。

## 观测结果摘要
（待补充）

## 局限与混杂因素
观察性teacher replay，Q→Q与自然bbox行为定义性耦合；pre-RoPE K cosine只是head-specific correspondence proxy，不等于语义理解；same-class donor来自另一forward且reference几何不同；LaSOT未完整标注query中所有同类实例；数据和main4已被多轮分析，故本run是机制审计而非fresh confirmation；multiple heads/layers完整报告，不从最优head形成确认性claim。

## 可支持的结论
（待补充）

## 不支持的结论 / Claim 边界
最多支持/削弱：冻结main4的自然bbox-stage reference读取与pre-RoPE K跨图对应质量是否和query-side空间定位及行为错误形成一致的观察性链条。不证明identity semantics、因果中介、唯一电路、SFT必要性或跨模型泛化。

## Artifacts
（待补充）

## 审核入口
设计文献=shell/02_search/hypothesis_reference_query_correspondence_scan_20260811.md及shell/03_evidence/papers/{persam2023,ostrack2022,mixformer2022}.md；数据前序=/home/featurize/work/mechanism/explog/E-005/runs/E005-R-029c-original140-positive-targets-binding-640/{config,logs,analysis,artifacts,manifests}；实现参考=/home/featurize/work/mechanism/scripts/e005/e005_r029c_original140_binding_640.py。

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
- run_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-007-natural-query-head-reference-correspondence-chain-audit-n140
- log_file: /home/featurize/work/mechanism/explog/E-007/E007-R-007-natural-query-head-reference-correspondence-chain-audit-n140/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-007-natural-query-head-reference-correspondence-chain-audit-n140/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-007/E007-R-007-natural-query-head-reference-correspondence-chain-audit-n140/metrics.json
- tmux_session: incontext-E-007-E007-R-007-natural-query-head-reference-correspondence-chain-audit-n140
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-12T12:01:15
- updated: 2026-08-12T12:16:45

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
