import sys,json,time,pathlib
sys.path.insert(0,'/home/zhengyuesong/Tools/survey-tool')
import surveyctl
from survey_tool import experiments as ex
from survey_tool.managed_execution import managed_execution_start,managed_execution_status,managed_execution_complete
root=surveyctl.root_for('/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext')
rid='e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis'
consumer='pi-steward:codex-e014-multibox-analysis'
command='python /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/'+rid+'/analyze.py'
ex.prepare_managed_run_command(root,rid,command,consumer)
claim=ex.claim_run_execution(root,rid,consumer)
assert claim.get('claimed'), 'no claimable analysis dispatch'
dispatch=claim['task']['dispatch']['dispatch_id']; token=claim['lease_token']
ex._leased_transition(root,dispatch,token,consumer,'acknowledge',{'actual_agent':'codex','actual_model':'','fallback_reason':'User-authorized read-only analysis executed by current Codex; exact model identifier not inferred.'})
started=managed_execution_start(root,dispatch,token,consumer)
print(json.dumps({'run_id':rid,'started':started.get('ok')},ensure_ascii=False),flush=True)
for _ in range(18):
    status=managed_execution_status(root,dispatch,token,consumer,heartbeat=True)
    print(json.dumps({k:status.get(k) for k in ('state','exit_code','completion_candidate')},ensure_ascii=False),flush=True)
    if status.get('completion_candidate') and str(status.get('exit_code'))=='0':
        try:
            result=managed_execution_complete(root,dispatch,token,consumer)
            print(json.dumps({'completed':result.get('ok'),'run':result.get('run'),'warnings':result.get('warnings')},ensure_ascii=False),flush=True)
            break
        except ValueError as e:
            if 'not yet stable' not in str(e):raise
    if status.get('exit_code') not in (None,0,'0'): raise RuntimeError('analysis execution exited '+str(status['exit_code']))
    time.sleep(3)
else: raise RuntimeError('analysis completion observation timed out')
