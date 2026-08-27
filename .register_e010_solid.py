import json, subprocess
from pathlib import Path
CTL="/home/zhengyuesong/Tools/survey-tool/surveyctl.py"
PROJECT=str(Path.cwd())

def create(run_id, variant, **fields):
    cmd=["python3",CTL,"--project",PROJECT,"run","create","E-010","--id",run_id,"--variant",variant]
    for key,value in fields.items():
        if value is not None:
            cmd += ["--"+key.replace("_","-"), str(value)]
    print(subprocess.run(cmd,check=True,text=True,capture_output=True).stdout)

original_prompt="""用户原始定义（2026-08-26，逐字保留）：首先我们的实验都是去测量Query bbox token对query/reference image token的注意力，不存在找reference bbox对reference image token的。然后通过query bbox token对两个不同image的注意力经过算法可以得到两批head，一个是query head一个是reference head，指的是模型在生成query bbox token时，看了query/reference图像的哪些区域。所以我指的query head和reference head都是query bbox token对前面的图像的注意力。我现在想确定的是，这两个head是否显著且稳定，而让query head在reference image token的注意力是否有偏差？"""

create(
 "E010-R-003-natural-query-bbox-dual-span-head-discovery-stability",
 "自然Query-bbox双图Query/Reference head无GT发现与稳定性复核",
 run_type="analysis",
 purpose="以模型自然生成的Query bbox token prediction rows为唯一query rows，分别读取其到Query image tokens和Reference image tokens的逐头注意力，使用同一套LocalizationHeads式无GT算法独立发现query heads与reference heads，并验证二者在20图重复抽样、较大子集和sequence-held-out样本上的显著性、稳定性与空间有效性。明确禁止使用Reference bbox token rows定义任何head。",
 necessity="E-005/E-010历史记录混用了Reference GT bbox rows→Reference、自然Query bbox rows→Reference、teacher-forced Query bbox rows及GT-conditioned visual rows，导致‘reference head’术语与用户目标不一致。必须以唯一rows定义重建两批head，才能判断固定少数head是否真实存在并为后续跨span偏差检验提供冻结名单。",
 evidence_basis="LocalizationHeads论文以image-attention sum、connected-component spatial entropy和跨样本selection frequency无GT发现固定heads；GT仅用于发现后的空间验证。E010旧R-001已保存140条自然bbox replay的Q→Q/Q→R全头张量，但其entropy采用residual-mass而非论文二值连通域面积，且56图leave-one-fold不能直接回答每次20图是否换head。本Run按用户新定义与论文公式重做。",
 implementation_summary="计划复用旧R-001的140条自然回答、精确bbox-token对齐与全头attention artifacts，优先纯离线分析；先核验artifact来自相同自然Query bbox rows及双图span。新增严格论文版二值连通域面积entropy、确定性20图重采样、双角色独立排名和冻结held-out验证，不加载模型，除非artifact契约核验失败且另行审核。",
 implementation_details="唯一attention row集合：自然生成Query bbox从左方括号到首个右方括号的全部token positions之p−1 rows，逐head在这些rows上求预注册平均；同一rows分别截取Query image span得到Qbbox→Q map、截取Reference image span得到Qbbox→R map。query heads仅由Qbbox→Q discovery maps选出；reference heads仅由Qbbox→R discovery maps选出。发现阶段不读取GT。对每个角色独立执行：排除层0/1；按跨discovery样本平均image-attention sum及论文最大曲率阈值筛选；map按自身均值二值化；8邻域连通域；按component token count计算entropy；每图低熵Top10；按selection frequency固定Top3/Top5。不得用GT、自然IoU或correct/error重选head。",
 data_definition="沿用旧R-001的140条IPLoc-ID positive自然回答及对应精确replay attention，按LaSOT sequence_cluster隔离。固定seed先划70 discovery/70 evaluation；evaluation在所有head名单、阈值和重采样规则冻结前不可用于选择。训练暴露未知，evaluation只能称selection-held-out sequences。",
 data_scale="主发现70条、最终评价70条。稳定性在70条discovery内部执行100次无放回n=20重采样，并补n=40、n=56各100次形成样本量曲线；不得从evaluation补足。每个角色、每个样本量都完整保存Top3/Top5名单和全排名。",
 model_config="冻结Qwen3-VL-8B-Instruct + IPLoc-ID LoRA、max_side=640及旧R-001自然回答/replay artifacts；不重新自然生成、不teacher-force GT bbox。必须记录模型、LoRA、manifest、自然输出和artifact manifest哈希。",
 variables_controls="角色A query heads=Qbbox→Query；角色B reference heads=Qbbox→Reference。相同rows、相同样本、相同selection参数，唯一变化是image key span。控制包括同层随机Top3/5、image-attention-sum-only、entropy-only、all-head mean、per-image oracle；oracle只作上限不得进入固定名单。",
 metric_definition="稳定性：100次n=20重采样的head inclusion probability、Top3/Top5相对70图基准与两两Jaccard分布、完整rank Spearman、selection-frequency置信区间；显著性：相对同层随机的selection-frequency集中度、held-out pointing、GT area-normalized enrichment、target mass、S50 fractional-token IoU和至少一头/多数头覆盖；角色关系：query/reference Top-k overlap和rank correlation。GT指标仅在名单冻结后计算。",
 integrity_gates="G1 所有map必须由同一自然Query bbox p−1 rows生成，禁止Reference bbox rows、GT Query bbox teacher forcing或GT-conditioned rows；G2 双image spans与token grids逐样本精确核验，row/span契约哈希保存；G3 discovery/evaluation sequence零重叠；G4严格使用二值连通域token-count entropy并以单元测试对手算例验证；G5 n=20抽样seed和100个subset IDs预先物化；G6 GT、correct/error、自然IoU不得进入发现；G7负结果不得通过改阈值、改rows或改head数挽救。",
 expected_outcome="分别给出query heads与reference heads是否存在少数显著高频核心、每次20图会不会换名单、随样本量增加是否收敛，以及冻结名单能否在selection-held-out图上定位各自目标。允许出现query heads稳定有效而reference heads稳定但无效，或reference heads完全不稳定等负面结果。",
 acceptance_criteria="140条rows/spans契约全通过且零静默失败；70/70 sequence隔离；query/reference两套严格论文式发现结果齐全；n=20/40/56各100次稳定性结果及inclusion/Jaccard/rank表齐全；冻结Top3/5对同层随机与held-out GT指标齐全；至少保存12张query-head Q→Q和12张reference-head Q→R逐头热图；完整结果、配置、subset manifest与哈希可追溯。",
 dependencies="旧E010-R-001仅作为自然回答与全头artifact数据源；不继承其G→R定义、residual-mass entropy排名或科学结论。",
 limitations="自然bbox token rows可能混合坐标数字、标点和格式生成；对rows求平均可能掩盖token阶段差异，本Run先固定该定义并把逐token结果作为附录，不事后挑token。训练暴露未知；attention显著性不证明因果或身份选择性。",
 claim_boundary="只回答自然生成Query bbox rows下，Qbbox→Query与Qbbox→Reference两批固定heads的无GT发现显著性、20图/更大样本稳定性和selection-held-out空间有效性；不使用或支持Reference bbox→Reference head概念，不证明这些head为任务必要电路。",
 audit_paths="旧R-001 records.json/artifacts/analysis/summary.json；mechanism/iplocid/iplocid/attention/selection.py；新增严格entropy与resampling模块；"+original_prompt,
 status="planned",workspace_id="02",seed="20260826",
 research_question="仅使用模型自然生成Query bbox token的p−1 rows时，分别对Query和Reference image spans运行严格LocalizationHeads式无GT算法，能否找到显著且在独立20图重采样及selection-held-out序列上稳定有效的query heads与reference heads？",
 hypothesis="query heads将呈现高inclusion probability、较高Top-k一致性和held-out Query GT定位；reference heads若真实存在，也应在n=20重复抽样中收敛且在held-out Reference GT上优于同层随机，否则应判为不稳定或稳定偏置头。",
 metric_plan="主指标为n=20×100 inclusion/Jaccard/rank稳定性与held-out固定Top3/5相对同层随机的pointing/enrichment/S50 fIoU；n=40/56为样本量曲线；query/reference使用完全相同参数且独立排名。",
 architecture_plan="新增只读artifact审计与严格论文entropy/resampling分析入口，输出双角色selection manifests、subset manifests、metrics和逐头可视化；不得调用Reference bbox rows或旧G→R分支。"
)

create(
 "E010-R-004-frozen-query-head-reference-span-bias-audit",
 "冻结Query heads投向Reference图像的空间偏差与坐标复制审计",
 run_type="analysis",
 purpose="冻结R-003仅由Qbbox→Query发现的query heads，在完全相同的自然Query bbox prediction rows上把key span切换到Reference image，测量其注意力是否相对R-003 reference heads表现出系统目标错位、Query坐标复制、固定位置/边界偏置或仅仅较弱的Reference目标信号。",
 necessity="用户特别关心‘让query head在reference image token的注意力是否有偏差’。旧实验只报告部分Q→R target mass或把G→R作为参照，无法区分query-head跨span后的四种解释：仍跟随Reference目标、复制Query归一化坐标、固定/边界位置偏置、或无结构噪声。必须冻结R-003两批名单后做同rows跨span配对比较。",
 evidence_basis="R-003将提供严格定义的query heads和reference heads及其selection-held-out集合。旧E010可视化提示旧Q→R自发现heads常聚焦Reference图边缘，但旧entropy实现和head定义不足以形成solid结论；本Run预注册位置候选与统计，避免看到热图后再解释。",
 implementation_summary="计划纯离线读取R-003冻结名单及同一自然bbox全头artifacts，不重选任何head。对每个held-out样本同时形成四个配对map：query heads→Query、query heads→Reference、reference heads→Reference、reference heads→Query；主比较聚焦query heads→Reference，其他三项作为定位上界、角色基线和交换对照。",
 implementation_details="所有map使用与R-003完全相同的自然Query bbox p−1 rows。query heads与reference heads分别读取R-003不可变selection manifest及SHA-256。每个head先保留raw map，再形成预注册Top3/Top5等权均值；禁止按held-out GT重新加权。将Query GT bbox按归一化坐标投影到Reference grid，形成四个预注册候选区域：Reference GT、projected Query GT、固定中心区域、边界带。另保留无候选的COM/argmax分布和热图。",
 data_definition="只使用R-003的70条selection-held-out evaluation sequences；若R-003完整性或稳定性gate失败，本Run记录dependency stop而不把空结果记为零。每条同时需要Reference/Query GT、双图尺寸与token grid，GT仅用于本Run冻结后的偏差评价。",
 data_scale="主分析全部70条held-out；按自然bbox IoU预注册分层correct>=0.5、error<0.1、middle，其分层只用于解释，不改变主样本或head名单。至少1000次sequence bootstrap计算配对CI。",
 model_config="完全复用R-003自然回答、rows和attention artifacts，不重新加载模型；query/reference head名单、Top3/5和所有selection参数由R-003哈希锁定。",
 variables_controls="四格：Qheads→Q、Qheads→R（主项）、Rheads→R、Rheads→Q。Qheads→R内比较Reference GT vs projected-Query区域 vs center vs boundary；控制为同层随机heads、all-head mean及图像面积/GT coverage匹配。Reference GT和projected Query重叠高的歧义样本不进入候选胜负主分析，但仍保留raw指标。",
 metric_definition="主偏差分数：Qheads→R的mass/enrichment(Reference GT)减去mass/enrichment(projected Query region)，并同时报告二者各自绝对值；候选判别为argmax/COM到Reference GT、projected Query、center和boundary的归一化距离；边界偏置报告top/bottom/left/right带mass及COM分布。配对比较Qheads→R vs Rheads→R，及Qheads→R vs同层随机。空间map补充JSD、S50 fIoU和token-grid coverage。所有效应给sequence bootstrap CI，不只报命中率。",
 integrity_gates="G1 R-003 selection manifest/hash和70 held-out IDs必须匹配；G2禁止任何重新挑头、按GT加权或剔除不利样本；G3所有四格使用相同自然Query bbox rows；G4 projected Query区域必须按图像归一化坐标投影并记录Reference token-grid occupancy，不直接复制像素坐标；G5 Reference GT与projected区域IoU超过预注册阈值0.3者标记ambiguous并从候选胜负主分析排除但不删除；G6边界带固定为merged grid外圈20%且运行前冻结；G7逐样本图使用共同色标/同时给raw mass，避免独立min-max造成视觉误判。",
 expected_outcome="区分：A query heads跨到Reference仍优先Reference GT；B显著偏向projected Query位置，支持坐标复制；C显著偏向固定边界/中心，支持位置偏置；D无候选优势且接近随机，支持跨span失效。reference heads→Reference作为独立角色基线，而不是G→R。",
 acceptance_criteria="R-003依赖和hash核对；70条四格map和逐样本raw metrics齐全；Reference/projected/center/boundary四候选及ambiguity计数齐全；Top3/5、同层随机、all-head配对CI齐全；correct/error只作预注册分层；至少12张统一色标四格总览和每个query head投向Reference的逐头图；结论明确落入A/B/C/D或不确定。",
 dependencies="E010-R-003-natural-query-bbox-dual-span-head-discovery-stability完成且输出冻结query/reference Top3/5及held-out manifest；若R-003 query heads不稳定，仍可做描述性跨span分析但不得称固定query-head偏差；若artifact契约失败则停止。",
 limitations="Attention位置偏差不等于信息内容或因果作用；projected Query坐标与Reference目标可能自然重叠；两图物体尺度和背景不同会影响map；自然bbox rows平均可能混合token阶段。",
 claim_boundary="只判断R-003冻结query heads在Reference image tokens上的空间分布相对Reference目标、Query投影坐标和固定位置是否有系统偏差，并与R-003 reference heads/随机对照比较；不引入Reference bbox rows，不证明身份匹配或因果必要性。",
 audit_paths="R-003 selection manifest/held-out manifest；旧E010全头artifacts；新增bias candidate occupancy与统一色标可视化；"+original_prompt,
 status="planned",workspace_id="02",seed="20260826",
 research_question="当仅由Qbbox→Query发现的冻结query heads在同一自然Query bbox rows下改看Reference image tokens时，其注意力是否系统偏离Reference目标，并更接近Query归一化坐标投影、固定边界/中心或随机分布？",
 hypothesis="若query heads是Query侧坐标定位专用头，其Qheads→Reference map可能更偏向projected Query位置或固定位置而非Reference GT；若它们是跨图共享目标头，则应接近Rheads→Reference并优先Reference GT。",
 metric_plan="主指标为held-out配对的Reference-GT minus projected-Query mass/enrichment偏差及bootstrap CI；辅以四候选距离、边界mass、Qheads→R与Rheads→R/同层随机差、统一色标四格可视化。",
 architecture_plan="新增纯离线frozen-head cross-span bias分析入口，读取R-003 hashes和旧全头artifacts，生成四格raw maps、候选occupancy、paired metrics与可视化；不得重跑选择算法。"
)
