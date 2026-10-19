import sys,json,time,shlex
sys.path.insert(0,'/home/zhengyuesong/Tools/survey-tool');import surveyctl
from survey_tool import experiments as ex
from survey_tool.managed_execution import managed_execution_start,managed_execution_status
root=surveyctl.root_for('.');rid='e014-boxes-then-scores-beta0-step150-eval1766';c='pi-steward:e014-newprotocol-step150-eval'
base='/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/'
run=base+rid;cp=base+'e014-boxes-then-scores-beta0-sft659-seed11451/payload/grpo/checkpoints/step_000150'
config='configs/experiments/E-014/evaluation/e014_boxes_then_scores_sft659_step0_eval1766.py'
options={'work_dir':run+'/payload','test_dataloader.dataset.ann_file':run+'/inputs/manifest.json','evaluation.inputs_file':run+'/inputs/inputs.json','evaluation.checkpoint':cp,'evaluation.adapter_subdir':'adapter/policy','evaluation.expected_inputs.checkpoint':cp,'evaluation.expected_inputs.step':150}
argv=['env','HF_HOME='+run+'/cache/huggingface','TORCH_HOME='+run+'/cache/torch','XDG_CACHE_HOME='+run+'/cache/xdg','TRITON_CACHE_DIR='+run+'/cache/triton','bash','tools/run.sh',config,'--cfg-options']+[f'{k}={v}' for k,v in options.items()]
r=ex.update_run(root,rid,dict(git_commit='41698665d15742276bf22d1376e8d53a367c07db',seed=20260901,config=config,log_path=run+'/managed_console.log',metrics_path=run+'/payload/evaluation/metrics.json',implementation_details='原训练主动停止于8rank共同184；checkpoint150 optimizer.steps=150，完整非空稳定文件核验，policy SHA256=fad960526f97d6642cd84cbb8e31c9a5d929a9b45c2566933be039fdb93fda14。复用新协议step0通用入口，CLI仅替换step150 checkpoint/adapter子目录及独立路径。1766/greedy192/vision4096/seed20260901/require_eos/boxes_then_scores_v1不变；训练来源beta0、两种补偿0。无源码修改、未测试、不自动恢复训练，不持续监控。'))
ex.prepare_direct_steward_run(root,rid,r['updated'],actor='terminal_pi:user-request-stop-and-evaluate-step150')
ex.prepare_managed_run_command(root,rid,shlex.join(argv),consumer=c)
a=ex.claim_run_execution(root,rid,c);assert a.get('claimed')
d=a['task']['dispatch']['dispatch_id'];t=a['lease_token']
ex._leased_transition(root,d,t,c,'acknowledge',dict(actual_agent='codex',actual_model='',fallback_reason='Current user-authorized Codex executor'))
managed_execution_start(root,d,t,c)
s=managed_execution_status(root,d,t,c,heartbeat=True)
print(json.dumps(dict(run=rid,state=s['state'],running=s['tmux_alive'],exit_code=s['exit_code'])),flush=True)
