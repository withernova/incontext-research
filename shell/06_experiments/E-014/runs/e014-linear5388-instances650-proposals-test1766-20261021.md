# e014-linear5388-instances650-proposals-test1766-20261021 · 用户明确要求测试固定三框checkpoint的proposal。固定父Run最终线性LR step5388选择器，在同1766例上将当前step200候选替换为

- 父 Run：`e014-selector-linear-decay4041-to5388-eval1766-20261021`
- 来源版本：2026-10-21T13:39:45
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户明确要求测试固定三框checkpoint的proposal。固定父Run最终线性LR step5388选择器，在同1766例上将当前step200候选替换为instances650历史冻结三框候选；先核对同Reference/Query图像和标注，再做一次全量评测。只改proposal来源，不训练，不做并集或新checkpoint搜索。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户明确要求测试固定三框checkpoint的proposal。固定父Run最终线性LR step5388选择器，在同1766例上将当前step200候选替换为instances650历史冻结三框候选；先核对同Reference/Query图像和标注，再做一次全量评测。只改proposal来源，不训练，不做并集或新checkpoint搜索。 selector BF16/SDPA/r8alpha16/greedy16/EOS/vision4096/seed20260901/8GPU/exact_instance无框两张全图与父Run一致；无score输入/无QueryGT输入。复用已部署clean7caae090，无源码修改或重新部署。历史proposal生成NF4/SDPA/greedy192/vision4096/seed20260901，原prompt focus-multi3-instance-search-v1，Run lineage已核step650。首次只读图像审计90秒超时，未形成成功证据、无模型执行；同Run受管CPU输入核验后才启动VQA。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'b9d92fd711f80c1dd806fc1079b4a6f36da54748d39cb734a9e001ab814a218a'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：7caae090351c9c71ce65fd8c98a0bbbbb1825bc6
- 随机种子：20260901
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "candidate_vqa",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/metrics.json"
  },
  {
    "metric_id": "evaluated_samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/metrics.json"
  },
  {
    "metric_id": "world_size",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/metrics.json"
  },
  {
    "metric_id": "vqa_samples",
    "value": 1765,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/metrics.json"
  },
  {
    "metric_id": "all",
    "value": {
      "samples": 1766,
      "vqa_iou_mean": 0.7132368712227971,
      "vqa_iou_acc50": 0.7808607021517554,
      "score_iou_mean": 0.6929771413460712,
      "score_iou_acc50": 0.7565118912797282,
      "first_iou_mean": 0.6936630966970494,
      "first_iou_acc50": 0.7570781426953568,
      "oracle_iou_mean": 0.7621490161770924,
      "oracle_iou_acc50": 0.840317100792752,
      "valid_vqa_answers": 1765,
      "invalid_vqa_answers": 0,
      "improves_score": 105,
      "worsens_score": 61,
      "fixes_score_miss": 77,
      "breaks_score_hit": 34,
      "oracle_hit_samples": 1484,
      "vqa_hit_given_oracle_hit": 0.9292452830188679
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/metrics.json"
  },
  {
    "metric_id": "multi",
    "value": {
      "samples": 1765,
      "vqa_iou_mean": 0.7136409714331217,
      "vqa_iou_acc50": 0.7813031161473087,
      "score_iou_mean": 0.693369762955899,
      "score_iou_acc50": 0.7569405099150142,
      "first_iou_mean": 0.6940561069501356,
      "first_iou_acc50": 0.7575070821529745,
      "oracle_iou_mean": 0.7625808286508472,
      "oracle_iou_acc50": 0.8407932011331445,
      "valid_vqa_answers": 1765,
      "invalid_vqa_answers": 0,
      "improves_score": 105,
      "worsens_score": 61,
      "fixes_score_miss": 77,
      "breaks_score_hit": 34,
      "oracle_hit_samples": 1484,
      "vqa_hit_given_oracle_hit": 0.9292452830188679
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/metrics.json"
  },
  {
    "metric_id": "by_dataset",
    "value": {
      "GOT10k": {
        "samples": 180,
        "vqa_iou_mean": 0.8177044985855059,
        "vqa_iou_acc50": 0.9,
        "score_iou_mean": 0.8082437952622664,
        "score_iou_acc50": 0.8888888888888888,
        "first_iou_mean": 0.8082437952622664,
        "first_iou_acc50": 0.8888888888888888,
        "oracle_iou_mean": 0.849528949210067,
        "oracle_iou_acc50": 0.9388888888888889,
        "valid_vqa_answers": 180,
        "invalid_vqa_answers": 0,
        "improves_score": 4,
        "worsens_score": 1,
        "fixes_score_miss": 3,
        "breaks_score_hit": 1,
        "oracle_hit_samples": 169,
        "vqa_hit_given_oracle_hit": 0.9585798816568047
      },
      "LaSOT": {
        "samples": 600,
        "vqa_iou_mean": 0.678549305159281,
        "vqa_iou_acc50": 0.7616666666666667,
        "score_iou_mean": 0.6615607811338836,
        "score_iou_acc50": 0.7416666666666667,
        "first_iou_mean": 0.6606670920191018,
        "first_iou_acc50": 0.74,
        "oracle_iou_mean": 0.7274794815973005,
        "oracle_iou_acc50": 0.8266666666666667,
        "valid_vqa_answers": 600,
        "invalid_vqa_answers": 0,
        "improves_score": 32,
        "worsens_score": 24,
        "fixes_score_miss": 22,
        "breaks_score_hit": 10,
        "oracle_hit_samples": 496,
        "vqa_hit_given_oracle_hit": 0.9213709677419355
      },
      "TAO": {
        "samples": 986,
        "vqa_iou_mean": 0.7152737542986778,
        "vqa_iou_acc50": 0.77079107505071,
        "score_iou_mean": 0.6910520079002231,
        "score_iou_acc50": 0.7413793103448276,
        "first_iou_mean": 0.6928244324627959,
        "first_iou_acc50": 0.7434077079107505,
        "oracle_iou_mean": 0.767294384130375,
        "oracle_iou_acc50": 0.8306288032454361,
        "valid_vqa_answers": 985,
        "invalid_vqa_answers": 0,
        "improves_score": 69,
        "worsens_score": 36,
        "fixes_score_miss": 52,
        "breaks_score_hit": 23,
        "oracle_hit_samples": 819,
        "vqa_hit_given_oracle_hit": 0.927960927960928
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/metrics.json"
  },
  {
    "metric_id": "source_manifest_sha256",
    "value": "8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/metrics.json"
  },
  {
    "metric_id": "source_predictions_sha256",
    "value": "83fbe295158970c37d56ba9caa7750e538235b97d3fd3d364f3cd20c73d77b4b",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/metrics.json"
  },
  {
    "metric_id": "prompt_sha256",
    "value": "b737f254c6c86215fa009600eccad51ac741cb46db6e7188aacfe3f390f7f6f2",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/metrics.json"
  },
  {
    "metric_id": "prompt_variant",
    "value": "exact_instance",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/metrics.json"
  },
  {
    "metric_id": "image_presentation",
    "value": "original",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/metrics.json"
  },
  {
    "metric_id": "selector",
    "value": "selection_lora_bfloat16",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/metrics.json"
  },
  {
    "metric_id": "selector_checkpoint",
    "value": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-linear-decay4041-to5388-eval1766-20261021/payload/training/checkpoints/samples_00086208_step_005388",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/metrics.json"
  },
  {
    "metric_id": "candidate_order",
    "value": "source",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/metrics.json"
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
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/metrics.json"
  }
]
```

### 分析
固定linear5388同一选择器、同1766图像与标注、seed20260901和完整推理快照，仅将step200候选替换为instances650冻结三框候选。真实exit0/marker，3532图像路径SHA匹配；1766逐例ID/原顺序/严格编号EOS/IoU及各分组指标重算通过。全量mIoU .7194462334134393→.7132368712227971（-0.620936pp），Acc50 .7859569648924122→.7808607021517554（-0.509626pp；1388→1379命中），修复49/损害58。Oracle mIoU .7573992982137026→.7621490161770924（+0.474972pp），Oracle命中1467→1484；候选可命中但最终未选中79→105，因此新增覆盖未转化为整体提升。新增覆盖62例实际命中38；丢覆盖45例中原有36命中；双方都覆盖1422例修复11/损害22。旧单框964 mIoU76.518773→75.887457%，旧多框791 67.370554→66.619238%，旧空11新增1命中。LaSOT mIoU67.818107→67.854931%，GOT82.697259→81.770450%，TAO72.492732→71.527375%；净少9命中全部来自TAO。实际VQA调用791→1765，新1765回答全有效、另1空候选计零。直接替换本次不改善；结果支持候选覆盖与选择均仍有缺口，不能证明数据集极限。

### 局限
单seed、同一反复探索测试集、固定现有selector而非为新候选重训。历史生成器checkpoint、prompt和生成契约随候选源一起变化；历史逐例EOS证据缺失，不能单独归因于checkpoint或固定三框要求。候选条件命中集合变化，不能由误选增加断言selector通用能力下降。未执行并集或新增训练；无显著性结论，不提升Claim或Solid标签。

### Claim 边界
只测固定选择器对两组冻结proposal的效果，不隔离生成器checkpoint与prompt因果。历史proposal无逐例EOS证据保留限制。单seed及已反复探索的测试集，不升Claim。

### 产物索引
.pi/analysis/e014/instances650-selector-20261021/spec.json
.pi/analysis/e014/instances650-selector-20261021/final_audit.json
.pi/analysis/e014/instances650-selector-20261021/complete_receipt.json
shell/06_experiments/E-014/执行对照-20261021.md
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/managed_console.log
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-linear5388-instances650-proposals-test1766-20261021/payload/evaluation/predictions.jsonl

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
