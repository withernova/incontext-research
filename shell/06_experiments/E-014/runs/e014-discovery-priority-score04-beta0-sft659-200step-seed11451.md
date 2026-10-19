# e014-discovery-priority-score04-beta0-sft659-200step-seed11451 · 用户批准新的统一标量奖励：H+OracleIoU+.5双实例min覆盖+.2SelectedIoU+.4(1-max score误差)-.05近重复-.05逆序

- 父 Run：`e014-boxes-then-scores-beta0-sft659-seed11451`
- 来源版本：2026-10-15T15:14:21
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户批准新的统一标量奖励：H+OracleIoU+.5双实例min覆盖+.2SelectedIoU+.4(1-max score误差)-.05近重复-.05逆序，非法-1；置信度项由.2加倍到.4。用户明确重新训练200step，原SFT659、boxes_then_scores_v1、KL0、G4、seed11451、192tokens、原数据构造，save50，到200自动结束。无分段优势/score分支采样/偏好损失/框数补偿；独立新Run，不恢复旧训练，不持续监控。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：统一标量candidate_discovery_priority_v1：H+OracleIoU+.5C+.2SelectedIoU+.4(1-E)-.05D-.05O；min一对一覆盖仅已知两实例collage，H用IoU>=.5，D=max((pairIoU-.9)/.1,0)，O任一次逆序。非法-1，负样本定位/命中/覆盖0。原SFT659全新启动，beta0、G4、seed11451、lr8e-5、clip.2、192tokens、max_pixels262144、原4000+对称4000；原epoch调度仅加max_steps200上限，save50，旧配置无变化。无分段优势、score分支、CE/偏好或框数补偿。审阅aef31162078fffc0通过，AST/导航/diff静态检查通过；未测试。只启动核验，无持续监控或自动延长。
训练目录已按用户要求改名：真实目录 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/20261015-172638__discovery-priority__score0.4-selected0.2-coverage0.5__kl0__sft659__200step__seed11451；时间来自canonical启动2026-10-15T17:26:38。工具要求artifact_dir末级目录等于Run ID，因此canonical artifact/output/log/metrics入口保留原路径（现为相对兼容symlink），真实文件已在新名目录。2102项inode/size/mtime/mode及相对路径指纹不变。Run ID、历史执行command、代码SHA及历史文件内容不变；未提交的日志代码改造已撤回。
- 命令：bash tools/run.sh configs/experiments/E-014/training/e014_discovery_priority_score04_grpo.py
- 代码版本：1c47c7305c695151df81d46019143028e01752ad
- 随机种子：11451
- 配置：configs/experiments/E-014/training/e014_discovery_priority_score04_grpo.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-priority-score04-beta0-sft659-200step-seed11451/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-priority-score04-beta0-sft659-200step-seed11451/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-priority-score04-beta0-sft659-200step-seed11451/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "optimizer_steps",
    "value": 200,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-priority-score04-beta0-sft659-200step-seed11451/metrics.json"
  },
  {
    "metric_id": "world_size",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-priority-score04-beta0-sft659-200step-seed11451/metrics.json"
  },
  {
    "metric_id": "counterfactual_pairs",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-priority-score04-beta0-sft659-200step-seed11451/metrics.json"
  },
  {
    "metric_id": "valid_rollouts",
    "value": 12514,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-priority-score04-beta0-sft659-200step-seed11451/metrics.json"
  },
  {
    "metric_id": "resumed_step",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-priority-score04-beta0-sft659-200step-seed11451/metrics.json"
  },
  {
    "metric_id": "segment_updates",
    "value": 200,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-priority-score04-beta0-sft659-200step-seed11451/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 0 declared and 6 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-priority-score04-beta0-sft659-200step-seed11451/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-priority-score04-beta0-sft659-200step-seed11451/managed_console.log
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/20261015-172638__discovery-priority__score0.4-selected0.2-coverage0.5__kl0__sft659__200step__seed11451
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/20261015-172638__discovery-priority__score0.4-selected0.2-coverage0.5__kl0__sft659__200step__seed11451/payload/grpo/checkpoints/step_000200

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
