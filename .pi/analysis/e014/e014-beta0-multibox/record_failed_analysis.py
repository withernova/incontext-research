import sys,json
sys.path.insert(0,'/home/zhengyuesong/Tools/survey-tool')
import surveyctl
from survey_tool import experiments as ex
from survey_tool.managed_execution import managed_execution_status,managed_execution_fail
root=surveyctl.root_for('/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext');rid='e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis'
r=next(r for r in ex.experiment_data(root)['runs'] if r['id']==rid)
# The owned execution adapter exited after observing code 1; recover its in-memory authority only.
ex.force_expire_managed_steward_lease(root,rid,r['updated'],actor='codex:owned-analysis-executor-exited')
d=next(x for x in reversed(ex.execution_outbox_public(root)['execution_outbox']['items']) if x.get('run_id')==rid and x.get('status')=='running')
consumer='pi-steward:codex-record-failed-readonly-analysis';claim=ex.reattach_managed_execution(root,d['dispatch_id'],consumer)
s=managed_execution_status(root,d['dispatch_id'],claim['lease_token'],consumer,heartbeat=True)
assert str(s['exit_code'])=='1'
v=managed_execution_fail(root,d['dispatch_id'],claim['lease_token'],consumer,'implementation','只读分析脚本min(completed.values(),150)类型错误，尚未形成统计结果；原目录与日志保留，无训练或模型执行失败。',False)
print(json.dumps({'recorded_analysis_failure':v.get('ok'),'training_untouched':True}))
