import json,pathlib,hashlib,collections,statistics,math
P=pathlib.Path('/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014')
T=P/'e014-boxes-then-scores-beta0-sft659-seed11451'
O=P/'analysis/e014-boxes-then-scores-collapse-analysis'
rows=[];hashes={};groups=collections.defaultdict(list)
for p in sorted((T/'payload/grpo').glob('rollouts-rank*.jsonl')):
 blob=p.read_bytes();hashes[str(p)]=hashlib.sha256(blob).hexdigest()
 for line in blob.splitlines():
  r=json.loads(line);r['rank']=p.stem;r['update']=r['step']+1;r['raw_multi']=r['text'].count('<answer>')>1
  rows.append(r);groups[(r['rank'],r['step'],r['sample_id'])].append(r)
assert len(rows)==184*64 and len(groups)==184*16
assert all(len(g)==4 for g in groups.values())
cfg=json.loads((T/'payload/trainer_config.json').read_text());assert cfg['beta']==0 and cfg['reward']['exploration_penalty']==cfg['reward']['multibox_bonus_weight']==0
err=0
for g in groups.values():
 rewards=[r['reward']['total'] for r in g];mu=statistics.mean(rewards);sd=statistics.pstdev(rewards)
 for r in g:err=max(err,abs(r['advantage']-(r['reward']['total']-mu)/(sd+1e-6)))
# Float32 normalization can magnify rounding in near-identical groups; record error.
def mean(v):return statistics.mean(v) if v else None
def subset(a):
 v=[r for r in a if r['reward']['valid']];pos=[r for r in v if r['target_present']]
 return dict(n=len(a),valid=len(v),multi=sum(r['reward']['candidate_count']>1 for r in v),raw_multi=sum(r['raw_multi'] for r in a),not_terminated=sum(not r['terminated'] for r in a),tokens=mean([r['completion_tokens'] for r in a]),reward=mean([r['reward']['total'] for r in a]),advantage=mean([r['advantage'] for r in a]),positive_advantage=sum(r['advantage']>0 for r in a),order_violations=sum(bool(r['reward']['order_violation']) for r in v),max_score_error=mean([r['reward']['max_score_error'] for r in v]),valid_pos_n=len(pos),selected_iou=mean([r['reward']['selected_iou'] for r in pos]),oracle_iou=mean([max(r['reward']['candidate_ious']) for r in pos]))
bands={}
for lo,hi in [(1,5),(6,10),(11,20),(21,50),(51,100),(101,150),(151,184)]:
 a=[r for r in rows if lo<=r['update']<=hi]
 bands[f'{lo}-{hi}']=subset(a)
classes={}
for name,fn in [('valid_single',lambda r:r['reward']['valid'] and r['reward']['candidate_count']==1),('valid_multi',lambda r:r['reward']['valid'] and r['reward']['candidate_count']>1),('invalid_raw_multi',lambda r:not r['reward']['valid'] and r['raw_multi']),('invalid_other',lambda r:not r['reward']['valid'] and not r['raw_multi'])]:classes[name]=subset([r for r in rows if fn(r)])
matched=[];matched_valid=[];rawmatched=[]
for g in groups.values():
 single=[r for r in g if r['reward']['valid'] and r['reward']['candidate_count']==1]
 multi=[r for r in g if r['reward']['valid'] and r['reward']['candidate_count']>1]
 rawmulti=[r for r in g if r['raw_multi']]
 if single and rawmulti:rawmatched.append(dict(reward_delta=mean([r['reward']['total'] for r in rawmulti])-mean([r['reward']['total'] for r in single]),raw_multi_advantage=mean([r['advantage'] for r in rawmulti])))
 if not single or not multi:continue
 row={}
 for k in ['total','structure_reward','score_reward','iou_reward']:
  row[k]=mean([r['reward'][k] for r in multi])-mean([r['reward'][k] for r in single])
 row['multi_advantage']=mean([r['advantage'] for r in multi]);row['single_advantage']=mean([r['advantage'] for r in single]);matched.append(row)
 if all(r['reward']['valid'] for r in g):matched_valid.append(row)
def aggregate(items):return dict(n=len(items),means={k:mean([r[k] for r in items]) for k in items[0]} if items else {},multi_reward_wins=sum(r.get('total',r.get('reward_delta',0))>1e-8 for r in items))
cf=[];examples=[]
for r in rows:
 w=r['reward']
 if not w['valid'] or w['candidate_count']<2:continue
 s=w['scores'];y=w['correctness_labels'];u=w['candidate_ious'];idx=w['selected_index']
 first_iou=u[0] if r['target_present'] else 0
 first_score=1-(s[0]-y[0])**2
 first_reward=1+1.1*first_score+first_iou
 selected_only=1+1.1*(1-(s[idx]-y[idx])**2)+w['iou_reward']
 row=dict(total_delta_vs_first=w['total']-first_reward,structure_delta=w['structure_reward']-1,score_delta=1.1*(w['score_reward']-first_score),iou_delta=w['iou_reward']-first_iou,selected_only_gain=selected_only-w['total'],coverage_gain=(max(u)-u[0]) if r['target_present'] else 0,selected_nonfirst=idx>0,positive=r['target_present'])
 cf.append(row)
 if len(examples)<4 and (row['total_delta_vs_first']<-.2 or row['iou_delta']>.2):examples.append(dict(update=r['update'],sample_id=r['sample_id'],text=r['text'],reward=w,advantage=r['advantage'],counterfactual=row))
cfsummary=dict(n=len(cf),means={k:mean([x[k] for x in cf]) for k in cf[0]},better_than_first=sum(x['total_delta_vs_first']>1e-8 for x in cf),worse_than_first=sum(x['total_delta_vs_first']< -1e-8 for x in cf),equal_to_first=sum(abs(x['total_delta_vs_first'])<=1e-8 for x in cf),coverage_improved=sum(x['coverage_gain']>1e-8 for x in cf),selected_iou_improved=sum(x['iou_delta']>1e-8 for x in cf),selected_only_strictly_better=sum(x['selected_only_gain']>1e-8 for x in cf))
metrics=dict(rows=len(rows),groups=len(groups),updates=184,bands=bands,classes=classes,matched_valid_single_multi=aggregate(matched),matched_all_valid_groups=aggregate(matched_valid),matched_raw_multi=aggregate(rawmatched),fixed_candidate_counterfactual=cfsummary,invalid_reasons=dict(collections.Counter(r['reward'].get('invalid_reason') for r in rows if not r['reward']['valid'])),advantage_max_recompute_error=err,by_source={s:subset([r for r in rows if r['training_source']==s]) for s in sorted(set(r['training_source'] for r in rows))})
for file,data in [('metrics.json',metrics),('source_hashes.json',hashes),('examples.json',examples)]:
 with (O/file).open('x') as f:json.dump(data,f,ensure_ascii=False,indent=2)
print(json.dumps(metrics,ensure_ascii=False))
