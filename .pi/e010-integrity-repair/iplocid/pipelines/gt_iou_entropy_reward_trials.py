"""Frozen R-003 GT-IoU reward variants for E010-R-006 (offline diagnostic)."""
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path
import numpy as np
from iplocid.pipelines.per_image_nogt_oracle import sha, score, aggregate, random_sets, bootstrap, summary, hname, entropy, METRICS

from iplocid.pipelines.e010_integrity import T003_PARAMETERS

def validate_rank_config(c):
    """Fail closed: trial metadata cannot claim a formula different from code."""
    if c.get("iou_metric") != "support50_fiou":
        raise ValueError("only support50_fiou is implemented")
    form=c.get("reward_form")
    expected={
        "linear_iou_reward":"-normalized_entropy + iou_reward_weight * support50_fiou",
        "thresholded_iou_bonus":"-normalized_entropy + iou_reward_weight * max(0, support50_fiou-iou_threshold)",
        "multiplicative_iou_reward":"(1-normalized_entropy) * (1 + iou_reward_weight * support50_fiou)",
    }
    if form in expected and c.get("rank_score") != expected[form]:
        raise ValueError("rank_score metadata does not match implemented reward formula")
    if form == "thresholded_iou_bonus":
        for key, value in T003_PARAMETERS.items():
            if c.get(key) != value: raise ValueError(f"T-003 {key} mismatch")


def rank(a, target, c):
    validate_rank_config(c)
    individual=[score(a[h], target) for h in range(1152)]
    norm=np.asarray([entropy(a[h])/np.log(a[h].size) for h in range(1152)])
    iou=np.asarray([x["support50_fiou"] for x in individual])
    w=float(c["iou_reward_weight"]); ew=float(c["entropy_weight"]); form=c["reward_form"]
    if form == "linear_iou_reward": value=-ew*norm+w*iou
    elif form == "multiplicative_iou_reward": value=(1-ew*norm)*(1+w*iou)
    elif form == "thresholded_iou_bonus": value=-ew*norm+w*np.maximum(0,iou-float(c["iou_threshold"]))
    elif form == "multiplicative_iou_plus_max_token_hit":
        hit=np.asarray([x["pointing_hit"] for x in individual], dtype=float)
        value=(1-ew*norm)*(1+w*iou)+float(c["max_token_hit_reward_weight"])*hit
    else: raise ValueError(f"unknown reward form {form}")
    order=sorted(range(1152),key=lambda h:(-value[h],h))
    return order, individual, norm, value

def delta(a,b,seed,reps):
    return {m:{"mean":float(np.mean([x[m]-y[m] for x,y in zip(a,b)])),"bootstrap95":bootstrap([x[m]-y[m] for x,y in zip(a,b)],seed,reps)} for m in METRICS}
def run(c):
    validate_rank_config(c)
    out=Path(c["run_dir"]); (out/"analysis").mkdir(parents=True,exist_ok=True)
    r3=Path(c["r003_run_dir"]); src=Path(c["source_run_dir"]); base=Path(c["baseline_r006_dir"])
    ss=load(r3/"analysis/summary.json"); subsets=load(r3/"manifests/subsets.json"); payload=load(src/"records.json")
    if ss.get("status")!="completed" or payload.get("failures") or len(subsets["discovery"])!=70 or len(subsets["evaluation"])!=70 or set(subsets["discovery"])&set(subsets["evaluation"]): raise RuntimeError("frozen split/source contract")
    if sha(r3/"manifests/subsets.json")!=ss["integrity"]["subsets_sha256"] or sha(r3/"manifests/row_span_contract.json")!=ss["integrity"]["row_span_contract_sha256"]: raise RuntimeError("R003 hash contract")
    arrays={}; targets={}
    for i,r in enumerate(payload["records"]):
        p=src/"artifacts"/f"sample_{i:04d}.npz"
        if r["index"]!=i or not p.exists() or not str(r.get("natural_response","")).startswith("["): raise RuntimeError(f"artifact contract {i}")
        with np.load(p) as z: a=z["q_to_r"].astype(float).reshape(1152,*z["q_to_r"].shape[-2:])
        t=np.asarray(r["targets"]["reference"],float)
        if a.shape[1:]!=t.shape or not np.isfinite(a).all() or (a<0).any() or t.sum()<=0: raise RuntimeError(f"grid contract {i}")
        arrays[i]=a; targets[i]=t
    top1=Counter(); discovery=[]
    for i in subsets["discovery"]:
        order,ind,ent,val=rank(arrays[i],targets[i],c); top1[order[0]]+=1
        discovery.append({"index":i,"sample_id":payload["records"][i]["sample_id"],"top1":order[0],"top10":order[:10],"top1_reward":float(val[order[0]]),"top1_entropy_normalized":float(ent[order[0]]),"top1_iou":ind[order[0]]["support50_fiou"]})
    fixed={k:[h for h,_ in sorted(top1.items(),key=lambda x:(-x[1],x[0]))[:k]] for k in (3,5)}
    if any(len(v)!=k for k,v in fixed.items()): raise RuntimeError("insufficient frozen heads")
    seed=int(c["seed"]); reps=int(c["random_repeats"]); boot=int(c["bootstrap_repeats"]); heldout={}
    baseline=load(base/"analysis/summary.json")["heldout"]
    for k,heads in fixed.items():
        random=random_sets(heads,list(range(1152)),seed+k,reps); rows=[]
        for i in subsets["evaluation"]:
            a,t=arrays[i],targets[i]; order,individual,_,_=rank(a,t,c); fixed_score=score(aggregate(a,heads),t); rr=[score(aggregate(a,x),t) for x in random]; rm={m:float(np.mean([z[m] for z in rr])) for m in METRICS}
            rows.append({"index":i,"sample_id":payload["records"][i]["sample_id"],"fixed":fixed_score,"random_layer_matched_mean":rm,"all_head_mean":score(a.mean(0),t),"per_image_gt_oracle":individual[order[0]],"oracle_in_fixed":int(order[0] in heads)})
        heldout[str(k)]={"fixed_heads":[hname(h) for h in heads],"random_layer_matched_sets":[[hname(h) for h in x] for x in random],"fixed":summary([x["fixed"] for x in rows]),"random_layer_matched":summary([x["random_layer_matched_mean"] for x in rows]),"all_head_mean":summary([x["all_head_mean"] for x in rows]),"per_image_gt_oracle":summary([x["per_image_gt_oracle"] for x in rows]),"paired_fixed_minus_random":delta([x["fixed"] for x in rows],[x["random_layer_matched_mean"] for x in rows],seed+k,boot),"baseline_r006_fixed":baseline[str(k)]["fixed"],"delta_vs_baseline_r006_fixed":delta([x["fixed"] for x in rows],[baseline[str(k)]["records"][j]["fixed"] for j in range(70)],seed+100+k,boot),"heldout_oracle_head_coverage":float(np.mean([x["oracle_in_fixed"] for x in rows])),"records":rows}
    manifest={"schema":"iplocid.e010.gt-iou-entropy-reward-trial/v1","trial_id":c["trial_id"],"parameters":{x:c[x] for x in ("reward_form","iou_metric","entropy_weight","iou_reward_weight","iou_threshold","max_token_hit_reward_weight","max_token_metric","rank_score")},"status":"completed","integrity":{"records":140,"discovery":70,"evaluation":70,"sequence_overlap":0,"same_r003_split":True,"same_natural_query_bbox_rows":True,"no_model_load":True,"gt_used_in_discovery":True,"heldout_reselection":False,"outcome_used_in_ranking":False,"failures":0},"discovery":{"top1_frequency":{hname(h):int(n) for h,n in sorted(top1.items())},"fixed_heads":{str(k):[hname(h) for h in v] for k,v in fixed.items()},"records":discovery},"heldout":heldout,"claim_boundary":"GT-supervised offline reward diagnostic. Neither deployed selector nor evidence of causal/identity routing."}
    (out/"analysis/summary.json").write_text(json.dumps(manifest,indent=2,allow_nan=False)+"\n")
    metrics={"schema":"survey-tool.trial-metrics/v1","trial_id":c["trial_id"],"parameters":manifest["parameters"],"status":"completed","evaluation_records":70,"top3_pointing_rate":heldout["3"]["fixed"]["pointing_rate"],"top5_pointing_rate":heldout["5"]["fixed"]["pointing_rate"],"top3_pointing_delta_vs_random":heldout["3"]["paired_fixed_minus_random"]["pointing_hit"],"top5_pointing_delta_vs_random":heldout["5"]["paired_fixed_minus_random"]["pointing_hit"],"top3_pointing_delta_vs_r006":heldout["3"]["delta_vs_baseline_r006_fixed"]["pointing_hit"],"top5_pointing_delta_vs_r006":heldout["5"]["delta_vs_baseline_r006_fixed"]["pointing_hit"]}
    (out/"metrics.json").write_text(json.dumps(metrics,indent=2,allow_nan=False)+"\n")
    print(c["trial_id"] + "_COMPLETE records=140", flush=True)
def main():
    p=argparse.ArgumentParser(); p.add_argument("--config",required=True); run(load(p.parse_args().config))
if __name__ == "__main__": main()
