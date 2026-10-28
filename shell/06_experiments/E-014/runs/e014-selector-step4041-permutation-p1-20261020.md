# e014-selector-step4041-permutation-p1-20261020 · 用户已授权“可以部署运行”，部署7caae090351c9c71ce65fd8c98a0bbbbb1825bc6及有限逻辑/真实输入验收已完成。现在执行一次st

- 父 Run：`e014-historical-balanced-vqa-step4041-test1766-20261020`
- 来源版本：2026-10-20T11:19:55
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户已授权“可以部署运行”，部署7caae090351c9c71ce65fd8c98a0bbbbb1825bc6及有限逻辑/真实输入验收已完成。现在执行一次step4041选择器换序P1诊断：冻结1766/791和原候选不变，无框exact_instance，原顺序加每题1个非重复排列；8GPU/BF16/SDPA/greedy16/EOS/vision4096/seed20260901。1582次多框VQA，原顺序保留为主结果，不投票、不训练、不自动重试或恢复历史任务；记录映射/回复/有效性/实际grid。仅启动核验，无短周期轮询。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：单次指定step4041候选换序诊断P1；原冻结1766/791输入与SHA不变；无框原图exact_instance、BF16/SDPA、8GPU、greedy16/EOS、vision4096每图、seed20260901。791多框各原顺序+1个非重复排列，共1582模型调用；单框964/空11保持原路由；主结果原顺序，不投票、不回退。adapterSHA=a3c7ba7dff8df6c8bd1743db9b51a3ef95c5eae6d092999438594bef44d88840。模型路径、来源checkpoint及真实命令见command；仅一次，无自动重试。1766已反复探索、单seed，换序不是独立样本；不改Claim。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,subprocess; assert hashlib.sha256(pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-balanced-vqa-lora4epoch-20261019/payload/training/checkpoints/samples_00064656_step_004041/adapter/adapter_model.safetensors'"'"').read_bytes()).hexdigest()=='"'"'a3c7ba7dff8df6c8bd1743db9b51a3ef95c5eae6d092999438594bef44d88840'"'"'; p=subprocess.check_output(['"'"'nvidia-smi'"'"','"'"'--query-compute-apps=pid'"'"','"'"'--format=csv,noheader'"'"'],text=True); assert not p.strip(), '"'"'GPU compute process already active'"'"'; print('"'"'CHECKPOINT_SHA_AND_GPU_PREFLIGHT_PASSED'"'"',flush=True)' && test ! -e /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json && test ! -L /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json && PYTHONPATH=. OMP_NUM_THREADS=1 /songzhengyue/miniconda3/envs/IPLoc/bin/python -m torch.distributed.run --standalone --nproc_per_node=8 tools/evaluate_candidate_vqa.py --manifest /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-score04-step200-eval1766-20261015T152856Z/inputs/manifest.json --manifest-sha256 8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d --predictions /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-score04-step200-eval1766-20261015T152856Z/payload/evaluation/predictions.jsonl --predictions-sha256 1a864fdce10f300ec53ddf2945b7e2d063c74280d7a750207dcff99a7ff76129 --model-path /defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct --output-dir /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/payload --expected-samples 1766 --expected-multi 791 --seed 20260901 --max-new-tokens 16 --vision-max-patch-tokens 4096 --prompt-variant exact_instance --permutation-extra-orders 1 --selector-checkpoint /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-balanced-vqa-lora4epoch-20261019/payload/training/checkpoints/samples_00064656_step_004041 && cp /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/payload/metrics.json /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json && echo SURVEY_TOOL_RUN_COMPLETE
- 代码版本：7caae090351c9c71ce65fd8c98a0bbbbb1825bc6
- 随机种子：20260901
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "candidate_vqa",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json"
  },
  {
    "metric_id": "evaluated_samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json"
  },
  {
    "metric_id": "world_size",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json"
  },
  {
    "metric_id": "vqa_samples",
    "value": 791,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json"
  },
  {
    "metric_id": "all",
    "value": {
      "samples": 1766,
      "vqa_iou_mean": 0.718586281701126,
      "vqa_iou_acc50": 0.7865232163080408,
      "score_iou_mean": 0.6916960157722533,
      "score_iou_acc50": 0.7553793884484711,
      "first_iou_mean": 0.656632485224866,
      "first_iou_acc50": 0.7151755379388448,
      "oracle_iou_mean": 0.7573992982137026,
      "oracle_iou_acc50": 0.8306908267270668,
      "valid_vqa_answers": 791,
      "invalid_vqa_answers": 0,
      "improves_score": 108,
      "worsens_score": 48,
      "fixes_score_miss": 84,
      "breaks_score_hit": 29,
      "oracle_hit_samples": 1467,
      "vqa_hit_given_oracle_hit": 0.9468302658486708
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json"
  },
  {
    "metric_id": "multi",
    "value": {
      "samples": 791,
      "vqa_iou_mean": 0.6717855957127017,
      "vqa_iou_acc50": 0.729456384323641,
      "score_iou_mean": 0.6117499324631576,
      "score_iou_acc50": 0.6599241466498104,
      "first_iou_mean": 0.5334665001664629,
      "first_iou_acc50": 0.5701643489254109,
      "oracle_iou_mean": 0.7584401938937492,
      "oracle_iou_acc50": 0.8280657395701644,
      "valid_vqa_answers": 791,
      "invalid_vqa_answers": 0,
      "improves_score": 108,
      "worsens_score": 48,
      "fixes_score_miss": 84,
      "breaks_score_hit": 29,
      "oracle_hit_samples": 655,
      "vqa_hit_given_oracle_hit": 0.8809160305343512
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json"
  },
  {
    "metric_id": "by_dataset",
    "value": {
      "GOT10k": {
        "samples": 180,
        "vqa_iou_mean": 0.8218918400987801,
        "vqa_iou_acc50": 0.8944444444444445,
        "score_iou_mean": 0.7959036041152275,
        "score_iou_acc50": 0.8611111111111112,
        "first_iou_mean": 0.782188525520559,
        "first_iou_acc50": 0.85,
        "oracle_iou_mean": 0.8462972143842374,
        "oracle_iou_acc50": 0.9222222222222223,
        "valid_vqa_answers": 51,
        "invalid_vqa_answers": 0,
        "improves_score": 8,
        "worsens_score": 3,
        "fixes_score_miss": 8,
        "breaks_score_hit": 2,
        "oracle_hit_samples": 166,
        "vqa_hit_given_oracle_hit": 0.9698795180722891
      },
      "LaSOT": {
        "samples": 600,
        "vqa_iou_mean": 0.6775315741357881,
        "vqa_iou_acc50": 0.7616666666666667,
        "score_iou_mean": 0.6537116103330052,
        "score_iou_acc50": 0.7366666666666667,
        "first_iou_mean": 0.625383400920118,
        "first_iou_acc50": 0.7,
        "oracle_iou_mean": 0.7167223918508266,
        "oracle_iou_acc50": 0.8083333333333333,
        "valid_vqa_answers": 246,
        "invalid_vqa_answers": 0,
        "improves_score": 35,
        "worsens_score": 18,
        "fixes_score_miss": 27,
        "breaks_score_hit": 12,
        "oracle_hit_samples": 485,
        "vqa_hit_given_oracle_hit": 0.9422680412371134
      },
      "TAO": {
        "samples": 986,
        "vqa_iou_mean": 0.7247098354816787,
        "vqa_iou_acc50": 0.781947261663286,
        "score_iou_mean": 0.6957865607639502,
        "score_iou_acc50": 0.7474645030425964,
        "first_iou_mean": 0.652727174200144,
        "first_iou_acc50": 0.6997971602434077,
        "oracle_iou_mean": 0.7659231510605866,
        "oracle_iou_acc50": 0.8275862068965517,
        "valid_vqa_answers": 494,
        "invalid_vqa_answers": 0,
        "improves_score": 65,
        "worsens_score": 27,
        "fixes_score_miss": 49,
        "breaks_score_hit": 15,
        "oracle_hit_samples": 816,
        "vqa_hit_given_oracle_hit": 0.9448529411764706
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json"
  },
  {
    "metric_id": "source_manifest_sha256",
    "value": "8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json"
  },
  {
    "metric_id": "source_predictions_sha256",
    "value": "1a864fdce10f300ec53ddf2945b7e2d063c74280d7a750207dcff99a7ff76129",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json"
  },
  {
    "metric_id": "prompt_sha256",
    "value": "b737f254c6c86215fa009600eccad51ac741cb46db6e7188aacfe3f390f7f6f2",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json"
  },
  {
    "metric_id": "prompt_variant",
    "value": "exact_instance",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json"
  },
  {
    "metric_id": "image_presentation",
    "value": "original",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json"
  },
  {
    "metric_id": "selector",
    "value": "selection_lora_bfloat16",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json"
  },
  {
    "metric_id": "selector_checkpoint",
    "value": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-balanced-vqa-lora4epoch-20261019/payload/training/checkpoints/samples_00064656_step_004041",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json"
  },
  {
    "metric_id": "candidate_order",
    "value": "source",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json"
  },
  {
    "metric_id": "settings",
    "value": {
      "seed": 20260901,
      "max_new_tokens": 16,
      "vision_max_patch_tokens": 4096,
      "do_sample": false,
      "require_eos": true,
      "record_input_metadata": true
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json"
  },
  {
    "metric_id": "order_diagnostics",
    "value": {
      "source_samples": 791,
      "total_order_attempts": 1582,
      "valid_answers": 1582,
      "invalid_answers": 0,
      "samples_with_at_least_two_valid_answers": 791,
      "samples_all_valid_same_source_index": 744,
      "all_valid_same_source_index_fraction": 0.9405815423514539,
      "valid_order_pairs": 791,
      "invalid_order_pairs": 0,
      "same_source_index_pairs": 744,
      "same_box_pairs": 747,
      "valid_source_index_agreement": 0.9405815423514539,
      "valid_box_agreement": 0.9443742098609356,
      "baseline_valid_pairs": 791,
      "baseline_same_source_index": 744,
      "baseline_valid_agreement": 0.9405815423514539,
      "primary_result": "original source order; no vote or fallback",
      "interpretation": "descriptive consistency; source samples need not be independent; orders/pairs are correlated"
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json"
  },
  {
    "metric_id": "permutation_extra_orders_requested",
    "value": 1,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json"
  }
]
```

### 分析
真实exit0/完成标记，1766 unique索引/ID、冻结框、两次映射/回复EOS/实际grid/IoU逐行核验通过。原顺序choice/response/EOS/IoU与既有step4041基线逐例完全一致，全量mIoU.718586281701126，多框.6717855957127017。1582回复全有效，791题744同source index(94.0582%)，747同bbox(94.4374%)；47换index中3仅重复框索引变化。换序修复7例Acc50错误、损害14例，交换后全量mIoU.7155103189382463/Acc50.782559456398641。原顺序保持主结果、未投票，相关排列非新独立样本，单seed探索不作显著性或Reference因果声明。证据.pi/analysis/e014/selector-experiments-20261021/permutation_final_audit.json，47条变化样本及产物SHA已保存。

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### Claim 边界
暂停训练不自动恢复，不宣称完成4epoch。较旧模型数据、采样、预算同时变化，测试集又已反复探索，不是单因果或无偏泛化。只评测最新完整step4041，不选其它checkpoint。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-permutation-p1-20261020/managed_console.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
