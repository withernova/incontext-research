"""One-off read-only snapshot analysis of the explicitly referenced parent Run."""
import collections, hashlib, json, math, pathlib, re, sys, time
PARENT=pathlib.Path('/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-sft659-seed11451/payload')
OUT=pathlib.Path('/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis')
OUT.mkdir(exist_ok=True)
SOURCES=OUT/'source_snapshot'; SOURCES.mkdir(exist_ok=False)
AUDIT=[]
def snapshot(path):
    size=path.stat().st_size
    with path.open('rb') as f: data=f.read(size)
    dest=SOURCES/path.name
    dest.write_bytes(data)
    AUDIT.append(dict(source=str(path),size=len(data),sha256=hashlib.sha256(data).hexdigest(),snapshot=str(dest)))
    return data
config=json.loads(snapshot(PARENT/'trainer_config.json'))
assert config['reward_scheme']=='structure_score_selected_iou_explore_v1'
assert config['group_size']==4
assert set(config['reward'])=={'correctness_threshold','exploration_threshold','distinct_threshold','score_weight','iou_weight','order_penalty','exploration_penalty'}
completed=collections.defaultdict(set)
for match in re.finditer(rb'\{"rank":\s*\d+,\s*"step":\s*\d+,[^{}\n]*\}', snapshot(PARENT/'training.log')):
    try: item=json.loads(match[0])
    except (ValueError,UnicodeDecodeError): continue
    if isinstance(item,dict) and {'rank','step','gradient_norm'}<=item.keys(): completed[item['rank']].add(item['step'])
assert set(completed)==set(range(8)), 'missing rank completion records'
cutoff=0
while all(cutoff+1 in completed[rank] for rank in range(8)): cutoff+=1
assert cutoff>=150
cutoff=150
rows=[]; excluded=0; unfinished=0
for path in sorted((PARENT/'grpo').glob('rollouts-rank*.jsonl')):
    rank=int(re.search(r'rank(\d+)',path.name)[1])
    data=snapshot(path)
    for line in data.splitlines(keepends=True):
        if not line.endswith(b'\n'): unfinished+=1; continue
        item=json.loads(line); step=item['step']
        if step>=cutoff: excluded+=1; continue
        assert 0<=step<cutoff
        rew=item['reward']; assert rew['reward_scheme']==config['reward_scheme']
        assert rew['target_present']==item['target_present']
        if rew['valid']:
            n=rew['candidate_count']; scores=rew['scores']; overlaps=rew['candidate_ious']
            assert n==len(scores)==len(rew['correctness_labels'])
            assert rew['selected_index']==max(range(n),key=lambda j:scores[j])
            if item['target_present']:
                assert n==len(overlaps)
                assert rew['correctness_labels']==[int(u>=.5) for u in overlaps]
                assert math.isclose(rew['selected_iou'],overlaps[rew['selected_index']],abs_tol=1e-12)
            else: assert overlaps is None and rew['selected_iou'] is None
            error=max((s-y)**2 for s,y in zip(scores,rew['correctness_labels']))
            total=1-.12*rew['order_violation']+1.1*(1-error)+(rew['selected_iou'] if item['target_present'] else 0)
            exp=-.2 if item['target_present'] and rew['selected_iou']<.3 and not rew['has_distinct_pair'] else 0
            assert math.isclose(rew['exploration_reward'],exp,abs_tol=1e-12)
            assert math.isclose(rew['total'],total+exp,abs_tol=1e-10)
        else: assert rew['total']==-1
        item['_rank']=rank; rows.append(item)
assert len(rows)==cutoff*8*2*4,(len(rows),cutoff)
groups=collections.defaultdict(list)
for row in rows: groups[(row['_rank'],row['step'],row['sample_id'])].append(row)
assert all(len(g)==4 for g in groups.values())
assert len(groups)==cutoff*8*2

def avg(values): return sum(values)/len(values) if values else None
def condition(row): return row.get('training_source','original')+(':positive' if row['target_present'] else ':negative')
def summary(rs):
    valid=[r for r in rs if r['reward']['valid']]
    single=[r for r in valid if r['reward']['candidate_count']==1]
    multi=[r for r in valid if r['reward']['candidate_count']>1]
    def measure(sub):
        pos=[r['reward'] for r in sub if r['target_present']]
        result=dict(count=len(sub),positive_count=len(pos),selected_miou=avg([r['selected_iou'] for r in pos]),
            first_miou=avg([r['candidate_ious'][0] for r in pos]),oracle_miou=avg([max(r['candidate_ious']) for r in pos]),
            selected_success_05=avg([r['selected_iou']>=.5 for r in pos]),
            selected_success_075=avg([r['selected_iou']>=.75 for r in pos]),oracle_success_05=avg([max(r['candidate_ious'])>=.5 for r in pos]))
        if pos:
            better=[r for r in pos if max(r['candidate_ious'])>r['candidate_ious'][0]+1e-9]
            chosen=[r for r in pos if r['selected_index']!=0]
            result.update(later_better_than_first=len(better),nonfirst_selected=len(chosen),
                selected_improves_first=sum(r['selected_iou']>r['candidate_ious'][0]+1e-9 for r in pos),
                selected_worsens_first=sum(r['selected_iou']<r['candidate_ious'][0]-1e-9 for r in pos),
                selected_hits_oracle=sum(abs(r['selected_iou']-max(r['candidate_ious']))<1e-9 for r in pos),
                later_better_selected_improves=sum(r['selected_iou']>r['candidate_ious'][0]+1e-9 for r in better),
                oracle_rescues_first05=sum(r['candidate_ious'][0]<.5 and max(r['candidate_ious'])>=.5 for r in pos),
                selected_rescues_first05=sum(r['candidate_ious'][0]<.5 and r['selected_iou']>=.5 for r in pos),
                selected_loses_first05=sum(r['candidate_ious'][0]>=.5 and r['selected_iou']<.5 for r in pos))
        return result
    low=[r for r in valid if r['target_present'] and r['reward']['selected_iou']<.3]
    return dict(reward_mean=avg([r['reward']['total'] for r in rs]),score_error_max_mean=avg([r['reward']['max_score_error'] for r in valid]),selected_score_mean=avg([r['reward']['score'] for r in valid]),exploration_penalty_count=sum(r['reward'].get('exploration_reward') == -.2 for r in valid),order_violation_count=sum(bool(r['reward']['order_violation']) for r in valid),zero_advantage_rate=avg([r['advantage']==0 for r in rs]),rollouts=len(rs),valid=len(valid),invalid=len(rs)-len(valid),multi_count=len(multi),
                multi_rate_all=len(multi)/len(rs) if rs else None,multi_rate_valid=len(multi)/len(valid) if valid else None,
                single=measure(single),multi=measure(multi),low_iou_positive=len(low),
                low_iou_distinct=sum(r['reward']['has_distinct_pair'] for r in low))

def paired(gs):
    by=collections.defaultdict(list)
    for g in gs:
        valid=[r for r in g if r['reward']['valid']]
        a=[r for r in valid if r['reward']['candidate_count']==1]
        b=[r for r in valid if r['reward']['candidate_count']>1]
        if not a or not b or not g[0]['target_present']: continue
        av=[r['reward']['selected_iou'] for r in a]; bv=[r['reward']['selected_iou'] for r in b]
        bo=[max(r['reward']['candidate_ious']) for r in b]
        item=dict(selected_diff=avg(bv)-avg(av),oracle_diff=avg(bo)-avg(av),
            success05_diff=avg([v>=.5 for v in bv])-avg([v>=.5 for v in av]),
            selected_pair_wins=avg([y>x+1e-9 for x in av for y in bv]),selected_pair_ties=avg([abs(y-x)<=1e-9 for x in av for y in bv]))
        by[condition(g[0])].append(item); by['all_positive'].append(item)
    return {c:dict(mixed_prompt_groups=len(items),**{k:avg([v[k] for v in items]) for k in items[0]}) for c,items in by.items()}
conditions=sorted(set(condition(r) for r in rows))
result=dict(parent_run=PARENT.parent.name,analysis_run=OUT.name,cutoff_completed_update=cutoff,
    last_reported_by_rank={str(k):max(v) for k,v in completed.items()},rollout_step_convention='zero based: 0..cutoff-1 included',
    excluded_pending_rows=excluded,trailing_partial_lines=unfinished,group_size=4,
    overall=summary(rows),by_condition={c:summary([r for r in rows if condition(r)==c]) for c in conditions},
    within_same_prompt=paired(groups.values()),windows=[])
for start in range(0,cutoff,50):
    sub=[r for r in rows if start<=r['step']<min(cutoff,start+50)]
    result['windows'].append(dict(update_start=start+1,update_end=min(cutoff,start+50),overall=summary(sub),by_condition={c:summary([r for r in sub if condition(r)==c]) for c in conditions}))
latest=max((PARENT/'grpo/checkpoints').glob('step_*'),default=None)
result['latest_checkpoint'] = dict(path=str(latest),files={str(p.relative_to(latest)):p.stat().st_size for p in latest.rglob('*') if p.is_file()}) if latest else None

(OUT/'integrity_audit.json').write_text(json.dumps(dict(sources=AUDIT,completed_updates=cutoff,rollout_count=len(rows),groups=len(groups),reward_record_checks='passed',scope='training on-policy observational diagnostic; no causal or heldout evaluation conclusion'),indent=2)+'\n')
metrics={'completed_updates':cutoff,'rollouts':len(rows),'valid_multibox_count':result['overall']['multi_count'],'valid_multibox_rate':result['overall']['multi_rate_valid']}
for c,item in result['within_same_prompt'].items():
    for k,v in item.items(): metrics[c.replace(':','_')+'.'+k]=v
(OUT/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')



def describe(sub):
    vals=[r['advantage'] for r in sub]
    return dict(n=len(sub),positive_advantages=sum(v>1e-6 for v in vals),negative_advantages=sum(v< -1e-6 for v in vals),zero_advantages=sum(abs(v)<=1e-6 for v in vals),mean_advantage=avg(vals),mean_tokens=avg([r['completion_tokens'] for r in sub]),mean_reward=avg([r['reward']['total'] for r in sub]))

def raw_multi(r):return r['text'].count('<answer>')>=2

def valid_multi(r):return r['reward']['valid'] and r['reward']['candidate_count']>1
positive=[r for r in rows if r['target_present']]
vm=[r for r in rows if valid_multi(r)]
raw=[r for r in rows if raw_multi(r)]
invalid=[r for r in rows if not r['reward']['valid']]
raw_invalid=[r for r in invalid if raw_multi(r)]
explore_groups=collections.Counter()
diffs=collections.defaultdict(list)
strengths={str(w):dict(positive=0,negative=0,zero=0,multibox_samples=0) for w in [.2,.4,.6,1.]}
for g in groups.values():
    if g[0]['target_present']:
        explore_groups['positive_groups']+=1
        valid=[r for r in g if r['reward']['valid']]
        low=[r for r in valid if r['reward']['selected_iou']<.3]
        explore_groups['groups_with_any_low_iou']+=bool(low)
        explore_groups['all_four_valid_and_low_iou']+=len(low)==4
        explores=[r['reward']['exploration_reward'] for r in valid]
        explore_groups['groups_with_exploration_component_difference']+=len(set(explores))>1
        explore_groups['groups_with_low_iou_but_no_valid_multibox']+=bool(low) and not any(valid_multi(r) for r in g)
        explore_groups['groups_with_uniform_penalty_four']+=len(explores)==4 and all(v==-.2 for v in explores)
    single=[r for r in g if r['reward']['valid'] and r['reward']['candidate_count']==1]
    multi=[r for r in g if valid_multi(r)]
    if g[0]['target_present'] and multi:
        for key,stats in strengths.items():
            weight=float(key)
            rewards=[r['reward']['total']-(weight-.2)*int(r['reward'].get('exploration_reward')==-.2) for r in g]
            mean=avg(rewards)
            for r,v in zip(g,rewards):
                if not valid_multi(r):continue
                stats['multibox_samples']+=1
                stats['positive']+=v>mean+1e-6;stats['negative']+=v<mean-1e-6;stats['zero']+=abs(v-mean)<=1e-6
    if single and multi and g[0]['target_present']:
        item={k:avg([r['reward'][k] for r in multi])-avg([r['reward'][k] for r in single]) for k in ['structure_reward','score_reward','iou_reward','exploration_reward','total']}
        item['weighted_score_diff']=1.1*item['score_reward']
        diffs['all_positive'].append(item);diffs[condition(g[0])].append(item)
        if all(r['reward']['selected_iou']<.3 for r in single+multi):diffs['both_single_multi_low_iou'].append(item)
first_only=[]
for row in vm:
    if not row['target_present']:continue
    r=row['reward'];s=r['scores'][0];u=r['candidate_ious'][0];y=int(u>=.5)
    first_reward=1+1.1*(1-(s-y)**2)+u-(.2 if u<.3 else 0)
    first_only.append(dict(delta=r['total']-first_reward,
        score_contribution=1.1*((1-r['max_score_error'])-(1-(s-y)**2)),
        iou_contribution=r['selected_iou']-u,
        structure_contribution=r['structure_reward']-1,
        exploration_contribution=r['exploration_reward']-(-.2 if u<.3 else 0)))
counts={c:describe([r for r in vm if condition(r)==c]) for c in conditions}
diagnostic=dict(
    raw_multi=describe(raw),valid_multi=describe(vm),by_condition_valid_multi=counts,
    valid_single=describe([r for r in rows if r['reward']['valid'] and not valid_multi(r)]),
    invalid_raw_multi=describe(raw_invalid),invalid_count=len(invalid),
    raw_multi_invalid_count=len(raw_invalid),raw_multi_invalid_not_terminated=sum(not r['terminated'] for r in raw_invalid),
    raw_multi_invalid_at_token_budget=sum(r['completion_tokens']>=config['max_new_tokens'] for r in raw_invalid),
    invalid_reason_counts=dict(collections.Counter(r['reward'].get('invalid_reason') for r in invalid)),
    valid_multi_max_update=max((r['step']+1 for r in vm),default=None),
    raw_multi_max_update=max((r['step']+1 for r in raw),default=None),
    multibox_per10=[dict(start=start+1,end=min(start+10,cutoff),valid_multi=sum(valid_multi(r) for r in rows if start<=r['step']<min(start+10,cutoff)),raw_multi=sum(raw_multi(r) for r in rows if start<=r['step']<min(start+10,cutoff))) for start in range(0,cutoff,10)],
    exploration_group_counts=dict(explore_groups),
    mixed_group_reward_differences={c:dict(groups=len(v),**{k:avg([r[k] for r in v]) for k in v[0]}) for c,v in diffs.items()},
    penalty_strength_rescoring_existing_samples=strengths,
    multibox_vs_its_first_only=dict(n=len(first_only),mean_delta=avg([r['delta'] for r in first_only]),wins=sum(r['delta']>1e-9 for r in first_only),losses=sum(r['delta']< -1e-9 for r in first_only),ties=sum(abs(r['delta'])<=1e-9 for r in first_only),**{k:avg([r[k] for r in first_only]) for k in ['score_contribution','iou_contribution','structure_contribution','exploration_contribution']}),
    limitations='Reward re-scoring only on existing samples; no causal estimate or prediction of changed-policy sampling. KL and EOS continuation probabilities were not logged separately.')
result['collapse_diagnostic']=diagnostic
(OUT/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
metrics.update(valid_multibox_count=len(vm),raw_multibox_count=len(raw),raw_multibox_invalid_count=len(raw_invalid),valid_multibox_last_update=diagnostic['valid_multi_max_update'],exploration_mixed_groups=explore_groups['groups_with_exploration_component_difference'])
(OUT/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps({'cutoff':cutoff,'diagnostic':diagnostic},ensure_ascii=False),flush=True)
