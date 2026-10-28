# [[doveh2025iploc]] — Teaching VLMs to Localize Specific Objects from In-context Examples

> source: shell/03_evidence/papers/doveh2025iploc.pdf
> content_hash 仍以原始 PDF 计算；以下阅读以 MinerU .md 为准（若有）。
> mineru_md: /home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/papers/Teaching VLMs to Localize Specific Objects from In-context Examples_2024/hybrid_auto/Teaching VLMs to Localize Specific Objects from In-context Examples_2024.md   # ← 优先阅读对象（含图像 + 公式，见 SKILL.md C2）
> mineru_images: /home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/papers/Teaching VLMs to Localize Specific Objects from In-context Examples_2024/hybrid_auto/images
> 引用格式：[[doveh2025iploc]] §小节。

## 书目信息
- authors:
- year:
- venue:
- doi:

## TL;DR（3 行，用你自己的话）

## 与本项目相关的关键声明

## 方法 / 设置

## 结果 / 表格（标注表/图编号；图像见 mineru_images）

## 局限 / 效度威胁

## 可能引用的原句（附 §定位）
- p.X §: "..." — 支持哪条声明？[Cxx]

## 对我们任意声明的反驳证据


## 2026-10-23 数据协议与 checkpoint 复用审计（未提升 Claim）

依据：本地 MinerU 全文 §3.2/§4.1、已校验 PDF；官方仓库固定 commit `27682bc2a059a932c70d9ecdef01265026fdcc30`，下载 README、loader、推理入口及四份 LaSOT 原始清单。证据目录 `.pi/analysis/e015/protocol-research-20261023/`。

- 论文提出同视频单目标、最大间隔采样、1–8shot训练，LaSOT训练测试类别各半。官方仓库公开的是评测代码及固定清单，没有本次树中可见的训练清单或构建器；不能把推断公式冒称作者源码。
- 作者LaSOT 1/2/4/8shot各144条、36类×4视频，四清单Query顺序完全一致。36类这一发布事实与论文约半数的文字不能静默改为35。
- airplane-1实际索引：1shot [1]→2788；2shot [1,1395]→2788；4shot [1,698,1395,2092]→2788；8shot [1,349,697,1045,1393,1741,2089,2437]→2788。2/4shot最近support-query间隔分别最少499/249帧。
- 576条清单记录均符合观测公式support_i=1+i*floor(query_frame/nshot)，但这只是发布数据的核对结果，不是恢复出的训练生成器。正式测试优先逐项使用原清单，不重建它。
- loc_dataset.py读取JSON后原样返回；Loc_Qwen2VL7B.py只给前N图的框，最后图作为Query。其chunks>1分片含`[curr_chunk:-1:chunks]`，适配时应保证144全覆盖，不能继承尾条遗漏。
- 作废E015训练LaSOT内部35类与其自有测试35类互斥，不能说原实现未隔离类别；但与官方36类不同，官方144视频中68条及相同Query帧已经在旧SFT训练，涉及18类。换官方测试JSON不会消除污染，旧SFT/GRPO及依赖它们构造候选的selector不能用于干净官方测试结论。
- 可复用官方Qwen2基础权重、经过验证的4×2代码和原始数据缓存。其他历史adapter必须逐个检查模型家族和训练谱系，不能默认安全。
- 新评测建议固定官方144条原清单；训练协议仍须明确作者缺失项，不能把官方36类的补集冒称论文35类训练集。FOCUS的GOT/TAO数据未获得可复现清单，暂不纳入所谓严格对齐比较。


### 2026-10-23 重启前清单退化框核验

固定作者commit `27682bc2a059a932c70d9ecdef01265026fdcc30` 的LaSOT清单各144条；逐坐标检查发现每个shot均有6个Query GT `[0,0,0,0]`。2shot另有2个、4shot另有9个退化参考框（包含 `[1,1,1,1]`）。不得把训练有效框过滤规则用于官方测试，否则会改变作者清单及分母。新Run原样保留，现有本项目box_iou对退化GT计0；作者Loc_Qwen2VL7B.py调用torchvision.ops.box_iou，二者在双方均零面积的特殊数值行为不能宣称完全相同。主评测仍为全144，不能把138条有效GT子集冒充官方144结果。逐条证据：`.pi/analysis/e015/restart-iploc-r3-20261023/official_degenerate_annotations.json`。这是源文件审计事实，非性能结果、非validated研究Claim。


### 2026-10-23 用户提出50/50后的原文复核与执行纠正

[[focusfor2026]] §7.4明确LaSOT70类，35类训练、35类未见测试；[[doveh2025iploc]] §4.1明确50%类别训练、其余测试。不能将“类别不相交”替代“论文要求的比例与作者类别ID”。公开IPLoc JSON有36类这一文件事实仍保留，但其补集34类不是论文35/35。精确作者35/35 ID当前没有核实，因此不从36类中任意删一类、不默认为FOCUS与IPLoc使用相同清单。GOT在FOCUS中是官方类别互斥split，不据此要求全部数据集都重新50/50划分；TAO没有在已核对小节中给出同样的35/35要求。此前新Run选择34/36的决策已撤回，进程暂挂，等待落实明确数据协议。
