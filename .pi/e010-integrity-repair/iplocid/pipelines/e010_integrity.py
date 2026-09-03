"""Shared scientific contracts for E010 R-006/R-007/R-008.

These helpers deliberately lock the two frozen head authorities, enforce the
natural Query-bbox p−1 row semantics, and keep statistics/control construction
identical across the 140-artifact and full-LaSOT pipelines.
"""
from __future__ import annotations
import hashlib, json
from collections import deque
from pathlib import Path
import numpy as np

T003_SCHEMA = "iplocid.e010.gt-iou-entropy-reward-trial/v1"
T003_HEADS = {"3": ["L18H05", "L12H00", "L20H12"], "5": ["L18H05", "L12H00", "L20H12", "L7H25", "L20H15"]}
T003_PARAMETERS = {"reward_form": "thresholded_iou_bonus", "iou_metric": "support50_fiou", "entropy_weight": 1, "iou_reward_weight": 2, "iou_threshold": 0.1, "rank_score": "-normalized_entropy + iou_reward_weight * max(0, support50_fiou-iou_threshold)"}
ROW_CONTRACT = "natural_query_bbox_pminus1/v1"
METRICS = ("pointing", "fractional_mass", "enrichment", "s50_fiou", "core30_hit", "s30_iou", "largest4n_hit", "largest4n_iou")


def sha256(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate_repaired_r008_summary(summary):
    """Reject v1/v2 or any output lacking the T-003 R→R semantic contract."""
    if summary.get("schema") != "iplocid.e010.full-lasot-frozen-query-and-reference-top5/v3":
        raise RuntimeError("stale or incompatible R-008 summary schema")
    readouts=summary.get("readouts", {})
    semantic=readouts.get("rheads_t003_on_qbbox_to_reference", {})
    if semantic.get("row_source") != ROW_CONTRACT or semantic.get("key_span") != "reference":
        raise RuntimeError("R-008 summary lacks T-003 natural-Qbbox R→R contract")
    if summary.get("authority", {}).get("reference_t003", {}).get("sha256") is None:
        raise RuntimeError("R-008 summary lacks T-003 authority hash")

def load_json(path): return json.loads(Path(path).read_text())
def hindex(name):
    layer, head = name[1:].split("H", 1); value = int(layer) * 32 + int(head)
    if not 0 <= value < 1152: raise ValueError(f"invalid head: {name}")
    return value
def hname(value): return f"L{int(value)//32}H{int(value)%32:02d}"

def _exact(value, expected, label):
    if value != expected: raise RuntimeError(f"{label} mismatch: {value!r} != {expected!r}")

def load_and_validate_r003_query_heads(authority):
    path = Path(authority["summary_path"]); data = load_json(path)
    _exact(sha256(path), authority["summary_sha256"], "R-003 summary SHA-256")
    _exact(data.get("status"), "completed", "R-003 status")
    got = data["roles"][authority.get("role", "query_heads")]["fixed_heads"]
    _exact(got, authority["sets"], "R-003 query head sets")
    return {str(k): tuple(v) for k, v in got.items()}

def load_and_validate_r006_t003_reference_heads(authority):
    path = Path(authority["summary_path"]); data = load_json(path)
    _exact(sha256(path), authority["summary_sha256"], "R-006 T-003 summary SHA-256")
    _exact(data.get("schema"), T003_SCHEMA, "T-003 schema")
    _exact(data.get("trial_id"), authority.get("trial_id", "T-003"), "T-003 trial id")
    _exact(data.get("status"), "completed", "T-003 status")
    for key, expected in authority["parameters"].items(): _exact(data["parameters"].get(key), expected, f"T-003 parameter {key}")
    expected_integrity = {"records":140,"discovery":70,"evaluation":70,"sequence_overlap":0,"same_natural_query_bbox_rows":True,"gt_used_in_discovery":True,"heldout_reselection":False,"outcome_used_in_ranking":False,"failures":0}
    for key, expected in expected_integrity.items(): _exact(data["integrity"].get(key), expected, f"T-003 integrity {key}")
    got = data["discovery"]["fixed_heads"]
    _exact(got, authority["sets"], "T-003 reference head sets")
    return {str(k): tuple(v) for k, v in got.items()}, {"path":str(path),"sha256":sha256(path),"trial_id":data["trial_id"],"parameters":data["parameters"],"sets":got}

def normalize_and_aggregate_heads(maps):
    arrays = [np.asarray(x, dtype=float) for x in maps]
    if not arrays: raise ValueError("empty head ensemble")
    shape = arrays[0].shape
    if len(shape) != 2 or any(x.shape != shape for x in arrays): raise ValueError("head map shape mismatch")
    out=[]
    for x in arrays:
        if not np.isfinite(x).all() or (x < 0).any() or x.sum() <= 0: raise ValueError("head map must be finite, nonnegative, nonzero")
        out.append(x / x.sum())
    return np.mean(out, axis=0)

def layer_matched_random_sets_without_replacement(frozen_names, *, seed, repeats=100, heads_per_layer=32):
    frozen = tuple(frozen_names); layers = [hindex(x)//heads_per_layer for x in frozen]
    rng=np.random.default_rng(int(seed)); out=[]
    for _ in range(int(repeats)):
        selected=[]
        for layer in sorted(set(layers)):
            count=layers.count(layer)
            picks=rng.choice(heads_per_layer,size=count,replace=False)
            selected.extend((layer*heads_per_layer+int(h) for h in picks))
        # restore frozen layer order while preserving distinct sampled heads per layer
        pools={layer:[x for x in selected if x//heads_per_layer==layer] for layer in set(layers)}
        draw=tuple(pools[layer].pop() for layer in layers)
        if len(draw)!=len(frozen) or len(set(draw))!=len(draw) or sorted(x//heads_per_layer for x in draw)!=sorted(layers): raise RuntimeError("random layer-matched control contract")
        out.append(draw)
    return tuple(out)

def outcome_label(record):
    if record.get("parse_status") not in (None,"ok") or record.get("natural_iou") is None: return "unparsed"
    if record.get("natural_pn_label", "positive") != "positive" or record.get("positive") is False: return "nonpositive"
    value=float(record["natural_iou"])
    if not np.isfinite(value): return "unparsed"
    return "correct" if value >= .7 else "error" if value < .1 else "middle"

def largest4n(mask):
    mask=np.asarray(mask,bool); seen=np.zeros_like(mask,bool); h,w=mask.shape; components=[]
    for y,x in zip(*np.where(mask)):
        if seen[y,x]: continue
        q=deque([(int(y),int(x))]); seen[y,x]=True; pts=[]
        while q:
            a,b=q.popleft(); pts.append((a,b))
            for u,v in ((a-1,b),(a+1,b),(a,b-1),(a,b+1)):
                if 0<=u<h and 0<=v<w and mask[u,v] and not seen[u,v]: seen[u,v]=True; q.append((u,v))
        components.append(pts)
    if not components: raise ValueError("empty S30 support")
    winner=min(components,key=lambda z:(-len(z),min(a*w+b for a,b in z))); out=np.zeros_like(mask,bool)
    for y,x in winner: out[y,x]=True
    return out

def s30_metrics(attention,target):
    a=np.asarray(attention,float); t=np.asarray(target,float)
    if a.ndim!=2 or a.shape!=t.shape or not np.isfinite(a).all() or (a<0).any() or a.sum()<=0 or not np.isfinite(t).all() or t.sum()<=0: raise ValueError("invalid map/occupancy")
    k=int(np.ceil(.30*a.size)); order=np.argsort(-a.ravel(),kind="stable"); s=np.zeros(a.size,bool); s[order[:k]]=True; s=s.reshape(a.shape); g=t>0; c=largest4n(s)
    def overlap(x):
        inter=int(np.logical_and(x,g).sum()); union=int(np.logical_or(x,g).sum()); return inter,union,float(inter/union)
    si,su,sio=overlap(s); ci,cu,cio=overlap(c)
    return {"core30_hit":int(si>0),"s30_token_count":k,"gt_token_count":int(g.sum()),"s30_intersection_tokens":si,"s30_union_tokens":su,"s30_iou":sio,"largest4n_hit":int(ci>0),"largest4n_token_count":int(c.sum()),"largest4n_fraction_of_s30":float(c.sum()/k),"largest4n_intersection_tokens":ci,"largest4n_union_tokens":cu,"largest4n_iou":cio}

def bootstrap_correct_minus_error(rows, metric, *, seed, repeats):
    c=np.asarray([r[metric] for r in rows if r["outcome"]=="correct"],float); e=np.asarray([r[metric] for r in rows if r["outcome"]=="error"],float)
    result={"n_correct":len(c),"n_error":len(e),"correct":{"mean":None,"median":None},"error":{"mean":None,"median":None},"difference":None,"ci95":None,"reason":None}
    if not len(c) or not len(e): result["reason"]="empty correct or error stratum"; return result
    result["correct"]={"mean":float(c.mean()),"median":float(np.median(c))}; result["error"]={"mean":float(e.mean()),"median":float(np.median(e))}; result["difference"]=float(c.mean()-e.mean())
    rng=np.random.default_rng(int(seed)); draws=c[rng.integers(len(c),size=(int(repeats),len(c)))].mean(1)-e[rng.integers(len(e),size=(int(repeats),len(e)))].mean(1); result["ci95"]=[float(np.quantile(draws,.025)),float(np.quantile(draws,.975))]; return result

def bootstrap_difference_in_differences(rows, selected, control, metric, *, seed, repeats):
    paired=[]
    for row in rows:
        if row["outcome"] in ("correct","error"): paired.append({"outcome":row["outcome"],metric:row["methods"][selected][metric]-row["methods"][control][metric]})
    out=bootstrap_correct_minus_error(paired,metric,seed=seed,repeats=repeats); out["definition"]=f"({selected}-{control}) correct mean minus ({selected}-{control}) error mean"; return out
