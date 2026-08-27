"""Offline contract for E-010 fixed-head stability and held-out scoring."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Mapping, Sequence
import numpy as np
from iplocid.attention.selection import fixed_top, select_fixed_heads

SCHEMA = "iplocid.e010.fixed-head-validation/v1"
REQUIRED_CONFIG = ("records_path", "output_path", "seed", "discovery_groups", "evaluation_groups")


def _load(path): return json.loads(Path(path).read_text())
def _hash(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def _head(text):
    layer, head = str(text).lstrip("L").replace("H", ":").split(":")
    return int(layer), int(head)

def _maps(records, groups):
    selected = [r for r in records if r["group"] in set(groups)]
    if not selected: raise ValueError("selected groups contain zero records")
    return [{_head(name): value for name, value in r["head_maps"].items()} for r in selected]

def _overlap(left, right):
    a,b=set(left),set(right); return len(a & b) / len(a | b) if a or b else 1.0

def validate_split(records, discovery, evaluation):
    if set(discovery) & set(evaluation): raise ValueError("discovery and evaluation groups overlap")
    known={r.get("group") for r in records}
    missing=(set(discovery)|set(evaluation))-known
    if missing: raise ValueError(f"configured groups missing from records: {sorted(missing)}")
    if any(not r.get("sample_id") or not r.get("group") or not r.get("head_maps") for r in records):
        raise ValueError("every record needs sample_id, group, and nonempty head_maps")

def run(config: Mapping):
    missing=[k for k in REQUIRED_CONFIG if not config.get(k)]
    if missing: raise ValueError(f"missing required config values: {missing}")
    records=_load(config["records_path"]); records=records.get("records",records)
    if not isinstance(records,list) or not records: raise ValueError("records input is empty")
    validate_split(records,config["discovery_groups"],config["evaluation_groups"])
    repeats=config.get("repeat_discovery_groups") or [config["discovery_groups"]]
    selections=[]
    for groups in repeats:
        result=select_fixed_heads(_maps(records,groups),per_sample=int(config.get("per_sample",10)),mean_multiplier=float(config.get("mean_multiplier",1.0)))
        selections.append({"groups":groups,"top3":fixed_top(result,3),"top5":fixed_top(result,5),"ranked":result.ranked_heads,"frequency":result.frequency})
    fixed=selections[0]
    evaluation=[r for r in records if r["group"] in set(config["evaluation_groups"])]
    def score(heads):
        values=[]
        for record in evaluation:
            metrics=record.get("head_metrics",{})
            row=[]
            for head in heads:
                item=metrics.get(f"L{head[0]}H{head[1]:02d}")
                if item is None: raise ValueError(f"missing held-out metric for {head}")
                row.append(item)
            values.append({"sample_id":record["sample_id"],"group":record["group"],"metrics":row})
        return values
    manifest={"schema":SCHEMA,"seed":int(config["seed"]),"top3":[list(x) for x in fixed["top3"]],"top5":[list(x) for x in fixed["top5"]],"selection_hash":_hash({"top3":fixed["top3"],"top5":fixed["top5"],"config":config}),"repeat_overlap_top3":[_overlap(fixed["top3"],x["top3"]) for x in selections],"repeat_overlap_top5":[_overlap(fixed["top5"],x["top5"]) for x in selections],"evaluation":{"top3":score(fixed["top3"]),"top5":score(fixed["top5"])},"failures":[]}
    out=Path(config["output_path"]); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n"); return manifest

def main():
    parser=argparse.ArgumentParser(description="Validate fixed IPLoc-ID attention heads from pre-extracted records.")
    parser.add_argument("--config",required=True); args=parser.parse_args(); run(_load(args.config))
if __name__=="__main__": main()
