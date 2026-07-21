# E003-R-007 configuration

- nature: offline evaluation audit
- source: completed E003-R-004b per-record outputs and formal summary
- data: 140 paired clusters / 280 records; local deterministic LaSOT reconstruction; not official split
- thresholds: 0.00..1.00 inclusive, step 0.01
- bootstrap: 10,000 sample-clustered replicates; positive+negative pair resampled together
- seed: 20260721
- no model load or rerun
- gates: 280 records; 140 complete clusters; finite IoU; tau=0 equals identification; tau=0.3/0.5/0.7 exactly reproduce R-004b; 10,000 replicates
