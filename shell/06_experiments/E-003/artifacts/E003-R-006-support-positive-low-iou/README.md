# Support + positive-query low-IoU visualization

Offline rendering from completed E003-R-006 outputs; no model rerun.

Selection: natural positive-query decision Yes and predicted/GT IoU < 0.1, N=35.

Panels:
- Support/reference: green = reference target GT.
- Positive query: green = tracked target GT; red = natural model prediction.
- Reject query is intentionally omitted. No background candidate is shown.

Seven cases carry a single-reviewer possible-wrong-instance flag. This is visual screening, not finalized multi-instance ground truth. Low IoU alone does not establish identity confusion.
