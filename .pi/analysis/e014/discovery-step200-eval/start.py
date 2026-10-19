import sys,json,time,shlex
sys.path.insert(0,'/home/zhengyuesong/Tools/survey-tool');import surveyctl
from survey_tool import experiments as ex
from survey_tool.managed_execution import managed_execution_start,managed_execution_status
from pathlib import Path
binding=json.loads(Path('.pi/analysis/e014/discovery-step200-eval/binding.json').read_text())
root=surveyctl.root_for('.');rid=binding['run_id'];c='pi-steward:e014-discovery-step200-eval'
base='/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/'
run=binding['run_dir'];cp=binding['checkpoint']
config='configs/experiments/E-014/evaluation/e014_boxes_then_scores_sft659_step0_eval1766.py'
options={'work_dir':run+'/payload','test_dataloader.dataset.ann_file':run+'/inputs/manifest.json','evaluation.inputs_file':run+'/inputs/inputs.json','evaluation.checkpoint':cp,'evaluation.adapter_subdir':'adapter/policy','evaluation.expected_inputs.checkpoint':cp,'evaluation.expected_inputs.step':200}
argv=['env','HF_HOME='+run+'/cache/huggingface','TORCH_HOME='+run+'/cache/torch','XDG_CACHE_HOME='+run+'/cache/xdg','TRITON_CACHE_DIR='+run+'/cache/triton','bash','tools/run.sh',config,'--cfg-options']+[f'{k}={v}' for k,v in options.items()]
r=ex.update_run(root,rid,dict(git_commit=binding['evaluation_git_commit'],seed=20260901,config=config,log_path=run+'/managed_console.log',metrics_path=run+'/payload/evaluation/metrics.json',implementation_details='用户要求改名训练目录后评测step200；真实训练目录已更名、旧路径symlink兼容、原文件元数据保留。step200 optimizer.steps=200和权重/优化器文件哈希稳定核验；原训练candidate_discovery_priority_v1/beta0/score.4/Selected.2/200步正常完成。共享新协议评测入口CLI仅覆盖checkpoint/adapter_subdir/expected step与独立路径，1766/greedy192/vision4096/seed20260901/require_eos/boxes_then_scores_v1保持。代码1c47c730未变化，误解产生的未提交日志代码已撤回；无额外测试，不恢复训练，不持续监控。'))
ex.prepare_direct_steward_run(root,rid,r['updated'],actor='terminal_pi:user-request-rename-directory-then-evaluate-step200')
ex.prepare_managed_run_command(root,rid,shlex.join(argv),consumer=c)
a=ex.claim_run_execution(root,rid,c);assert a.get('claimed')
d=a['task']['dispatch']['dispatch_id'];t=a['lease_token']
ex._leased_transition(root,d,t,c,'acknowledge',dict(actual_agent='codex',actual_model='',fallback_reason='Current user-authorized Codex executor'))
managed_execution_start(root,d,t,c)
s=managed_execution_status(root,d,t,c,heartbeat=True)
print(json.dumps(dict(run=rid,state=s['state'],running=s['tmux_alive'],exit_code=s['exit_code'])),flush=True)
