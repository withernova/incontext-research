"""One-off read-only snapshot analysis of the explicitly referenced parent Run."""
import collections, hashlib, json, math, pathlib, re, sys, time
PARENT=pathlib.Path('/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-sft659-seed11451/payload')
OUT=pathlib.Path('/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis')
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
assert cutoff>0
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
(OUT/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(OUT/'integrity_audit.json').write_text(json.dumps(dict(sources=AUDIT,completed_updates=cutoff,rollout_count=len(rows),groups=len(groups),reward_record_checks='passed',scope='training on-policy observational diagnostic; no causal or heldout evaluation conclusion'),indent=2)+'\n')
metrics={'completed_updates':cutoff,'rollouts':len(rows),'valid_multibox_count':result['overall']['multi_count'],'valid_multibox_rate':result['overall']['multi_rate_valid']}
for c,item in result['within_same_prompt'].items():
    for k,v in item.items(): metrics[c.replace(':','_')+'.'+k]=v
(OUT/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps({'cutoff':cutoff,'overall':result['overall'],'within_same_prompt':result['within_same_prompt']},ensure_ascii=False),flush=True)
