# e015-qwen2-vqa-actual-budget4096-r2-20261021 · 使用实际Qwen3 processor配置修正回归测试导入，继续CPU和五图预算验证。

- 父 Run：`e015-qwen2-vqa-actual-budget4096-20261021`
- 来源版本：2026-10-21T20:32:48
- 状态：analysis_pending
- Workspace：03

## 本次任务
使用实际Qwen3 processor配置修正回归测试导入，继续CPU和五图预算验证。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：校正实际视觉预算：Qwen2Fast的legacy min/max_pixels覆盖size导致之前测试实际每图10764/4784 rawpatch，不能声称4096；原SFT/selector更新和恢复事实保留但预算解释纠正。共享helper同时作用SFT/GRPO/eval；真实处理器CPU回归重现旧bug，检查5图实际grid≤4096并验证Qwen3像素输出不变。随后复用已训练短程selector，仅重跑8例五图VQA，检查真实grid和严格编号EOS；不报告合成候选mIoU为性能。正式SFT首次更新将验证校正后预算。 修正CPU回归fixture：真实Qwen3同样使用Qwen2VLImageProcessorFast，patch16/size-only，不存在独立Qwen3Fast类。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-vqa-actual-budget4096-r2-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'b9824d3fcff13ece7795441c1fa227ed75f1a0c966e531b5dc87ea94379fab8b'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：28c72afff503650316e37039c5931f2587b62b45
- 随机种子：11451
- 配置：tools/evaluate_candidate_vqa.py --model-family qwen2_vl --devices-per-replica 2
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-vqa-actual-budget4096-r2-20261021/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-vqa-actual-budget4096-r2-20261021/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-vqa-actual-budget4096-r2-20261021/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "passed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-vqa-actual-budget4096-r2-20261021/metrics.json"
  },
  {
    "metric_id": "model",
    "value": "Qwen2-VL-7B-Instruct",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-vqa-actual-budget4096-r2-20261021/metrics.json"
  },
  {
    "metric_id": "sft_parent",
    "value": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-sft-selector-ddp4x2-capability-20261021",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-vqa-actual-budget4096-r2-20261021/metrics.json"
  },
  {
    "metric_id": "results",
    "value": {
      "shot1": {
        "metrics_sha256": "1e77c37e23bfc6135ff1dfa495e9b5858f25dce48c28561068a896658667e595",
        "steps": 2,
        "peak_gpu_memory_gib_by_rank": [
          12.56752347946167,
          12.566938877105713,
          10.395349979400635,
          10.395349979400635
        ],
        "replica_consistency": [
          {
            "step": 0,
            "replicas": [
              {
                "rank": 0,
                "sha256": "27b33a4f39498f4f20ac40f78e9b8fe13ef784240b3ac3413054ad16f4efa268",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "27b33a4f39498f4f20ac40f78e9b8fe13ef784240b3ac3413054ad16f4efa268",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "27b33a4f39498f4f20ac40f78e9b8fe13ef784240b3ac3413054ad16f4efa268",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "27b33a4f39498f4f20ac40f78e9b8fe13ef784240b3ac3413054ad16f4efa268",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:6",
                  "cuda:7"
                ]
              }
            ],
            "passed": true
          },
          {
            "step": 1,
            "replicas": [
              {
                "rank": 0,
                "sha256": "2ba43c631ed6ec6c92752f2e57e3fbf4079ed1486bc871d48ce550758e8464de",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "2ba43c631ed6ec6c92752f2e57e3fbf4079ed1486bc871d48ce550758e8464de",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "2ba43c631ed6ec6c92752f2e57e3fbf4079ed1486bc871d48ce550758e8464de",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "2ba43c631ed6ec6c92752f2e57e3fbf4079ed1486bc871d48ce550758e8464de",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:6",
                  "cuda:7"
                ]
              }
            ],
            "passed": true
          },
          {
            "step": 2,
            "replicas": [
              {
                "rank": 0,
                "sha256": "18272e3192f428fa443f29ac421a7cf4727ef8d17360e702e8d0f56d9b408742",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "18272e3192f428fa443f29ac421a7cf4727ef8d17360e702e8d0f56d9b408742",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "18272e3192f428fa443f29ac421a7cf4727ef8d17360e702e8d0f56d9b408742",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "18272e3192f428fa443f29ac421a7cf4727ef8d17360e702e8d0f56d9b408742",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:6",
                  "cuda:7"
                ]
              }
            ],
            "passed": true
          }
        ]
      },
      "shot2": {
        "metrics_sha256": "ed3d52fddbdbf26a508d466abc5163bc872ee66e79396b94f1a8e81bc245f8b0",
        "steps": 2,
        "peak_gpu_memory_gib_by_rank": [
          14.540404796600342,
          14.539085388183594,
          11.28208065032959,
          11.28208065032959
        ],
        "replica_consistency": [
          {
            "step": 0,
            "replicas": [
              {
                "rank": 0,
                "sha256": "27b33a4f39498f4f20ac40f78e9b8fe13ef784240b3ac3413054ad16f4efa268",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "27b33a4f39498f4f20ac40f78e9b8fe13ef784240b3ac3413054ad16f4efa268",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "27b33a4f39498f4f20ac40f78e9b8fe13ef784240b3ac3413054ad16f4efa268",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "27b33a4f39498f4f20ac40f78e9b8fe13ef784240b3ac3413054ad16f4efa268",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:6",
                  "cuda:7"
                ]
              }
            ],
            "passed": true
          },
          {
            "step": 1,
            "replicas": [
              {
                "rank": 0,
                "sha256": "a9c2c277eb5973e0a05b6072806354f146070d09e573952d5269cca04a14ce5c",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "a9c2c277eb5973e0a05b6072806354f146070d09e573952d5269cca04a14ce5c",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "a9c2c277eb5973e0a05b6072806354f146070d09e573952d5269cca04a14ce5c",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "a9c2c277eb5973e0a05b6072806354f146070d09e573952d5269cca04a14ce5c",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:6",
                  "cuda:7"
                ]
              }
            ],
            "passed": true
          },
          {
            "step": 2,
            "replicas": [
              {
                "rank": 0,
                "sha256": "271e518aec09bd77a01f8761b6cfb7f65fbd87f486f5774f6d08842e98d171d9",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "271e518aec09bd77a01f8761b6cfb7f65fbd87f486f5774f6d08842e98d171d9",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "271e518aec09bd77a01f8761b6cfb7f65fbd87f486f5774f6d08842e98d171d9",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "271e518aec09bd77a01f8761b6cfb7f65fbd87f486f5774f6d08842e98d171d9",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:6",
                  "cuda:7"
                ]
              }
            ],
            "passed": true
          }
        ]
      },
      "shot4": {
        "metrics_sha256": "92ea5c0845bc176cce3b1a94de0ab0de473ee47118ca905d6f72ef341a36a8b4",
        "steps": 2,
        "peak_gpu_memory_gib_by_rank": [
          18.490792274475098,
          18.49037456512451,
          13.060842990875244,
          13.060842990875244
        ],
        "replica_consistency": [
          {
            "step": 0,
            "replicas": [
              {
                "rank": 0,
                "sha256": "27b33a4f39498f4f20ac40f78e9b8fe13ef784240b3ac3413054ad16f4efa268",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "27b33a4f39498f4f20ac40f78e9b8fe13ef784240b3ac3413054ad16f4efa268",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "27b33a4f39498f4f20ac40f78e9b8fe13ef784240b3ac3413054ad16f4efa268",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "27b33a4f39498f4f20ac40f78e9b8fe13ef784240b3ac3413054ad16f4efa268",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:6",
                  "cuda:7"
                ]
              }
            ],
            "passed": true
          },
          {
            "step": 1,
            "replicas": [
              {
                "rank": 0,
                "sha256": "ebec137ec44673840073b6186dc2133f6fe513737c2f27e797f3a1ddd73082a4",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "ebec137ec44673840073b6186dc2133f6fe513737c2f27e797f3a1ddd73082a4",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "ebec137ec44673840073b6186dc2133f6fe513737c2f27e797f3a1ddd73082a4",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "ebec137ec44673840073b6186dc2133f6fe513737c2f27e797f3a1ddd73082a4",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:6",
                  "cuda:7"
                ]
              }
            ],
            "passed": true
          },
          {
            "step": 2,
            "replicas": [
              {
                "rank": 0,
                "sha256": "3f0aa098f0c8555ef8c44eec37ed80d73876dc794a7db0fe96c7bd4321d3b28f",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "3f0aa098f0c8555ef8c44eec37ed80d73876dc794a7db0fe96c7bd4321d3b28f",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "3f0aa098f0c8555ef8c44eec37ed80d73876dc794a7db0fe96c7bd4321d3b28f",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "3f0aa098f0c8555ef8c44eec37ed80d73876dc794a7db0fe96c7bd4321d3b28f",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:6",
                  "cuda:7"
                ]
              }
            ],
            "passed": true
          }
        ]
      },
      "shot4_resume": {
        "metrics_sha256": "7c6a513cfe34d61c94f7832b5ac5effb10145325af63f016a7b397b325bc04ff",
        "steps": 3,
        "peak_gpu_memory_gib_by_rank": [
          18.490452766418457,
          18.48959255218506,
          13.059812545776367,
          13.059812545776367
        ],
        "replica_consistency": [
          {
            "step": 2,
            "replicas": [
              {
                "rank": 0,
                "sha256": "3f0aa098f0c8555ef8c44eec37ed80d73876dc794a7db0fe96c7bd4321d3b28f",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "3f0aa098f0c8555ef8c44eec37ed80d73876dc794a7db0fe96c7bd4321d3b28f",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "3f0aa098f0c8555ef8c44eec37ed80d73876dc794a7db0fe96c7bd4321d3b28f",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "3f0aa098f0c8555ef8c44eec37ed80d73876dc794a7db0fe96c7bd4321d3b28f",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:6",
                  "cuda:7"
                ]
              }
            ],
            "passed": true
          },
          {
            "step": 3,
            "replicas": [
              {
                "rank": 0,
                "sha256": "47a30592e31d2fab7a15f0295523fa6846b43de2d93a19b7d748feb539a4cc28",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "47a30592e31d2fab7a15f0295523fa6846b43de2d93a19b7d748feb539a4cc28",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "47a30592e31d2fab7a15f0295523fa6846b43de2d93a19b7d748feb539a4cc28",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "47a30592e31d2fab7a15f0295523fa6846b43de2d93a19b7d748feb539a4cc28",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:6",
                  "cuda:7"
                ]
              }
            ],
            "passed": true
          }
        ]
      },
      "selector": {
        "metrics_sha256": "4ac0cdd273b6b9610f72f8a482558121b5b6a91356aa0d5ce11a3a9779debfdd",
        "steps": 2,
        "peak_gpu_memory_gib_by_rank": [
          18.540510177612305,
          18.539060592651367,
          13.110541343688965,
          13.110541343688965
        ],
        "replica_consistency": [
          {
            "step": 0,
            "replicas": [
              {
                "rank": 0,
                "sha256": "27b33a4f39498f4f20ac40f78e9b8fe13ef784240b3ac3413054ad16f4efa268",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "27b33a4f39498f4f20ac40f78e9b8fe13ef784240b3ac3413054ad16f4efa268",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "27b33a4f39498f4f20ac40f78e9b8fe13ef784240b3ac3413054ad16f4efa268",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "27b33a4f39498f4f20ac40f78e9b8fe13ef784240b3ac3413054ad16f4efa268",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:6",
                  "cuda:7"
                ]
              }
            ],
            "passed": true
          },
          {
            "step": 1,
            "replicas": [
              {
                "rank": 0,
                "sha256": "abba23db0196b9defd19f145f1d863c19e5dcf7d84edecc573ab0b0810e36f36",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "abba23db0196b9defd19f145f1d863c19e5dcf7d84edecc573ab0b0810e36f36",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "abba23db0196b9defd19f145f1d863c19e5dcf7d84edecc573ab0b0810e36f36",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "abba23db0196b9defd19f145f1d863c19e5dcf7d84edecc573ab0b0810e36f36",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:6",
                  "cuda:7"
                ]
              }
            ],
            "passed": true
          },
          {
            "step": 2,
            "replicas": [
              {
                "rank": 0,
                "sha256": "ca362325ea2ad0f16b38588651fdeb8248d32cfd7a5cae82d374bba6667f5471",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "ca362325ea2ad0f16b38588651fdeb8248d32cfd7a5cae82d374bba6667f5471",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "ca362325ea2ad0f16b38588651fdeb8248d32cfd7a5cae82d374bba6667f5471",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "ca362325ea2ad0f16b38588651fdeb8248d32cfd7a5cae82d374bba6667f5471",
                "trainable_numel": 20185088,
                "devices": [
                  "cuda:6",
                  "cuda:7"
                ]
              }
            ],
            "passed": true
          }
        ]
      },
      "vqa": {
        "samples": 8,
        "actual_images_per_call": 5,
        "valid_answers": 8,
        "metrics_sha256": "80f7465bd092c229d412558ff5c7c932b2c3acb46f705bc19b94c20aa0c192dc"
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-vqa-actual-budget4096-r2-20261021/metrics.json"
  },
  {
    "metric_id": "limitations",
    "value": "Previous SFT/selector size-only settings were overridden by Qwen2 legacy pixel fields, so prior training peaks do not establish the intended4096 budget. Corrected SFT budget is checked by real processor tests and formal training guards. SFT evidence reused from four passed stages of a Run whose selector initialization failed; selector evidence reused from its passed stage; inference checked here. Eight videos, synthetic candidates, no performance or GRPO GPU conclusion.",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-vqa-actual-budget4096-r2-20261021/metrics.json"
  }
]
```

### 分析
9项相关CPU回归通过。GPU VQA实际8例、每例5图，全部4032rawpatch/图≤4096，8合法编号EOS；NCCL早期barrier问题已解决。复核既有SFT1/2/4shot、恢复和selector真实更新与副本哈希，但那些训练的size-only预算未生效，显存峰值不能解释为4096设置。正式SFT将依靠新增实际grid守卫及首步验证。

### 局限
合成候选工程验证，不构成定位性能；先前SFT能力实际部分10764rawpatch。没有GRPO真实GPU结果，正式全链尚待执行。

### Claim 边界
仅八视频短程工程能力，非正式性能或GRPO能力。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-vqa-actual-budget4096-r2-20261021/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-vqa-actual-budget4096-r2-20261021/managed_console.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
