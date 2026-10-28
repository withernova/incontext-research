# [[focusfor2026]] — (待补)

> source:

## 七问细读（survey-tool 管理）
### ① 解决了什么问题？


### ② 方法具体怎么做？
输入：
输出：

训练阶段：
推理阶段：

核心流程：
输入 → 步骤1 → 步骤2 → 步骤3 → 输出

关键模块：
- 模块1：作用
- 模块2：作用
- 模块3：作用

（基于 [[focusfor2026]] § / Fig 补充）

### ③ 真正的创新点是什么？


### ④ 实验说明了什么？


### ⑤ 依赖哪些前提，边界在哪里？


### ⑥ 作为审稿人，最关键的质疑是什么？


### ⑦ 对当前项目有什么启发？



## 图片标注（survey-tool 管理）

## 2026-10-21 多shot方案核对

优先读取已有同名目录下MinerU正文；原PDF SHA-256 `2bc9af3713f20730b04d862bbb57d461774ad5521e4b7df0d1eaf10f7ab79391`，完整路径已登记kernel/citations.md。在线核对：https://arxiv.org/html/2605.31145v1 。以下为设置事实与建议，未升级项目Claim。

- [[focusfor2026]] §7.1/Table7：Qwen2-VL-7B-Instruct、4-shot训练，同一模型评测1/2/4-shot、DeepSpeed；4-bit、LoRA r8/alpha16/dropout0，SFT lr2e-4、梯度累积16、warmup.03、clip.3、BF16；GRPO G4、max_prompt_length8192、lr1e-5、FlashAttention-2。不能由累积16推导未核实的global batch。
- [[focusfor2026]] §7：均匀时序采样、最后帧Query；support末端措辞需核对具体实现。项目`tools/prepare_focus_datasets.py::_focus_indices`实际为首帧至倒数第二个标注帧均匀取support、最后帧Query，1-shot仅首帧；这是项目实现事实，不冒称作者代码。
- [[focusfor2026]] §5/Table3：完整FOCUS包含SFT＋attention loss，再GRPO，普通多图SFT不等于完整复现。§9报告SFT57.2GB、加attention loss64.1GB，所读段落不足以推出本项目每卡峰值。
- 当前`qwen3vl_lora_ddp.py`显式加载Qwen3VLForConditionalGeneration、每卡完整副本，已有NF4/checkpointing/use_cache=False；共享runner已有assistant_only_logits。Qwen2适配需核对模型类、processor、视觉grid/坐标和attention路径。
- 待执行建议：4-shot训练→同ckpt评测1/2/4；固定Query/划分，增加最近support的1-shot对照；固定原proposal选择诊断与端到端重新生成proposal分开统计。优先相同目标下的分片/重计算/offload和attention统计节省，再考虑显式记录的图像预算调整。不承诺任意nshot，不把79例可视化当作时距因果证明。

本轮没有GPU检查、模型执行、训练或源码修改。


## 2026-10-23 严格协议复核（覆盖此前实现等价暗示）
[[focusfor2026]] §7描述support首尾覆盖全视频且最后帧为Query，但没有提供精确整数索引，也不能推出“Query前一帧必须作为support”。论文§7.4给出35/35类设定而未列类别ID。本次检索论文标题+GitHub、作者+GitHub、arXiv ID+code/dataset，未定位到可验证的FOCUS官方构建源码或清单；这是当前检索边界，不是不存在的证明。不得据此发明帧间隔、类别划分或将IPLoc清单等同FOCUS。IPLoc官方发布数据的具体间隔和36类/144条事实见同次doveh2025iploc审计。当前旧E015的1/2shot性能及FOCUS比较已作废。


### 2026-10-23 用户提出50/50后的原文复核与执行纠正

[[focusfor2026]] §7.4明确LaSOT70类，35类训练、35类未见测试；[[doveh2025iploc]] §4.1明确50%类别训练、其余测试。不能将“类别不相交”替代“论文要求的比例与作者类别ID”。公开IPLoc JSON有36类这一文件事实仍保留，但其补集34类不是论文35/35。精确作者35/35 ID当前没有核实，因此不从36类中任意删一类、不默认为FOCUS与IPLoc使用相同清单。GOT在FOCUS中是官方类别互斥split，不据此要求全部数据集都重新50/50划分；TAO没有在已核对小节中给出同样的35/35要求。此前新Run选择34/36的决策已撤回，进程暂挂，等待落实明确数据协议。
