import sys,json,shlex,time,subprocess,pathlib
sys.path.insert(0,'/home/zhengyuesong/Tools/survey-tool')
import surveyctl
from survey_tool import experiments as ex
from survey_tool.managed_execution import managed_execution_start,managed_execution_status,managed_execution_complete
root=surveyctl.root_for('/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext')
rid='e014-structure-score-iou-explore-v1-beta0-step50-eval1766';remote='/defaultShare/archive/songzhengyue/projects/IPLoc';run=remote+'/experiments/E-014/'+rid
cp=remote+'/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-sft659-seed11451/payload/grpo/checkpoints/step_000050'
config='configs/experiments/E-014/evaluation/e014_structure_score_iou_explore_beta0_step50_eval1766.py'
command=shlex.join(['env','E014_EVAL_PROFILE=explicit_binding','E014_EVAL_RUN='+run,'E014_EVAL_CHECKPOINT='+cp,'E014_EVAL_CONFIG='+config,'E014_EVAL_VARIANT=multi_v2','E014_EVAL_STEP=50','E014_EVAL_PROMPT_SHA=c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba','bash','tools/run/eval/e014/e014_step800_eval1766_8gpu.sh'])
ex.update_run(root,rid,dict(seed='20260901',git_commit='599ed6809ba7b9fd36dde7e354605e56d306fbb5'))
consumer='pi-steward:codex-e014-beta0-step50-evaluation'
ex.prepare_managed_run_command(root,rid,command,consumer)
claim=ex.claim_run_execution(root,rid,consumer);assert claim.get('claimed')
dispatch=claim['task']['dispatch']['dispatch_id'];token=claim['lease_token']
ex._leased_transition(root,dispatch,token,consumer,'acknowledge',{'actual_agent':'codex','actual_model':'','fallback_reason':'Current explicit user evaluation task executed by current Codex; exact model identifier not inferred.'})
r=managed_execution_start(root,dispatch,token,consumer)
print(json.dumps({'run_id':rid,'started':r.get('ok'),'managed':r.get('managed')},ensure_ascii=False),flush=True)
progress_code="""import pathlib,json,re
r=pathlib.Path(%s);p=r/'managed_console.log';s=p.read_text(errors='replace') if p.exists() else ''
counts={}
for m in re.finditer(r'\\[EVAL_PROGRESS\\] rank=(\\d+) local=(\\d+)',s):counts[m[1]]=int(m[2])
print(json.dumps({'rank_progress':counts,'reported_samples':sum(counts.values()),'error_records':sum('Traceback (most recent call last)' in line or 'RuntimeError:' in line or 'ValueError:' in line for line in s.splitlines()),'inputs_ready':(r/'payload/inputs.json').exists(),'metrics_ready':(r/'metrics.json').exists()}))
"""%repr(run)
for attempt in range(90):
 s=managed_execution_status(root,dispatch,token,consumer,heartbeat=True)
 print(json.dumps({k:s.get(k) for k in ['state','exit_code','completion_candidate']},ensure_ascii=False),flush=True)
 obs=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ClearAllForwardings=yes','SZY-3090','--',shlex.join(['python3','-c',progress_code])],capture_output=True,text=True,timeout=25)
 if obs.returncode==0: print(obs.stdout.strip(),flush=True)
 else: print(json.dumps({'progress_observation_unavailable':True}),flush=True)
 if s.get('completion_candidate') and str(s.get('exit_code'))=='0':
  for _ in range(3):
   try:
    done=managed_execution_complete(root,dispatch,token,consumer)
    print(json.dumps({'completed':done.get('ok'),'run':done.get('run'),'warnings':done.get('warnings')},ensure_ascii=False),flush=True)
    pathlib.Path('.pi/analysis/e014-beta0-step50-eval/completion_receipt.json').write_text(json.dumps({'run_id':rid,'completed':done.get('ok'),'run':done.get('run'),'warnings':done.get('warnings')},ensure_ascii=False,indent=2)+'\n')
    break
   except ValueError as e:
    if 'not yet stable' not in str(e):raise
    time.sleep(2)
  else:raise RuntimeError('metrics did not stabilize')
  break
 if s.get('exit_code') not in (None,0,'0'):raise RuntimeError('evaluation exited '+str(s['exit_code'])+'; inspect own logs and preserve outputs')
 time.sleep(30)
else:raise RuntimeError('evaluation monitoring reached 45 minute observation limit; do not restart')
