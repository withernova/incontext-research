# 独立复核：step741 baseline 的 Query 五头→Reference GT 集中度（按预测正误分组）

日期：2026-09-15。讨论级离线复核；未启动模型 forward / 训练 / 消融，未写远端，未修改审批、Claim、Run 授权或其它治理状态。

## 输入与身份

| 输入 | 路径 | sha256 |
|---|---|---|
| Attention（baseline step741，118条 Confirmation） | `.../R-006-query-r005-ref3-transfer-step247-3ep-v1/attention_compare_step741_v1/baseline/records.json` | `76b47106…b3b07` |
| 自然预测（用户指定分支） | `.../E-009/…/branches/20260915T071307686259Z--baseline-eval-741-new-ft/evaluation/predictions.jsonl` | `c013e704…326c` |

- 两份 sha256 与远端 `sha256sum` 及 attention `integrity.json`（`records_sha256`）一致。
- 118/118 条按 `dataset_index` 唯一匹配（118 个唯一 index、118 个唯一 component，无重复、无缺失）；prediction 侧共 1766 行。
- 正确＝`parsed and IoU>=0.5`：100 正确 / 18 错误（LaSOT 49/11、TAO 33/7、GOT10k 18/0）。

## 结果（ensemble＝五头等权）

| 指标 | 正确 (n=100) | 错误 (n=18) | 差值 95% CI | CI 是否跨 0 |
|---|---:|---:|---|---|
| Reference span 内 GT mass 占比 | 13.88% | 11.93% | −5.86 ~ +8.29 pp | 跨 0 |
| 面积校正 log GT enrichment | 0.926 | 1.330 | −1.354 ~ +0.495 | 跨 0 |
| Reference span mass（attention 预算） | 0.416% | 1.916% | −2.895 ~ −0.401 pp | 不跨 0（正确更低） |
| 峰值命中率 | 8.0% | 22.2% | −35.4 ~ +4.4 pp | 跨 0 |
| Reference 占两视觉 span 的份额 | 0.707% | 3.491% | −5.30 ~ −0.81 pp | 不跨 0（正确更低） |

逐头 GT mass（正确 / 错误，差 95% CI，pp）：L24H13 8.77/8.96（−8.96~+6.47）、L23H30 12.13/13.12（−10.60~+7.02）、L26H20 3.41/5.85（−8.35~+2.01）、L21H11 26.41/15.36（**+0.50~+19.75**）、L23H13 18.69/16.38（−6.89~+10.45）。仅 L21H11 未跨 0，未做多重比较校正。

稳健性：错误收紧到 IoU<0.1（12条）→ GT mass 差 +5.49 pp，CI −1.27~+11.11；正确收紧到 IoU≥0.75（85条）→ GT mass 差 +3.26 pp，CI −1.70~+7.75、log enrichment 差 CI 整体为负。按目标面积档分层（medium 21/2：14.92% vs 14.99%；small 61/16：12.48% vs 11.55%）也不支持正确组更集中。

## 结论与边界

- 在**这 118 条 teacher-forced 归档 attention** 上，没有"预测正确时 Query 五头对 Reference 的 attention 更集中于 GT"的证据：点估计为正但区间跨 0，面积校正指标方向相反；正确组的 Reference attention 预算反而显著更低。
- 该统计不是用户所问的最终口径：attention 记录来自 GT 坐标行的 teacher-forced 前向，图像 token 预算（`vision_max_patch_tokens`）与自然评估不一致；1766 条全量、按自然生成 token 行提取的 Q→R attention 仍缺。
- 本地脚本 `independent_recheck.py` 与结果 `independent_recheck.json` 可复现；与同目录既有 `report.md` / `statistics.json` 在主结论和逐头方向上一致，均值/CI 差异来自 bootstrap 蒙特卡洛噪声（n=18）。

```bash
python3 shell/06_experiments/E-012/diagnostics/r006_query_heads_step741_20260915/independent_recheck.py \
  --attention /tmp/e012_r006_recheck/baseline_records.json \
  --predictions /tmp/e012_r006_recheck/predictions.jsonl \
  --output shell/06_experiments/E-012/diagnostics/r006_query_heads_step741_20260915/independent_recheck.json
```
