# e015-multishot-data-preparation-r5-20261021 · 复用已完成六份清单（训练10175、测试1728），重核同Query/GT/索引和SHA；仅复核被排除记录并记录原因。GRPO中保留原始行与奖励，对无效中间参考

- 父 Run：`e015-multishot-data-preparation-r4-20261021`
- 来源版本：2026-10-21T19:36:35
- 状态：analysis_pending
- Workspace：03

## 本次任务
复用已完成六份清单（训练10175、测试1728），重核同Query/GT/索引和SHA；仅复核被排除记录并记录原因。GRPO中保留原始行与奖励，对无效中间参考帧选择同轨迹最近的有效帧，不裁剪标注，逐例记录nominal→actual和原始标注SHA。继续用户授权的E015。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：复用父Run六份已生成清单，不重做全量逐图扫描；逐条核固定Query/GT与索引，重新解释349训练/38测试排除记录；原GRPO行不改，只有无效中间支持帧选同轨迹最近有效帧，保存替换及图像/标注SHA。无GPU或性能结果。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'65bde882b236eb713a6e897a07b1083b9e0076a37013fc48b233bf6750879abc'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：dcdf731dfa0e6d672ee8a684e4c0e23e1f7175c8
- 随机种子：20260901
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/metrics.json"
  },
  {
    "metric_id": "source",
    "value": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-009/E009-real-focus-data/manifests/train_only_1shot_focus_valid10524.json",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/metrics.json"
  },
  {
    "metric_id": "source_sha256",
    "value": "c10e5b45f31c81d93d9a792b23b987908008e1f949295043e1487b393c662dc0",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/metrics.json"
  },
  {
    "metric_id": "eval_source",
    "value": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/_shared/manifests/iploc_1shot_frozen_eval_v1.json",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/metrics.json"
  },
  {
    "metric_id": "eval_source_sha256",
    "value": "48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/metrics.json"
  },
  {
    "metric_id": "parent_manifest_run",
    "value": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r4-20261021",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/metrics.json"
  },
  {
    "metric_id": "outputs",
    "value": {
      "train_1shot.json": {
        "samples": 10175,
        "sha256": "11c395efb4f2ba18953c7dc50a0f2f873a95ff83c89b9419ddd5908f9356def1",
        "parent_sha256": "11c395efb4f2ba18953c7dc50a0f2f873a95ff83c89b9419ddd5908f9356def1",
        "datasets": {
          "GOT10k": 9009,
          "LaSOT": 675,
          "TAO": 491
        }
      },
      "train_2shot.json": {
        "samples": 10175,
        "sha256": "636a6072217a55236f7c9d7ed627b250cc6674abfcaadef475f97e3ad5240d9d",
        "parent_sha256": "636a6072217a55236f7c9d7ed627b250cc6674abfcaadef475f97e3ad5240d9d",
        "datasets": {
          "GOT10k": 9009,
          "LaSOT": 675,
          "TAO": 491
        }
      },
      "train_4shot.json": {
        "samples": 10175,
        "sha256": "430b2b5b028cbb6aaf8b240b9d92162c6c07bb4ad64af714074d64038bf747d6",
        "parent_sha256": "430b2b5b028cbb6aaf8b240b9d92162c6c07bb4ad64af714074d64038bf747d6",
        "datasets": {
          "GOT10k": 9009,
          "LaSOT": 675,
          "TAO": 491
        }
      },
      "test_1shot.json": {
        "samples": 1728,
        "sha256": "af37df520b6fb71b16bb55f86fee0eb149aa63f3a67e45b067eb1d9d08149463",
        "parent_sha256": "af37df520b6fb71b16bb55f86fee0eb149aa63f3a67e45b067eb1d9d08149463",
        "datasets": {
          "LaSOT": 583,
          "GOT10k": 180,
          "TAO": 965
        }
      },
      "test_2shot.json": {
        "samples": 1728,
        "sha256": "8cb4bbb7737ac6eed40a9e0a7158eb331d31815064e761a07b9d4497d25d4e25",
        "parent_sha256": "8cb4bbb7737ac6eed40a9e0a7158eb331d31815064e761a07b9d4497d25d4e25",
        "datasets": {
          "LaSOT": 583,
          "GOT10k": 180,
          "TAO": 965
        }
      },
      "test_4shot.json": {
        "samples": 1728,
        "sha256": "2841023464a4424cc014f6bf8c5988c5891c2942ab4795b4e2667f058d403361",
        "parent_sha256": "2841023464a4424cc014f6bf8c5988c5891c2942ab4795b4e2667f058d403361",
        "datasets": {
          "LaSOT": 583,
          "GOT10k": 180,
          "TAO": 965
        }
      },
      "pilot_1shot.json": {
        "samples": 8,
        "sha256": "0a16cfc8c5a3868b3828b2945b853f8d3420aabb2f914a46470c4e54cff902d8"
      },
      "pilot_2shot.json": {
        "samples": 8,
        "sha256": "8930294598321c1194f474e64b63d8d0590796414a969a09e366afa1f530378e"
      },
      "pilot_4shot.json": {
        "samples": 8,
        "sha256": "0c826fe2a862a15ba3d95bb2deafa63a67cc4e2e93c09e8ce95524e968d0f57a"
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/metrics.json"
  },
  {
    "metric_id": "rejected",
    "value": [
      {
        "split": "train",
        "index": 146,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000147",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 147,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000148",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 148,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000149",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 185,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000186",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 220,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000221",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 221,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000222",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 222,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000223",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 223,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000224",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 255,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000256",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 256,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000257",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 257,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000258",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 265,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000266",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 266,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000267",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 267,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000268",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 268,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000269",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 269,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000270",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 272,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000273",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 348,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000349",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 349,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000350",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 350,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000351",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 351,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000352",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 352,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000353",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 353,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000354",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 354,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000355",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 414,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000415",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 430,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000431",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 431,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000432",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 432,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000433",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 522,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000523",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 523,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000524",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 524,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000525",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 525,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000526",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 526,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000527",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 527,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000528",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 563,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000564",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 564,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000565",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 565,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000566",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 566,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000567",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 567,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000568",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 568,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000569",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 569,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000570",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 570,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000571",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 571,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000572",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 572,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000573",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 573,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000574",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 574,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000575",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 575,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000576",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 576,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000577",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 577,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000578",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 578,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000579",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 579,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000580",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 580,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000581",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 581,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000582",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 582,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000583",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 583,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000584",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 584,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000585",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 585,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000586",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 586,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000587",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 587,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000588",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 604,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000605",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 605,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000606",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 606,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000607",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 607,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000608",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 608,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000609",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 626,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000627",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 627,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000628",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 628,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000629",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 629,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000630",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 630,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000631",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 631,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000632",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 632,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000633",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 633,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000634",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 634,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000635",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 635,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000636",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 636,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000637",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 637,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000638",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 702,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000703",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 707,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000708",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 715,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000716",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 717,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000718",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 857,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000858",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 980,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_000981",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1005,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001006",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1023,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001024",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1024,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001025",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1025,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001026",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1026,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001027",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1027,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001028",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1072,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001073",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1073,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001074",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1093,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001094",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1209,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001210",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1285,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001286",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1298,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001299",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1393,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001394",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1394,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001395",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1395,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001396",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1396,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001397",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1414,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001415",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1415,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001416",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1416,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001417",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1417,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001418",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1418,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001419",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1419,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001420",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1420,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001421",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1421,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001422",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1561,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001562",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1617,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001618",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1618,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001619",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1664,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001665",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_001665/00000140.jpg",
            "box": [
              -1.0,
              -1.0,
              -2.0,
              -2.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 1728,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001729",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1729,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001730",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1730,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001731",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1733,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001734",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1734,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001735",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1735,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001736",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1736,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001737",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1737,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001738",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1738,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001739",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1781,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001782",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1796,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001797",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1866,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001867",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_001867/00000054.jpg",
            "box": [
              -1.0,
              -1.0,
              -2.0,
              -2.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 1877,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001878",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1878,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001879",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1879,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001880",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1940,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001941",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1941,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001942",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1942,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001943",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1943,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001944",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1969,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001970",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1970,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001971",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1971,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001972",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1972,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001973",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1973,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001974",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1974,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001975",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1975,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001976",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 1976,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_001977",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 2219,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_002220",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 2220,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_002221",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 2744,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_002745",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 2795,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_002796",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 2809,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_002810",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 2810,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_002811",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 2834,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_002835",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 2914,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_002915",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 2925,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_002926",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3022,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003023",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3032,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003033",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3049,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003050",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3050,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003051",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3051,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003052",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3052,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003053",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3080,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003081",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3081,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003082",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3099,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003100",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3100,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003101",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3101,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003102",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3102,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003103",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3103,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003104",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3104,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003105",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3105,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003106",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3106,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003107",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3107,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003108",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3108,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003109",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3109,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003110",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3125,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003126",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3126,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003127",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3181,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003182",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3182,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003183",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3183,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003184",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3306,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003307",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3321,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003322",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3364,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003365",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3385,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003386",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3386,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003387",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3387,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003388",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3424,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003425",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3524,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003525",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3525,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003526",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3526,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003527",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3576,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003577",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3577,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003578",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3578,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003579",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3579,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003580",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3580,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003581",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3602,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003603",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3603,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003604",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3604,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003605",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3770,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003771",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3773,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003774",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3905,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003906",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 3906,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_003907",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4670,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004672",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4701,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004703",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4703,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004705",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4704,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004706",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4705,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004707",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4736,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004738",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4817,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004819",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4818,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004820",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4819,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004821",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4820,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004822",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4821,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004823",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4822,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004824",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4823,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004825",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4832,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004834",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4833,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004835",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4834,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004836",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4835,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004837",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4836,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004838",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4837,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004839",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4838,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004840",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4839,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004841",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4927,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004929",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4928,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004930",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4929,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004931",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4930,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004932",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 4973,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_004975",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5036,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005038",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5037,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005039",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5038,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005040",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5039,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005041",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5040,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005042",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5041,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005043",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5042,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005044",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5200,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005202",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5201,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005203",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5202,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005204",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5203,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005205",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5204,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005206",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5205,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005207",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5206,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005208",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5380,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005382",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5381,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005383",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5382,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005384",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5383,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005385",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5384,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005386",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5385,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005387",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5386,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005388",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5402,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005404",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5403,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005405",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5416,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005418",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5417,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005419",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5514,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005516",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5518,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005520",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5519,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005521",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5520,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005522",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5581,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005583",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5582,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005584",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 5583,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_005585",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 6215,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_006217",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 6836,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_006838",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 6837,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_006839",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 6838,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_006840",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 6839,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_006841",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 6840,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_006842",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 6841,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_006843",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 6842,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_006844",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 7084,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_007086",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_007086/00000073.jpg",
            "box": [
              374.0,
              107.0,
              718.0,
              763.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 7221,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_007223",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 7222,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_007224",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 7223,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_007225",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 7224,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_007226",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 7353,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_007355",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 7354,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_007356",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 7355,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_007357",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 7356,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_007358",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 7357,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_007359",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 7608,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_007610",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_007610/00000147.jpg",
            "box": [
              -1.0,
              -1.0,
              -2.0,
              -2.0
            ],
            "size": [
              1920,
              1080
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 7643,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_007645",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_007645/00000050.jpg",
            "box": [
              -1.0,
              -1.0,
              -2.0,
              -2.0
            ],
            "size": [
              1920,
              1080
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 7760,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_007762",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 7824,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_007826",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 7972,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_007974",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 7973,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_007975",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 7983,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_007985",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 7984,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_007986",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8031,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008033",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8032,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008034",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8084,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008086",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8085,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008087",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8126,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008128",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8129,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008131",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8130,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008132",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8260,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008262",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8261,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008263",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8262,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008264",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8263,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008265",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8268,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008270",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8292,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008294",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8293,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008295",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8294,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008296",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8349,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008351",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8350,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008352",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8354,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008356",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8366,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008368",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008368/00000001.jpg",
            "box": [
              107.0,
              -1.0,
              354.0,
              252.0
            ],
            "size": [
              640,
              480
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 8384,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008386",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8385,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008387",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8386,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008388",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8422,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008424",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8423,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008425",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8424,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008426",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8425,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008427",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8486,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008488",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8619,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008621",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8621,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008623",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008623/00000001.jpg",
            "box": [
              1066.0,
              315.0,
              1546.0,
              549.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008623/00000027.jpg",
            "box": [
              1003.0,
              389.0,
              1402.0,
              640.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 8623,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008625",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008625/00000001.jpg",
            "box": [
              252.0,
              237.0,
              546.0,
              446.0
            ],
            "size": [
              640,
              360
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008625/00000027.jpg",
            "box": [
              393.0,
              95.0,
              598.0,
              471.0
            ],
            "size": [
              640,
              360
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008625/00000054.jpg",
            "box": [
              138.0,
              172.0,
              421.0,
              440.0
            ],
            "size": [
              640,
              360
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008625/00000080.jpg",
            "box": [
              241.0,
              185.0,
              721.0,
              456.0
            ],
            "size": [
              640,
              360
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008625/00000081.jpg",
            "box": [
              237.0,
              209.0,
              654.0,
              456.0
            ],
            "size": [
              640,
              360
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "train",
        "index": 8624,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008626",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008626/00000001.jpg",
            "box": [
              271.0,
              221.0,
              516.0,
              428.0
            ],
            "size": [
              640,
              360
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008626/00000027.jpg",
            "box": [
              231.0,
              192.0,
              660.0,
              433.0
            ],
            "size": [
              640,
              360
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008626/00000054.jpg",
            "box": [
              281.0,
              169.0,
              468.0,
              479.0
            ],
            "size": [
              640,
              360
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008626/00000080.jpg",
            "box": [
              227.0,
              180.0,
              444.0,
              443.0
            ],
            "size": [
              640,
              360
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008626/00000081.jpg",
            "box": [
              216.0,
              216.0,
              430.0,
              450.0
            ],
            "size": [
              640,
              360
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "train",
        "index": 8625,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008627",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008627/00000001.jpg",
            "box": [
              144.0,
              142.0,
              324.0,
              457.0
            ],
            "size": [
              640,
              360
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008627/00000027.jpg",
            "box": [
              176.0,
              114.0,
              422.0,
              456.0
            ],
            "size": [
              640,
              360
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008627/00000053.jpg",
            "box": [
              166.0,
              19.0,
              305.0,
              375.0
            ],
            "size": [
              640,
              360
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008627/00000079.jpg",
            "box": [
              0.0,
              5.0,
              106.0,
              375.0
            ],
            "size": [
              640,
              360
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008627/00000080.jpg",
            "box": [
              0.0,
              5.0,
              106.0,
              375.0
            ],
            "size": [
              640,
              360
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "train",
        "index": 8626,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008628",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008628/00000001.jpg",
            "box": [
              952.0,
              665.0,
              1532.0,
              1079.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008628/00000027.jpg",
            "box": [
              651.0,
              754.0,
              1290.0,
              1079.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008628/00000054.jpg",
            "box": [
              1196.0,
              644.0,
              1639.0,
              864.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008628/00000080.jpg",
            "box": [
              1371.0,
              583.0,
              1655.0,
              797.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008628/00000081.jpg",
            "box": [
              1371.0,
              583.0,
              1655.0,
              797.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "train",
        "index": 8627,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008629",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008629/00000001.jpg",
            "box": [
              966.0,
              625.0,
              1229.0,
              900.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008629/00000027.jpg",
            "box": [
              963.0,
              546.0,
              1176.0,
              1016.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008629/00000054.jpg",
            "box": [
              746.0,
              611.0,
              943.0,
              785.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 8628,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008630",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008630/00000001.jpg",
            "box": [
              1284.0,
              761.0,
              1645.0,
              1079.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008630/00000031.jpg",
            "box": [
              0.0,
              568.0,
              356.0,
              1059.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008630/00000060.jpg",
            "box": [
              860.0,
              735.0,
              1443.0,
              1079.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008630/00000090.jpg",
            "box": [
              1245.0,
              571.0,
              1665.0,
              928.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008630/00000091.jpg",
            "box": [
              1245.0,
              565.0,
              1680.0,
              896.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "train",
        "index": 8630,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008632",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008632/00000001.jpg",
            "box": [
              1082.0,
              643.0,
              1340.0,
              854.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008632/00000027.jpg",
            "box": [
              854.0,
              619.0,
              1322.0,
              968.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008632/00000053.jpg",
            "box": [
              641.0,
              629.0,
              1446.0,
              909.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008632/00000079.jpg",
            "box": [
              840.0,
              646.0,
              1754.0,
              899.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008632/00000080.jpg",
            "box": [
              862.0,
              646.0,
              1757.0,
              895.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "train",
        "index": 8631,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008633",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008633/00000001.jpg",
            "box": [
              199.0,
              666.0,
              425.0,
              817.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008633/00000031.jpg",
            "box": [
              155.0,
              661.0,
              554.0,
              843.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008633/00000060.jpg",
            "box": [
              519.0,
              679.0,
              772.0,
              864.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008633/00000090.jpg",
            "box": [
              586.0,
              635.0,
              977.0,
              982.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008633/00000091.jpg",
            "box": [
              603.0,
              635.0,
              976.0,
              982.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "train",
        "index": 8632,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008634",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008634/00000001.jpg",
            "box": [
              409.0,
              165.0,
              1374.0,
              736.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008634/00000027.jpg",
            "box": [
              73.0,
              239.0,
              1496.0,
              744.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008634/00000054.jpg",
            "box": [
              0.0,
              227.0,
              1031.0,
              1056.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008634/00000080.jpg",
            "box": [
              414.0,
              182.0,
              1385.0,
              1021.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008634/00000081.jpg",
            "box": [
              406.0,
              182.0,
              1407.0,
              1022.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "train",
        "index": 8635,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008637",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008637/00000001.jpg",
            "box": [
              413.0,
              190.0,
              1579.0,
              794.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008637/00000034.jpg",
            "box": [
              512.0,
              613.0,
              991.0,
              936.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_008637/00000100.jpg",
            "box": [
              934.0,
              429.0,
              1330.0,
              668.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "train",
        "index": 8991,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008993",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 8992,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_008994",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 9025,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_009027",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 9056,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_009058",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_009058/00000001.jpg",
            "box": [
              763.0,
              375.0,
              950.0,
              834.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_009058/00000077.jpg",
            "box": [
              734.0,
              586.0,
              1016.0,
              893.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_009058/00000154.jpg",
            "box": [
              913.0,
              615.0,
              1084.0,
              828.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_009058/00000230.jpg",
            "box": [
              932.0,
              611.0,
              1213.0,
              836.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_009058/00000231.jpg",
            "box": [
              901.0,
              628.0,
              1212.0,
              840.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "train",
        "index": 9057,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_009059",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_009059/00000001.jpg",
            "box": [
              705.0,
              313.0,
              888.0,
              894.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_009059/00000067.jpg",
            "box": [
              463.0,
              277.0,
              686.0,
              1010.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_009059/00000134.jpg",
            "box": [
              728.0,
              578.0,
              1135.0,
              817.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_009059/00000200.jpg",
            "box": [
              1062.0,
              341.0,
              1364.0,
              880.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_009059/00000201.jpg",
            "box": [
              1051.0,
              356.0,
              1332.0,
              878.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "train",
        "index": 9184,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_009186",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/GOT10k/train/GOT-10k_Train_009186/00000048.jpg",
            "box": [
              952.0,
              645.0,
              1635.0,
              1086.0
            ],
            "size": [
              1920,
              1080
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 9212,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_009214",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 9227,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_009229",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 9228,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_009230",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 9333,
        "dataset": "GOT10k",
        "sequence": "GOT-10k_Train_009335",
        "reason": "frozen_test_identity_or_original_video_overlap"
      },
      {
        "split": "train",
        "index": 9547,
        "dataset": "LaSOT",
        "sequence": "drone-3",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/drone/drone-3/img/00001192.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 9582,
        "dataset": "LaSOT",
        "sequence": "gecko-17",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/gecko/gecko-17/img/00001264.jpg",
            "box": [
              470.0,
              60.0,
              481.0,
              129.0
            ],
            "size": [
              480,
              360
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 9588,
        "dataset": "LaSOT",
        "sequence": "gecko-5",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/gecko/gecko-5/img/00000834.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              202,
              360
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 9599,
        "dataset": "LaSOT",
        "sequence": "giraffe-15",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/giraffe/giraffe-15/img/00000494.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 9673,
        "dataset": "LaSOT",
        "sequence": "hippo-11",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/hippo/hippo-11/img/00001325.jpg",
            "box": [
              1215.0,
              57.0,
              1281.0,
              248.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/hippo/hippo-11/img/00001326.jpg",
            "box": [
              1215.0,
              57.0,
              1281.0,
              248.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "train",
        "index": 9721,
        "dataset": "LaSOT",
        "sequence": "lion-3",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/lion/lion-3/img/00000743.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              320,
              240
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 9735,
        "dataset": "LaSOT",
        "sequence": "lizard-16",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/lizard/lizard-16/img/00002783.jpg",
            "box": [
              509.0,
              640.0,
              767.0,
              721.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/lizard/lizard-16/img/00002784.jpg",
            "box": [
              509.0,
              640.0,
              767.0,
              721.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "train",
        "index": 9737,
        "dataset": "LaSOT",
        "sequence": "lizard-18",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/lizard/lizard-18/img/00000792.jpg",
            "box": [
              1119.0,
              464.0,
              1281.0,
              676.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 9753,
        "dataset": "LaSOT",
        "sequence": "microphone-15",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/microphone/microphone-15/img/00000662.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/microphone/microphone-15/img/00001322.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 9764,
        "dataset": "LaSOT",
        "sequence": "microphone-8",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/microphone/microphone-8/img/00003323.jpg",
            "box": [
              1265.0,
              187.0,
              1281.0,
              225.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "train",
        "index": 9927,
        "dataset": "LaSOT",
        "sequence": "tiger-11",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/tiger/tiger-11/img/00001129.jpg",
            "box": [
              451.0,
              69.0,
              481.0,
              115.0
            ],
            "size": [
              480,
              360
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/tiger/tiger-11/img/00001130.jpg",
            "box": [
              451.0,
              69.0,
              481.0,
              115.0
            ],
            "size": [
              480,
              360
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "train",
        "index": 9990,
        "dataset": "LaSOT",
        "sequence": "volleyball-14",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/volleyball/volleyball-14/img/00000353.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 9993,
        "dataset": "LaSOT",
        "sequence": "volleyball-17",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/volleyball/volleyball-17/img/00000377.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/volleyball/volleyball-17/img/00000752.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 9995,
        "dataset": "LaSOT",
        "sequence": "volleyball-19",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/volleyball/volleyball-19/img/00000489.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 9998,
        "dataset": "LaSOT",
        "sequence": "volleyball-3",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/volleyball/volleyball-3/img/00001368.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              640,
              360
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 9999,
        "dataset": "LaSOT",
        "sequence": "volleyball-4",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/volleyball/volleyball-4/img/00000372.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "train",
        "index": 10130,
        "dataset": "TAO",
        "sequence": "train/YFCC100M/v_e16e325327dd0974bda9bbd7a35118c",
        "reason": "KeyError",
        "detail": "'train/YFCC100M/v_e16e325327dd0974bda9bbd7a35118c'"
      },
      {
        "split": "train",
        "index": 10221,
        "dataset": "TAO",
        "sequence": "train/ArgoVerse/side_left_f9fa3960-537f-3151-a1a3-37a9c0d6d7f7",
        "reason": "KeyError",
        "detail": "'train/ArgoVerse/side_left_f9fa3960-537f-3151-a1a3-37a9c0d6d7f7'"
      },
      {
        "split": "train",
        "index": 10224,
        "dataset": "TAO",
        "sequence": "train/ArgoVerse/side_left_a6cab660-f086-3e2a-8ad9-7144f93f5b68",
        "reason": "KeyError",
        "detail": "'train/ArgoVerse/side_left_a6cab660-f086-3e2a-8ad9-7144f93f5b68'"
      },
      {
        "split": "train",
        "index": 10232,
        "dataset": "TAO",
        "sequence": "train/ArgoVerse/side_right_2c07fcda-6671-3ac0-ac23-4a232e0e031e",
        "reason": "KeyError",
        "detail": "'train/ArgoVerse/side_right_2c07fcda-6671-3ac0-ac23-4a232e0e031e'"
      },
      {
        "split": "train",
        "index": 10233,
        "dataset": "TAO",
        "sequence": "train/ArgoVerse/side_right_e8ce69b2-36ab-38e8-87a4-b9e20fee7fd2",
        "reason": "KeyError",
        "detail": "'train/ArgoVerse/side_right_e8ce69b2-36ab-38e8-87a4-b9e20fee7fd2'"
      },
      {
        "split": "train",
        "index": 10234,
        "dataset": "TAO",
        "sequence": "train/ArgoVerse/side_right_08a8b7f0-c317-3bdb-b3dc-b7c9b6d033e2",
        "reason": "KeyError",
        "detail": "'train/ArgoVerse/side_right_08a8b7f0-c317-3bdb-b3dc-b7c9b6d033e2'"
      },
      {
        "split": "train",
        "index": 10235,
        "dataset": "TAO",
        "sequence": "train/ArgoVerse/side_right_84c35ea7-1a99-3a0c-a3ea-c5915d68acbc",
        "reason": "KeyError",
        "detail": "'train/ArgoVerse/side_right_84c35ea7-1a99-3a0c-a3ea-c5915d68acbc'"
      },
      {
        "split": "train",
        "index": 10280,
        "dataset": "TAO",
        "sequence": "train/LaSOT/bus-19",
        "reason": "KeyError",
        "detail": "'train/LaSOT/bus-19'"
      },
      {
        "split": "test",
        "index": 163,
        "dataset": "LaSOT",
        "sequence": "electricfan-11",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/electricfan/electricfan-11/img/00001758.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "test",
        "index": 170,
        "dataset": "LaSOT",
        "sequence": "electricfan-18",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/electricfan/electricfan-18/img/00001862.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/electricfan/electricfan-18/img/00001863.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "test",
        "index": 178,
        "dataset": "LaSOT",
        "sequence": "electricfan-9",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/electricfan/electricfan-9/img/00001387.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              568,
              320
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/electricfan/electricfan-9/img/00001388.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              568,
              320
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "test",
        "index": 208,
        "dataset": "LaSOT",
        "sequence": "flag-3",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/flag/flag-3/img/00001903.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/flag/flag-3/img/00001904.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "test",
        "index": 215,
        "dataset": "LaSOT",
        "sequence": "fox-1",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/fox/fox-1/img/00000834.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/fox/fox-1/img/00001250.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/fox/fox-1/img/00001251.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "test",
        "index": 219,
        "dataset": "LaSOT",
        "sequence": "fox-14",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/fox/fox-14/img/00001525.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              480,
              360
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "test",
        "index": 220,
        "dataset": "LaSOT",
        "sequence": "fox-15",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/fox/fox-15/img/00001544.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              640,
              360
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/fox/fox-15/img/00002315.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              640,
              360
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/fox/fox-15/img/00002316.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              640,
              360
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "test",
        "index": 226,
        "dataset": "LaSOT",
        "sequence": "fox-20",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/fox/fox-20/img/00004182.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/fox/fox-20/img/00004183.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "test",
        "index": 227,
        "dataset": "LaSOT",
        "sequence": "fox-3",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/fox/fox-3/img/00002494.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              480,
              360
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/fox/fox-3/img/00002495.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              480,
              360
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "test",
        "index": 231,
        "dataset": "LaSOT",
        "sequence": "fox-8",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/fox/fox-8/img/00001050.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              480,
              360
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "test",
        "index": 238,
        "dataset": "LaSOT",
        "sequence": "frog-17",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/frog/frog-17/img/00002751.jpg",
            "box": [
              51.0,
              304.0,
              195.0,
              361.0
            ],
            "size": [
              480,
              360
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "test",
        "index": 263,
        "dataset": "LaSOT",
        "sequence": "hand-12",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/hand/hand-12/img/00002233.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "test",
        "index": 265,
        "dataset": "LaSOT",
        "sequence": "hand-15",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/hand/hand-15/img/00004121.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/hand/hand-15/img/00004122.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "test",
        "index": 285,
        "dataset": "LaSOT",
        "sequence": "hat-19",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/hat/hat-19/img/00000847.jpg",
            "box": [
              1.0,
              1.0,
              1.0,
              1.0
            ],
            "size": [
              480,
              360
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/hat/hat-19/img/00001694.jpg",
            "box": [
              1.0,
              1.0,
              1.0,
              1.0
            ],
            "size": [
              480,
              360
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "test",
        "index": 332,
        "dataset": "LaSOT",
        "sequence": "leopard-13",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/leopard/leopard-13/img/00002791.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              640,
              360
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "test",
        "index": 335,
        "dataset": "LaSOT",
        "sequence": "leopard-16",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/leopard/leopard-16/img/00002232.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          },
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/leopard/leopard-16/img/00002233.jpg",
            "box": [
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "query"
          }
        ]
      },
      {
        "split": "test",
        "index": 520,
        "dataset": "LaSOT",
        "sequence": "swing-14",
        "reason": "invalid_or_out_of_bounds_annotation",
        "invalid_annotations": [
          {
            "path": "/defaultShare/pubdata/LaSOT/LaSOT/swing/swing-14/img/00002563.jpg",
            "box": [
              230.0,
              569.0,
              671.0,
              721.0
            ],
            "size": [
              1280,
              720
            ],
            "role": "reference"
          }
        ]
      },
      {
        "split": "test",
        "index": 1044,
        "dataset": "TAO",
        "sequence": "val/BDD/b2715214-d38332ea",
        "reason": "KeyError",
        "detail": "'val/BDD/b2715214-d38332ea'"
      },
      {
        "split": "test",
        "index": 1056,
        "dataset": "TAO",
        "sequence": "val/BDD/b3a58c04-e89d17a2",
        "reason": "KeyError",
        "detail": "'val/BDD/b3a58c04-e89d17a2'"
      },
      {
        "split": "test",
        "index": 1087,
        "dataset": "TAO",
        "sequence": "val/BDD/b2ae0446-f456c162",
        "reason": "KeyError",
        "detail": "'val/BDD/b2ae0446-f456c162'"
      },
      {
        "split": "test",
        "index": 1091,
        "dataset": "TAO",
        "sequence": "val/BDD/b3121071-461523a5",
        "reason": "KeyError",
        "detail": "'val/BDD/b3121071-461523a5'"
      },
      {
        "split": "test",
        "index": 1095,
        "dataset": "TAO",
        "sequence": "val/BDD/b3e08585-1fcf0877",
        "reason": "KeyError",
        "detail": "'val/BDD/b3e08585-1fcf0877'"
      },
      {
        "split": "test",
        "index": 1167,
        "dataset": "TAO",
        "sequence": "val/YFCC100M/v_2c42b9d2c724ad2240a6c8bb28914f73",
        "reason": "KeyError",
        "detail": "'val/YFCC100M/v_2c42b9d2c724ad2240a6c8bb28914f73'"
      },
      {
        "split": "test",
        "index": 1170,
        "dataset": "TAO",
        "sequence": "val/ArgoVerse/side_left_21e37598-52d4-345c-8ef9-03ae19615d3d",
        "reason": "KeyError",
        "detail": "'val/ArgoVerse/side_left_21e37598-52d4-345c-8ef9-03ae19615d3d'"
      },
      {
        "split": "test",
        "index": 1172,
        "dataset": "TAO",
        "sequence": "val/ArgoVerse/side_left_5dc52355-0757-37c8-8d73-e930ee681de3",
        "reason": "KeyError",
        "detail": "'val/ArgoVerse/side_left_5dc52355-0757-37c8-8d73-e930ee681de3'"
      },
      {
        "split": "test",
        "index": 1173,
        "dataset": "TAO",
        "sequence": "val/ArgoVerse/side_left_033669d3-3d6b-3d3d-bd93-7985d86653ea",
        "reason": "KeyError",
        "detail": "'val/ArgoVerse/side_left_033669d3-3d6b-3d3d-bd93-7985d86653ea'"
      },
      {
        "split": "test",
        "index": 1175,
        "dataset": "TAO",
        "sequence": "val/ArgoVerse/side_left_de777454-df62-3d5a-a1ce-2edb5e5d4922",
        "reason": "KeyError",
        "detail": "'val/ArgoVerse/side_left_de777454-df62-3d5a-a1ce-2edb5e5d4922'"
      },
      {
        "split": "test",
        "index": 1178,
        "dataset": "TAO",
        "sequence": "val/ArgoVerse/side_left_6162d72f-2990-3a30-9bba-19bbd882985c",
        "reason": "KeyError",
        "detail": "'val/ArgoVerse/side_left_6162d72f-2990-3a30-9bba-19bbd882985c'"
      },
      {
        "split": "test",
        "index": 1179,
        "dataset": "TAO",
        "sequence": "val/ArgoVerse/side_left_45753856-4575-4575-4575-345754906624",
        "reason": "KeyError",
        "detail": "'val/ArgoVerse/side_left_45753856-4575-4575-4575-345754906624'"
      },
      {
        "split": "test",
        "index": 1183,
        "dataset": "TAO",
        "sequence": "val/ArgoVerse/side_left_11953248-1195-1195-1195-511954366464",
        "reason": "KeyError",
        "detail": "'val/ArgoVerse/side_left_11953248-1195-1195-1195-511954366464'"
      },
      {
        "split": "test",
        "index": 1184,
        "dataset": "TAO",
        "sequence": "val/ArgoVerse/side_left_4137e94a-c5da-38bd-ad06-6d57b24bccd0",
        "reason": "KeyError",
        "detail": "'val/ArgoVerse/side_left_4137e94a-c5da-38bd-ad06-6d57b24bccd0'"
      },
      {
        "split": "test",
        "index": 1186,
        "dataset": "TAO",
        "sequence": "val/ArgoVerse/side_left_10b8dee6-778f-33e4-a946-d842d2d9c3d7",
        "reason": "KeyError",
        "detail": "'val/ArgoVerse/side_left_10b8dee6-778f-33e4-a946-d842d2d9c3d7'"
      },
      {
        "split": "test",
        "index": 1192,
        "dataset": "TAO",
        "sequence": "val/ArgoVerse/side_right_6db21fda-80cd-3f85-b4a7-0aadeb14724d",
        "reason": "KeyError",
        "detail": "'val/ArgoVerse/side_right_6db21fda-80cd-3f85-b4a7-0aadeb14724d'"
      },
      {
        "split": "test",
        "index": 1193,
        "dataset": "TAO",
        "sequence": "val/ArgoVerse/side_right_c9d6ebeb-be15-3df8-b6f1-5575bea8e6b9",
        "reason": "KeyError",
        "detail": "'val/ArgoVerse/side_right_c9d6ebeb-be15-3df8-b6f1-5575bea8e6b9'"
      },
      {
        "split": "test",
        "index": 1197,
        "dataset": "TAO",
        "sequence": "val/ArgoVerse/side_right_230970eb-dc2e-3133-b252-ff3c6f5d4284",
        "reason": "KeyError",
        "detail": "'val/ArgoVerse/side_right_230970eb-dc2e-3133-b252-ff3c6f5d4284'"
      },
      {
        "split": "test",
        "index": 1202,
        "dataset": "TAO",
        "sequence": "val/ArgoVerse/side_right_aebe6aaa-6a95-39e6-9a8d-06103141fcde",
        "reason": "KeyError",
        "detail": "'val/ArgoVerse/side_right_aebe6aaa-6a95-39e6-9a8d-06103141fcde'"
      },
      {
        "split": "test",
        "index": 1203,
        "dataset": "TAO",
        "sequence": "val/ArgoVerse/side_right_52af191b-ba56-326c-b569-e37790db40f3",
        "reason": "KeyError",
        "detail": "'val/ArgoVerse/side_right_52af191b-ba56-326c-b569-e37790db40f3'"
      },
      {
        "split": "test",
        "index": 1531,
        "dataset": "TAO",
        "sequence": "val/HACS/Hurling_v_C5DkqCKgM5M",
        "reason": "KeyError",
        "detail": "'val/HACS/Hurling_v_C5DkqCKgM5M'"
      }
    ],
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/metrics.json"
  },
  {
    "metric_id": "rejection_counts",
    "value": {
      "train:frozen_test_identity_or_original_video_overlap": 305,
      "train:invalid_or_out_of_bounds_annotation": 36,
      "train:KeyError": 8,
      "test:invalid_or_out_of_bounds_annotation": 17,
      "test:KeyError": 21
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/metrics.json"
  },
  {
    "metric_id": "grpo_reference_manifest_sha256",
    "value": "6a6f37966035444508ff722a0b045caf04f26074361f3cca9d29720002499d8d",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/metrics.json"
  },
  {
    "metric_id": "grpo_reference_identities",
    "value": 2001,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/metrics.json"
  },
  {
    "metric_id": "grpo_support_adjustments",
    "value": [
      {
        "identity": "LaSOT:drone-3",
        "nominal": [
          0,
          1191,
          2383,
          3574
        ],
        "chosen": [
          0,
          1190,
          2383,
          3574
        ],
        "reason": "nearest valid same-track support, query final frame excluded; original labels not clipped"
      }
    ],
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/metrics.json"
  },
  {
    "metric_id": "grpo_test_source_overlap",
    "value": [
      "GOT10k:video:0vSvaGa-Gfk",
      "GOT10k:video:9Jzt4Tjnnso",
      "GOT10k:video:AnN7wOKBT6I",
      "GOT10k:video:FEGdL-ItuXs",
      "GOT10k:video:GCc2SIYjDCM",
      "GOT10k:video:GI5jWO5AjGI",
      "GOT10k:video:HH6kemXUZAs",
      "GOT10k:video:Keuc__i7kLk",
      "GOT10k:video:MYUfCN-yeyg",
      "GOT10k:video:PF7y4sjRbGM",
      "GOT10k:video:PREsgySYnBI",
      "GOT10k:video:PdybmsGGGVI",
      "GOT10k:video:SxuAh8hXnS4",
      "GOT10k:video:Vu0XlCKXa8U",
      "GOT10k:video:YYiyTTpCMT0",
      "GOT10k:video:jzQyN64PnCs",
      "GOT10k:video:kUv1eUKu5CA",
      "GOT10k:video:lD63JOjqTDg",
      "GOT10k:video:lS1CpEqgZEQ",
      "GOT10k:video:lob98l5Q-4Y",
      "GOT10k:video:mFOpnHBXOjo",
      "GOT10k:video:mcR0x0ds924",
      "GOT10k:video:nvMXJu8c73k",
      "GOT10k:video:tzH0JVn1G80",
      "GOT10k:video:vRb8mEY3xJY",
      "GOT10k:video:wlUn0qeMLIw"
    ],
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/metrics.json"
  },
  {
    "metric_id": "image_count",
    "value": 8269,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/metrics.json"
  },
  {
    "metric_id": "sampling",
    "value": "SFT/test preserve nominal uniform full span and use same eligible subset; only invalid GRPO supports use nearest valid same-track annotation",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/metrics.json"
  },
  {
    "metric_id": "claim_boundary",
    "value": "Data audit, not training success or performance. Original 1766 test rows reduce to common1728. Whole pipeline separation uses dataset/sequence plus GOT original-video identities; not a cross-dataset pixel-duplicate audit.",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/metrics.json"
  }
]
```

### 分析
完成10175训练与1728共同测试清单、2001支持身份和8269图像审计。发现原GRPO与冻结测试26个GOT原始视频重合；E015正式任务将用显式SHA排除清单整正负对/整ABBA四元组剔除，原输入不改。

### 局限
仅数据审计，非模型结果；共同测试较原1766少38。缺失轨迹/越界标注及305训练源视频重合剔除记录完整保留；未做跨数据集像素去重。

### Claim 边界
仅输入完整性与来源审计，不代表训练能力或性能。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multishot-data-preparation-r5-20261021/managed_console.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
