import sys,json,pathlib,subprocess,hashlib,time
sys.path.insert(0,'/home/zhengyuesong/Tools/survey-tool')
import surveyctl
from survey_tool import experiments as ex
from survey_tool.managed_execution import managed_execution_status,managed_execution_complete
root=surveyctl.root_for('.')
rid='e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2'
remote=r'''
from pathlib import Path
from collections import Counter
import json,hashlib
r=Path('/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2')
m=r/'execution/metrics.json';p=r/'execution/payload/evaluation/predictions.jsonl'
a=json.loads(m.read_text());rows=[json.loads(x) for x in p.read_text().splitlines() if x.strip()]
assert a['status']=='completed' and len(rows)==a['evaluated_samples']==1766
assert len({x['dataset_index'] for x in rows})==1766 and {x['dataset_index'] for x in rows}==set(range(1766))
assert len({x['id'] for x in rows})==1766
assert (r/'.survey-tool-exit-code').read_text().strip()=='0'
assert (r/'.survey-tool-complete').is_file()
log=r/'managed_console.log'
assert any('E014_EVALUATION_COMPLETE samples=1766 world_size=8' in x for x in log.read_text().splitlines())
for k in ['iou','first_candidate_iou','oracle_iou']:
    v=sum(float(x.get(k) or 0) for x in rows)/1766
    expected={'iou':'miou','first_candidate_iou':'first_candidate_miou','oracle_iou':'oracle_miou'}[k]
    assert abs(v-a[expected])<1e-10,(k,v,a[expected])
second=[x['candidates'][1] for x in rows if len(x.get('candidates') or [])>=2]
summary={'predictions_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'metrics_sha256':hashlib.sha256(m.read_bytes()).hexdigest(),'samples':len(rows),'unique_indices_and_ids':True,'all_sample_metrics_recomputed':True,'postflight_complete_log_marker':True,'exit_code':0,'second_candidate_count':len(second),'second_candidate_mean_iou':sum(float(x.get('iou') or 0) for x in second)/len(second),'second_candidate_correct_count':sum(float(x.get('iou') or 0)>=.5 for x in second),'second_candidate_mean_score':sum(float(x.get('score') or 0) for x in second)/len(second),'second_candidate_zero_score_count':sum(x.get('score')==0 for x in second),'second_improves_iou_count':sum(float(x.get('oracle_iou') or 0)>float(x.get('first_candidate_iou') or 0)+1e-12 for x in rows),'second_rescues_first_at_05_count':sum(float(x.get('first_candidate_iou') or 0)<.5 and float(x.get('oracle_iou') or 0)>=.5 for x in rows),'selection_misses_available_correct_at_05_count':sum(float(x.get('iou') or 0)<.5 and float(x.get('oracle_iou') or 0)>=.5 for x in rows),'selected_second_count':sum(x.get('selected_candidate_index')==1 for x in rows),'most_frequent_second_boxes':[{'box':list(b),'count':n} for b,n in Counter(tuple(x['box']) for x in second).most_common(3)]}
print(json.dumps({'metrics':a,'audit':summary},ensure_ascii=False))
'''
res=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ClearAllForwardings=yes','SZY-3090','python3 -'],input=remote,text=True,capture_output=True)
if res.returncode:print(res.stderr[-2000:]);raise SystemExit(res.returncode)
payload=json.loads(res.stdout);folder=pathlib.Path('.pi/analysis/e014/e014-bonus05-step350-eval-r2')
for name,value in [('final_metrics.json',payload['metrics']),('final_integrity_audit.json',payload['audit'])]:
    with (folder/name).open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
r=next(r for r in ex.experiment_data(root)['runs'] if r['id']==rid)
consumer='pi-steward:codex-e014-step350-evaluation-completion'
if r['status']=='running':
    try:reattached=ex.reattach_managed_execution(root,r['execution_dispatch_id'],consumer)
    except ValueError as e:
        if '尚未过期' not in str(e):raise
        ex.force_expire_managed_steward_lease(root,rid,r['updated'],actor='codex:original-start-controller-exited-evaluation-now-complete')
        reattached=ex.reattach_managed_execution(root,r['execution_dispatch_id'],consumer)
    token=reattached['lease_token'];dispatch=reattached['dispatch']['dispatch_id']
    s=managed_execution_status(root,dispatch,token,consumer,heartbeat=True)
    assert s['completion_candidate'] and s['exit_code']=='0'
    try:done=managed_execution_complete(root,dispatch,token,consumer)
    except ValueError as e:
        if 'not yet stable' not in str(e):raise
        time.sleep(2)
        done=managed_execution_complete(root,dispatch,token,consumer)
    assert done['ok'],done.get('error_class')
    print(json.dumps({'managed_complete':True,'run_id':rid,'claim_modified':False},ensure_ascii=False))
print(json.dumps(payload['audit'],ensure_ascii=False,indent=2))
