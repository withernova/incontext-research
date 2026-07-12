# 想法（Idea） — In-Context Object Localization

> 活文档。随声明被支持/反驳而迭代。保持具体：写“机制”，而非“目标”。

## Pitch（来自 intake）
测试 idea

## 假设 / 机制
- （将在 DECOMPOSE 阶段拆解为原子声明）

## 什么会证伪它
- 

## 假设清单（待对照代码库 + 文献核查）
- 

## 待解决问题
-

## I-01
- title: 测试

- status: draft
- novelty: unknown
- novelty_note: 
- support_claims: 
- contra_claims: 
- created: 2026-07-09T15:45:08

- motivation: Mechanisms 发现定位靠"容器化"：物体 token 集体界定边界，内部排列对类别定位几乎无关（LLaVA shuffle 后 ↓0.0）；但实例定位必须区分"是哪一辆车"，只看整体语义不够。FOCUS 用一个全层全头的 attention loss 一刀切，既没区分这两种粒度，也监督了错的 token（坐标文本而非物体视觉 token）。

- hypothesis: 检测与跟踪的差异不在如何产生空间容器，而在验证器应当对容器内部组织保持多大不变性。

- key_experiments: |
  1. 在 Qwen2-VL 的 ICOL 设定上重跑 Mechanisms 的 shuffle/padding——确认 containerization 是否成立，且实例定位是否比类别定位对内部 shuffle 更敏感。此步不成，地基才稳。
  2. 干预套件：shuffle / 部件交换 / identity-marker 替换 / 背景替换，验证 Δs_category < Δs_instance。
  3. 把 FOCUS 的 attention loss 正 mask 从 BBOX 坐标文本换成 support 框内物体视觉 token，比 mIoU。
  4. 在 FOCUS 训练前后做 CMA 定位 support-conditioned 关键 head，仅对其做 LoRA，比 mIoU/显存/时长。
  5. oracle-proposal 实验：解耦"提框召回"与"身份验证"，分别归因失败来源。
- updated: 2026-07-12T09:16:40

## I-02
- title: 测试多行idea
- hypothesis: 容器不变性假设
- method: |
  统一打分：s=s_obj+a*s_sem+b*s_struct
  z控制权重
- key_experiments: 
- risks: 
- related_diff: 
- falsification: 如果shuffle对实例定位无影响则假设不成立
- status: draft
- novelty: unknown
- novelty_note: 
- support_claims: 
- contra_claims: 
- sources: 
- created: 2026-07-12T09:00:48




- motivation: |
  新的动机A
  新的动机B
- updated: 2026-07-12T09:13:16

## I-03
- title: 测试编辑idea
- hypothesis: 初始假设
- motivation: |
  初始动机第一行
  初始动机第二行

- key_experiments: 

- related_diff: 
- falsification: 
- status: draft
- novelty: unknown
- novelty_note: 
- support_claims: 
- contra_claims: 
- sources: 
- created: 2026-07-12T09:04:32

- method: |
  新方法
  第二行
- risks: 风险A
- updated: 2026-07-12T09:13:17
