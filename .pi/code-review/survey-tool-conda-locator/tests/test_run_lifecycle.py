import json,pathlib,tempfile,unittest
import server
from survey_tool.run_lifecycle import architecture_assessment,effective_run_workflow,validate_implementation_ref

class RunLifecycleTest(unittest.TestCase):
 def setUp(self):
  self.root=pathlib.Path(tempfile.mkdtemp());(self.root/'state.md').write_text('x')
  server.write_tool_json(self.root,'servers.json',[{'id':'S','ssh_host':'host'}]);server.write_tool_json(self.root,'workspaces.json',[{'id':'W','server_id':'S','remote_repo':'/repo','remote_experiment_root':'/exp'}]);server.create_experiment(self.root,{'title':'x','objective':'test','workspace_id':'W'},'E-001')
  self.metric={'id':'accuracy','name':'准确率','formula':'正确数/总数','meaning':'正确比例','direction':'higher','unit':'ratio','aggregation':'mean','scope':'test'}
 def ref(self): return {'schema':'survey-tool.run-implementation/v1','package_root':'src/lab','entrypoint':'lab.cli:main','config_path':'configs/e/r.yaml','launcher_path':'scripts/e/run.sh','reused_modules':['src/lab/pipeline.py'],'added_modules':['src/lab/hooks/mask.py'],'tests':['tests/test_mask.py']}
 def test_lifecycle_and_analysis(self):
  r=server.create_run(self.root,'E-001',{'workflow_version':2,'variant':'比较遮挡','purpose':'比较参考区域遮挡前后的定位准确率','metric_plan':'复用 accuracy，因为它直接衡量定位是否正确','workspace_id':'W','data_definition':'固定测试集','variables_controls':'只改变遮挡条件'},'R')
  self.assertEqual(effective_run_workflow(r)['stage'],'code_planning')
  server.update_experiment(self.root,'E-001',{'metric_definitions':[self.metric]})
  server.update_run(self.root,'R',{'architecture_plan':'公共 Pipeline 加 ReferenceMaskHook；Run 只增加配置和 Shell','implementation_ref':self.ref(),'command':'bash scripts/e/run.sh'})
  ready=server.advance_run_workflow(self.root,'R','implementation-ready');self.assertEqual(ready['run']['workflow_stage'],'ready_for_review')
  server.review_run(self.root,'R','submit');server.review_run(self.root,'R','approve');server.review_run(self.root,'R','authorize_execution')
  c=server.claim_next_execution(self.root,'pi');d=c['task']['dispatch'];tok=c['lease_token'];server._leased_transition(self.root,d['dispatch_id'],tok,'pi','acknowledge',{'actual_agent':d['requested_agent'],'actual_model':d['requested_model']});started=server._leased_transition(self.root,d['dispatch_id'],tok,'pi','running');self.assertFalse(started['steward_started']);self.assertTrue((self.root/'.pi/experiment-steward.json').exists());self.assertTrue((self.root/'.pi/stewards/R.json').exists())
  server._leased_transition(self.root,d['dispatch_id'],tok,'pi','complete',{'artifact':'metrics.json'});run=next(x for x in server.experiment_data(self.root)['runs'] if x['id']=='R');self.assertEqual(run['workflow_stage'],'analysis_pending')
  out=server.advance_run_workflow(self.root,'R','finalize-results',result_fields={'result_analysis':'准确率较对照提高，说明参考区域对定位有帮助。','key_results':[{'metric_id':'accuracy','value':0.8,'comparison':'control=0.7','delta':0.1,'artifact':'metrics.json','interpretation':'提高十个百分点'}]});self.assertEqual(out['run']['workflow_stage'],'completed')
 def test_failed_run_status_can_be_audited_and_corrected_on_same_attempt(self):
  server.create_run(self.root,'E-001',{'workflow_version':2,'variant':'状态修正','purpose':'验证同一个执行 attempt 的误判修正','metric_plan':'accuracy','workspace_id':'W','data_definition':'固定测试集','variables_controls':'固定参数'},'R-correct')
  server.update_experiment(self.root,'E-001',{'metric_definitions':[self.metric]})
  server.update_run(self.root,'R-correct',{'architecture_plan':'复用现有 Pipeline','implementation_ref':self.ref(),'command':'bash scripts/e/run.sh'})
  server.advance_run_workflow(self.root,'R-correct','implementation-ready');server.review_run(self.root,'R-correct','submit');server.review_run(self.root,'R-correct','approve');server.review_run(self.root,'R-correct','authorize_execution')
  claimed=server.claim_run_execution(self.root,'R-correct','pi-steward:test');dispatch=claimed['task']['dispatch'];token=claimed['lease_token']
  server._leased_transition(self.root,dispatch['dispatch_id'],token,'pi-steward:test','acknowledge',{'executor_kind':'steward'})
  server._leased_transition(self.root,dispatch['dispatch_id'],token,'pi-steward:test','running',{'managed_execution':True})
  server.update_managed_execution_metadata(self.root,dispatch['dispatch_id'],{'started_evidence':'tmux_new_session_ok','tmux_session':'run-correct'})
  run=next(row for row in server.experiment_data(self.root)['runs'] if row['id']=='R-correct')
  failed=server.mark_steward_attempt_failed(self.root,'R-correct',run['updated'],'错误地认为 Steward 退出')
  corrected=server.correct_failed_run_state(self.root,'R-correct',failed['run']['updated'],'running','远端 tmux 与日志确认仍在运行')
  self.assertEqual(corrected['dispatch']['dispatch_id'],dispatch['dispatch_id']);self.assertEqual(corrected['dispatch']['status'],'running');self.assertTrue(corrected['requires_reattach']);self.assertEqual(corrected['run']['workflow_stage'],'running')
  self.assertEqual(corrected['run']['status_correction_history'][-1]['prior_failure']['reason'],'错误地认为 Steward 退出')
  reattached=server.reattach_managed_execution(self.root,dispatch['dispatch_id'],'pi-steward:replacement');self.assertTrue(reattached['reattached']);self.assertEqual(reattached['dispatch']['dispatch_id'],dispatch['dispatch_id'])
  run=next(row for row in server.experiment_data(self.root)['runs'] if row['id']=='R-correct');failed_again=server.mark_steward_attempt_failed(self.root,'R-correct',run['updated'],'错误地把正常退出当作失败')
  completed=server.correct_failed_run_state(self.root,'R-correct',failed_again['run']['updated'],'analysis_pending','退出码与产物确认程序已经结束','exit 0；metrics.json 已生成')
  self.assertEqual(completed['dispatch']['dispatch_id'],dispatch['dispatch_id']);self.assertEqual(completed['dispatch']['status'],'completed');self.assertFalse(completed['requires_reattach']);self.assertEqual(completed['run']['workflow_stage'],'analysis_pending');self.assertEqual(completed['run']['execution_dispatch_completion_evidence']['result_message'],'exit 0；metrics.json 已生成');self.assertEqual(len(completed['run']['status_correction_history']),2)
  with self.assertRaisesRegex(ValueError,'failed workflow-v2'):
   server.correct_failed_run_state(self.root,'R-correct',completed['run']['updated'],'running','不可重复修正')
 def test_unsatisfactory_results_open_revision_then_direct_steward_snapshots_new_spec(self):
  server.create_run(self.root,'E-001',{'workflow_version':2,'variant':'首轮','purpose':'验证结果不满意后的原地修订','metric_plan':'accuracy','workspace_id':'W','data_definition':'固定测试集','variables_controls':'两角色对照'},'R-revise')
  server.update_experiment(self.root,'E-001',{'metric_definitions':[self.metric]})
  server.update_run(self.root,'R-revise',{'architecture_plan':'两角色实现','implementation_ref':self.ref(),'command':'bash scripts/e/run.sh'})
  server.advance_run_workflow(self.root,'R-revise','implementation-ready');server.review_run(self.root,'R-revise','submit');server.review_run(self.root,'R-revise','approve');server.review_run(self.root,'R-revise','authorize_execution')
  claimed=server.claim_run_execution(self.root,'R-revise','pi');dispatch=claimed['task']['dispatch'];token=claimed['lease_token'];server._leased_transition(self.root,dispatch['dispatch_id'],token,'pi','acknowledge',{'actual_agent':dispatch['requested_agent'],'actual_model':dispatch['requested_model']});server._leased_transition(self.root,dispatch['dispatch_id'],token,'pi','running');server._leased_transition(self.root,dispatch['dispatch_id'],token,'pi','complete',{'artifact':'first-round.json'})
  revision=server.advance_run_workflow(self.root,'R-revise','mark-failed')['run']
  self.assertEqual(revision['workflow_stage'],'failed');self.assertEqual(revision['review_status'],'changes_requested');self.assertNotIn('execution_authorized_at',revision);self.assertNotIn('execution_dispatch_id',revision);self.assertEqual(revision['revision_history'][-1]['prior_dispatch_id'],dispatch['dispatch_id'])
  old_dispatch=next(row for row in server._outbox_read(self.root)['items'] if row['dispatch_id']==dispatch['dispatch_id']);self.assertEqual(old_dispatch['status'],'completed')
  revised=server.update_run(self.root,'R-revise',{'architecture_plan':'三角色实现，新增 Q→R 与可视化交付','variables_controls':'三角色固定对照与可视化'})
  prepared=server.prepare_direct_steward_run(self.root,'R-revise',revised['updated'])
  self.assertEqual(prepared['run']['workflow_stage'],'ready_to_run');self.assertEqual(prepared['run']['review_status'],'approved');self.assertTrue(prepared['run']['execution_authorized_at']);self.assertEqual(prepared['run']['approved_spec']['architecture_plan'],'三角色实现，新增 Q→R 与可视化交付');self.assertNotEqual(prepared['dispatch']['dispatch_id'],dispatch['dispatch_id']);self.assertEqual(prepared['dispatch']['status'],'queued')
 def test_failed_approved_run_can_be_returned_for_revision_without_registry_bypass(self):
  server.create_run(self.root,'E-001',{'workflow_version':2,'variant':'失败后修订','purpose':'验证 failed approved 可显式退回修改','metric_plan':'accuracy','workspace_id':'W','data_definition':'固定测试集','variables_controls':'旧 head 名单'},'R-failed-revise')
  server.update_experiment(self.root,'E-001',{'metric_definitions':[self.metric]});server.update_run(self.root,'R-failed-revise',{'architecture_plan':'旧实现','implementation_ref':self.ref(),'command':'bash scripts/e/run.sh'});server.advance_run_workflow(self.root,'R-failed-revise','implementation-ready');server.review_run(self.root,'R-failed-revise','submit');server.review_run(self.root,'R-failed-revise','approve');server.review_run(self.root,'R-failed-revise','authorize_execution')
  claimed=server.claim_run_execution(self.root,'R-failed-revise','pi');dispatch=claimed['task']['dispatch'];token=claimed['lease_token'];server._leased_transition(self.root,dispatch['dispatch_id'],token,'pi','acknowledge',{'actual_agent':dispatch['requested_agent'],'actual_model':dispatch['requested_model']});server._leased_transition(self.root,dispatch['dispatch_id'],token,'pi','running');server._leased_transition(self.root,dispatch['dispatch_id'],token,'pi','fail',{'failure_class':'implementation','reason':'首轮实现不满足要求','retryable':True})
  failed=next(row for row in server.experiment_data(self.root)['runs'] if row['id']=='R-failed-revise');self.assertEqual((failed['workflow_stage'],failed['review_status']),('failed','approved'))
  with self.assertRaisesRegex(ValueError,'运行开始后'):
   server.advance_run_workflow(self.root,'R-failed-revise','reopen-design')
  opened=server.review_run(self.root,'R-failed-revise','request_changes','改用 actual Top3/Top5 并加入哈希断言')
  self.assertEqual((opened['workflow_stage'],opened['review_status']),('failed','changes_requested'));self.assertNotIn('execution_authorized_at',opened);self.assertNotIn('execution_dispatch_id',opened)
  invalidated=next(row for row in server._outbox_read(self.root)['items'] if row['dispatch_id']==dispatch['dispatch_id']);self.assertEqual(invalidated['status'],'failed');self.assertFalse(invalidated['retryable']);self.assertTrue(invalidated['revision_invalidated_at'])
  stale_retry=server.retry_execution(self.root,dispatch['dispatch_id'],'旧 Steward 尝试 retry','Run 已由人类退回修改');self.assertFalse(stale_retry['requeued']);self.assertEqual(stale_retry['state'],'revision_open');self.assertEqual(stale_retry['run']['review_status'],'changes_requested')
  reopened=server.advance_run_workflow(self.root,'R-failed-revise','reopen-design')['run'];self.assertEqual((reopened['workflow_stage'],reopened['review_status']),('research_design','changes_requested'))
  revised=server.update_run(self.root,'R-failed-revise',{'architecture_plan':'读取 actual summary 并精确断言','variables_controls':'新 actual head 名单'});prepared=server.prepare_direct_steward_run(self.root,'R-failed-revise',revised['updated'])
  self.assertEqual((prepared['run']['workflow_stage'],prepared['run']['review_status']),('ready_to_run','approved'));self.assertEqual(prepared['run']['approved_spec']['variables_controls'],'新 actual head 名单');self.assertNotEqual(prepared['dispatch']['dispatch_id'],dispatch['dispatch_id'])
  redirected=server.retry_execution(self.root,dispatch['dispatch_id'],'旧 Agent 仍引用旧 ID','用户已经批准当前修订');self.assertEqual(redirected['state'],'superseded_by_current_attempt');self.assertEqual(redirected['current_dispatch']['dispatch_id'],prepared['dispatch']['dispatch_id']);self.assertEqual(redirected['next_action'],'claim_current_dispatch_by_run_id')
  with self.assertRaisesRegex(ValueError,prepared['dispatch']['dispatch_id']): server.reattach_managed_execution(self.root,dispatch['dispatch_id'],'pi-steward:stale')
 def test_rejected_spec_can_be_content_deleted_without_deleting_run_identity(self):
  run=server.create_run(self.root,'E-001',{'workflow_version':2,'variant':'错误旧方案','purpose':'旧 G/L heads','research_question':'旧 G heads 是否有效','metric_plan':'旧指标','variables_controls':'G=[L1H1], L=[L2H2]','architecture_plan':'旧实现','command':'bash old.sh','workspace_id':'W'},'R-discard')
  prepared=server.prepare_direct_steward_run(self.root,'R-discard',run['updated']);self.assertEqual(prepared['dispatch']['status'],'queued')
  current_context=server.experiment_constraints(self.root,'E-001','R-discard');visible=current_context['target_run'];self.assertEqual(visible['purpose'],'旧 G/L heads');self.assertNotIn('approved_spec',visible);self.assertNotIn('review_history',visible);self.assertFalse(visible['historical_snapshots_available_to_agent'])
  stored=next(row for row in server.experiment_data(self.root)['runs'] if row['id']=='R-discard');self.assertNotIn('snapshot',stored['review_history'][-1]);self.assertRegex(stored['review_history'][-1]['snapshot_hash'],r'^sha256:[0-9a-f]{64}$')
  discarded=server.discard_rejected_run_spec(self.root,'R-discard',prepared['run']['updated'],'旧 G/L 规格已被用户明确否决')['run']
  self.assertEqual((discarded['workflow_stage'],discarded['review_status']),('research_design','changes_requested'));self.assertEqual(discarded['variant'],'错误旧方案');self.assertNotIn('purpose',discarded);self.assertNotIn('variables_controls',discarded);self.assertNotIn('approved_spec',discarded);self.assertNotIn('execution_authorized_at',discarded);self.assertEqual(discarded['review_history'][0]['snapshot_content_retained'],False)
  old=next(row for row in server._outbox_read(self.root)['items'] if row['run_id']=='R-discard');self.assertEqual(old['status'],'cancelled')
  after=json.dumps(server.experiment_constraints(self.root,'E-001','R-discard'),ensure_ascii=False);self.assertNotIn('旧 G/L heads',after);self.assertNotIn('G=[L1H1]',after);self.assertNotIn('bash old.sh',after)
  after_full=json.dumps(server.experiment_constraints(self.root,'E-001','R-discard',full=True),ensure_ascii=False);self.assertNotIn('旧 G/L heads',after_full);self.assertNotIn('G=[L1H1]',after_full);self.assertNotIn('bash old.sh',after_full)
 def test_legacy_codespace_is_rejected(self):
  ref=self.ref();ref['package_root']='codespace/e'
  with self.assertRaisesRegex(ValueError,'codespace'): architecture_assessment(ref)
  server.create_run(self.root,'E-001',{'variant':'hard-cut'},'R-cut')
  with self.assertRaisesRegex(ValueError,'codespace'): server.update_run(self.root,'R-cut',{'command':'bash ./codespace/run.sh'})
 def test_historical_codespace_ref_is_removed_by_workflow_and_optional_ref_is_valid(self):
  self.assertEqual(validate_implementation_ref({})['launcher_path'],'')
  server.create_run(self.root,'E-001',{'workflow_version':2,'variant':'migrate','purpose':'p','metric_plan':'accuracy','workspace_id':'W'},'R-migrate')
  data=server.experiment_data(self.root);run=next(row for row in data['runs'] if row['id']=='R-migrate');run['architecture_plan']='复用主仓库训练入口，由 Pi 在启动前解析实际配置';run['command']='python train.py --manifest <manifest>';run['implementation_ref']={**self.ref(),'launcher_path':'codespace/E-001/run.sh'};server.write_tool_json(self.root,'runs.json',data['runs'])
  ready=server.advance_run_workflow(self.root,'R-migrate','implementation-ready');self.assertEqual(ready['run']['workflow_stage'],'ready_for_review');self.assertEqual(ready['run']['implementation_ref']['launcher_path'],'');self.assertEqual(ready['run']['implementation_history'][-1]['migration'],'removed_legacy_codespace_references')
  with self.assertRaisesRegex(ValueError,'codespace'):
   server.update_run(self.root,'R-migrate',{'implementation_ref':{**self.ref(),'launcher_path':'codespace/new.sh'}})
 def test_legacy_unchanged(self):
  run=server.create_run(self.root,'E-001',{'variant':'old'},'OLD');self.assertTrue(effective_run_workflow(run)['legacy'])
 def test_steward_configs_are_run_scoped(self):
  first=server.create_run(self.root,'E-001',{'variant':'one','workspace_id':'W','command':'python one.py','artifact_dir':'/exp/R-one'},'R-one');second=server.create_run(self.root,'E-001',{'variant':'two','workspace_id':'W','command':'python two.py','artifact_dir':'/exp/R-two'},'R-two')
  server._write_steward_config(self.root,first,managed=True);server._write_steward_config(self.root,second,managed=True)
  one=json.loads((self.root/'.pi/stewards/R-one.json').read_text());two=json.loads((self.root/'.pi/stewards/R-two.json').read_text());legacy=json.loads((self.root/'.pi/experiment-steward.json').read_text())
  self.assertEqual(one['identity']['runId'],'R-one');self.assertEqual(two['identity']['runId'],'R-two');self.assertEqual(legacy['identity']['runId'],'R-two')

if __name__=='__main__':unittest.main()
