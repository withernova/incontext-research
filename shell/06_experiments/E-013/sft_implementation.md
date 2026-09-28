# E-013：FOCUS 置信度 SFT 实现记录

日期：2026-09-20。仅实现代码与聚焦检查，未启动 SFT/GRPO，未修改治理状态。
本记录补充之前的讨论草案；实现采用本轮确定的 FOCUS 单框协议，而不是早期
草案中的类别条件 JSON、多实例或多候选协议。

## 实际代码位置

SSH 主机 NKU-LWC：
`/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy`

- prompt：`iploc_szy/prompting/messages.py` 中 `focus_confidence_messages()`。
- 数值语法与严格解析：`iploc_szy/prompting/confidence.py`。
- 数据与 mask：`iploc_szy/datasets/iploc.py`、`collator.py`。
- 格式辅助损失：`iploc_szy/attention_distillation/confidence.py`。
- 配置：`configs/sft/e013_qwen3vl8b_focus_confidence.py`。
- 启动：`tools/run/train/train_focus_confidence_sft.sh`。
- 使用说明：`docs/focus_confidence_sft.md`。

保留 FOCUS 的单 user 消息、交错图像/BBOX、无类别输入，最终输出：

```text
<answer>[120,180,460,720]</answer><score>0.87</score>
```

新增协议名 `focus_confidence`，旧 `focus` 不变。格式约定数值为 0.00–1.00
两位小数。SFT/eval 共享消息构造；eval 移除最后的 assistant 训练答案。

## 损失边界

`L = assistant CE（屏蔽 score 数值） + 0.1 × 数值格式损失`。
数值格式损失为合法下一 token 集合总概率的负对数，不以占位分数为分类标签。
teacher-forcing 数值由路径 hash 确定，只覆盖格式分支，不是真实置信度。
格式监督仍会更新共享参数，但末尾分数不会在因果前向中影响此前的坐标。
权重 0.1 是配置初值，未进行科学验证。

此实现未加入强制解码约束，不能保证自由生成一定合法；新增评测器分别报告
定位与严格置信度格式有效率，缺失/非法分数不回填默认值。
不包含置信度校准、GRPO、多候选实现或相关效果结论。

## 检查

- 聚焦测试 153 passed：数值 mask、合法集合损失、梯度、完整/suffix logits
  等价、左右 padding、旧协议、config/launcher，以及实际 Qwen processor 对齐。
- 既有坐标对齐测试单独运行：6 passed。
- shell 语法、启动脚本 `--inspect`、`git diff --check` 通过。
- 补丁应用前校验旧文件 SHA-256，应用后校验 11 个变更文件内容与已测版本一致。
- 未加载模型权重做 GPU forward/backward，未运行科学实验；Solid Run ID：无。

## 使用

在上述代码仓库、已有 IPLoc Python 环境下：

```bash
bash tools/run/train/train_focus_confidence_sft.sh --inspect

bash tools/run/train/train_focus_confidence_sft.sh \
  work_dir=/absolute/path/to/new-e013-output
```

第二条仅为启动模板，本次没有执行。默认复用四卡 NF4 QLoRA、有效 batch 64
和原 SFT runner。用户后续明确指定使用 E-009 相同的完整训练集，已将默认训练
manifest 设置为：
`/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-real-focus-data/manifests/train_only_1shot_focus.json`。
核对包含 10,534 条记录、10,534 个 positive target 样本，无额外子集筛选。
文件 SHA-256：`c607700075de7eba1b0dc8237a32eb1760d3864a4e320f01a41bce8aec94ba78`。
配置一致性测试 1 passed，启动脚本 `--inspect` 和 `git diff --check` 通过。
评测 manifest 仍需单独指定；本次未启动训练，真实 GPU smoke 待后续处理。
