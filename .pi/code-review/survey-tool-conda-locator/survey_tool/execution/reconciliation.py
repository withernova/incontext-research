"""Pure reconciliation planning. This module intentionally never imports server."""

def plan_reconciliation(runs, outbox_items, experiment_id=""):
    actions=[]; anomalies=[]; unchanged=[]
    by_id={str(x.get("dispatch_id")):x for x in outbox_items if x.get("dispatch_id")}
    by_auth={}
    for item in outbox_items:
        by_auth.setdefault((str(item.get("run_id")),str(item.get("authorization_timestamp"))),[]).append(item)
    for run in runs:
        if experiment_id and run.get("experiment_id")!=experiment_id: continue
        rid=str(run.get("id") or ""); consumed=run.get("execution_authorization_consumed_at"); linked=str(run.get("execution_dispatch_id") or "")
        if consumed:
            if not linked: anomalies.append({"run_id":rid,"type":"legacy_consumed_untracked","detail":"consumed timestamp exists without dispatch linkage"})
            elif linked not in by_id: anomalies.append({"run_id":rid,"type":"consumed_dispatch_missing","dispatch_id":linked})
            elif by_id[linked].get("status") not in {"running","completed","failed"}: anomalies.append({"run_id":rid,"type":"consumed_dispatch_state_mismatch","dispatch_id":linked,"status":by_id[linked].get("status")})
            else: unchanged.append({"run_id":rid,"reason":"consumed_dispatch_linked","dispatch_id":linked})
            continue
        auth=str(run.get("execution_authorized_at") or "")
        related=by_auth.get((rid,auth),[]) if auth else []
        impossible=[x for x in related if x.get("status") in {"running","completed"}]
        if impossible:
            anomalies.append({"run_id":rid,"type":"unconsumed_dispatch_already_started","dispatch_ids":[x.get("dispatch_id") for x in impossible]}); continue
        if str(run.get("review_status") or "")!="approved" or not auth: continue
        if related: unchanged.append({"run_id":rid,"reason":"same_authorization_dispatch_exists","dispatch_id":related[0].get("dispatch_id")})
        else: actions.append({"action":"enqueue","run_id":rid,"authorization_timestamp":auth})
    return {"actions":actions,"anomalies":anomalies,"unchanged":unchanged,"totals":{"actions":len(actions),"anomalies":len(anomalies),"unchanged":len(unchanged)}}
