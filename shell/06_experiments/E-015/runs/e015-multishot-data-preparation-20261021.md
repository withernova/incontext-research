# e015-multishot-data-preparation-20261021 · 构造同查询的多帧数据

- workflow: v2 / failed / 运行失败
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-f7db4a16d7c5979126993ef6 / failed

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
（待补充）

## 2. 目的
保留现有测试查询，为一、二、四张参考帧生成可追溯清单，并检查训练与测试来源重叠。

## 3. 方法（干预 · 对照 · 指标与判定规则）
（待补充：干预什么、和什么比、什么算通过）

## 4. 详细实现细节
CPU清单构造，复用已有FOCUS均匀采样器和GOT原视频分组；固定测试集Query/GT，保留共同有效子集和排除原因；对旧GRPO4000条生成独立四参考帧映射，不改原始数据。无模型调用。

- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试路径（不代表已执行）：（未登记，可留空）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'7a5a29a01a52b3bfbd0b4f7594f88f1720ee8d2655633c0ad4fd43d2179fd031'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'`
- commit: `c3e72178f8cca22a14bce9d9b470b1cda4b54c05`
- workspace: 03
- tmux: incontext-E-015-e015-multishot-data-preparation-20261021
- log: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-20261021/managed_console.log
- output: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-20261021/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
（可留空；如有明显的数据、模型或比较限制，请简短记录。）

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "necessity": "现有数据大多是单参考帧，不能直接支持本次四参考帧训练。",
  "implementation_details": "CPU清单构造，复用已有FOCUS均匀采样器和GOT原视频分组；固定测试集Query/GT，保留共同有效子集和排除原因；对旧GRPO4000条生成独立四参考帧映射，不改原始数据。无模型调用。",
  "claim_boundary": "仅输入完整性与来源审计，不代表训练能力或性能。"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
