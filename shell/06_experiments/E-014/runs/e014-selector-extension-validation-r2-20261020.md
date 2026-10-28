# e014-selector-extension-validation-r2-20261020 · 继续用户已授权的部署运行验收：首次验收脚本遗漏仓库现有torchvision NMS兼容初始化，在任何测试/模型调用前exit1，保留失败事实。修正版仅复用ip

- 父 Run：`e014-selector-extension-validation-20261020`
- 来源版本：2026-10-20T18:52:56
- 状态：analysis_pending
- Workspace：03

## 本次任务
继续用户已授权的部署运行验收：首次验收脚本遗漏仓库现有torchvision NMS兼容初始化，在任何测试/模型调用前exit1，保留失败事实。修正版仅复用iploc_szy.compat.ensure_torchvision_nms_schema，并使用独立payload目录与受管outputs分离；部署SHA、科学代码和验证范围不变，不安装依赖、不恢复历史训练。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：一次性验收输入脚本SHA=b8ae20e93f7702641cda3cfd4e7f5e2dd5d784be032e7c222f40c68f376ea4f3。已部署7caae09；合成候选排列、无效统计、裁剪像素/顺序、真实AdamW小参数的LR端点与二次恢复；三数据集各一个真实图片processor编码train/eval一致性。生成模型为明确标记的编码stub，模型推理0、训练更新0；不作为真实TAO配对规模或训练收益证据。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import hashlib,pathlib; assert hashlib.sha256(pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-r2-20261020/inputs/validate_extensions.py'"'"').read_bytes()).hexdigest()=='"'"'b8ae20e93f7702641cda3cfd4e7f5e2dd5d784be032e7c222f40c68f376ea4f3'"'"'' && env PYTHONPATH=. OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 /songzhengyue/miniconda3/envs/IPLoc/bin/python /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-r2-20261020/inputs/validate_extensions.py /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-r2-20261020
- 代码版本：7caae090351c9c71ce65fd8c98a0bbbbb1825bc6
- 随机种子：20260901
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-r2-20261020/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-r2-20261020/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-r2-20261020/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "validation_passed",
    "value": 1,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-r2-20261020/metrics.json"
  },
  {
    "metric_id": "synthetic_logic_checks_passed",
    "value": 1,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-r2-20261020/metrics.json"
  },
  {
    "metric_id": "real_image_encoding_examples",
    "value": 3,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-r2-20261020/metrics.json"
  },
  {
    "metric_id": "model_generations",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-r2-20261020/metrics.json"
  },
  {
    "metric_id": "training_updates",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-r2-20261020/metrics.json"
  },
  {
    "metric_id": "code_sha",
    "value": "7caae090351c9c71ce65fd8c98a0bbbbb1825bc6",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-r2-20261020/metrics.json"
  },
  {
    "metric_id": "validation_script_sha256",
    "value": "b8ae20e93f7702641cda3cfd4e7f5e2dd5d784be032e7c222f40c68f376ea4f3",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-r2-20261020/metrics.json"
  },
  {
    "metric_id": "seed",
    "value": 20260901,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-r2-20261020/metrics.json"
  },
  {
    "metric_id": "limitations",
    "value": "Real processor/image validation plus synthetic logic; no real TAO paired corpus, GPU model generation, or training.",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-r2-20261020/metrics.json"
  }
]
```

### 分析
验收真实exit0/完成标记，官方complete已登记analysis_pending。合成K=2/3/4/5/24、extra=0/1/64唯一排列与映射、invalid/invalid不计一致、重复框区别通过；100x80梯度图片裁剪像素及角色顺序通过；合成原始track配对不同正确答案及重复track/排除组拒绝通过。真实AdamW小参数状态未重置，linear/cosine从更新4042到5388共1347个调度值，首5e-5末5e-6，保存后4500二次恢复通过（非真实模型续训）。实际processor使用GOT10k603/LaSOT1/TAO780各一例、每例K2共5图，train/eval grid与prefix一致，编号+EOS监督通过；输出为明确编码stub，无模型生成、训练0。前次脚本导入失败事实保留。未测真实TAO成对数据规模、GPU生成质量或真实checkpoint完整恢复，不能声称科学收益。证据.pi/analysis/e014/selector-deploy-20261020/validation-r2_results.json以及Run payload两个JSON。

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### Claim 边界
暂停训练不自动恢复，不宣称完成4epoch。较旧模型数据、采样、预算同时变化，测试集又已反复探索，不是单因果或无偏泛化。只评测最新完整step4041，不选其它checkpoint。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-r2-20261020/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-extension-validation-r2-20261020/managed_console.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
