import sys,json,shlex
sys.path.insert(0,'/home/zhengyuesong/Tools/survey-tool')
import surveyctl
from survey_tool import experiments as ex
from survey_tool.managed_execution import managed_execution_start,managed_execution_status
root=surveyctl.root_for('/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext')
rid='e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2'
command='env E014_EVAL_PROFILE=explicit_binding E014_EVAL_RUN=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution E014_EVAL_CHECKPOINT=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451/payload/grpo/checkpoints/step_000350 E014_EVAL_CONFIG=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/config/evaluation_config.py E014_EVAL_VARIANT=multi_v2 E014_EVAL_STEP=350 E014_EVAL_PROMPT_SHA=c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba bash tools/run/eval/e014/e014_step800_eval1766_8gpu.sh'
ex.update_run(root,rid,dict(seed='20260901',git_commit='7bb09c762b4e6030fe870b34f9c1a119d7c81425'))
consumer='pi-steward:codex-e014-bonus05-step350-evaluation-r2'
ex.prepare_managed_run_command(root,rid,command,consumer)
claim=ex.claim_run_execution(root,rid,consumer);assert claim.get('claimed')
dispatch=claim['task']['dispatch']['dispatch_id'];token=claim['lease_token']
ex._leased_transition(root,dispatch,token,consumer,'acknowledge',{'actual_agent':'codex','actual_model':'','fallback_reason':'Current explicit user evaluation task; exact model identifier not inferred.'})
r=managed_execution_start(root,dispatch,token,consumer)
print(json.dumps({'run_id':rid,'started':r.get('ok')},ensure_ascii=False),flush=True)
s=managed_execution_status(root,dispatch,token,consumer,heartbeat=True)
print(json.dumps({k:s.get(k) for k in ['run_id','state','exit_code','completion_candidate']},ensure_ascii=False),flush=True)
