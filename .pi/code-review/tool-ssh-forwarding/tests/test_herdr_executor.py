import io
import json
import os
import pathlib
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

from survey_tool.v2 import V2Store
from survey_tool.v2 import herdr_executor
from survey_tool.v2.herdr_adapter import HerdrStartError, OwnershipAttestation, PromptTurnResult


class HerdrExecutorPreflightTest(unittest.TestCase):
    def setUp(self):
        self.root=pathlib.Path(tempfile.mkdtemp(prefix="herdr-preflight-")); self.store=V2Store(self.root); self.store.initialize()
        self.store.create_object(object_id="Q-cli",object_type="question",project_id="PROJECT-test")
        self.store.create_herdr_launch_request(object_id="HLR-cli",project_id="PROJECT-test",target_object_id="Q-cli",agent_kind="codex",task_type="analysis",task_summary="Review safe evidence")
        self.store.transition_herdr_launch_request("HLR-cli",expected_revision=1,status="awaiting_approval"); self.store.transition_herdr_launch_request("HLR-cli",expected_revision=2,status="approved")
        self.store.authorize_herdr_execution(execution_id="HEX-cli",project_id="PROJECT-test",launch_request_id="HLR-cli",expected_request_revision=3,capability={"managed":True,"cli_available":True,"codex_supported":True})
        self.capability={"managed":True,"cli_available":True,"codex_supported":True,"probe_status":"available","access":"discovery_only"}

    def test_one_shot_cli_claims_and_completes_without_control_or_token_leakage(self):
        output=io.StringIO()
        with mock.patch.dict(os.environ,{"HERDR_ENV":"1"},clear=True), \
             mock.patch("survey_tool.v2.herdr_executor.herdr_capability",return_value=self.capability), \
             mock.patch("survey_tool.v2.store.secrets.token_urlsafe",return_value="RAW-LEASE-SECRET"), \
             mock.patch("survey_tool.v2.capabilities.subprocess.Popen") as popen, \
             redirect_stdout(output):
            code=herdr_executor.main(["--project",str(self.root),"--execution","HEX-cli","--once"])
        self.assertEqual(code,0); payload=json.loads(output.getvalue()); self.assertEqual(payload["state"],"completed")
        self.assertFalse(payload["execution_started"]); self.assertFalse(payload["herdr_invoked"]); self.assertNotIn("RAW-LEASE-SECRET",output.getvalue()); self.assertNotIn(str(self.root),output.getvalue()); popen.assert_not_called()
        execution=self.store.get_herdr_execution("HEX-cli"); self.assertEqual(execution["state"],"completed"); self.assertEqual(execution["lease_token_hash"],""); self.assertEqual(execution["attempt"],1)

    def test_cli_reports_safe_expired_authorization_reason(self):
        output=io.StringIO()
        with mock.patch.dict(os.environ,{"HERDR_ENV":"1"},clear=True),mock.patch("survey_tool.v2.herdr_executor.herdr_capability",return_value=self.capability),redirect_stdout(output):
            self.store.create_object(object_id="Q-expire",object_type="question",project_id="PROJECT-test")
            self.store.create_herdr_launch_request(object_id="HLR-expire",project_id="PROJECT-test",target_object_id="Q-expire",agent_kind="codex",task_type="analysis",task_summary="Review expiry")
            self.store.transition_herdr_launch_request("HLR-expire",expected_revision=1,status="awaiting_approval"); self.store.transition_herdr_launch_request("HLR-expire",expected_revision=2,status="approved")
            self.store.authorize_herdr_execution(execution_id="HEX-expire",project_id="PROJECT-test",launch_request_id="HLR-expire",expected_request_revision=3,capability=self.capability,ttl_seconds=60)
            with self.store.transaction() as conn: conn.execute("UPDATE herdr_executions SET not_after='2000-01-01T00:00:00+00:00' WHERE object_id='HEX-expire'")
            code=herdr_executor.main(["--project",str(self.root),"--execution","HEX-expire","--once","--start-owned"])
        payload=json.loads(output.getvalue()); self.assertEqual(code,1); self.assertEqual(payload["reason"],"Herdr execution authorization has expired")

    def test_cli_refuses_outside_herdr_without_probe_or_store_mutation(self):
        output=io.StringIO()
        with mock.patch.dict(os.environ,{},clear=True),mock.patch("survey_tool.v2.herdr_executor.herdr_capability") as capability,redirect_stdout(output):
            code=herdr_executor.main(["--project",str(self.root),"--execution","HEX-cli","--once","--preflight-only"])
        self.assertEqual(code,1); self.assertEqual(json.loads(output.getvalue())["state"],"refused"); capability.assert_not_called()
        self.assertEqual(self.store.get_herdr_execution("HEX-cli")["state"],"authorized")

    def test_cli_project_lock_prevents_overlap_before_capability_probe(self):
        output=io.StringIO()
        with herdr_executor._project_lock(self.store),mock.patch.dict(os.environ,{"HERDR_ENV":"1"},clear=True),mock.patch("survey_tool.v2.herdr_executor.herdr_capability") as capability,redirect_stdout(output):
            code=herdr_executor.main(["--project",str(self.root),"--execution","HEX-cli","--once","--preflight-only"])
        self.assertEqual(code,1); self.assertEqual(json.loads(output.getvalue())["state"],"failed"); capability.assert_not_called()
        self.assertNotIn(str(self.root),output.getvalue())

    def test_run_state_reader_does_not_import_legacy_server_cycle(self):
        (self.root/".survey-tool").mkdir(exist_ok=True)
        (self.root/".survey-tool"/"runs.json").write_text(json.dumps([{"id":"R-state","experiment_id":"E-001","workflow_stage":"ready_to_run","review_status":"approved","execution_authorized_at":"yes"}]))
        (self.root/".survey-tool"/"execution-outbox.json").write_text(json.dumps({"items":[{"run_id":"R-state","status":"queued","created_at":"1"}]}))
        self.assertEqual(herdr_executor._run_execution_state(self.root,"R-state"),{"experiment_id":"E-001","workflow_stage":"ready_to_run","review_status":"approved","execution_authorized":True,"dispatch_status":"queued"})

    def test_remote_code_workspace_resolves_run_inheritance_without_exposing_paths(self):
        tool=self.root/".survey-tool"
        (tool/"experiments.json").write_text(json.dumps([{"id":"E-code","workspace_id":"W-code"}]))
        (tool/"runs.json").write_text(json.dumps([{"id":"R-code","experiment_id":"E-code","workspace_id":""}]))
        (tool/"workspaces.json").write_text(json.dumps([{"id":"W-code","server_id":"S-code","remote_repo":"/srv/main","code_development":{"mode":"remote"}}]))
        (tool/"servers.json").write_text(json.dumps([{"id":"S-code","ssh_host":"user@gpu"}]))
        self.assertEqual(herdr_executor._remote_code_workspace(self.root,"run","R-code"),{"workspace_id":"W-code","ssh_host":"user@gpu","remote_repo":"/srv/main"})
        (tool/"workspaces.json").write_text(json.dumps([{"id":"W-code","server_id":"S-code","remote_repo":"relative"}]))
        with self.assertRaisesRegex(ValueError,"incomplete"): herdr_executor._remote_code_workspace(self.root,"run","R-code")

    def _local_code_execution(self):
        # Initialize the legacy registry through its supported server entry point.
        import server
        from survey_tool.code_workflow import save_local_binding
        self.store.create_object(object_id="E-local",object_type="experiment",project_id="PROJECT-test")
        self.store.create_herdr_launch_request(object_id="HLR-local",project_id="PROJECT-test",target_object_id="E-local",agent_kind="pi",task_type="implementation",task_summary="本地实现代码")
        self.store.transition_herdr_launch_request("HLR-local",expected_revision=1,status="awaiting_approval")
        self.store.transition_herdr_launch_request("HLR-local",expected_revision=2,status="approved")
        capability={"managed":True,"cli_available":True,"pi_supported":True}
        self.store.authorize_herdr_execution(execution_id="HEX-local",project_id="PROJECT-test",launch_request_id="HLR-local",expected_request_revision=3,capability=capability)
        tool=self.root/".survey-tool"
        (tool/"experiments.json").write_text(json.dumps([{"id":"E-local","workspace_id":"W-local"}]))
        (tool/"runs.json").write_text("[]")
        (tool/"servers.json").write_text(json.dumps([{"id":"S-local","ssh_host":"user@gpu"}]))
        (tool/"workspaces.json").write_text(json.dumps([{"id":"W-local","server_id":"S-local","remote_repo":"/srv/code","code_development":{"mode":"local-git","repository_url":"https://github.com/withernova/iploc-szy","branch":"main"}}]))
        save_local_binding(self.root,"W-local","/local/code")
        adapter=mock.Mock()
        adapter.start_owned.side_effect=lambda **kwargs:OwnershipAttestation(agent_name=kwargs["agent_name"],pane_id="private-pane")
        adapter.prompt_owned.return_value=PromptTurnResult(agent_status="done")
        return capability,adapter

    def test_local_git_prepares_before_agent_and_does_not_start_remote_tmux(self):
        capability,adapter=self._local_code_execution()
        order=[]
        original_start=adapter.start_owned.side_effect
        adapter.start_owned.side_effect=lambda **kw:(order.append('agent'),original_start(**kw))[1]
        with mock.patch("survey_tool.code_workflow.prepare_code",side_effect=lambda *a:order.append('sync')) as prepare:
            result=herdr_executor.run_start_owned(self.root,"HEX-local",environ={"HERDR_ENV":"1"},capability_getter=lambda:capability,adapter=adapter)
        self.assertEqual(result["state"],"completed")
        self.assertEqual(order,['sync','agent'])
        prepare.assert_called_once_with(self.root,'W-local')
        adapter.start_remote_owned.assert_not_called(); adapter.inspect_remote_workspace.assert_not_called()
        envelope=adapter.prompt_owned.call_args.kwargs['envelope'].text
        self.assertIn('local_repo=/local/code',envelope)
        self.assertIn('code prepare --workspace-id W-local',envelope)
        self.assertIn('code publish --workspace-id W-local --commit',envelope)
        self.assertIn('自动提交远端代码改动并 push',envelope)
        self.assertNotIn('或自动 push',envelope)
        self.assertNotIn('代码操作限定于该远端仓库',envelope)
        self.assertNotIn('传 ssh_host、repository_path',envelope)

    def test_unconfigured_code_task_auto_binds_before_prompt_and_uses_discovered_path(self):
        capability,adapter=self._local_code_execution()
        path=self.root/'.survey-tool'/'workspaces.json'
        workspaces=json.loads(path.read_text()); workspaces[0].pop('code_development'); path.write_text(json.dumps(workspaces))
        original=path.read_text()
        with mock.patch('survey_tool.code_workflow._invoke',side_effect=AssertionError('network in prompt')):
            before=herdr_executor._remote_code_workspace(self.root,'experiment','E-local')
        self.assertIn('本地 Git 自动绑定',before['local_code_rules'])
        self.assertEqual(path.read_text(),original,'prompt assembly must not save/SSH')
        def prepare(root,wid):
            workspaces[0]['code_development']={'mode':'local-git','repository_url':'https://github.com/owner/discovered','branch':'feature/actual','storage':'project','transport':'ssh'}
            path.write_text(json.dumps(workspaces))
            return {'binding_created':True}
        with mock.patch('survey_tool.code_workflow.prepare_code',side_effect=prepare) as sync:
            result=herdr_executor.run_start_owned(self.root,'HEX-local',environ={'HERDR_ENV':'1'},capability_getter=lambda:capability,adapter=adapter)
        self.assertEqual(result['state'],'completed')
        sync.assert_called_once_with(self.root,'W-local')
        adapter.start_remote_owned.assert_not_called()
        envelope=adapter.prompt_owned.call_args.kwargs['envelope'].text
        self.assertIn('local_repo='+str(self.root/'code-repositories'/'W-local'/'discovered'),envelope)
        self.assertIn('branch=feature/actual',envelope)
        self.assertNotIn('未绑定：停止',envelope)

    def test_failed_local_git_sync_blocks_agent_creation(self):
        capability,adapter=self._local_code_execution()
        with mock.patch("survey_tool.code_workflow.prepare_code",side_effect=ValueError('dirty repository')):
            result=herdr_executor.run_start_owned(self.root,"HEX-local",environ={"HERDR_ENV":"1"},capability_getter=lambda:capability,adapter=adapter)
        self.assertEqual(result["state"],"attention_required")
        adapter.start_owned.assert_not_called(); adapter.start_remote_owned.assert_not_called(); adapter.prompt_owned.assert_not_called()

    def test_implementation_starts_pi_inside_bound_remote_repo(self):
        self.store.create_object(object_id="E-code",object_type="experiment",project_id="PROJECT-test")
        self.store.create_herdr_launch_request(object_id="HLR-code",project_id="PROJECT-test",target_object_id="E-code",agent_kind="pi",task_type="implementation",task_summary="Add the requested module")
        self.store.transition_herdr_launch_request("HLR-code",expected_revision=1,status="awaiting_approval"); self.store.transition_herdr_launch_request("HLR-code",expected_revision=2,status="approved")
        capability={"managed":True,"cli_available":True,"pi_supported":True,"probe_status":"available","access":"discovery_only"}
        self.store.authorize_herdr_execution(execution_id="HEX-code",project_id="PROJECT-test",launch_request_id="HLR-code",expected_request_revision=3,capability=capability)
        tool=self.root/".survey-tool"
        (tool/"experiments.json").write_text(json.dumps([{"id":"E-code","workspace_id":"W-code"}]))
        (tool/"runs.json").write_text("[]"); (tool/"workspaces.json").write_text(json.dumps([{"id":"W-code","server_id":"S-code","remote_repo":"/srv/main","code_development":{"mode":"remote"}}]))
        (tool/"servers.json").write_text(json.dumps([{"id":"S-code","ssh_host":"user@gpu"}]))
        adapter=mock.Mock(); adapter.start_remote_owned.side_effect=lambda **kwargs:OwnershipAttestation(agent_name=kwargs["agent_name"],pane_id="private-pane"); adapter.prompt_owned.return_value=PromptTurnResult(agent_status="done")
        adapter.inspect_remote_workspace.side_effect=[{"revision":"abc123","files":["src/main.py","pyproject.toml"],"changed_files":[],"unchanged":False},{"revision":"def456","files":["src/main.py","src/new.py","pyproject.toml"],"changed_files":["src/new.py"],"unchanged":False}]
        result=herdr_executor.run_start_owned(self.root,"HEX-code",environ={"HERDR_ENV":"1"},capability_getter=lambda:capability,adapter=adapter)
        self.assertEqual(result["state"],"completed"); self.assertTrue(result["checks"]["remote_repo_context"]); self.assertTrue(result["checks"]["remote_tmux_context"])
        adapter.start_owned.assert_not_called(); call=adapter.start_remote_owned.call_args.kwargs
        self.assertEqual(call["ssh_host"],"user@gpu"); self.assertEqual(call["remote_repo"],"/srv/main")
        envelope=adapter.prompt_owned.call_args.kwargs["envelope"].text
        self.assertIn("Pi 仍运行在本机",envelope); self.assertIn("SSH host：user@gpu",envelope); self.assertIn("代码根目录：/srv/main",envelope)
        self.assertIn("顶层模块=src",envelope); self.assertIn("关键文件=pyproject.toml",envelope)
        maps=json.loads((tool/"workspace-code-maps.json").read_text()); saved=maps["maps"][0]
        self.assertEqual(saved["revision"],"def456"); self.assertIn("src/new.py",saved["files"]); self.assertEqual(saved["recent_changed_files"],["src/new.py"]); self.assertTrue(result["checks"]["workspace_code_map_maintained"])

    def test_implementation_can_start_codex_with_current_canonical_context(self):
        self.store.create_object(object_id="E-codex",object_type="experiment",project_id="PROJECT-test")
        summary="实现数据适配器，并复用明确选择的 Q-001 结论"
        self.store.create_herdr_launch_request(object_id="HLR-codex",project_id="PROJECT-test",target_object_id="E-codex",agent_kind="codex",task_type="implementation",task_summary=summary,safe_config={"reference_ids":["R-explicit"]})
        self.store.transition_herdr_launch_request("HLR-codex",expected_revision=1,status="awaiting_approval"); self.store.transition_herdr_launch_request("HLR-codex",expected_revision=2,status="approved")
        capability={"managed":True,"cli_available":True,"codex_supported":True,"probe_status":"available","access":"discovery_only"}
        self.store.authorize_herdr_execution(execution_id="HEX-codex",project_id="PROJECT-test",launch_request_id="HLR-codex",expected_request_revision=3,capability=capability)
        tool=self.root/".survey-tool"
        (tool/"experiments.json").write_text(json.dumps([{"id":"E-codex","title":"Context experiment","objective":"Implement robust loading","hypothesis":"The adapter removes schema drift","workspace_id":"W-code"}]))
        (tool/"runs.json").write_text(json.dumps([{"id":"R-solid","experiment_id":"E-codex","purpose":"Verified adapter output","result_summary":"SOLID-CONTEXT","evidence_label":"solid"},{"id":"R-explicit","experiment_id":"E-other","purpose":"Explicit comparison","result_summary":"EXPLICIT-CONTEXT"},{"id":"R-hidden","experiment_id":"E-codex","purpose":"Stale failed output","result_summary":"HIDDEN-CONTEXT"}]))
        (tool/"workspaces.json").write_text(json.dumps([{"id":"W-code","server_id":"S-code","remote_repo":"/srv/main","code_development":{"mode":"remote"}}]))
        (tool/"servers.json").write_text(json.dumps([{"id":"S-code","ssh_host":"user@gpu"}]))
        adapter=mock.Mock(); adapter.start_owned.side_effect=lambda **kwargs:OwnershipAttestation(agent_name=kwargs["agent_name"],pane_id="private-pane"); adapter.prompt_owned.return_value=PromptTurnResult(agent_status="done")
        adapter.inspect_remote_workspace.return_value={"revision":"abc123","files":["src/main.py","pyproject.toml"],"changed_files":[],"unchanged":False}
        result=herdr_executor.run_start_owned(self.root,"HEX-codex",environ={"HERDR_ENV":"1"},capability_getter=lambda:capability,adapter=adapter)
        self.assertEqual(result["state"],"completed"); adapter.start_remote_owned.assert_not_called()
        call=adapter.start_owned.call_args.kwargs; self.assertEqual(call["agent_kind"],"codex"); self.assertTrue(call["agent_name"].startswith("codex-"))
        envelope=adapter.prompt_owned.call_args.kwargs["envelope"].text
        self.assertIn(summary,envelope); self.assertIn("Implement robust loading",envelope); self.assertIn("SOLID-CONTEXT",envelope); self.assertIn("EXPLICIT-CONTEXT",envelope); self.assertNotIn("HIDDEN-CONTEXT",envelope)
        self.assertIn("结果证据默认拒绝",envelope); self.assertIn("Agent memory",envelope)
        self.assertIn("/srv/main",envelope); self.assertIn('"cross_experiment_context":"excluded"',envelope)

    def test_run_implementation_uses_inherited_workspace_remote_repo(self):
        self.store.create_object(object_id="R-code",object_type="run",project_id="PROJECT-test")
        self.store.create_herdr_launch_request(object_id="HLR-run-code",project_id="PROJECT-test",target_object_id="R-code",agent_kind="pi",task_type="run_implementation",task_summary="Implement the approved Run design")
        self.store.transition_herdr_launch_request("HLR-run-code",expected_revision=1,status="awaiting_approval"); self.store.transition_herdr_launch_request("HLR-run-code",expected_revision=2,status="approved")
        capability={"managed":True,"cli_available":True,"pi_supported":True,"probe_status":"available","access":"discovery_only"}
        self.store.authorize_herdr_execution(execution_id="HEX-run-code",project_id="PROJECT-test",launch_request_id="HLR-run-code",expected_request_revision=3,capability=capability)
        tool=self.root/".survey-tool"
        (tool/"experiments.json").write_text(json.dumps([{"id":"E-code","workspace_id":"W-code"}]))
        (tool/"runs.json").write_text(json.dumps([{"id":"R-code","experiment_id":"E-code","workspace_id":""}]))
        (tool/"execution-outbox.json").write_text(json.dumps({"items":[]}))
        (tool/"workspaces.json").write_text(json.dumps([{"id":"W-code","server_id":"S-code","remote_repo":"/srv/run-repo","code_development":{"mode":"remote"}}]))
        (tool/"servers.json").write_text(json.dumps([{"id":"S-code","ssh_host":"user@gpu"}]))
        adapter=mock.Mock(); adapter.start_remote_owned.side_effect=lambda **kwargs:OwnershipAttestation(agent_name=kwargs["agent_name"],pane_id="private-pane"); adapter.prompt_owned.return_value=PromptTurnResult(agent_status="done")
        result=herdr_executor.run_start_owned(self.root,"HEX-run-code",environ={"HERDR_ENV":"1"},capability_getter=lambda:capability,adapter=adapter)
        self.assertEqual(result["state"],"completed"); self.assertTrue(result["checks"]["remote_repo_context"]); self.assertTrue(result["checks"]["remote_tmux_context"])
        adapter.start_owned.assert_not_called(); call=adapter.start_remote_owned.call_args.kwargs
        self.assertEqual(call["ssh_host"],"user@gpu"); self.assertEqual(call["remote_repo"],"/srv/run-repo")

    def test_start_owned_persists_private_attestation_and_safe_output(self):
        output=io.StringIO(); adapter=mock.Mock(); adapter.start_owned.side_effect=lambda **kwargs: OwnershipAttestation(agent_name=kwargs["agent_name"],pane_id="private-pane"); adapter.prompt_owned.return_value=PromptTurnResult(agent_status="done")
        with mock.patch.dict(os.environ,{"HERDR_ENV":"1"},clear=True),mock.patch("survey_tool.v2.herdr_executor.herdr_capability",return_value=self.capability),mock.patch("survey_tool.v2.herdr_executor.HerdrAdapter",return_value=adapter),mock.patch("survey_tool.v2.store.secrets.token_urlsafe",return_value="RAW-START-LEASE"),redirect_stdout(output):
            code=herdr_executor.main(["--project",str(self.root),"--execution","HEX-cli","--once","--start-owned"])
        self.assertEqual(code,0); payload=json.loads(output.getvalue()); self.assertEqual(payload["state"],"completed"); self.assertTrue(payload["checks"]["prompt_submitted"]); self.assertTrue(payload["checks"]["prompt_settled"])
        self.assertEqual(set(payload),{"execution_id","state","checks"}); self.assertNotIn("RAW-START-LEASE",output.getvalue()); self.assertNotIn("private-pane",output.getvalue()); self.assertNotIn(str(self.root),output.getvalue())
        call=adapter.start_owned.call_args.kwargs; self.assertEqual(call["project_root"],str(self.root)); self.assertRegex(call["agent_name"],r"^[a-z][a-z0-9_-]{0,31}$")
        self.assertEqual(call["agent_kind"],"codex"); self.assertEqual(call["topology"],"new_tab")
        self.assertEqual(call["tab_label"],"Codex · Q-cli · 分析"); self.assertEqual(call["session_name"],"Q-cli · 分析")
        prompt_call=adapter.prompt_owned.call_args.kwargs; self.assertEqual(prompt_call["agent_name"],call["agent_name"]); self.assertIn("Review safe evidence",prompt_call["envelope"].text)
        execution=self.store.get_herdr_execution("HEX-cli"); self.assertEqual(execution["state"],"completed"); self.assertEqual(execution["internal_agent_name"],call["agent_name"]); self.assertNotIn("private-pane",repr(execution)); self.assertEqual(execution["lease_token_hash"],"")
        import server
        public=server.public_herdr_execution(execution); self.assertNotIn("internal_agent_name",public); self.assertNotIn("lease_token_hash",public); self.assertNotIn("lease_owner",public)
        events=self.store.list_events("HEX-cli"); self.assertNotIn(call["agent_name"],repr(events)); self.assertNotIn("private-pane",repr(events))

    def test_prompt_failure_is_attention_and_never_retried(self):
        output=io.StringIO(); adapter=mock.Mock(); adapter.start_owned.side_effect=lambda **kwargs: OwnershipAttestation(agent_name=kwargs["agent_name"],pane_id="private-pane"); adapter.prompt_owned.side_effect=HerdrStartError("prompt failed",split_succeeded=True,failure_class="prompt_timeout")
        with mock.patch.dict(os.environ,{"HERDR_ENV":"1"},clear=True),mock.patch("survey_tool.v2.herdr_executor.herdr_capability",return_value=self.capability),mock.patch("survey_tool.v2.herdr_executor.HerdrAdapter",return_value=adapter),redirect_stdout(output):
            code=herdr_executor.main(["--project",str(self.root),"--execution","HEX-cli","--once","--start-owned"])
        self.assertEqual(code,1); payload=json.loads(output.getvalue()); self.assertEqual(payload["state"],"attention_required"); self.assertEqual(payload["checks"]["failure_class"],"prompt_timeout")
        adapter.prompt_owned.assert_called_once(); self.assertNotIn("private-pane",output.getvalue()); self.assertNotIn("Review safe evidence",output.getvalue())
        execution=self.store.get_herdr_execution("HEX-cli"); self.assertEqual(execution["state"],"attention_required"); self.assertEqual(execution["lease_token_hash"],"")

    def test_start_owned_failure_after_split_requires_attention_without_cleanup(self):
        output=io.StringIO(); adapter=mock.Mock(); adapter.start_owned.side_effect=HerdrStartError("start failed",split_succeeded=True)
        with mock.patch.dict(os.environ,{"HERDR_ENV":"1"},clear=True),mock.patch("survey_tool.v2.herdr_executor.herdr_capability",return_value=self.capability),mock.patch("survey_tool.v2.herdr_executor.HerdrAdapter",return_value=adapter),redirect_stdout(output):
            code=herdr_executor.main(["--project",str(self.root),"--execution","HEX-cli","--once","--start-owned"])
        self.assertEqual(code,1); payload=json.loads(output.getvalue()); self.assertEqual(payload["state"],"attention_required"); self.assertEqual(set(payload),{"execution_id","state","checks"})
        self.assertNotIn("pane",output.getvalue().lower()); self.assertNotIn(str(self.root),output.getvalue()); adapter.start_owned.assert_called_once()
        execution=self.store.get_herdr_execution("HEX-cli"); self.assertEqual(execution["state"],"attention_required"); self.assertEqual(execution["internal_agent_name"],""); self.assertTrue(execution["safe_runtime"]["split_succeeded"]); self.assertEqual(execution["lease_token_hash"],"")


if __name__ == "__main__": unittest.main()
