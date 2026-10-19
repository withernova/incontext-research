import sys,json,shlex
sys.path.insert(0,'/home/zhengyuesong/Tools/survey-tool')
import surveyctl
from survey_tool import experiments as ex
from survey_tool.managed_execution import managed_execution_start,managed_execution_status
root=surveyctl.root_for('/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext');rid='e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451'
command=shlex.join(['bash','tools/run.sh','configs/experiments/E-014/training/e014_structure_score_iou_explore_multibox_bonus_grpo.py','settings.trainer.reward.multibox_bonus_weight=0.5','output.run_name='+rid])
consumer='pi-steward:codex-e014-bonus05-training'
ex.prepare_managed_run_command(root,rid,command,consumer)
claim=ex.claim_run_execution(root,rid,consumer);assert claim.get('claimed')
dispatch=claim['task']['dispatch']['dispatch_id'];token=claim['lease_token']
ex._leased_transition(root,dispatch,token,consumer,'acknowledge',{'actual_agent':'codex','actual_model':'','fallback_reason':'Explicit user startup request handled by current Codex; exact model identifier not inferred.'})
r=managed_execution_start(root,dispatch,token,consumer)
print(json.dumps({'run_id':rid,'started':r.get('ok'),'health_check':'startup only'},ensure_ascii=False),flush=True)
s=managed_execution_status(root,dispatch,token,consumer,heartbeat=True)
print(json.dumps({k:s.get(k) for k in ['run_id','state','exit_code','completion_candidate']},ensure_ascii=False),flush=True)
