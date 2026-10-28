# e014-model-parallel-ddp4x2-bf16-20261021 · 继续完成用户要求的4x2模型并行DDP能力验证。前次1/2shot通过而4shot反向OOM；此次保留全部失败产物，使用独立新目录，同8个GOT视频/同1,2,

- 父 Run：`e014-model-parallel-ddp4x2-capability-20261021`
- 来源版本：2026-10-21T18:00:04
- 状态：failed
- Workspace：03

## 本次任务
继续完成用户要求的4x2模型并行DDP能力验证。前次1/2shot通过而4shot反向OOM；此次保留全部失败产物，使用独立新目录，同8个GOT视频/同1,2,4shot采样/每图4096raw patches/14+22层切分/4进程/global16，仅显式改为冻结embedding BF16＋SFT autocast BF16，记录真实q_proj dtype。不安装或改变环境；FlashAttention2现有扩展GLIBC不兼容，使用原生SDPA。每shot2步并4shot恢复1步，共7更新112呈现，fresh LoRA，非长训练/非Qwen2/非FOCUS attention loss。包含聚焦测试、必要指定SHA发布部署与受管运行，失败停止。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户要求4副本×2卡DDP能力验证。使用8个GOT训练视频真实1/2/4shot、最后帧Query、同原采样器；Qwen3-VL-8B fresh语言NF4LoRA r8/alpha16、BF16/SDPA、nonreentrant checkpoint、4096 raw patches/图、前14/后22层切分、4DDP进程、每副本batch1累积4/global16、SFT lr2e-4/warmup.03/clip.3/seed20260901。每shot2更新32呈现；4shot保存step2后独立目录恢复至step3再16呈现，共7更新112呈现。核每次更新全LoRA跨rank SHA一致、全卡峰值、保存恢复与有限梯度。包含18项聚焦CPU测试（实际计数以日志为准）。无历史checkpoint续训、无正式泛化评测；不继承父训练预算、指标、数据定义或Claim。任一步失败停止，不自动重跑。 父能力Run已保留：1/2shot通过，4shot首次反向OOM。此次独立重测显式frozen embedding BF16及runner autocast BF16；属于数值路径变更，非位级等价优化。记录各rank首尾attention q_proj实际输出dtype；使用原生SDPA，不安装依赖。三份manifest逐字SHA固定与父Run一致。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-bf16-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'d209334566a51e8a50e9f7cc79ed25c54a3e2291c03d7e72c120c41680b47b51'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：f3497cad782e03a8b80c5bac581b987e501cd31f
- 随机种子：20260901
- 配置：configs/sft/qwen3vl_lora_model_parallel_ddp.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-bf16-20261021/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-bf16-20261021/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-bf16-20261021/metrics.json

## 结果
尚无结果。

### 分析
四组GPU训练均成功：1/2/4shot各2更新32呈现，4shot checkpoint恢复再1更新16呈现，共112呈现。所有finite_grad_fraction=1、LoRA有真实更新，每步四副本全部LoRA SHA一致，恢复起始SHA与原step2相同且loss_before=原loss_after。单卡allocated/reserved峰值GiB：1shot11.082329/11.802734；2shot11.445843/12.248047；4shot12.813782/13.498047；恢复12.813532/13.496094。完整Run真实exit1：仅末尾汇总脚本要求q_proj输出BF16，而实测均FP32。父Run保持failed，不冒记exit0；独立CPU审计Run核验有效训练事实与实际dtype。45份下载文件SHA核验通过。

### 局限
启用BF16 embedding/autocast不等于q_proj输出BF16；首尾实测FP32，未直接观测SDPA内部算子dtype，不做精度机制因果结论。8段训练视频、短程Qwen3 NF4 SFT；无Qwen2/全FOCUS/全量最长样本/定位泛化结论。

### Claim 边界
仅当前Qwen3 NF4 SFT短程多图能力，非Qwen2/FOCUS attention loss/GRPO验证，不代表全量最长样本都可运行或科研性能提升。

### 审核入口
```json
[
  ".pi/analysis/e014/model-parallel-bf16-20261021/download_audit.json",
  ".pi/analysis/e014/model-parallel-bf16-20261021/failure_receipt.json"
]
```

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
