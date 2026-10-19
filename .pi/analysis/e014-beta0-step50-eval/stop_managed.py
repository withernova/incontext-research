import sys,json
sys.path.insert(0,'/home/zhengyuesong/Tools/survey-tool')
import surveyctl
from survey_tool import experiments as ex
from survey_tool.managed_execution import managed_execution_fail
root=surveyctl.root_for('/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext')
rid='e014-structure-score-iou-explore-v1-beta0-sft659-seed11451'
items=ex.execution_outbox_public(root)['execution_outbox']['items']
item=next(x for x in reversed(items) if x.get('run_id')==rid and x.get('status')=='running')
consumer='pi-steward:codex-e014-user-stop'
claim=ex.reattach_managed_execution(root,item['dispatch_id'],consumer)
r=managed_execution_fail(root,item['dispatch_id'],claim['lease_token'],consumer,'authorization','用户明确要求现在停止训练，并评测本Run保存的step50；主动停止，不是1500步训练完成，不自动恢复。',False)
print(json.dumps({'recorded_user_stop':r.get('ok'),'run_id':rid},ensure_ascii=False))
