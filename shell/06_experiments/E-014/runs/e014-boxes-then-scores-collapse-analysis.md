# e014-boxes-then-scores-collapse-analysis · 用户要求分析新协议多框为何消失。对已停止的184步rollout做一次CPU离线诊断：分阶段合法/原始多框、长度/截断、同prompt组优势、奖励分解和固定候选

- 父 Run：`e014-boxes-then-scores-beta0-sft659-seed11451`
- 来源版本：2026-10-15T15:14:21
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户要求分析新协议多框为何消失。对已停止的184步rollout做一次CPU离线诊断：分阶段合法/原始多框、长度/截断、同prompt组优势、奖励分解和固定候选删框反事实。不新推理、不改奖励、不恢复训练；仅机制假设，不做因果Claim。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：一次性CPU分析脚本位于Run根，读取唯一父训练8rank完整rollout，184更新；固定输入分组与删框奖励反事实，输出聚合metrics/source_hashes/examples。不加载模型或修改训练，不继承Solid结论；脚本AST及计算定义静态审阅，未测试。
- 命令：python /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-boxes-then-scores-collapse-analysis/analyze.py
- 代码版本：41698665d15742276bf22d1376e8d53a367c07db
- 随机种子：11451
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-boxes-then-scores-collapse-analysis/logs/run.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-boxes-then-scores-collapse-analysis/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-boxes-then-scores-collapse-analysis/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "rows",
    "value": 11776,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-boxes-then-scores-collapse-analysis/metrics.json"
  },
  {
    "metric_id": "groups",
    "value": 2944,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-boxes-then-scores-collapse-analysis/metrics.json"
  },
  {
    "metric_id": "updates",
    "value": 184,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-boxes-then-scores-collapse-analysis/metrics.json"
  },
  {
    "metric_id": "bands",
    "value": {
      "1-5": {
        "n": 320,
        "valid": 251,
        "multi": 25,
        "raw_multi": 88,
        "not_terminated": 47,
        "tokens": 62.334375,
        "reward": 1.4596483776252516,
        "advantage": 1.8539285520091653e-07,
        "positive_advantage": 141,
        "order_violations": 11,
        "max_score_error": 0.36488725099601593,
        "valid_pos_n": 181,
        "selected_iou": 0.6135516620998923,
        "oracle_iou": 0.6540365940191211
      },
      "6-10": {
        "n": 320,
        "valid": 313,
        "multi": 2,
        "raw_multi": 2,
        "not_terminated": 0,
        "tokens": 31.825,
        "reward": 2.090785666905932,
        "advantage": 4.4370244722813367e-08,
        "positive_advantage": 180,
        "order_violations": 0,
        "max_score_error": 0.30088753993610223,
        "valid_pos_n": 218,
        "selected_iou": 0.5612247404123772,
        "oracle_iou": 0.5612247404123772
      },
      "11-20": {
        "n": 640,
        "valid": 637,
        "multi": 49,
        "raw_multi": 51,
        "not_terminated": 0,
        "tokens": 34.8546875,
        "reward": 2.1861661212913117,
        "advantage": 1.3069802662357688e-07,
        "positive_advantage": 348,
        "order_violations": 12,
        "max_score_error": 0.283858398744113,
        "valid_pos_n": 478,
        "selected_iou": 0.5539453925239318,
        "oracle_iou": 0.588235811077334
      },
      "21-50": {
        "n": 1920,
        "valid": 1907,
        "multi": 0,
        "raw_multi": 0,
        "not_terminated": 0,
        "tokens": 31.857291666666665,
        "reward": 2.2486960515822445,
        "advantage": -8.085416432853283e-06,
        "positive_advantage": 1035,
        "order_violations": 0,
        "max_score_error": 0.26349669638175144,
        "valid_pos_n": 1442,
        "selected_iou": 0.6092464903175517,
        "oracle_iou": 0.6092464903175517
      },
      "51-100": {
        "n": 3200,
        "valid": 3182,
        "multi": 0,
        "raw_multi": 0,
        "not_terminated": 0,
        "tokens": 31.7753125,
        "reward": 2.454881444668789,
        "advantage": -1.7761106209945865e-06,
        "positive_advantage": 1327,
        "order_violations": 0,
        "max_score_error": 0.14337840980515398,
        "valid_pos_n": 2341,
        "selected_iou": 0.7233121456386696,
        "oracle_iou": 0.7233121456386696
      },
      "101-150": {
        "n": 3200,
        "valid": 3195,
        "multi": 2,
        "raw_multi": 2,
        "not_terminated": 0,
        "tokens": 31.8784375,
        "reward": 2.4811919565656266,
        "advantage": -1.2811393753509036e-06,
        "positive_advantage": 1227,
        "order_violations": 0,
        "max_score_error": 0.13443073552425666,
        "valid_pos_n": 2351,
        "selected_iou": 0.7264019910718865,
        "oracle_iou": 0.7267860762804546
      },
      "151-184": {
        "n": 2176,
        "valid": 2175,
        "multi": 0,
        "raw_multi": 0,
        "not_terminated": 0,
        "tokens": 31.776194852941178,
        "reward": 2.4819612173992587,
        "advantage": -4.4870054861188264e-07,
        "positive_advantage": 793,
        "order_violations": 0,
        "max_score_error": 0.15210206896551723,
        "valid_pos_n": 1639,
        "selected_iou": 0.7310261190120725,
        "oracle_iou": 0.7310261190120725
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-boxes-then-scores-collapse-analysis/metrics.json"
  },
  {
    "metric_id": "classes",
    "value": {
      "valid_single": {
        "n": 11582,
        "valid": 11582,
        "multi": 0,
        "raw_multi": 0,
        "not_terminated": 0,
        "tokens": 31.838801588672077,
        "reward": 2.419018436166432,
        "advantage": 0.007960952625288712,
        "positive_advantage": 5008,
        "order_violations": 0,
        "max_score_error": 0.17678829217751685,
        "valid_pos_n": 8579,
        "selected_iou": 0.6932264515304368,
        "oracle_iou": 0.6932264515304368
      },
      "valid_multi": {
        "n": 78,
        "valid": 78,
        "multi": 78,
        "raw_multi": 78,
        "not_terminated": 0,
        "tokens": 71.43589743589743,
        "reward": 1.896058926225997,
        "advantage": -0.00037092314316676214,
        "positive_advantage": 43,
        "order_violations": 23,
        "max_score_error": 0.4880358974358974,
        "valid_pos_n": 71,
        "selected_iou": 0.4045926231778558,
        "oracle_iou": 0.7513753988292651
      },
      "invalid_raw_multi": {
        "n": 65,
        "valid": 0,
        "multi": 0,
        "raw_multi": 65,
        "not_terminated": 46,
        "tokens": 163.75384615384615,
        "reward": -1.0,
        "advantage": -0.4022416362395653,
        "positive_advantage": 0,
        "order_violations": 0,
        "max_score_error": null,
        "valid_pos_n": 0,
        "selected_iou": null,
        "oracle_iou": null
      },
      "invalid_other": {
        "n": 51,
        "valid": 0,
        "multi": 0,
        "raw_multi": 0,
        "not_terminated": 1,
        "tokens": 28.784313725490197,
        "reward": -1.0,
        "advantage": -1.2952008107129265,
        "positive_advantage": 0,
        "order_violations": 0,
        "max_score_error": null,
        "valid_pos_n": 0,
        "selected_iou": null,
        "oracle_iou": null
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-boxes-then-scores-collapse-analysis/metrics.json"
  },
  {
    "metric_id": "matched_valid_single_multi",
    "value": {
      "n": 28,
      "means": {
        "total": -0.4616631394596908,
        "structure_reward": -0.00785714285714286,
        "score_reward": -0.2653738095238095,
        "iou_reward": -0.16189480612635748,
        "multi_advantage": -0.5320317138518605,
        "single_advantage": 0.3926591795115244
      },
      "multi_reward_wins": 6
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-boxes-then-scores-collapse-analysis/metrics.json"
  },
  {
    "metric_id": "matched_all_valid_groups",
    "value": {
      "n": 24,
      "means": {
        "total": -0.46906813087247645,
        "structure_reward": -0.00916666666666667,
        "score_reward": -0.24281527777777775,
        "iou_reward": -0.19280465865025426,
        "multi_advantage": -0.710597732414802,
        "single_advantage": 0.32093995271457565
      },
      "multi_reward_wins": 6
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-boxes-then-scores-collapse-analysis/metrics.json"
  },
  {
    "metric_id": "matched_raw_multi",
    "value": {
      "n": 32,
      "means": {
        "reward_delta": -0.9684779489116212,
        "raw_multi_advantage": -0.7276679550608
      },
      "multi_reward_wins": 6
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-boxes-then-scores-collapse-analysis/metrics.json"
  },
  {
    "metric_id": "fixed_candidate_counterfactual",
    "value": {
      "n": 78,
      "means": {
        "total_delta_vs_first": -0.21559760757835875,
        "structure_delta": -0.03538461538461538,
        "score_delta": -0.2564776923076923,
        "iou_delta": 0.076264700113949,
        "selected_only_gain": 0.19287217948717952,
        "coverage_gain": 0.39192594461715485,
        "selected_nonfirst": 0.5,
        "positive": 0.9102564102564102
      },
      "better_than_first": 16,
      "worse_than_first": 46,
      "equal_to_first": 16,
      "coverage_improved": 37,
      "selected_iou_improved": 18,
      "selected_only_strictly_better": 40
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-boxes-then-scores-collapse-analysis/metrics.json"
  },
  {
    "metric_id": "invalid_reasons",
    "value": {
      "not_terminated": 47,
      "invalid_bbox_score_protocol": 69
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-boxes-then-scores-collapse-analysis/metrics.json"
  },
  {
    "metric_id": "advantage_max_recompute_error",
    "value": 0.0037198623232166383,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-boxes-then-scores-collapse-analysis/metrics.json"
  },
  {
    "metric_id": "by_source",
    "value": {
      "collage": {
        "n": 5664,
        "valid": 5607,
        "multi": 61,
        "raw_multi": 104,
        "not_terminated": 26,
        "tokens": 33.18485169491525,
        "reward": 2.5217409488597022,
        "advantage": -1.1974690317345315e-06,
        "positive_advantage": 2837,
        "order_violations": 15,
        "max_score_error": 0.19147108970929194,
        "valid_pos_n": 5607,
        "selected_iou": 0.6684817147032911,
        "oracle_iou": 0.6726908339506953
      },
      "original": {
        "n": 6112,
        "valid": 6053,
        "multi": 17,
        "raw_multi": 39,
        "not_terminated": 21,
        "tokens": 32.47414921465968,
        "reward": 2.2522616802329667,
        "advantage": -3.164911061584467e-06,
        "positive_advantage": 2214,
        "order_violations": 8,
        "max_score_error": 0.1671981496778457,
        "valid_pos_n": 3043,
        "selected_iou": 0.7320863718645719,
        "oracle_iou": 0.7324219109546327
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-boxes-then-scores-collapse-analysis/metrics.json"
  }
]
```

### 分析
已完成父训练184步11776rollout/2944个完整G4组的离线分析。21..100共5120条原始/合法多框0；101..150仅2/3200；151..184为0/2176。78合法多框、65非法原始多框（46未终止）。28个同prompt合法单/多混合组中，多框相对单框平均reward差-.461663，score原始项差-.265374（权重1.1后-.291911）、IoU差-.161895、结构差-.007857；多框logged advantage-.532032、单框+.392659，6/28组多框reward更高。24个整组全合法组中差-.469068，多框advantage-.710598。71合法正样本多框Selected .404593/Oracle .751375。78条固定生成候选保留第一框的奖励反事实：完整多框16更好/46更差/16相同，平均delta-.215598，其中score-.256478、结构-.035385、IoU+.076265；37条覆盖改善，18条Selected改善。示例step12 IoU[0,.755915]/score[.45,.31]选错，完整reward1.57629，相比只保留第一框降低.30096。证据支持早期未完成惩罚、评分收益未兑现和序列级共同强化促成单框收敛；beta0仍发生故KL不是必要条件，未证明关闭KL无影响。

### 局限
观察性日志与固定候选删框奖励反事实，不是重新生成或重训的因果消融；不能保证模型可直接单框生成原选中框。合法多框集中早期、同prompt混合仅28组，整体单/多均值有时间和难度混杂。优势使用日志原值；Python双精度复算与训练float32最大差.00372，不能称逐值精确复现。未测试/新模型推理，未改奖励、训练或Claim；本Run无Solid结论。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-boxes-then-scores-collapse-analysis/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-boxes-then-scores-collapse-analysis/source_hashes.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-boxes-then-scores-collapse-analysis/examples.json

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
