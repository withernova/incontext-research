#!/usr/bin/env python3
"""Read-only R-007/R-008 overlap-140 audit and decomposition."""
import argparse, json, hashlib
from collections import Counter
from pathlib import Path
import numpy as np
from iplocid.pipelines.e010_integrity import outcome_label

def readl(p): return [json.loads(x) for x in Path(p).read_text().splitlines()]
def mean_by(rows, role, method, metric, label):
 x=[r['scores'][role][method][metric] for r in rows if r[label] in ('correct','error')]
 return float(np.mean(x)) if x else None
def diff(rows, role, method, metric, label):
 c=[r['scores'][role][method][metric] for r in rows if r[label]=='correct']; e=[r['scores'][role][method][metric] for r in rows if r[label]=='error']
 return None if not c or not e else {'correct_mean':float(np.mean(c)),'error_mean':float(np.mean(e)),'correct_minus_error':float(np.mean(c)-np.mean(e)),'n_correct':len(c),'n_error':len(e)}
def main():
 p=argparse.ArgumentParser();p.add_argument('--r001-records',required=True);p.add_argument('--r007-per-image',required=True);p.add_argument('--r008-per-image',required=True);p.add_argument('--r008-manifest',required=True);p.add_argument('--out-dir',required=True);a=p.parse_args()
 old=json.load(open(a.r001_records))['records']; manifest=json.load(open(a.r008_manifest)); new=readl(a.r008_per_image); r7=readl(a.r007_per_image)
 byseq={x['source']['sequence_cluster']:(i,x) for i,x in enumerate(manifest)}; byidx={x['index']:x for x in new}; mappings=[]; failures=[]
 for x in old:
  seq=f"{x['element']}/{x['group']}"; pair=byseq.get(seq)
  if not pair: failures.append({'old_index':x['index'],'sequence':seq,'reason':'missing_sequence'});continue
  r008_index,m=pair
  n=byidx.get(r008_index)
  if not n: failures.append({'old_index':x['index'],'sequence':seq,'reason':'missing_r008'});continue
  # exact old-source and full manifest agree on category/sequence; old bbox grid is compared to v3 target only through scores.
  oldout=outcome_label({'natural_pn_label':x['natural_pn_label'],'natural_iou':x['natural_iou'],'parse_status':'ok'})
  mappings.append({'r007_index':x['index'],'r008_index':r008_index,'sequence':seq,'category':x['element'],'old_response_sha256':hashlib.sha256(x['natural_response'].encode()).hexdigest(),'r008_response_sha256':n['row_span_contract']['response_text_sha256'],'old_positive':x['natural_pn_label']=='positive','r008_positive':n['natural']['positive'],'old_iou':x['natural_iou'],'r008_iou':n['natural']['natural_iou'],'old_outcome':oldout,'r008_outcome':n['outcome'],'r008_cohort':n['cohort']})
 if failures or len(mappings)!=140: raise RuntimeError(f'overlap mapping failed: {len(mappings)} mapped, failures={failures[:3]}')
 old_label={x['r008_index']:x['old_outcome'] for x in mappings}
 rows=[]
 for r in new:
  if r['index'] in old_label:
   q=dict(r);q['old_outcome']=old_label[r['index']];rows.append(q)
 metrics=('pointing','fractional_mass','s50_fiou','s30_iou','largest4n_iou'); roles=('q_to_q','q_to_r','rheads_t003_on_qbbox_to_reference'); methods=('top3','top5')
 strata={}
 for role in roles:
  strata[role]={}
  for method in methods: strata[role][method]={m:{'by_r007_old_outcome':diff(rows,role,method,m,'old_outcome'),'by_r008_new_outcome':diff(rows,role,method,m,'outcome')} for m in metrics}
 # old R-007 map metrics are included only for rows with matching original index; direct delta exposes map+definition changes, no causal attribution.
 r7by={(int(x['index']),x['role']):x for x in r7}; parity=[]
 for z in mappings:
  for role in roles:
   legacy='r_to_r' if role.startswith('rheads') else role
   o=r7by.get((z['r007_index'],legacy)); n=byidx[z['r008_index']]
   if o and 'top5' in o['methods']: parity.append({'r007_index':z['r007_index'],'r008_index':z['r008_index'],'role':role,'old_outcome':z['old_outcome'],'new_outcome':z['r008_outcome'],'r007_top5':{k:o['methods']['top5'][k] for k in metrics},'r008_top5':{k:n['scores'][role]['top5'][k] for k in metrics}})
 out={'schema':'iplocid.e010.r007-r008-overlap140-audit/v1','status':'completed','purpose':'read-only mapping and outcome-relabeling comparison; does not alter R-007/R-008 results','integrity':{'r007_source_records':len(old),'r008_manifest':len(manifest),'mapped':len(mappings),'mapping_failures':failures,'r008_records_in_overlap':len(rows),'r007_metric_rows_available':len(parity),'response_hash_equal':sum(x['old_response_sha256']==x['r008_response_sha256'] for x in mappings)},'outcome_transfer':{'|'.join(k):v for k,v in Counter((x['old_outcome'],x['r008_outcome']) for x in mappings).items()},'positive_transfer':{'|'.join(map(str,k)):v for k,v in Counter((x['old_positive'],x['r008_positive']) for x in mappings).items()},'response_hash_transfer':Counter(x['old_response_sha256']==x['r008_response_sha256'] for x in mappings),'mappings':mappings,'r008_same_maps_restratified':strata,'r007_to_r008_metric_pairs':parity,'limitations':['R-007 uses its frozen old natural artifacts while R-008 uses new frozen natural outputs; response hashes are explicitly audited, not assumed equal.','R-007 and R-008 map metrics are not asserted as bitwise-parity because their natural responses/rows may differ.','The same R-008 maps are separately stratified by R-007 old versus R-008 new outcomes, isolating outcome relabeling within R-008 maps; it does not establish causal mechanism.']}
 d=Path(a.out_dir);d.mkdir(parents=True,exist_ok=True);(d/'summary.json').write_text(json.dumps(out,indent=2)+'\n');(d/'mappings.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in mappings));print(json.dumps({'mapped':len(mappings),'response_hash_equal':out['integrity']['response_hash_equal'],'metric_pairs':len(parity),'out':str(d)}))
if __name__=='__main__':main()
