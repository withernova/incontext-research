# E011-R-001-query-attention-gt-alignment-smoke · 1

- workflow: v2 / code_planning / 代码方案
- review_status: draft
- group_id: 未分组
- execution_dispatch:  / 

## 1. 研究设计
### 研究问题
当把预先指定的 query attention head 在边界框生成行、对 query 图像视觉 token 的注意力概率改写为 GT 框分布时，IPLoc 生成的边界框是否相对于原始基线向 GT 移动？
### 本轮目的
在同一批冻结样本上比较原始基线、已安装但不改变数值的 no-op hook、以及 GT 对齐干预，排除单纯增加 hook 或重放误差造成的预测变化。该 Run 只验证预测对指定注意力分布改写的敏感性。
### 假设或比较预期
若该 query head 的注意力分布在该生成行对边界框决策具有直接影响，则 GT 对齐干预相对原始和 no-op 对照会使预测框 IoU 或中心点距离朝 GT 方向变化；无变化或 no-op 同样变化均不支持该解释。
### 数据与主要变量
待确认：从一个已存在的 E-011 manifest 中，在运行前固定小规模样本及其顺序；不写入或修改数据集。

三条件：原始 baseline；no-op hook（执行同一路径但保持原 attention 概率）；GT 对齐 hook。固定同一模型、LoRA、输入、生成设置、样本顺序和随机种子。待确认：目标 layer/head、bbox 输出的生成行、GT→token-grid 重叠面积归一化规则。

## 2. 指标设计
使用现有基线 IoU 与有效框率，并增加预测框中心距离及 attention-map 对齐审计；只比较同一冻结样本的三条件配对差异。
## 3. 代码架构
在 Qwen2-VL 实际 attention 概率计算后、attention×V 之前插入可开关 hook；新增实现须被 IPLoc 现有评估入口显式调用，不复制基线评估逻辑。
- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: ``
- commit: ``
- workspace: 02
- tmux: incontext-E-011-E011-R-001-query-attention-gt-alignment-smoke
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-011/E011-R-001-query-attention-gt-alignment-smoke/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-011/E011-R-001-query-attention-gt-alignment-smoke/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
GT 强制对齐是干预，不反映模型自然注意力；单个预指定 head/行的结果不可推广为整个模型机制，也不构成因果电路的充分证明。

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "当前 IPLoc 评估脚本直接调用 `model.generate`，未暴露 attention hook；因此尚无法判断 query-head attention map 与预测框之间是否存在可操作的关联。",
  "evidence_basis": "已验证 `mechanism/IPLoc/run_e011_iploc_baseline.sh` 调用 `Loc_Qwen2VL7B.py`；后者加载 Qwen2-VL+LoRA 后通过 `model.generate` 生成并以 IoU 评估边界框。",
  "model_config": "IPLoc 当前 Qwen2-VL 基线与其现有 LoRA；模型、adapter revision、图像预处理和生成参数须在代码实现后记录。",
  "metric_definition": "逐样本保存生成文本、有效框状态、IoU、预测框中心至 GT 中心的距离；另审计干预前后目标 head 对 GT token 的 attention mass、token-grid、selected-token-counts 和行/span 对齐。主比较为 GT 对齐条件相对原始与 no-op 条件的配对变化。",
  "integrity_gates": "1) 原始和 no-op 在逐 token 输出与 logits/attention 审计允许误差内一致；2) GT token-grid 非空且 selected-token-counts 已记录；3) hook 仅作用于预注册 layer/head、生成行、query image token span；4) 三条件均保存完整逐样本记录，禁止以零有效框得出结论；5) 在结果前固定样本、head、行和归一化规则。",
  "expected_outcome": "若干预确实将目标 head 的 query-image attention mass 移至 GT 且预测框同步改善，可证明该预测对这一受控改写敏感；若无同步变化，则在本实现和条件下不支持该 head 的直接充分作用。",
  "acceptance_criteria": "可复现运行三条件；no-op 等价 gate 通过；GT 对齐 attention 审计通过；每个样本均有可解析状态和完整比较记录；仅在上述 gate 通过后报告配对预测变化。",
  "claim_boundary": "本 Run 只回答受控 attention 概率改写是否伴随预测变化；不证明 IPLoc 自然预测时使用 GT、不证明 identity 理解，也不修改任何 Claim verdict。",
  "audit_paths": "远端待实现：`mechanism/IPLoc/` 的最小 hook 模块、基线入口及 `experiments/E-011/E011-R-001-query-attention-gt-alignment-smoke/` 下的配置、逐样本审计和结果。"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
