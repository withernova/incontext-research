# E-005 · 实验结果

## 运行汇总（survey-tool 管理）
### 分辨率稳定性复核 (`resolution-stability`)
| Run | Variant | Seed | 状态 | 指标摘要 |
|---|---|---:|---|---|
| [E005-R-028-r023-matched35x2-same-resolution-640](runs/resolution-stability/E005-R-028-r023-matched35x2-same-resolution-640.md) | matched35x2 same-resolution640 attention and visualization | 20260728 | completed_passed_integrity | （尚无结构化观测） |

### 正样本绑定审计 (`positive-binding-audit`)
| Run | Variant | Seed | 状态 | 指标摘要 |
|---|---|---:|---|---|
| [E005-R-029c-original140-positive-targets-binding-640](runs/positive-binding-audit/E005-R-029c-original140-positive-targets-binding-640.md) | original E003 positive n140 same-resolution640 binding audit | 20260728 | completed_passed_integrity | （尚无结构化观测） |

### 负样本绑定诊断 (`negative-binding-audit`)
| Run | Variant | Seed | 状态 | 指标摘要 |
|---|---|---:|---|---|
| [E005-R-030c-original140-negative-targets-binding-640](runs/negative-binding-audit/E005-R-030c-original140-negative-targets-binding-640.md) | original E003 same-class negative n140 separate640 diagnostic | 20260728 | completed_passed_integrity | （尚无结构化观测） |

### 统一五面板可视化 (`unified-visualization`)
| Run | Variant | Seed | 状态 | 指标摘要 |
|---|---|---:|---|---|
| [E005-R-033-positive-full140-unified-fivepanel-640](runs/unified-visualization/E005-R-033-positive-full140-unified-fivepanel-640.md) | full original n140 positive unified five-panel640 visualizations | 20260728 | completed_passed_integrity_visualization_only | （尚无结构化观测） |
| [E005-R-033-negative-full140-unified-fivepanel-640](runs/unified-visualization/E005-R-033-negative-full140-unified-fivepanel-640.md) | full original n140 negative unified five-panel640 visualizations | 20260728 | completed_passed_integrity_visualization_only | （尚无结构化观测） |

### 离线 Q→R 阈值曲线 (`offline-threshold-curve`)
| Run | Variant | Seed | 状态 | 指标摘要 |
|---|---|---:|---|---|
| [E005-R-034-qr-continuous-threshold-curve-offline-640](runs/offline-threshold-curve/E005-R-034-qr-continuous-threshold-curve-offline-640.md) | offline Q→R curve analysis first implementation | 20260728 | failed_implementation_no_scientific_output | （尚无结构化观测） |
| [E005-R-034b-qr-continuous-threshold-curve-offline-640](runs/offline-threshold-curve/E005-R-034b-qr-continuous-threshold-curve-offline-640.md) | pure numpy recovery | 20260728 | failed_implementation_no_scientific_output | （尚无结构化观测） |
| [E005-R-034d-qr-continuous-threshold-curve-offline-640](runs/offline-threshold-curve/E005-R-034d-qr-continuous-threshold-curve-offline-640.md) | final frozen Q→R continuous threshold fIoU analysis | 20260728 | completed_passed_integrity_inference_only | （尚无结构化观测） |


## 指标观测（survey-tool 管理）
（尚无结构化观测）

## 结果摘要（survey-tool 管理）
（待登记）

## 对 Claims 的影响（survey-tool 管理）
（待人工判断；不会自动提升 Claim）

## 局限性（survey-tool 管理）
（待补充）

## 详细审计正文（canonical）
这里保存指标定义、证据链、逐层结论边界与审核入口；后续 Run 更新不会覆盖本节。
