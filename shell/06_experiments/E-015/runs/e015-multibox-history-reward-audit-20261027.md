# e015-multibox-history-reward-audit-20261027 · 用户明确要求分析过去多框率较高的样本，解释当前单框收缩。独立CPU衍生分析：冻结同Qwen2/SFT636/4shot/数据的旧discovery400步128

- 父 Run：`e015-qwen2-tier3-ddp8-full-20261027`
- 来源版本：2026-10-27T15:15:53
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户明确要求分析过去多框率较高的样本，解释当前单框收缩。独立CPU衍生分析：冻结同Qwen2/SFT636/4shot/数据的旧discovery400步12800rollouts与当前tier3-DDP8前84步5376rollouts（按每rank前672行SHA冻结，不读取后续训练更新作为主数据），复用现有parser和two_instance_coverage。逐输出重算旧/新奖励并核对实际记录误差<1e-8；在同prompt同G4采样组比较真实单框/多框排序，分别替换coverage权重/mean方式、Oracle权重、score权重、选中档位以诊断排序变化。核验旧前168步与新前84步相同采样预算的sample_id多重集；比较旧前/后100步与新20步窗口。按明确排序规则选择反转样例及同prompt跨训练Oracle损失样例，生成可离线查看的HTML（实际4张参考图、原图+SVG框、完整输出/分项奖励），不是随机代表样本。无模型生成、无GPU计算、不改变/暂停正在运行的正式训练，不修改共享源码。排序重算不是重训因果或最终测试mIoU；保留数据划分与原图未标注其他实例的限制。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户明确要求分析过去多框率较高的样本，解释当前单框收缩。独立CPU衍生分析：冻结同Qwen2/SFT636/4shot/数据的旧discovery400步12800rollouts与当前tier3-DDP8前84步5376rollouts（按每rank前672行SHA冻结，不读取后续训练更新作为主数据），复用现有parser和two_instance_coverage。逐输出重算旧/新奖励并核对实际记录误差<1e-8；在同prompt同G4采样组比较真实单框/多框排序，分别替换coverage权重/mean方式、Oracle权重、score权重、选中档位以诊断排序变化。核验旧前168步与新前84步相同采样预算的sample_id多重集；比较旧前/后100步与新20步窗口。按明确排序规则选择反转样例及同prompt跨训练Oracle损失样例，生成可离线查看的HTML（实际4张参考图、原图+SVG框、完整输出/分项奖励），不是随机代表样本。无模型生成、无GPU计算、不改变/暂停正在运行的正式训练，不修改共享源码。排序重算不是重训因果或最终测试mIoU；保留数据划分与原图未标注其他实例的限制。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'53c3001131b8f0d144ec9513c7e827825e97d1f226838c1185652aabc3ec498f'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：0e02d856ae30837eb60b511e8303cb50a50d1c26
- 随机种子：11451
- 配置：CPU artifact analysis; existing variable candidate parser and coverage reward helper; no GPU/model calls
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json

## 结果
尚无结果。

### 指标
```json
[
  {
    "metric_id": "history_audit_old_rollouts",
    "value": 12800,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json"
  },
  {
    "metric_id": "history_audit_current_rollouts",
    "value": 5376,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json"
  },
  {
    "metric_id": "history_audit_old_last100_original_multi",
    "value": 9.35960591133005,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json"
  },
  {
    "metric_id": "history_audit_old_last100_collage_multi",
    "value": 80.7741116751269,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json"
  },
  {
    "metric_id": "history_audit_current_last20_original_multi",
    "value": 0.5747126436781609,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json"
  },
  {
    "metric_id": "history_audit_current_last20_collage_multi",
    "value": 2.054794520547945,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json"
  }
]
```

### 关键结果
```json
[
  {
    "metric_id": "history_audit_old_rollouts",
    "value": 12800,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json"
  },
  {
    "metric_id": "history_audit_current_rollouts",
    "value": 5376,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json"
  },
  {
    "metric_id": "history_audit_old_last100_original_multi",
    "value": 9.35960591133005,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json"
  },
  {
    "metric_id": "history_audit_old_last100_collage_multi",
    "value": 80.7741116751269,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json"
  },
  {
    "metric_id": "history_audit_current_last20_original_multi",
    "value": 0.5747126436781609,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json"
  },
  {
    "metric_id": "history_audit_current_last20_collage_multi",
    "value": 2.054794520547945,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 6 declared and 0 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence and declared metrics only; it does not validate causal or Claim conclusions.

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-multibox-history-reward-audit-20261027/managed_console.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
