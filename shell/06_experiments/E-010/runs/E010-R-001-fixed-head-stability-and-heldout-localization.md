# E010-R-001-fixed-head-stability-and-heldout-localization · IPLoc-ID固定注意力头稳定性与新样本定位检查

- workflow: v2 / ready_to_run / 等待执行授权
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-410f5211cf4748d45bcdf89f / queued

## 1. 研究设计
### 研究问题
在已经训练好的IPLoc-ID模型上，更换用于挑选注意力头的图片后，能否反复找到相近的一组头；这组头固定后，能否在未参与挑选的参考图和待查图上找到真实物体？
### 本轮目的
一次提取IPLoc-ID自然回答及对应注意力，依次检查位置读取、名单稳定性、新样本定位、多数图片覆盖、答对与答错差异，以及参考图和待查图是否需要不同的头。目标是排除名单由少数图片偶然决定或只在挑头数据上有效。
### 假设或比较预期
如果IPLoc-ID上确实存在可靠的固定少数注意力头，那么按视频序列或物体身份更换挑头数据后，重复出现的头应明显多于随机挑选；固定名单在新样本上也应比随机头更偏向真实物体，并覆盖多数图片。
### 数据与主要变量
使用本地工具绑定工作区中的IPLoc-ID真实双图任务数据。按视频序列或物体身份分组，同一组不得同时进入挑头数据和检查数据。必须记录每个样本是否可能在模型训练时出现；训练内和训练外样本若都存在则分开报告。

主要比较：论文式固定3头和5头；随机选择相同数量且来自相近模型层的头；只挑经常看图的头；只挑热图集中的头；所有头平均；每张图片临时挑最有利的头。参考图和待查图分开，模型答对和答错分开。

## 2. 指标设计
名单稳定性：不同数据分组中完全相同头的数量及完整排名接近程度，并与随机挑头比较。位置质量：热图最强点是否落在真实框、真实框注意力相对其面积是否高于1。物体框质量：预测框与真实框重合比例及超过0.3、0.5、0.7的图片比例。覆盖：逐图命中头数、至少一头和多数头命中比例、最差分组。
## 3. 代码架构
直接复用mechanism/iplocid公共包：attention/spans.py负责双图位置，attention/metrics.py负责物体区域分数，inference/generation.py负责自然回答，inference/replay.py负责答案位置对齐，models/qwen.py负责Qwen3-VL和附加权重加载。最小新增：attention/selection.py实现论文式挑头和随机对照；pipelines/fixed_head_validation.py串联一次模型加载、自然回答、注意力保存及离线分组分析；configs/e010_r001.json保存样本划分和固定参数；tools/run_e010_r001.sh仅调用公共入口。测试新增tests/test_attention_selection.py，并扩展位置测试覆盖双图和答案坐标位置。不得复制历史E-005脚本。
- 公共包：`mechanism/iplocid/iplocid`
- 入口：`iplocid.pipelines.fixed_head_validation:main`
- 配置：`mechanism/iplocid/configs/e010_r001.json`
- Shell launcher：`mechanism/iplocid/tools/run_e010_r001.sh`
- 复用模块：iplocid/attention/spans.py, iplocid/attention/metrics.py, iplocid/inference/replay.py, iplocid/models/qwen.py
- 新增模块：iplocid/attention/selection.py, iplocid/pipelines/fixed_head_validation.py
- 测试：tests/test_attention_selection.py, tests/test_attention_spans.py, tests/test_attention_metrics.py

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `bash tools/run_e010_r001.sh --config configs/e010_r001.json`
- commit: `9a53a24d4e345b4c75a8dee4f6769f93c3720377`
- workspace: 02
- tmux: incontext-E-010-E010-R-001-fixed-head-stability-and-heldout-localization
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-001-fixed-head-stability-and-heldout-localization/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-001-fixed-head-stability-and-heldout-localization/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
若样本曾用于模型训练，只能检验挑头与检查之间的复现，不能声称模型对未见身份泛化。注意力热图只能说明可读出物体位置，不能证明模型必须依赖这些头。

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "已有E-005结果显示，出现次数最多的5个头固定后在另外40个样本上的物体框重合很弱；但旧结果的数据划分、图像尺寸和后续调整较多。必须用提前固定的分组和判断规则做一次完整复核，才能决定是否值得进行身份错配、空间变换和关闭注意力头。",
  "evidence_basis": "论文方法先在每张图片中找注意力集中的候选头，再统计跨图片出现次数并固定少数头。项目已有E-005初步负面证据：固定头在未参与挑选样本上的平均框重合约0.034，达到0.5重合的比例为0；参考图和待查图的高频头也大多不同。",
  "implementation_summary": "已完成只读代码规划。现有公共包可复用模型加载、自然回答、双图位置、答案重放、空间评分和热图基础；只需新增通用挑头模块、一条验证流程、声明式配置和薄启动脚本。当前项目根AGENTS.md仍只授权E-008离线渲染并禁止代码修改和推理，因此尚未实施。",
  "implementation_details": "内部步骤共六项但只作为一个Run：一，位置对应和重复运行检查；二，多组挑头数据的名单比较；三，固定3头和5头的新样本定位；四，逐张覆盖及最差分组；五，自然回答正确与错误样本对比；六，参考图用头和待查图用头分别挑选并交换检查。模型只加载一次，注意力只提取一次；后续比较离线完成。",
  "model_config": "工作区当前已训练IPLoc-ID模型及其附加训练权重；真实问题格式和自然逐字生成；逐头注意力输出。模型路径、权重版本、图像尺寸、实际读取的文字符号和图像小块布局在实现检查时写入，不从相邻实验猜测。",
  "metric_definition": "框重合比例=预测框与真实框的交集面积/两框并集面积。物体区域偏好=真实框内注意力比例/真实框面积比例，大于1表示比均匀看图更偏向物体。名单稳定性同时报告固定3头、固定5头的完全重合数量和全头排名接近程度。所有指标按参考图/待查图、答对/答错、正/负样本分别报告。",
  "integrity_gates": "第一，参考图、待查图、文字位置、图像小块和物体框全部正确对应，重复运行一致；失败立即停止。第二，样本按视频序列或物体身份隔离。第三，查看检查数据前固定样本、随机数、头数、选择方法和画框方法。第四，自然回答与读取注意力一一对应，答错和无法解析样本显式计数。第五，名单不稳定或新样本不优于随机时保留负结果，不修改规则挽救。",
  "expected_outcome": "得到一个明确结论：支持一组稳定且能在新图片上找物体的固定头；或不支持固定头，只能认为不同图片/不同用途需要不同头。无论正负均交付完整逐样本结果。",
  "acceptance_criteria": "位置对应检查全部通过；多次更换挑头数据后的名单稳定性与相近层随机头对照完整；固定头在未参与挑选样本上的逐图定位、覆盖、答对/答错和参考图/待查图结果齐全；所有失败和无法解析样本有明确计数；正常结束且产物可追溯。",
  "claim_boundary": "只回答LocalizationHeads式固定少数头在IPLoc-ID上的稳定性和定位有效性；不复现或否定RefCOCO论文数值，不证明个体识别作用，也不证明这些头是模型完成任务的必要原因。",
  "audit_paths": "/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iplocid/iplocid/attention; /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iplocid/iplocid/inference; /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iplocid/iplocid/pipelines/role_audit_pipeline.py; /defaultShare/archive/liuwenchu/projects/IPLoc/AGENTS.md"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
