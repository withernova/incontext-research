# e014-historical-three-source-train8367-generation-20261019 · 用户批准上一轮三来源在训练集生成候选：固定合法8367对manifest SHA184f50ab3663a5a2640f62b9cdb6ebf96dd71214

- 父 Run：`e014-selection-fulltrain-step200-gtaugment-20261018`
- 来源版本：2026-10-19T01:12:40
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户批准上一轮三来源在训练集生成候选：固定合法8367对manifest SHA184f50ab3663a5a2640f62b9cdb6ebf96dd7121480d9508caf7e3aef99d95640；顺序E012 ref10query5 step494 focus单框无score、E013 SFT659三框位置假设v2、E013三实例GRPO650 focus_multi3_instances_v1。各8367，总25101源-样本生成，单次串行8GPU BF16SDPA/vision4096/greedy192tokens/seed20260901。保留原始预测/所有解析失败/配置prompt快照与SHA；本Run只候选收集，不补GT、不混组、不选择器训练、不做1766评测、不恢复旧训练、不自动retry。复用现有evaluate.py和配置覆盖，不新增批量runner。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import json,hashlib,os;from pathlib import Path;b=Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-three-source-train8367-generation-20261019/inputs/command.json'"'"').read_bytes();assert hashlib.sha256(b).hexdigest()=='"'"'fa6f8351eb71a21c0dd15dd63ef5c705d89bd3929d25128b8f97f6425d4eb740'"'"';os.execv("/bin/bash",["bash","-c",json.loads(b)["command"]])'
- 代码版本：53ab7653602f62ffc1d5c9dadfbefccf7ad67474
- 随机种子：20260901
- 配置：configs/sft/qwen3vl_8b_lora_focus_1shot_single.py + explicit evaluator/dataset overrides; tools/evaluate.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-three-source-train8367-generation-20261019/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-three-source-train8367-generation-20261019/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-three-source-train8367-generation-20261019/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-three-source-train8367-generation-20261019/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "training_candidate_collection",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-three-source-train8367-generation-20261019/metrics.json"
  },
  {
    "metric_id": "total_generations",
    "value": 25101,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-three-source-train8367-generation-20261019/metrics.json"
  },
  {
    "metric_id": "sources",
    "value": {
      "e012_single494": {
        "samples": 8367,
        "predictions_sha256": "742168600f1ad15a1cb36e344ead46f1dc2d1316c0c1261fa2ad557ecb8166d7",
        "metrics_path": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-three-source-train8367-generation-20261019/payload/e012_single494/evaluation/metrics.json"
      },
      "sft659_three_hypotheses": {
        "samples": 8367,
        "predictions_sha256": "9fb19c16e0cbcafb1d2c2a6e7546405a7943aaf257f6c0dd3838572dbc9b67aa",
        "metrics_path": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-three-source-train8367-generation-20261019/payload/sft659_three_hypotheses/evaluation/metrics.json"
      },
      "instances650": {
        "samples": 8367,
        "predictions_sha256": "8345dabb9a7dfcd7d21bbdce25e2ea651997eaa9527a8bbabe5bfe2dc09ef572",
        "metrics_path": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-three-source-train8367-generation-20261019/payload/instances650/evaluation/metrics.json"
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-three-source-train8367-generation-20261019/metrics.json"
  },
  {
    "metric_id": "selection_training_started",
    "value": false,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-three-source-train8367-generation-20261019/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 0 declared and 5 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### Claim 边界
仅生成，绝不补GT/混组/选择SFT或测试集生成，不自动恢复任何旧训练。指标仅描述训练候选而非泛化。legacy evaluator不记录逐例EOS标记；EOS停止默认生效但不是显式终止审计，后续入库需声明限制。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-three-source-train8367-generation-20261019/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-three-source-train8367-generation-20261019/managed_console.log

### 审核入口
.pi/analysis/e014/historical-candidate-sources-20261019/generation_result_audit.json

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
