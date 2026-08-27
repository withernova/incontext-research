# E010-R-002-identity-spatial-controls-and-head-necessity · IPLoc-ID身份与位置排除检查及注意力头必要性验证

- workflow: v2 / awaiting_review / 等待审核
- review_status: pending_review
- group_id: 未分组
- execution_dispatch:  / 

## 1. 研究设计
### 研究问题
Run 1固定的注意力头是否真的利用参考物体身份并跟随真实物体位置，而不是只看显眼同类物体、复制另一张图的坐标或停在固定位置；关闭这些头后，IPLoc-ID是否比关闭随机头下降更多？
### 本轮目的
在同一批未参与挑头的样本上，依次更换错误参考身份、单独变换参考图或待查图，并在内部条件通过后关闭固定注意力头。目标是排除身份无关和位置规律等简单解释，并区分“热图能显示物体”与“模型完成任务需要这些头”。
### 假设或比较预期
若Run 1固定的头参与IPLoc-ID个体定位，它们应对正确与错误参考身份产生不同响应，并随被单独变换图中的真实物体移动；关闭这些头造成的任务下降应大于关闭相同数量、相近模型层的随机头。
### 数据与主要变量
使用Run 1未参与挑头的IPLoc-ID样本。身份错配要求同类别不同物体身份；空间变换分别作用于参考图或待查图并同步对应真实框。优先选择存在有效错误身份配对、变换后物体仍完整可见的样本。样本清单在运行前固定。

比较一：正确参考身份与同类别错误参考身份，待查图不变。比较二：只变换参考图、只变换待查图与原图。比较三：关闭固定头、关闭相同数量且来自相近模型层的随机头、完全不关闭。相同输入重复运行作为稳定性对照。

## 2. 指标设计
身份检查：模型答案变化、参考图和待查图真实物体区域注意力变化。空间检查：还原方向后的热图接近程度、热区中心和最强点移动距离，并直接比较跟随真实物体、复制另一张图坐标、固定位置三种解释。关闭头检查：模型答对比例与预测框重合程度相对原始运行下降多少，并与随机头比较。
## 3. 代码架构
复用Run 1的样本读取、自然回答、双图位置、热图和固定名单文件；复用attention/rewrite.py在softmax之后、与value相乘之前修改指定头的成熟控制器。最小新增：pipelines/head_reliability_controls.py实现错误参考身份、参考图单独变换、待查图单独变换和有条件关闭固定头；configs/e010_r002.json声明Run 1名单输入、变换和停止条件；tools/run_e010_r002.sh调用公共入口。扩展tests/test_attention_rewrite.py验证关闭模式、未选头不变和随机对照数量一致；新增纯图像坐标变换测试。不得修改或覆盖E-008历史流程。
- 公共包：`mechanism/iplocid/iplocid`
- 入口：`iplocid.pipelines.head_reliability_controls:main`
- 配置：`mechanism/iplocid/configs/e010_r002.json`
- Shell launcher：`mechanism/iplocid/tools/run_e010_r002.sh`
- 复用模块：iplocid/attention/rewrite.py, iplocid/attention/spans.py, iplocid/attention/metrics.py
- 新增模块：iplocid/pipelines/head_reliability_controls.py
- 测试：tests/test_e010_controls.py, tests/test_attention_rewrite.py

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `bash tools/run_e010_r002.sh --config configs/e010_r002.json`
- commit: `9a53a24d4e345b4c75a8dee4f6769f93c3720377`
- workspace: 02
- tmux: incontext-E-010-E010-R-002-identity-spatial-controls-and-head-necessity
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-002-identity-spatial-controls-and-head-necessity/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/E010-R-002-identity-spatial-controls-and-head-necessity/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
错误参考身份与图像变换可能使输入偏离模型训练分布；结果必须与未改变输入的重复运行比较。关闭注意力头可能同时影响一般语言或图像处理能力，因此需要相近层随机头和正常输出能力对照。

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "Run 1即使找到稳定且能定位物体的头，也仍可能只是看向显眼物体、复制坐标或提供不被模型使用的可读信号。只有身份错配、单图空间变换和公平的关闭注意力头对照，才能限制这些解释。",
  "evidence_basis": "LocalizationHeads使用原始注意力生成物体区域，但原始注意力本身不证明个体识别或模型依赖。项目已有E-005结果也显示参考图、待查图和不同输出时刻可能对应不同注意力头，因此必须使用Run 1固定名单并分别检查。",
  "implementation_summary": "已完成只读代码规划。现有attention/rewrite.py已在注意力概率与图像信息汇合前提供带审计的修改入口，可安全扩展明确的关闭模式；Run 2只需新增控制流程、配置、薄启动脚本和聚焦测试，并读取Run 1固定名单。当前项目根AGENTS.md禁止代码修改和推理，因此尚未实施。",
  "implementation_details": "内部步骤共三项但只作为一个Run：一，正确参考身份与同类别错误身份成对比较；二，参考图单独翻转或受控移动、待查图单独翻转或受控移动，并还原坐标比较热图；三，只有前两项通过时才关闭Run 1固定头。关闭方式必须在实现审核时明确具体张量位置和范围，不得临时改为其他干预。",
  "model_config": "与Run 1完全相同的已训练IPLoc-ID模型、附加训练权重、真实问题格式、图像处理和答案生成方式。固定注意力头名单由Run 1产物提供。具体关闭位置、随机对照抽样和图像变换参数在实现检查时写入。",
  "metric_definition": "身份响应以同一待查图的正确/错误参考成对差值报告。空间跟随以变换后的热图还原到原方向后与原热图的接近程度，以及热区中心和最强点相对真实物体移动的误差报告。必要性以关闭固定头后的任务下降减去关闭随机头后的任务下降报告。",
  "integrity_gates": "第一，只能使用Run 1自动导出的固定名单，禁止重新挑头。第二，Run 1必须同时证明名单换数据后较稳定且新图片上优于随机头，否则本Run取消。第三，身份和空间条件成对使用同一样本并固定变换参数。第四，若热区主要复制坐标或停在固定位置，停止关闭头步骤。第五，所有未执行步骤必须记录被哪条停止条件阻止，不能记为零结果。",
  "expected_outcome": "区分四种结论：固定头支持个体身份和真实物体跟随；只支持普通物体定位；主要利用坐标或固定位置；或虽能显示物体但关闭后模型并不更依赖它们。",
  "acceptance_criteria": "Run 1依赖和固定名单哈希可核对；正确/错误参考身份成对结果完整；参考图单独变换和待查图单独变换结果完整；三种位置解释直接比较；若内部条件通过则固定头、随机头和不关闭三组任务结果齐全，若未通过则停止原因明确；正常结束且产物可追溯。",
  "claim_boundary": "只回答Run 1固定头是否响应参考身份、是否跟随真实物体位置，以及模型是否比随机对照更依赖这些头。不证明完整身份信息只由这些头承载，不评价RefCOCO论文数值，也不外推到其他模型。",
  "audit_paths": "/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iplocid/iplocid/attention/rewrite.py; /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iplocid/iplocid/pipelines/natural_iou_stress_trial_pipeline.py; /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iplocid/tests/test_attention_rewrite.py; /defaultShare/archive/liuwenchu/projects/IPLoc/AGENTS.md"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
