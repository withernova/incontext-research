# 原生成LoRA低IoU候选：50个补GT训练样本

打开 `index.html` 浏览50张独立对照图。`contact_01.jpg` 至 `contact_05.jpg` 为每页10例的总览。

- 绿色REF：Reference目标；红色C1…：生成器原始候选；青色GT：训练数据中追加的GT。
- 下方显示原候选IoU、评分和原评分选中的框。这些诊断数值不进入选择器训练提示词。
- 从729个原最佳候选IoU<0.5、后来补GT的训练源中，按GOT10k 30 / LaSOT 10 / TAO 10分层无放回抽样，seed=20260901；按原最佳IoU升序展示。50例原最佳IoU范围0–0.492703。
- 每例为不同源图像对，不重复使用编号轮换版本。展示原始候选顺序，不是训练随机编号。
- 该分层样本不是总体比例估计；生成困难不等于补GT后选择仍然困难。图像仅为显示缩放，没有修改原始数据。
- 生成器：score0.4/step200。来源Run：`e014-selection-fulltrain-step200-gtaugment-20261018`。完整原候选、GT、源索引、图像路径及展示图SHA见 `manifest.json`。
- 已校验50张图像可解码、本地下载SHA与远端一致；5张总览。无新增模型推理、训练或评测。

远端副本：`/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/visualizations/gt-injected-hard50-20261019/`。
