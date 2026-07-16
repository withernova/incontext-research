# E-003 Results

> 主题：审计 IPLoc-ID identification-only F1 是否与 localization correctness 解耦。正式措辞是“是否高估 joint task success”，不预设或声称论文造假。

## Run 状态

| Run | 性质 | 状态 | 可否引用 |
|---|---|---|---|
| E003-R-001-data-rehydrate-local-lasot-n140 | data preparation | completed | 只引用数据完整性 |
| E003-R-002-joint-f1-n140-failed-env | failed attempt | failed | 否；零有效记录 |
| E003-R-003-torch-compat-smoke-local-lasot-n1 | environment smoke | passed | 只引用链路通过 |
| E003-R-004-joint-f1-iou-local-lasot-n140 | early attempt | aborted/superseded | 否；输出被 80-token 截断 |
| E003-R-004b-joint-f1-iou-local-lasot-n140-t128 | main diagnostic | completed | 是，限本地 split 与指标审计范围 |

## 数据与完整性

`E003-R-001` 从 `/home/featurize/data/LaSOTTesting` 重建：

```text
140 samples / 70 classes
140 positive + 140 same-class negative
missing=0 / invalid_bbox=0
```

这是本地确定性重建，不是官方 IPLoc-ID test split。

## 失败与工程运行

- `E003-R-002`：torch 2.2.2 缺失 `torch.compiler.is_compiling`，processor 对全部 target 失败；`outputs=[]`、`num_data=0`，随后 `ZeroDivisionError`。文件中的 0 指标不是模型性能。
- `E003-R-003`：以本地 snapshot 和最小兼容注入跑通 1 positive + 1 negative，得到 TP=1、TN=1；仅为 smoke。
- `E003-R-004`：在约9/140主动停止，因为 `max_new_tokens=80` 令部分 generation 在 Yes/No 前截断；由 R-004b 取代。

## E003-R-004b 主结果

完整性：280 records，140 positive、140 negative，无 processor failure/traceback。

| 口径 | TP | TN | FP | FN | F1 | positive joint recall |
|---|---:|---:|---:|---:|---:|---:|
| Identification-only | 133 | 136 | 4 | 7 | **0.9603** | 0.9500（Yes recall） |
| Joint @ IoU≥0.3 | 97 | 136 | 4 | 43 | **0.8050** | 0.6929 |
| Joint @ IoU≥0.5 | 89 | 136 | 4 | 51 | **0.7639** | 0.6357 |
| Joint @ IoU≥0.7 | 76 | 136 | 4 | 64 | **0.6909** | 0.5429 |

Positive localization：

```text
mean IoU all positives   = 0.5745
median IoU all positives = 0.7414
mean IoU | identification TP   = 0.5880
median IoU | identification TP = 0.7441
```

133 个 identification TP 的 IoU bins：

```text
[0,.1):   35
[.1,.3):   1
[.3,.5):   8
[.5,.7):  13
[.7,1]:   76
```

即 identification TP 中：

```text
IoU < 0.3: 36/133 = 27.1%
IoU < 0.5: 44/133 = 33.1%
IoU < 0.7: 57/133 = 42.9%
```

## 当前结论

可支持：

> 在该本地重建 LaSOT POIL split 上，IPLoc-ID 的 identification-only F1 与联合 identification-localization 正确性明显解耦。回答 Yes 的 positive 即使 bbox 严重错误仍被计为 identification TP，因此 F1=0.9603 并不代表同等比例的 joint task success；要求 IoU≥0.5 后 Joint F1 为0.7639。

不能支持：

- 不可声称官方论文 split 上一定有相同幅度；
- 不可把 F1 与 mIoU 直接相减解释成“错误推理比例”；
- 不可仅凭该结果断言背景、类别、global appearance 或 container shortcut；
- verifier 是否依赖 candidate box 仍需 `E003-R-005` forced-candidate probe。

## 审核入口

```text
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128/config/run.md
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128/logs/run.log
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128/analysis/joint_f1_iou.json
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128/results/LASOT_local_1shot_T2_n140_v2/generated_texts/e003_r004b_joint_n140.json
```
