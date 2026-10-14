import datetime as dt
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import server
import survey_tool.experiments as experiments
import survey_tool.managed_execution as managed_execution
from survey_tool import steward_runtime
from survey_tool.v2.herdr_adapter import AgentConsoleResult, OwnershipAttestation, PromptTurnResult


class StewardRuntimeTest(unittest.TestCase):
    def test_each_handoff_uses_a_unique_private_agent_name(self):
        first=steward_runtime._new_steward_agent_name("002","auth","dispatch-1")
        second=steward_runtime._new_steward_agent_name("002","auth","dispatch-1")
        self.assertNotEqual(first,second)
        self.assertRegex(first,r"^steward-002-[a-f0-9]{10}$")
        self.assertLessEqual(len(first),32)

    def test_long_run_id_produces_bounded_recognizable_herdr_labels(self):
        run={"id":"E010-R-001-fixed-head-stability-and-heldout-localization","variant":"fixed head stability and heldout localization with a very long suffix"}
        display=steward_runtime._steward_display(run,"steward-e010-1234567890")
        self.assertLessEqual(len(display["tab_label"]),80); self.assertLessEqual(len(display["session_name"]),80)
        self.assertIn("E010-R-001",display["tab_label"]); self.assertEqual(display["agent_name"],"steward-e010-1234567890")

    def test_handoff_returns_copy_only_command_and_starts_nothing(self):
        root=Path(tempfile.mkdtemp(prefix="steward-handoff-")); run={"id":"R-1","updated":"u1","workflow_version":2,"workflow_stage":"ready_to_run","review_status":"approved","execution_authorized_at":"auth"}
        stale={"run_id":"R-1","phase":"attention_required","error_class":"old_failure","finished_at":"old"}
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(experiments,"run_review_status",return_value="approved"), mock.patch.object(experiments,"ensure_authorization_dispatch",return_value={"queued":True,"dispatch":{"dispatch_id":"D-1","status":"queued"}}), mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{"R-1":stale}}), mock.patch.object(steward_runtime,"_update_runtime") as update, mock.patch.object(steward_runtime,"start_steward_background") as started:
            result=steward_runtime.prepare_steward_handoff(root,"R-1","u1")
        self.assertFalse(result["execution_started"]); self.assertFalse(result["herdr_invoked"]); self.assertFalse(result["lease_exposed"]); started.assert_not_called()
        self.assertIn("HERDR_ENV=1",result["handoff_command"]); self.assertIn("--start-agent",result["handoff_command"]); self.assertIn("--run R-1",result["handoff_command"]); self.assertNotIn("token",result["handoff_command"].lower())
        self.assertEqual(result["supervisor_phase"],"handoff_ready"); self.assertEqual(update.call_args.kwargs["phase"],"handoff_ready"); self.assertEqual(update.call_args.kwargs["error_class"],""); self.assertEqual(update.call_args.kwargs["finished_at"],"")

    def test_trial_handoff_command_is_bound_to_visible_plan_fingerprint(self):
        root=Path(tempfile.mkdtemp(prefix="steward-trial-handoff-")); plan={"contract":"survey-tool.run-trial-plan/v1","planning_mode":"ai_planned","request":"plan useful trials","trial_budget":6,"axes":[],"trials":[],"concurrency":2,"max_retries":1}
        run={"id":"R-1","updated":"u1","workflow_version":2,"workflow_stage":"ready_to_run","review_status":"approved","execution_authorized_at":"auth","trial_plan":plan}
        patches=(mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}),mock.patch.object(experiments,"run_review_status",return_value="approved"),mock.patch.object(experiments,"ensure_authorization_dispatch",return_value={"queued":True,"dispatch":{"dispatch_id":"D-1","status":"queued"}}),mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{}}),mock.patch.object(steward_runtime,"_update_runtime"))
        with patches[0],patches[1],patches[2],patches[3],patches[4]: result=steward_runtime.prepare_steward_handoff(root,"R-1","u1")
        fingerprint=result["trial_plan_fingerprint"]
        self.assertRegex(fingerprint,r"^sha256:[0-9a-f]{64}$"); self.assertIn(f"--expected-trial-plan {fingerprint}",result["handoff_command"]); self.assertEqual(result["trial_budget"],6)
        stale={**plan,"trial_budget":7}
        self.assertNotEqual(steward_runtime._trial_plan_fingerprint(stale),fingerprint)

    def test_background_start_rejects_stale_trial_plan_before_agent_creation(self):
        root=Path(tempfile.mkdtemp(prefix="steward-stale-trial-")); run={"id":"R-1","updated":"u1","workflow_version":2,"workflow_stage":"ready_to_run","review_status":"approved","execution_authorized_at":"auth","trial_plan":{"contract":"survey-tool.run-trial-plan/v1","request":"new"}}
        launcher=mock.Mock()
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(experiments,"run_review_status",return_value="approved"):
            with self.assertRaisesRegex(RuntimeError,"trial_plan_version_conflict"): steward_runtime.start_steward_background(root,"R-1","u1",launcher=launcher,capability_getter=lambda:{"managed":True,"cli_available":True,"pi_supported":True},expected_trial_plan="sha256:"+"0"*64)
        launcher.assert_not_called()

    def test_handoff_directly_snapshots_draft_without_review_ceremony(self):
        root=Path(tempfile.mkdtemp(prefix="steward-direct-")); draft={"id":"R-1","updated":"u1","workflow_version":2,"workflow_stage":"code_planning","review_status":"draft"}; ready={**draft,"updated":"u2","workflow_stage":"ready_to_run","review_status":"approved","execution_authorized_at":"auth"}
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[draft]}), mock.patch.object(experiments,"run_review_status",side_effect=lambda run:run.get("review_status","draft")), mock.patch.object(experiments,"prepare_direct_steward_run",return_value={"run":ready,"dispatch":{"dispatch_id":"D-1","status":"queued"}}) as direct, mock.patch.object(experiments,"ensure_authorization_dispatch",return_value={"queued":True,"dispatch":{"dispatch_id":"D-1","status":"queued"}}), mock.patch.object(steward_runtime,"steward_status",return_value={"supervisor_active":False,"dispatch":{}}), mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{}}), mock.patch.object(steward_runtime,"_update_runtime"):
            result=steward_runtime.prepare_steward_handoff(root,"R-1","u1")
        direct.assert_called_once_with(root,"R-1","u1","human:web-v2"); self.assertIn("--expected-updated u2",result["handoff_command"]); self.assertFalse(result["execution_started"])

    def test_handoff_does_not_clear_failed_or_consumed_dispatch(self):
        root=Path(tempfile.mkdtemp(prefix="steward-handoff-blocked-")); run={"id":"R-1","updated":"u1","workflow_version":2,"workflow_stage":"ready_to_run","review_status":"approved","execution_authorized_at":"auth"}
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(experiments,"run_review_status",return_value="approved"), mock.patch.object(experiments,"ensure_authorization_dispatch",return_value={"queued":False,"needs_attention":True,"error":"执行授权已消耗，请重新授权"}), mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{}}), mock.patch.object(steward_runtime,"_update_runtime") as update:
            with self.assertRaisesRegex(ValueError,"重新授权"): steward_runtime.prepare_steward_handoff(root,"R-1","u1")
        update.assert_not_called()

    def test_handoff_replaces_failed_dispatch_even_when_run_stage_is_ready(self):
        root=Path(tempfile.mkdtemp(prefix="steward-handoff-failed-attempt-")); run={"id":"R-1","updated":"u1","workflow_version":2,"workflow_stage":"ready_to_run","review_status":"approved","execution_authorized_at":"auth"}; ready={**run,"updated":"u2"}
        observed={"supervisor_active":False,"dispatch":{"dispatch_id":"D-old","status":"failed"}}
        restarted={"run":ready,"dispatch":{"dispatch_id":"D-new","status":"queued"}}
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(experiments,"run_review_status",return_value="approved"), mock.patch.object(experiments,"restart_failed_run_execution",return_value=restarted) as restart, mock.patch.object(experiments,"ensure_authorization_dispatch") as ensure, mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{}}), mock.patch.object(steward_runtime,"steward_status",return_value=observed), mock.patch.object(steward_runtime,"_update_runtime") as update:
            result=steward_runtime.prepare_steward_handoff(root,"R-1","u1")
        restart.assert_called_once_with(root,"R-1","u1","human:web-v2:auto-restart"); ensure.assert_not_called()
        self.assertIn("--expected-updated u2",result["handoff_command"]); self.assertIn("D-new",update.call_args.kwargs["dispatch_id"]); self.assertIn("调研仓库",update.call_args.kwargs["message"])

    def test_new_attempt_is_not_blocked_by_old_live_pi_and_clears_ownership(self):
        root=Path(tempfile.mkdtemp(prefix="steward-handoff-old-pi-")); run={"id":"R-1","updated":"u2","workflow_version":2,"workflow_stage":"ready_to_run","review_status":"approved","execution_authorized_at":"auth"}
        runtime={"phase":"agent_running","runtime_kind":"herdr_pi","dispatch_id":"D-old","internal_agent_name":"old-agent","internal_pane_id":"old-pane"}
        observed={"supervisor_active":False,"dispatch":{"dispatch_id":"D-new","status":"queued"},"can_start":True}
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(experiments,"run_review_status",return_value="approved"), mock.patch.object(experiments,"ensure_authorization_dispatch",return_value={"queued":True,"dispatch":{"dispatch_id":"D-new","status":"queued"}}), mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{"R-1":runtime}}), mock.patch.object(steward_runtime,"steward_status",return_value=observed), mock.patch.object(steward_runtime,"_update_runtime") as update:
            result=steward_runtime.prepare_steward_handoff(root,"R-1","u2")
        self.assertIn("--start-agent",result["handoff_command"])
        self.assertEqual(update.call_args.kwargs["dispatch_id"],"D-new"); self.assertEqual(update.call_args.kwargs["internal_agent_name"],""); self.assertEqual(update.call_args.kwargs["internal_pane_id"],""); self.assertEqual(update.call_args.kwargs["agent_status"],"superseded")

    def test_status_does_not_attach_old_pi_to_new_dispatch(self):
        run={"id":"R-1","workflow_version":2,"workflow_stage":"ready_to_run","review_status":"approved","execution_authorized_at":"auth"}
        runtime={"phase":"agent_running","runtime_kind":"herdr_pi","dispatch_id":"D-old"}; dispatch={"dispatch_id":"D-new","status":"queued","authorization_timestamp":"auth"}
        status=steward_runtime._status_for_run(run,runtime,dispatch,experiments,agent_active=True)
        self.assertFalse(status["supervisor_active"]); self.assertTrue(status["can_start"])

    def test_handoff_recovers_settled_owned_pi_prestart_claim(self):
        root=Path(tempfile.mkdtemp(prefix="steward-handoff-recover-")); run={"id":"R-1","updated":"u1","workflow_version":2,"workflow_stage":"ready_to_run","review_status":"approved","execution_authorized_at":"auth"}
        runtime={"run_id":"R-1","phase":"agent_running","runtime_kind":"herdr_pi","internal_agent_name":"private-agent"}
        observed={"supervisor_active":False,"supervisor":{"agent_status":"done"},"dispatch":{"dispatch_id":"D-1","status":"acknowledged"},"can_recover":False}
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(experiments,"run_review_status",return_value="approved"), mock.patch.object(experiments,"recover_abandoned_steward_claim") as recover, mock.patch.object(experiments,"ensure_authorization_dispatch",return_value={"queued":True,"dispatch":{"dispatch_id":"D-1","status":"queued"}}), mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{"R-1":runtime}}), mock.patch.object(steward_runtime,"steward_status",return_value=observed), mock.patch.object(steward_runtime,"_update_runtime"):
            result=steward_runtime.prepare_steward_handoff(root,"R-1","u1")
        recover.assert_called_once_with(root,"D-1","owned_agent_settled"); self.assertIn("--start-agent",result["handoff_command"])

    def test_handoff_allows_expired_running_attempt_to_open_a_new_pi(self):
        root=Path(tempfile.mkdtemp(prefix="steward-handoff-reattach-")); run={"id":"R-1","updated":"u1","workflow_version":2,"workflow_stage":"failed","review_status":"approved","execution_authorized_at":"auth"}
        observed={"supervisor_active":False,"supervisor":{"agent_status":"done"},"dispatch":{"dispatch_id":"dispatch-1234567890abcdef12345678","status":"running"},"can_resume":True}
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(experiments,"run_review_status",return_value="approved"), mock.patch.object(experiments,"ensure_authorization_dispatch") as ensure, mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{}}), mock.patch.object(steward_runtime,"steward_status",return_value=observed), mock.patch.object(steward_runtime,"_update_runtime") as update:
            result=steward_runtime.prepare_steward_handoff(root,"R-1","u1")
        ensure.assert_not_called(); self.assertIn("--start-agent",result["handoff_command"]); self.assertIn("reattach",update.call_args.kwargs["message"])

    def test_force_restart_handoff_revokes_controller_but_starts_nothing(self):
        root=Path(tempfile.mkdtemp(prefix="steward-force-handoff-")); dispatch={"dispatch_id":"dispatch-1234567890abcdef12345678","status":"running"}
        with mock.patch.object(experiments,"force_expire_managed_steward_lease",return_value={"revoked":True,"execution_restarted":False,"dispatch":dispatch}) as revoke, mock.patch.object(steward_runtime,"_update_runtime") as update:
            result=steward_runtime.force_restart_steward_handoff(root,"R-1","u1")
        revoke.assert_called_once_with(root,"R-1","u1","human:web-v2"); self.assertFalse(result["execution_started"]); self.assertFalse(result["execution_restarted"]); self.assertFalse(result["herdr_invoked"]); self.assertIn("--start-agent",result["handoff_command"]); self.assertNotIn("token",str(result).lower().replace("lease_exposed","")); self.assertIn("撤销旧 Pi",update.call_args.kwargs["message"])

    def test_background_start_creates_owned_pi_and_does_not_touch_ssh(self):
        root=Path(tempfile.mkdtemp(prefix="steward-start-")); run={"id":"R-1","updated":"u1","workflow_version":2,"workflow_stage":"ready_to_run","review_status":"approved","execution_authorized_at":"auth","trial_plan":{"contract":"survey-tool.run-trial-plan/v1","planning_mode":"ai_planned","request":"choose useful settings","trial_budget":6,"axes":[],"trials":[],"concurrency":2,"max_retries":1}}
        class Adapter:
            def __init__(self): self.start_call=None; self.prompt_call=None
            def start_owned(self,**kwargs): self.start_call=kwargs; return OwnershipAttestation(kwargs["agent_name"],"private-pane")
            def prompt_owned_async(self,**kwargs): self.prompt_call=kwargs; return PromptTurnResult("working")
        adapter=Adapter()
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(experiments,"run_review_status",return_value="approved"), mock.patch.object(experiments,"ensure_authorization_dispatch",return_value={"queued":True,"dispatch":{"dispatch_id":"D-1"}}), mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{}}), mock.patch.object(steward_runtime,"_update_runtime") as update, mock.patch.object(steward_runtime,"steward_status",return_value={"run_id":"R-1","lease_exposed":False,"prompt_used":False}), mock.patch.object(managed_execution,"_ssh") as ssh:
            result=steward_runtime.start_steward_background(root,"R-1","u1",launcher=adapter,capability_getter=lambda:{"managed":True,"cli_available":True,"pi_supported":True})
        self.assertTrue(result["worker_started"]); self.assertTrue(result["agent_created"]); self.assertEqual(adapter.start_call["agent_kind"],"pi"); self.assertEqual(adapter.start_call["topology"],"new_tab"); self.assertEqual(adapter.prompt_call["agent_name"],adapter.start_call["agent_name"]); self.assertIn("survey_run_execution",adapter.prompt_call["envelope"].text); self.assertIn('"planning_mode":"ai_planned"',adapter.prompt_call["envelope"].text); self.assertIn("trial_budget",adapter.prompt_call["envelope"].text); self.assertEqual(update.call_args_list[0].kwargs["phase"],"preparing"); self.assertEqual(update.call_args_list[-1].kwargs["runtime_kind"],"herdr_pi"); ssh.assert_not_called()

    def test_background_resume_prompts_new_pi_to_reattach_not_restart(self):
        root=Path(tempfile.mkdtemp(prefix="steward-resume-")); did="dispatch-1234567890abcdef12345678"
        run={"id":"R-1","updated":"u1","workflow_version":2,"workflow_stage":"failed","review_status":"approved","execution_authorized_at":"auth","purpose":"resume it","experiment_id":"E-1"}
        class Adapter:
            def start_owned(self,**kwargs): return OwnershipAttestation(kwargs["agent_name"],"private-pane")
            def prompt_owned_async(self,**kwargs): self.envelope=kwargs["envelope"]; return PromptTurnResult("working")
        adapter=Adapter(); observed={"supervisor_active":False,"can_resume":True,"dispatch":{"dispatch_id":did,"status":"running"},"lease_exposed":False,"prompt_used":False}
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run],"experiments":[{"id":"E-1","title":"Exp","objective":"Objective","workspace_id":"W-1"}],"workspaces":[{"id":"W-1","server_id":"S-1","remote_repo":"/srv/repo"}]}), mock.patch.object(experiments,"run_review_status",return_value="approved"), mock.patch.object(experiments,"ensure_authorization_dispatch") as ensure, mock.patch.object(steward_runtime,"steward_status",return_value=observed), mock.patch.object(steward_runtime,"_update_runtime"):
            result=steward_runtime.start_steward_background(root,"R-1","u1",launcher=adapter,capability_getter=lambda:{"managed":True,"cli_available":True,"pi_supported":True})
        ensure.assert_not_called(); self.assertTrue(result["agent_created"]); self.assertIn("interrupted-Steward recovery",adapter.envelope.text); self.assertIn(f'{{action:"reattach",dispatch_id:"{did}"}}',adapter.envelope.text); self.assertIn('"remote_repo":"/srv/repo"',adapter.envelope.text); self.assertIn("不得重新启动第二个远端实验",adapter.envelope.text)

    def test_supervisor_claims_exact_run_and_keeps_lease_private(self):
        dispatch={"dispatch_id":"D-1","run_id":"R-1","requested_agent":"pi","requested_model":""}; calls=[]
        with mock.patch.object(steward_runtime,"_update_runtime"), mock.patch.object(experiments,"experiment_data",return_value={"runs":[{"id":"R-1","workflow_stage":"ready_to_run"}]}), mock.patch.object(experiments,"claim_run_execution",return_value={"claimed":True,"lease_token":"raw-secret","task":{"dispatch":dispatch}}) as claim, mock.patch.object(experiments,"_leased_transition",side_effect=lambda *_args,**_kwargs:calls.append("ack")), mock.patch.object(managed_execution,"managed_execution_start",side_effect=lambda *_args,**_kwargs:calls.append("start")), mock.patch.object(managed_execution,"managed_execution_status",return_value={"completion_candidate":True,"tmux_alive":False}), mock.patch.object(managed_execution,"managed_execution_complete",return_value={"ok":True}):
            result=steward_runtime.run_supervisor(Path("/project"),"R-1",poll_seconds=1,max_cycles=1,sleep=lambda _seconds:None)
        self.assertEqual(calls,["ack","start"]); self.assertEqual(claim.call_args.args[1],"R-1"); self.assertNotIn("token",str(result).lower()); self.assertEqual(result["phase"],"analysis_pending")

    def test_public_status_omits_pid_consumer_and_token(self):
        run={"id":"R-1","workflow_version":2,"workflow_stage":"running","review_status":"approved","execution_authorized_at":"auth"}
        runtime={"run_id":"R-1","phase":"running","pid":os.getpid(),"consumer":"private","lease_token":"raw","message":"safe"}
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{"R-1":runtime}}), mock.patch.object(experiments,"_outbox_read",return_value={"items":[{"run_id":"R-1","status":"running","lease_token":"secret"}]}):
            result=steward_runtime.steward_status(Path("/project"),"R-1")
        self.assertTrue(result["supervisor_active"]); self.assertNotIn("pid",result["supervisor"]); self.assertNotIn("consumer",result["supervisor"]); self.assertNotIn("token",str(result).lower().replace("lease_exposed",""))

    def test_project_monitor_lists_safe_status_without_remote_probe(self):
        runs=[{"id":"R-1","experiment_id":"E-1","variant":"Trial","workflow_version":2,"workflow_stage":"running","review_status":"approved","execution_authorized_at":"auth"},{"id":"R-old","experiment_id":"E-1","workflow_version":2,"workflow_stage":"analysis_pending"}]
        runtime={"run_id":"R-1","phase":"running","pid":os.getpid(),"lease_token":"secret","message":"watching"}
        dispatch={"run_id":"R-1","status":"running","managed_execution":{"ssh_host":"private","tmux_session":"private","status_observation":{"tmux_alive":True}}}
        old={"run_id":"R-old","status":"completed"}
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":runs}), mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{"R-1":runtime}}), mock.patch.object(experiments,"_outbox_read",return_value={"items":[dispatch,old]}):
            result=steward_runtime.list_steward_statuses(Path("/project"))
        self.assertEqual(result["summary"]["active"],1); self.assertEqual(len(result["items"]),1); self.assertFalse(result["remote_probe_performed"]); self.assertEqual(result["items"][0]["run_label"],"Trial"); self.assertNotIn("secret",str(result)); self.assertNotIn("private",str(result))

    def test_monitor_ignores_authorized_dispatch_without_steward_enrollment(self):
        run={"id":"R-approved","workflow_version":2,"workflow_stage":"ready_to_run","review_status":"approved","execution_authorized_at":"auth"}; dispatch={"run_id":"R-approved","status":"blocked","last_error":"policy"}
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{}}), mock.patch.object(experiments,"_outbox_read",return_value={"items":[dispatch]}):
            result=steward_runtime.list_steward_statuses(Path("/project"))
        self.assertEqual(result["items"],[]); self.assertEqual(result["summary"]["total"],0)

    def test_console_captures_only_owned_active_tmux(self):
        run={"id":"R-1"}; runtime={"phase":"running","pid":os.getpid()}; dispatch={"run_id":"R-1","status":"running","managed_execution":{"ssh_host":"server","tmux_session":"steward-r1"}}
        runner=mock.Mock()
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{"R-1":runtime}}), mock.patch.object(experiments,"_outbox_read",return_value={"items":[dispatch]}), mock.patch.object(managed_execution,"_ssh",return_value={"returncode":0,"stdout":"\x1b[31mtraining step 4\x1b[0m\n"}) as capture:
            result=steward_runtime.steward_console(Path("/project"),"R-1",runner=runner)
        self.assertTrue(result["available"]); self.assertEqual(result["output"],"training step 4\n"); self.assertNotIn("server",str(result)); self.assertNotIn("steward-r1",str(result)); self.assertEqual(capture.call_args.args[2],["tmux","capture-pane","-p","-J","-S","-400","-t","steward-r1"])

    def test_console_reads_owned_herdr_pi_without_exposing_identity(self):
        run={"id":"R-1"}; runtime={"phase":"agent_running","runtime_kind":"herdr_pi","internal_agent_name":"private-agent","internal_pane_id":"private-pane"}
        adapter=mock.Mock(); adapter.read_owned.return_value=AgentConsoleResult("Pi is checking epoch 3\n","working",False)
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{"R-1":runtime}}):
            result=steward_runtime.steward_console(Path("/project"),"R-1",adapter=adapter)
        self.assertEqual(result["source"],"herdr_pi"); self.assertEqual(result["agent_status"],"working"); self.assertIn("epoch 3",result["output"]); self.assertNotIn("private-agent",str(result)); self.assertNotIn("private-pane",str(result)); adapter.read_owned.assert_called_once_with(agent_name="private-agent",lines=400)

    def test_settled_pi_without_claim_is_recoverable_not_permanently_active(self):
        run={"id":"R-1","experiment_id":"E-1","workflow_version":2,"workflow_stage":"ready_to_run","review_status":"approved","execution_authorized_at":"auth"}
        runtime={"phase":"agent_running","runtime_kind":"herdr_pi","internal_agent_name":"private-agent","agent_status":"working"}; dispatch={"run_id":"R-1","status":"queued"}
        adapter=mock.Mock(); adapter.owned_status.return_value="done"
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{"R-1":runtime}}), mock.patch.object(experiments,"_outbox_read",return_value={"items":[dispatch]}):
            result=steward_runtime.steward_status(Path("/project"),"R-1",adapter=adapter)
        self.assertFalse(result["supervisor_active"]); self.assertTrue(result["needs_attention"]); self.assertTrue(result["can_recover"]); self.assertEqual(result["supervisor"]["agent_status"],"done")
        adapter.owned_status.assert_called_once_with(agent_name="private-agent")

    def test_failed_dispatch_never_hides_restart_behind_live_old_pi(self):
        run={"id":"R-1","experiment_id":"E-1","workflow_version":2,"workflow_stage":"failed","review_status":"approved","execution_authorized_at":"auth"}
        runtime={"phase":"agent_running","runtime_kind":"herdr_pi","internal_agent_name":"old-agent","message":"old Pi still open"}; dispatch={"dispatch_id":"D-1","run_id":"R-1","authorization_timestamp":"auth","status":"failed"}
        adapter=mock.Mock(); adapter.owned_status.return_value="working"
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{"R-1":runtime}}), mock.patch.object(experiments,"_outbox_read",return_value={"items":[dispatch]}):
            current=steward_runtime.steward_status(Path("/project"),"R-1",adapter=adapter)
        self.assertFalse(current["supervisor_active"]); self.assertTrue(current["needs_attention"]); self.assertTrue(current["can_restart"]); self.assertEqual(current["workflow_stage"],"failed")

    def test_changes_requested_projects_old_steward_as_revision_open_not_blocker(self):
        run={"id":"R-1","experiment_id":"E-1","workflow_version":2,"workflow_stage":"failed","review_status":"changes_requested"}
        runtime={"phase":"handoff_ready","runtime_kind":"herdr_pi","dispatch_id":"D-old","message":"stale retry message","agent_status":"superseded"}
        dispatch={"dispatch_id":"D-old","run_id":"R-1","status":"failed","retryable":False}
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{"R-1":runtime}}), mock.patch.object(experiments,"_outbox_read",return_value={"items":[dispatch]}):
            current=steward_runtime.steward_status(Path("/project"),"R-1")
        self.assertTrue(current["revision_open"]); self.assertFalse(current["needs_attention"]); self.assertFalse(current["supervisor_active"]); self.assertFalse(current["can_restart"]); self.assertEqual(current["supervisor"]["phase"],"revision_open"); self.assertNotIn("D-old",current["supervisor"].values())

    def test_linked_remote_running_evidence_overrides_stale_failed_display_only(self):
        run={"id":"R-1","experiment_id":"E-1","workflow_version":2,"workflow_stage":"failed","review_status":"approved","execution_authorized_at":"auth","execution_dispatch_id":"D-1"}
        runtime={"phase":"agent_running","runtime_kind":"herdr_pi","internal_agent_name":"private-agent"}; dispatch={"dispatch_id":"D-1","run_id":"R-1","authorization_timestamp":"auth","status":"running","managed_execution":{"started_evidence":"tmux_new_session_ok"}}
        adapter=mock.Mock(); adapter.owned_status.return_value="working"
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{"R-1":runtime}}), mock.patch.object(experiments,"_outbox_read",return_value={"items":[dispatch]}):
            current=steward_runtime.steward_status(Path("/project"),"R-1",adapter=adapter)
        self.assertTrue(current["remote_execution_active"]); self.assertFalse(current["remote_tmux_observed"]); self.assertTrue(current["canonical_stage_stale"]); self.assertEqual(current["workflow_stage"],"running"); self.assertFalse(current["state_conflict"])
        run["execution_dispatch_id"]="D-new"
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{"R-1":runtime}}), mock.patch.object(experiments,"_outbox_read",return_value={"items":[dispatch]}):
            conflict=steward_runtime.steward_status(Path("/project"),"R-1",adapter=adapter)
        self.assertFalse(conflict["remote_execution_active"]); self.assertTrue(conflict["state_conflict"]); self.assertTrue(conflict["needs_attention"])

    def test_remote_tmux_label_requires_a_timestamped_status_observation(self):
        run={"id":"R-1","experiment_id":"E-1","workflow_version":2,"workflow_stage":"running","review_status":"approved","execution_authorized_at":"auth","execution_dispatch_id":"D-1"}
        runtime={"phase":"agent_running","runtime_kind":"herdr_pi","internal_agent_name":"private-agent"}
        managed={"started_evidence":"tmux_new_session_ok","status_observation":{"tmux_alive":True,"observed_at":"2026-08-24T12:00:00"}}
        dispatch={"dispatch_id":"D-1","run_id":"R-1","authorization_timestamp":"auth","status":"running","managed_execution":managed}
        adapter=mock.Mock(); adapter.owned_status.return_value="working"
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{"R-1":runtime}}), mock.patch.object(experiments,"_outbox_read",return_value={"items":[dispatch]}):
            result=steward_runtime.steward_status(Path("/project"),"R-1",adapter=adapter)
        self.assertTrue(result["remote_tmux_observed"]); self.assertEqual(result["remote_observed_at"],"2026-08-24T12:00:00"); self.assertFalse(result["canonical_stage_stale"])

    def test_interrupted_running_pi_waits_for_lease_then_becomes_resumable(self):
        run={"id":"R-1","experiment_id":"E-1","workflow_version":2,"workflow_stage":"running","review_status":"approved","execution_authorized_at":"auth","execution_dispatch_id":"D-1"}
        runtime={"phase":"agent_running","runtime_kind":"herdr_pi","internal_agent_name":"private-agent"}; adapter=mock.Mock(); adapter.owned_status.return_value="done"
        future=(dt.datetime.now()+dt.timedelta(minutes=2)).isoformat(); dispatch={"dispatch_id":"D-1","run_id":"R-1","authorization_timestamp":"auth","status":"running","lease_expires_at":future,"managed_execution":{"started_evidence":"tmux_new_session_ok"}}
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{"R-1":runtime}}), mock.patch.object(experiments,"_outbox_read",return_value={"items":[dispatch]}):
            waiting=steward_runtime.steward_status(Path("/project"),"R-1",adapter=adapter)
        self.assertTrue(waiting["resume_waiting"]); self.assertFalse(waiting["can_resume"]); self.assertEqual(waiting["resume_available_at"],future)
        dispatch["lease_expires_at"]=(dt.datetime.now()-dt.timedelta(seconds=1)).isoformat()
        with mock.patch.object(experiments,"experiment_data",return_value={"runs":[run]}), mock.patch.object(steward_runtime,"_runtime_rows",return_value={"version":1,"runs":{"R-1":runtime}}), mock.patch.object(experiments,"_outbox_read",return_value={"items":[dispatch]}):
            resumable=steward_runtime.steward_status(Path("/project"),"R-1",adapter=adapter)
        self.assertFalse(resumable["resume_waiting"]); self.assertTrue(resumable["can_resume"])


if __name__=="__main__": unittest.main()
