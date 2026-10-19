import sys,json,shlex
sys.path.insert(0,'/home/zhengyuesong/Tools/survey-tool')
import surveyctl
from survey_tool import experiments as ex
from survey_tool.managed_execution import managed_execution_start,managed_execution_status
root=surveyctl.root_for('/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext')
rid='e014-structure-score-iou-explore-v1-step150-eval1766'
remote='/defaultShare/archive/songzhengyue/projects/IPLoc'
run=remote+'/experiments/E-014/'+rid
cp=remote+'/experiments/E-014/e014-structure-score-iou-explore-v1-sft659-seed11451/payload/grpo/checkpoints/step_000150'
config='configs/experiments/E-014/evaluation/e014_structure_score_iou_explore_step150_eval1766.py'
command=shlex.join(['env','E014_EVAL_PROFILE=explicit_binding','E014_EVAL_RUN='+run,'E014_EVAL_CHECKPOINT='+cp,'E014_EVAL_CONFIG='+config,'E014_EVAL_VARIANT=multi_v2','E014_EVAL_STEP=150','E014_EVAL_PROMPT_SHA=c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba','bash','tools/run/eval/e014/e014_step800_eval1766_8gpu.sh'])
fields=dict(config=config,git_commit='f394b5704a9a258f4863e0d525ca5ca0a2bdec3b',seed='20260901',output_dir=run+'/outputs',log_path=run+'/managed_console.log',
 implementation_details='父训练按用户要求停止，8rank最后154；只评测保存step150。训练SHA1e2caec81668dafaf015005415d219b4e5e4ca2e，scheme structure_score_selected_iou_explore_v1/G4；policy SHA256=2d6b64aec234746230d820e7a4b112f4d23788b036485312a8ba7b2435b24379，读期间stat稳定。新薄配置预期7项新reward/G4/step150，复用现有explicit_binding Shell/tools.evaluate。原1766清单SHA48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b，只迁移image_path至只读alias；8GPU/multi_v2/greedy192/vision4096/eval seed20260901。评测代码指定部署SHAf394b5704a9a258f4863e0d525ca5ca0a2bdec3b，review295cedf073227cf9通过，AST/navigation/diff静态核验通过，未测试；现有必要执行preflight校验optimizer.steps150、GPU空闲、source hashes与prompt。不恢复训练、不覆盖产物，不自动重跑。')
ex.update_run(root,rid,fields)
consumer='pi-steward:codex-e014-newreward-step150-eval'
ex.prepare_managed_run_command(root,rid,command,consumer)
claim=ex.claim_run_execution(root,rid,consumer);assert claim.get('claimed')
dispatch=claim['task']['dispatch']['dispatch_id'];token=claim['lease_token']
ex._leased_transition(root,dispatch,token,consumer,'acknowledge',{'actual_agent':'codex','actual_model':'','fallback_reason':'Current user explicitly requested evaluation by current Codex; exact model identifier not inferred.'})
result=managed_execution_start(root,dispatch,token,consumer)
print(json.dumps({'run_id':rid,'started':result.get('ok'),'managed':result.get('managed')},ensure_ascii=False),flush=True)
status=managed_execution_status(root,dispatch,token,consumer,heartbeat=True)
print(json.dumps({k:status.get(k) for k in ('run_id','state','exit_code','completion_candidate')},ensure_ascii=False),flush=True)
