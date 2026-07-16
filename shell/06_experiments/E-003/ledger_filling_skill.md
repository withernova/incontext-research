# Experiment ledger filling skill（跨项目通用版）

> 目的：任何 agent 在把实验结果写入本地实验表、run registry、结果 Markdown 或同步工具前，必须先按本文件做自检。本文件只记录**跨项目通用要求**；项目特定路径、模型、hook、数据集细节应写到该项目的 `experiment_audit_notes.md` / run note / config 中。

## 1. 一一对应原则

实验登记中的 `run_id` 必须能唯一映射到真实实验产物目录。

要求：
- 本地 registry 的 `id`、结果表中的 Run、run note 文件名、远端/本地产物目录名应尽量一致。
- 如果因为历史原因不能一致，必须有明确 mapping 表，且不能让审核者猜。
- 禁止创建无法对应到真实产物目录的“自动编号 run”。

推荐目录结构：

```text
<experiment_root>/runs/<RUN_ID>/
  logs/
  results/
  analysis/
  visualizations/
  manifests/
  artifacts/
  config/
```

## 2. 填表前必须读取的材料

填写或更新 run 记录前，至少读取：

1. `config/run.md` 或等价配置文件；
2. `logs/run.log`；
3. `analysis/summary.json` / `metrics.json` / 等价汇总文件；
4. `results/outputs.*` / per-sample 输出；
5. 若有可视化，读取/确认 `visualizations/manifest.*`。

如果缺少关键文件，状态应写为：
- `incomplete`：实验没跑完或产物缺失；
- `unknown`：无法确认；
- `failed`：有明确错误。

不得凭记忆或聊天上下文补写不存在的指标。

## 3. 每个 run 的必填信息

每条实验记录至少包含：

1. **run_id**：和产物目录一致或有 mapping。
2. **实验性质**：例如 `smoke`、`sanity baseline`、`main experiment`、`ablation`、`destructive control`、`data preparation`、`monitoring/ops`。
3. **目的 / 必要性**：该 run 回答什么问题；为什么需要它；缺少它会导致哪条证据链断裂。
4. **数据与规模**：数据源、manifest、样本数、类别数、positive/negative 数、随机种子、筛选规则。
5. **模型与入口**：模型版本、权重、主要脚本/命令、关键参数。
6. **干预或变量定义**：每个 variant/mode 到底改了什么。
7. **对照组**：baseline、negative control、positive/destructive control 是否齐全。
8. **指标**：主指标、辅助指标、计算公式、缺失值处理。
9. **结果摘要**：只总结实际观测，不加入未验证推断。
10. **结论边界**：这个 run 能支持什么，不能支持什么。
11. **局限与混杂因素**：样本小、代理扰动、artifact、数据偏差、解析不稳等。
12. **审核入口**：log、summary、outputs、visualization、config 路径。

## 4. 干预实验的额外记录要求

凡是涉及 shuffle、mask、ablation、replacement、copy/padding、dropout、prompt 改写、数据扰动等，都必须记录到可复现粒度。

### 4.1 干预层级
必须说明干预发生在哪一层：
- 输入级：像素、patch、文本、prompt、bbox；
- 表征级：embedding、token、feature map、attention；
- 输出级：post-processing、threshold、解析器。

不同层级的结果不能混为同一种机制证据。

### 4.2 干预区域 / 对象选择
必须说明被干预对象如何选中：
- bbox 全区域；
- bbox 中心区域；
- mask overlap；
- padding ring；
- top-k token / hard token；
- 全局随机；
- 其他规则。

如果讨论过“中心区域是否更重要”，表中必须明确当前 run 是中心区域还是完整区域；不能只写“object region”。

### 4.3 坐标和网格映射
涉及图像或 token grid 时必须记录：
- resize / crop / padding 规则；
- 原图坐标到模型输入坐标的变换；
- feature/token grid 尺寸；
- cell 与 bbox/mask 的 overlap 判定；
- 每个样本或每张图被选中的元素数量。

### 4.4 shuffle / replacement / ablation 规则
必须记录：
- shuffle 是在值之间 permute，还是位置 permute，还是同时改变；
- replacement 的 donor 来源；
- ablation 用 zero、mean、learned mask、random token 还是其他值；
- 随机种子；
- 是否 per-sample / per-image / global 固定；
- 是否多 seed。

### 4.5 必要对照
干预实验通常需要：
- baseline；
- 局部干预；
- 全局/破坏性干预；
- 随机或无关区域 control；
- 如果是 ablation，尽量区分 zero 与 distribution-preserving replacement。

## 5. 结果解释规范

结果表必须把三类内容分开：

1. **观测事实**：指标、曲线、输出文本、错误率。
2. **直接解释**：在当前设置下 A 比 B 高/低，某干预导致某指标变化。
3. **机制推断**：只能写成谨慎假设，必须列出替代解释和下一步验证。

禁止：
- 用 smoke test 写科学结论；
- 用 patch/input-level proxy 直接证明 hidden/token-level 机制；
- 用小样本结果写强结论；
- 省略失败 run 或异常解析；
- 只报喜不报局限。

## 6. 推荐表格模板

```markdown
### <RUN_ID>
- 产物目录：`.../<RUN_ID>/`
- 性质：main experiment / ablation / smoke / ...
- 必要性：...
- 数据：manifest=..., n=..., split/filter=..., seed=...
- 模型与命令：...
- 变量/干预：
  - mode_a: ...
  - mode_b: ...
- 干预层级：input / representation / output
- 干预区域：bbox_full / bbox_center / mask / ring / all / ...
- 映射规则：resize=..., grid=..., overlap=..., selected_counts=...
- 对照：baseline=..., destructive_control=..., random_control=...
- 指标：...
- 结果：...
- 支持的结论：...
- 不支持/不能回答：...
- 局限与下一步：...
- 审核入口：config=..., log=..., summary=..., outputs=..., vis=...
```

## 7. 写入前自检清单

填表前逐项确认：

- [ ] run id 能对应真实目录。
- [ ] 读过 config/log/summary/outputs。
- [ ] 写清楚实验性质和必要性。
- [ ] 写清楚数据规模和筛选规则。
- [ ] 写清楚每个 mode 到底改了什么。
- [ ] 写清楚干预层级、区域、映射、seed。
- [ ] 有 baseline 和必要 control。
- [ ] 指标来自文件，不是记忆。
- [ ] 结论边界和局限已写。
- [ ] 没有把 proxy/smoke/ops run 写成主证据。
