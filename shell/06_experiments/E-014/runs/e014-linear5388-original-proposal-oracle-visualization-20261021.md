# e014-linear5388-original-proposal-oracle-visualization-20261021 · 用户请求可视化当前选择器与Oracle的差距，明确用原step200 proposal而非三框。对已完成的1766冻结预测做CPU事后分析，核逐例IoU，拆解g

- 父 Run：`e014-selector-linear-decay4041-to5388-eval1766-20261021`
- 来源版本：2026-10-21T13:39:45
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户请求可视化当前选择器与Oracle的差距，明确用原step200 proposal而非三框。对已完成的1766冻结预测做CPU事后分析，核逐例IoU，拆解gap分布/数据集/候选数/命中阈值，导出可筛选图册、参考图及Query上的GT/选择/Oracle对照、统计图与CSV。无新推理、训练或checkpoint变化。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户明确要求原proposal下当前选择器与Oracle的可视化。CPU读取固定linear5388评测与原step200预测，锁定1766 manifest/预测/指标SHA，复用坐标归一化、box_iou及parse_choice源码纯函数（AST载入避免模型包注册）核逐例结果；全部1766图册/CSV、分数据集与损失类别统计、PNG/PDF概览、每数据集最大损失2例对照图。3532图像出现使用原manifest路径，等比例900px JPEG副本，无裁剪；原图SHA/尺寸记录。无模型调用、训练或proposal变化；Git只读clean7caae090，无仓库代码修改或部署。一次性分析脚本与模板作为本Run输入保存并SHA绑定，font亦SHA绑定。seed20260901继承来源事实，本分析确定性排序不采样。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'6eb298e6bba1bf16345d3c78b981eef964aaf2c352dd958d12e76e3dfb209721'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：7caae090351c9c71ce65fd8c98a0bbbbb1825bc6
- 随机种子：20260901
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "frozen_oracle_gap_analysis",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "all",
    "value": {
      "samples": 1766,
      "ours_miou": 0.7194462334134393,
      "oracle_miou": 0.7573992982137026,
      "gap_miou": 0.037953064800262476,
      "gap_sum": 67.02511243726353,
      "contribution_pp": 3.7953064800262477,
      "ours_hits": 1388,
      "oracle_hits": 1467,
      "positive_gap": 109,
      "invalid": 1
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "multi",
    "value": {
      "samples": 791,
      "ours_miou": 0.6737055384736944,
      "oracle_miou": 0.7584401938937492,
      "gap_miou": 0.08473465542005504,
      "gap_sum": 67.02511243726353,
      "contribution_pp": 3.7953064800262477,
      "ours_hits": 576,
      "oracle_hits": 655,
      "positive_gap": 109,
      "invalid": 1
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "by_dataset",
    "value": {
      "LaSOT": {
        "samples": 600,
        "ours_miou": 0.6781810701280799,
        "oracle_miou": 0.7167223918508266,
        "gap_miou": 0.0385413217227463,
        "gap_sum": 23.124793033647776,
        "contribution_pp": 1.3094446791420034,
        "ours_hits": 457,
        "oracle_hits": 485,
        "positive_gap": 38,
        "invalid": 0
      },
      "GOT10k": {
        "samples": 180,
        "ours_miou": 0.8269725873337589,
        "oracle_miou": 0.8462972143842374,
        "gap_miou": 0.019324627050478636,
        "gap_sum": 3.4784328690861543,
        "contribution_pp": 0.19696675362888758,
        "ours_hits": 162,
        "oracle_hits": 166,
        "positive_gap": 4,
        "invalid": 0
      },
      "TAO": {
        "samples": 986,
        "ours_miou": 0.7249273229322606,
        "oracle_miou": 0.7659231510605866,
        "gap_miou": 0.04099582812832618,
        "gap_sum": 40.42188653452961,
        "contribution_pp": 2.2888950472553575,
        "ours_hits": 769,
        "oracle_hits": 816,
        "positive_gap": 67,
        "invalid": 1
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "by_category",
    "value": {
      "threshold_miss": {
        "samples": 79,
        "ours_miou": 0.03639597067795778,
        "oracle_miou": 0.8272734097024002,
        "gap_miou": 0.7908774390244423,
        "gap_sum": 62.47931768293094,
        "contribution_pp": 3.537900208546486,
        "ours_hits": 0,
        "oracle_hits": 79,
        "positive_gap": 79,
        "invalid": 0
      },
      "both_hit_gap": {
        "samples": 5,
        "ours_miou": 0.6961494627904086,
        "oracle_miou": 0.8148852935742275,
        "gap_miou": 0.11873583078381884,
        "gap_sum": 0.5936791539190942,
        "contribution_pp": 0.033617166133584044,
        "ours_hits": 5,
        "oracle_hits": 5,
        "positive_gap": 5,
        "invalid": 0
      },
      "both_miss_gap": {
        "samples": 25,
        "ours_miou": 0.04227315871835416,
        "oracle_miou": 0.200357782734894,
        "gap_miou": 0.1580846240165398,
        "gap_sum": 3.952115600413495,
        "contribution_pp": 0.2237891053461775,
        "ours_hits": 0,
        "oracle_hits": 0,
        "positive_gap": 25,
        "invalid": 1
      },
      "at_oracle": {
        "samples": 1657,
        "ours_miou": 0.7622988474608716,
        "oracle_miou": 0.7622988474608716,
        "gap_miou": 0.0,
        "gap_sum": 0.0,
        "contribution_pp": 0.0,
        "ours_hits": 1383,
        "oracle_hits": 1383,
        "positive_gap": 0,
        "invalid": 0
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "by_candidate_count",
    "value": {
      "0": {
        "samples": 11,
        "ours_miou": 0.0,
        "oracle_miou": 0.0,
        "gap_miou": 0.0,
        "gap_sum": 0.0,
        "contribution_pp": 0.0,
        "ours_hits": 0,
        "oracle_hits": 0,
        "positive_gap": 0,
        "invalid": 0
      },
      "1": {
        "samples": 964,
        "ours_miou": 0.7651877253894614,
        "oracle_miou": 0.7651877253894614,
        "gap_miou": 0.0,
        "gap_sum": 0.0,
        "contribution_pp": 0.0,
        "ours_hits": 812,
        "oracle_hits": 812,
        "positive_gap": 0,
        "invalid": 0
      },
      "2": {
        "samples": 650,
        "ours_miou": 0.7019188725954242,
        "oracle_miou": 0.7640605449207177,
        "gap_miou": 0.06214167232529393,
        "gap_sum": 40.392087011441056,
        "contribution_pp": 2.2872076450419625,
        "ours_hits": 496,
        "oracle_hits": 543,
        "positive_gap": 67,
        "invalid": 1
      },
      "3": {
        "samples": 92,
        "ours_miou": 0.5505602210774075,
        "oracle_miou": 0.7286406005979065,
        "gap_miou": 0.17808037952049902,
        "gap_sum": 16.38339491588591,
        "contribution_pp": 0.9277120563921805,
        "ours_hits": 52,
        "oracle_hits": 72,
        "positive_gap": 26,
        "invalid": 0
      },
      "4": {
        "samples": 31,
        "ours_miou": 0.6578910254004976,
        "oracle_miou": 0.7485438847417573,
        "gap_miou": 0.09065285934125955,
        "gap_sum": 2.810238639579046,
        "contribution_pp": 0.15913016079156547,
        "ours_hits": 22,
        "oracle_hits": 25,
        "positive_gap": 6,
        "invalid": 0
      },
      "5": {
        "samples": 10,
        "ours_miou": 0.27743985462476184,
        "oracle_miou": 0.7402140744483651,
        "gap_miou": 0.46277421982360323,
        "gap_sum": 4.6277421982360325,
        "contribution_pp": 0.26204655709150804,
        "ours_hits": 3,
        "oracle_hits": 8,
        "positive_gap": 6,
        "invalid": 0
      },
      "6": {
        "samples": 8,
        "ours_miou": 0.3541566341102544,
        "oracle_miou": 0.7056128431254423,
        "gap_miou": 0.3514562090151878,
        "gap_sum": 2.8116496721215025,
        "contribution_pp": 0.15921006070903185,
        "ours_hits": 3,
        "oracle_hits": 7,
        "positive_gap": 4,
        "invalid": 0
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "eps",
    "value": 1e-10,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "top_gap_shares",
    "value": {
      "10": 0.1450258161070968,
      "20": 0.28517010286925293,
      "50": 0.664599764181482,
      "100": 0.997153120145331
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "positive_gap_quantiles",
    "value": {
      "0.25": 0.3738353465973894,
      "0.5": 0.710409472126295,
      "0.75": 0.8845346737592114,
      "0.9": 0.9542218089754363
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "overlap_below_point1",
    "value": 89,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "source_run",
    "value": "e014-selector-linear-decay4041-to5388-eval1766-20261021",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "analysis_run",
    "value": "e014-linear5388-original-proposal-oracle-visualization-20261021",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "git_commit",
    "value": "7caae090351c9c71ce65fd8c98a0bbbbb1825bc6",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "seed",
    "value": 20260901,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "input_pins",
    "value": {
      "selector_predictions": {
        "path": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-linear-decay4041-to5388-eval1766-20261021/payload/evaluation/predictions.jsonl",
        "sha256": "88723b51c29aac929d6f576a43821f949b83f59515348f318d46ed1fa1cafb50"
      },
      "proposal_predictions": {
        "path": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-score04-step200-eval1766-20261015T152856Z/payload/evaluation/predictions.jsonl",
        "sha256": "1a864fdce10f300ec53ddf2945b7e2d063c74280d7a750207dcff99a7ff76129"
      },
      "manifest": {
        "path": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-score04-step200-eval1766-20261015T152856Z/inputs/manifest.json",
        "sha256": "8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d"
      },
      "metrics": {
        "path": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-linear-decay4041-to5388-eval1766-20261021/payload/evaluation/metrics.json",
        "sha256": "171f568318af6d84824bab8b5129992339af7e86c3c9ec3344a3a08f306f68e4"
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "shared_implementations",
    "value": {
      "iploc_szy/prompting/coordinates.py": {
        "sha256": "0e0412245ba3fcab3db2791bf3c7557195994af3afaba9a19e2cbb1d4e37197f",
        "functions": [
          "parse_box",
          "pixel_to_normalized",
          "format_box"
        ]
      },
      "iploc_szy/evaluation/bbox.py": {
        "sha256": "3ee0ded78803ef411d443ac2132f64ce6ffa252db148c69f0e81e89ce3945f36",
        "functions": [
          "box_iou"
        ]
      },
      "iploc_szy/evaluation/candidate_vqa.py": {
        "sha256": "9cd99507df770531b11e683b7335be8f63bb78b9e0f591384077e7a386b2a2f7",
        "functions": [
          "parse_choice"
        ]
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "model_calls",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "interpretation",
    "value": "Oracle为同一冻结候选集合中GT IoU最高的框；差距=Oracle IoU−实际IoU。与Oracle相等不代表GT定位完美。几何重叠不能证明对象身份。",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "image_audit",
    "value": {
      "unique_images": 3532,
      "matched_manifest_occurrences": 3532,
      "gt_normalization_matches": 1766,
      "preview_max_edge": 900,
      "jpeg_quality": 84,
      "crop": false
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  },
  {
    "metric_id": "example_ids",
    "value": [
      "560-1",
      "383-1",
      "682-1",
      "649-1",
      "1362-1",
      "1533-1"
    ],
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-original-proposal-oracle-visualization-20261021/metrics.json"
  }
]
```

### 分析
原step200 proposal×linear5388的1766冻结结果CPU分析，新增模型调用0。真实exit0/marker；1766逐例ID/候选顺序/GT归一化/IoU/编号EOS和聚合指标核对通过，3532原图SHA与尺寸及预览下载SHA记录。全量mIoU71.944623→Oracle75.739930%，差3.795306pp；791多框67.370554→75.844019%，差8.473466pp。109条正差距：79条实际<.5而Oracle≥.5贡献3.537900pp（93.217774%，61条实际IoU0）；5条均命中贡献.033617pp（.885756%）；25条均未命中贡献.223789pp（5.896470%，含唯一无效回复）。其余1657达Oracle，其中274仍低于.5。LaSOT/GOT/TAO正差距38/4/67，漏选好框28/4/47；TAO占总差距60.308570%。前20/50条解释28.517010/66.459976%损失。全部1766离线图册可按类型/数据集/候选数/ID筛选，显示Reference、所选框、Oracle与GT；另有PNG/PDF/CSV。优先诊断79条漏选好框，比已命中后的边框精度更直接对应当前差距。

### 局限
Oracle为同冻结候选中GT IoU最大者，是事后上限，不是可用推理或数据集极限。单次固定测试结果，无新泛化/显著性结论；几何低重叠不能直接等价身份混淆。每数据集最大损失两例观察到相似实例间误选，只是定向六例，不外推全部成因或Reference因果。图像为最长边900px JPEG84等比例浏览副本，无裁剪。13组Node筛选逻辑验收、PNG/PDF人工目视，未做真实浏览器自动渲染测试。首图图例遮挡后仅生成独立v2展示版本，首版、预测与指标保留。22未注册字段为辅助指标，Claim不变。

### Claim 边界
本次仅补原第4epoch，不是再加4epoch；从保存4041开始，不使用未保存4463状态。逐rank RNG不精确恢复，seed重设，不能声称逐位等价不间断续训。测试反复探索，单seed，不修改Claim。

### 产物索引
shell/06_experiments/E-014/visualizations/original-proposal-oracle-20261021/index_v2.html
shell/06_experiments/E-014/visualizations/original-proposal-oracle-20261021/overview_v2.png
shell/06_experiments/E-014/visualizations/original-proposal-oracle-20261021/overview_v2.pdf
shell/06_experiments/E-014/visualizations/original-proposal-oracle-20261021/largest_gap_examples.pdf
shell/06_experiments/E-014/visualizations/original-proposal-oracle-20261021/samples.csv
shell/06_experiments/E-014/执行对照-20261021.md
.pi/analysis/e014/oracle-gap-20261021/spec.json
.pi/analysis/e014/oracle-gap-20261021/download_audit.json
.pi/analysis/e014/oracle-gap-20261021/presentation_revision_receipt.json
.pi/analysis/e014/oracle-gap-20261021/viewer_logic_audit.json
.pi/analysis/e014/oracle-gap-20261021/complete_receipt.json

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
