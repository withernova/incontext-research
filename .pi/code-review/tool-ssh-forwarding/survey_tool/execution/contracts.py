"""Pure execution lane/status contracts. No storage or server imports."""

from dataclasses import dataclass

OUTBOX_ACTIVE = frozenset({"queued", "delivered", "claimed", "acknowledged", "running", "blocked"})
OUTBOX_TERMINAL = frozenset({"completed", "failed", "cancelled", "superseded"})
PIPELINE_LANES = (
    "needs_grouping", "draft", "pending_review", "needs_human_review", "approved",
    "authorized_queued", "delivered_unacked", "claimed", "running", "analysis_pending", "completed",
    "failed", "legacy_untracked",
)

@dataclass(frozen=True)
class LaneResult:
    lane: str
    reason: str
    anomaly: str = ""

def classify_pipeline_lane(run, dispatch=None, reconciliation_anomaly=""):
    """Assign exactly one lifecycle lane; dispatch/consumption wins over review."""
    consumed=bool(run.get("execution_authorization_consumed_at"))
    if reconciliation_anomaly in {"legacy_consumed_untracked", "consumed_dispatch_missing", "consumed_dispatch_state_mismatch"} or (consumed and not dispatch):
        return LaneResult("legacy_untracked", "非Outbox消费，无法追溯claim/ACK", reconciliation_anomaly or "legacy_consumed_untracked")
    status=str((dispatch or {}).get("status") or "")
    if status in {"queued","blocked"}: return LaneResult("authorized_queued",status)
    if status=="delivered": return LaneResult("delivered_unacked",status)
    if status in {"claimed","acknowledged"}: return LaneResult("claimed",status)
    if status=="running": return LaneResult("running",status)
    if status=="completed" and run.get("workflow_version")==2: return LaneResult("analysis_pending",status)
    if status=="completed": return LaneResult("completed",status)
    if status in {"failed","cancelled","superseded"}: return LaneResult("failed",status)
    operational=str(run.get("status") or "draft")
    if operational in {"completed","done","succeeded"} or operational.startswith("completed_"): return LaneResult("completed",operational)
    if operational in {"failed","cancelled","aborted","timeout"}: return LaneResult("failed",operational)
    review=str(run.get("review_status") or "draft")
    if review=="approved": return LaneResult("approved","approved but not authorized" if not run.get("execution_authorized_at") else "authorized without dispatch")
    if review=="pending_review": return LaneResult("pending_review",review)
    if review in {"changes_requested","needs_human_review"}: return LaneResult("needs_human_review",review)
    if not run.get("group_id"): return LaneResult("needs_grouping","draft Run is ungrouped")
    return LaneResult("draft",review)
