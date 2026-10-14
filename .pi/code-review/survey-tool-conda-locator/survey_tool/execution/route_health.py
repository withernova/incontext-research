"""Pure route observation validation and public aggregation."""

ROUTE_RESULTS=frozenset({"success","unsupported","unavailable","quota","error"})
import re

ROUTE_EVENT_FIELDS=frozenset({"route","subject","requested_agent","requested_model","actual_agent","actual_model","fallback_reason","result","error_code","message","time","run_id"})
SECRET_PATTERN=re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----|(?:password|passwd|api[_-]?key|access[_-]?token|lease[_-]?token)\s*[:=]\s*\S+",re.I)

def _contains_secret(value):
    if isinstance(value,dict):
        return any(re.search(r"password|passwd|secret|token|private.?key|prompt|messages",str(key),re.I) or _contains_secret(child) for key,child in value.items())
    if isinstance(value,(list,tuple)): return any(_contains_secret(child) for child in value)
    return bool(SECRET_PATTERN.search(str(value or "")))

def validate_route_event(value):
    if not isinstance(value,dict): raise ValueError("route event 必须是对象")
    unknown=set(value)-ROUTE_EVENT_FIELDS
    if unknown: raise ValueError("route event 未知字段："+", ".join(sorted(unknown)))
    if _contains_secret(value): raise ValueError("route event 不得包含凭据、token、Prompt、消息或私钥")
    out={key:str(value.get(key) or "").strip() for key in ROUTE_EVENT_FIELDS}
    out["subject"]=out["subject"] or "requested"
    if not out["route"] or out["result"] not in ROUTE_RESULTS: raise ValueError("route/result 非法")
    if out["subject"] not in {"requested","actual"}: raise ValueError("route event subject 非法")
    if any(len(v)>4000 for v in out.values()): raise ValueError("route event 字段过长")
    if SECRET_PATTERN.search(out["message"]) or SECRET_PATTERN.search(out["fallback_reason"]): raise ValueError("route event 不得包含凭据、token 或私钥")
    return out

def aggregate_route_health(events):
    health={}
    for raw in sorted(events,key=lambda x:str(x.get("time") or "")):
        try: event=validate_route_event(raw)
        except ValueError: continue
        agent=event["actual_agent"] if event["subject"]=="actual" else event["requested_agent"]
        model=event["actual_model"] if event["subject"]=="actual" else event["requested_model"]
        key="|".join((event["route"],event["subject"],agent,model)); row=health.setdefault(key,{"route":event["route"],"subject":event["subject"],"agent":agent,"model":model,"requested_agent":event["requested_agent"],"requested_model":event["requested_model"],"actual_agent":event["actual_agent"],"actual_model":event["actual_model"],"last_result":"","last_error":"","last_seen":"","consecutive_failures":0})
        row["last_result"]=event["result"]; row["last_seen"]=event["time"]
        if event["result"]=="success": row["consecutive_failures"]=0; row["last_error"]=""
        else: row["consecutive_failures"]+=1; row["last_error"]=event["message"] or event["error_code"]
    return list(health.values())
