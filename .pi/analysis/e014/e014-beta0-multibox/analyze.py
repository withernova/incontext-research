"""Matched-update observational comparison of the two explicitly referenced Runs."""
import collections,hashlib,json,math,pathlib,re
ROOT=pathlib.Path('/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014')
NEW=ROOT/'e014-structure-score-iou-explore-v1-beta0-sft659-seed11451/payload'
OLD=ROOT/'e014-structure-score-iou-explore-v1-sft659-seed11451/payload'
OUT=ROOT/'e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis'
OUT.mkdir(exist_ok=True);(OUT/'source_snapshot').mkdir(exist_ok=False)
AUDIT=[]
def snapshot(p,prefix):
 size=p.stat().st_size
 with p.open('rb') as f:data=f.read(size)
 dest=OUT/'source_snapshot'/(prefix+'_'+p.name);dest.write_bytes(data)
 AUDIT.append(dict(source=str(p),snapshot=str(dest),size=len(data),sha256=hashlib.sha256(data).hexdigest()))
 return data
configs={k:json.loads(snapshot(p/'trainer_config.json',k)) for k,p in [('beta0',NEW),('beta004',OLD)]}
assert configs['beta0']['beta']==0. and configs['beta004']['beta']==.04
ignore={'beta','manifest','symmetry_manifest','output_dir'}
assert all(configs['beta0'].get(k)==configs['beta004'].get(k) for k in set(configs['beta0'])|set(configs['beta004']) if k not in ignore)
assert configs['beta0']['reward_scheme']=='structure_score_selected_iou_explore_v1' and configs['beta0']['group_size']==4
completed={}
for name,p in [('beta0',NEW),('beta004',OLD)]:
 ranks=collections.defaultdict(set)
 for m in re.finditer(rb'\{"rank":\s*\d+,\s*"step":\s*\d+,[^{}\n]*\}',snapshot(p/'training.log',name)):
  try:d=json.loads(m[0])
  except ValueError:continue
  if 'gradient_norm' in d:ranks[d['rank']].add(d['step'])
 assert set(ranks)==set(range(8))
 n=0
 while all(n+1 in ranks[k] for k in range(8)):n+=1
 completed[name]=n
cutoff=min(completed.values(),150);assert cutoff>0
rows={};groups={};excluded={}
for name,p in [('beta0',NEW),('beta004',OLD)]:
 rr=[];skip=0;gg=collections.defaultdict(list)
 for path in sorted((p/'grpo').glob('rollouts-rank*.jsonl')):
  rank=int(re.search(r'rank(\d+)',path.name)[1])
  for line in snapshot(path,name).splitlines(keepends=True):
   if not line.endswith(b'\n'):continue
   d=json.loads(line)
   if d['step']>=cutoff:skip+=1;continue
   r=d['reward'];assert r['reward_scheme']==configs[name]['reward_scheme']
   if r['valid']:
    assert len(r['scores'])==r['candidate_count']
    u=r['selected_iou'] if d['target_present'] else 0
    E=max((s-y)**2 for s,y in zip(r['scores'],r['correctness_labels']))
    expected=1-.12*r['order_violation']+1.1*(1-E)+u+(-.2 if d['target_present'] and u<.3 and not r['has_distinct_pair'] else 0)
    assert math.isclose(expected,r['total'],abs_tol=1e-10)
   else:assert r['total']==-1
   d['_rank']=rank;rr.append(d);gg[(rank,d['step'],d['sample_id'])].append(d)
 assert len(rr)==cutoff*64 and len(gg)==cutoff*16 and all(len(v)==4 for v in gg.values())
 rows[name]=rr;groups[name]=gg;excluded[name]=skip
assert groups['beta0'].keys()==groups['beta004'].keys(), 'prompt schedule mismatch'
def cond(r):return r.get('training_source','original')+(':positive' if r['target_present'] else ':negative')
assert all(cond(groups['beta0'][k][0])==cond(groups['beta004'][k][0]) for k in groups['beta0'])
def mean(v):return sum(v)/len(v) if v else None
def multi(r):return r['reward']['valid'] and r['reward']['candidate_count']>1
def rawmulti(r):return r['text'].count('<answer>')>=2
def summary(rs):
 valid=[r for r in rs if r['reward']['valid']];m=[r for r in rs if multi(r)];raw=[r for r in rs if rawmulti(r)];pos=[r for r in valid if r['target_present']];mp=[r for r in m if r['target_present']]
 return dict(rollouts=len(rs),valid=len(valid),valid_multi=len(m),raw_multi=len(raw),raw_multi_invalid=sum(not r['reward']['valid'] for r in raw),multi_rate_all=len(m)/len(rs) if rs else None,multi_rate_valid=len(m)/len(valid) if valid else None,raw_multi_rate=len(raw)/len(rs) if rs else None,last_valid_multi_update=max((r['step']+1 for r in m),default=None),last_raw_multi_update=max((r['step']+1 for r in raw),default=None),multi_positive_adv=sum(r['advantage']>1e-6 for r in m),multi_negative_adv=sum(r['advantage']< -1e-6 for r in m),multi_mean_adv=mean([r['advantage'] for r in m]),positive_selected_miou=mean([r['reward']['selected_iou'] for r in pos]),multibox_positive_count=len(mp),multibox_selected_miou=mean([r['reward']['selected_iou'] for r in mp]),multibox_oracle_miou=mean([max(r['reward']['candidate_ious']) for r in mp]))
conditions=sorted(set(cond(r) for r in rows['beta0']))
result=dict(completed_by_run=completed,matched_update_end=cutoff,matching_prompt_groups=len(groups['beta0']),excluded_rows=excluded,config_difference='beta .04->0; independent input/output paths; all other trainer fields equal',runs={})
for name,rr in rows.items():
 result['runs'][name]=dict(overall=summary(rr),by_condition={c:summary([r for r in rr if cond(r)==c]) for c in conditions},per_update=[dict(update=i+1,**summary([r for r in rr if r['step']==i])) for i in range(cutoff)],windows=[dict(start=i+1,end=min(i+5,cutoff),**summary([r for r in rr if i<=r['step']<min(i+5,cutoff)])) for i in range(0,cutoff,5)])
(OUT/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(OUT/'integrity_audit.json').write_text(json.dumps(dict(sources=AUDIT,reward_recalculation='passed',matched_prompt_groups='passed',group_size=4,cutoff=cutoff),indent=2)+'\n')
metrics={'matched_updates':cutoff}
for name,v in result['runs'].items():
 for k in ['rollouts','valid_multi','raw_multi','multi_rate_all','raw_multi_rate','last_valid_multi_update']:
  metrics[name+'.'+k]=v['overall'][k]
(OUT/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps({'matched_updates':cutoff,'comparison':{k:v['overall'] for k,v in result['runs'].items()}},ensure_ascii=False),flush=True)
