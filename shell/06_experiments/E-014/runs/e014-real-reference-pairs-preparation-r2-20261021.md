# e014-real-reference-pairs-preparation-r2-20261021 · 继续当前明确授权的真实配对准备，首次脚本历史路径缺generation层，在任何配对数据写出前失败。已从原真实命令纠正路径并实测三份SHA相符，科学设置不变；独

- 父 Run：`e014-real-reference-pairs-preparation-20261021`
- 来源版本：2026-10-21T01:08:47
- 状态：analysis_pending
- Workspace：03

## 本次任务
继续当前明确授权的真实配对准备，首次脚本历史路径缺generation层，在任何配对数据写出前失败。已从原真实命令纠正路径并实测三份SHA相符，科学设置不变；独立修正版执行，原失败保留。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户明确运行配对方向。CPU读取已钉住SHA的TAO原始train标注和8367训练源中的499TAO视频，合并三组已有冻结候选（step200/SFT659/instances650）；仅重编号并保留source mapping，不改候选/顺序/目标或补GT。按同Query同类别异track选择Reference，优先原Reference帧，否则最早非Query帧；调用既有reference-pairs CLI核验身份/图像SHA/框/两不同答案/best>=.5/gap>.05/已有留出视频排除/seed20260901视频15%拆分。保存所有接受拒绝；非空后导出两行普通SFT、A-only等行数控制和双Reference验证输入。实际可用量决定后续轻量训练；零数据也保留真实不足结论。无GPU/模型推理/训练。 首次准备脚本遗漏step200历史路径generation层而失败，保留原Run；本修正版仅纠正来源路径，实际SHA三份已核对，科学定义不变。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'ed31940d1354d2ba20c417722e3dfb0f0d794a9ae81dc0f7b64de3b65c4bb562'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：7caae090351c9c71ce65fd8c98a0bbbbb1825bc6
- 随机种子：20260901
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "real_reference_pair_preparation",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json"
  },
  {
    "metric_id": "requested_pairs",
    "value": 1314,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json"
  },
  {
    "metric_id": "source_records",
    "value": 1497,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json"
  },
  {
    "metric_id": "prepare_exit_code",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json"
  },
  {
    "metric_id": "accepted_pairs",
    "value": {
      "train": 359,
      "validation": 62
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json"
  },
  {
    "metric_id": "accepted_unique_queries",
    "value": 152,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json"
  },
  {
    "metric_id": "accepted_video_groups",
    "value": 152,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json"
  },
  {
    "metric_id": "rejection_counts",
    "value": {
      "ValueError: Missing or ambiguous good candidate for one paired target": 727,
      "ValueError: At least two frozen candidates required": 156,
      "ValueError: Changing Reference does not change the correct candidate": 10
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json"
  },
  {
    "metric_id": "training_started",
    "value": false,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json"
  },
  {
    "metric_id": "seed",
    "value": 20260901,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json"
  },
  {
    "metric_id": "limitations",
    "value": "Pairs/rows across sources are correlated. New split is not independent for previously exposed step4041; fresh training required for pair-only split interpretation.",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json"
  },
  {
    "metric_id": "control_train_sha256",
    "value": "7a8c7a761cdb3a114b5bee6db61454c91e5e1167a23ff502a3983dfbd3420116",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json"
  },
  {
    "metric_id": "paired_train_sha256",
    "value": "dd798ba7c48d6a01f764b1af4c4a291404cacc6aa5dd35db8ffe86bc2ca382f6",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json"
  },
  {
    "metric_id": "train_rows",
    "value": 718,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json"
  },
  {
    "metric_id": "validation_rows",
    "value": 124,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json"
  },
  {
    "metric_id": "validation_manifest_sha256",
    "value": "67536ed1f2463e09dfc7afec87f2e3aa88d256825786c7f95b8e0288101330ff",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json"
  },
  {
    "metric_id": "validation_predictions_sha256",
    "value": "2c38ba5fce978582210a4543f97ba6ecda2736ddab9b7f74e3ff48e2f9ac764d",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json"
  }
]
```

### 分析
真实exit0/CLI exit0，1314请求接受421对（359train/62validation），分别129/23个视频组，合计152独立Query/视频；多个候选来源相关，不冒称421独立场景。893拒绝：727缺失/歧义好框、156少于2候选、10换Reference正确索引未变。导出718配对训练行、718等预算A-only控制、124验证行，所有输入/审计/输出SHA保存；真实标注track/category/image/frame/bbox核验，无补GT。首个脚本路径错误失败记录保留。已另建fresh训练对照子Run；新拆分对旧step4041非独立，fresh两arm初始模型相同。两训练arm答案编号分布不同（paired1:334/2:270/3:112/4:1/5:1；control1:546/2:142/3:30），保留归因限制。证据.pi/analysis/e014/selector-experiments-20261021/pairs_results.json。

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### Claim 边界
仅生成，绝不补GT/混组/选择SFT或测试集生成，不自动恢复任何旧训练。指标仅描述训练候选而非泛化。legacy evaluator不记录逐例EOS标记；EOS停止默认生效但不是显式终止审计，后续入库需声明限制。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-real-reference-pairs-preparation-r2-20261021/managed_console.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
