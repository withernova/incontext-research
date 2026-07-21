# Simple positive low-IoU visualization

Source: E003-R-006 per-sample geometry outputs. No model rerun.

Selection: positive query, natural decision Yes, bbox IoU < 0.1. N=35.

- Green: positive-query target GT.
- Red: natural model-predicted bbox.
- No background/control box is shown.

The seven flagged cases are a single-reviewer visual screen for possible same-image wrong-instance predictions, not a final annotation. The remaining cases are not semantically classified. Low IoU alone does not establish wrong-instance selection.
