import sys,json,time,pathlib
sys.path.insert(0,'/home/zhengyuesong/Tools/survey-tool')
import surveyctl
from survey_tool import experiments as ex
from survey_tool.managed_execution import managed_execution_start,managed_execution_status,managed_execution_complete
root=surveyctl.root_for('.')
consumer='pi-steward:e014-boxes-then-scores-authorized'
SHA='41698665d15742276bf22d1376e8d53a367c07db'
E='e014-boxes-then-scores-sft659-step0-eval1766'
T='e014-boxes-then-scores-beta0-sft659-seed11451'
base='/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/'
configs={E:'configs/experiments/E-014/evaluation/e014_boxes_then_scores_sft659_step0_eval1766.py',T:'configs/experiments/E-014/training/e014_boxes_then_scores_grpo.py'}
def emit(**kw):print(json.dumps(kw,ensure_ascii=False),flush=True)
for rid in (E,T):
 command='bash tools/run.sh '+configs[rid]
 if rid==E:
  command='env HF_HOME='+base+rid+'/cache/huggingface TORCH_HOME='+base+rid+'/cache/torch XDG_CACHE_HOME='+base+rid+'/cache/xdg TRITON_CACHE_DIR='+base+rid+'/cache/triton '+command
 details=('新协议boxes_then_scores_v1：先所有bbox再按序score；解析/奖励/评测显式路由；原始序列重放不变；review3086e33f5f827fb4通过，静态检查通过，未测试。'+('原SFT659新协议step0，1766条，greedy192/vision4096/EOS完整性；只迁移image_path，不改变身份GT/split。' if rid==E else '全新SFT659；beta0、exploration_penalty0、multibox_bonus_weight0；score1.1/IoU1/order.12；G4/seed11451/3epochs1500updates/save50/lr8e-5/192tokens；原4000+对称4000；不resume。只做启动核验，无持续训练监控。'))
 r=ex.update_run(root,rid,dict(git_commit=SHA,config=configs[rid],seed=20260901 if rid==E else 11451,implementation_details=details,log_path=base+rid+'/managed_console.log',metrics_path=base+rid+('/payload/evaluation/metrics.json' if rid==E else '/metrics.json')))
 # Concrete fields implement this user's current explicit request; refresh the
 # still-unstarted direct-mode snapshot before resolving its command placeholder.
 ex.prepare_direct_steward_run(root,rid,r['updated'],actor='terminal_pi:user-request-new-protocol-eval-and-training-beta0')
 ex.prepare_managed_run_command(root,rid,command,consumer=consumer)
 emit(prepared=rid,config=configs[rid])
def start(rid):
 c=ex.claim_run_execution(root,rid,consumer)
 if not c.get('claimed'):raise RuntimeError('Run could not be claimed')
 d=c['task']['dispatch']['dispatch_id'];t=c['lease_token']
 ex._leased_transition(root,d,t,consumer,'acknowledge',dict(actual_agent='codex',actual_model='',fallback_reason='Current user-authorized Codex executor'))
 managed_execution_start(root,d,t,consumer)
 emit(started=rid)
 return d,t
d,t=start(E)
for iteration in range(90):
 s=managed_execution_status(root,d,t,consumer,heartbeat=True)
 if s['completion_candidate']:
  if str(s['exit_code'])!='0':raise RuntimeError('step0 evaluation exited nonzero; training not started')
  try:r=managed_execution_complete(root,d,t,consumer)
  except ValueError as exc:
   if 'not yet stable' not in str(exc):raise
   time.sleep(3);r=managed_execution_complete(root,d,t,consumer)
  if not r.get('ok'):raise RuntimeError('step0 result registration incomplete')
  emit(completed=E,stage=r['run']['workflow_stage']);break
 if not s['tmux_alive']:raise RuntimeError('step0 process ended without completion evidence')
 emit(waiting_for='step0 completion',check=iteration)
 time.sleep(120)
else:raise RuntimeError('step0 completion time bound reached; training not started')
d,t=start(T)
time.sleep(30)
s=managed_execution_status(root,d,t,consumer,heartbeat=True)
emit(training=T,state=s['state'],running=s['tmux_alive'],exit_code=s['exit_code'],continuous_monitoring=False)
