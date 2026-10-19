# e014-selection-lora-step360-test1766-20261018 · 用户要求现在评测已完成累计5epoch的step360选择LoRA。复用上一轮1766完整冻结测试集（791多框），只改变selector-checkpoint

- 父 Run：`e014-selection-lora-resume72-total5epochs-20261018`
- 来源版本：2026-10-18T20:08:34
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户要求现在评测已完成累计5epoch的step360选择LoRA。复用上一轮1766完整冻结测试集（791多框），只改变selector-checkpoint到samples_00005760_step_000360，其余exact_instance画框/候选顺序/seed20260901/greedy16/EOS/vision4096/BF16 SDPA保持一致。与已有step72、原score及原生画框VQA逐例比较，不新增baseline推理，不训练或选择其他checkpoint。父训练实际exit0/metrics passed但管理工具64KiB截断导致external_dependency标记，保留该事实；本评测独立Run。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 命令：test ! -e /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json && test ! -L /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json && PYTHONPATH=. OMP_NUM_THREADS=1 /songzhengyue/miniconda3/envs/IPLoc/bin/python -m torch.distributed.run --standalone --nproc_per_node=8 tools/evaluate_candidate_vqa.py --manifest /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-score04-step200-eval1766-20261015T152856Z/inputs/manifest.json --manifest-sha256 8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d --predictions /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-score04-step200-eval1766-20261015T152856Z/payload/evaluation/predictions.jsonl --predictions-sha256 1a864fdce10f300ec53ddf2945b7e2d063c74280d7a750207dcff99a7ff76129 --model-path /defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct --output-dir /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/payload --expected-samples 1766 --expected-multi 791 --seed 20260901 --max-new-tokens 16 --vision-max-patch-tokens 4096 --prompt-variant exact_instance --draw-boxes --selector-checkpoint /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-resume72-total5epochs-20261018/payload/training/checkpoints/samples_00005760_step_000360 && cp /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/payload/metrics.json /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json && echo SURVEY_TOOL_RUN_COMPLETE
- 代码版本：53ab7653602f62ffc1d5c9dadfbefccf7ad67474
- 随机种子：20260901
- 配置：tools/evaluate_candidate_vqa.py (standalone CLI)
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json

## 结果
step360完整1766评测exit0，全部791多框回答有效。全量mIoU70.3153%、Acc50 76.6138%；较step72提升0.3546pp/净增7命中，较原score提升1.1457pp/净增19命中。多框mIoU63.7329%，Oracle75.8440%。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "candidate_vqa",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "evaluated_samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "world_size",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "vqa_samples",
    "value": 791,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "all",
    "value": {
      "samples": 1766,
      "vqa_iou_mean": 0.7031528163827832,
      "vqa_iou_acc50": 0.7661381653454133,
      "score_iou_mean": 0.6916960157722533,
      "score_iou_acc50": 0.7553793884484711,
      "first_iou_mean": 0.656632485224866,
      "first_iou_acc50": 0.7151755379388448,
      "oracle_iou_mean": 0.7573992982137026,
      "oracle_iou_acc50": 0.8306908267270668,
      "valid_vqa_answers": 791,
      "invalid_vqa_answers": 0,
      "improves_score": 83,
      "worsens_score": 57,
      "fixes_score_miss": 65,
      "breaks_score_hit": 46,
      "oracle_hit_samples": 1467,
      "vqa_hit_given_oracle_hit": 0.9222903885480572
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "multi",
    "value": {
      "samples": 791,
      "vqa_iou_mean": 0.6373285795910921,
      "vqa_iou_acc50": 0.683944374209861,
      "score_iou_mean": 0.6117499324631576,
      "score_iou_acc50": 0.6599241466498104,
      "first_iou_mean": 0.5334665001664629,
      "first_iou_acc50": 0.5701643489254109,
      "oracle_iou_mean": 0.7584401938937492,
      "oracle_iou_acc50": 0.8280657395701644,
      "valid_vqa_answers": 791,
      "invalid_vqa_answers": 0,
      "improves_score": 83,
      "worsens_score": 57,
      "fixes_score_miss": 65,
      "breaks_score_hit": 46,
      "oracle_hit_samples": 655,
      "vqa_hit_given_oracle_hit": 0.8259541984732824
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "by_dataset",
    "value": {
      "GOT10k": {
        "samples": 180,
        "vqa_iou_mean": 0.8279267235444414,
        "vqa_iou_acc50": 0.9,
        "score_iou_mean": 0.7959036041152275,
        "score_iou_acc50": 0.8611111111111112,
        "first_iou_mean": 0.782188525520559,
        "first_iou_acc50": 0.85,
        "oracle_iou_mean": 0.8462972143842374,
        "oracle_iou_acc50": 0.9222222222222223,
        "valid_vqa_answers": 51,
        "invalid_vqa_answers": 0,
        "improves_score": 9,
        "worsens_score": 3,
        "fixes_score_miss": 9,
        "breaks_score_hit": 2,
        "oracle_hit_samples": 166,
        "vqa_hit_given_oracle_hit": 0.9759036144578314
      },
      "LaSOT": {
        "samples": 600,
        "vqa_iou_mean": 0.6644908227436466,
        "vqa_iou_acc50": 0.7466666666666667,
        "score_iou_mean": 0.6537116103330052,
        "score_iou_acc50": 0.7366666666666667,
        "first_iou_mean": 0.625383400920118,
        "first_iou_acc50": 0.7,
        "oracle_iou_mean": 0.7167223918508266,
        "oracle_iou_acc50": 0.8083333333333333,
        "valid_vqa_answers": 246,
        "invalid_vqa_answers": 0,
        "improves_score": 28,
        "worsens_score": 19,
        "fixes_score_miss": 22,
        "breaks_score_hit": 16,
        "oracle_hit_samples": 485,
        "vqa_hit_given_oracle_hit": 0.9237113402061856
      },
      "TAO": {
        "samples": 986,
        "vqa_iou_mean": 0.7039011864582227,
        "vqa_iou_acc50": 0.7535496957403651,
        "score_iou_mean": 0.6957865607639502,
        "score_iou_acc50": 0.7474645030425964,
        "first_iou_mean": 0.652727174200144,
        "first_iou_acc50": 0.6997971602434077,
        "oracle_iou_mean": 0.7659231510605866,
        "oracle_iou_acc50": 0.8275862068965517,
        "valid_vqa_answers": 494,
        "invalid_vqa_answers": 0,
        "improves_score": 46,
        "worsens_score": 35,
        "fixes_score_miss": 34,
        "breaks_score_hit": 28,
        "oracle_hit_samples": 816,
        "vqa_hit_given_oracle_hit": 0.9105392156862745
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "source_manifest_sha256",
    "value": "8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "source_predictions_sha256",
    "value": "1a864fdce10f300ec53ddf2945b7e2d063c74280d7a750207dcff99a7ff76129",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "prompt_sha256",
    "value": "3a67c77b2e548f255f1b891ece30a5ab3d42fa527958fac9f868aa8cfe88a27f",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "prompt_variant",
    "value": "exact_instance",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "image_presentation",
    "value": "outlined_numbered",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "selector",
    "value": "selection_lora_bfloat16",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "selector_checkpoint",
    "value": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-resume72-total5epochs-20261018/payload/training/checkpoints/samples_00005760_step_000360",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "candidate_order",
    "value": "source",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "settings",
    "value": {
      "seed": 20260901,
      "max_new_tokens": 16,
      "vision_max_patch_tokens": 4096,
      "do_sample": false,
      "require_eos": true
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json"
  }
]
```

### 分析
21:41:06 managed complete成功。1766唯一ID/索引与固定候选GT重算、791合法VQA/964单框/11无候选、1582原图及渲染SHA核验通过；渲染与step72/native完全一致，模型step360 SHA/快照/提示词/参数已核。全量mIoU step72 69.9607→step360 70.3153（+0.3546pp）；Acc50 76.2174→76.6138（净增7）。多框mIoU62.9412→63.7329。对step72选择改变75：28 IoU改善/25损害/22持平，25命中修复/18损害；对原score83改善/57损害，65修复/46损害；对native76改善/30损害，70修复/20损害。全量原score69.1696、native67.8265、Oracle75.7399，仍差Oracle5.4246pp。分集GOT82.5101→82.7927，LaSOT66.4820→66.4491，TAO69.7865→70.3901。仅小幅且分集不一致的改善。完整证据.pi/analysis/e014/selection-sft/test1766_step360_audit.json。

### 局限
管理工具将17项指标保存为辅助指标，未登记为Experiment主指标，不升级Claim。测试集重复探索且单seed、未检验显著性，不能称无偏独立测试或稳定泛化；生成器历史同视频暴露仍存在。训练loss大幅下降不能替代测试指标。无额外训练/评测/选checkpoint，父管理失败记录保留。

### Claim 边界
训练数据来源没有新增评测原视频重叠，但固定生成器过去曾见部分同源视频，不能宣称整链无泄漏泛化。无TAO训练来源，属选择器诊断。保持GRPO停止。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step360-test1766-20261018/managed_console.log

### 审核入口
.pi/analysis/e014/selection-sft/test1766_step360_audit.json

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
