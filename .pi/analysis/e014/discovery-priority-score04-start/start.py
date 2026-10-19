import sys,json
sys.path.insert(0,'/home/zhengyuesong/Tools/survey-tool');import surveyctl
from survey_tool import experiments as ex
from survey_tool.managed_execution import managed_execution_start,managed_execution_status
root=surveyctl.root_for('.');rid='e014-discovery-priority-score04-beta0-sft659-200step-seed11451';c='pi-steward:e014-discovery-priority-200step'
base='/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/'+rid
config='configs/experiments/E-014/training/e014_discovery_priority_score04_grpo.py'
r=ex.update_run(root,rid,dict(git_commit='1c47c7305c695151df81d46019143028e01752ad',seed=11451,config=config,log_path=base+'/managed_console.log',metrics_path=base+'/metrics.json',implementation_details='统一标量candidate_discovery_priority_v1：H+OracleIoU+.5C+.2SelectedIoU+.4(1-E)-.05D-.05O；min一对一覆盖仅已知两实例collage，H用IoU>=.5，D=max((pairIoU-.9)/.1,0)，O任一次逆序。非法-1，负样本定位/命中/覆盖0。原SFT659全新启动，beta0、G4、seed11451、lr8e-5、clip.2、192tokens、max_pixels262144、原4000+对称4000；原epoch调度仅加max_steps200上限，save50，旧配置无变化。无分段优势、score分支、CE/偏好或框数补偿。审阅aef31162078fffc0通过，AST/导航/diff静态检查通过；未测试。只启动核验，无持续监控或自动延长。'))
ex.prepare_direct_steward_run(root,rid,r['updated'],actor='terminal_pi:user-request-discovery-score04-200step')
ex.prepare_managed_run_command(root,rid,'bash tools/run.sh '+config,consumer=c)
a=ex.claim_run_execution(root,rid,c);assert a.get('claimed');d=a['task']['dispatch']['dispatch_id'];t=a['lease_token']
ex._leased_transition(root,d,t,c,'acknowledge',dict(actual_agent='codex',actual_model='',fallback_reason='Current user-authorized Codex executor'))
managed_execution_start(root,d,t,c)
s=managed_execution_status(root,d,t,c,heartbeat=True)
print(json.dumps({'run':rid,'state':s['state'],'running':s['tmux_alive'],'exit_code':s['exit_code']}),flush=True)
