"""Offline contracts for E-010 identity, geometry, and intervention controls."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Mapping, Sequence
import numpy as np

SCHEMA="iplocid.e010.head-reliability-controls/v1"

def _load(path): return json.loads(Path(path).read_text())
def _sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require_run1_manifest(path, expected_hash=None):
    value=_load(path)
    if value.get("schema")!="iplocid.e010.fixed-head-validation/v1": raise ValueError("invalid Run 1 manifest schema")
    if expected_hash and value.get("selection_hash")!=expected_hash: raise ValueError("Run 1 selection hash mismatch")
    if not value.get("top3") or not value.get("top5"): raise ValueError("Run 1 supplied no fixed heads")
    return value

def transform_box(box: Sequence[float], width: float, height: float, mode: str):
    x1,y1,x2,y2=map(float,box)
    if mode=="identity": return [x1,y1,x2,y2]
    if mode=="horizontal_flip": return [width-x2,y1,width-x1,y2]
    if mode=="vertical_flip": return [x1,height-y2,x2,height-y1]
    raise ValueError(f"unsupported transform: {mode}")
def invert_box(box,width,height,mode): return transform_box(box,width,height,mode)
def transform_map(value,mode):
    arr=np.asarray(value)
    if mode=="identity": return arr.copy()
    if mode=="horizontal_flip": return np.fliplr(arr)
    if mode=="vertical_flip": return np.flipud(arr)
    raise ValueError(f"unsupported transform: {mode}")
def invert_map(value,mode): return transform_map(value,mode)
def center_of_mass(value):
    arr=np.maximum(np.asarray(value,dtype=np.float64),0); total=arr.sum()
    if total<=0 or not np.isfinite(total): raise ValueError("map has no finite positive mass")
    y,x=np.indices(arr.shape); return [float((x*arr).sum()/total),float((y*arr).sum()/total)]
def explanation_errors(original, transformed, mode):
    base=np.asarray(original,dtype=np.float64); changed=np.asarray(transformed,dtype=np.float64)
    restored=invert_map(changed,mode)
    return {"object_following_mse":float(np.mean((restored-base)**2)),"fixed_position_mse":float(np.mean((changed-base)**2)),"object_following_com_error":float(np.linalg.norm(np.subtract(center_of_mass(restored),center_of_mass(base))))}
def paired_identity(records):
    groups={}
    for row in records: groups.setdefault(row.get("pair_id"),{})[row.get("condition")]=row
    failures=[]; pairs=[]
    for key,items in groups.items():
        if not key or set(items)!={"correct_reference","wrong_reference"}: failures.append({"pair_id":key,"reason":"pair must contain correct_reference and wrong_reference"}); continue
        pairs.append({"pair_id":key,"correct":items["correct_reference"],"wrong":items["wrong_reference"]})
    return pairs,failures

def run(config: Mapping):
    for key in ("run1_manifest","records_path","output_path"):
        if not config.get(key): raise ValueError(f"missing required config value: {key}")
    run1=require_run1_manifest(config["run1_manifest"],config.get("expected_selection_hash"))
    if config.get("require_run1_gate",True) and not config.get("run1_gate_passed",False): raise ValueError("Run 1 gate did not pass; Run 2 is cancelled")
    raw=_load(config["records_path"]); records=raw.get("records",raw)
    if not isinstance(records,list) or not records: raise ValueError("controls input is empty")
    pairs,failures=paired_identity([r for r in records if r.get("condition") in {"correct_reference","wrong_reference"}])
    geometry=[]
    for row in records:
        if row.get("condition") not in {"reference_transform","query_transform"}: continue
        if not row.get("original_map") or not row.get("transformed_map"): failures.append({"sample_id":row.get("sample_id"),"reason":"missing geometry maps"}); continue
        geometry.append({"sample_id":row.get("sample_id"),"condition":row["condition"],**explanation_errors(row["original_map"],row["transformed_map"],row["transform"])})
    if not pairs or not geometry: raise ValueError("controls require nonempty identity pairs and geometry records")
    result={"schema":SCHEMA,"run1_selection_hash":run1["selection_hash"],"run1_manifest_sha256":_sha(config["run1_manifest"]),"fixed_heads":{"top3":run1["top3"],"top5":run1["top5"]},"identity_pairs":pairs,"geometry":geometry,"failures":failures,"intervention":{"eligible":bool(config.get("identity_gate_passed",False) and config.get("geometry_gate_passed",False)),"status":"not_executed_offline_contract"}}
    out=Path(config["output_path"]); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n"); return result

def main():
    parser=argparse.ArgumentParser(description="Evaluate E-010 identity and geometry controls from paired records.")
    parser.add_argument("--config",required=True); args=parser.parse_args(); run(_load(args.config))
if __name__=="__main__": main()
