import json
from pathlib import Path
p=Path(__file__).resolve().parents[1];src=p/'sources'
a=[json.loads(x) for x in (src/'150-predictions.jsonl').read_text().splitlines()];b=[json.loads(x) for x in (src/'200-predictions.jsonl').read_text().splitlines()]
a={x['dataset_index']:x for x in a};b={x['dataset_index']:x for x in b}
assert len(a)==len(b)==1766 and set(a)==set(b)
m=json.loads((src/'200-manifest.json').read_text());assert m==json.loads((src/'150-manifest.json').read_text())
for i in a:assert (a[i]['id'],a[i]['target'])==(b[i]['id'],b[i]['target'])
valid=lambda x:x.get('variable_candidate_format_valid',False)
sel=lambda x:x['iou']
ora=lambda x:x['oracle_iou']
cs={
 'rescue':[i for i,x in b.items() if valid(x) and x['candidate_count']>1 and x['first_candidate_iou']<.5 and sel(x)>=.5],
 'selection_failure':[i for i,x in b.items() if valid(x) and x['candidate_count']>1 and ora(x)>=.5 and sel(x)<.5],
 'ineffective_extra':[i for i,x in b.items() if valid(x) and x['candidate_count']>1 and ora(x)<.5 and ora(x)-x['first_candidate_iou']<=.01],
 'improved':[i for i,x in b.items() if valid(x) and valid(a[i]) and x['candidate_count']>1 and sel(x)-sel(a[i])>=.2],
 'regressed':[i for i,x in b.items() if valid(x) and valid(a[i]) and max(x['candidate_count'],a[i]['candidate_count'])>1 and sel(a[i])-sel(x)>=.2]}
keys={'rescue':lambda i:sel(b[i])-b[i]['first_candidate_iou'],'selection_failure':lambda i:ora(b[i])-sel(b[i]),'ineffective_extra':lambda i:b[i]['candidate_count'],'improved':lambda i:sel(b[i])-sel(a[i]),'regressed':lambda i:sel(a[i])-sel(b[i])}
cases=[];used=set()
for group,ids in cs.items():
 sequences=set()
 for i in sorted(ids,key=lambda i:(-keys[group](i),i)):
  if i in used or b[i]['sequence'] in sequences:continue
  cases.append(dict(index=i,category=group,step150=a[i],step200=b[i],manifest=m[i]));used.add(i);sequences.add(b[i]['sequence'])
  if len(sequences)==3:break
summary={}
for step,rows in [(150,a),(200,b)]:
 v=[x for x in rows.values() if valid(x)];multi=[x for x in v if x['candidate_count']>1]
 summary[step]=dict(n=len(rows),valid=len(v),multibox=len(multi),multibox_rate=len(multi)/len(rows),selected_miou=sum(x['iou'] for x in rows.values())/len(rows),oracle_miou=sum(x['oracle_iou'] for x in rows.values())/len(rows),multi_selected=sum(x['iou'] for x in multi)/len(multi),multi_oracle=sum(x['oracle_iou'] for x in multi)/len(multi),rescue=sum(x['first_candidate_iou']<.5 and x['iou']>=.5 for x in multi),selection_failure=sum(x['oracle_iou']>=.5 and x['iou']<.5 for x in multi))
(p/'cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2));(p/'summary.json').write_text(json.dumps(dict(metrics=summary,category_pool_counts={k:len(v) for k,v in cs.items()},selection='Top magnitude per category, maximum one per sequence, globally unique; illustrative not representative',cases=len(cases)),indent=2))
print((p/'summary.json').read_text())
