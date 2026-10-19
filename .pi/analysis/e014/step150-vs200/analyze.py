import json,statistics,collections
from pathlib import Path
p=Path(__file__).parent;data=json.loads((p/'evidence.json').read_text());out={}
mean=lambda v:sum(v)/len(v) if v else None
for step in ['150','200']:
 rows=data[step]['predictions'];valid=[r for r in rows if r['variable_candidate_format_valid']];multi=[r for r in valid if r['candidate_count']>1];resc=[r for r in multi if r['first_candidate_iou']<.5 and r['oracle_iou']>=.5];miss=[r for r in valid if r['oracle_iou']>=.5 and r['iou']<.5]
 out[step]={'n':len(rows),'multi_n':len(multi),'multi_selected':mean([r['iou'] for r in multi]),'multi_oracle':mean([r['oracle_iou'] for r in multi]),'oracle_hit':sum(r['oracle_iou']>=.5 for r in valid),'selected_hit':sum(r['iou']>=.5 for r in valid),'available_rescues':len(resc),'realized_rescues':sum(r['iou']>=.5 for r in resc),'oracle_hit_selected_miss':len(miss),'top_score_ties_multi':sum(sum(c['score']==max(x['score'] for x in r['candidates']) for c in r['candidates'])>1 for r in multi),'miss_examples':[{'index':r['dataset_index'],'dataset':r['dataset'],'candidates':[(c['iou'],c['score']) for c in r['candidates']]} for r in miss[:5]]}
a={r['dataset_index']:r for r in data['150']['predictions']};b={r['dataset_index']:r for r in data['200']['predictions']};assert a.keys()==b.keys();groups=collections.defaultdict(list)
for i in a:
 x,y=a[i],b[i];assert (x['id'],x['dataset'],x['target'])==(y['id'],y['dataset'],y['target'])
 def typ(r):return 'invalid' if not r['variable_candidate_format_valid'] else 'multi' if r['candidate_count']>1 else 'single'
 groups[typ(x)+'->'+typ(y)].append((x,y))
out['paired_groups']={k:dict(n=len(v),selected150=mean([x['iou'] for x,y in v]),selected200=mean([y['iou'] for x,y in v]),oracle150=mean([x.get('oracle_iou') or 0 for x,y in v]),oracle200=mean([y.get('oracle_iou') or 0 for x,y in v])) for k,v in groups.items()}
out['hit_transitions']={'lost':sum(a[i]['iou']>=.5 and b[i]['iou']<.5 for i in a),'gained':sum(a[i]['iou']<.5 and b[i]['iou']>=.5 for i in a)}
(p/'analysis.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
