# Config / Shell 声明与路由审查

基线 `1622e5f64a70239d02145f017cfd991cf8318e47`。此报告审查源码，不执行 config、Shell、worker 或模型。

## 覆盖事实

- 129 Python config：87 个非 config_alias 文件均全文读取；42 个 config_alias 均经仅一条 literal 声明/库内现存目标/继承图核对。继承型兼容配方仍属于87，不混入42。
- 当前配置没有 import。AST call inventory 只有 dict、sum(screening_counts.values())、list(range(8))。非纯 dict 的三个配置已逐行核对。未见顶层模型、manifest/checkpoint、GPU或目录IO。这不证明通用 Config Python 执行器是安全沙箱。
- 88 Shell：全部已有 bash -n=0；现在每个入口主体已全文读取或经过严格短模板核对。21 common shortcuts、27 relative aliases 经精确模板验证；另1个 alias 是已全文读取的固定绝对外部路径，不能等同当前 checkout。
- 所有显式 `-m iploc_szy...` 与 literal analysis.entrypoint 的29条边，经 AST 文件/函数/显式 re-export 解析核对。初次检查把 re-export 当未定义而拒绝，已改用真实显式转发链；未将该启发式结果记成缺失实现。
- “入口存在/主体已核对”不等于所有目标 worker 算法已完成审查。head/蒸馏/统计/测试/文档等覆盖继续在全仓账本追踪。

## 按职责的配置链

| 族 | 入口与实现 | 已确认要点 / 风险 |
|---|---|---|
| 单进程模型分片 SFT | qwen3vl_lora.py → train.py → Qwen3VLLoRASFT/Runner | 是一份模型跨GPU，不能称DDP；设备图/显存声明与实际硬件未运行验证 |
| 单rank/2/4rank NF4 SFT | qwen3vl_lora_ddp → localization/focus recipes → common launcher | 单rank DDP envelope 缺失A001；max_epochs/max_steps A003；fresh seed时序A007 |
| 普通/branch evaluate | launch/branch → evaluate.py | 动作解析A004/A005；checkpoint完整性A002；LoRA metadata边界A014 |
| native infer | frozen eval base → native recipe → infer.py | 当前声明visual2048/greedy/selection不全部进入worker，A006；真实processor/generation默认未知 |
| named run | named_run/output/work_dir → run_branch/run_management | 身份、恢复和独占目录不能机械等同；普通非train named action与worker不一致A005 |
| GT-mask/dynamic/fixed teacher | alignment/gt_mask/dynamic/pipeline → SFT/attention_distillation | 已确认声明treatment/heads/teacher sources；构造与loss完整审查待完成，不从配置名称推断处理真的生效 |
| E-012 CLI head screening | config run_spec/selection_spec/visualization_spec → -m head_screening.* | 大多保留旧liuwenchu绝对ROOT/Conda；不是可自由迁移的新通用launcher。两个circuit迁移后relative ROOT错A016 |
| E-012 analyze | analysis.entrypoint → analyze.py → collector/audit worker | metric/split/null/seed/预算声明显式；caller/worker参数和统计处理仍需逐项核对 |
| E-013 GRPO | branch → grpo.py → rl | source/init/G4等已穿透；multi3/rank无有效rank开关A015，rank-CF还改变rank数量 |
| E-014 symmetric GRPO | shared settings base → thin recipes → original coordinator → rl | 冻结SFT659/8rank/数据来源；不是任意manifest适配；reward/observer变体不复制算法 |
| E-014 frozen eval | profile aliases → step800 shared Shell → evaluate.py | CLI不自动resume；step/checkpoint/prompt来源显式；生产assert门禁A013，不能以本地HEAD代远端实际执行SHA |
| E-013 standalone probes | dedicated CLI/no config | single inspect有输出A009、零有效证据exit0 A010；不推及有独立门禁的8GPU版本 |

## 路径、名称与注释不能冒充事实

- `run_e009_head_stability_suite.sh` 实际 exec 固定绝对 liuwenchu checkout；其 canonical launcher 也 cd 固定 PROJECT。索引中的相对转发名称只是导航，不能证明运行当前绑定源码。
- `qwen3vl_8b_focus_tasks.py` 的 checkpoint label/notes仍出现validation100，而默认 test_dataloader 指向combined1766；常规branch部分run_name写500但source路径650。这些不证明实际运行错误，但只能从有效 config/snapshot取来源和cohort，不能从名字/注释补造。
- 多个旧 E-012 run_spec使用旧readonlyartifact SHA。source存在不是远端文件存在，亦不是SHA当前匹配；只有实际执行preflight能核验输入。
- R-011声明150样本含TAO，R-012默认100样本无TAO；其“唯一差别”注释不能代替真实cohort对照。
- R-014的oracle_query_gt是明确的GT信息上界诊断，会把Query GT放入support框文本。它不能作为普通不泄漏Query GT的推理结果；必须按条件单独记录。GRPO生成条件不使用该路径。
- R-016注释已明确v1图像替换未生效。不得把该注释里的历史观察当作本次重新验证；需核对v2 worker同时修改messages/image_paths再讨论结果。
- root路径/manifest/model/checkpoint非本机可验证输入未读取、替换、创建或安装。没有把动态/缺失字段从当前Shell默认值补回历史Run。

## 不做的事

不改参数、默认prompt/reward/parser、预算、resume能力、source/SHA、历史Run或输出。没有因审查而运行shell inspect、模型、tests、Conda/GPU/SSH、push或deploy。审查发现与修复授权、科学设计批准、实验执行授权分别处理。
