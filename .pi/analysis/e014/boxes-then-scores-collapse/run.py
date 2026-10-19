import sys,pathlib,subprocess,shlex,time,json
sys.path.insert(0,'/home/zhengyuesong/Tools/survey-tool');import surveyctl
from survey_tool import experiments as ex
from survey_tool.managed_execution import managed_execution_start,managed_execution_complete
root=surveyctl.root_for('.');rid='e014-boxes-then-scores-collapse-analysis';c='pi-steward:e014-collapse-analysis';dest='/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/'+rid
code="import pathlib,sys;p=pathlib.Path(sys.argv[1]);p.mkdir(parents=True,exist_ok=False);(p/'analyze.py').write_bytes(sys.stdin.buffer.read())"
a=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ClearAllForwardings=yes','SZY-3090',shlex.join(['python3','-c',code,dest])],input=pathlib.Path('.pi/analysis/e014/boxes-then-scores-collapse/analyze.py').read_bytes(),capture_output=True)
assert a.returncode==0,'analysis upload failed'
r=ex.update_run(root,rid,dict(artifact_dir=dest,output_dir=dest+'/outputs',log_path=dest+'/logs/run.log',metrics_path=dest+'/metrics.json',git_commit='41698665d15742276bf22d1376e8d53a367c07db',implementation_details='一次性CPU分析脚本位于Run根，读取唯一父训练8rank完整rollout，184更新；固定输入分组与删框奖励反事实，输出聚合metrics/source_hashes/examples。不加载模型或修改训练，不继承Solid结论；脚本AST及计算定义静态审阅，未测试。'))
ex.prepare_direct_steward_run(root,rid,r['updated'],actor='terminal_pi:user-request-collapse-analysis')
ex.prepare_managed_run_command(root,rid,'python '+dest+'/analyze.py',consumer=c)
a=ex.claim_run_execution(root,rid,c);assert a.get('claimed');d=a['task']['dispatch']['dispatch_id'];t=a['lease_token']
ex._leased_transition(root,d,t,c,'acknowledge',dict(actual_agent='codex',actual_model='',fallback_reason='Current user-authorized Codex executor'))
managed_execution_start(root,d,t,c)
time.sleep(5)
try:r=managed_execution_complete(root,d,t,c)
except ValueError as e:
 if 'not yet stable' not in str(e):raise
 time.sleep(3);r=managed_execution_complete(root,d,t,c)
print(json.dumps({'ok':r['ok'],'run':r.get('run')},ensure_ascii=False))
a=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ClearAllForwardings=yes','SZY-3090','cat '+shlex.quote(dest+'/metrics.json')],capture_output=True,text=True);assert a.returncode==0
pathlib.Path('.pi/analysis/e014/boxes-then-scores-collapse/metrics.json').write_text(a.stdout);print(a.stdout)
