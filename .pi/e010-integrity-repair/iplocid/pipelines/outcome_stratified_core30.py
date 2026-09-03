"""E010-R-007 immutable 140-artifact anchor with T-003 Reference authority."""
from __future__ import annotations
import argparse, json
from collections import defaultdict
from pathlib import Path
import numpy as np
from iplocid.attention.metrics import area_normalized_enrichment, fractional_mass, fractional_token_iou, pointing_hit, retained_mass_support
from iplocid.pipelines.e010_integrity import (bootstrap_correct_minus_error, bootstrap_difference_in_differences, hindex, hname, largest4n, layer_matched_random_sets_without_replacement, load_and_validate_r003_query_heads, load_and_validate_r006_t003_reference_heads, normalize_and_aggregate_heads, outcome_label, s30_metrics, sha256)
SCHEMA="iplocid.e010.outcome-stratified-core30/v4"; OUTCOMES=("correct","error")
READOUTS={"q_to_q":("query","q_to_q","query"),"q_to_r":("query","q_to_r","reference"),"rheads_t003_on_qbbox_to_reference":("reference","q_to_r","reference")}; ROLES={"r_to_r":READOUTS["rheads_t003_on_qbbox_to_reference"],"q_to_q":READOUTS["q_to_q"],"q_to_r":READOUTS["q_to_r"]}
def load(p): return json.loads(Path(p).read_text())
def outcome(r): return outcome_label(r)
def largest4n_compat(mask): return largest4n(mask)
def metrics(a,t):
 d=s30_metrics(a,t); a=np.asarray(a,float); k=d["s30_token_count"]; order=np.argsort(-a.ravel(),kind="stable"); s=np.zeros(a.size,bool); s[order[:k]]=True; s=s.reshape(a.shape); return {"hit":d["core30_hit"],"selected_token_count":k,**d},s,largest4n(s)
def core30_hit(a,t): d,_,_=metrics(a,t); return d["hit"],d["selected_token_count"]
def _spatial(a,t):
 a=normalize_and_aggregate_heads([a]); support=retained_mass_support(a,.5); d=s30_metrics(a,t)
 return {"pointing":int(pointing_hit(a,t)),"fractional_mass":fractional_mass(a,t),"enrichment":area_normalized_enrichment(a,t),"s50_fiou":fractional_token_iou(support,t),"selected_token_count_s50":int(support.sum()),**d}
def _summarize(rows, seed, repeats):
 out={"n":len(rows)}
 for metric in ("pointing","fractional_mass","enrichment","s50_fiou","core30_hit","s30_iou","largest4n_hit","largest4n_iou"):
  x=np.asarray([r[metric] for r in rows],float); out[metric]={"mean":float(x.mean()) if len(x) else None,"median":float(np.median(x)) if len(x) else None,"q25":float(np.quantile(x,.25)) if len(x) else None,"q75":float(np.quantile(x,.75)) if len(x) else None}
 return out
def run(c):
 source=Path(c["source_run_dir"]); r3=Path(c["r003_run_dir"]); out=Path(c["run_dir"]); records=load(source/"records.json")["records"]; subsets=load(r3/"manifests/subsets.json")
 qsets=load_and_validate_r003_query_heads(c["query_head_authority"]); rsets,rauth=load_and_validate_r006_t003_reference_heads(c["reference_head_authority"])
 if len(records)!=140 or sha256(r3/"analysis/summary.json")!=c["r003_summary_sha256"]: raise RuntimeError("R-007 source/R-003 contract")
 fixed={"query":{k:tuple(map(hindex,v)) for k,v in qsets.items()},"reference":{k:tuple(map(hindex,v)) for k,v in rsets.items()}}; controls={role:{k:layer_matched_random_sets_without_replacement(names,seed=int(c["seed"])+1000*ri+int(k),repeats=int(c["random_repeats"])) for k,names in (qsets if family=="query" else rsets).items()} for ri,(role,(family,_,_)) in enumerate(READOUTS.items())}
 rows=[]; exclusions=defaultdict(list)
 for i,r in enumerate(records):
  label=outcome_label(r)
  if label not in OUTCOMES: exclusions[label].append(i); continue
  p=source/"artifacts"/f"sample_{i:04d}.npz";
  if not p.is_file(): raise RuntimeError(f"missing artifact {i}")
  with np.load(p) as z: arrays={k:z[k].astype(float).reshape(1152,*z[k].shape[-2:]) for k in ("q_to_q","q_to_r")}
  for role,(family,key,targetkey) in READOUTS.items():
   target=np.asarray(r["targets"][targetkey],float); array=arrays[key]
   if array.shape[1:]!=target.shape: raise RuntimeError(f"grid mismatch {i} {role}")
   methods={}
   for size,heads in fixed[family].items():
    methods[f"top{size}"]=_spatial(normalize_and_aggregate_heads([array[h] for h in heads]),target)
    for h in heads: methods[hname(h)]=_spatial(array[h],target)
    random_maps=[normalize_and_aggregate_heads([array[h] for h in draw]) for draw in controls[role][size]]; methods[f"top{size}_random"]={m:float(np.mean([_spatial(x,target)[m] for x in random_maps])) for m in methods[f"top{size}"]}
   methods["all_head_mean"]=_spatial(normalize_and_aggregate_heads(array),target)
   rows.append({"index":i,"sample_id":r["sample_id"],"cohort":"heldout" if i in set(subsets["evaluation"]) else "discovery","role":role,"outcome":label,"methods":methods})
 result={}
 for role in READOUTS:
  result[role]={"semantic_name":"rheads_t003_on_qbbox_to_reference" if role=="rheads_t003_on_qbbox_to_reference" else role,"cohorts":{}}
  for cohort, ids in {"all":set(range(140)),"heldout":set(subsets["evaluation"])}.items():
   block={}; rr=[x for x in rows if x["index"] in ids and x["role"]==role]
   for method in sorted(rr[0]["methods"]) if rr else []:
    values=[{"outcome":x["outcome"],**x["methods"][method]} for x in rr]; block[method]={"by_outcome":{o:_summarize([v for v in values if v["outcome"]==o],int(c["seed"]),int(c["bootstrap_repeats"])) for o in OUTCOMES},"correct_minus_error":{m:bootstrap_correct_minus_error(values,m,seed=int(c["seed"]),repeats=int(c["bootstrap_repeats"])) for m in ("pointing","fractional_mass","enrichment","s50_fiou","core30_hit","s30_iou","largest4n_hit","largest4n_iou")}}
   for size in ("3","5"):
    selected=f"top{size}"; control=f"top{size}_random"
    if selected in block:
     block[selected]["vs_random_difference_in_differences"]={m:bootstrap_difference_in_differences(rr,selected,control,m,seed=int(c["seed"])+int(size),repeats=int(c["bootstrap_repeats"])) for m in ("pointing","fractional_mass","enrichment","s50_fiou","core30_hit","s30_iou","largest4n_hit","largest4n_iou")}
   result[role]["cohorts"][cohort]=block
 manifest={"schema":SCHEMA,"status":"completed","inputs":{"r001_records_sha256":sha256(source/"records.json"),"r003_summary_sha256":sha256(r3/"analysis/summary.json"),"r003_subsets_sha256":sha256(r3/"manifests/subsets.json"),"r003_row_span_contract_sha256":sha256(r3/"manifests/row_span_contract.json"),"r006_t003":rauth,"query_head_authority":c["query_head_authority"]},"row_contract":"all readouts are natural Query-bbox p−1 rows; r_to_r aliases rheads_t003_on_qbbox_to_reference; no Reference-bbox rows","integrity":{"source_records":140,"included":len({x["index"] for x in rows}),"exclusions":{k:list(v) for k,v in exclusions.items()},"heldout_count":70,"no_model_load":True,"random_control_repeats":c["random_repeats"]},"roles":result}
 stage=out/"staging"/SCHEMA.replace("/","_"); stage.mkdir(parents=True,exist_ok=True); (stage/"per_image_core30.jsonl").write_text("".join(json.dumps(x,allow_nan=False)+"\n" for x in rows)); (stage/"summary.json").write_text(json.dumps(manifest,indent=2,allow_nan=False)+"\n"); print("E010_R007_STAGED",stage)
def main(): p=argparse.ArgumentParser(); p.add_argument("--config",required=True); run(load(p.parse_args().config))
if __name__=="__main__": main()
