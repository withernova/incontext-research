# e015-qwen2-cleanvqa-e014-124shot-now-20261027 · 用户明确取消当前GRPO并立即执行已准备的新Qwen2 VQA×E014固定proposal的1/2/4shot评测。只取消等待依赖，科学配置和已核验输入全部复

- 父 Run：`e015-qwen2-cleanvqa-e014-124shot-20261027`
- 来源版本：2026-10-27T20:17:08
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户明确取消当前GRPO并立即执行已准备的新Qwen2 VQA×E014固定proposal的1/2/4shot评测。只取消等待依赖，科学配置和已核验输入全部复用；不单列多框子集。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户明确“直接进行，grpo取消现在的”。正式GRPO和旧评测等待命令均精确SIGTERM、exit143，全部GPU释放；保存step50/100和日志，不恢复GRPO或其后续评测。本Run立即依次运行已核验的1/2/4shot Qwen2 VQA对照，取消资源依赖；只变调度和输出目录，不变科学参数。直接引用旧已冻结helper与manifest/proposals，不重做输入准备；审计元数据按SHA复制到新Run，旧产物保留。固定共同1745 Query及E014原1shot proposal，18原视频重合另报1727；只汇总总体/三数据集、VQA/score/Oracle，不单列多框子集。checkpoint clean VQA4172、BF16/SDPA/4×2GPU/layer_split10/exact_instance原图/greedy16/EOS/4096patches/seed20260901均沿已准备Run。复用已部署0e02d856，无源码修改、新训练或新proposal。任务完成后192指标按原定义汇总，并逐例核IoU。旧探索集边界不变，不升级Claim。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'ec9a698eeedf3781bd5b8d348e7dcbf2a670c2befb30e742256e6a08431f71fe'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：0e02d856ae30837eb60b511e8303cb50a50d1c26
- 随机种子：20260901
- 配置：tools/evaluate_candidate_vqa.py direct CLI; fixed E014 proposals, Qwen2 VQA, references=1/2/4; existing temporal sampling and frozen GOT/TAO manifests
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json

## 结果
尚无结果。

### 指标
```json
[
  {
    "metric_id": "diag_q2old124_all_vqa_miou_1shot",
    "value": 70.98720046306559,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_vqa_acc50_1shot",
    "value": 77.42120343839541,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_score_miou_1shot",
    "value": 69.42985617220447,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_score_acc50_1shot",
    "value": 75.81661891117479,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_oracle_miou_1shot",
    "value": 75.95319130977694,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_oracle_acc50_1shot",
    "value": 83.32378223495702,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_invalid_1shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_delta_score_pp_1shot",
    "value": 1.557344290861118,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_vqa_miou_1shot",
    "value": 66.85139162399032,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_vqa_acc50_1shot",
    "value": 75.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_score_miou_1shot",
    "value": 65.37116103330052,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_score_acc50_1shot",
    "value": 73.66666666666667,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_oracle_miou_1shot",
    "value": 71.67223918508266,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_oracle_acc50_1shot",
    "value": 80.83333333333333,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_invalid_1shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_delta_score_pp_1shot",
    "value": 1.4802305906898017,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_vqa_miou_1shot",
    "value": 82.30688173062983,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_vqa_acc50_1shot",
    "value": 89.44444444444444,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_score_miou_1shot",
    "value": 79.59036041152275,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_score_acc50_1shot",
    "value": 86.11111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_oracle_miou_1shot",
    "value": 84.62972143842374,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_oracle_acc50_1shot",
    "value": 92.22222222222223,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_invalid_1shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_delta_score_pp_1shot",
    "value": 2.716521319107068,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_vqa_miou_1shot",
    "value": 71.44724468615739,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_vqa_acc50_1shot",
    "value": 76.68393782383419,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_score_miou_1shot",
    "value": 70.05817360253094,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_score_acc50_1shot",
    "value": 75.23316062176167,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_oracle_miou_1shot",
    "value": 76.99650307315515,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_oracle_acc50_1shot",
    "value": 83.21243523316062,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_invalid_1shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_delta_score_pp_1shot",
    "value": 1.3890710836264586,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_vqa_miou_1shot",
    "value": 71.09957077147594,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_vqa_acc50_1shot",
    "value": 77.53329473074696,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_score_miou_1shot",
    "value": 69.52599475088957,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_score_acc50_1shot",
    "value": 75.91198610306891,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_oracle_miou_1shot",
    "value": 76.11732064264632,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_oracle_acc50_1shot",
    "value": 83.4973943254198,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_invalid_1shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_delta_score_pp_1shot",
    "value": 1.5735760205863758,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_vqa_miou_1shot",
    "value": 67.05692248914723,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_vqa_acc50_1shot",
    "value": 75.25773195876289,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_score_miou_1shot",
    "value": 65.5309115709103,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_score_acc50_1shot",
    "value": 73.8831615120275,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_oracle_miou_1shot",
    "value": 72.02686842841769,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_oracle_acc50_1shot",
    "value": 81.27147766323024,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_invalid_1shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_delta_score_pp_1shot",
    "value": 1.5260109182369197,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_vqa_miou_1shot",
    "value": 82.30688173062983,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_vqa_acc50_1shot",
    "value": 89.44444444444444,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_score_miou_1shot",
    "value": 79.59036041152275,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_score_acc50_1shot",
    "value": 86.11111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_oracle_miou_1shot",
    "value": 84.62972143842374,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_oracle_acc50_1shot",
    "value": 92.22222222222223,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_invalid_1shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_delta_score_pp_1shot",
    "value": 2.716521319107068,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_vqa_miou_1shot",
    "value": 71.44724468615739,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_vqa_acc50_1shot",
    "value": 76.68393782383419,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_score_miou_1shot",
    "value": 70.05817360253094,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_score_acc50_1shot",
    "value": 75.23316062176167,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_oracle_miou_1shot",
    "value": 76.99650307315515,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_oracle_acc50_1shot",
    "value": 83.21243523316062,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_invalid_1shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_delta_score_pp_1shot",
    "value": 1.3890710836264586,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_vqa_miou_2shot",
    "value": 68.28444602803226,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_vqa_acc50_2shot",
    "value": 74.32664756446992,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_score_miou_2shot",
    "value": 69.42985617220447,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_score_acc50_2shot",
    "value": 75.81661891117479,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_oracle_miou_2shot",
    "value": 75.95319130977694,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_oracle_acc50_2shot",
    "value": 83.32378223495702,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_invalid_2shot",
    "value": 13,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_delta_score_pp_2shot",
    "value": -1.1454101441722098,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_vqa_miou_2shot",
    "value": 64.16441792849078,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_vqa_acc50_2shot",
    "value": 71.83333333333334,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_score_miou_2shot",
    "value": 65.37116103330052,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_score_acc50_2shot",
    "value": 73.66666666666667,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_oracle_miou_2shot",
    "value": 71.67223918508266,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_oracle_acc50_2shot",
    "value": 80.83333333333333,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_invalid_2shot",
    "value": 6,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_delta_score_pp_2shot",
    "value": -1.2067431048097377,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_vqa_miou_2shot",
    "value": 83.12890510394139,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_vqa_acc50_2shot",
    "value": 90.55555555555556,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_score_miou_2shot",
    "value": 79.59036041152275,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_score_acc50_2shot",
    "value": 86.11111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_oracle_miou_2shot",
    "value": 84.62972143842374,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_oracle_acc50_2shot",
    "value": 92.22222222222223,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_invalid_2shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_delta_score_pp_2shot",
    "value": 3.5385446924186326,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_vqa_miou_2shot",
    "value": 68.07720688405429,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_vqa_acc50_2shot",
    "value": 72.84974093264248,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_score_miou_2shot",
    "value": 70.05817360253094,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_score_acc50_2shot",
    "value": 75.23316062176167,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_oracle_miou_2shot",
    "value": 76.99650307315515,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_oracle_acc50_2shot",
    "value": 83.21243523316062,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_invalid_2shot",
    "value": 7,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_delta_score_pp_2shot",
    "value": -1.980966718476651,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_vqa_miou_2shot",
    "value": 68.49978704719805,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_vqa_acc50_2shot",
    "value": 74.5801968731905,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_score_miou_2shot",
    "value": 69.52599475088957,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_score_acc50_2shot",
    "value": 75.91198610306891,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_oracle_miou_2shot",
    "value": 76.11732064264632,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_oracle_acc50_2shot",
    "value": 83.4973943254198,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_invalid_2shot",
    "value": 13,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_delta_score_pp_2shot",
    "value": -1.0262077036915063,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_vqa_miou_2shot",
    "value": 64.67598740324607,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_vqa_acc50_2shot",
    "value": 72.5085910652921,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_score_miou_2shot",
    "value": 65.5309115709103,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_score_acc50_2shot",
    "value": 73.8831615120275,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_oracle_miou_2shot",
    "value": 72.02686842841769,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_oracle_acc50_2shot",
    "value": 81.27147766323024,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_invalid_2shot",
    "value": 6,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_delta_score_pp_2shot",
    "value": -0.8549241676642283,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_vqa_miou_2shot",
    "value": 83.12890510394139,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_vqa_acc50_2shot",
    "value": 90.55555555555556,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_score_miou_2shot",
    "value": 79.59036041152275,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_score_acc50_2shot",
    "value": 86.11111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_oracle_miou_2shot",
    "value": 84.62972143842374,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_oracle_acc50_2shot",
    "value": 92.22222222222223,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_invalid_2shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_delta_score_pp_2shot",
    "value": 3.5385446924186326,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_vqa_miou_2shot",
    "value": 68.07720688405429,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_vqa_acc50_2shot",
    "value": 72.84974093264248,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_score_miou_2shot",
    "value": 70.05817360253094,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_score_acc50_2shot",
    "value": 75.23316062176167,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_oracle_miou_2shot",
    "value": 76.99650307315515,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_oracle_acc50_2shot",
    "value": 83.21243523316062,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_invalid_2shot",
    "value": 7,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_delta_score_pp_2shot",
    "value": -1.980966718476651,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_vqa_miou_4shot",
    "value": 63.05745564259644,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_vqa_acc50_4shot",
    "value": 68.59598853868195,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_score_miou_4shot",
    "value": 69.42985617220447,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_score_acc50_4shot",
    "value": 75.81661891117479,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_oracle_miou_4shot",
    "value": 75.95319130977694,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_oracle_acc50_4shot",
    "value": 83.32378223495702,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_invalid_4shot",
    "value": 154,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_delta_score_pp_4shot",
    "value": -6.3724005296080355,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_vqa_miou_4shot",
    "value": 59.0227832324664,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_vqa_acc50_4shot",
    "value": 66.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_score_miou_4shot",
    "value": 65.37116103330052,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_score_acc50_4shot",
    "value": 73.66666666666667,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_oracle_miou_4shot",
    "value": 71.67223918508266,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_oracle_acc50_4shot",
    "value": 80.83333333333333,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_invalid_4shot",
    "value": 53,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_delta_score_pp_4shot",
    "value": -6.348377800834115,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_vqa_miou_4shot",
    "value": 75.21257071664161,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_vqa_acc50_4shot",
    "value": 81.66666666666667,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_score_miou_4shot",
    "value": 79.59036041152275,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_score_acc50_4shot",
    "value": 86.11111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_oracle_miou_4shot",
    "value": 84.62972143842374,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_oracle_acc50_4shot",
    "value": 92.22222222222223,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_invalid_4shot",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_delta_score_pp_4shot",
    "value": -4.37778969488114,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_vqa_miou_4shot",
    "value": 63.29878489933212,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_vqa_acc50_4shot",
    "value": 67.7720207253886,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_score_miou_4shot",
    "value": 70.05817360253094,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_score_acc50_4shot",
    "value": 75.23316062176167,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_oracle_miou_4shot",
    "value": 76.99650307315515,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_oracle_acc50_4shot",
    "value": 83.21243523316062,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_invalid_4shot",
    "value": 93,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_delta_score_pp_4shot",
    "value": -6.759388703198821,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_vqa_miou_4shot",
    "value": 63.17422638665753,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_vqa_acc50_4shot",
    "value": 68.73190503763752,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_score_miou_4shot",
    "value": 69.52599475088957,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_score_acc50_4shot",
    "value": 75.91198610306891,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_oracle_miou_4shot",
    "value": 76.11732064264632,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_oracle_acc50_4shot",
    "value": 83.4973943254198,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_invalid_4shot",
    "value": 153,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_delta_score_pp_4shot",
    "value": -6.3517683642320355,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_vqa_miou_4shot",
    "value": 59.24449967853375,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_vqa_acc50_4shot",
    "value": 66.32302405498281,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_score_miou_4shot",
    "value": 65.5309115709103,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_score_acc50_4shot",
    "value": 73.8831615120275,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_oracle_miou_4shot",
    "value": 72.02686842841769,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_oracle_acc50_4shot",
    "value": 81.27147766323024,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_invalid_4shot",
    "value": 52,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_delta_score_pp_4shot",
    "value": -6.286411892376553,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_vqa_miou_4shot",
    "value": 75.21257071664161,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_vqa_acc50_4shot",
    "value": 81.66666666666667,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_score_miou_4shot",
    "value": 79.59036041152275,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_score_acc50_4shot",
    "value": 86.11111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_oracle_miou_4shot",
    "value": 84.62972143842374,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_oracle_acc50_4shot",
    "value": 92.22222222222223,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_invalid_4shot",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_delta_score_pp_4shot",
    "value": -4.37778969488114,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_vqa_miou_4shot",
    "value": 63.29878489933212,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_vqa_acc50_4shot",
    "value": 67.7720207253886,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_score_miou_4shot",
    "value": 70.05817360253094,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_score_acc50_4shot",
    "value": 75.23316062176167,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_oracle_miou_4shot",
    "value": 76.99650307315515,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_oracle_acc50_4shot",
    "value": 83.21243523316062,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_invalid_4shot",
    "value": 93,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_delta_score_pp_4shot",
    "value": -6.759388703198821,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  }
]
```

### 关键结果
```json
[
  {
    "metric_id": "diag_q2old124_all_vqa_miou_1shot",
    "value": 70.98720046306559,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_vqa_acc50_1shot",
    "value": 77.42120343839541,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_score_miou_1shot",
    "value": 69.42985617220447,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_score_acc50_1shot",
    "value": 75.81661891117479,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_oracle_miou_1shot",
    "value": 75.95319130977694,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_oracle_acc50_1shot",
    "value": 83.32378223495702,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_invalid_1shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_delta_score_pp_1shot",
    "value": 1.557344290861118,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_vqa_miou_1shot",
    "value": 66.85139162399032,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_vqa_acc50_1shot",
    "value": 75.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_score_miou_1shot",
    "value": 65.37116103330052,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_score_acc50_1shot",
    "value": 73.66666666666667,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_oracle_miou_1shot",
    "value": 71.67223918508266,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_oracle_acc50_1shot",
    "value": 80.83333333333333,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_invalid_1shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_delta_score_pp_1shot",
    "value": 1.4802305906898017,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_vqa_miou_1shot",
    "value": 82.30688173062983,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_vqa_acc50_1shot",
    "value": 89.44444444444444,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_score_miou_1shot",
    "value": 79.59036041152275,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_score_acc50_1shot",
    "value": 86.11111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_oracle_miou_1shot",
    "value": 84.62972143842374,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_oracle_acc50_1shot",
    "value": 92.22222222222223,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_invalid_1shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_delta_score_pp_1shot",
    "value": 2.716521319107068,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_vqa_miou_1shot",
    "value": 71.44724468615739,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_vqa_acc50_1shot",
    "value": 76.68393782383419,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_score_miou_1shot",
    "value": 70.05817360253094,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_score_acc50_1shot",
    "value": 75.23316062176167,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_oracle_miou_1shot",
    "value": 76.99650307315515,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_oracle_acc50_1shot",
    "value": 83.21243523316062,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_invalid_1shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_delta_score_pp_1shot",
    "value": 1.3890710836264586,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_vqa_miou_1shot",
    "value": 71.09957077147594,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_vqa_acc50_1shot",
    "value": 77.53329473074696,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_score_miou_1shot",
    "value": 69.52599475088957,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_score_acc50_1shot",
    "value": 75.91198610306891,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_oracle_miou_1shot",
    "value": 76.11732064264632,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_oracle_acc50_1shot",
    "value": 83.4973943254198,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_invalid_1shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_delta_score_pp_1shot",
    "value": 1.5735760205863758,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_vqa_miou_1shot",
    "value": 67.05692248914723,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_vqa_acc50_1shot",
    "value": 75.25773195876289,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_score_miou_1shot",
    "value": 65.5309115709103,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_score_acc50_1shot",
    "value": 73.8831615120275,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_oracle_miou_1shot",
    "value": 72.02686842841769,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_oracle_acc50_1shot",
    "value": 81.27147766323024,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_invalid_1shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_delta_score_pp_1shot",
    "value": 1.5260109182369197,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_vqa_miou_1shot",
    "value": 82.30688173062983,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_vqa_acc50_1shot",
    "value": 89.44444444444444,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_score_miou_1shot",
    "value": 79.59036041152275,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_score_acc50_1shot",
    "value": 86.11111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_oracle_miou_1shot",
    "value": 84.62972143842374,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_oracle_acc50_1shot",
    "value": 92.22222222222223,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_invalid_1shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_delta_score_pp_1shot",
    "value": 2.716521319107068,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_vqa_miou_1shot",
    "value": 71.44724468615739,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_vqa_acc50_1shot",
    "value": 76.68393782383419,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_score_miou_1shot",
    "value": 70.05817360253094,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_score_acc50_1shot",
    "value": 75.23316062176167,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_oracle_miou_1shot",
    "value": 76.99650307315515,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_oracle_acc50_1shot",
    "value": 83.21243523316062,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_invalid_1shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_delta_score_pp_1shot",
    "value": 1.3890710836264586,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_vqa_miou_2shot",
    "value": 68.28444602803226,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_vqa_acc50_2shot",
    "value": 74.32664756446992,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_score_miou_2shot",
    "value": 69.42985617220447,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_score_acc50_2shot",
    "value": 75.81661891117479,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_oracle_miou_2shot",
    "value": 75.95319130977694,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_oracle_acc50_2shot",
    "value": 83.32378223495702,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_invalid_2shot",
    "value": 13,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_delta_score_pp_2shot",
    "value": -1.1454101441722098,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_vqa_miou_2shot",
    "value": 64.16441792849078,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_vqa_acc50_2shot",
    "value": 71.83333333333334,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_score_miou_2shot",
    "value": 65.37116103330052,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_score_acc50_2shot",
    "value": 73.66666666666667,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_oracle_miou_2shot",
    "value": 71.67223918508266,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_oracle_acc50_2shot",
    "value": 80.83333333333333,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_invalid_2shot",
    "value": 6,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_delta_score_pp_2shot",
    "value": -1.2067431048097377,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_vqa_miou_2shot",
    "value": 83.12890510394139,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_vqa_acc50_2shot",
    "value": 90.55555555555556,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_score_miou_2shot",
    "value": 79.59036041152275,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_score_acc50_2shot",
    "value": 86.11111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_oracle_miou_2shot",
    "value": 84.62972143842374,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_oracle_acc50_2shot",
    "value": 92.22222222222223,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_invalid_2shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_delta_score_pp_2shot",
    "value": 3.5385446924186326,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_vqa_miou_2shot",
    "value": 68.07720688405429,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_vqa_acc50_2shot",
    "value": 72.84974093264248,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_score_miou_2shot",
    "value": 70.05817360253094,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_score_acc50_2shot",
    "value": 75.23316062176167,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_oracle_miou_2shot",
    "value": 76.99650307315515,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_oracle_acc50_2shot",
    "value": 83.21243523316062,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_invalid_2shot",
    "value": 7,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_delta_score_pp_2shot",
    "value": -1.980966718476651,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_vqa_miou_2shot",
    "value": 68.49978704719805,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_vqa_acc50_2shot",
    "value": 74.5801968731905,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_score_miou_2shot",
    "value": 69.52599475088957,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_score_acc50_2shot",
    "value": 75.91198610306891,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_oracle_miou_2shot",
    "value": 76.11732064264632,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_oracle_acc50_2shot",
    "value": 83.4973943254198,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_invalid_2shot",
    "value": 13,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_delta_score_pp_2shot",
    "value": -1.0262077036915063,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_vqa_miou_2shot",
    "value": 64.67598740324607,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_vqa_acc50_2shot",
    "value": 72.5085910652921,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_score_miou_2shot",
    "value": 65.5309115709103,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_score_acc50_2shot",
    "value": 73.8831615120275,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_oracle_miou_2shot",
    "value": 72.02686842841769,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_oracle_acc50_2shot",
    "value": 81.27147766323024,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_invalid_2shot",
    "value": 6,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_delta_score_pp_2shot",
    "value": -0.8549241676642283,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_vqa_miou_2shot",
    "value": 83.12890510394139,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_vqa_acc50_2shot",
    "value": 90.55555555555556,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_score_miou_2shot",
    "value": 79.59036041152275,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_score_acc50_2shot",
    "value": 86.11111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_oracle_miou_2shot",
    "value": 84.62972143842374,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_oracle_acc50_2shot",
    "value": 92.22222222222223,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_invalid_2shot",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_delta_score_pp_2shot",
    "value": 3.5385446924186326,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_vqa_miou_2shot",
    "value": 68.07720688405429,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_vqa_acc50_2shot",
    "value": 72.84974093264248,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_score_miou_2shot",
    "value": 70.05817360253094,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_score_acc50_2shot",
    "value": 75.23316062176167,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_oracle_miou_2shot",
    "value": 76.99650307315515,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_oracle_acc50_2shot",
    "value": 83.21243523316062,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_invalid_2shot",
    "value": 7,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_delta_score_pp_2shot",
    "value": -1.980966718476651,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_vqa_miou_4shot",
    "value": 63.05745564259644,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_vqa_acc50_4shot",
    "value": 68.59598853868195,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_score_miou_4shot",
    "value": 69.42985617220447,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_score_acc50_4shot",
    "value": 75.81661891117479,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_oracle_miou_4shot",
    "value": 75.95319130977694,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_oracle_acc50_4shot",
    "value": 83.32378223495702,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_invalid_4shot",
    "value": 154,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_all_delta_score_pp_4shot",
    "value": -6.3724005296080355,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_vqa_miou_4shot",
    "value": 59.0227832324664,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_vqa_acc50_4shot",
    "value": 66.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_score_miou_4shot",
    "value": 65.37116103330052,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_score_acc50_4shot",
    "value": 73.66666666666667,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_oracle_miou_4shot",
    "value": 71.67223918508266,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_oracle_acc50_4shot",
    "value": 80.83333333333333,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_invalid_4shot",
    "value": 53,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_lasot_delta_score_pp_4shot",
    "value": -6.348377800834115,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_vqa_miou_4shot",
    "value": 75.21257071664161,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_vqa_acc50_4shot",
    "value": 81.66666666666667,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_score_miou_4shot",
    "value": 79.59036041152275,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_score_acc50_4shot",
    "value": 86.11111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_oracle_miou_4shot",
    "value": 84.62972143842374,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_oracle_acc50_4shot",
    "value": 92.22222222222223,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_invalid_4shot",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_got10k_delta_score_pp_4shot",
    "value": -4.37778969488114,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_vqa_miou_4shot",
    "value": 63.29878489933212,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_vqa_acc50_4shot",
    "value": 67.7720207253886,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_score_miou_4shot",
    "value": 70.05817360253094,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_score_acc50_4shot",
    "value": 75.23316062176167,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_oracle_miou_4shot",
    "value": 76.99650307315515,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_oracle_acc50_4shot",
    "value": 83.21243523316062,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_invalid_4shot",
    "value": 93,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_tao_delta_score_pp_4shot",
    "value": -6.759388703198821,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_vqa_miou_4shot",
    "value": 63.17422638665753,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_vqa_acc50_4shot",
    "value": 68.73190503763752,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_score_miou_4shot",
    "value": 69.52599475088957,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_score_acc50_4shot",
    "value": 75.91198610306891,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_oracle_miou_4shot",
    "value": 76.11732064264632,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_oracle_acc50_4shot",
    "value": 83.4973943254198,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_invalid_4shot",
    "value": 153,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_all_delta_score_pp_4shot",
    "value": -6.3517683642320355,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_vqa_miou_4shot",
    "value": 59.24449967853375,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_vqa_acc50_4shot",
    "value": 66.32302405498281,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_score_miou_4shot",
    "value": 65.5309115709103,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_score_acc50_4shot",
    "value": 73.8831615120275,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_oracle_miou_4shot",
    "value": 72.02686842841769,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_oracle_acc50_4shot",
    "value": 81.27147766323024,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_invalid_4shot",
    "value": 52,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_lasot_delta_score_pp_4shot",
    "value": -6.286411892376553,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_vqa_miou_4shot",
    "value": 75.21257071664161,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_vqa_acc50_4shot",
    "value": 81.66666666666667,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_score_miou_4shot",
    "value": 79.59036041152275,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_score_acc50_4shot",
    "value": 86.11111111111111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_oracle_miou_4shot",
    "value": 84.62972143842374,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_oracle_acc50_4shot",
    "value": 92.22222222222223,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_invalid_4shot",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_got10k_delta_score_pp_4shot",
    "value": -4.37778969488114,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_vqa_miou_4shot",
    "value": 63.29878489933212,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_vqa_acc50_4shot",
    "value": 67.7720207253886,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_score_miou_4shot",
    "value": 70.05817360253094,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_score_acc50_4shot",
    "value": 75.23316062176167,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_oracle_miou_4shot",
    "value": 76.99650307315515,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_oracle_acc50_4shot",
    "value": 83.21243523316062,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_invalid_4shot",
    "value": 93,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  },
  {
    "metric_id": "diag_q2old124_filtered_tao_delta_score_pp_4shot",
    "value": -6.759388703198821,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-cleanvqa-e014-124shot-now-20261027/metrics.json"
  }
]
```

### 分析
三档评测均exit0，逐条候选/ID/IoU及总体统计核验通过。以下为排除18已知训练原视频重合后的共同1727查询，mIoU（%）：

| 范围 | score | VQA 1shot | VQA 2shot | VQA 4shot | Oracle |
|---|---:|---:|---:|---:|---:|
| 总体（1727） | 69.53 | 71.10 | 68.50 | 63.17 | 76.12 |
| LaSOT（582） | 65.53 | 67.06 | 64.68 | 59.24 | 72.03 |
| GOT10k（180） | 79.59 | 82.31 | 83.13 | 75.21 | 84.63 |
| TAO（965） | 70.06 | 71.45 | 68.08 | 63.30 | 77.00 |

完整共同1745查询VQA mIoU为70.987200/68.284446/63.057456%；相应score69.429856、Oracle75.953191。排除重合后1shot相对score+1.573576pp，2shot−1.026208pp，4shot−6.351768pp；同1727查询旧Qwen3 VQA（1shot）72.220238%，新Qwen2 1shot低1.120668pp，模型、数据规模与训练预算同时变化，非模型版本单因素对照。

排除重合后的无效选择数1/2/4shot为0/13/153。2shot十三条均输出Reference 1或Reference 2；4shot148条输出候选范围外的3/4（88/60），另5条输出Reference X，均EOS结束，不是生成截断。提示多参考输入/编号适配异常；没有因此修改parser、回退score或重训。仅用于诊断的计算：若4shot无效项回退原score，总体可增加5.089593pp至68.2638%，仍低于原score69.525995%；这一数值不是正式VQA指标。有效回答上的错误选择也存在，不能把全部下降归因格式。

三个shot共享冻结E014原1shot proposal，只改变VQA参考帧数；原1766中21条TAO不足5标注帧排除，1745中18视频重合另报1727。报告不单列多框子集。GRPO保持取消（115步，最近checkpoint100），无新训练、推理或Claim升级。

### 局限
共同1745查询排除了21条参考不足TAO；18训练原视频重合另报1727。冻结E014原1shot proposal，仅改VQA参考数，旧探索集非E015当前作者划分。模型/数据/预算非单因素。诊断回退分数不是正式结果；不单列多框子集。

### Claim 边界
只改变VQA参考数，proposal仍冻结E014原1shot；旧探索集及源视频重合边界，不等同当前作者划分，不升级Claim。

### 产物索引
/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/.pi/analysis/e015/cleanvqa-e014-124shot-now-20261027/results_observation_20261028.json
/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/.pi/analysis/e015/cleanvqa-e014-124shot-now-20261027/prediction_audit_20261028.json
/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/.pi/analysis/e015/cleanvqa-e014-124shot-now-20261027/completion_20261028.json

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
