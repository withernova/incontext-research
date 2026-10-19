import sys,json,shlex
from pathlib import Path
sys.path.insert(0,'/home/zhengyuesong/Tools/survey-tool');import surveyctl
from survey_tool import experiments as ex
from survey_tool.managed_execution import managed_execution_start,managed_execution_status
p=Path('.pi/analysis/e014/e014-20261016T014300Z-discovery-score05-g8-kl0-sft659-400step-seed11451');b=json.loads((p/'binding.json').read_text())
root=surveyctl.root_for('.');rid=b['run_id'];c='pi-steward:e014-discovery-score05-g8-400step';base=b['run_dir']
r=ex.update_run(root,rid,dict(git_commit=b['git_commit'],seed=11451,config=b['config'],log_path=base+'/managed_console.log',metrics_path=base+'/metrics.json',implementation_details='用户确认回退并重新训练：candidate_discovery_priority_v1，H+Oracle+.5C+.2Selected+.5(1-E)-.05D-.05O。相对旧发现优先score .4改为.5；G4改G8、200改400，非单变量实验。C仅双实例拼图一对一min覆盖，D近重复连续惩罚，O任一次逆序；非法-1、负样本命中/定位/覆盖0。fresh SFT659，beta0，seed11451，save50，lr8e-5/clip.2/192tokens/原4000+对称4000不变；无CE/偏好/分段优势/额外多框补偿。复用已发布部署e64c874代码，CLI覆盖，不修改源码，不新增测试。必要源数据和配置preflight通过后正式启动。保留所有旧产物，不持续监控、不自动续训。'))
ex.prepare_direct_steward_run(root,rid,r['updated'],actor='terminal_pi:user-request-tier-reward-g8-400step')
argv=['bash','tools/run.sh',b['config'],'--cfg-options',*b['overrides']]
ex.prepare_managed_run_command(root,rid,shlex.join(argv),consumer=c)
a=ex.claim_run_execution(root,rid,c);assert a.get('claimed');d=a['task']['dispatch']['dispatch_id'];t=a['lease_token']
ex._leased_transition(root,d,t,c,'acknowledge',dict(actual_agent='codex',actual_model='',fallback_reason='Current user-authorized Codex executor'))
managed_execution_start(root,d,t,c)
s=managed_execution_status(root,d,t,c,heartbeat=True)
result={'run':rid,'state':s['state'],'running':s['tmux_alive'],'exit_code':s['exit_code']}
(p/'startup_status.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
