# e015-three-dataset-eval-20261026 · 用户授权使用已完成E015模型联合评测LaSOT/GOT10k/TAO的1/2/4shot。复用父GRPO与selector及LaSOT144预测；新增GOT1

- 父 Run：`e015-iploc144-qwen2-4shot-restart-r3-20261023`
- 来源版本：2026-10-26T01:10:11
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户授权使用已完成E015模型联合评测LaSOT/GOT10k/TAO的1/2/4shot。复用父GRPO与selector及LaSOT144预测；新增GOT10k和TAO-Amodal官方validation带标签评测，按父训练的均匀参考取帧构造共同query集，核查SFT/GRPO源视频互斥并报告类别重合。分别报告score/VQA/Oracle mIoU与Acc50，各数据集、合并样本微平均、三数据集等权宏平均。不是FOCUS官方test复现；保留原标注异常，缺帧或不足5帧记录排除。不训练，不改变模型/prompt/score/奖励。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户授权使用已完成E015模型联合评测LaSOT/GOT10k/TAO的1/2/4shot。复用父GRPO与selector及LaSOT144预测；新增GOT10k和TAO-Amodal官方validation带标签评测，按父训练的均匀参考取帧构造共同query集，核查SFT/GRPO源视频互斥并报告类别重合。分别报告score/VQA/Oracle mIoU与Acc50，各数据集、合并样本微平均、三数据集等权宏平均。不是FOCUS官方test复现；保留原标注异常，缺帧或不足5帧记录排除。不训练，不改变模型/prompt/score/奖励。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'8b41d9ea2bba7e7ac8f0e77f6087059c62b14da0750f50f43fb1217cb74381e6'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：28c72afff503650316e37039c5931f2587b62b45
- 随机种子：20260901
- 配置：configs/experiments/E-015/evaluate.py + tools/evaluate_candidate_vqa.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json

## 结果
尚无结果。

### 指标
```json
[
  {
    "metric_id": "jointval_lasot_vqa_miou_1shot",
    "value": 60.93249183877414,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_score_miou_1shot",
    "value": 59.06520773132588,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_oracle_miou_1shot",
    "value": 60.93249183877414,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_vqa_acc50_1shot",
    "value": 67.36111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_score_acc50_1shot",
    "value": 65.27777777777779,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_oracle_acc50_1shot",
    "value": 67.36111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_vqa_miou_1shot",
    "value": 76.72734942773748,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_score_miou_1shot",
    "value": 77.31695533583304,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_oracle_miou_1shot",
    "value": 77.31695533583304,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_vqa_acc50_1shot",
    "value": 82.77777777777777,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_score_acc50_1shot",
    "value": 83.33333333333334,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_oracle_acc50_1shot",
    "value": 83.33333333333334,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_vqa_miou_1shot",
    "value": 62.08848199525181,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_score_miou_1shot",
    "value": 62.31441567475361,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_oracle_miou_1shot",
    "value": 63.546319671871174,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_vqa_acc50_1shot",
    "value": 67.15025906735751,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_score_acc50_1shot",
    "value": 67.46113989637306,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_oracle_acc50_1shot",
    "value": 68.9119170984456,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_vqa_miou_1shot",
    "value": 64.00355845399083,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_score_miou_1shot",
    "value": 64.0464336694322,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_oracle_miou_1shot",
    "value": 65.17729190736164,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_vqa_acc50_1shot",
    "value": 69.35608999224205,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_score_acc50_1shot",
    "value": 69.43366951124904,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_oracle_acc50_1shot",
    "value": 70.75252133436773,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_vqa_miou_1shot",
    "value": 66.58277442058781,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_score_miou_1shot",
    "value": 66.23219291397083,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_oracle_miou_1shot",
    "value": 67.26525561549278,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_vqa_acc50_1shot",
    "value": 72.42971598541547,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_score_acc50_1shot",
    "value": 72.02408366916139,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_oracle_acc50_1shot",
    "value": 73.20212051429668,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_vqa_miou_2shot",
    "value": 61.162480906632446,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_score_miou_2shot",
    "value": 60.78279528273303,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_oracle_miou_2shot",
    "value": 61.98003586156338,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_vqa_acc50_2shot",
    "value": 65.97222222222221,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_score_acc50_2shot",
    "value": 65.27777777777779,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_oracle_acc50_2shot",
    "value": 66.66666666666666,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_vqa_miou_2shot",
    "value": 78.93338946581325,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_score_miou_2shot",
    "value": 79.32342481529638,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_oracle_miou_2shot",
    "value": 79.32342481529638,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_vqa_acc50_2shot",
    "value": 85.55555555555556,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_score_acc50_2shot",
    "value": 86.11111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_oracle_acc50_2shot",
    "value": 86.11111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_vqa_miou_2shot",
    "value": 69.38132026112342,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_score_miou_2shot",
    "value": 69.6223584901695,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_oracle_miou_2shot",
    "value": 70.63971067177198,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_vqa_acc50_2shot",
    "value": 75.5440414507772,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_score_acc50_2shot",
    "value": 75.75129533678756,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_oracle_acc50_2shot",
    "value": 76.99481865284974,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_vqa_miou_2shot",
    "value": 69.79703755344111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_score_miou_2shot",
    "value": 69.989538347929,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_oracle_miou_2shot",
    "value": 70.88492042597241,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_vqa_acc50_2shot",
    "value": 75.87276958882855,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_score_acc50_2shot",
    "value": 76.02792862684251,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_oracle_acc50_2shot",
    "value": 77.11404189294026,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_vqa_miou_2shot",
    "value": 69.82573021118971,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_score_miou_2shot",
    "value": 69.90952619606631,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_oracle_miou_2shot",
    "value": 70.64772378287724,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_vqa_acc50_2shot",
    "value": 75.69060640951832,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_score_acc50_2shot",
    "value": 75.71339474189215,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_oracle_acc50_2shot",
    "value": 76.59086547687583,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_vqa_miou_4shot",
    "value": 65.23348855828748,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_score_miou_4shot",
    "value": 65.38908655975659,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_oracle_miou_4shot",
    "value": 65.38908655975659,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_vqa_acc50_4shot",
    "value": 72.91666666666666,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_score_acc50_4shot",
    "value": 72.91666666666666,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_oracle_acc50_4shot",
    "value": 72.91666666666666,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_vqa_miou_4shot",
    "value": 82.19969489966476,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_score_miou_4shot",
    "value": 82.19969489966476,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_oracle_miou_4shot",
    "value": 82.19969489966476,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_vqa_acc50_4shot",
    "value": 90.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_score_acc50_4shot",
    "value": 90.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_oracle_acc50_4shot",
    "value": 90.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_vqa_miou_4shot",
    "value": 73.05563864241168,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_score_miou_4shot",
    "value": 73.53099737136853,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_oracle_miou_4shot",
    "value": 74.01252082579934,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_vqa_acc50_4shot",
    "value": 79.48186528497409,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_score_acc50_4shot",
    "value": 79.89637305699482,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_oracle_acc50_4shot",
    "value": 80.51813471502591,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_vqa_miou_4shot",
    "value": 73.45869567436793,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_score_miou_4shot",
    "value": 73.83195190839031,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_oracle_miou_4shot",
    "value": 74.19244076294869,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_vqa_acc50_4shot",
    "value": 80.21722265321955,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_score_acc50_4shot",
    "value": 80.52754072924748,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_oracle_acc50_4shot",
    "value": 80.99301784328937,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_vqa_miou_4shot",
    "value": 73.49627403345464,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_score_miou_4shot",
    "value": 73.70659294359663,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_oracle_miou_4shot",
    "value": 73.86710076174023,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_vqa_acc50_4shot",
    "value": 80.79951065054692,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_score_acc50_4shot",
    "value": 80.93767990788714,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_oracle_acc50_4shot",
    "value": 81.14493379389752,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  }
]
```

### 关键结果
```json
[
  {
    "metric_id": "jointval_lasot_vqa_miou_1shot",
    "value": 60.93249183877414,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_score_miou_1shot",
    "value": 59.06520773132588,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_oracle_miou_1shot",
    "value": 60.93249183877414,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_vqa_acc50_1shot",
    "value": 67.36111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_score_acc50_1shot",
    "value": 65.27777777777779,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_oracle_acc50_1shot",
    "value": 67.36111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_vqa_miou_1shot",
    "value": 76.72734942773748,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_score_miou_1shot",
    "value": 77.31695533583304,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_oracle_miou_1shot",
    "value": 77.31695533583304,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_vqa_acc50_1shot",
    "value": 82.77777777777777,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_score_acc50_1shot",
    "value": 83.33333333333334,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_oracle_acc50_1shot",
    "value": 83.33333333333334,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_vqa_miou_1shot",
    "value": 62.08848199525181,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_score_miou_1shot",
    "value": 62.31441567475361,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_oracle_miou_1shot",
    "value": 63.546319671871174,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_vqa_acc50_1shot",
    "value": 67.15025906735751,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_score_acc50_1shot",
    "value": 67.46113989637306,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_oracle_acc50_1shot",
    "value": 68.9119170984456,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_vqa_miou_1shot",
    "value": 64.00355845399083,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_score_miou_1shot",
    "value": 64.0464336694322,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_oracle_miou_1shot",
    "value": 65.17729190736164,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_vqa_acc50_1shot",
    "value": 69.35608999224205,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_score_acc50_1shot",
    "value": 69.43366951124904,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_oracle_acc50_1shot",
    "value": 70.75252133436773,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_vqa_miou_1shot",
    "value": 66.58277442058781,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_score_miou_1shot",
    "value": 66.23219291397083,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_oracle_miou_1shot",
    "value": 67.26525561549278,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_vqa_acc50_1shot",
    "value": 72.42971598541547,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_score_acc50_1shot",
    "value": 72.02408366916139,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_oracle_acc50_1shot",
    "value": 73.20212051429668,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_vqa_miou_2shot",
    "value": 61.162480906632446,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_score_miou_2shot",
    "value": 60.78279528273303,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_oracle_miou_2shot",
    "value": 61.98003586156338,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_vqa_acc50_2shot",
    "value": 65.97222222222221,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_score_acc50_2shot",
    "value": 65.27777777777779,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_oracle_acc50_2shot",
    "value": 66.66666666666666,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_vqa_miou_2shot",
    "value": 78.93338946581325,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_score_miou_2shot",
    "value": 79.32342481529638,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_oracle_miou_2shot",
    "value": 79.32342481529638,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_vqa_acc50_2shot",
    "value": 85.55555555555556,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_score_acc50_2shot",
    "value": 86.11111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_oracle_acc50_2shot",
    "value": 86.11111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_vqa_miou_2shot",
    "value": 69.38132026112342,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_score_miou_2shot",
    "value": 69.6223584901695,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_oracle_miou_2shot",
    "value": 70.63971067177198,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_vqa_acc50_2shot",
    "value": 75.5440414507772,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_score_acc50_2shot",
    "value": 75.75129533678756,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_oracle_acc50_2shot",
    "value": 76.99481865284974,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_vqa_miou_2shot",
    "value": 69.79703755344111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_score_miou_2shot",
    "value": 69.989538347929,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_oracle_miou_2shot",
    "value": 70.88492042597241,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_vqa_acc50_2shot",
    "value": 75.87276958882855,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_score_acc50_2shot",
    "value": 76.02792862684251,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_oracle_acc50_2shot",
    "value": 77.11404189294026,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_vqa_miou_2shot",
    "value": 69.82573021118971,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_score_miou_2shot",
    "value": 69.90952619606631,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_oracle_miou_2shot",
    "value": 70.64772378287724,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_vqa_acc50_2shot",
    "value": 75.69060640951832,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_score_acc50_2shot",
    "value": 75.71339474189215,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_oracle_acc50_2shot",
    "value": 76.59086547687583,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_vqa_miou_4shot",
    "value": 65.23348855828748,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_score_miou_4shot",
    "value": 65.38908655975659,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_oracle_miou_4shot",
    "value": 65.38908655975659,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_vqa_acc50_4shot",
    "value": 72.91666666666666,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_score_acc50_4shot",
    "value": 72.91666666666666,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_lasot_oracle_acc50_4shot",
    "value": 72.91666666666666,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_vqa_miou_4shot",
    "value": 82.19969489966476,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_score_miou_4shot",
    "value": 82.19969489966476,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_oracle_miou_4shot",
    "value": 82.19969489966476,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_vqa_acc50_4shot",
    "value": 90.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_score_acc50_4shot",
    "value": 90.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_got10k_oracle_acc50_4shot",
    "value": 90.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_vqa_miou_4shot",
    "value": 73.05563864241168,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_score_miou_4shot",
    "value": 73.53099737136853,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_oracle_miou_4shot",
    "value": 74.01252082579934,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_vqa_acc50_4shot",
    "value": 79.48186528497409,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_score_acc50_4shot",
    "value": 79.89637305699482,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_tao_oracle_acc50_4shot",
    "value": 80.51813471502591,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_vqa_miou_4shot",
    "value": 73.45869567436793,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_score_miou_4shot",
    "value": 73.83195190839031,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_oracle_miou_4shot",
    "value": 74.19244076294869,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_vqa_acc50_4shot",
    "value": 80.21722265321955,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_score_acc50_4shot",
    "value": 80.52754072924748,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_pooled_oracle_acc50_4shot",
    "value": 80.99301784328937,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_vqa_miou_4shot",
    "value": 73.49627403345464,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_score_miou_4shot",
    "value": 73.70659294359663,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_oracle_miou_4shot",
    "value": 73.86710076174023,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_vqa_acc50_4shot",
    "value": 80.79951065054692,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_score_acc50_4shot",
    "value": 80.93767990788714,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  },
  {
    "metric_id": "jointval_macro_oracle_acc50_4shot",
    "value": 81.14493379389752,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 90 declared and 0 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence and declared metrics only; it does not validate causal or Claim conclusions.

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-three-dataset-eval-20261026/managed_console.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
