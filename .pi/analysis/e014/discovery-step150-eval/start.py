import sys,json,time,shlex
sys.path.insert(0,'/home/zhengyuesong/Tools/survey-tool');import surveyctl
from survey_tool import experiments as ex
from survey_tool.managed_execution import managed_execution_start,managed_execution_status
from pathlib import Path
binding=json.loads(Path('.pi/analysis/e014/discovery-step150-eval/binding.json').read_text())
root=surveyctl.root_for('.');rid=binding['run_id'];c='pi-steward:e014-discovery-step150-eval'
base='/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/'
run=binding['run_dir'];cp=binding['checkpoint']
config='configs/experiments/E-014/evaluation/e014_boxes_then_scores_sft659_step0_eval1766.py'
options={'work_dir':run+'/payload','test_dataloader.dataset.ann_file':run+'/inputs/manifest.json','evaluation.inputs_file':run+'/inputs/inputs.json','evaluation.checkpoint':cp,'evaluation.adapter_subdir':'adapter/policy','evaluation.expected_inputs.checkpoint':cp,'evaluation.expected_inputs.step':150}
argv=['env','HF_HOME='+run+'/cache/huggingface','TORCH_HOME='+run+'/cache/torch','XDG_CACHE_HOME='+run+'/cache/xdg','TRITON_CACHE_DIR='+run+'/cache/triton','bash','tools/run.sh',config,'--cfg-options']+[f'{k}={v}' for k,v in options.items()]
r=ex.update_run(root,rid,dict(git_commit=binding['evaluation_git_commit'],seed=20260901,config=config,log_path=run+'/managed_console.log',metrics_path=run+'/payload/evaluation/metrics.json',implementation_details='用户授权评测同一轮discovery-priority score0.4 beta0训练的step150，与step200比较。checkpoint optimizer.steps=150及哈希核验；源训练总预算仍为200。沿用step200的1766条冻结输入、greedy192、vision4096、seed20260901、require_eos、boxes_then_scores_v1及代码1c47c730，仅改变checkpoint与独立输出路径。不恢复训练、不持续监控。'))
ex.prepare_direct_steward_run(root,rid,r['updated'],actor='terminal_pi:user-request-evaluate-step150-compare-step200')
ex.prepare_managed_run_command(root,rid,shlex.join(argv),consumer=c)
a=ex.claim_run_execution(root,rid,c);assert a.get('claimed')
d=a['task']['dispatch']['dispatch_id'];t=a['lease_token']
ex._leased_transition(root,d,t,c,'acknowledge',dict(actual_agent='codex',actual_model='',fallback_reason='Current user-authorized Codex executor'))
managed_execution_start(root,d,t,c)
s=managed_execution_status(root,d,t,c,heartbeat=True)
print(json.dumps(dict(run=rid,state=s['state'],running=s['tmux_alive'],exit_code=s['exit_code'])),flush=True)
