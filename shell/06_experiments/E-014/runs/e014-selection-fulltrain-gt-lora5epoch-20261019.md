# e014-selection-fulltrain-gt-lora5epoch-20261019 · 用户明确授权完成数据后自动启动5epoch训练且不走Steward。现在启动一个受管串行任务：只读inotify等待已在运行的渲染exit0，不重复渲染；核增强

- 父 Run：`e014-selection-fulltrain-step200-gtaugment-20261018`
- 来源版本：2026-10-19T00:22:07
- 状态：failed
- Workspace：03

## 本次任务
用户明确授权完成数据后自动启动5epoch训练且不走Steward。现在启动一个受管串行任务：只读inotify等待已在运行的渲染exit0，不重复渲染；核增强来源/GT规则/标签/全部渲染SHA/视频隔离及8379条3571源后，复用configs/sft/candidate_selection_lora.py训练全新独立Qwen3VL8B语言LoRA，5epoch，seed20260901/globalbatch16/lr5e-5/r8alpha16/NF4/vision4096，每.5epoch保存，原loss门禁保留。无resume或旧选择器初始化，不额外评测，任何阶段失败停止且不自动retry。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：共享代码53ab765不变。单Run脚本为inputs固定SHA工件，独立本地审阅仓库提交ae4eb85757b4f09bd26e5943056c372d6c9447b3/review3fd7274200e7d6de，无push/共享源码部署。直接受管执行，不使用Steward队列或自动监控，用户已明确授权。
- 命令：PYTHONPATH=. OMP_NUM_THREADS=1 /songzhengyue/miniconda3/envs/IPLoc/bin/python -u -c 'from pathlib import Path;import hashlib;p=Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-gt-lora5epoch-20261019/inputs/auto_train_fulltrain.py'"'"');assert hashlib.sha256(p.read_bytes()).hexdigest()=='"'"'974c76f4ad1abd12e075148f008fa6c18906848f11833df0f075a7d0cf1b9b9e'"'"';exec(compile(p.read_bytes(),str(p),"exec"))'
- 代码版本：53ab7653602f62ffc1d5c9dadfbefccf7ad67474
- 随机种子：20260901
- 配置：configs/sft/candidate_selection_lora.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-gt-lora5epoch-20261019/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-gt-lora5epoch-20261019/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-gt-lora5epoch-20261019/metrics.json

## 结果
尚无结果。

### Claim 边界
仅训练事实，未授权额外验证测试；不得声称泛化收益或修改Claim。完整训练源含TAO；生成器历史暴露限制仍存在。

### 审核入口
.pi/analysis/e014/selection-sft/fulltrain_autostart_command.json

### 过程记录
01:13:29 managed running/tmux_alive；已读取真实日志AUTO_STAGE waiting_for_existing_render; event-driven, no polling。自动串行进程已单次启动，不是仅计划：等父渲染exit0→固定输入及全量渲染验收→检查GPU空闲和代码SHA→fresh5epoch训练。当前尚无训练更新。Steward监控stopped/队列paused，不需要用户再次同意；不做周期进度检查，若人工安排定时检查必须>=30min。初次continue被父受管控制拒绝并未执行；父生成真实完成后managed complete释放，再次continue实际单次启动，禁止再launch。工件review3fd7274200e7d6de/commit ae4eb85757b4f09bd26e5943056c372d6c9447b3，scriptSHA974c76f4ad1abd12e075148f008fa6c18906848f11833df0f075a7d0cf1b9b9e，共享源码53ab765未变。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
