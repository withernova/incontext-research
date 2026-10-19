"""用户请求的一次固定训练快照与显式上一轮前缀对照；不加载模型。"""
import pathlib,json,collections,re,hashlib,math
ROOT=pathlib.Path('/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014')
P=ROOT/'e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-sft659-seed11451/payload'
B=ROOT/'e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis/source_snapshot'
OUT=ROOT/'e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis'
S=OUT/'source_snapshot';S.mkdir(exist_ok=False);sources=[]
def snapshot(p,label):
 size=p.stat().st_size
 with p.open('rb') as f:data=f.read(size)
 dest=S/label;dest.mkdir(exist_ok=True)
 (dest/p.name).write_bytes(data)
 sources.append(dict(source=str(p),snapshot=str(dest/p.name),size=len(data),sha256=hashlib.sha256(data).hexdigest()))
 return data
def load(base,label,bonus):
 cfg=json.loads(snapshot(base/'trainer_config.json',label));rw=cfg['reward']
 assert cfg['beta']==0 and rw['exploration_penalty']==.6 and rw.get('multibox_bonus_weight',0)==bonus
 assert cfg['group_size']==4 and cfg['seed']==11451 and cfg['reward_scheme']=='structure_score_selected_iou_explore_v1'
 completed=collections.defaultdict(set)
 for m in re.finditer(rb'\{"rank":\s*\d+,\s*"step":\s*\d+,[^{}\n]*\}',snapshot(base/'training.log',label)):
  d=json.loads(m[0])
  if 'gradient_norm' in d:completed[d['rank']].add(d['step'])
 assert set(completed)==set(range(8));cutoff=0
 while all(cutoff+1 in completed[k] for k in range(8)):cutoff+=1
 assert cutoff>0
 rows=[];groups=collections.defaultdict(list);excluded=0;partial=0
 files=sorted((base/'grpo' if label=='current' else base).glob('rollouts-rank*.jsonl'))
 assert len(files)==8
 for f in files:
  rank=int(re.search(r'rank(\d+)',f.name)[1])
  for line in snapshot(f,label).splitlines(keepends=True):
   if not line.endswith(b'\n'):partial+=1;continue
   row=json.loads(line)
   if row['step']>=cutoff:excluded+=1;continue
   r=row['reward'];assert r['reward_scheme']==cfg['reward_scheme']
   if r['valid']:
    assert r['candidate_count']==len(r['scores'])==len(r['correctness_labels'])
    error=max((s-y)**2 for s,y in zip(r['scores'],r['correctness_labels']))
    loc=r['selected_iou'] if row['target_present'] else 0
    explore=-rw['exploration_penalty'] if row['target_present'] and loc<rw['exploration_threshold'] and not r['has_distinct_pair'] else 0
    extra=bonus if row['target_present'] and r['has_distinct_pair'] else 0
    expected=1-rw['order_penalty']*r['order_violation']+rw['score_weight']*(1-error)+rw['iou_weight']*loc+explore+extra
    assert math.isclose(expected,r['total'],abs_tol=1e-10)
    assert math.isclose(explore,r['exploration_reward'],abs_tol=1e-12)
    if label=='current':
     assert math.isclose(extra,r['multibox_bonus_reward'],abs_tol=1e-12)
     assert r['multibox_bonus_eligible']==bool(row['target_present'] and r['has_distinct_pair'])
   else:assert r['total']==-1
   groups[(rank,row['step'],row['sample_id'])].append(row);rows.append(row)
 assert len(rows)==cutoff*64 and len(groups)==cutoff*16 and all(len(v)==4 for v in groups.values())
 return cfg,cutoff,rows,groups,dict(excluded_pending_rows=excluded,trailing_partial_lines=partial)
def cond(r):return r.get('training_source','original')+(':positive' if r['target_present'] else ':negative')
def vm(r):return r['reward']['valid'] and r['reward']['candidate_count']>1
def raw(r):return r['text'].count('<answer>')>=2
def mean(xs):return sum(xs)/len(xs) if xs else None
def quality(rs):
 ps=[r for r in rs if r['target_present'] and r['reward']['valid']]
 first=[r['reward']['candidate_ious'][0] for r in ps]
 selected=[r['reward']['selected_iou'] for r in ps]
 oracle=[max(r['reward']['candidate_ious']) for r in ps]
 return dict(positive_valid=len(ps),first_miou=mean(first),selected_miou=mean(selected),oracle_miou=mean(oracle),selected_hit50=sum(v>=.5 for v in selected),oracle_hit50=sum(v>=.5 for v in oracle),later_better=sum(o>f+1e-12 for f,o in zip(first,oracle)),selection_improved=sum(s>f+1e-12 for f,s in zip(first,selected)),selection_worsened=sum(s<f-1e-12 for f,s in zip(first,selected)),oracle_rescue50=sum(f<.5<=o for f,o in zip(first,oracle)),selected_rescue50=sum(f<.5<=s for f,s in zip(first,selected)),selected_loss50=sum(s<.5<=f for f,s in zip(first,selected)))
def summary(rs):
 v=[r for r in rs if r['reward']['valid']];m=[r for r in rs if vm(r)];rm=[r for r in rs if raw(r)]
 low=[r for r in v if r['target_present'] and r['reward']['selected_iou']<.3]
 neg=[r for r in v if not r['target_present']]
 return dict(rollouts=len(rs),valid=len(v),valid_multi=len(m),valid_multi_rate_all=len(m)/len(rs) if rs else None,valid_multi_rate_valid=len(m)/len(v) if v else None,raw_multi=len(rm),raw_multi_invalid=sum(not r['reward']['valid'] for r in rm),raw_multi_rate=len(rm)/len(rs) if rs else None,last_valid_multi_update=max((r['step']+1 for r in m),default=None),last_raw_multi_update=max((r['step']+1 for r in rm),default=None),low_iou_positive=len(low),low_iou_distinct=sum(r['reward']['has_distinct_pair'] for r in low),positive_distinct_count=sum(r['target_present'] and r['reward']['has_distinct_pair'] for r in v),accurate_distinct_count=sum(r['target_present'] and r['reward']['has_distinct_pair'] and r['reward']['selected_iou']>=.3 for r in v),candidate_count_histogram=dict(collections.Counter(str(r['reward']['candidate_count']) for r in v)),multi_positive_adv=sum(r['advantage']>1e-6 for r in m),multi_negative_adv=sum(r['advantage']< -1e-6 for r in m),quality_all=quality(rs),quality_multibox=quality(m),negative_max_score_mean=mean([max(r['reward']['scores']) for r in neg]))
def grouped_summary(rs):
 return dict(overall=summary(rs),by_condition={c:summary([r for r in rs if cond(r)==c]) for c in sorted(set(cond(r) for r in rs))})
config,cutoff,rows,groups,pending=load(P,'current',.1)
bconfig,bcutoff,brows,bgroups,bpending=load(B,'baseline',0)
a=json.loads(json.dumps(config));b=json.loads(json.dumps(bconfig))
for cfg in (a,b):
 for k in ('manifest','original_manifest','symmetry_manifest','output_dir'):cfg.pop(k,None)
 cfg['reward'].pop('multibox_bonus_weight',None)
assert a==b,'unexpected config differences'
common=min(cutoff,bcutoff)
keys={k for k in groups if k[1]<common};bkeys={k for k in bgroups if k[1]<common}
matched=keys==bkeys
if matched:assert all(cond(groups[k][0])==cond(bgroups[k][0]) for k in keys)
mixed=[]
for k,g in groups.items():
 singles=[r for r in g if r['reward']['valid'] and r['reward']['candidate_count']==1];multi=[r for r in g if vm(r)]
 if singles and multi:
  pairs=[(m['reward']['total'],s['reward']['total']) for m in multi for s in singles]
  mixed.append(dict(condition=cond(g[0]),update=k[1]+1,q=sum(m>s for m,s in pairs)/len(pairs),difference=mean([r['reward']['total'] for r in multi])-mean([r['reward']['total'] for r in singles])))
result=dict(parent_run=P.parent.name,completed_updates=cutoff,rollouts=len(rows),groups=len(groups),**pending,**grouped_summary(rows),windows=[dict(start=s+1,end=min(s+25,cutoff),**grouped_summary([r for r in rows if s<=r['step']<min(s+25,cutoff)])) for s in range(0,cutoff,25)],last20=grouped_summary([r for r in rows if r['step']>=max(0,cutoff-20)]),last50=grouped_summary([r for r in rows if r['step']>=max(0,cutoff-50)]),mixed_groups=len(mixed),mixed_group_equal_weight_win_rate=mean([g['q'] for g in mixed]),mixed_mean_reward_difference=mean([g['difference'] for g in mixed]),comparison=dict(baseline_run='e014-structure-score-iou-explore-v1-beta0-explore06-sft659-seed11451',baseline_completed_updates=bcutoff,common_updates=common,matched_input_group_keys=matched,current=grouped_summary([r for r in rows if r['step']<common]),baseline=grouped_summary([r for r in brows if r['step']<common])))
(OUT/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(OUT/'integrity_audit.json').write_text(json.dumps(dict(sources=sources,reward_recalculation='passed',g4_groups='passed',config_difference='only multibox bonus and run paths',matched_input_group_keys=matched,completed_updates=cutoff,baseline_completed_updates=bcutoff),ensure_ascii=False,indent=2)+'\n')
metrics={k:result[k] for k in ('completed_updates','rollouts','groups')};metrics.update(valid_multibox_count=result['overall']['valid_multi'],valid_multibox_rate_all=result['overall']['valid_multi_rate_all'],recent20_multibox_count=result['last20']['overall']['valid_multi'],recent50_multibox_count=result['last50']['overall']['valid_multi'],matched_updates=common)
(OUT/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps({'completed_updates':cutoff,'overall':result['overall'],'last20':result['last20']['overall'],'last50':result['last50']['overall'],'comparison':result['comparison']},ensure_ascii=False),flush=True)
