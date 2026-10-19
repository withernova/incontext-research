"""固定75步已有轨迹的额外多框补偿离线扫描，不生成或更新模型。"""
import pathlib,json,collections,math,re,hashlib
ROOT=pathlib.Path('/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014')
P=ROOT/'e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis'
SRC=P/'source_snapshot'
OUT=ROOT/'e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep'
S=OUT/'source_snapshot';S.mkdir(exist_ok=False);sources=[]
WEIGHTS=[.1,.2,.3,.5]
def snapshot(p):
 data=p.read_bytes();(S/p.name).write_bytes(data);sources.append(dict(source=str(p),size=len(data),sha256=hashlib.sha256(data).hexdigest()));return data
cfg=json.loads(snapshot(SRC/'trainer_config.json'));assert cfg['beta']==0 and cfg['group_size']==4 and cfg['reward']['exploration_penalty']==.6 and cfg['reward']['multibox_bonus_weight']==.1
completed=collections.defaultdict(set)
for m in re.finditer(rb'\{"rank":\s*\d+,\s*"step":\s*\d+,[^{}\n]*\}',snapshot(SRC/'training.log')):
 d=json.loads(m[0])
 if 'gradient_norm' in d:completed[d['rank']].add(d['step'])
assert set(completed)==set(range(8));cutoff=0
while all(cutoff+1 in completed[k] for k in range(8)):cutoff+=1
assert cutoff==75
rows=[];groups=collections.defaultdict(list)
for p in sorted(SRC.glob('rollouts-rank*.jsonl')):
 rank=int(re.search(r'rank(\d+)',p.name)[1])
 for line in snapshot(p).splitlines(keepends=True):
  if not line.endswith(b'\n'):continue
  r=json.loads(line)
  if r['step']>=cutoff:continue
  r['_rank']=rank;r['_key']=(rank,r['step'],r['sample_id']);r['_eligible']=bool(r['reward']['valid'] and r['target_present'] and r['reward']['has_distinct_pair'])
  assert math.isclose(r['reward']['multibox_bonus_reward'] or 0,.1*r['_eligible'],abs_tol=1e-12)
  groups[r['_key']].append(r);rows.append(r)
assert len(rows)==4800 and len(groups)==1200 and all(len(g)==4 for g in groups.values())
cfs=[json.loads(l) for l in snapshot(P/'counterfactual_rows.jsonl').splitlines()]
multis=[r for r in rows if r['reward']['valid'] and r['reward']['candidate_count']>1]
assert len(multis)==len(cfs)==467
for r,cf in zip(multis,cfs):
 assert (r['_rank'],r['step']+1,r['sample_id'])==(cf['rank'],cf['update'],cf['sample_id'])
 assert r['reward']['scores']==cf['scores'] and r['reward']['candidate_ious']==cf['candidate_ious']
 assert math.isclose(r['reward']['total'],cf['full']['total'],abs_tol=1e-10)
 r['_cf']=cf

def mean(v):return sum(v)/len(v) if v else None
def normalize(v):
 mu=mean(v);std=math.sqrt(mean([(x-mu)**2 for x in v]));return [(x-mu)/(std+1e-6) for x in v]
def cond(r):return r.get('training_source','original')+(':positive' if r['target_present'] else ':negative')
def ismulti(r):return r['reward']['valid'] and r['reward']['candidate_count']>1
def risk(r):return r['reward']['valid'] and r['target_present'] and max(r['reward']['candidate_ious'])>=.5 and r['reward']['selected_iou']<.5

def rollout_summary(rs):
 ms=[r for r in rs if ismulti(r)];ps=[r for r in ms if r['target_present']];bad=[r for r in rs if risk(r)];correct=[r for r in ms if r['target_present'] and r['reward']['selected_iou']>=.5]
 firstcorrect=[r for r in ps if r['reward']['candidate_ious'][0]>=.5];firstbad=[r for r in ps if r['reward']['candidate_ious'][0]<.3]
 def csum(xs):
  ds=[r['_new_total']-r['_cf']['first_only']['total'] for r in xs]
  return dict(n=len(xs),full_vs_first_mean_delta=mean(ds),full_vs_first_win=sum(d>1e-10 for d in ds),full_vs_first_loss=sum(d< -1e-10 for d in ds),positive_adv=sum(r['_new_adv']>1e-6 for r in xs),negative_adv=sum(r['_new_adv']< -1e-6 for r in xs))
 return dict(rollouts=len(rs),multibox=len(ms),positive_multibox=len(ps),multibox_positive_adv=sum(r['_new_adv']>1e-6 for r in ms),multibox_negative_adv=sum(r['_new_adv']< -1e-6 for r in ms),positive_multibox_positive_adv=sum(r['_new_adv']>1e-6 for r in ps),positive_multibox_positive_adv_rate=sum(r['_new_adv']>1e-6 for r in ps)/len(ps) if ps else None,positive_multibox_mean_adv=mean([r['_new_adv'] for r in ps]),positive_multibox_reward_mean=mean([r['_new_total'] for r in ps]),first_correct=csum(firstcorrect),first_bad=csum(firstbad),selected_correct=csum(correct),selection_failure=csum(bad),positive_multi_negative_to_positive=sum(r['_base_adv']<=1e-6 and r['_new_adv']>1e-6 for r in ps))
def group_summary(gs):
 mixed=[g for g in gs if g['_mixed']]
 return dict(groups=len(gs),mixed_groups=len(mixed),mixed_equal_group_win_rate=mean([g['_q'] for g in mixed]),mixed_equal_group_tie_rate=mean([g['_tie'] for g in mixed]),mixed_mean_reward_difference=mean([g['_diff'] for g in mixed]),bonus_varies_groups=sum(g['_varies'] for g in gs),all_four_bonus_eligible=sum(g['_all_eligible'] for g in gs))
outputs=[];detail=[];groupdetail=[];baseline_error=0.;baseline_multi_sign_mismatch=0;unchanged_without_eligible=0
for weight in WEIGHTS:
 gmeta=[]
 for key,g in groups.items():
  original=[r['reward']['total'] for r in g];base_adv=normalize(original)
  rewards=[r['reward']['total']+(weight-.1)*r['_eligible'] for r in g];adv=normalize(rewards)
  eligible=[r['_eligible'] for r in g]
  for i,r in enumerate(g):
   r['_base_adv']=base_adv[i];r['_new_total']=rewards[i];r['_new_adv']=adv[i]
   if weight==.1:
    baseline_error=max(baseline_error,abs(adv[i]-r['advantage']))
    if ismulti(r):baseline_multi_sign_mismatch+=int((adv[i]>1e-6)!=(r['advantage']>1e-6))
   if not r['reward']['valid']:assert rewards[i]==-1.
   if not r['target_present']:assert math.isclose(rewards[i],original[i],abs_tol=1e-12)
   detail.append(dict(weight=weight,rank=r['_rank'],update=r['step']+1,sample_id=r['sample_id'],group_position=i,condition=cond(r),candidate_count=r['reward']['candidate_count'],valid=r['reward']['valid'],bonus_eligible=r['_eligible'],old_reward=original[i],new_reward=rewards[i],logged_advantage=r['advantage'],hypothetical_advantage=adv[i],selected_iou=r['reward']['selected_iou'],selection_failure=risk(r)))
  if not any(eligible):
   assert all(math.isclose(a,b,abs_tol=1e-12) for a,b in zip(adv,base_adv));unchanged_without_eligible+=int(weight==.1)
  if all(eligible):assert all(math.isclose(a,b,abs_tol=1e-9) for a,b in zip(adv,base_adv))
  m=[r for r in g if ismulti(r)];s=[r for r in g if r['reward']['valid'] and r['reward']['candidate_count']==1]
  pairs=[(a['_new_total'],b['_new_total']) for a in m for b in s]
  gm=dict(rank=key[0],update=key[1]+1,sample_id=key[2],condition=cond(g[0]),_mixed=bool(m and s),_q=sum(a>b for a,b in pairs)/len(pairs) if pairs else None,_tie=sum(abs(a-b)<=1e-12 for a,b in pairs)/len(pairs) if pairs else None,_diff=mean([r['_new_total'] for r in m])-mean([r['_new_total'] for r in s]) if m and s else None,_varies=any(eligible) and not all(eligible),_all_eligible=all(eligible))
  gmeta.append(gm);groupdetail.append(dict(weight=weight,**gm))
 conditions=sorted(set(cond(r) for r in rows))
 examples=[]
 for r in multis:
  if r['step']+1==73:
   examples.append(dict(first_iou=r['reward']['candidate_ious'][0],selected_iou=r['reward']['selected_iou'],scores=r['reward']['scores'],new_reward=r['_new_total'],first_only_reward=r['_cf']['first_only']['total'],delta_vs_first=r['_new_total']-r['_cf']['first_only']['total'],hypothetical_advantage=r['_new_adv']))
 outputs.append(dict(weight=weight,rollouts=rollout_summary(rows),groups=group_summary(gmeta),by_condition={c:dict(rollouts=rollout_summary([r for r in rows if cond(r)==c]),groups=group_summary([g for g in gmeta if g['condition']==c])) for c in conditions},windows=[dict(start=a,end=b,rollouts=rollout_summary([r for r in rows if a<=r['step']+1<=b]),groups=group_summary([g for g in gmeta if a<=g['update']<=b])) for a,b in [(1,25),(26,39),(40,75)]],update73_examples=examples))
assert baseline_multi_sign_mismatch==0
for a,b in zip(outputs,outputs[1:]):assert b['rollouts']['positive_multibox_positive_adv']>=a['rollouts']['positive_multibox_positive_adv']
result=dict(source_run=P.name,completed_updates=75,rollouts=4800,groups=1200,weights=WEIGHTS,scans=outputs,baseline_float64_max_advantage_difference=baseline_error,baseline_multibox_sign_mismatch=baseline_multi_sign_mismatch,no_bonus_eligible_groups=unchanged_without_eligible,warning='Frozen on-policy .1 trajectories only: no new rollouts, no model update, IoUs and multibox frequency do not change. Float64 diagnostic advantage is approximate to logged float32.')
(OUT/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(OUT/'sweep_rollouts.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in detail))
(OUT/'sweep_groups.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in groupdetail))
(OUT/'integrity_audit.json').write_text(json.dumps(dict(sources=sources,baseline_bonus=.1,conditional_exploration_penalty=.6,beta=0,cutoff=75,groups=1200,rollouts=4800,cf_rows=467,weights=WEIGHTS,source_group_and_cf_matching='passed',invalid_and_negative_rewards_unchanged='passed',no_eligible_groups_advantages_unchanged='passed',all_four_eligible_groups_advantages_unchanged='passed',baseline_multibox_sign_mismatch=baseline_multi_sign_mismatch,baseline_float64_max_advantage_difference=baseline_error),ensure_ascii=False,indent=2)+'\n')
metrics={f'mixed_win_rate_bonus_{str(x["weight"]).replace(".","_")}':x['groups']['mixed_equal_group_win_rate'] for x in outputs}
metrics.update({f'positive_multibox_positive_adv_bonus_{str(x["weight"]).replace(".","_")}':x['rollouts']['positive_multibox_positive_adv'] for x in outputs})
(OUT/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps({'scans':[{'weight':x['weight'],'groups':x['groups'],'rollouts':x['rollouts'],'update73_examples':x['update73_examples']} for x in outputs]},ensure_ascii=False),flush=True)
