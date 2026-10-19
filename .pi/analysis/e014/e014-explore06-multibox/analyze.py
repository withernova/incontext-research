"""One fixed snapshot of the currently selected exploration-0.6 training."""
import pathlib,json,collections,re,hashlib,math
ROOT=pathlib.Path('/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014')
P=ROOT/'e014-structure-score-iou-explore-v1-beta0-explore06-sft659-seed11451/payload'
OUT=ROOT/'e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis'
OUT.mkdir(exist_ok=True);S=OUT/'source_snapshot';S.mkdir(exist_ok=False);sources=[]
def snapshot(p):
 size=p.stat().st_size
 with p.open('rb') as f:data=f.read(size)
 (S/p.name).write_bytes(data);sources.append(dict(source=str(p),size=len(data),sha256=hashlib.sha256(data).hexdigest()))
 return data
config=json.loads(snapshot(P/'trainer_config.json'));rw=config['reward']
assert config['beta']==0 and rw['exploration_penalty']==.6 and config['group_size']==4 and config['reward_scheme']=='structure_score_selected_iou_explore_v1'
completed=collections.defaultdict(set)
for m in re.finditer(rb'\{"rank":\s*\d+,\s*"step":\s*\d+,[^{}\n]*\}',snapshot(P/'training.log')):
 try:d=json.loads(m[0])
 except ValueError:continue
 if 'gradient_norm' in d:completed[d['rank']].add(d['step'])
assert set(completed)==set(range(8));cutoff=0
while all(cutoff+1 in completed[k] for k in range(8)):cutoff+=1
assert cutoff>0
rows=[];groups=collections.defaultdict(list);excluded=0;partial=0
for f in sorted((P/'grpo').glob('rollouts-rank*.jsonl')):
 rank=int(re.search(r'rank(\d+)',f.name)[1])
 for line in snapshot(f).splitlines(keepends=True):
  if not line.endswith(b'\n'):partial+=1;continue
  row=json.loads(line)
  if row['step']>=cutoff:excluded+=1;continue
  r=row['reward'];assert r['reward_scheme']==config['reward_scheme']
  if r['valid']:
   assert r['candidate_count']==len(r['scores'])==len(r['correctness_labels'])
   error=max((s-y)**2 for s,y in zip(r['scores'],r['correctness_labels']))
   loc=r['selected_iou'] if row['target_present'] else 0
   explore=-rw['exploration_penalty'] if row['target_present'] and loc<rw['exploration_threshold'] and not r['has_distinct_pair'] else 0
   expected=1-rw['order_penalty']*r['order_violation']+rw['score_weight']*(1-error)+rw['iou_weight']*loc+explore
   assert math.isclose(expected,r['total'],abs_tol=1e-10) and math.isclose(explore,r['exploration_reward'],abs_tol=1e-12)
  else:assert r['total']==-1
  groups[(rank,row['step'],row['sample_id'])].append(row);rows.append(row)
assert len(rows)==cutoff*64 and len(groups)==cutoff*16 and all(len(v)==4 for v in groups.values())
def cond(r):return r.get('training_source','original')+(':positive' if r['target_present'] else ':negative')
def vm(r):return r['reward']['valid'] and r['reward']['candidate_count']>1
def raw(r):return r['text'].count('<answer>')>=2
def summary(rs):
 v=[r for r in rs if r['reward']['valid']];m=[r for r in rs if vm(r)];rm=[r for r in rs if raw(r)];low=[r for r in v if r['target_present'] and r['reward']['selected_iou']<rw['exploration_threshold']]
 return dict(rollouts=len(rs),valid=len(v),valid_multi=len(m),valid_multi_rate_all=len(m)/len(rs) if rs else None,valid_multi_rate_valid=len(m)/len(v) if v else None,raw_multi=len(rm),raw_multi_invalid=sum(not r['reward']['valid'] for r in rm),raw_multi_rate=len(rm)/len(rs) if rs else None,last_valid_multi_update=max((r['step']+1 for r in m),default=None),last_raw_multi_update=max((r['step']+1 for r in rm),default=None),low_iou_positive=len(low),low_iou_distinct=sum(r['reward']['has_distinct_pair'] for r in low),candidate_count_histogram=dict(collections.Counter(str(r['reward']['candidate_count']) for r in v)),multi_positive_adv=sum(r['advantage']>1e-6 for r in m),multi_negative_adv=sum(r['advantage']< -1e-6 for r in m))
conditions=sorted(set(cond(r) for r in rows))
result=dict(parent_run=P.parent.name,completed_updates=cutoff,rollouts=len(rows),groups=len(groups),excluded_pending_rows=excluded,trailing_partial_lines=partial,overall=summary(rows),by_condition={c:summary([r for r in rows if cond(r)==c]) for c in conditions},per_update=[dict(update=u+1,**summary([r for r in rows if r['step']==u])) for u in range(cutoff)],windows=[dict(start=s+1,end=min(s+25,cutoff),**summary([r for r in rows if s<=r['step']<min(s+25,cutoff)])) for s in range(0,cutoff,25)],last20=summary([r for r in rows if r['step']>=max(0,cutoff-20)]),last50=summary([r for r in rows if r['step']>=max(0,cutoff-50)]))
(OUT/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(OUT/'integrity_audit.json').write_text(json.dumps(dict(sources=sources,config_beta=0,exploration_penalty=.6,reward_recalculation='passed',g4_groups='passed',completed_updates=cutoff),indent=2)+'\n')
metrics={'completed_updates':cutoff,'rollouts':len(rows),'valid_multibox_count':result['overall']['valid_multi'],'valid_multibox_rate_all':result['overall']['valid_multi_rate_all'],'raw_multibox_count':result['overall']['raw_multi'],'recent20_multibox_count':result['last20']['valid_multi'],'recent50_multibox_count':result['last50']['valid_multi']}
(OUT/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps({'completed_updates':cutoff,'overall':result['overall'],'last20':result['last20'],'last50':result['last50']},ensure_ascii=False),flush=True)
