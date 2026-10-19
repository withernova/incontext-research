# e014-selection-fulltrain-step200-gtaugment-20261018 · 用户明确授权启动完整训练集的固定候选生成LoRA推理及选择数据构造，不训练选择器。采用E009完整有效10522正例清单（原10534排除12无效框），包括GO

- 父 Run：`e014-selection-sft-data-step200-20261018`
- 来源版本：2026-10-18T13:20:19
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户明确授权启动完整训练集的固定候选生成LoRA推理及选择数据构造，不训练选择器。采用E009完整有效10522正例清单（原10534排除12无效框），包括GOT10k/LaSOT/TAO，按原视频/序列排除已有1766评测、334选择验证及E013已有validation/test来源，去重并固定实际可用规模。固定score0.4/step200生成LoRA，沿用上一轮生成参数与seed20260901。保留原始候选/评分/IoU；Oracle<0.5且至少有一个候选时在独立副本加GT，Oracle>=0.5保持原候选；零候选单列不生成单选训练题。复用既有sft数据接口/画框与编号轮换，最优gap>0.05；现有334验证不加GT、不新增验证推理。完整记录输入SHA/排除/GT插入及候选置换来源；只完成生成和数据，不额外训练或测试/修改Claim。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：无源码改变。先准备pinned全训练manifest，复用普通variable_candidates evaluator。managed命令只执行生成阶段；终态后核验并通过离线数据变换+原prepare_candidate_selection.py sft构造，不启动第二次推理，不修改远端代码。
- 命令：test ! -e /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/payload/generation && test ! -e /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json && PYTHONPATH=. OMP_NUM_THREADS=1 IPLOC_PYTHON=/songzhengyue/miniconda3/envs/IPLoc/bin/python bash tools/run.sh configs/eval/variable_candidates.py --cfg-options work_dir=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/payload/generation model.model_path=/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct test_dataloader.dataset.ann_file=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/inputs/manifest.json test_dataloader.dataset.ann_file_sha256=184f50ab3663a5a2640f62b9cdb6ebf96dd7121480d9508caf7e3aef99d95640 test_dataloader.dataset.prompt_variant=boxes_then_scores_v1 evaluator.prompt_variant=boxes_then_scores_v1 evaluation.checkpoint=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/20261015-172638__discovery-priority__score0.4-selected0.2-coverage0.5__kl0__sft659__200step__seed11451/payload/grpo/checkpoints/step_000200 evaluation.require_eos=True evaluation.seed=20260901 && cp /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/payload/generation/evaluation/metrics.json /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json && echo SURVEY_TOOL_RUN_COMPLETE
- 代码版本：53ab7653602f62ffc1d5c9dadfbefccf7ad67474
- 随机种子：20260901
- 配置：configs/eval/variable_candidates.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json

## 结果
8367候选生成已exit0，生成阶段已核验；729源GT副本已准备，渲染仍运行。完整数据验收转交用户新授权自动训练子Run中的强制前置门禁，不能称数据已全部验收。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "evaluate",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "checkpoint",
    "value": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/20261015-172638__discovery-priority__score0.4-selected0.2-coverage0.5__kl0__sft659__200step__seed11451/payload/grpo/checkpoints/step_000200",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "dataloader",
    "value": "test_dataloader",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "dataset_size",
    "value": 8367,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "evaluated_samples",
    "value": 8367,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "world_size",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "max_new_tokens",
    "value": 192,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "vision_max_patch_tokens",
    "value": 4096,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "vision_max_pixels",
    "value": 1048576,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "selection",
    "value": "head",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "selection_seed",
    "value": null,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "seconds",
    "value": 6690.168206691742,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "samples_per_second",
    "value": 1.2506412008641326,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "samples",
    "value": 8367,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "parse_rate",
    "value": 0.9958168997251106,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "miou",
    "value": 0.7608360878380894,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.25",
    "value": 0.8728337516433609,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.5",
    "value": 0.8448667383769571,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.75",
    "value": 0.736584199832676,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "iou_distribution",
    "value": {
      "count": 8367,
      "min": 0.0,
      "q25": 0.7325772755059056,
      "median": 0.9017369124256043,
      "q75": 0.958839229671187,
      "max": 1.0,
      "bins": {
        "[0.00,0.10)": 966,
        "[0.10,0.25)": 98,
        "[0.25,0.50)": 234,
        "[0.50,0.75)": 906,
        "[0.75,1.00]": 6163
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "confidence_format_valid_rate",
    "value": 0.9958168997251106,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "confidence_invalid_count",
    "value": 35,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "candidate_selection",
    "value": "highest_score_then_first",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "candidate_output_layout",
    "value": "boxes_then_scores",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "candidate_count_policy",
    "value": "variable_nonempty_no_box_count_cap",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "candidate_count_histogram",
    "value": {
      "0": 35,
      "1": 5172,
      "2": 2503,
      "3": 456,
      "4": 139,
      "5": 40,
      "6": 22
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "variable_candidate_format_valid_rate",
    "value": 0.9958168997251106,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "multiple_candidate_rate",
    "value": 0.3776741962471615,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "first_candidate_miou",
    "value": 0.7189127966104869,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "oracle_miou",
    "value": 0.8142817034082082,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "oracle_gap",
    "value": 0.05344561557011873,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "selected_nonfirst_rate",
    "value": 0.1007529580494801,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "spatial_order_valid_rate",
    "value": 0.9156208915979444,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "spatial_order_valid_given_format",
    "value": 0.9194671147383582,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "near_duplicate_rate",
    "value": 0.002270825863511414,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "nonfirst_acc",
    "value": 0.572541382667965,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "nonfirst_acc_samples",
    "value": 1027,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "iou_argmax_tie_policy",
    "value": "earliest_candidate",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  },
  {
    "metric_id": "by_dataset",
    "value": {
      "GOT10k": {
        "samples": 7315,
        "parse_rate": 0.9957621326042378,
        "miou": 0.7724573314570699,
        "acc_iou_0.25": 0.8839371155160629,
        "acc_iou_0.5": 0.8585099111414901,
        "acc_iou_0.75": 0.7520164046479836,
        "iou_distribution": {
          "count": 7315,
          "min": 0.0,
          "q25": 0.7517387312202907,
          "median": 0.9049343863191022,
          "q75": 0.9587443419682387,
          "max": 1.0,
          "bins": {
            "[0.00,0.10)": 773,
            "[0.10,0.25)": 76,
            "[0.25,0.50)": 186,
            "[0.50,0.75)": 779,
            "[0.75,1.00]": 5501
          }
        },
        "confidence_format_valid_rate": 0.9957621326042378,
        "confidence_invalid_count": 31,
        "candidate_selection": "highest_score_then_first",
        "candidate_output_layout": "boxes_then_scores",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "0": 31,
          "1": 4546,
          "2": 2152,
          "3": 410,
          "4": 121,
          "5": 35,
          "6": 20
        },
        "variable_candidate_format_valid_rate": 0.9957621326042378,
        "multiple_candidate_rate": 0.37429938482570063,
        "first_candidate_miou": 0.726540264610641,
        "oracle_miou": 0.8239544521538856,
        "oracle_gap": 0.05149712069681578,
        "selected_nonfirst_rate": 0.10157211209842788,
        "spatial_order_valid_rate": 0.9166097060833903,
        "spatial_order_valid_given_format": 0.9205107084019769,
        "near_duplicate_rate": 0.0019138755980861245,
        "nonfirst_acc": 0.5877192982456141,
        "nonfirst_acc_samples": 912,
        "iou_argmax_tie_policy": "earliest_candidate"
      },
      "LaSOT": {
        "samples": 553,
        "parse_rate": 0.9927667269439421,
        "miou": 0.6672903174652682,
        "acc_iou_0.25": 0.8137432188065099,
        "acc_iou_0.5": 0.7649186256781193,
        "acc_iou_0.75": 0.5913200723327305,
        "iou_distribution": {
          "count": 553,
          "min": 0.0,
          "q25": 0.538986977710314,
          "median": 0.8054249826616321,
          "q75": 0.9287542087542088,
          "max": 0.9941747572815534,
          "bins": {
            "[0.00,0.10)": 91,
            "[0.10,0.25)": 12,
            "[0.25,0.50)": 27,
            "[0.50,0.75)": 96,
            "[0.75,1.00]": 327
          }
        },
        "confidence_format_valid_rate": 0.9927667269439421,
        "confidence_invalid_count": 4,
        "candidate_selection": "highest_score_then_first",
        "candidate_output_layout": "boxes_then_scores",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "0": 4,
          "1": 362,
          "2": 156,
          "3": 17,
          "4": 12,
          "5": 1,
          "6": 1
        },
        "variable_candidate_format_valid_rate": 0.9927667269439421,
        "multiple_candidate_rate": 0.33815551537070526,
        "first_candidate_miou": 0.6545671645750369,
        "oracle_miou": 0.7292294631565639,
        "oracle_gap": 0.06193914569129566,
        "selected_nonfirst_rate": 0.09584086799276673,
        "spatial_order_valid_rate": 0.9113924050632911,
        "spatial_order_valid_given_format": 0.9180327868852459,
        "near_duplicate_rate": 0.0054249547920434,
        "nonfirst_acc": 0.48214285714285715,
        "nonfirst_acc_samples": 56,
        "iou_argmax_tie_policy": "earliest_candidate"
      },
      "TAO": {
        "samples": 499,
        "parse_rate": 1.0,
        "miou": 0.6941455346183206,
        "acc_iou_0.25": 0.7755511022044088,
        "acc_iou_0.5": 0.7334669338677354,
        "acc_iou_0.75": 0.6713426853707415,
        "iou_distribution": {
          "count": 499,
          "min": 0.0,
          "q25": 0.42475797633157886,
          "median": 0.9176272139443351,
          "q75": 0.9784705640402068,
          "max": 1.0,
          "bins": {
            "[0.00,0.10)": 102,
            "[0.10,0.25)": 10,
            "[0.25,0.50)": 21,
            "[0.50,0.75)": 31,
            "[0.75,1.00]": 335
          }
        },
        "confidence_format_valid_rate": 1.0,
        "confidence_invalid_count": 0,
        "candidate_selection": "highest_score_then_first",
        "candidate_output_layout": "boxes_then_scores",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "1": 264,
          "2": 195,
          "3": 29,
          "4": 6,
          "5": 4,
          "6": 1
        },
        "variable_candidate_format_valid_rate": 1.0,
        "multiple_candidate_rate": 0.4709418837675351,
        "first_candidate_miou": 0.6784081996054504,
        "oracle_miou": 0.7667420877459615,
        "oracle_gap": 0.0725965531276409,
        "selected_nonfirst_rate": 0.09418837675350701,
        "spatial_order_valid_rate": 0.905811623246493,
        "spatial_order_valid_given_format": 0.905811623246493,
        "near_duplicate_rate": 0.004008016032064128,
        "nonfirst_acc": 0.423728813559322,
        "nonfirst_acc_samples": 59,
        "iou_argmax_tie_policy": "earliest_candidate"
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 0 declared and 40 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### Claim 边界
本次扩大到TAO train499，不再沿用父无TAO训练来源说明。只构造数据不训练/评测选择器，不宣称新泛化收益；生成器历史暴露限制不消失。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step200-gtaugment-20261018/managed_console.log

### 审核入口
.pi/analysis/e014/selection-sft/fulltrain_preparation.json
.pi/analysis/e014/selection-sft/fulltrain_command.json

### 过程记录
用户新授权自动等待→数据完整验收→5epoch训练，且不用Steward。子Run e014-selection-fulltrain-gt-lora5epoch-20261019保存有审核及SHA锁定的串行脚本；父managed命令本来只生成+copy原生成metrics，不含渲染，现仅完成父生成进程登记以释放同进程受管控制。父完整数据任务验收未完成，子训练只在全部数据门禁通过后启动。父原始metrics/输出保持不动，队列paused、监控stopped。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
