# e015-qwen2-selector-e014clean4shot-20261028 · 用户明确重新训练：E014清洗仅作数据来源，VQA参考数/提示/训练配置统一原E015四参考协议；沿原4epoch/global16设置，训练后固定E015和E

- 父 Run：`e015-qwen2-selector-e014clean-20261026`
- 来源版本：2026-10-27T10:39:10
- 状态：running
- Workspace：03

## 本次任务
用户明确重新训练：E014清洗仅作数据来源，VQA参考数/提示/训练配置统一原E015四参考协议；沿原4epoch/global16设置，训练后固定E015和E014两组proposal均评测1/2/4shot，不单列多框子集；不恢复GRPO。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户纠正：只将数据来源替换为E014清洗数据，E015内VQA参考数/提示/训练设置必须统一，并明确重新训练。原1shot clean模型保留为历史非统一协议诊断，本次fresh Qwen2独立LoRA四参考重训，不恢复旧1shot权重或已取消GRPO。以原E015 r3 selector真实resolved配置SHA0842fe71...为设置基准：NF4/BF16/SDPA、4×2GPU/layer_split10、LoRA r8 alpha16 dropout0、语言层target_modules、原图exact_instance多参考prompt、只监督候选编号+EOS、global batch16、4epoch、lr5e-5/weight_decay0/warmup.03/clip.3/seed20260901、末1/4线性降至.1、每.5epoch保存均相同。数据取原E014清洗16684行，直接按相同首参考/查询帧匹配E015冻结有效4shot训练清单；验证来源GT和TAO track，保留候选/排列/标签与余下样本顺序；26个不在原有效清单的来源记录删除，不做近邻帧替换。保护E015作者36测试类及全1/2/4shot测试视频/图片，同时保护当前E014测试查询视频及全部参考图；之前18跨数据集重合视频及新增图像路径/SHA交集整组删除。对新五图输入逐图哈希/可读性/尺寸/框检查，核原E015全部1604题共享prompt完全相同；真实保留数、删除清单和步数在data/audit.json，不预造。4epoch保持而总更新数依规模变化，不宣称等步数纯数据因果。普通训练/评测复用现有launcher和evaluate_candidate_vqa CLI，唯一任务局部run.py负责数据对齐与调用；无共享源码修改，固定已部署0e02d856。训练完成后固定E015每shot1289查询与E014共同1745查询proposal各做1/2/4shot，原候选不重生成；E014另报同1727历史无重合子集以保持比较分母，只报告总体/分集，不单列多框子集。244指标含训练行数/步数/有限梯度/adapter变化。继承旧探索/生成器曝光/近重复未知边界，无Claim升级。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean4shot-20261028/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'9c39ad246fddb8c598f94d2cdfe7ce562974d1e260e5ac5ed0997fda9a6355ea'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：0e02d856ae30837eb60b511e8303cb50a50d1c26
- 随机种子：20260901
- 配置：configs/experiments/E-015/selector.py with original r3 resolved model/runner/loader settings; data-only source adaptation; existing candidate VQA CLI
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean4shot-20261028/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean4shot-20261028/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean4shot-20261028/metrics.json

## 结果
尚无结果。

### Claim 边界
保持训练协议，数据规模与更新总数随数据来源变化；旧探索候选、源视频/图像零交集非全部近重复保证；旧1shot训练结果为非统一协议诊断；不升级Claim。

### 产物索引

2026-10-28 已核实际训练首步：e015-qwen2-selector-e014clean4shot-20261028，全部16173条4shot（LaSOT2908/GOT7175/TAO6090），删511条（26个无有效四参考来源及18测试重合视频关联题目）；7806源样本，48870训练/测试唯一图像可读性/SHA检查通过。原1604题prompt逐条一致，候选排列/标签保留；视频/路径/内容SHA/受保护LaSOT类别交集均0。数据SHA6492bd956a13fae0be6018867328a00a7dddcbcbba03715514fbe18029d3ceeb。实际resolved配置与原E015仅数据路径/SHA、输出目录及epoch缩放衰减起止不同。4epoch/global16/4044更新；4×2GPU实际first update loss0.4964896869、finite_grad_fraction1.0、rank0双卡峰值allocated12.3623GiB（不是全卡峰值）；无OOM/Traceback。初始化耗时为四副本完整输入哈希复核，已完成进入训练。随后固定E0151289与E0141745各1/2/4shot评测，E014另保留同1727分母；只总体/分集。GRPO保持取消，尚无本次最终结果。证据.pi/analysis/e015/selector-e014clean4shot-20261028/{data_and_startup_observation,input_read_progress_observation,training_progress_observation,startup_managed_status}.json。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
