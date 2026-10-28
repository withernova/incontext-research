# e015-qwen2-selector-e014clean-20261026 · 用户纠正：去掉可能影响当前测试集的旧E014数据。排除当前作者LaSOT36测试类别（含TAO内LaSOT来源），排除三数据集1/2/4shot全部测试源视频（

- 父 Run：`e015-three-dataset-eval-20261026`
- 来源版本：2026-10-26T15:15:01
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户纠正：去掉可能影响当前测试集的旧E014数据。排除当前作者LaSOT36测试类别（含TAO内LaSOT来源），排除三数据集1/2/4shot全部测试源视频（跨数据集LaSOT/YouTube身份、AVA/HACS场景归一）及相同图像路径/SHA，按整源组/source_index闭包删除全部排列。原始21552行文件保持，独立过滤清单和删除原因/SHA留档，不重采样平衡。中止旧e014data Run并不得续训；从官方Qwen2 fresh独立LoRA，4epochs/global16/lr5e-5/warmup.03/clip.3/seed20260901，步数按过滤后规模计算、末1/4线性衰减。固定现有GRPO proposal和1289 Query各1/2/4shot自动三数据集评测，对比旧VQA、score、Oracle，45个diag_e014clean独立指标。保留原1shot题目/标签，调用既有训练评测入口，已知重合零不声称所有近重复完全排除，非单因素因果结论。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户纠正：去掉可能影响当前测试集的旧E014数据。排除当前作者LaSOT36测试类别（含TAO内LaSOT来源），排除三数据集1/2/4shot全部测试源视频（跨数据集LaSOT/YouTube身份、AVA/HACS场景归一）及相同图像路径/SHA，按整源组/source_index闭包删除全部排列。原始21552行文件保持，独立过滤清单和删除原因/SHA留档，不重采样平衡。中止旧e014data Run并不得续训；从官方Qwen2 fresh独立LoRA，4epochs/global16/lr5e-5/warmup.03/clip.3/seed20260901，步数按过滤后规模计算、末1/4线性衰减。固定现有GRPO proposal和1289 Query各1/2/4shot自动三数据集评测，对比旧VQA、score、Oracle，45个diag_e014clean独立指标。保留原1shot题目/标签，调用既有训练评测入口，已知重合零不声称所有近重复完全排除，非单因素因果结论。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'fe1acb121adbc87a098aae7fe6c26fd30c2b9db17211d617253c28fb39d5535f'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：28c72afff503650316e37039c5931f2587b62b45
- 随机种子：20260901
- 配置：configs/experiments/E-015/selector.py + tools/evaluate_candidate_vqa.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json

## 结果
尚无结果。

### 指标
```json
[
  {
    "metric_id": "diag_e014clean_lasot_vqa_miou_1shot",
    "value": 60.24948934008074,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_lasot_vqa_acc50_1shot",
    "value": 66.66666666666666,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_lasot_delta_vqa_miou_1shot",
    "value": -0.6830024986933978,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_got10k_vqa_miou_1shot",
    "value": 77.31695533583304,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_got10k_vqa_acc50_1shot",
    "value": 83.33333333333334,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_got10k_delta_vqa_miou_1shot",
    "value": 0.5896059080955638,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_tao_vqa_miou_1shot",
    "value": 63.31027965084585,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_tao_vqa_acc50_1shot",
    "value": 68.60103626943005,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_tao_delta_vqa_miou_1shot",
    "value": 1.2217976555940382,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_pooled_vqa_miou_1shot",
    "value": 64.92428106166629,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_pooled_vqa_acc50_1shot",
    "value": 70.4422032583398,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_pooled_delta_vqa_miou_1shot",
    "value": 0.920722607675458,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_macro_vqa_miou_1shot",
    "value": 66.95890810891987,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_macro_vqa_acc50_1shot",
    "value": 72.86701208981002,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_macro_delta_vqa_miou_1shot",
    "value": 0.37613368833206096,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_lasot_vqa_miou_2shot",
    "value": 61.36961192652692,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_lasot_vqa_acc50_2shot",
    "value": 65.97222222222221,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_lasot_delta_vqa_miou_2shot",
    "value": 0.2071310198944758,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_got10k_vqa_miou_2shot",
    "value": 79.13086819660238,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_got10k_vqa_acc50_2shot",
    "value": 86.11111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_got10k_delta_vqa_miou_2shot",
    "value": 0.19747873078912903,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_tao_vqa_miou_2shot",
    "value": 69.97817606517961,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_tao_vqa_acc50_2shot",
    "value": 76.16580310880829,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_tao_delta_vqa_miou_2shot",
    "value": 0.5968558040561902,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_pooled_vqa_miou_2shot",
    "value": 70.2945851789811,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_pooled_vqa_acc50_2shot",
    "value": 76.41582622187742,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_pooled_delta_vqa_miou_2shot",
    "value": 0.4975476255399798,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_macro_vqa_miou_2shot",
    "value": 70.15955206276963,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_macro_vqa_acc50_2shot",
    "value": 76.08304548071388,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_macro_delta_vqa_miou_2shot",
    "value": 0.33382185157992694,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_lasot_vqa_miou_4shot",
    "value": 65.23348855828748,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_lasot_vqa_acc50_4shot",
    "value": 72.91666666666666,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_lasot_delta_vqa_miou_4shot",
    "value": 0.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_got10k_vqa_miou_4shot",
    "value": 81.56340126592931,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_got10k_vqa_acc50_4shot",
    "value": 88.88888888888889,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_got10k_delta_vqa_miou_4shot",
    "value": -0.6362936337354483,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_tao_vqa_miou_4shot",
    "value": 72.87637171041258,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_tao_vqa_acc50_4shot",
    "value": 79.17098445595855,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_tao_delta_vqa_miou_4shot",
    "value": -0.17926693199909494,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_pooled_vqa_miou_4shot",
    "value": 73.23563481831556,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_pooled_vqa_acc50_4shot",
    "value": 79.82932505818464,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_pooled_delta_vqa_miou_4shot",
    "value": -0.22306085605237058,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_macro_vqa_miou_4shot",
    "value": 73.22442051154313,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_macro_vqa_acc50_4shot",
    "value": 80.32551333717136,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_macro_delta_vqa_miou_4shot",
    "value": -0.2718535219115097,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  }
]
```

### 关键结果
```json
[
  {
    "metric_id": "diag_e014clean_lasot_vqa_miou_1shot",
    "value": 60.24948934008074,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_lasot_vqa_acc50_1shot",
    "value": 66.66666666666666,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_lasot_delta_vqa_miou_1shot",
    "value": -0.6830024986933978,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_got10k_vqa_miou_1shot",
    "value": 77.31695533583304,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_got10k_vqa_acc50_1shot",
    "value": 83.33333333333334,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_got10k_delta_vqa_miou_1shot",
    "value": 0.5896059080955638,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_tao_vqa_miou_1shot",
    "value": 63.31027965084585,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_tao_vqa_acc50_1shot",
    "value": 68.60103626943005,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_tao_delta_vqa_miou_1shot",
    "value": 1.2217976555940382,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_pooled_vqa_miou_1shot",
    "value": 64.92428106166629,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_pooled_vqa_acc50_1shot",
    "value": 70.4422032583398,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_pooled_delta_vqa_miou_1shot",
    "value": 0.920722607675458,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_macro_vqa_miou_1shot",
    "value": 66.95890810891987,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_macro_vqa_acc50_1shot",
    "value": 72.86701208981002,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_macro_delta_vqa_miou_1shot",
    "value": 0.37613368833206096,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_lasot_vqa_miou_2shot",
    "value": 61.36961192652692,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_lasot_vqa_acc50_2shot",
    "value": 65.97222222222221,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_lasot_delta_vqa_miou_2shot",
    "value": 0.2071310198944758,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_got10k_vqa_miou_2shot",
    "value": 79.13086819660238,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_got10k_vqa_acc50_2shot",
    "value": 86.11111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_got10k_delta_vqa_miou_2shot",
    "value": 0.19747873078912903,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_tao_vqa_miou_2shot",
    "value": 69.97817606517961,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_tao_vqa_acc50_2shot",
    "value": 76.16580310880829,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_tao_delta_vqa_miou_2shot",
    "value": 0.5968558040561902,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_pooled_vqa_miou_2shot",
    "value": 70.2945851789811,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_pooled_vqa_acc50_2shot",
    "value": 76.41582622187742,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_pooled_delta_vqa_miou_2shot",
    "value": 0.4975476255399798,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_macro_vqa_miou_2shot",
    "value": 70.15955206276963,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_macro_vqa_acc50_2shot",
    "value": 76.08304548071388,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_macro_delta_vqa_miou_2shot",
    "value": 0.33382185157992694,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_lasot_vqa_miou_4shot",
    "value": 65.23348855828748,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_lasot_vqa_acc50_4shot",
    "value": 72.91666666666666,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_lasot_delta_vqa_miou_4shot",
    "value": 0.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_got10k_vqa_miou_4shot",
    "value": 81.56340126592931,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_got10k_vqa_acc50_4shot",
    "value": 88.88888888888889,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_got10k_delta_vqa_miou_4shot",
    "value": -0.6362936337354483,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_tao_vqa_miou_4shot",
    "value": 72.87637171041258,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_tao_vqa_acc50_4shot",
    "value": 79.17098445595855,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_tao_delta_vqa_miou_4shot",
    "value": -0.17926693199909494,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_pooled_vqa_miou_4shot",
    "value": 73.23563481831556,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_pooled_vqa_acc50_4shot",
    "value": 79.82932505818464,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_pooled_delta_vqa_miou_4shot",
    "value": -0.22306085605237058,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_macro_vqa_miou_4shot",
    "value": 73.22442051154313,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_macro_vqa_acc50_4shot",
    "value": 80.32551333717136,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  },
  {
    "metric_id": "diag_e014clean_macro_delta_vqa_miou_4shot",
    "value": -0.2718535219115097,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 45 declared and 0 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence and declared metrics only; it does not validate causal or Claim conclusions.

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-selector-e014clean-20261026/managed_console.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
