"""75步固定快照：反事实单框奖励及实际G4组信号诊断，无模型重放。"""
import pathlib,json,math,re,hashlib,collections
ROOT=pathlib.Path('/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014')
SRC=ROOT/'e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis/source_snapshot'
OUT=ROOT/'e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis'
S=OUT/'source_snapshot';S.mkdir(exist_ok=False);sources=[]
def snapshot(p):
 data=p.read_bytes();(S/p.name).write_bytes(data)
 sources.append(dict(source=str(p),size=len(data),sha256=hashlib.sha256(data).hexdigest()))
 return data
cfg=json.loads(snapshot(SRC/'trainer_config.json'));rw=cfg['reward']
assert cfg['beta']==0 and cfg['group_size']==4 and rw['exploration_penalty']==.6 and rw['multibox_bonus_weight']==.1
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
  row=json.loads(line)
  if row['step']>=cutoff:continue
  row['_rank']=rank;row['_key']=(rank,row['step'],row['sample_id'])
  rows.append(row);groups[row['_key']].append(row)
assert len(rows)==4800 and len(groups)==1200 and all(len(g)==4 for g in groups.values())
def mean(v):return sum(v)/len(v) if v else None
def normalize(v):
 mu=mean(v);std=math.sqrt(mean([(r-mu)**2 for r in v]));return [(r-mu)/(std+1e-6) for r in v]
def cond(r):return r.get('training_source','original')+(':positive' if r['target_present'] else ':negative')
def iou(a,b):
 inter=max(0.,min(a[2],b[2])-max(a[0],b[0]))*max(0.,min(a[3],b[3])-max(a[1],b[1]))
 return inter/((a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-inter)
def components(row,indices=None):
 r=row['reward'];indices=list(range(r['candidate_count'])) if indices is None else indices
 scores=[r['scores'][i] for i in indices];ys=[r['correctness_labels'][i] for i in indices];boxes=[row['_boxes'][i] for i in indices]
 order=any(a[0]+a[2]>b[0]+b[2] for a,b in zip(boxes,boxes[1:]))
 distinct=any(iou(a,b)<rw['distinct_threshold'] for i,a in enumerate(boxes) for b in boxes[i+1:])
 k=max(range(len(indices)),key=lambda i:scores[i]);loc=r['candidate_ious'][indices[k]] if row['target_present'] else 0.
 error=max((s-y)**2 for s,y in zip(scores,ys))
 c=dict(structure=1-rw['order_penalty']*order,score=rw['score_weight']*(1-error),iou=rw['iou_weight']*loc,exploration=-rw['exploration_penalty'] if row['target_present'] and loc<rw['exploration_threshold'] and not distinct else 0.,bonus=rw['multibox_bonus_weight'] if row['target_present'] and distinct else 0.)
 c['total']=sum(c.values());return c
for row in rows:
 r=row['reward']
 if r['valid']:
  matches=re.findall(r'<answer>(.*?)</answer><score>(.*?)</score>',row['text'],re.S)
  row['_boxes']=[json.loads(b) for b,s in matches]
  assert len(matches)==r['candidate_count'] and all(float(s)==v for (b,s),v in zip(matches,r['scores']))
  assert r['correctness_labels']==([int(u>=rw['correctness_threshold']) for u in r['candidate_ious']] if row['target_present'] else [0]*r['candidate_count'])
  row['_full']=components(row)
  expected={'structure_reward':row['_full']['structure'],'score_reward':row['_full']['score']/rw['score_weight'],'iou_reward':row['_full']['iou']/rw['iou_weight'],'exploration_reward':row['_full']['exploration'],'multibox_bonus_reward':row['_full']['bonus'],'total':row['_full']['total']}
  assert all(math.isclose(r[k],v,abs_tol=1e-10) for k,v in expected.items())
 else:assert r['total']==-1.
cf=[]
for row in rows:
 r=row['reward']
 if not r['valid'] or r['candidate_count']<2:continue
 full=row['_full'];first=components(row,[0]);selected=components(row,[r['selected_index']])
 g=groups[row['_key']];index=next(i for i,x in enumerate(g) if x is row);rewards=[x['reward']['total'] for x in g]
 fvalues=rewards.copy();fvalues[index]=first['total'];svalues=rewards.copy();svalues[index]=selected['total']
 errors=[(s-y)**2 for s,y in zip(r['scores'],r['correctness_labels'])];worst=[i for i,e in enumerate(errors) if math.isclose(e,max(errors),abs_tol=1e-12)]
 rec=dict(rank=row['_rank'],update=row['step']+1,sample_id=row['sample_id'],condition=cond(row),target_present=row['target_present'],candidate_count=r['candidate_count'],first_iou=r['candidate_ious'][0] if row['target_present'] else None,selected_iou=r['selected_iou'],selected_index=r['selected_index'],distinct=r['has_distinct_pair'],order_violation=r['order_violation'],scores=r['scores'],correctness_labels=r['correctness_labels'],candidate_ious=r['candidate_ious'],worst_candidates=worst,worst_contains_added=any(i>0 for i in worst),score_error_increased_vs_first=max(errors)>errors[0]+1e-12,worst_is_wrong=any(r['correctness_labels'][i]==0 for i in worst),worst_is_correct=any(r['correctness_labels'][i]==1 for i in worst),actual_advantage=row['advantage'],first_only_hypothetical_advantage=normalize(fvalues)[index],selected_only_hypothetical_advantage=normalize(svalues)[index],full=full,first_only=first,selected_only=selected,delta_vs_first={k:full[k]-first[k] for k in full},delta_vs_selected={k:full[k]-selected[k] for k in full})
 cf.append(rec)
(OUT/'counterfactual_rows.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in cf))
def cfsum(xs):
 return dict(n=len(xs),positive=sum(x['target_present'] for x in xs),actual_positive_adv=sum(x['actual_advantage']>1e-6 for x in xs),actual_negative_adv=sum(x['actual_advantage']< -1e-6 for x in xs),error_increased_vs_first=sum(x['score_error_increased_vs_first'] for x in xs),order_violation=sum(x['order_violation'] for x in xs),worst_wrong=sum(x['worst_is_wrong'] for x in xs),worst_correct=sum(x['worst_is_correct'] for x in xs),worst_contains_added=sum(x['worst_contains_added'] for x in xs),first_only_hypothetical_positive_adv=sum(x['first_only_hypothetical_advantage']>1e-6 for x in xs),first_only_hypothetical_negative_adv=sum(x['first_only_hypothetical_advantage']< -1e-6 for x in xs),comparisons={name:dict(win=sum(x[name]['total']>1e-10 for x in xs),loss=sum(x[name]['total']< -1e-10 for x in xs),tie=sum(abs(x[name]['total'])<=1e-10 for x in xs),mean_delta={k:mean([x[name][k] for x in xs]) for k in ['structure','score','iou','exploration','bonus','total']}) for name in ['delta_vs_first','delta_vs_selected']})
grecords=[];max_adv_error=0.;sign_mismatches=0
for key,g in groups.items():
 v=[x for x in g if x['reward']['valid']];m=[x for x in v if x['reward']['candidate_count']>1];s=[x for x in v if x['reward']['candidate_count']==1]
 vals=[x['reward']['total'] for x in g];adv=normalize(vals);max_adv_error=max(max_adv_error,max(abs(a-x['advantage']) for a,x in zip(adv,g)))
 sign_mismatches+=sum((a>0)!=(x['advantage']>0) for a,x in zip(adv,g) if abs(a)>.01 and abs(x['advantage'])>.01)
 bonus=[x['reward']['multibox_bonus_reward'] or 0 for x in g];explore=[x['reward']['exploration_reward'] or 0 for x in g]
 adv_no_bonus=normalize([r-b for r,b in zip(vals,bonus)]);adv_no_explore=normalize([r-e for r,e in zip(vals,explore)])
 q=sum(a['reward']['total']>b['reward']['total'] for a in m for b in s)/(len(m)*len(s)) if m and s else None
 grecords.append(dict(rank=key[0],update=key[1]+1,sample_id=key[2],condition=cond(g[0]),valid=len(v),multi=len(m),single=len(s),invalid=4-len(v),raw_multi=sum(x['text'].count('<answer>')>=2 for x in g),mixed=bool(m and s),multi_single_win_rate=q,multi_single_mean_difference=mean([x['reward']['total'] for x in m])-mean([x['reward']['total'] for x in s]) if m and s else None,multi_positive_adv=sum(x['advantage']>1e-6 for x in m),multi_negative_adv=sum(x['advantage']< -1e-6 for x in m),all_four_single=len(s)==4,all_four_single_low_positive=len(s)==4 and g[0]['target_present'] and all(x['reward']['selected_iou']<.3 for x in g),any_low_positive=g[0]['target_present'] and any(x['reward']['valid'] and x['reward']['selected_iou']<.3 for x in g),uniform_explore=max(explore)-min(explore)<1e-12,explore_changes_in_group=max(explore)-min(explore)>.01,bonus_changes_in_group=max(bonus)-min(bonus)>.01,zero_total_variation=max(vals)-min(vals)<1e-12,bonus_turns_multi_positive=sum(x['reward']['valid'] and x['reward']['candidate_count']>1 and adv[i]>1e-6 and adv_no_bonus[i]<=1e-6 for i,x in enumerate(g)),explore_turns_multi_positive=sum(x['reward']['valid'] and x['reward']['candidate_count']>1 and adv[i]>1e-6 and adv_no_explore[i]<=1e-6 for i,x in enumerate(g)),uniform_explore_adv_max_difference=max(abs(a-b) for a,b in zip(adv,adv_no_explore)) if max(explore)-min(explore)<1e-12 else None))
assert sign_mismatches==0
(OUT/'group_rows.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in grecords))
def gsum(xs):
 mixed=[g for g in xs if g['mixed']];positive=[g for g in xs if g['condition'].endswith(':positive')];low=[g for g in positive if g['any_low_positive']]
 return dict(groups=len(xs),positive_groups=len(positive),mixed_groups=len(mixed),groups_with_valid_multi=sum(g['multi']>0 for g in xs),groups_with_raw_multi=sum(g['raw_multi']>0 for g in xs),all_four_single=sum(g['all_four_single'] for g in xs),all_four_single_low_positive=sum(g['all_four_single_low_positive'] for g in xs),positive_any_low_groups=len(low),positive_any_low_no_valid_multi=sum(g['multi']==0 for g in low),positive_any_low_uniform_explore=sum(g['uniform_explore'] for g in low),explore_changes_in_group=sum(g['explore_changes_in_group'] for g in xs),explore_changes_without_multi=sum(g['explore_changes_in_group'] and g['multi']==0 for g in xs),bonus_changes_in_group=sum(g['bonus_changes_in_group'] for g in xs),zero_total_variation=sum(g['zero_total_variation'] for g in xs),multi_positive_adv=sum(g['multi_positive_adv'] for g in xs),multi_negative_adv=sum(g['multi_negative_adv'] for g in xs),mixed_group_win_rate=mean([g['multi_single_win_rate'] for g in mixed]),mixed_mean_difference=mean([g['multi_single_mean_difference'] for g in mixed]),bonus_turns_multi_positive=sum(g['bonus_turns_multi_positive'] for g in xs),explore_turns_multi_positive=sum(g['explore_turns_multi_positive'] for g in xs))
conditions=sorted(set(x['condition'] for x in cf));positive=[x for x in cf if x['target_present']]
invalid=[r for r in rows if not r['reward']['valid']];rawmulti=[r for r in rows if r['text'].count('<answer>')>=2];invalidmulti=[r for r in rawmulti if not r['reward']['valid']]
invalid_summary=dict(invalid=len(invalid),raw_multi=len(rawmulti),invalid_raw_multi=len(invalidmulti),invalid_multi_nonterminated=sum(not r['terminated'] for r in invalidmulti),invalid_multi_at_budget=sum(r['completion_tokens']>=cfg['max_new_tokens'] for r in invalidmulti),invalid_reasons=dict(collections.Counter(r['reward']['invalid_reason'] for r in invalidmulti)),token_mean_valid_single=mean([r['completion_tokens'] for r in rows if r['reward']['valid'] and r['reward']['candidate_count']==1]),token_mean_valid_multi=mean([r['completion_tokens'] for r in rows if r['reward']['valid'] and r['reward']['candidate_count']>1]))
windows=[]
for a,b in [(1,8),(9,16),(17,25),(26,39),(40,50),(51,75)]:
 rs=[r for r in rows if a<=r['step']+1<=b];cs=[x for x in cf if a<=x['update']<=b];gs=[g for g in grecords if a<=g['update']<=b]
 windows.append(dict(start=a,end=b,rollouts=len(rs),valid_multi=len(cs),valid_multi_rate=len(cs)/len(rs),counterfactual=cfsum(cs),groups=gsum(gs),by_condition={c:dict(counterfactual=cfsum([x for x in cs if x['condition']==c]),groups=gsum([g for g in gs if g['condition']==c])) for c in sorted(set(g['condition'] for g in gs))}))
result=dict(completed_updates=cutoff,rollouts=len(rows),groups=len(groups),counterfactual_all=cfsum(cf),counterfactual_positive=cfsum(positive),counterfactual_by_condition={c:cfsum([x for x in cf if x['condition']==c]) for c in conditions},counterfactual_first_iou_bands={name:cfsum([x for x in positive if pred(x['first_iou'])]) for name,pred in [('below_03',lambda u:u<.3),('03_to_05',lambda u:.3<=u<.5),('at_least_05',lambda u:u>=.5)]},counterfactual_selected_iou_bands={name:cfsum([x for x in positive if pred(x['selected_iou'])]) for name,pred in [('below_03',lambda u:u<.3),('03_to_05',lambda u:.3<=u<.5),('at_least_05',lambda u:u>=.5)]},group_all=gsum(grecords),group_by_condition={c:gsum([g for g in grecords if g['condition']==c]) for c in sorted(set(g['condition'] for g in grecords))},invalid=invalid_summary,windows=windows,advantage_float64_max_difference=max_adv_error,advantage_sign_mismatches=sign_mismatches,uniform_explore_max_adv_difference=max(g['uniform_explore_adv_max_difference'] or 0 for g in grecords))
(OUT/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(OUT/'integrity_audit.json').write_text(json.dumps(dict(sources=sources,cutoff=75,rollouts=4800,groups=1200,g4_groups='passed',reward_components_recalculation='passed',advantage_sign_mismatches=sign_mismatches,advantage_float64_max_difference=max_adv_error,source_policy='immutable prior snapshot only; no live logs',counterfactual_policy='retain existing first/selected candidate, no GT selection or model generation'),ensure_ascii=False,indent=2)+'\n')
metrics=dict(completed_updates=75,legal_multibox=len(cf),positive_multibox=len(positive),first_only_delta_mean=result['counterfactual_positive']['comparisons']['delta_vs_first']['mean_delta']['total'],mixed_groups=result['group_all']['mixed_groups'],mixed_group_win_rate=result['group_all']['mixed_group_win_rate'],uniform_low_single_groups=result['group_all']['all_four_single_low_positive'])
(OUT/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps(metrics,ensure_ascii=False),flush=True)
