# E-004 Results

## R-000 module audit

Qwen3-VL text decoder 为36层、32 query heads、8 KV heads、head_dim=128。已定位潜在单-head hook 到每层 `self_attn.o_proj` 的 forward pre-input slice；这只是实现审计，不是机制结果。

## R-001 synthetic behavioral gate

4个 synthetic double-instance quartets / 16 conditions：

```text
accuracy = 9/16 = 0.5625
quartets all-four-correct = 0/4
matched-minus-mismatched mean margin by quartet =
0.5625, 0.125, 0.71875, 0.125
```

方向上每组 matched margin 都高于 mismatched，但没有一个 quartet 能把 A/A、A/B、B/A、B/B 四个离散判断全部答对。因此预注册 behavioral gate 失败，不能直接把后续 head ranking 解释为可靠 instance-verification circuit。下一步只做 hook correctness smoke，并优先改善/获取真实同图双实例数据；synthetic composite 结果不外推自然场景。
