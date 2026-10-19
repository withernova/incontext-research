"""Audit this authorized evaluation's fixed inputs and complete predictions."""
import collections,hashlib,json,math,pathlib
RUN=pathlib.Path('/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766')
def digest(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
i=json.loads((RUN/'payload/inputs.json').read_text());m=json.loads((RUN/'metrics.json').read_text())
assert i['step']==50 and i['training_group_size']==4 and i['prompt_variant']=='multi_v2' and i['expected_samples']==1766
assert all(digest(p)==sha for p,sha in i['source_sha256'].items())
assert digest(RUN/'payload/manifest.json')==i['derived_manifest_sha256']
source_manifest=next(pathlib.Path(p) for p in i['source_sha256'] if pathlib.Path(p).name=='test_combined_lasot600_gotval_taoval_1shot_focus.json')
original=json.loads(source_manifest.read_text());derived=json.loads((RUN/'payload/manifest.json').read_text())
assert [{k:v for k,v in row.items() if k!='image_path'} for row in original]==[{k:v for k,v in row.items() if k!='image_path'} for row in derived]
cp=pathlib.Path(i['checkpoint']);assert 'beta0-sft659' in str(cp) and cp.name=='step_000050'
assert digest(cp/'adapter/policy/adapter_model.safetensors')=='d917925092923f0841ecc4cba74b7c8508bb80c95a4f17b3551a333e4fe0e18a'
train=json.loads((cp.parent.parent/'config_snapshot.json').read_text())
assert train['config']['beta']==0 and train['config']['reward_scheme']=='structure_score_selected_iou_explore_v1'
pred=RUN/'payload/evaluation/predictions.jsonl';rows=[json.loads(s) for s in pred.read_text().splitlines()]
assert len(rows)==1766 and len({r['id'] for r in rows})==1766 and [r['dataset_index'] for r in rows]==list(range(1766))
ranks=collections.Counter(r['rank'] for r in rows)
assert dict(ranks)=={rank:(221 if rank<6 else 220) for rank in range(8)}
assert m['checkpoint']==str(cp) and m['world_size']==8 and m['evaluated_samples']==1766
snap=list((RUN/'payload/logs/config_snapshots').glob('evaluate-*'));assert len(snap)==1
resolved=json.loads((snap[0]/'resolved.json').read_text());e=resolved['evaluation']
assert e['seed']==20260901 and e['max_new_tokens']==192 and e['do_sample'] is False and e['vision_max_patch_tokens']==4096
assert resolved['test_dataloader']['dataset']['prompt_variant']=='multi_v2'
example=json.loads((snap[0]/'prompt_example.json').read_text());prompt=example['messages'][0]['content'][0]['text']
assert hashlib.sha256(prompt.encode()).hexdigest()==i['prompt_sha256']
valid=[r for r in rows if r['variable_candidate_format_valid']];multi=[r for r in valid if r['candidate_count']>1];invalid=[r for r in rows if not r['variable_candidate_format_valid']]
for r in valid:
 cs=r['candidates'];k=max(range(len(cs)),key=lambda j:cs[j]['score']);assert k==r['selected_candidate_index'] and abs(cs[k]['iou']-r['iou'])<1e-12
selected=sum(r['iou'] for r in rows)/1766;first=sum(r['first_candidate_iou'] for r in rows)/1766;oracle=sum(r['oracle_iou'] for r in rows)/1766
assert math.isclose(selected,m['miou'],abs_tol=1e-12) and math.isclose(first,m['first_candidate_miou'],abs_tol=1e-12) and math.isclose(oracle,m['oracle_miou'],abs_tol=1e-12)
chosen=[r for r in valid if r['selected_candidate_index']!=0]
result=dict(run_id=RUN.name,complete=True,samples=1766,source_hashes_verified=len(i['source_sha256']),checkpoint_policy_sha256=digest(cp/'adapter/policy/adapter_model.safetensors'),predictions_sha256=digest(pred),valid_count=len(valid),invalid_count=len(invalid),valid_multibox_count=len(multi),valid_multibox_rate=len(multi)/1766,raw_multibox_attempt_count=sum(r['raw_prediction'].count('<answer>')>=2 for r in rows),candidate_count_histogram=dict(collections.Counter(str(r['candidate_count']) for r in rows)),first_miou=first,selected_miou=selected,oracle_miou=oracle,selected_iou_ge05_count=sum(r['iou']>=.5 for r in rows),selected_iou_ge075_count=sum(r['iou']>=.75 for r in rows),first_iou_ge05_count=sum(r['first_candidate_iou']>=.5 for r in rows),oracle_iou_ge05_count=sum(r['oracle_iou']>=.5 for r in rows),selected_nonfirst_count=len(chosen),nonfirst_improves_first=sum(r['iou']>r['first_candidate_iou']+1e-9 for r in chosen),nonfirst_worsens_first=sum(r['iou']<r['first_candidate_iou']-1e-9 for r in chosen),rank_counts=dict(collections.Counter(str(r.get('rank')) for r in rows)),dataset_counts=dict(collections.Counter(r['dataset'] for r in rows)),manifest_only_image_path_changed=True,limitations='Single checkpoint exploratory evaluation on previously viewed cohort; no matched step50 beta.04 baseline, no Claim promotion.')
result['audit_script_sha256']=digest(pathlib.Path(__file__))
with (RUN/'evaluation_audit.json').open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(result,ensure_ascii=False),flush=True)
