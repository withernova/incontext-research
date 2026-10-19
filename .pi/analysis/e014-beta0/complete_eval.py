import sys,json,time
sys.path.insert(0,'/home/zhengyuesong/Tools/survey-tool')
import surveyctl
from survey_tool import experiments as ex
from survey_tool.managed_execution import managed_execution_status,managed_execution_complete
root=surveyctl.root_for('/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext')
rid='e014-structure-score-iou-explore-v1-step150-eval1766'
item=next(x for x in reversed(ex.execution_outbox_public(root)['execution_outbox']['items']) if x.get('run_id')==rid and x.get('status')=='running')
consumer='pi-steward:codex-e014-complete-step150-eval'
claim=ex.reattach_managed_execution(root,item['dispatch_id'],consumer);token=claim['lease_token'];dispatch=item['dispatch_id']
s=managed_execution_status(root,dispatch,token,consumer,heartbeat=True)
print(json.dumps({k:s.get(k) for k in ['state','exit_code','completion_candidate']}),flush=True)
for _ in range(3):
 try:
  r=managed_execution_complete(root,dispatch,token,consumer)
  print(json.dumps({'completed':r.get('ok'),'run':r.get('run')},ensure_ascii=False),flush=True);break
 except ValueError as e:
  if 'not yet stable' not in str(e):raise
  time.sleep(2)
else:raise RuntimeError('metrics did not reach stable observation')
