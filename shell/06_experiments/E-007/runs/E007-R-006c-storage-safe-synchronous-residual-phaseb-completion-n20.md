# E007-R-006c-storage-safe-synchronous-residual-phaseb-completion-n20 · R-006b存储安全恢复：完整重跑n20自然行为阶段

- canonical_run_id: `E007-R-006c-storage-safe-synchronous-residual-phaseb-completion-n20`
- group_id: （未分组 / 待整理）
- run_type: recovery_causal_behavior_pilot
- review_status: approved
- review_round: 1
- submitted_for_review_at: 2026-08-11T16:08:46
- approved_at: 2026-08-11T16:09:06
- approved_by: human
- execution_authorized_at: 2026-08-11T16:09:08
- execution_authorized_by: 
- execution_authorization_consumed_at: 2026-08-11T16:17:14
- legacy_registry_ids: （无）

> 已分组 Run 位于 `runs/<group-id>/<run-id>.md`；未分组 Run 位于 `runs/<run-id>.md`。
> Run 必须经过 Agent 初稿 → 用户审核/补充 → Agent 完善并重新提交 → 用户批准 → 单独执行授权。批准不等于执行。

## 状态
completed_passed_integrity_scientific_upgrade_failed

## 本轮目的
在不改变R-006b科学变量的前提下，完整重跑其尚未完成的Phase B：比较matched、mismatched与background reference residual在三个固定强度下对自然bbox定位的影响。旧R-006b保留为通过工程门槛但行为阶段不完整的前序run，本run提供唯一完整行为结果。

## 必要性 / 证据链位置
R-006b的Phase0/PhaseA已经证明同步prefix实现可靠且reference residual会改变下游Q→R和Q→Q，但PhaseB仅生成18/220条后会话消失；3.62GB累积checkpoint暴露出逐条重写巨大完整attention数组的存储风险。缺少完整n20×11结果，无法判断matched是否优于mismatched/background，也无法收束无训练干预路线。

## 研究依据 / 被审计对象
远端R-006b phase0.json gate_pass=true；phaseA.json gate_pass=true且4/4 identity_exact、residual_nonzero、both_changed、mismatched_prefix_exact；旧checkpoint含20条PhaseA和18条PhaseB，日志止于第2个样本mismatched_0.25；无summary.json/metrics.json。R-006b脚本SHA256=bf2ca1bc2e888af36192e1b49e36c7541ef5dde4c3eb31f88b29035da1ca8754。

## 实现方式（简版）
继承R-006b冻结的20个样本、donor映射、L16H23→layer17 input链路、三个source类型和lambda集合；Phase0/PhaseA不重新产生科学记录，只在启动时核验其hash和gate。PhaseB的220个case-condition从头独立重跑，不混用旧18条残缺结果。将每条行为结果写成原子化小型JSON，并仅保存预注册标量attention审计，最后合并统计，避免反复覆盖数GB checkpoint。

## 实现方式（详细版）
主分支继续使用upstream model.generate；auxiliary分支继续使用与target完全相同的已生成prefix，独立KV cache且永不采样，只提供L16H23 reference-span c_t与g_t。注入仍为layer17当前row的x+lambda*g*RMS(x)/(RMS(c)+1e-6)c。baseline/identity、matched/mismatched/background×{0.1,0.25,0.5}均保持不变。每个case-condition写入records/<index>/<condition>.json.tmp后fsync并原子rename；记录tokens、response、bbox、IoU、parse、Yes、closed、prefix/hash、注入次数和每step标量摘要。完整qtor/qtoq向量仅沿用已通过的R-006b PhaseA，不在PhaseB重复持久化。支持按缺失文件续跑，但启动时若已存在记录必须先校验config hash、sample hash、condition和schema；不合格则GATE_STOP，不覆盖。

## 数据身份与构造
严格使用R-006b frozen_design.json中的20个phaseB indices=[15,22,23,25,27,33,35,39,42,43,0,2,4,5,7,8,9,10,11,12]及固定cyclic donor映射；10个历史localization-error+10个historical-correct positives，sequence unique。GT仅在生成完成后计算IoU；不换样本、不读取旧18条结果选择条件。

## 数据规模
PhaseB=20样本×11条件=220次独立greedy generation：baseline、identity，以及matched/mismatched/background×lambda{0.1,0.25,0.5}。Phase0/PhaseA仅hash/gate读取核验，不计新行为generation。若因外部中断恢复，只补齐已通过原子记录校验的缺失case-condition，最终仍要求220个唯一记录。

## 模型、权重与关键配置
Qwen3-VL-8B-Instruct+同一IPLoc-ID 1shot LoRA，bf16 eager，max_side=640，官方原prompt与processor/EOS，greedy/do_sample=False，max_new_tokens=128，GPU上限22GiB+CPU offload；seed=20260805；单GPU串行且不与其他run并发。模型与LoRA路径启动时hash/verified marker核验。

## 变量、干预与对照
固定source=L16H23、injection=layer17 input、bbox生成在线窗口和RMS公式。变量仅source type matched/mismatched/background与lambda 0.1/0.25/0.5。baseline与lambda0 identity是工程/行为对照；禁止改head、layer、样本、donor、window、prompt、解码、lambda或依据中间结果提前停止。

## 指标与计数规则
Primary：每个lambda下matched相对baseline的sequence-paired mean/median IoU delta，以及matched相对同lambda mismatched/background的paired mean/median差。Secondary：各条件mIoU、IoU>=.3/.5/.7、parse、Yes、rescue（baseline<.1且condition>=.3）与damage（baseline>=.7且condition<.3）、每step gate/delta-RMS和冻结下游heads的Q→R/Q→Q总质量标量变化。按sequence做10000次bootstrap、seed=20260805；n20为探索性，完整Identification/Joint F1记NA。

## 完整性门槛 / no-silent-zero
启动前要求R-006b frozen_design/phase0/phaseA的SHA256分别为7a2e98ad82c990f73c1856b4d0579211dc6fdcec1beb20a8172772e69203b849、f529f08c0ace67d5b0c74dec99fc62861b210441241a15a640efe5d847df0086、8f9dd8344375b8532691bf3e84f120c272f5be74dfb2d3d094df7045e6f05f29且gate均true。220/220唯一原子记录；baseline/identity 20/20 tokens exact；所有aux_prefix_exact、closed、finite；donor sequence不同；inside/background不重叠；只改layer17当前row；每步prefix hash持久化；无future token；失败记录显式保留。预计PhaseB持久产物上限2GB，启动前可用空间>=10GB；禁止覆盖旧R-006b。

## 竞争假设与预期特征
若matched在某个预注册lambda下相对baseline为正、rescue>damage，且同时优于同lambda mismatched和background，则提示reference-specific residual具有有限自然行为贡献；若只改变下游路由但行为null，说明该冻结路径的影响不足以改善定位；若controls等效或更好，则倾向非特异性/OOD注入解释。

## 验收条件
完整性PASS要求220/220唯一有效记录、identity exact、全部prefix/window/hash/finite gate通过并生成summary.json、metrics.json和per-record manifest。科学upgrade沿用R-006b预注册规则：至少一个固定lambda的matched mean IoU delta>0、rescue>damage，且matched mIoU同时高于同lambda mismatched与background；否则记mixed/null并停止该无训练residual family。无论方向如何均报告全部三个lambda和全部controls，不挑最佳样本。

## 依赖的 Run / 证据
依赖已完成但不完整的E007-R-006b的不可变Phase0/PhaseA工程证据，以及R-001冻结n20和原模型资产。该恢复run必须单独人工审核和单独执行授权；不得沿用R-006b已消费授权。

## 观测结果摘要
R-006c完整完成220/220，exit0、identity exact、integrity PASS；scientific upgrade失败。baseline mIoU=.46909；matched λ=.1/.25/.5相对baseline mean ΔIoU分别-.00496、-.00463、-.03727，均0 rescue，λ=.5有1 damage。matched未在任一λ同时优于baseline、mismatched和background，故按预注册停止无训练residual-injection family。

## 局限与混杂因素
positive-only n20、历史极端分层、分布外residual注入，不能估计完整Identification/Joint F1；mismatched同时改变reference内容和bbox/container；即使正向也不证明identity semantics、训练可行性或跨数据泛化。PhaseB压缩attention为预注册标量，完整向量级工程证据仅来自R-006b PhaseA。

## 可支持的结论
可支持：R-006b已证明该注入会改变下游Q→R/Q→Q，R-006c进一步表明这种变化未转化为该冻结n20上的source-specific自然定位改善。不可支持：reference信息无用、query heads没有reference理解、SFT无效；本run是positive-only、n20、分布外residual干预。

## 不支持的结论 / Claim 边界
最多支持或反驳：在相同target生成prefix下，L16H23 reference-span residual经layer17注入是否对该冻结n20的自然bbox定位产生source-specific探索性因果影响。不证明身份理解、唯一电路、SFT收益或泛化Joint F1改善。

## Artifacts
records=220; summary=analysis/summary.json; manifest=manifests/records_manifest.json; log=logs/train.log; exit=logs/exit.code

## 审核入口
前序=/home/featurize/work/mechanism/explog/E-007/E007-R-006b-synchronous-counterfactual-prefix-residual-conditioning-gate-n4-20/{manifests/frozen_design.json,analysis/phase0.json,analysis/phaseA.json,artifacts/records_checkpoint.json,logs/train.log}; local=shell/06_experiments/_legacy/codespace/e007/runner_006b.py; 新run默认目录由canonical ID解析。

## 过程记录与补充细节
（待补充）

## 指标观测
/home/featurize/work/mechanism/explog/E-007/E007-R-006c-storage-safe-synchronous-residual-phaseb-completion-n20/metrics.json

> 以上为兼容历史 metrics；后续请改用 metric_observations。

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
20260805

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
- run_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-006c-storage-safe-synchronous-residual-phaseb-completion-n20
- log_file: /home/featurize/work/mechanism/explog/E-007/E007-R-006c-storage-safe-synchronous-residual-phaseb-completion-n20/logs/train.log
- output_dir: /home/featurize/work/mechanism/explog/E-007/E007-R-006c-storage-safe-synchronous-residual-phaseb-completion-n20/outputs
- metrics_file: /home/featurize/work/mechanism/explog/E-007/E007-R-006c-storage-safe-synchronous-residual-phaseb-completion-n20/metrics.json
- tmux_session: incontext-E-007-E007-R-006c-storage-safe-synchronous-residual-phaseb-completion-n20
- launcher: tmux
- environment_activation: 
- complete: true

> 这是服务器与监控的唯一配置源。Agent 不得自行读取历史 watchdog 配置或猜测其他服务器。配置不完整时必须停止。

- created_by: terminal_pi
- created: 2026-08-11T16:08:46
- updated: 2026-08-12T11:59:55

## 自由笔记（Obsidian）

这里可补充不适合结构化字段的观察；工作台更新 Run 时不会覆盖本节。
