# Codex上下文交接：In-Context Object Localization的VQA选择器探索

> 最新更新（2026-10-21）：用户要求直接执行已说明方案。换序诊断已完成；LR衰减续训已实际更新，局部图对照与两个配对训练arm已分别受管安排，按GPU释放事件顺序执行；真实配对数据359训练对/62验证对已准备完成。接手先读 [执行对照记录](执行对照-20261021.md) 和 state.md，以下旧状态保留为历史。

> 最新执行更新（2026-10-20）：用户已明确“可以部署运行”。`7caae090351c9c71ce65fd8c98a0bbbbb1825bc6` 已发布部署；有限逻辑和三例真实图片编码验收通过，单次step4041换序P1诊断已受管启动，尚无最终指标。首先读取 [部署与首轮验证](部署与首轮验证-20261020.md) 和 state.md 最新记录；以下离线状态与权限描述均为历史快照。

> 保存日期：2026-10-20。本文是会话交接快照，不是实时运行状态。
> 最重要的状态：旧续训和评测已经完成；新的四方向探索目前只读了代码，尚未修改源码，也没有启动新实验。
> 本文及后续交接记录不授予新的实验执行权限。

> 后续更新（2026-10-20）：用户已明确授权离线实现，四项代码已完成并本地提交为 `7caae090351c9c71ce65fd8c98a0bbbbb1825bc6`，静态审阅通过；未测试、未执行实验、未发布或部署。接手时先读 [四项代码实现交付](四项代码实现交付-20261020.md) 和 state.md 的最新记录。下文保留为此前交接快照。

## 1. 用户当前要求与授权范围

用户原话：

> “这几步我觉得可以尝试，你能试着编写代码探索一下吗，在执行前先跟我汇报一下。”

用户明确选择了此前讨论中的方向3、4、5、6：

### 方向3：更换Reference后，正确选择必须相应改变

在相同Query、相同候选框及相同顺序下：
- Reference对应实例A时，答案应为A；
- Reference对应实例B时，答案应为B。

目的是迫使模型使用Reference身份，而不是仅选择最大、最完整、最显眼或排在前面的候选。

约束：
- 必须有可核验的真实实例身份对应关系。
- 不能随便替换Reference，然后猜测新答案。
- 历史拼图数据不能未经身份、坐标和来源核验直接使用。
- 目前没有完成可用成对数据的核验，也没有实现对应构建器。

### 方向4：无框全图＋局部裁剪

保留原始Reference和Query全图，同时可增加：
- Reference目标局部图；
- 带适量上下文的候选局部图。

不画框，以免遮挡。不能只用裁剪替代全图，因为会丢失位置、尺度和完整性信息。

进阶设想是只对困难样本或前两个候选做第二阶段局部比较。但这还只是设想，没有实现，也未确定触发规则。

### 方向5：候选换序诊断

先做低成本诊断：
- 同一组候选换几次顺序；
- 将输出编号映射回原始候选；
- 检查模型是否仍选择同一个实际框。

现有“全局正确编号均衡”不保证单样本换序不变。

如果发现明显位置敏感性，再考虑：
- 换序一致性训练；
- 对每个候选打分，再选择最高分，而不是主要学习列表编号。

不要默认把这一项扩大成全新打分架构重构。先实现诊断更合适。

### 方向6：后期学习率衰减

当前训练warmup后基本维持5e-5。3→4epoch的训练loss继续下降，但评测略降。

可为相同续训预算加入显式可选的学习率衰减。不能据此先认定过拟合，也不能直接认为降低学习率必然有效。

### 本轮授权边界

可以：
- 阅读代码、文档、已有记录。
- 编写本地代码，但当前需先处理第3节同步阻塞或取得明确离线授权。
- 做静态接口、引用、默认值和diff审阅。
- 按任务范围准备文档和执行方案。

暂不执行：
- 测试、构建、import/smoke检查。
- 数据生成、数据转换、裁剪生成。
- 模型推理、训练、评测。
- 新Run、Trial扫描。
- 服务器部署。
- 自动push。

用户要求的是先编写、先汇报，再执行。不要把“觉得可以尝试”解释成已经批准实际计算任务。

此前讨论过动态候选组抽样、当前VQA难例挖掘，但本次用户明确引用并要求尝试的是方向3、4、5、6，不要擅自扩大范围。

## 2. 当前开发进展：尚未修改源码

已经完成：
1. 读取项目技能与仓库维护规则。
2. 读取当前state.md。
3. 确认当前任务使用Workspace 03。
4. 检查本地Git状态：干净。
5. 检查服务器Git状态：干净。
6. 本地与服务器HEAD均为：

```text
53ab7653602f62ffc1d5c9dadfbefccf7ad67474
```

服务器相对其upstream的计数是：

```text
0  0
```

7. 阅读选择器的数据、推理、训练、collator、checkpoint和学习率接口。
8. 补做了上一项已成功结束实验的受管完成登记。
9. 尚未写任何新源码、测试或配置。
10. 尚未对本轮代码调用code_change_review，因为没有代码改动。

用户连续说“中断了”，主要是在阅读和工具调用阶段停顿。不要误认为已经存在一半写好的补丁。本文是随后按用户要求保存的交接文档，不是实现补丁。

## 3. 当前阻塞：代码准备流程的Git fetch失败

按照项目流程，编辑前调用：

```bash
python3 /home/zhengyuesong/Tools/survey-tool/surveyctl.py \
  --project . code prepare --workspace-id 03
```

第一次返回：

```text
bound repository has an active Run/lease; stop or repair it before syncing
```

原因是上一项续训已执行完毕，但管理记录仍是running。

对此已经处理：
- 查询确认：tmux不存在、真实exit code为0、完成marker存在。
- survey_run_execution complete首次返回：metrics observation is not yet stable。
- 后续再次完成登记成功，时间：2026-10-20 16:30:35。
- 没有重新运行训练或评测。

然后再次执行code prepare，返回：

```text
Git command failed: fetch; check authentication/configuration locally (stderr withheld)
```

只知道失败发生在fetch阶段，不能断言一定是哪一种认证问题。

当前处理：
- 按项目规则停止编辑。
- 没有stash/reset/clean。
- 没有改origin或分支。
- 没有SSH打补丁。
- 没有自动push。
- 计划已改为等待恢复同步，或者用户明确允许基于当前已核实基线离线开发。

项目允许用户明确授权的离线本地开发，但本轮尚未明确拿到“绕过失败同步、离线编辑”的授权。下一位Agent应说明这一点，不要伪称已同步。

## 4. 目录、环境与版本

### 研究项目根目录

```text
/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext
```

研究项目根目录本身不是Git仓库。

### 本地代码仓库

```text
/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/code-repositories/03/iploc-szy
```

### Workspace

```text
Workspace ID: 03
label: SZY-IPLoc
code_development.mode: local-git
branch: main
storage: project
transport: ssh
repository_url: https://github.com/withernova/iploc-szy
```

执行绑定来自当前Run及Workspace记录，不是仅凭聊天猜测。

### 服务器

```text
SSH alias: SZY-3090
```

SSH命令使用：

```bash
ssh -o BatchMode=yes -o ClearAllForwardings=yes SZY-3090 ...
```

### 远端代码仓库

```text
/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/iploc-szy
```

### 远端实验根目录

```text
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments
```

E-014目录：

```text
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014
```

下文简称<E014>。

### Python

```text
/songzhengyue/miniconda3/envs/IPLoc/bin/python
```

### 原始模型

```text
/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct
```

### 当前源码基线

```text
53ab7653602f62ffc1d5c9dadfbefccf7ad67474
```

提交说明：

```text
fix: satisfy base runner threshold validation for selection SFT
```

此前未变更源码实验使用的审阅记录：

```text
b70b584a7301ac8e
```

这个旧审阅不能代替未来新补丁的审阅。

## 5. 项目规则与工作方式

必须先读：

```text
/home/zhengyuesong/.pi/agent/skills/research-survey/SKILL.md
```

代码修改前读：

```text
code-repositories/03/iploc-szy/AGENTS.md
code-repositories/03/iploc-szy/README.md
code-repositories/03/iploc-szy/CONFIG_MANAGEMENT.md
```

找入口优先：

```text
docs/LAUNCH_CATALOG.md
configs/ENTRYPOINT_INDEX.md
MODULE_MAP.md
```

核心规则：
- 参数差异优先CLI覆盖。
- 长期组合才加薄配置。
- 缺能力才扩展职责模块。
- 不复制整套实验实现后改编号。
- 共用代码按职责命名，不让实验编号成为公共实现的归属。
- 不动历史数据、checkpoint、日志、结果和Run ID。
- 不静默改变prompt、采样、损失、指标和默认参数。
- 新功能默认关闭，保留当前行为。
- 不用导航检查替代测试。
- 未执行测试必须明确写“未测试/未运行验证”。
- 在Pi中改代码后需要code_change_review，修复阻塞项再审阅。
- 本轮不自动push或部署。
- 不因换到Codex就伪造审阅、执行、同步或测试记录。
- 技能中默认自动发布的描述不能覆盖本轮更高优先级的禁止自动push要求。

若入口、action或转发关系发生变化，导航生成命令是：

```bash
python tools/audit_entrypoints.py \
  --source-only \
  --write-index \
  --write-catalog \
  --write-run-readme \
  --write-shell-nav

python tools/audit_entrypoints.py --source-only --check-navigation
```

这是源码导航维护，不是模型执行或测试。仅改内部算法且入口关系不变时，不要求无关全仓导航改动。

研究记录更新走规范工具：

```bash
python3 /home/zhengyuesong/Tools/survey-tool/surveyctl.py --project .
```

不要直接修改.survey-tool JSON，不冒充人工批准。

## 6. 科学任务背景

研究领域：in-context object localization。

目前系统有两个分开的模块：

1. 冻结候选生成器：score0.4 / step200，为Query生成候选框。
2. 独立VQA选择LoRA：输入Reference、Query、Reference bbox和编号候选bbox，输出一个候选编号和EOS，不修改冻结生成器。

目前主线采用：

> 原始无标注Reference/Query图像＋文字bbox＋编号候选列表。

模型输入不包括：
- Query GT；
- 候选IoU；
- 原生成器score；
- 候选来源模型名称；
- 是否由GT加入等来源标志。

独立的新选择器实验从原始模型新建LoRA；只有明确“续训”的任务才恢复旧选择器。

## 7. 冻结1766例评测集与主要结果

固定组成：
- 总样本：1766。
- 多候选、实际调用VQA：791。
- 单候选直接保留：964。
- 无候选：11。

数据集组成：
- GOT10k：180。
- LaSOT：600。
- TAO：986。

固定候选条件下：

| 方法 | 全量mIoU | 多候选mIoU | 全量Acc50 |
|---|---:|---:|---:|
| 第一个候选 | 65.6632% | 53.3467% | 71.5176% |
| 原生成器score选择 | 69.1696% | 61.1750% | 75.5379% |
| 原生模型画框VQA | 67.8265% | 58.1763% | 73.7826% |
| 小数据选择器step72 | 69.9607% | 62.9412% | 76.2174% |
| 小数据选择器step360 | 70.3153% | 63.7329% | 76.6138% |
| 全数据画框选择器step2095 | 71.1392% | 65.5724% | 77.6897% |
| 原全数据无框选择器step1310 | 71.1487% | 65.5935% | 77.8029% |
| 历史候选＋均衡，step4041，3epoch | 71.8586% | 67.1786% | 78.6523% |
| 续训至step5388，4epoch | 71.6467% | 66.7055% | 78.4258% |
| 固定候选Oracle | 75.7399% | 75.8440% | 83.0691% |

### 当前结论

- 历史候选扩充＋均衡的组合方案，比原无框step1310高约0.710个百分点全量mIoU。
- 从3epoch续训到4epoch，没有进一步提升：全量mIoU下降约0.212个百分点，多候选mIoU下降约0.473个百分点，Acc50净少命中4例。
- 两次均为791个有效编号回复、0个无效回复。
- 不能仅凭这次小幅下降确认过拟合。
- 当前两个历史均衡版本中，step4041结果较好，但不是经过独立验证选择出的“最优checkpoint”。

以step4041为参照：
- 固定候选全量Oracle差距约3.8813个百分点mIoU。
- Oracle能命中的样本1467例，实际命中1389例。
- 即78例有IoU≥0.5候选但选择器没选中。
- 另外299例没有IoU≥0.5候选，纯选择器无法把它们变成Acc50命中。

这些数字说明仍有选择空间，但不保证全部Oracle差距可被模型恢复。

## 8. 最新已完成的续训Run

### 父训练Run

```text
e014-historical-balanced-vqa-lora4epoch-20261019
```

父训练原计划：4epoch、5388更新、86208样本呈现。

用户中途要求暂停：
- 最后日志step4463。
- 最新完整checkpoint为step4041。
- 父Run记录为用户中断，不是4epoch完成，也不是科学失败。

### 新续训Run

```text
e014-historical-vqa-resume4041-to5388-eval1766-20261020
```

Dispatch：

```text
dispatch-fa4dbf97078548450b180f74
```

任务：
- 从step4041恢复。
- 仅补1347更新、21552呈现。
- 到原总4epoch端点step5388。
- 原训练门禁通过后，自动评测最终checkpoint一次。
- 不搜索其他checkpoint，不自动重试。

### 真实执行结果

```text
exit code: 0
root metrics status: completed
training status: passed
steps: 5388
examples_seen: 86208
session_examples_seen: 21552
finite_grad_fraction: 1.0
```

固定batch训练门禁：

```text
loss_before: 6.459710672857e-05
loss_after:  2.937922826040662e-05
adapter_delta_norm: 5.5452647419556405
```

训练耗时：13754.442301273346秒。

已在2026-10-20 16:30:35完成受管登记：

```text
dispatch status: completed
run workflow_stage: analysis_pending
```

工具将训练、评测嵌套指标保留为辅助指标草稿；未修改Claim。

### 恢复限制

恢复了adapter、AdamW状态、scheduler、step、samples、历史loss等记录。

没有恢复逐rank RNG完整状态，而是重新设置seed。不能声称与不间断训练逐位等价。

## 9. 关键checkpoint、文件和SHA

### 3epoch checkpoint

```text
<E014>/e014-historical-balanced-vqa-lora4epoch-20261019/payload/training/checkpoints/samples_00064656_step_004041
```

adapter SHA：

```text
a3c7ba7dff8df6c8bd1743db9b51a3ef95c5eae6d092999438594bef44d88840
```

已核：step4041、samples64656、history4041、AdamW状态504项、scheduler last_epoch4041、原max_steps5388。

### 4epoch最终checkpoint

```text
<E014>/e014-historical-vqa-resume4041-to5388-eval1766-20261020/payload/training/checkpoints/samples_00086208_step_005388
```

adapter SHA：

```text
4bebaaa3ef6b13e6fdae2343e5093f18b3545fec28253f747db8da429d8646d3
```

### 最新Run产物

```text
managed_console.log
.survey-tool-exit-code
training_summary.json
metrics.json
payload/training/metrics.json
payload/evaluation/metrics.json
payload/evaluation/predictions.jsonl
```

完整训练metrics SHA：

```text
7796628285e7b09256d57d9360e9d206832151c8c2d5f07f47131dbd2d6efb6d
```

### 最新评测精确指标

```text
full mIoU:   .7164674866079094
multi mIoU:  .6670551378939651
full Acc50:  .7842582106455266
multi Acc50: .7243994943109987
```

对原score选择：
- IoU改善100例、损害50例。
- 修复80例Acc50错误、破坏29例原命中。

注意：step4041有独立逐样本审计文件；step5388当前结果已读取成功产物并完成管理登记，尚未新增同等完整的独立逐行比较审计文件。不要夸大验收范围。

## 10. 当前训练数据是怎样构建的

### 合法原始训练对

最初从E009训练数据清理得到：8367个合法正Reference–Query对，4540个原视频/序列组。

按数据集：
- GOT10k：7315。
- LaSOT：553。
- TAO：499。

排除了已有验证/测试来源组。

分组依据：
- GOT10k：meta_info.ini中的原视频URL。
- LaSOT、TAO：序列。
- TAO仅训练split。

不同候选组、编号排列，不算新的独立图像对，更不等于新的独立视频。

### 四个候选来源

1. 已有score0.4/step200生成器。
2. E012 step494单框模型，无score协议。
3. E013 SFT step659，三个同一实例的位置/边界假设。
4. E013 instances step650，多实例候选协议。

后三个模型已经分别在8367合法训练对上生成，总计25101个source-input组合。

不能混淆“同一实例的三个框假设”和“多个相似实例的候选框”。历史1766预测没有拿来训练。

### 入题门槛

```text
K >= 2
best IoU >= 0.5
best IoU - second IoU > 0.05
```

### 当前历史均衡训练池

```text
8203个不同图像对
14668个候选组
```

不同图像对：
- GOT10k：7183。
- LaSOT：527。
- TAO：493。

候选组：
- 原生组：13934。
- 跨源互补组：326。
- GT加入组：408。

跨源互补组只在旧生成器非空但没有好框、其他来源存在好框时构建，受明确规则限制。

GT加入规则：
- 全部四个来源都没有IoU≥0.5好框时，才在训练中加入GT。
- 评测输入绝不加入Query GT。

### 当前实际训练清单

```text
21552行/epoch
三个数据集各7184次曝光/epoch
```

特点：
- 每个合法source至少覆盖一次。
- 同一数据集内source曝光次数差≤1。
- 候选组均匀抽取。
- 正确编号在dataset × candidate_count条件下均衡。
- 是冻结的静态清单，4epoch重复同一清单。
- 不是动态加权DataLoader。
- 候选组/排列数量不会增加某个source的总曝光权重。

实际选中：
- 9014种候选组。
- 原生行19187。
- GT加入行1878。
- 互补行487。
- 1823行是生成器score漏选，但不代表当前VQA一定会错。

数据哈希：

```text
train.json:
6d2a9b4fcd6825736aa3534afd6b2de895da4f45352d79246ef11125cd2ffc21

candidate_groups.json:
ba1ad072b520427f0cd96011493b6a2c6ddab633532d339e3ef10c60706975b5
```

位置：

```text
<E014>/e014-historical-balanced-vqa-lora4epoch-20261019/inputs/
  train.json
  candidate_groups.json
  source_exposure.json
  data_acceptance.json
  prompt.txt
```

### 验证集缺口

旧内部验证集334例：
- 多候选数量少。
- 没有TAO。
- 不能充分评估三域均衡策略。

若重新建立验证集：
- 按视频组隔离。
- 覆盖三域。
- 已被当前模型训练过的样本，不能直接称为当前模型的独立验证集。

## 11. 当前训练和评测设置

选择训练：
- Qwen3-VL-8B-Instruct。
- 独立语言LoRA。
- r8、alpha16、dropout0。
- NF4、BF16、SDPA。
- 8GPU，每卡batch1，梯度累积2，有效global batch16。
- lr 5e-5，warmup ratio .05，gradient clip .3。
- vision patch预算4096。
- seed 20260901。
- 半epoch保存一次checkpoint。
- 仅监督编号和EOS。
- 当前不使用额外辅助loss。

评测：
- BF16、SDPA、8GPU。
- greedy，max_new_tokens=16，显式要求EOS。
- vision4096，seed20260901。
- --prompt-variant exact_instance。
- 不传--draw-boxes。
- source候选原顺序。
- 无效回复计IoU=0，不回退到score。

无框prompt SHA：

```text
b737f254c6c86215fa009600eccad51ac741cb46db6e7188aacfe3f390f7f6f2
```

## 12. 已读源码与关键接口

以下路径以代码仓库code-repositories/03/iploc-szy为根。

### A. VQA推理与输入构建

```text
iploc_szy/evaluation/candidate_vqa.py
```

约330行，当前同时承载prompt、输入构建、可选画框、编号解析、评测CLI主体和统计。

主要函数：

```python
selection_prompt(variant="exact_instance", draw_boxes=True)
draw_inputs(reference_bbox, image_paths, boxes, destination)
read_pinned(path, digest)
dump(path, value)
model_sample(reference_bbox, image_paths, boxes, prompt=PROMPT)
parse_choice(text, count, terminated)
summarize(rows)
main()
```

特别注意默认值：
- selection_prompt()函数默认draw_boxes=True。
- CLI的--draw-boxes是显式开关，默认false。
- CLI默认prompt variant是baseline。
- 当前实际实验显式传exact_instance。
- 不要在重构时把这些默认值静默改掉。

model_sample()是输入白名单：
- 只传图像、Reference bbox、候选bbox。
- 不带Query GT、score、类别、旧回复。
- assistant占位为空，由生成逻辑移除。
- 新视图和换序功能应维持这个边界。

parse_choice()：
- 要求terminated/EOS。
- 严格正整数。
- 返回0-based候选index。
- 非法值返回None。

当前CLI预检：
- manifest/predictions SHA。
- 样本ID、dataset_index、GT对应。
- 每个候选box合法性。
- 重算IoU并核对。
- 原score/first/Oracle指标一致。
- 全量与多候选预期数量。
- 输出目录必须全新。

### B. VQA薄CLI

```text
tools/evaluate_candidate_vqa.py
```

仅约9行，是共享实现的兼容转发。不要另复制一套评测器。

### C. 数据准备

```text
tools/prepare_candidate_selection.py
```

约209行，已有子命令manifest、sft。

主要能力：
- SHA绑定。
- 正样本筛选。
- GOT原视频/LaSOT序列隔离。
- 固定验证拆分。
- 候选IoU检查。
- 随机基础排列＋全部循环移位。
- 画框SFT数据导出。
- 保存来源与哈希。

限制：
- 原manifest子命令只显式支持GOT10k和LaSOT身份协议。
- 不能因为后来数据有TAO，就假装这个通用入口已经支持TAO实例身份构对。
- 当前sft路径固定使用画框prompt和draw_inputs()。
- 后来的大规模无框/历史均衡数据由独立Run的数据准备过程产生；不要把旧工具能力说大。

如增加Reference成对子命令，应明确：
- 输入schema。
- 身份证据。
- annotation/source哈希。
- 同Query、同候选约束。
- 分组隔离。
- 不合格样本拒绝原因。
- 不凭一个verified=True就冒充真正核验。

具体采用TAO原生标注适配还是显式审核过的中间契约，尚未决定。

### D. 选择数据集与collator

```text
iploc_szy/datasets/candidate_selection.py
```

类：CandidateSelectionDataset、CandidateSelectionCollator。

数据集当前检查：
- manifest SHA。
- 非空、ID唯一。
- prompt_protocol == "candidate_selection"。
- 答案为合法编号。
- 最后一条assistant内容严格等于answer。
- image_paths和image_sha256长度必须为2。
- 每张图片SHA。

这就是加入局部图的直接接口缺口：需要显式支持多图视图协议，而不是随便放宽校验。

Collator：
- 复用Qwen SFT collator。
- 不做bbox输出token定位。
- 监督严格为编号＋EOS。
- 屏蔽EOS后模板尾换行。
- 记录supervised token IDs。

### E. 共用collator

```text
iploc_szy/datasets/collator.py
```

类：Qwen3VLSFTCollator。

本体按sample["image_paths"]加载图片，支持可变图像数的基本结构。

会记录image paths、image_grid_thw、每图patch tokens、prefix/answer token数、reference answers。

因此，裁剪功能不必复制整套collator。但需要验证：
- messages图像顺序与image_paths一致。
- 各图角色明确。
- train/eval共用同一视图构建逻辑。
- 多图预算和实际token-grid可追溯。

每图4096不等于总共4096。增加图片会增加计算量。

### F. 选择器runner

```text
iploc_szy/engine/selection.py
```

类：SelectionSFTLoRARunner(SFTLoRARunner)。

当前约33行，仅覆盖空诊断指标、teacher-forced编号准确率、分布式汇总。没有独立训练循环。

### G. 共用SFT runner

```text
iploc_szy/engine/runner.py
```

约737行。

重要方法：

```python
batch()
run()
_train_step()
_prepare_run()
_finalize_run()
_save_checkpoint()
_initialize_or_restore_checkpoint()
_restore_checkpoint_if_requested()
```

#### 数据访问

batch()采用确定性strided modulo索引，不是加权DataLoader。

因此：
- 加一个未被读取的JSON weight字段不会改变采样。
- 如果未来实现成对batch或动态抽样，必须真正接入现有访问逻辑。
- 本轮不必顺带实现这些未授权扩展。

#### 学习率

当前：

```python
torch.optim.lr_scheduler.LambdaLR(
    optimizer,
    lr_lambda=lambda step: (
        min((step + 1) / warmup_steps, 1.0)
        if warmup_steps else 1.0
    ),
)
```

即warmup后保持常数。

_train_step()顺序：
1. 计算loss/反向。
2. 有限性检查。
3. clip。
4. 记录当前optimizer lr。
5. optimizer.step()。
6. scheduler.step()，准备下一步lr。

设计衰减时必须明确：
- 函数输入是已完成步数还是即将执行步数。
- 从4041恢复后，第一次新更新是4042。
- 最终5388是否达到预定end LR。
- 是否保留原warmup。
- 是否保持原总预算。

#### 恢复陷阱

恢复会：

```python
optimizer.load_state_dict(...)
scheduler.load_state_dict(...)
```

所以仅覆盖config里的optimizer.lr，可能被checkpoint中的optimizer lr覆盖。不能只改一个CLI数字就声称续训LR已改变。

如果支持改变恢复后的调度策略：
- 必须显式opt-in。
- 记录旧策略与新策略。
- 保留AdamW状态、history和步数。
- 保存可再次恢复的新调度状态。
- 防止恢复时静默退回旧策略。
- 默认恢复行为保持不变。

这部分目前只有设计考虑，尚未编码。

#### checkpoint内容

trainer_state.pt包含：format_version、step、samples_seen、next_checkpoint_samples、history、localization_history、auxiliary_history、pipeline_state、optimizer、scheduler、max_steps、seed。

#### 原完成门禁

必须保留：
- 同一个固定batch的loss下降。
- adapter delta > 0。
- finite gradient fraction == 1。

不能为了让新实验“成功”放松门禁。

### H. Hooks

```text
iploc_szy/engine/hooks.py
```

重要：
- TrainingHistoryHook保存真实逐步lr、loss、step、样本数。
- MetricsWriterHook在after_run中写完整metrics。
- 若新增调度策略元信息，要在metrics写出前加入，不要在写出后才修改内存字典。

### I. 配置

```text
configs/sft/candidate_selection_lora.py
```

入口链：

```text
tools/run.sh
  → configs/sft/candidate_selection_lora.py
  → tools/train.py
  → SelectionSFTLoRARunner
```

默认：独立fresh LoRA、max_epochs1、lr5e-5、warmup.05、clip.3、initialize_from=None、resume_from=None。

包含：

```python
localization_iou_thresholds=(0.5,)
```

这是为满足base runner构造器校验。选择器实际覆盖了定位诊断方法。不要误删它，否则会重现历史构造失败。

## 13. 建议的最小实现边界

这是建议，不是已经实现的设计。

### Reference成对数据

优先扩展已有准备入口，单独封装可复用身份校验职责。

至少保存：
- pair/group ID。
- 两个Reference的真实instance ID。
- 同一个Query身份。
- 候选集合与顺序。
- 两个不同正确答案。
- 来源annotation SHA。
- 图像SHA。
- 视频组。
- split。
- 接受或拒绝原因。

训练输出可以先复用现有编号SFT格式，不必一开始引入新loss。

不能保证数据规模之前，不承诺能生成多少成对题。

### 局部视图

共享一个train/eval都能调用的构建接口：
- 默认仍是原两张图。
- opt-in时增加Reference crop和候选crop。
- 原图不覆盖。
- crop坐标、padding、裁剪边界、图像SHA可追溯。
- 不通过Query GT决定crop。
- crop顺序与候选编号严格对应。
- 不在图上画GT或候选框。
- 文档说明新增图像带来的计算变化。

### 换序诊断

复用当前评测器：
- 每个原始样本保存不同排列。
- 明确permuted_index → source_index。
- 原始候选框不变。
- 单框、无候选路由不变。
- 保存每次回复、EOS、合法性、映射后选择。
- 统计有效选择一致性，单独统计无效回复。
- 不把两次都无效当成正确一致。
- 多次排列不算更多独立样本。
- 第一版不必自动多数投票覆盖原选择结果。

### LR衰减

优先小范围扩展选择器runner或可复用调度职责：
- 默认None保持原逻辑。
- 显式线性或cosine策略。
- 显式start step、end factor/target LR。
- checkpoint中保存策略。
- 恢复策略发生变化必须显式声明。
- 不重置AdamW。
- 不改变总更新数。
- 不改原门禁。

## 14. 本地证据文件

主要目录：

```text
.pi/analysis/e014/historical-candidate-sources-20261019/
```

已有文件：

```text
remote_paths.txt
asset_probe.json
prediction_reuse_audit.json
identity_audit.json
shortlist_verified.json
generation_preflight.json
generation_command.json
generation_result_audit.json
balanced_training_data_audit.json
balanced_train_command.json
balanced_training_user_stop.json
step4041_eval_command.json
step4041_eval_audit.json
resume4041_preflight.json
resume4041_command.json
```

注意：
- 初版prediction_reuse_audit.json中基于不存在的ID得到的0匹配结论无效。
- 后续identity_audit.json才是正确的身份审计依据。
- 不要重新引用已经纠正的错误统计。

历史候选报告：

```text
shell/06_experiments/E-014/历史checkpoint候选扩集审计-20261019.md
```

旧选择器证据：

```text
.pi/analysis/e014/selection-sft/
```

其中包含初始小数据准备和训练、step72和step360评测、全数据GT加入、画框step2095评测、无框step1310训练和评测、用户中断记录。

### state.md仍有过时状态

顶部还写着最新续训“已启动”，尚未追加完成结果。实际最新状态以真实exit0、root metrics、本次成功的managed complete为准。

未来更新应追加完成事实，不删除旧启动/中断历史。

## 15. 冻结评测输入

来源Run：

```text
e014-discovery-score04-step200-eval1766-20261015T152856Z
```

manifest相对该Run目录：

```text
inputs/manifest.json
```

SHA：

```text
8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d
```

冻结候选：

```text
payload/evaluation/predictions.jsonl
```

SHA：

```text
1a864fdce10f300ec53ddf2945b7e2d063c74280d7a750207dcff99a7ff76129
```

不要重新生成或覆盖这些输入。

## 16. 历史限制与不能遗忘的边界

- Frozen1766已经多次用于探索，不能继续把它称为完全未触碰的独立测试集。
- 历史生成器对数据的暴露情况尚未完全厘清。
- 单seed结果不能声称统计显著。
- 历史候选、GT政策、采样均衡、训练数据量和计算预算一起变化，不能把收益单独归因于某一个因素。
- 三数据集等曝光不等于独立场景等覆盖。
- 旧历史生成器没有逐例EOS标志，不能把默认EOS停止说成逐例EOS认证。
- “score为0的单框模型”仍没有唯一核实的checkpoint；实际使用的是已验证的E012无score模型，不要混称。
- 老的用户中断训练必须保持中断历史，不能因为有可用checkpoint就写成完成。
- 老小数据5epoch训练曾因64KiB管理读取限制而登记失败，尽管训练本身成功。不要在本轮顺带重跑或洗掉历史。
- Steward自动监控和任务队列保持停止/暂停。
- 用户不希望短周期轮询；计划性检查间隔至少30分钟，优先事件驱动。
- 不自动恢复训练、不扫checkpoint、不新增评测。
- 本轮不修改Claim。

## 17. 当前计划与下一步

当前计划全部尚未进入实现：

1. 恢复代码同步，或获准基于53ab765离线开发。
2. 实现经验证的Reference成对数据入口和无框局部视图。
3. 实现候选换序诊断及可选续训LR衰减。
4. 静态审阅、修复、本地提交，向用户汇报：
   - 哪些功能已写。
   - 默认行为是否保持。
   - 哪些真实数据依据仍缺失。
   - 哪些验证未执行。
   - 建议先运行什么。
   - 预期数据和计算预算。
   - 等待用户批准实际执行。

不要在这一步自动执行训练、评测、数据准备或测试。

## 可直接给Codex的简短任务指令

> 请接手以上任务。先确认本地仓库状态与代码同步阻塞。当前代码基线为53ab7653602f62ffc1d5c9dadfbefccf7ad67474，尚无本轮源码改动。用户希望准备Reference成对监督、无框局部裁剪、候选换序诊断、续训LR衰减四项代码，并要求执行前先汇报。复用已有数据准备、VQA评测和SFT runner，不复制实验实现。所有功能默认关闭，保留历史行为。尚未授权测试、数据生成、训练、评测、push或部署。代码prepare因Git fetch失败受阻，不要伪称同步成功，也不要未经明确授权绕过。先解决同步或确认离线编辑权限，然后实现、静态审阅并汇报。
