# R-010 formal gate result

- engineering integrity: PASS (21 records, 7×3, finite logits, 7 visualizations)
- natural-prefix replay: **FAIL** (expected R-004b Yes on 7/7; exact prefix replay gives Yes on 1/7)
- scientific status: **completed / replay gate failed**

The target/wrong/background margins are retained for audit but are not candidate-binding evidence. The current forced-prefix environment does not reproduce the natural decision at the exact wrong-instance prefix. Reconcile model/environment/chat-token inputs before rerunning counterfactuals.

Token boundary audit: end prefix at `?`, then score leading-space decision tokens ` Yes`=7414 and ` No`=2308. Attempts 004/005 used mismatched boundary/token forms and are archived as invalid.
