# E003-R-007 summary

Offline analysis; no model rerun. 140 paired clusters / 280 records; 10,000 clustered bootstrap replicates, seed 20260721.

- Identification F1: **0.9603**, 95% CI [0.9348, 0.9819]
- Joint F1@0.3: **0.8050**, 95% CI [0.7468, 0.8583]
- Joint F1@0.5: **0.7639**, 95% CI [0.6996, 0.8216]
- Joint F1@0.7: **0.6909**, 95% CI [0.6161, 0.7598]

Curve points: IoU threshold 0.00–1.00 in steps of 0.01. All integrity gates passed and registered 0.3/0.5/0.7 values exactly reproduce R-004b.

Boundary: local deterministic LaSOT reconstruction, not official IPLoc-ID split; evaluation-coverage evidence only.
