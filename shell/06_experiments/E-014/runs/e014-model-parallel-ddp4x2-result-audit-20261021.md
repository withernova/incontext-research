# e014-model-parallel-ddp4x2-result-audit-20261021 · 继续完成用户要求的4×2 DDP能力验证：只读既有4×2 DDP短程GPU训练产物的CPU审计；不新增训练/模型推理/部署。父Run的汇总脚本错误地要求q_pr

- 父 Run：`e014-model-parallel-ddp4x2-bf16-20261021`
- 来源版本：2026-10-21T18:19:46
- 状态：analysis_pending
- Workspace：03

## 本次任务
继续完成用户要求的4×2 DDP能力验证：只读既有4×2 DDP短程GPU训练产物的CPU审计；不新增训练/模型推理/部署。父Run的汇总脚本错误地要求q_proj输出必须BF16，实际首尾层均为FP32，即使显式embedding BF16与autocast已启用。保留父Run终态和错误，单独核验1/2/4shot各2步和4shot恢复step3、112呈现、有限梯度、全LoRA跨rank SHA一致、恢复SHA连续、四组独占GPU、实际code/config快照、逐卡memory及原样记录FP32；不声称attention内部dtype或单独精度机制因果。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：只读既有4×2 DDP短程GPU训练产物的CPU审计；不新增训练/模型推理/部署。父Run的汇总脚本错误地要求q_proj输出必须BF16，实际首尾层均为FP32，即使显式embedding BF16与autocast已启用。保留父Run终态和错误，单独核验1/2/4shot各2步和4shot恢复step3、112呈现、有限梯度、全LoRA跨rank SHA一致、恢复SHA连续、四组独占GPU、实际code/config快照、逐卡memory及原样记录FP32；不声称attention内部dtype或单独精度机制因果。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-result-audit-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'9b6b67dd23ea8744c800c48510cd878c8d1084fad646131ea176369a247e335a'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：f3497cad782e03a8b80c5bac581b987e501cd31f
- 随机种子：20260901
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-result-audit-20261021/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-result-audit-20261021/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-result-audit-20261021/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "passed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-result-audit-20261021/metrics.json"
  },
  {
    "metric_id": "training_capability_passed",
    "value": true,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-result-audit-20261021/metrics.json"
  },
  {
    "metric_id": "qproj_bf16_expectation_met",
    "value": false,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-result-audit-20261021/metrics.json"
  },
  {
    "metric_id": "source_run",
    "value": "e014-model-parallel-ddp4x2-bf16-20261021",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-result-audit-20261021/metrics.json"
  },
  {
    "metric_id": "audit_note",
    "value": "Parent GPU arms completed successfully; parent postprocessing rejected FP32 q_proj outputs. This audit records observed FP32 explicitly; it does not claim BF16 attention inputs or alter source artifacts.",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-result-audit-20261021/metrics.json"
  },
  {
    "metric_id": "git_commit",
    "value": "f3497cad782e03a8b80c5bac581b987e501cd31f",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-result-audit-20261021/metrics.json"
  },
  {
    "metric_id": "model",
    "value": "Qwen3-VL-8B-Instruct",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-result-audit-20261021/metrics.json"
  },
  {
    "metric_id": "replicas",
    "value": 4,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-result-audit-20261021/metrics.json"
  },
  {
    "metric_id": "devices_per_replica",
    "value": 2,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-result-audit-20261021/metrics.json"
  },
  {
    "metric_id": "shot_counts",
    "value": [
      1,
      2,
      4
    ],
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-result-audit-20261021/metrics.json"
  },
  {
    "metric_id": "raw_patch_budget_per_image",
    "value": 4096,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-result-audit-20261021/metrics.json"
  },
  {
    "metric_id": "results",
    "value": {
      "shot1": {
        "steps": 2,
        "session_examples_seen": 32,
        "loss_before": 1.3082141280174255,
        "loss_after": 0.7661198079586029,
        "attention_projection_dtypes": [
          {
            "module.base_model.model.model.language_model.layers.0.self_attn.q_proj": [
              "torch.float32"
            ],
            "module.base_model.model.model.language_model.layers.35.self_attn.q_proj": [
              "torch.float32"
            ]
          },
          {
            "module.base_model.model.model.language_model.layers.0.self_attn.q_proj": [
              "torch.float32"
            ],
            "module.base_model.model.model.language_model.layers.35.self_attn.q_proj": [
              "torch.float32"
            ]
          },
          {
            "module.base_model.model.model.language_model.layers.0.self_attn.q_proj": [
              "torch.float32"
            ],
            "module.base_model.model.model.language_model.layers.35.self_attn.q_proj": [
              "torch.float32"
            ]
          },
          {
            "module.base_model.model.model.language_model.layers.0.self_attn.q_proj": [
              "torch.float32"
            ],
            "module.base_model.model.model.language_model.layers.35.self_attn.q_proj": [
              "torch.float32"
            ]
          }
        ],
        "memory": [
          {
            "rank": 0,
            "devices": [
              0,
              1
            ],
            "allocated_gib": [
              7.1590399742126465,
              11.082329273223877
            ],
            "reserved_gib": [
              7.619140625,
              11.80078125
            ],
            "device_map": {
              "model.visual": 0,
              "model.language_model.embed_tokens": 0,
              "model.language_model.norm": 1,
              "model.language_model.rotary_emb": 0,
              "lm_head": 1,
              "model.language_model.layers.0": 0,
              "model.language_model.layers.1": 0,
              "model.language_model.layers.2": 0,
              "model.language_model.layers.3": 0,
              "model.language_model.layers.4": 0,
              "model.language_model.layers.5": 0,
              "model.language_model.layers.6": 0,
              "model.language_model.layers.7": 0,
              "model.language_model.layers.8": 0,
              "model.language_model.layers.9": 0,
              "model.language_model.layers.10": 0,
              "model.language_model.layers.11": 0,
              "model.language_model.layers.12": 0,
              "model.language_model.layers.13": 0,
              "model.language_model.layers.14": 1,
              "model.language_model.layers.15": 1,
              "model.language_model.layers.16": 1,
              "model.language_model.layers.17": 1,
              "model.language_model.layers.18": 1,
              "model.language_model.layers.19": 1,
              "model.language_model.layers.20": 1,
              "model.language_model.layers.21": 1,
              "model.language_model.layers.22": 1,
              "model.language_model.layers.23": 1,
              "model.language_model.layers.24": 1,
              "model.language_model.layers.25": 1,
              "model.language_model.layers.26": 1,
              "model.language_model.layers.27": 1,
              "model.language_model.layers.28": 1,
              "model.language_model.layers.29": 1,
              "model.language_model.layers.30": 1,
              "model.language_model.layers.31": 1,
              "model.language_model.layers.32": 1,
              "model.language_model.layers.33": 1,
              "model.language_model.layers.34": 1,
              "model.language_model.layers.35": 1
            }
          },
          {
            "rank": 1,
            "devices": [
              2,
              3
            ],
            "allocated_gib": [
              7.158267974853516,
              11.08056354522705
            ],
            "reserved_gib": [
              7.619140625,
              11.80078125
            ],
            "device_map": {
              "model.visual": 2,
              "model.language_model.embed_tokens": 2,
              "model.language_model.norm": 3,
              "model.language_model.rotary_emb": 2,
              "lm_head": 3,
              "model.language_model.layers.0": 2,
              "model.language_model.layers.1": 2,
              "model.language_model.layers.2": 2,
              "model.language_model.layers.3": 2,
              "model.language_model.layers.4": 2,
              "model.language_model.layers.5": 2,
              "model.language_model.layers.6": 2,
              "model.language_model.layers.7": 2,
              "model.language_model.layers.8": 2,
              "model.language_model.layers.9": 2,
              "model.language_model.layers.10": 2,
              "model.language_model.layers.11": 2,
              "model.language_model.layers.12": 2,
              "model.language_model.layers.13": 2,
              "model.language_model.layers.14": 3,
              "model.language_model.layers.15": 3,
              "model.language_model.layers.16": 3,
              "model.language_model.layers.17": 3,
              "model.language_model.layers.18": 3,
              "model.language_model.layers.19": 3,
              "model.language_model.layers.20": 3,
              "model.language_model.layers.21": 3,
              "model.language_model.layers.22": 3,
              "model.language_model.layers.23": 3,
              "model.language_model.layers.24": 3,
              "model.language_model.layers.25": 3,
              "model.language_model.layers.26": 3,
              "model.language_model.layers.27": 3,
              "model.language_model.layers.28": 3,
              "model.language_model.layers.29": 3,
              "model.language_model.layers.30": 3,
              "model.language_model.layers.31": 3,
              "model.language_model.layers.32": 3,
              "model.language_model.layers.33": 3,
              "model.language_model.layers.34": 3,
              "model.language_model.layers.35": 3
            }
          },
          {
            "rank": 2,
            "devices": [
              4,
              5
            ],
            "allocated_gib": [
              7.008448600769043,
              10.99346113204956
            ],
            "reserved_gib": [
              7.416015625,
              11.802734375
            ],
            "device_map": {
              "model.visual": 4,
              "model.language_model.embed_tokens": 4,
              "model.language_model.norm": 5,
              "model.language_model.rotary_emb": 4,
              "lm_head": 5,
              "model.language_model.layers.0": 4,
              "model.language_model.layers.1": 4,
              "model.language_model.layers.2": 4,
              "model.language_model.layers.3": 4,
              "model.language_model.layers.4": 4,
              "model.language_model.layers.5": 4,
              "model.language_model.layers.6": 4,
              "model.language_model.layers.7": 4,
              "model.language_model.layers.8": 4,
              "model.language_model.layers.9": 4,
              "model.language_model.layers.10": 4,
              "model.language_model.layers.11": 4,
              "model.language_model.layers.12": 4,
              "model.language_model.layers.13": 4,
              "model.language_model.layers.14": 5,
              "model.language_model.layers.15": 5,
              "model.language_model.layers.16": 5,
              "model.language_model.layers.17": 5,
              "model.language_model.layers.18": 5,
              "model.language_model.layers.19": 5,
              "model.language_model.layers.20": 5,
              "model.language_model.layers.21": 5,
              "model.language_model.layers.22": 5,
              "model.language_model.layers.23": 5,
              "model.language_model.layers.24": 5,
              "model.language_model.layers.25": 5,
              "model.language_model.layers.26": 5,
              "model.language_model.layers.27": 5,
              "model.language_model.layers.28": 5,
              "model.language_model.layers.29": 5,
              "model.language_model.layers.30": 5,
              "model.language_model.layers.31": 5,
              "model.language_model.layers.32": 5,
              "model.language_model.layers.33": 5,
              "model.language_model.layers.34": 5,
              "model.language_model.layers.35": 5
            }
          },
          {
            "rank": 3,
            "devices": [
              6,
              7
            ],
            "allocated_gib": [
              7.008448600769043,
              10.99346113204956
            ],
            "reserved_gib": [
              7.416015625,
              11.802734375
            ],
            "device_map": {
              "model.visual": 6,
              "model.language_model.embed_tokens": 6,
              "model.language_model.norm": 7,
              "model.language_model.rotary_emb": 6,
              "lm_head": 7,
              "model.language_model.layers.0": 6,
              "model.language_model.layers.1": 6,
              "model.language_model.layers.2": 6,
              "model.language_model.layers.3": 6,
              "model.language_model.layers.4": 6,
              "model.language_model.layers.5": 6,
              "model.language_model.layers.6": 6,
              "model.language_model.layers.7": 6,
              "model.language_model.layers.8": 6,
              "model.language_model.layers.9": 6,
              "model.language_model.layers.10": 6,
              "model.language_model.layers.11": 6,
              "model.language_model.layers.12": 6,
              "model.language_model.layers.13": 6,
              "model.language_model.layers.14": 7,
              "model.language_model.layers.15": 7,
              "model.language_model.layers.16": 7,
              "model.language_model.layers.17": 7,
              "model.language_model.layers.18": 7,
              "model.language_model.layers.19": 7,
              "model.language_model.layers.20": 7,
              "model.language_model.layers.21": 7,
              "model.language_model.layers.22": 7,
              "model.language_model.layers.23": 7,
              "model.language_model.layers.24": 7,
              "model.language_model.layers.25": 7,
              "model.language_model.layers.26": 7,
              "model.language_model.layers.27": 7,
              "model.language_model.layers.28": 7,
              "model.language_model.layers.29": 7,
              "model.language_model.layers.30": 7,
              "model.language_model.layers.31": 7,
              "model.language_model.layers.32": 7,
              "model.language_model.layers.33": 7,
              "model.language_model.layers.34": 7,
              "model.language_model.layers.35": 7
            }
          }
        ],
        "consistency": [
          {
            "step": 0,
            "replicas": [
              {
                "rank": 0,
                "sha256": "571ba57907b660cfa4534174d1beaff888d63c81510a24eeab80577d548a0196",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "571ba57907b660cfa4534174d1beaff888d63c81510a24eeab80577d548a0196",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "571ba57907b660cfa4534174d1beaff888d63c81510a24eeab80577d548a0196",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "571ba57907b660cfa4534174d1beaff888d63c81510a24eeab80577d548a0196",
                "trainable_numel": 21823488,
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
                "sha256": "ade711e32f5d6e2fce3456b900ce1926d09172ab24fdb79226c848fdb0645c2c",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "ade711e32f5d6e2fce3456b900ce1926d09172ab24fdb79226c848fdb0645c2c",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "ade711e32f5d6e2fce3456b900ce1926d09172ab24fdb79226c848fdb0645c2c",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "ade711e32f5d6e2fce3456b900ce1926d09172ab24fdb79226c848fdb0645c2c",
                "trainable_numel": 21823488,
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
                "sha256": "1f627a4f5e34734337199fcce447c655a882705de8263e1b58cd707969adf77f",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "1f627a4f5e34734337199fcce447c655a882705de8263e1b58cd707969adf77f",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "1f627a4f5e34734337199fcce447c655a882705de8263e1b58cd707969adf77f",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "1f627a4f5e34734337199fcce447c655a882705de8263e1b58cd707969adf77f",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:6",
                  "cuda:7"
                ]
              }
            ],
            "passed": true
          }
        ],
        "seconds": 26.37689709663391,
        "metrics_sha256": "dd30636347f5c0d7c2bf4fbe3f56d8c40914376841761dcdd05005b627c93c0c"
      },
      "shot2": {
        "steps": 2,
        "session_examples_seen": 32,
        "loss_before": 0.708606518805027,
        "loss_after": 0.5130217969417572,
        "attention_projection_dtypes": [
          {
            "module.base_model.model.model.language_model.layers.0.self_attn.q_proj": [
              "torch.float32"
            ],
            "module.base_model.model.model.language_model.layers.35.self_attn.q_proj": [
              "torch.float32"
            ]
          },
          {
            "module.base_model.model.model.language_model.layers.0.self_attn.q_proj": [
              "torch.float32"
            ],
            "module.base_model.model.model.language_model.layers.35.self_attn.q_proj": [
              "torch.float32"
            ]
          },
          {
            "module.base_model.model.model.language_model.layers.0.self_attn.q_proj": [
              "torch.float32"
            ],
            "module.base_model.model.model.language_model.layers.35.self_attn.q_proj": [
              "torch.float32"
            ]
          },
          {
            "module.base_model.model.model.language_model.layers.0.self_attn.q_proj": [
              "torch.float32"
            ],
            "module.base_model.model.model.language_model.layers.35.self_attn.q_proj": [
              "torch.float32"
            ]
          }
        ],
        "memory": [
          {
            "rank": 0,
            "devices": [
              0,
              1
            ],
            "allocated_gib": [
              7.801403522491455,
              11.44584321975708
            ],
            "reserved_gib": [
              8.537109375,
              12.248046875
            ],
            "device_map": {
              "model.visual": 0,
              "model.language_model.embed_tokens": 0,
              "model.language_model.norm": 1,
              "model.language_model.rotary_emb": 0,
              "lm_head": 1,
              "model.language_model.layers.0": 0,
              "model.language_model.layers.1": 0,
              "model.language_model.layers.2": 0,
              "model.language_model.layers.3": 0,
              "model.language_model.layers.4": 0,
              "model.language_model.layers.5": 0,
              "model.language_model.layers.6": 0,
              "model.language_model.layers.7": 0,
              "model.language_model.layers.8": 0,
              "model.language_model.layers.9": 0,
              "model.language_model.layers.10": 0,
              "model.language_model.layers.11": 0,
              "model.language_model.layers.12": 0,
              "model.language_model.layers.13": 0,
              "model.language_model.layers.14": 1,
              "model.language_model.layers.15": 1,
              "model.language_model.layers.16": 1,
              "model.language_model.layers.17": 1,
              "model.language_model.layers.18": 1,
              "model.language_model.layers.19": 1,
              "model.language_model.layers.20": 1,
              "model.language_model.layers.21": 1,
              "model.language_model.layers.22": 1,
              "model.language_model.layers.23": 1,
              "model.language_model.layers.24": 1,
              "model.language_model.layers.25": 1,
              "model.language_model.layers.26": 1,
              "model.language_model.layers.27": 1,
              "model.language_model.layers.28": 1,
              "model.language_model.layers.29": 1,
              "model.language_model.layers.30": 1,
              "model.language_model.layers.31": 1,
              "model.language_model.layers.32": 1,
              "model.language_model.layers.33": 1,
              "model.language_model.layers.34": 1,
              "model.language_model.layers.35": 1
            }
          },
          {
            "rank": 1,
            "devices": [
              2,
              3
            ],
            "allocated_gib": [
              7.8001933097839355,
              11.443726539611816
            ],
            "reserved_gib": [
              8.537109375,
              12.248046875
            ],
            "device_map": {
              "model.visual": 2,
              "model.language_model.embed_tokens": 2,
              "model.language_model.norm": 3,
              "model.language_model.rotary_emb": 2,
              "lm_head": 3,
              "model.language_model.layers.0": 2,
              "model.language_model.layers.1": 2,
              "model.language_model.layers.2": 2,
              "model.language_model.layers.3": 2,
              "model.language_model.layers.4": 2,
              "model.language_model.layers.5": 2,
              "model.language_model.layers.6": 2,
              "model.language_model.layers.7": 2,
              "model.language_model.layers.8": 2,
              "model.language_model.layers.9": 2,
              "model.language_model.layers.10": 2,
              "model.language_model.layers.11": 2,
              "model.language_model.layers.12": 2,
              "model.language_model.layers.13": 2,
              "model.language_model.layers.14": 3,
              "model.language_model.layers.15": 3,
              "model.language_model.layers.16": 3,
              "model.language_model.layers.17": 3,
              "model.language_model.layers.18": 3,
              "model.language_model.layers.19": 3,
              "model.language_model.layers.20": 3,
              "model.language_model.layers.21": 3,
              "model.language_model.layers.22": 3,
              "model.language_model.layers.23": 3,
              "model.language_model.layers.24": 3,
              "model.language_model.layers.25": 3,
              "model.language_model.layers.26": 3,
              "model.language_model.layers.27": 3,
              "model.language_model.layers.28": 3,
              "model.language_model.layers.29": 3,
              "model.language_model.layers.30": 3,
              "model.language_model.layers.31": 3,
              "model.language_model.layers.32": 3,
              "model.language_model.layers.33": 3,
              "model.language_model.layers.34": 3,
              "model.language_model.layers.35": 3
            }
          },
          {
            "rank": 2,
            "devices": [
              4,
              5
            ],
            "allocated_gib": [
              7.558039665222168,
              11.311076164245605
            ],
            "reserved_gib": [
              8.08203125,
              12.064453125
            ],
            "device_map": {
              "model.visual": 4,
              "model.language_model.embed_tokens": 4,
              "model.language_model.norm": 5,
              "model.language_model.rotary_emb": 4,
              "lm_head": 5,
              "model.language_model.layers.0": 4,
              "model.language_model.layers.1": 4,
              "model.language_model.layers.2": 4,
              "model.language_model.layers.3": 4,
              "model.language_model.layers.4": 4,
              "model.language_model.layers.5": 4,
              "model.language_model.layers.6": 4,
              "model.language_model.layers.7": 4,
              "model.language_model.layers.8": 4,
              "model.language_model.layers.9": 4,
              "model.language_model.layers.10": 4,
              "model.language_model.layers.11": 4,
              "model.language_model.layers.12": 4,
              "model.language_model.layers.13": 4,
              "model.language_model.layers.14": 5,
              "model.language_model.layers.15": 5,
              "model.language_model.layers.16": 5,
              "model.language_model.layers.17": 5,
              "model.language_model.layers.18": 5,
              "model.language_model.layers.19": 5,
              "model.language_model.layers.20": 5,
              "model.language_model.layers.21": 5,
              "model.language_model.layers.22": 5,
              "model.language_model.layers.23": 5,
              "model.language_model.layers.24": 5,
              "model.language_model.layers.25": 5,
              "model.language_model.layers.26": 5,
              "model.language_model.layers.27": 5,
              "model.language_model.layers.28": 5,
              "model.language_model.layers.29": 5,
              "model.language_model.layers.30": 5,
              "model.language_model.layers.31": 5,
              "model.language_model.layers.32": 5,
              "model.language_model.layers.33": 5,
              "model.language_model.layers.34": 5,
              "model.language_model.layers.35": 5
            }
          },
          {
            "rank": 3,
            "devices": [
              6,
              7
            ],
            "allocated_gib": [
              7.558039665222168,
              11.311076164245605
            ],
            "reserved_gib": [
              8.08203125,
              12.064453125
            ],
            "device_map": {
              "model.visual": 6,
              "model.language_model.embed_tokens": 6,
              "model.language_model.norm": 7,
              "model.language_model.rotary_emb": 6,
              "lm_head": 7,
              "model.language_model.layers.0": 6,
              "model.language_model.layers.1": 6,
              "model.language_model.layers.2": 6,
              "model.language_model.layers.3": 6,
              "model.language_model.layers.4": 6,
              "model.language_model.layers.5": 6,
              "model.language_model.layers.6": 6,
              "model.language_model.layers.7": 6,
              "model.language_model.layers.8": 6,
              "model.language_model.layers.9": 6,
              "model.language_model.layers.10": 6,
              "model.language_model.layers.11": 6,
              "model.language_model.layers.12": 6,
              "model.language_model.layers.13": 6,
              "model.language_model.layers.14": 7,
              "model.language_model.layers.15": 7,
              "model.language_model.layers.16": 7,
              "model.language_model.layers.17": 7,
              "model.language_model.layers.18": 7,
              "model.language_model.layers.19": 7,
              "model.language_model.layers.20": 7,
              "model.language_model.layers.21": 7,
              "model.language_model.layers.22": 7,
              "model.language_model.layers.23": 7,
              "model.language_model.layers.24": 7,
              "model.language_model.layers.25": 7,
              "model.language_model.layers.26": 7,
              "model.language_model.layers.27": 7,
              "model.language_model.layers.28": 7,
              "model.language_model.layers.29": 7,
              "model.language_model.layers.30": 7,
              "model.language_model.layers.31": 7,
              "model.language_model.layers.32": 7,
              "model.language_model.layers.33": 7,
              "model.language_model.layers.34": 7,
              "model.language_model.layers.35": 7
            }
          }
        ],
        "consistency": [
          {
            "step": 0,
            "replicas": [
              {
                "rank": 0,
                "sha256": "571ba57907b660cfa4534174d1beaff888d63c81510a24eeab80577d548a0196",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "571ba57907b660cfa4534174d1beaff888d63c81510a24eeab80577d548a0196",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "571ba57907b660cfa4534174d1beaff888d63c81510a24eeab80577d548a0196",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "571ba57907b660cfa4534174d1beaff888d63c81510a24eeab80577d548a0196",
                "trainable_numel": 21823488,
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
                "sha256": "3459d12257456109d2a1584f36ecce218a13966a741bb28cf470702f9a558bc0",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "3459d12257456109d2a1584f36ecce218a13966a741bb28cf470702f9a558bc0",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "3459d12257456109d2a1584f36ecce218a13966a741bb28cf470702f9a558bc0",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "3459d12257456109d2a1584f36ecce218a13966a741bb28cf470702f9a558bc0",
                "trainable_numel": 21823488,
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
                "sha256": "967eb1fada3e575d34bce8fb8e540ed9c5bffe23f90e0b3aa5f47cf60d70b49d",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "967eb1fada3e575d34bce8fb8e540ed9c5bffe23f90e0b3aa5f47cf60d70b49d",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "967eb1fada3e575d34bce8fb8e540ed9c5bffe23f90e0b3aa5f47cf60d70b49d",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "967eb1fada3e575d34bce8fb8e540ed9c5bffe23f90e0b3aa5f47cf60d70b49d",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:6",
                  "cuda:7"
                ]
              }
            ],
            "passed": true
          }
        ],
        "seconds": 36.46464514732361,
        "metrics_sha256": "8edcd306ecd9bb0a2e6395a943bf43341657b8ed41525695c3b560a2c3b74e7f"
      },
      "shot4": {
        "steps": 2,
        "session_examples_seen": 32,
        "loss_before": 0.6640730276703835,
        "loss_after": 0.498112790286541,
        "attention_projection_dtypes": [
          {
            "module.base_model.model.model.language_model.layers.0.self_attn.q_proj": [
              "torch.float32"
            ],
            "module.base_model.model.model.language_model.layers.35.self_attn.q_proj": [
              "torch.float32"
            ]
          },
          {
            "module.base_model.model.model.language_model.layers.0.self_attn.q_proj": [
              "torch.float32"
            ],
            "module.base_model.model.model.language_model.layers.35.self_attn.q_proj": [
              "torch.float32"
            ]
          },
          {
            "module.base_model.model.model.language_model.layers.0.self_attn.q_proj": [
              "torch.float32"
            ],
            "module.base_model.model.model.language_model.layers.35.self_attn.q_proj": [
              "torch.float32"
            ]
          },
          {
            "module.base_model.model.model.language_model.layers.0.self_attn.q_proj": [
              "torch.float32"
            ],
            "module.base_model.model.model.language_model.layers.35.self_attn.q_proj": [
              "torch.float32"
            ]
          }
        ],
        "memory": [
          {
            "rank": 0,
            "devices": [
              0,
              1
            ],
            "allocated_gib": [
              9.113962173461914,
              12.813782215118408
            ],
            "reserved_gib": [
              9.8515625,
              13.498046875
            ],
            "device_map": {
              "model.visual": 0,
              "model.language_model.embed_tokens": 0,
              "model.language_model.norm": 1,
              "model.language_model.rotary_emb": 0,
              "lm_head": 1,
              "model.language_model.layers.0": 0,
              "model.language_model.layers.1": 0,
              "model.language_model.layers.2": 0,
              "model.language_model.layers.3": 0,
              "model.language_model.layers.4": 0,
              "model.language_model.layers.5": 0,
              "model.language_model.layers.6": 0,
              "model.language_model.layers.7": 0,
              "model.language_model.layers.8": 0,
              "model.language_model.layers.9": 0,
              "model.language_model.layers.10": 0,
              "model.language_model.layers.11": 0,
              "model.language_model.layers.12": 0,
              "model.language_model.layers.13": 0,
              "model.language_model.layers.14": 1,
              "model.language_model.layers.15": 1,
              "model.language_model.layers.16": 1,
              "model.language_model.layers.17": 1,
              "model.language_model.layers.18": 1,
              "model.language_model.layers.19": 1,
              "model.language_model.layers.20": 1,
              "model.language_model.layers.21": 1,
              "model.language_model.layers.22": 1,
              "model.language_model.layers.23": 1,
              "model.language_model.layers.24": 1,
              "model.language_model.layers.25": 1,
              "model.language_model.layers.26": 1,
              "model.language_model.layers.27": 1,
              "model.language_model.layers.28": 1,
              "model.language_model.layers.29": 1,
              "model.language_model.layers.30": 1,
              "model.language_model.layers.31": 1,
              "model.language_model.layers.32": 1,
              "model.language_model.layers.33": 1,
              "model.language_model.layers.34": 1,
              "model.language_model.layers.35": 1
            }
          },
          {
            "rank": 1,
            "devices": [
              2,
              3
            ],
            "allocated_gib": [
              9.113393306732178,
              12.813014030456543
            ],
            "reserved_gib": [
              9.8515625,
              13.498046875
            ],
            "device_map": {
              "model.visual": 2,
              "model.language_model.embed_tokens": 2,
              "model.language_model.norm": 3,
              "model.language_model.rotary_emb": 2,
              "lm_head": 3,
              "model.language_model.layers.0": 2,
              "model.language_model.layers.1": 2,
              "model.language_model.layers.2": 2,
              "model.language_model.layers.3": 2,
              "model.language_model.layers.4": 2,
              "model.language_model.layers.5": 2,
              "model.language_model.layers.6": 2,
              "model.language_model.layers.7": 2,
              "model.language_model.layers.8": 2,
              "model.language_model.layers.9": 2,
              "model.language_model.layers.10": 2,
              "model.language_model.layers.11": 2,
              "model.language_model.layers.12": 2,
              "model.language_model.layers.13": 2,
              "model.language_model.layers.14": 3,
              "model.language_model.layers.15": 3,
              "model.language_model.layers.16": 3,
              "model.language_model.layers.17": 3,
              "model.language_model.layers.18": 3,
              "model.language_model.layers.19": 3,
              "model.language_model.layers.20": 3,
              "model.language_model.layers.21": 3,
              "model.language_model.layers.22": 3,
              "model.language_model.layers.23": 3,
              "model.language_model.layers.24": 3,
              "model.language_model.layers.25": 3,
              "model.language_model.layers.26": 3,
              "model.language_model.layers.27": 3,
              "model.language_model.layers.28": 3,
              "model.language_model.layers.29": 3,
              "model.language_model.layers.30": 3,
              "model.language_model.layers.31": 3,
              "model.language_model.layers.32": 3,
              "model.language_model.layers.33": 3,
              "model.language_model.layers.34": 3,
              "model.language_model.layers.35": 3
            }
          },
          {
            "rank": 2,
            "devices": [
              4,
              5
            ],
            "allocated_gib": [
              8.706356525421143,
              12.363231182098389
            ],
            "reserved_gib": [
              9.564453125,
              13.080078125
            ],
            "device_map": {
              "model.visual": 4,
              "model.language_model.embed_tokens": 4,
              "model.language_model.norm": 5,
              "model.language_model.rotary_emb": 4,
              "lm_head": 5,
              "model.language_model.layers.0": 4,
              "model.language_model.layers.1": 4,
              "model.language_model.layers.2": 4,
              "model.language_model.layers.3": 4,
              "model.language_model.layers.4": 4,
              "model.language_model.layers.5": 4,
              "model.language_model.layers.6": 4,
              "model.language_model.layers.7": 4,
              "model.language_model.layers.8": 4,
              "model.language_model.layers.9": 4,
              "model.language_model.layers.10": 4,
              "model.language_model.layers.11": 4,
              "model.language_model.layers.12": 4,
              "model.language_model.layers.13": 4,
              "model.language_model.layers.14": 5,
              "model.language_model.layers.15": 5,
              "model.language_model.layers.16": 5,
              "model.language_model.layers.17": 5,
              "model.language_model.layers.18": 5,
              "model.language_model.layers.19": 5,
              "model.language_model.layers.20": 5,
              "model.language_model.layers.21": 5,
              "model.language_model.layers.22": 5,
              "model.language_model.layers.23": 5,
              "model.language_model.layers.24": 5,
              "model.language_model.layers.25": 5,
              "model.language_model.layers.26": 5,
              "model.language_model.layers.27": 5,
              "model.language_model.layers.28": 5,
              "model.language_model.layers.29": 5,
              "model.language_model.layers.30": 5,
              "model.language_model.layers.31": 5,
              "model.language_model.layers.32": 5,
              "model.language_model.layers.33": 5,
              "model.language_model.layers.34": 5,
              "model.language_model.layers.35": 5
            }
          },
          {
            "rank": 3,
            "devices": [
              6,
              7
            ],
            "allocated_gib": [
              8.706356525421143,
              12.363231182098389
            ],
            "reserved_gib": [
              9.564453125,
              13.080078125
            ],
            "device_map": {
              "model.visual": 6,
              "model.language_model.embed_tokens": 6,
              "model.language_model.norm": 7,
              "model.language_model.rotary_emb": 6,
              "lm_head": 7,
              "model.language_model.layers.0": 6,
              "model.language_model.layers.1": 6,
              "model.language_model.layers.2": 6,
              "model.language_model.layers.3": 6,
              "model.language_model.layers.4": 6,
              "model.language_model.layers.5": 6,
              "model.language_model.layers.6": 6,
              "model.language_model.layers.7": 6,
              "model.language_model.layers.8": 6,
              "model.language_model.layers.9": 6,
              "model.language_model.layers.10": 6,
              "model.language_model.layers.11": 6,
              "model.language_model.layers.12": 6,
              "model.language_model.layers.13": 6,
              "model.language_model.layers.14": 7,
              "model.language_model.layers.15": 7,
              "model.language_model.layers.16": 7,
              "model.language_model.layers.17": 7,
              "model.language_model.layers.18": 7,
              "model.language_model.layers.19": 7,
              "model.language_model.layers.20": 7,
              "model.language_model.layers.21": 7,
              "model.language_model.layers.22": 7,
              "model.language_model.layers.23": 7,
              "model.language_model.layers.24": 7,
              "model.language_model.layers.25": 7,
              "model.language_model.layers.26": 7,
              "model.language_model.layers.27": 7,
              "model.language_model.layers.28": 7,
              "model.language_model.layers.29": 7,
              "model.language_model.layers.30": 7,
              "model.language_model.layers.31": 7,
              "model.language_model.layers.32": 7,
              "model.language_model.layers.33": 7,
              "model.language_model.layers.34": 7,
              "model.language_model.layers.35": 7
            }
          }
        ],
        "consistency": [
          {
            "step": 0,
            "replicas": [
              {
                "rank": 0,
                "sha256": "571ba57907b660cfa4534174d1beaff888d63c81510a24eeab80577d548a0196",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "571ba57907b660cfa4534174d1beaff888d63c81510a24eeab80577d548a0196",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "571ba57907b660cfa4534174d1beaff888d63c81510a24eeab80577d548a0196",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "571ba57907b660cfa4534174d1beaff888d63c81510a24eeab80577d548a0196",
                "trainable_numel": 21823488,
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
                "sha256": "cdbfb09ca3a8de8e5e008253a4b7cc512fa9a37f5890ff9afa495faf9ea24b9b",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "cdbfb09ca3a8de8e5e008253a4b7cc512fa9a37f5890ff9afa495faf9ea24b9b",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "cdbfb09ca3a8de8e5e008253a4b7cc512fa9a37f5890ff9afa495faf9ea24b9b",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "cdbfb09ca3a8de8e5e008253a4b7cc512fa9a37f5890ff9afa495faf9ea24b9b",
                "trainable_numel": 21823488,
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
                "sha256": "27c1524805cb51c3c4bac19ab6afed1dab8e73b7d23ae45f01f8450987a8a201",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "27c1524805cb51c3c4bac19ab6afed1dab8e73b7d23ae45f01f8450987a8a201",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "27c1524805cb51c3c4bac19ab6afed1dab8e73b7d23ae45f01f8450987a8a201",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "27c1524805cb51c3c4bac19ab6afed1dab8e73b7d23ae45f01f8450987a8a201",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:6",
                  "cuda:7"
                ]
              }
            ],
            "passed": true
          }
        ],
        "seconds": 58.905073165893555,
        "metrics_sha256": "2443e84c71c3b634bc311f710647cba6ed2e132133b6cc9e9efd1846ceafa6d4"
      },
      "shot4_resume": {
        "steps": 3,
        "session_examples_seen": 16,
        "loss_before": 0.498112790286541,
        "loss_after": 0.4239429347217083,
        "attention_projection_dtypes": [
          {
            "module.base_model.model.model.language_model.layers.0.self_attn.q_proj": [
              "torch.float32"
            ],
            "module.base_model.model.model.language_model.layers.35.self_attn.q_proj": [
              "torch.float32"
            ]
          },
          {
            "module.base_model.model.model.language_model.layers.0.self_attn.q_proj": [
              "torch.float32"
            ],
            "module.base_model.model.model.language_model.layers.35.self_attn.q_proj": [
              "torch.float32"
            ]
          },
          {
            "module.base_model.model.model.language_model.layers.0.self_attn.q_proj": [
              "torch.float32"
            ],
            "module.base_model.model.model.language_model.layers.35.self_attn.q_proj": [
              "torch.float32"
            ]
          },
          {
            "module.base_model.model.model.language_model.layers.0.self_attn.q_proj": [
              "torch.float32"
            ],
            "module.base_model.model.model.language_model.layers.35.self_attn.q_proj": [
              "torch.float32"
            ]
          }
        ],
        "memory": [
          {
            "rank": 0,
            "devices": [
              0,
              1
            ],
            "allocated_gib": [
              9.112834930419922,
              12.81353235244751
            ],
            "reserved_gib": [
              9.849609375,
              13.49609375
            ],
            "device_map": {
              "model.visual": 0,
              "model.language_model.embed_tokens": 0,
              "model.language_model.norm": 1,
              "model.language_model.rotary_emb": 0,
              "lm_head": 1,
              "model.language_model.layers.0": 0,
              "model.language_model.layers.1": 0,
              "model.language_model.layers.2": 0,
              "model.language_model.layers.3": 0,
              "model.language_model.layers.4": 0,
              "model.language_model.layers.5": 0,
              "model.language_model.layers.6": 0,
              "model.language_model.layers.7": 0,
              "model.language_model.layers.8": 0,
              "model.language_model.layers.9": 0,
              "model.language_model.layers.10": 0,
              "model.language_model.layers.11": 0,
              "model.language_model.layers.12": 0,
              "model.language_model.layers.13": 0,
              "model.language_model.layers.14": 1,
              "model.language_model.layers.15": 1,
              "model.language_model.layers.16": 1,
              "model.language_model.layers.17": 1,
              "model.language_model.layers.18": 1,
              "model.language_model.layers.19": 1,
              "model.language_model.layers.20": 1,
              "model.language_model.layers.21": 1,
              "model.language_model.layers.22": 1,
              "model.language_model.layers.23": 1,
              "model.language_model.layers.24": 1,
              "model.language_model.layers.25": 1,
              "model.language_model.layers.26": 1,
              "model.language_model.layers.27": 1,
              "model.language_model.layers.28": 1,
              "model.language_model.layers.29": 1,
              "model.language_model.layers.30": 1,
              "model.language_model.layers.31": 1,
              "model.language_model.layers.32": 1,
              "model.language_model.layers.33": 1,
              "model.language_model.layers.34": 1,
              "model.language_model.layers.35": 1
            }
          },
          {
            "rank": 1,
            "devices": [
              2,
              3
            ],
            "allocated_gib": [
              9.112266063690186,
              12.81267261505127
            ],
            "reserved_gib": [
              9.849609375,
              13.49609375
            ],
            "device_map": {
              "model.visual": 2,
              "model.language_model.embed_tokens": 2,
              "model.language_model.norm": 3,
              "model.language_model.rotary_emb": 2,
              "lm_head": 3,
              "model.language_model.layers.0": 2,
              "model.language_model.layers.1": 2,
              "model.language_model.layers.2": 2,
              "model.language_model.layers.3": 2,
              "model.language_model.layers.4": 2,
              "model.language_model.layers.5": 2,
              "model.language_model.layers.6": 2,
              "model.language_model.layers.7": 2,
              "model.language_model.layers.8": 2,
              "model.language_model.layers.9": 2,
              "model.language_model.layers.10": 2,
              "model.language_model.layers.11": 2,
              "model.language_model.layers.12": 2,
              "model.language_model.layers.13": 2,
              "model.language_model.layers.14": 3,
              "model.language_model.layers.15": 3,
              "model.language_model.layers.16": 3,
              "model.language_model.layers.17": 3,
              "model.language_model.layers.18": 3,
              "model.language_model.layers.19": 3,
              "model.language_model.layers.20": 3,
              "model.language_model.layers.21": 3,
              "model.language_model.layers.22": 3,
              "model.language_model.layers.23": 3,
              "model.language_model.layers.24": 3,
              "model.language_model.layers.25": 3,
              "model.language_model.layers.26": 3,
              "model.language_model.layers.27": 3,
              "model.language_model.layers.28": 3,
              "model.language_model.layers.29": 3,
              "model.language_model.layers.30": 3,
              "model.language_model.layers.31": 3,
              "model.language_model.layers.32": 3,
              "model.language_model.layers.33": 3,
              "model.language_model.layers.34": 3,
              "model.language_model.layers.35": 3
            }
          },
          {
            "rank": 2,
            "devices": [
              4,
              5
            ],
            "allocated_gib": [
              8.707088947296143,
              12.363378047943115
            ],
            "reserved_gib": [
              9.5625,
              13.078125
            ],
            "device_map": {
              "model.visual": 4,
              "model.language_model.embed_tokens": 4,
              "model.language_model.norm": 5,
              "model.language_model.rotary_emb": 4,
              "lm_head": 5,
              "model.language_model.layers.0": 4,
              "model.language_model.layers.1": 4,
              "model.language_model.layers.2": 4,
              "model.language_model.layers.3": 4,
              "model.language_model.layers.4": 4,
              "model.language_model.layers.5": 4,
              "model.language_model.layers.6": 4,
              "model.language_model.layers.7": 4,
              "model.language_model.layers.8": 4,
              "model.language_model.layers.9": 4,
              "model.language_model.layers.10": 4,
              "model.language_model.layers.11": 4,
              "model.language_model.layers.12": 4,
              "model.language_model.layers.13": 4,
              "model.language_model.layers.14": 5,
              "model.language_model.layers.15": 5,
              "model.language_model.layers.16": 5,
              "model.language_model.layers.17": 5,
              "model.language_model.layers.18": 5,
              "model.language_model.layers.19": 5,
              "model.language_model.layers.20": 5,
              "model.language_model.layers.21": 5,
              "model.language_model.layers.22": 5,
              "model.language_model.layers.23": 5,
              "model.language_model.layers.24": 5,
              "model.language_model.layers.25": 5,
              "model.language_model.layers.26": 5,
              "model.language_model.layers.27": 5,
              "model.language_model.layers.28": 5,
              "model.language_model.layers.29": 5,
              "model.language_model.layers.30": 5,
              "model.language_model.layers.31": 5,
              "model.language_model.layers.32": 5,
              "model.language_model.layers.33": 5,
              "model.language_model.layers.34": 5,
              "model.language_model.layers.35": 5
            }
          },
          {
            "rank": 3,
            "devices": [
              6,
              7
            ],
            "allocated_gib": [
              8.707088947296143,
              12.363378047943115
            ],
            "reserved_gib": [
              9.5625,
              13.078125
            ],
            "device_map": {
              "model.visual": 6,
              "model.language_model.embed_tokens": 6,
              "model.language_model.norm": 7,
              "model.language_model.rotary_emb": 6,
              "lm_head": 7,
              "model.language_model.layers.0": 6,
              "model.language_model.layers.1": 6,
              "model.language_model.layers.2": 6,
              "model.language_model.layers.3": 6,
              "model.language_model.layers.4": 6,
              "model.language_model.layers.5": 6,
              "model.language_model.layers.6": 6,
              "model.language_model.layers.7": 6,
              "model.language_model.layers.8": 6,
              "model.language_model.layers.9": 6,
              "model.language_model.layers.10": 6,
              "model.language_model.layers.11": 6,
              "model.language_model.layers.12": 6,
              "model.language_model.layers.13": 6,
              "model.language_model.layers.14": 7,
              "model.language_model.layers.15": 7,
              "model.language_model.layers.16": 7,
              "model.language_model.layers.17": 7,
              "model.language_model.layers.18": 7,
              "model.language_model.layers.19": 7,
              "model.language_model.layers.20": 7,
              "model.language_model.layers.21": 7,
              "model.language_model.layers.22": 7,
              "model.language_model.layers.23": 7,
              "model.language_model.layers.24": 7,
              "model.language_model.layers.25": 7,
              "model.language_model.layers.26": 7,
              "model.language_model.layers.27": 7,
              "model.language_model.layers.28": 7,
              "model.language_model.layers.29": 7,
              "model.language_model.layers.30": 7,
              "model.language_model.layers.31": 7,
              "model.language_model.layers.32": 7,
              "model.language_model.layers.33": 7,
              "model.language_model.layers.34": 7,
              "model.language_model.layers.35": 7
            }
          }
        ],
        "consistency": [
          {
            "step": 2,
            "replicas": [
              {
                "rank": 0,
                "sha256": "27c1524805cb51c3c4bac19ab6afed1dab8e73b7d23ae45f01f8450987a8a201",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "27c1524805cb51c3c4bac19ab6afed1dab8e73b7d23ae45f01f8450987a8a201",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "27c1524805cb51c3c4bac19ab6afed1dab8e73b7d23ae45f01f8450987a8a201",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "27c1524805cb51c3c4bac19ab6afed1dab8e73b7d23ae45f01f8450987a8a201",
                "trainable_numel": 21823488,
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
                "sha256": "99d414ecb332eda27343408c7b107cc91539317f2a4e24a3adc7814431472e52",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:0",
                  "cuda:1"
                ]
              },
              {
                "rank": 1,
                "sha256": "99d414ecb332eda27343408c7b107cc91539317f2a4e24a3adc7814431472e52",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:2",
                  "cuda:3"
                ]
              },
              {
                "rank": 2,
                "sha256": "99d414ecb332eda27343408c7b107cc91539317f2a4e24a3adc7814431472e52",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:4",
                  "cuda:5"
                ]
              },
              {
                "rank": 3,
                "sha256": "99d414ecb332eda27343408c7b107cc91539317f2a4e24a3adc7814431472e52",
                "trainable_numel": 21823488,
                "devices": [
                  "cuda:6",
                  "cuda:7"
                ]
              }
            ],
            "passed": true
          }
        ],
        "seconds": 29.450536251068115,
        "metrics_sha256": "969c48c44219aaf3052c9a1ca59a11e3a46c27d53ee3c003e7776e332222a596"
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-result-audit-20261021/metrics.json"
  },
  {
    "metric_id": "limitations",
    "value": "8 training sequences; short NF4 SFT capability only, not FOCUS attention loss/GRPO, Qwen2, full-data maximum or accuracy",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-result-audit-20261021/metrics.json"
  }
]
```

### 分析
CPU只读审计真实exit0/marker。1/2/4shot各2更新，4shot恢复第3步，112呈现，finite gradients、全LoRA副本SHA、恢复SHA连续、四组独占GPU与code/config快照全部通过。单卡allocated/reserved峰值GiB分别11.082329/11.802734、11.445843/12.248047、12.813782/13.498047；恢复12.813532/13.496094。父Run exit1由最终错误BF16 q_proj断言引起，实际首尾q_proj均FP32；父失败状态和全部原始数据保留。本审计不新增训练、不改变科学结果，仅明确training_capability_passed=true、qproj_bf16_expectation_met=false。

### 局限
Qwen3-VL-8B、8个GOT训练序列、NF4 LoRA短程SFT；不能外推Qwen2/完整FOCUS、全量最长样本、任意nshot、最终mIoU或吞吐优势。BF16 embedding和autocast联动变更，未作独立消融，不把显存改善归因于单一设置，未直接测SDPA内部dtype。

### Claim 边界
仅当前Qwen3 NF4 SFT短程多图能力，非Qwen2/FOCUS attention loss/GRPO验证，不代表全量最长样本都可运行或科研性能提升。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-result-audit-20261021/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-model-parallel-ddp4x2-result-audit-20261021/managed_console.log

### 审核入口
```json
[
  ".pi/analysis/e014/model-parallel-result-audit-20261021/download_audit.json",
  ".pi/analysis/e014/model-parallel-bf16-20261021/download_audit.json",
  ".pi/analysis/e014/model-parallel-result-audit-20261021/complete_receipt.json"
]
```

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
