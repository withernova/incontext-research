"""One authorized continuation after evaluation success; never retry training."""
import datetime,json,subprocess,sys,time,shlex
from pathlib import Path
HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[3]
B=json.loads((HERE/'binding.json').read_text())
sys.path.insert(0,'/home/zhengyuesong/Tools/survey-tool')
import surveyctl
from survey_tool import experiments as ex
from survey_tool.managed_execution import managed_execution_complete,managed_execution_start,managed_execution_status
ROOT=surveyctl.root_for(str(PROJECT))
def save(name,value):
 (HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2))
def remote(code):
 r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ClearAllForwardings=yes','SZY-3090','/songzhengyue/miniconda3/envs/IPLoc/bin/python -'],input=code,text=True,capture_output=True,timeout=240)
 if r.returncode:raise RuntimeError('remote operation failed: '+r.stderr[-2000:])
 return json.loads(r.stdout)
def code_action(action):
 argv=['python3','/home/zhengyuesong/Tools/survey-tool/surveyctl.py','--project',str(PROJECT),'code',action,'--workspace-id','03','--commit',B['git_commit']]
 if action=='deploy':argv+=['--confirmation','DEPLOY CODE 03 '+B['git_commit']]
 r=subprocess.run(argv,capture_output=True,text=True,timeout=180)
 if r.returncode:raise RuntimeError(action+' failed: '+r.stderr[-2000:])
 save(action+'.json',json.loads(r.stdout))
def main():
 try:
  with (HERE/'attempted.json').open('x') as f:json.dump({'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},f)
 except FileExistsError:return
 deadline=time.monotonic()+10800
 # Only completion metadata is polled, never rollout/metrics contents or training logs.
 while True:
  status=remote("from pathlib import Path\nimport json\np=Path("+repr(B['evaluation_run_dir'])+")/'.survey-tool-exit-code'\nprint(json.dumps(dict(exit_code=p.read_text().strip() if p.exists() else None)))")
  if status['exit_code'] is not None:break
  if time.monotonic()>deadline:raise TimeoutError('evaluation completion wait expired; training not started')
  time.sleep(60)
 if status['exit_code']!='0':raise RuntimeError('evaluation failed; training not started')
 r=next(x for x in ex.experiment_data(ROOT)['runs'] if x['id']==B['evaluation_run'])
 if r['status']=='running':
  c='pi-steward:auto-complete-before-resume'
  while True:
   try:a=ex.reattach_managed_execution(ROOT,r['execution_dispatch_id'],c);break
   except ValueError as error:
    if '尚未过期' not in str(error) or time.monotonic()>deadline:raise
    time.sleep(60)
  try:done=managed_execution_complete(ROOT,r['execution_dispatch_id'],a['lease_token'],c)
  except ValueError as error:
   if 'not yet stable' not in str(error):raise
   time.sleep(3);done=managed_execution_complete(ROOT,r['execution_dispatch_id'],a['lease_token'],c)
  if not done['ok']:raise RuntimeError('evaluation completion registration failed')
 code_action('publish');code_action('deploy')
 facts=remote("from pathlib import Path\nimport hashlib,json\np=Path("+repr(B['evaluation_run_dir']+'/inputs/manifest.json')+")\nprint(json.dumps(dict(sha=hashlib.sha256(p.read_bytes()).hexdigest(),samples=len(json.loads(p.read_text())))))")
 assert facts['samples']==1766
 periodic=dict(interval=150,expected_samples=1766,manifest_sha256=facts['sha'],seed=20260901,
  dataset=dict(type='VariableCandidateLocalizationDataset',ann_file=B['evaluation_run_dir']+'/inputs/manifest.json',ann_file_sha256=facts['sha'],prompt_variant='boxes_then_scores_v1',target_role='positive-image',normalized_scale=1000),
  evaluator=dict(type='VariableCandidateLocalizationEvaluator',prompt_variant='boxes_then_scores_v1',iou_thresholds=(.25,.5,.75)),
  generation=dict(max_new_tokens=192,do_sample=False,require_eos=True,vision_max_patch_tokens=4096))
 opts=['output.run_name='+B['run_id'],'settings.trainer.reward.score_weight=0.5','settings.trainer.group_size=8','settings.trainer.max_steps=400','settings.trainer.beta=0.0','settings.resume_step=200','settings.resume_source_run='+B['source_run_dir'],'settings.trainer.periodic_evaluation='+repr(periodic)]
 save('resolved_overrides.json',opts)
 preflight="""import sys,json
from pathlib import Path
repo=Path('/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/iploc-szy');sys.path.insert(0,str(repo))
from tools.run_symmetric_grpo import config_settings,source_preflight,resume_settings
from iploc_szy.rl.periodic_evaluation import validate_periodic_evaluation
s=config_settings(repo/CONFIG,OPTS);t=s['trainer'];source=Path(SOURCE);target=Path(TARGET)/'payload'
t.update(manifest=str(source/'payload/data/trainable_pairs.json'),original_manifest=s['source_manifest'],symmetry_manifest=str(source/'payload/data/groups.jsonl'),symmetry_source_pairs=s['symmetry_source_pairs'],output_dir=str(target/'grpo'))
assert t['reward']['coverage_weight']==.5 and t['reward']['score_weight']==.5 and t['group_size']==8 and t['beta']==0 and t['max_steps']==400
resume=resume_settings(source,target,t,200);validate_periodic_evaluation(t);facts=source_preflight(s)
assert facts['git_commit']==SHA
print(json.dumps(dict(preflight='passed',resume=resume,git_commit=facts['git_commit'])))
""".replace('CONFIG',repr(B['config'])).replace('OPTS',repr(opts)).replace('SOURCE',repr(B['source_run_dir'])).replace('TARGET',repr(B['run_dir'])).replace('SHA',repr(B['git_commit']))
 save('preflight.json',remote(preflight))
 rid=B['run_id'];base=B['run_dir'];c='pi-steward:resume200-eval150'
 r=ex.update_run(ROOT,rid,dict(git_commit=B['git_commit'],seed=11451,config=B['config'],log_path=base+'/managed_console.log',metrics_path=base+'/metrics.json',implementation_details='用户授权step200评测成功后，从同一policy+optimizer继续到累计400；coverage .5/score .5/G8/KL0与其余训练参数严格保留。独立Run旧数据只读，SFT659 anchor不变。每150累计步固定1766/greedy192/vision4096/seed20260901/boxes_then_scores评测，本段在300触发，保存到payload/grpo/evaluations/step_000300；评测无梯度且恢复RNG/模式/视觉预算，不参与奖励或选模。旧checkpoint未保存各rank RNG，非精确随机重放；step200以后未保存更新丢弃。代码审阅27d1652b11428115，AST与静态diff检查通过，未测试。已部署指定SHA、必要恢复/源数据preflight通过，无失败自动重试。'))
 ex.prepare_direct_steward_run(ROOT,rid,r['updated'],actor='terminal_pi:user-request-resume-periodic-eval')
 argv=['bash','tools/run.sh',B['config'],'--cfg-options']+opts
 ex.prepare_managed_run_command(ROOT,rid,shlex.join(argv),consumer=c)
 a=ex.claim_run_execution(ROOT,rid,c);assert a.get('claimed');d=a['task']['dispatch']['dispatch_id'];t=a['lease_token']
 ex._leased_transition(ROOT,d,t,c,'acknowledge',dict(actual_agent='codex',actual_model='',fallback_reason='User-authorized deferred continuation'))
 managed_execution_start(ROOT,d,t,c)
 status=managed_execution_status(ROOT,d,t,c,heartbeat=True)
 save('startup_status.json',dict(run=rid,state=status['state'],running=status['tmux_alive'],exit_code=status['exit_code']))
 snapshot=remote("from pathlib import Path\nimport json\np=Path("+repr(base)+")/'payload'\nout={}\nfor name in ['plan.json','trainer_config.json']:\n f=p/name\n if f.exists():\n  x=json.loads(f.read_text());out[name]={k:x.get(k) for k in (['start_step','total_steps','segment_updates'] if name=='plan.json' else ['group_size','beta','reward','periodic_evaluation','e014_resume'])}\nprint(json.dumps(out))")
 save('startup_snapshot.json',snapshot)
 with (PROJECT/'state.md').open('a') as f:f.write('\n- E014_RESUME200_AUTO_STARTED | '+rid+'; step200 eval completed; managed start running; step300 periodic eval enabled; no ongoing monitoring.\n')
if __name__=='__main__':
 try:main()
 except BaseException as error:
  save('error.json',dict(type=type(error).__name__,message=str(error),training_retry=False));raise
