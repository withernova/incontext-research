import sys,json,shlex
from pathlib import Path
sys.path.insert(0,'/home/zhengyuesong/Tools/survey-tool');import surveyctl
from survey_tool import experiments as ex
from survey_tool.managed_execution import managed_execution_start,managed_execution_status
p=Path('.pi/code-review/e014-tier-grpo');b=json.loads((p/'binding.json').read_text())
root=surveyctl.root_for('.');rid=b['run_id'];c='pi-steward:e014-tier-g8-400step';base=b['run_dir']
r=ex.update_run(root,rid,dict(git_commit=b['git_commit'],seed=11451,config=b['config'],log_path=base+'/managed_console.log',metrics_path=base+'/metrics.json',implementation_details='用户授权新训练：candidate_behavior_tier_v1；正样本 .65L+.05Oracle+.15Selected+.15(1-E)+.05C-.02D-.02O，L为五档0..4，IoU与score分档阈值均.5且用途不同；C仅双实例拼图一对一min覆盖；D为max((pairIoU-.9)/.1,0)，O为任一逆序。负样本沿用模拟独立公式1-E-.05D-.05O，无档位；非法-1。没有额外命中/结构常数/探索/框数奖励。原SFT659 fresh初始化，beta0、group_size8、max_steps400、save50，seed11451、lr8e-5、clip.2、192tokens、max_pixels262144、原4000+对称4000保持。相对父训练同时改变奖励/G/步数，非单变量对照。review 9ad1b2256a9b6235通过，AST/diff/导航静态检查通过；未测试。已授权指定SHA部署；只做启动核验，不持续监控、不自动续训。原模拟工具经官方扩展补审阅并提交c24c797，训练实现e64c874。'))
ex.prepare_direct_steward_run(root,rid,r['updated'],actor='terminal_pi:user-request-tier-reward-g8-400step')
argv=['bash','tools/run.sh',b['config'],'--cfg-options','output.run_name='+rid]
ex.prepare_managed_run_command(root,rid,shlex.join(argv),consumer=c)
a=ex.claim_run_execution(root,rid,c);assert a.get('claimed');d=a['task']['dispatch']['dispatch_id'];t=a['lease_token']
ex._leased_transition(root,d,t,c,'acknowledge',dict(actual_agent='codex',actual_model='',fallback_reason='Current user-authorized Codex executor'))
managed_execution_start(root,d,t,c)
s=managed_execution_status(root,d,t,c,heartbeat=True)
result={'run':rid,'state':s['state'],'running':s['tmux_alive'],'exit_code':s['exit_code']}
(p/'startup_status.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
