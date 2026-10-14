#!/usr/bin/env python3
import datetime
import pathlib
import tempfile
import threading
import unittest
import json

import server
import survey_tool.experiments as experiment_domain
import surveyctl
import contextlib
import io
import sys


class ExecutionOutboxTest(unittest.TestCase):
    def setUp(self):
        self.root=pathlib.Path(tempfile.mkdtemp(prefix="survey-outbox-")); (self.root/"state.md").write_text("state: TEST\n",encoding="utf-8")
        server.CFG={"projects_root":str(self.root.parent),"projects":[str(self.root)],"skill_dir":str(pathlib.Path(__file__).parents[1]/"skills/research-survey"),"port":7421}
        server.write_tool_json(self.root,"servers.json",[{"id":"S-01","ssh_host":"test"}])
        server.write_tool_json(self.root,"workspaces.json",[{"id":"W-01","server_id":"S-01","remote_repo":"/repo","remote_worktree_root":"/worktrees","remote_data_root":"/data","remote_experiment_root":"/exp"}])
        server.create_experiment(self.root,{"title":"outbox","objective":"test","workspace_id":"W-01"},"E-001")

    def policy(self,**changes):
        value={"enabled":True,"auto_queue_on_authorize":False,"auto_deliver_on_pi_live":False,"claim_lease_minutes":30,"max_delivery_attempts":5,"notes":"test"}; value.update(changes)
        server.save_execution_dispatch_policy(self.root,"E-001",value); return value

    def authorized(self,rid="R-outbox",artifact=None,auto=False):
        if auto: self.policy(auto_queue_on_authorize=True)
        server.create_run(self.root,"E-001",{"variant":rid,"purpose":"p","workspace_id":"W-01","command":"python run.py","artifact_dir":artifact or f"/exp/E-001/{rid}"},rid)
        server.review_run(self.root,rid,"submit",actor="terminal_pi"); server.review_run(self.root,rid,"approve",actor="human")
        return server.review_run(self.root,rid,"authorize_execution",actor="human")

    def authorized_v2(self,rid):
        server.create_run(self.root,"E-001",{"variant":rid,"purpose":"p","workspace_id":"W-01","command":"python run.py","artifact_dir":f"/exp/E-001/{rid}"},rid)
        server.review_run(self.root,rid,"submit",actor="terminal_pi"); server.review_run(self.root,rid,"approve",actor="human")
        data=server.experiment_data(self.root); run=next(row for row in data["runs"] if row["id"]==rid); run["workflow_version"]=2; run["workflow_stage"]="ready_to_run"; run["approved_spec"]=server._review_snapshot(run)
        server.write_tool_json(self.root,"runs.json",data["runs"]); server.save_run_spec(self.root,run)
        return server.review_run(self.root,rid,"authorize_execution",actor="human")

    def test_auto_queue_idempotency_reauthorize_and_request_changes_cancel(self):
        run=self.authorized(auto=True); result=run["execution_dispatch_enqueue_result"]
        self.assertTrue(result["queued"]); did=result["dispatch"]["dispatch_id"]
        again=server.enqueue_execution(self.root,"R-outbox"); self.assertTrue(again["idempotent"]); self.assertEqual(again["dispatch"]["dispatch_id"],did)
        server.review_run(self.root,"R-outbox","request_changes",requirements="change spec")
        item=server.execution_outbox_public(self.root)["execution_outbox"]["items"][0]; self.assertEqual(item["status"],"cancelled")
        self.assertNotIn("lease_token",item); self.assertNotIn("lease_token_hash",item)

    def test_enqueue_requires_authorization_and_notes_drift_without_blocking(self):
        server.create_run(self.root,"E-001",{"variant":"no auth"},"R-no-auth")
        with self.assertRaisesRegex(ValueError,"未获得执行授权"): server.enqueue_execution(self.root,"R-no-auth")
        self.authorized("R-drift"); data=server.experiment_data(self.root); run=next(x for x in data["runs"] if x["id"]=="R-drift"); run["command"]="python changed.py"; server.write_tool_json(self.root,"runs.json",data["runs"])
        # 批准后改规范不再阻断执行，只在 Run 与 outbox 留痕。
        drift=server.enqueue_execution(self.root,"R-drift")
        self.assertTrue(drift["queued"]); self.assertNotEqual(drift["dispatch"]["status"],"blocked")
        # Workspace 策略违规仍会阻断（这是运行时安全，不是填表门禁）。
        blocked=self.authorized("R-policy",artifact="/tmp/R-policy",auto=True)["execution_dispatch_enqueue_result"]
        self.assertFalse(blocked["queued"]); self.assertEqual(blocked["dispatch"]["status"],"blocked"); self.assertTrue(blocked["needs_attention"])

    def test_first_claim_generates_pending_rule_draft_and_blocks_without_changing_policy(self):
        self.policy(); self.authorized(); queued=server.enqueue_execution(self.root,"R-outbox")
        data=server.experiment_data(self.root); workspace=data["workspaces"][0]
        workspace["rule_input"]={"contract":"survey-tool.workspace-rule-input/v1","original_request":"数据只读，不要联网；代码和实验目录可写；禁止 sudo。","preset":"research_safe","updated_at":"client"}
        before_hash=server.workspace_execution_hash(workspace); server.write_tool_json(self.root,"workspaces.json",data["workspaces"])
        claimed=server.claim_next_execution(self.root,"worker")
        self.assertFalse(claimed["claimed"])
        workspace=server.experiment_data(self.root)["workspaces"][0]; pending=workspace["pending_rule_draft"]
        self.assertEqual(pending["trigger"],"execution_claim"); self.assertEqual(pending["organizer"]["used"],"basic")
        self.assertEqual(pending["original_request"],workspace["rule_input"]["original_request"])
        self.assertEqual(server.workspace_execution_hash(workspace),before_hash)
        item=next(row for row in server._outbox_read(self.root)["items"] if row["dispatch_id"]==queued["dispatch"]["dispatch_id"])
        self.assertEqual(item["status"],"blocked"); self.assertIn("规则尚未确认",item["last_error"])
        bindings=server.environment_bindings(self.root); current=next(row for row in bindings["workspaces"] if row["id"]=="W-01")
        with self.assertRaisesRegex(ValueError,"只能由执行准备阶段生成"):
            server.update_workspace_binding(self.root,"W-01",bindings["workspaces_hash"],{"pending_rule_draft":{"fake":True}})
        with self.assertRaisesRegex(ValueError,"应用同一草稿"):
            server.update_workspace_binding(self.root,"W-01",bindings["workspaces_hash"],{"pending_rule_draft":None})
        profile={"contract":"survey-tool.workspace-rule-profile/v1","original_request":pending["original_request"],"preset":pending["preset"]["id"],"rules":pending["rules"],"warnings":pending["warnings"],"questions":pending["questions"],"updated_at":"client","organizer":pending["organizer"]}
        saved=server.update_workspace_binding(self.root,"W-01",bindings["workspaces_hash"],{"environment_policy":pending["structured_preview"]["environment_policy"],"execution_isolation":pending["structured_preview"]["execution_isolation"],"dataset_bindings":pending["structured_preview"]["dataset_bindings"],"rule_input":workspace["rule_input"],"rule_profile":profile,"pending_rule_draft":None})
        self.assertNotIn("pending_rule_draft",saved["workspace"])

    def test_matching_saved_rule_profile_does_not_block_claim(self):
        self.policy(); self.authorized(); data=server.experiment_data(self.root); workspace=data["workspaces"][0]
        request="数据只读"; workspace["rule_input"]={"contract":"survey-tool.workspace-rule-input/v1","original_request":request,"preset":"research_safe","updated_at":"saved"}; workspace["rule_profile"]={"contract":"survey-tool.workspace-rule-profile/v1","original_request":request,"preset":"research_safe","rules":[],"warnings":[],"questions":[],"updated_at":"saved"}; server.write_tool_json(self.root,"workspaces.json",data["workspaces"])
        server.enqueue_execution(self.root,"R-outbox"); self.assertTrue(server.claim_next_execution(self.root,"worker")["claimed"])

    def test_concurrent_claim_unique_token_consumer_and_state_machine(self):
        self.policy(); self.authorized(); server.enqueue_execution(self.root,"R-outbox")
        barrier=threading.Barrier(3); results=[]
        def claim(name): barrier.wait(); results.append(server.claim_next_execution(self.root,name))
        threads=[threading.Thread(target=claim,args=(f"worker-{i}",)) for i in range(2)]
        for t in threads:t.start()
        barrier.wait()
        for t in threads:t.join()
        winners=[x for x in results if x["claimed"]]; self.assertEqual(len(winners),1)
        winner=winners[0]; token=winner["lease_token"]; item=winner["task"]["dispatch"]; did=item["dispatch_id"]; consumer=item["consumer"]
        with self.assertRaisesRegex(ValueError,"consumer"): server._leased_transition(self.root,did,token,"wrong","acknowledge",{"actual_agent":"codex"})
        with self.assertRaisesRegex(ValueError,"token"): server._leased_transition(self.root,did,"wrong",consumer,"acknowledge",{"actual_agent":"codex"})
        with self.assertRaisesRegex(ValueError,"fallback"): server._leased_transition(self.root,did,token,consumer,"acknowledge",{"actual_agent":"pi"})
        ack=server._leased_transition(self.root,did,token,consumer,"acknowledge",{"actual_agent":"codex","actual_model":"sol","fallback_reason":"configured model differs"}); self.assertEqual(ack["status"],"acknowledged")
        running=server._leased_transition(self.root,did,token,consumer,"running"); self.assertEqual(running["status"],"running")
        run=next(x for x in server.experiment_data(self.root)["runs"] if x["id"]=="R-outbox")
        self.assertTrue(run["execution_authorization_consumed_at"]); self.assertEqual(run["execution_dispatch_id"],did); self.assertEqual(run["execution_dispatch_latest_status"],"running")
        with self.assertRaisesRegex(ValueError,"证据"): server._leased_transition(self.root,did,token,consumer,"complete",{})
        done=server._leased_transition(self.root,did,token,consumer,"complete",{"result_message":"完成并核验"}); self.assertEqual(done["status"],"completed")
        run=next(x for x in server.experiment_data(self.root)["runs"] if x["id"]=="R-outbox")
        self.assertEqual(run["execution_dispatch_latest_status"],"completed"); self.assertEqual(run["execution_dispatch_completion_evidence"]["result_message"],"完成并核验")
        self.assertNotIn("Claim",json.dumps(run,ensure_ascii=False))

    def test_trial_implementation_error_repairs_and_restarts_same_attempt(self):
        rid="R-trial-repair"; manifest={"contract":"survey-tool.run-trial-manifest/v1","trials":[{"id":"T-001","parameters":{"seed":1}}]}
        server.create_run(self.root,"E-001",{"variant":rid,"purpose":"p","workspace_id":"W-01","command":"python run.py","artifact_dir":f"/exp/E-001/{rid}"},rid)
        server.review_run(self.root,rid,"submit",actor="terminal_pi"); server.review_run(self.root,rid,"approve",actor="human")
        data=server.experiment_data(self.root); run=next(row for row in data["runs"] if row["id"]==rid)
        plan=server.build_run_trial_plan("same T-001",None,1,1,"ai_planned",1); plan["campaign_id"]="C-001"
        run.update({"workflow_version":2,"workflow_stage":"ready_to_run","trial_plan":plan,"trial_manifest":manifest,"active_trial_campaign_id":"C-001","trial_campaigns":[{"id":"C-001","status":"ready_to_start","plan":plan,"manifest":manifest}]})
        run["approved_spec"]=server._review_snapshot(run)
        server.write_tool_json(self.root,"runs.json",data["runs"]); server.save_run_spec(self.root,run)
        server.review_run(self.root,rid,"authorize_execution",actor="human")
        queued=server.enqueue_execution(self.root,rid); did=queued["dispatch"]["dispatch_id"]
        first=server.claim_run_execution(self.root,rid,"pi-steward:test"); token=first["lease_token"]
        server._leased_transition(self.root,did,token,"pi-steward:test","acknowledge",{"actual_agent":first["task"]["dispatch"]["requested_agent"],"actual_model":first["task"]["dispatch"].get("requested_model","")})
        server._leased_transition(self.root,did,token,"pi-steward:test","running")

        repaired=server.begin_managed_execution_repair(self.root,did,token,"pi-steward:test","implementation","launcher import typo; fix and focused test")
        self.assertTrue(repaired["same_dispatch"]); self.assertTrue(repaired["approval_preserved"]); self.assertEqual(repaired["repair_attempt"],1)
        current=next(row for row in server.experiment_data(self.root)["runs"] if row["id"]==rid)
        self.assertEqual(current["workflow_stage"],"ready_to_run"); self.assertEqual(current["review_status"],"approved")
        self.assertEqual(current["trial_manifest"],manifest); self.assertEqual(current["trial_campaigns"][0]["status"],"repairing")
        prepared=server.prepare_managed_run_command(self.root,rid,"python run.py","pi-steward:test",manifest)
        self.assertTrue(prepared["idempotent"])
        second=server.claim_run_execution(self.root,rid,"pi-steward:test-2")
        self.assertEqual(second["task"]["dispatch"]["dispatch_id"],did)
        token2=second["lease_token"]
        server._leased_transition(self.root,did,token2,"pi-steward:test-2","acknowledge",{"actual_agent":second["task"]["dispatch"]["requested_agent"],"actual_model":second["task"]["dispatch"].get("requested_model","")})
        server._leased_transition(self.root,did,token2,"pi-steward:test-2","running")
        current=next(row for row in server.experiment_data(self.root)["runs"] if row["id"]==rid)
        self.assertEqual(current["workflow_stage"],"running"); self.assertEqual(current["trial_campaigns"][0]["status"],"running")

    def test_repair_budget_prevents_premature_terminal_fail(self):
        from survey_tool.managed_execution import managed_execution_fail
        rid="R-no-premature-fail"
        policy={"mode":"active","allowed_code_roots":["/repo"],"test_commands":["python -m pytest -q"],"max_repairs":1,"time_budget_minutes":30,"auto_rerun":True,"install_declared_dependencies":False,"dependency_files":[]}
        server.create_run(self.root,"E-001",{"variant":rid,"purpose":"p","workspace_id":"W-01","command":"python run.py","artifact_dir":f"/exp/E-001/{rid}","automation_policy":policy},rid)
        server.review_run(self.root,rid,"submit",actor="terminal_pi"); server.review_run(self.root,rid,"approve",actor="human")
        data=server.experiment_data(self.root); run=next(row for row in data["runs"] if row["id"]==rid); run["workflow_version"]=2; run["workflow_stage"]="ready_to_run"; run["approved_spec"]=server._review_snapshot(run)
        server.write_tool_json(self.root,"runs.json",data["runs"]); server.save_run_spec(self.root,run); server.review_run(self.root,rid,"authorize_execution",actor="human")
        did=server.enqueue_execution(self.root,rid)["dispatch"]["dispatch_id"]; claimed=server.claim_run_execution(self.root,rid,"pi:test"); token=claimed["lease_token"]
        server._leased_transition(self.root,did,token,"pi:test","acknowledge",{"actual_agent":claimed["task"]["dispatch"]["requested_agent"],"actual_model":claimed["task"]["dispatch"].get("requested_model","")}); server._leased_transition(self.root,did,token,"pi:test","running")
        with self.assertRaisesRegex(ValueError,"请调用 repair"):
            managed_execution_fail(self.root,did,token,"pi:test","implementation","one-line syntax error",True)
        current=next(row for row in server.experiment_data(self.root)["runs"] if row["id"]==rid)
        self.assertEqual(current["workflow_stage"],"running")

    def test_human_can_explicitly_mark_current_attempt_failed(self):
        run=server.create_run(self.root,"E-001",{"variant":"manual failure"},"R-human-fail")
        data=server.experiment_data(self.root); current=next(row for row in data["runs"] if row["id"]==run["id"])
        current.update({"workflow_version":2,"workflow_stage":"running","status":"running","execution_dispatch_id":"dispatch-human","execution_dispatch_latest_status":"running"})
        server.write_tool_json(self.root,"runs.json",data["runs"]); server.save_run_spec(self.root,current)
        server.write_tool_json(self.root,"execution-outbox.json",{"schema":server.OUTBOX_SCHEMA,"version":1,"items":[{"dispatch_id":"dispatch-human","run_id":run["id"],"status":"running","consumer":"pi-steward:test","lease_token_hash":"private","lease_expires_at":"2099-01-01T00:00:00","created_at":"2026-01-01T00:00:00","history":[]}]})
        result=server.mark_steward_attempt_failed(self.root,run["id"],current["updated"],"人工核对后确认进程未启动")
        self.assertFalse(result["execution_stopped"]); self.assertFalse(result["remote_process_changed"])
        self.assertEqual(result["dispatch"]["status"],"failed"); self.assertNotIn("token",json.dumps(result).lower())
        updated=next(row for row in server.experiment_data(self.root)["runs"] if row["id"]==run["id"])
        self.assertEqual(updated["workflow_stage"],"failed"); self.assertEqual(updated["execution_dispatch_failure"]["failure_class"],"human_adjudicated")

    def test_ack_same_route_needs_no_fallback_but_different_route_does(self):
        self.policy(); self.authorized(); queued=server.enqueue_execution(self.root,"R-outbox"); claim=server.claim_next_execution(self.root,"worker")
        item=claim["task"]["dispatch"]
        ack=server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"worker","acknowledge",{"actual_agent":item["requested_agent"],"actual_model":item["requested_model"]})
        self.assertEqual(ack["fallback_reason"],"")

        self.authorized("R-other"); other=server.enqueue_execution(self.root,"R-other"); claimed=server.claim_next_execution(self.root,"worker2")
        with self.assertRaisesRegex(ValueError,"fallback"):
            server._leased_transition(self.root,other["dispatch"]["dispatch_id"],claimed["lease_token"],"worker2","acknowledge",{"actual_agent":"different","actual_model":""})

    def test_fallback_actual_success_does_not_whiten_requested_health(self):
        self.policy(); self.authorized(); claim=server.claim_next_execution(self.root,"worker"); item=claim["task"]["dispatch"]
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"worker","acknowledge",{"actual_agent":"pi","actual_model":"","fallback_reason":"codex model unsupported"})
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"worker","running")
        health=server.agent_route_health(self.root); requested=next(x for x in health if x["subject"]=="requested"); actual=next(x for x in health if x["subject"]=="actual")
        self.assertEqual(requested["agent"],item["requested_agent"]); self.assertEqual(requested["last_result"],"unsupported")
        self.assertEqual(actual["agent"],"pi"); self.assertEqual(actual["last_result"],"success")

    def test_route_event_rejects_secret_patterns(self):
        with self.assertRaisesRegex(ValueError,"token"):
            server.record_agent_route_event(self.root,{"route":"local_tool_edit","result":"error","message":"access_token=abc123"})
        with self.assertRaisesRegex(ValueError,"私钥"):
            server.record_agent_route_event(self.root,{"route":"local_tool_edit","result":"error","fallback_reason":"-----BEGIN PRIVATE KEY-----"})
        with self.assertRaisesRegex(ValueError,"token"):
            server.record_agent_route_event(self.root,{"route":"local_tool_edit","result":"error","message":{"nested":{"password":"secret"}}})

    def test_fail_retry_basis_and_lease_expiry_survives_restart(self):
        self.policy(claim_lease_minutes=1); self.authorized(); queued=server.enqueue_execution(self.root,"R-outbox"); claim=server.claim_next_execution(self.root,"worker"); did=queued["dispatch"]["dispatch_id"]
        box=server._outbox_read(self.root); item=next(x for x in box["items"] if x["dispatch_id"]==did); item["lease_expires_at"]=(datetime.datetime.now()-datetime.timedelta(minutes=2)).isoformat(); server.write_tool_json(self.root,"execution-outbox.json",box)
        public=server.execution_outbox_public(self.root)["execution_outbox"]; self.assertEqual(public["items"][0]["status"],"queued")
        recovered=next(row for row in server.experiment_data(self.root)["runs"] if row["id"]=="R-outbox")
        self.assertEqual(recovered["review_status"],"approved"); self.assertTrue(recovered["execution_authorized_at"])
        claim=server.claim_next_execution(self.root,"worker2"); token=claim["lease_token"]
        reclaimed=next(row for row in server.experiment_data(self.root)["runs"] if row["id"]=="R-outbox")
        self.assertEqual(reclaimed["review_status"],"approved"); self.assertTrue(reclaimed["execution_authorized_at"])
        server._leased_transition(self.root,did,token,"worker2","acknowledge",{"actual_agent":"codex","fallback_reason":"model default"})
        failed=server._leased_transition(self.root,did,token,"worker2","fail",{"failure_class":"infra","reason":"GPU unavailable","retryable":True}); self.assertEqual(failed["status"],"failed")
        with self.assertRaises(ValueError): server.retry_execution(self.root,did,"retry","")
        retried=server.retry_execution(self.root,did,"GPU restored","scheduler evidence"); self.assertEqual(retried["status"],"queued")
        # Reading from disk after no in-memory object demonstrates restart persistence.
        self.assertEqual(server._outbox_read(self.root)["items"][0]["dispatch_id"],did)

    def test_running_lease_never_expires_back_to_queue(self):
        self.policy(claim_lease_minutes=1); self.authorized(); queued=server.enqueue_execution(self.root,"R-outbox"); claim=server.claim_next_execution(self.root,"worker"); did=queued["dispatch"]["dispatch_id"]
        server._leased_transition(self.root,did,claim["lease_token"],"worker","acknowledge",{"actual_agent":claim["task"]["dispatch"]["requested_agent"],"actual_model":claim["task"]["dispatch"]["requested_model"]})
        server._leased_transition(self.root,did,claim["lease_token"],"worker","running")
        box=server._outbox_read(self.root); box["items"][0]["lease_expires_at"]=(datetime.datetime.now()-datetime.timedelta(hours=1)).isoformat(); server.write_tool_json(self.root,"execution-outbox.json",box)
        self.assertEqual(server.execution_outbox_public(self.root)["execution_outbox"]["items"][0]["status"],"running")

    def test_failed_after_running_retries_same_consumed_dispatch(self):
        self.policy(); self.authorized_v2("R-outbox"); queued=server.enqueue_execution(self.root,"R-outbox"); claim=server.claim_next_execution(self.root,"worker"); item=claim["task"]["dispatch"]; did=queued["dispatch"]["dispatch_id"]
        server._leased_transition(self.root,did,claim["lease_token"],"worker","acknowledge",{"actual_agent":item["requested_agent"],"actual_model":item["requested_model"]})
        server._leased_transition(self.root,did,claim["lease_token"],"worker","running")
        server._leased_transition(self.root,did,claim["lease_token"],"worker","fail",{"failure_class":"infra","reason":"节点重启","retryable":True})
        server.retry_execution(self.root,did,"节点恢复","调度器事件")
        restored=next(row for row in server.experiment_data(self.root)["runs"] if row["id"]=="R-outbox")
        self.assertEqual(restored["workflow_stage"],"ready_to_run"); self.assertEqual(restored["review_status"],"approved")
        self.assertEqual(restored["execution_dispatch_latest_status"],"queued"); self.assertTrue(restored["execution_authorization_consumed_at"])
        reclaimed=server.claim_next_execution(self.root,"worker2"); self.assertTrue(reclaimed["claimed"]); self.assertEqual(reclaimed["task"]["dispatch"]["dispatch_id"],did)

    def test_retry_refuses_changed_approved_snapshot(self):
        self.policy(); self.authorized_v2("R-drift"); queued=server.enqueue_execution(self.root,"R-drift"); claim=server.claim_next_execution(self.root,"worker",run_id="R-drift"); item=claim["task"]["dispatch"]
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"worker","acknowledge",{"actual_agent":item["requested_agent"],"actual_model":item["requested_model"]}); server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"worker","running")
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"worker","fail",{"failure_class":"environment","reason":"cwd missing","retryable":True})
        data=server.experiment_data(self.root); run=next(row for row in data["runs"] if row["id"]=="R-drift"); run["purpose"]="changed scientific purpose"; server.write_tool_json(self.root,"runs.json",data["runs"])
        with self.assertRaisesRegex(ValueError,"approved authorization/spec"): server.retry_execution(self.root,queued["dispatch"]["dispatch_id"],"directory fixed","verified cwd")

    def test_settled_pi_steward_can_requeue_only_prestart_lease(self):
        self.policy(); self.authorized(); queued=server.enqueue_execution(self.root,"R-outbox"); claim=server.claim_next_execution(self.root,"pi-steward:123",run_id="R-outbox"); item=claim["task"]["dispatch"]
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"pi-steward:123","acknowledge",{"actual_agent":item["requested_agent"],"actual_model":item["requested_model"]})
        recovered=server.recover_abandoned_steward_claim(self.root,queued["dispatch"]["dispatch_id"],"owned_agent_settled")
        self.assertEqual(recovered["status"],"queued"); self.assertNotIn("consumer",recovered); self.assertNotIn("token",json.dumps(recovered).lower())
        next_claim=server.claim_next_execution(self.root,"pi-steward:456",run_id="R-outbox"); self.assertTrue(next_claim["claimed"])
        next_item=next_claim["task"]["dispatch"]; server._leased_transition(self.root,next_item["dispatch_id"],next_claim["lease_token"],"pi-steward:456","acknowledge",{"actual_agent":next_item["requested_agent"],"actual_model":next_item["requested_model"]}); server._leased_transition(self.root,next_item["dispatch_id"],next_claim["lease_token"],"pi-steward:456","running")
        with self.assertRaisesRegex(ValueError,"启动前"):
            server.recover_abandoned_steward_claim(self.root,queued["dispatch"]["dispatch_id"],"owned_agent_settled")

    def test_prestart_failure_does_not_mark_scientific_run_failed(self):
        self.policy(); self.authorized_v2("R-prestart"); queued=server.enqueue_execution(self.root,"R-prestart"); claim=server.claim_next_execution(self.root,"pi-steward:1",run_id="R-prestart"); item=claim["task"]["dispatch"]
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"pi-steward:1","acknowledge",{"actual_agent":item["requested_agent"],"actual_model":item["requested_model"]})
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"pi-steward:1","fail",{"failure_class":"preflight","reason":"tool unavailable before start","retryable":False})
        run=next(row for row in server.experiment_data(self.root)["runs"] if row["id"]=="R-prestart")
        self.assertEqual(run["workflow_stage"],"ready_to_run"); self.assertNotIn("execution_authorization_consumed_at",run); self.assertEqual(run["execution_dispatch_latest_status"],"failed")
        self.assertEqual(next(row for row in server._outbox_read(self.root)["items"] if row["dispatch_id"]==queued["dispatch"]["dispatch_id"])["status"],"failed")

    def test_old_running_dispatch_cannot_overwrite_current_run_linkage(self):
        self.policy(); self.authorized_v2("R-stale"); server.enqueue_execution(self.root,"R-stale"); claim=server.claim_next_execution(self.root,"pi-steward:1",run_id="R-stale"); item=claim["task"]["dispatch"]
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"pi-steward:1","acknowledge",{"actual_agent":item["requested_agent"],"actual_model":item["requested_model"]}); server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"pi-steward:1","running")
        data=server.experiment_data(self.root); run=next(row for row in data["runs"] if row["id"]=="R-stale"); run["execution_dispatch_id"]="dispatch-newer"; run["workflow_stage"]="ready_to_run"; server.write_tool_json(self.root,"runs.json",data["runs"])
        with self.assertRaisesRegex(ValueError,"旧 dispatch"):
            server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"pi-steward:1","fail",{"failure_class":"late","reason":"late callback","retryable":False})
        self.assertEqual(next(row for row in server._outbox_read(self.root)["items"] if row["dispatch_id"]==item["dispatch_id"])["status"],"running")
        self.assertEqual(next(row for row in server.experiment_data(self.root)["runs"] if row["id"]=="R-stale")["workflow_stage"],"ready_to_run")

    def test_browser_workflow_cannot_fail_a_live_outbox_attempt(self):
        self.policy(); self.authorized_v2("R-live"); server.enqueue_execution(self.root,"R-live")
        claim=server.claim_next_execution(self.root,"pi-steward:live",run_id="R-live"); item=claim["task"]["dispatch"]
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"pi-steward:live","acknowledge",{"actual_agent":item["requested_agent"],"actual_model":item["requested_model"]})
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"pi-steward:live","running")
        with self.assertRaisesRegex(ValueError,"持 lease 的 Steward"):
            server.advance_run_workflow(self.root,"R-live","mark-failed","human:web-v2")
        current=next(row for row in server.experiment_data(self.root)["runs"] if row["id"]=="R-live")
        self.assertEqual(current["workflow_stage"],"running")
        self.assertEqual(next(row for row in server._outbox_read(self.root)["items"] if row["dispatch_id"]==item["dispatch_id"])["status"],"running")

    def test_pi_prepares_placeholder_command_before_claim_without_new_authorization(self):
        self.policy(); rid="R-runtime"
        server.create_run(self.root,"E-001",{"variant":"runtime","purpose":"p","workspace_id":"W-01","command":"python train.py --manifest <manifest> --model <model-path>","artifact_dir":f"/exp/E-001/{rid}"},rid)
        server.review_run(self.root,rid,"submit",actor="terminal_pi"); server.review_run(self.root,rid,"approve",actor="human")
        data=server.experiment_data(self.root); run=next(row for row in data["runs"] if row["id"]==rid); run["workflow_version"]=2; run["workflow_stage"]="ready_to_run"; run["approved_spec"]=server._review_snapshot(run); server.write_tool_json(self.root,"runs.json",data["runs"]); server.save_run_spec(self.root,run)
        authorized=server.review_run(self.root,rid,"authorize_execution",actor="human"); auth=authorized["execution_authorized_at"]; queued=server.enqueue_execution(self.root,rid)["dispatch"]
        concrete="python train.py --manifest /data/e003.json --model /models/qwen"
        prepared=server.prepare_managed_run_command(self.root,rid,concrete,"pi-steward:123")
        self.assertTrue(prepared["prepared"]); self.assertFalse(prepared["idempotent"]); self.assertEqual(prepared["run"]["command"],concrete); self.assertEqual(prepared["run"]["execution_authorized_at"],auth)
        item=next(row for row in server._outbox_read(self.root)["items"] if row["dispatch_id"]==queued["dispatch_id"]); self.assertEqual(item["status"],"queued"); self.assertEqual(item["approved_spec_hash"],server._approved_spec_hash(prepared["run"])); self.assertEqual(item["history"][-1]["type"],"runtime_command_prepared")
        with self.assertRaisesRegex(ValueError,"不是占位命令"):
            server.prepare_managed_run_command(self.root,rid,"python other.py","pi-steward:123")
        with self.assertRaisesRegex(ValueError,"仍包含"):
            server.prepare_managed_run_command(self.root,rid,"python train.py --model <still-missing>","pi-steward:123")

    def test_pi_can_confirm_exact_real_command_inside_approved_proposal_wrapper(self):
        self.policy(); rid="R-proposed-runtime"; concrete="cd /srv/repo && bash tools/run_full.sh"
        server.create_run(self.root,"E-001",{"variant":"approved proposal","purpose":"p","workspace_id":"W-01","command":"proposed after approval: "+concrete,"artifact_dir":f"/exp/E-001/{rid}"},rid)
        server.review_run(self.root,rid,"submit",actor="terminal_pi");server.review_run(self.root,rid,"approve",actor="human")
        data=server.experiment_data(self.root);run=next(row for row in data["runs"] if row["id"]==rid);run["workflow_version"]=2;run["workflow_stage"]="ready_to_run";run["approved_spec"]=server._review_snapshot(run);server.write_tool_json(self.root,"runs.json",data["runs"]);server.save_run_spec(self.root,run)
        authorized=server.review_run(self.root,rid,"authorize_execution",actor="human");queued=server.enqueue_execution(self.root,rid)["dispatch"]
        with self.assertRaisesRegex(ValueError,"逐字一致"):
            server.prepare_managed_run_command(self.root,rid,"cd /srv/repo && bash tools/other.sh","pi-steward:123")
        prepared=server.prepare_managed_run_command(self.root,rid,concrete,"pi-steward:123")
        self.assertFalse(prepared["idempotent"]);self.assertEqual(prepared["run"]["command"],concrete);self.assertEqual(prepared["run"]["approved_spec"]["command"],concrete);self.assertEqual(prepared["run"]["execution_authorized_at"],authorized["execution_authorized_at"]);self.assertEqual(prepared["dispatch"]["dispatch_id"],queued["dispatch_id"]);self.assertEqual(prepared["dispatch"]["history"][-1]["detail"],"Pi confirmed the exact approved proposed command")
        again=server.prepare_managed_run_command(self.root,rid,concrete,"pi-steward:123");self.assertTrue(again["idempotent"]);self.assertEqual(again["dispatch"]["dispatch_id"],queued["dispatch_id"])

    def test_human_can_revoke_only_steward_control_and_reattach_same_attempt(self):
        self.policy(); self.authorized_v2("R-force"); server.enqueue_execution(self.root,"R-force")
        claim=server.claim_next_execution(self.root,"pi-steward:old",run_id="R-force"); item=claim["task"]["dispatch"]
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"pi-steward:old","acknowledge",{"actual_agent":item["requested_agent"],"actual_model":item["requested_model"]})
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"pi-steward:old","running",{"managed_execution":True})
        server.update_managed_execution_metadata(self.root,item["dispatch_id"],{"started_evidence":"tmux_new_session_ok"})
        run=next(row for row in server.experiment_data(self.root)["runs"] if row["id"]=="R-force")
        forced=server.force_expire_managed_steward_lease(self.root,"R-force",run["updated"])
        self.assertTrue(forced["revoked"]); self.assertFalse(forced["execution_restarted"]); self.assertEqual(forced["dispatch"]["status"],"running")
        with self.assertRaisesRegex(ValueError,"lease token"):
            server.managed_execution_heartbeat(self.root,item["dispatch_id"],claim["lease_token"],"pi-steward:old")
        attached=server.reattach_managed_execution(self.root,item["dispatch_id"],"pi-steward:new")
        self.assertTrue(attached["reattached"]); self.assertEqual(attached["dispatch"]["dispatch_id"],item["dispatch_id"]); self.assertNotIn("token",json.dumps(forced).lower()); self.assertTrue((self.root/".pi"/"stewards"/"R-force.json").exists())

    def test_expired_managed_heartbeat_repairs_cleared_run_projection(self):
        self.policy(); self.authorized_v2("R-heartbeat-repair"); server.enqueue_execution(self.root,"R-heartbeat-repair")
        consumer="pi-steward:same"; claim=server.claim_next_execution(self.root,consumer,run_id="R-heartbeat-repair"); item=claim["task"]["dispatch"]
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],consumer,"acknowledge",{"actual_agent":item["requested_agent"],"actual_model":item["requested_model"]})
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],consumer,"running",{"managed_execution":True})
        server.update_managed_execution_metadata(self.root,item["dispatch_id"],{"started_evidence":"tmux_new_session_ok"})
        data=server.experiment_data(self.root); run=next(row for row in data["runs"] if row["id"]=="R-heartbeat-repair")
        run["review_status"]="changes_requested"; run["review_requirements"]="stale UI projection"
        for key in ("execution_authorized_at","execution_authorized_by","execution_authorization_consumed_at","authorized_workspace_execution_hash","execution_dispatch_id","execution_dispatch_latest_status"): run.pop(key,None)
        server.write_tool_json(self.root,"runs.json",data["runs"]); server.save_run_spec(self.root,run)
        box=server._outbox_read(self.root); dispatch=next(row for row in box["items"] if row["dispatch_id"]==item["dispatch_id"]); dispatch["lease_expires_at"]=(datetime.datetime.now()-datetime.timedelta(seconds=1)).isoformat(timespec="seconds"); server.write_tool_json(self.root,"execution-outbox.json",box)
        renewed=server.managed_execution_heartbeat(self.root,item["dispatch_id"],claim["lease_token"],consumer)
        self.assertEqual(renewed["history"][-1]["type"],"managed_heartbeat_reacquired")
        repaired=next(row for row in server.experiment_data(self.root)["runs"] if row["id"]=="R-heartbeat-repair")
        self.assertEqual(repaired["review_status"],"approved"); self.assertEqual(repaired["execution_dispatch_id"],item["dispatch_id"]); self.assertEqual(repaired["workflow_stage"],"running"); self.assertNotIn("review_requirements",repaired)
        self.assertEqual(repaired["execution_projection_repair_history"][-1]["prior_review_status"],"changes_requested")

    def test_expired_managed_attempt_can_reattach_after_projection_was_cleared(self):
        self.policy(); self.authorized_v2("R-reattach-repair"); server.enqueue_execution(self.root,"R-reattach-repair")
        old_consumer="pi-steward:old"; claim=server.claim_next_execution(self.root,old_consumer,run_id="R-reattach-repair"); item=claim["task"]["dispatch"]
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],old_consumer,"acknowledge",{"actual_agent":item["requested_agent"],"actual_model":item["requested_model"]})
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],old_consumer,"running",{"managed_execution":True})
        server.update_managed_execution_metadata(self.root,item["dispatch_id"],{"started_evidence":"tmux_new_session_ok"})
        data=server.experiment_data(self.root); run=next(row for row in data["runs"] if row["id"]=="R-reattach-repair"); run["review_status"]="changes_requested"
        for key in ("execution_authorized_at","execution_authorized_by","execution_authorization_consumed_at","authorized_workspace_execution_hash","execution_dispatch_id","execution_dispatch_latest_status"): run.pop(key,None)
        server.write_tool_json(self.root,"runs.json",data["runs"]); server.save_run_spec(self.root,run)
        box=server._outbox_read(self.root); dispatch=next(row for row in box["items"] if row["dispatch_id"]==item["dispatch_id"]); dispatch["lease_expires_at"]=(datetime.datetime.now()-datetime.timedelta(seconds=1)).isoformat(timespec="seconds"); server.write_tool_json(self.root,"execution-outbox.json",box)
        attached=server.reattach_managed_execution(self.root,item["dispatch_id"],"pi-steward:new")
        self.assertTrue(attached["run_projection_repaired"]); self.assertTrue(attached["lease_token"]); self.assertEqual(attached["dispatch"]["consumer"],"pi-steward:new")

    def test_running_attempt_blocks_automation_policy_mutation(self):
        self.policy(); self.authorized_v2("R-policy-live"); server.enqueue_execution(self.root,"R-policy-live")
        claim=server.claim_next_execution(self.root,"pi-steward:policy",run_id="R-policy-live"); item=claim["task"]["dispatch"]
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"pi-steward:policy","acknowledge",{"actual_agent":item["requested_agent"],"actual_model":item["requested_model"]})
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"pi-steward:policy","running",{"managed_execution":True})
        policy={"mode":"off","allowed_code_roots":[],"test_commands":[],"max_repairs":0,"time_budget_minutes":30,"auto_rerun":False,"install_declared_dependencies":False,"dependency_files":[]}
        with self.assertRaisesRegex(ValueError,"attempt.*正在运行"):
            server.update_run(self.root,"R-policy-live",{"automation_policy":policy})

    def test_failed_v2_run_can_restart_as_new_attempt_without_reopening_spec(self):
        self.policy(auto_queue_on_authorize=True)
        server.create_run(self.root,"E-001",{"variant":"restart","purpose":"p","workspace_id":"W-01","command":"python run.py","artifact_dir":"/exp/E-001/R-restart"},"R-restart")
        server.review_run(self.root,"R-restart","submit",actor="terminal_pi"); server.review_run(self.root,"R-restart","approve",actor="human")
        data=server.experiment_data(self.root); run=next(row for row in data["runs"] if row["id"]=="R-restart")
        run["workflow_version"]=2; run["workflow_stage"]="ready_to_run"; run["approved_spec"]=server._review_snapshot(run)
        server.write_tool_json(self.root,"runs.json",data["runs"]); server.save_run_spec(self.root,run)
        authorized=server.review_run(self.root,"R-restart","authorize_execution",actor="human")
        old_dispatch=authorized["execution_dispatch_enqueue_result"]["dispatch"]; claim=server.claim_next_execution(self.root,"worker",run_id="R-restart")
        item=claim["task"]["dispatch"]; server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"worker","acknowledge",{"actual_agent":item["requested_agent"],"actual_model":item["requested_model"]})
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"worker","running")
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"worker","fail",{"failure_class":"launch","reason":"remote process never started","retryable":False})
        failed=next(row for row in server.experiment_data(self.root)["runs"] if row["id"]=="R-restart")
        restarted=server.restart_failed_run_execution(self.root,"R-restart",failed["updated"])
        self.assertEqual(restarted["run"]["workflow_stage"],"ready_to_run"); self.assertEqual(restarted["run"]["review_status"],"approved")
        self.assertNotEqual(restarted["dispatch"]["dispatch_id"],old_dispatch["dispatch_id"]); self.assertEqual(restarted["dispatch"]["status"],"queued")
        attempts=[row for row in server._outbox_read(self.root)["items"] if row["run_id"]=="R-restart"]
        self.assertEqual([row["status"] for row in attempts],["failed","queued"])
        self.assertEqual(restarted["run"]["workflow_history"][-1]["action"],"restart-failed-execution")

    def test_trial_matrix_is_one_direct_authorized_run_attempt(self):
        self.policy(); run=server.create_run(self.root,"E-001",{"workflow_version":2,"variant":"matrix","purpose":"compare parameters","research_question":"which setting works","metric_plan":"accuracy","workspace_id":"W-01"},"R-matrix")
        result=server.prepare_run_trials_for_steward(self.root,"R-matrix",run["updated"],"compare variants and seeds",[{"name":"variant","values":["base","permute"]},{"name":"seed","values":[1,2]}],2,1)
        self.assertEqual(len(result["trial_plan"]["trials"]),4); self.assertEqual(result["run"]["workflow_stage"],"ready_to_run"); self.assertEqual(result["run"]["review_status"],"approved"); self.assertEqual(result["dispatch"]["status"],"queued")
        self.assertEqual(result["run"]["approved_spec"]["trial_plan"]["contract"],"survey-tool.run-trial-plan/v1")
        manifest={"contract":"survey-tool.run-trial-manifest/v1","trials":[{"id":row["id"],"parameters":row["parameters"]} for row in result["trial_plan"]["trials"]]}
        server.prepare_managed_run_command(self.root,"R-matrix","python matrix.py","pi-steward:test",manifest)
        claim=server.claim_next_execution(self.root,"pi-steward:test",run_id="R-matrix"); item=claim["task"]["dispatch"]
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"pi-steward:test","acknowledge",{"actual_agent":item["requested_agent"],"actual_model":item["requested_model"]})
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"pi-steward:test","running")
        current=next(row for row in server.experiment_data(self.root)["runs"] if row["id"]=="R-matrix")
        replacement=server.prepare_run_trials_for_steward(self.root,"R-matrix",current["updated"],"replace the stale attempt",None,1,1,"human:web-v2","ai_planned",5)
        self.assertEqual(replacement["replaced_dispatch_ids"],[result["dispatch"]["dispatch_id"]])
        attempts=[item for item in server._outbox_read(self.root)["items"] if item.get("run_id")=="R-matrix"]
        self.assertEqual([item["status"] for item in attempts],["superseded","queued"])
        self.assertNotIn("lease_token_hash",attempts[0]); self.assertNotEqual(attempts[0]["dispatch_id"],attempts[1]["dispatch_id"])

    def test_ai_trial_budget_is_one_direct_authorized_run_attempt(self):
        self.policy(); run=server.create_run(self.root,"E-001",{"workflow_version":2,"variant":"adaptive","purpose":"find informative settings","research_question":"which settings matter","metric_plan":"accuracy","workspace_id":"W-01"},"R-adaptive")
        result=server.prepare_run_trials_for_steward(self.root,"R-adaptive",run["updated"],"inspect the implementation and plan useful trials",None,2,1,"human:web-v2","ai_planned",8)
        plan=result["trial_plan"]
        self.assertEqual(plan["planning_mode"],"ai_planned"); self.assertEqual(plan["trial_budget"],8); self.assertEqual(plan["trials"],[])
        self.assertEqual(result["run"]["workflow_stage"],"ready_to_run"); self.assertEqual(result["dispatch"]["status"],"queued")

    def test_trial_run_cannot_claim_until_exact_manifest_is_prepared(self):
        self.policy(); run=server.create_run(self.root,"E-001",{"workflow_version":2,"variant":"manifest","purpose":"compare settings","research_question":"which setting","metric_plan":"accuracy","workspace_id":"W-01"},"R-manifest")
        prepared=server.prepare_run_trials_for_steward(self.root,"R-manifest",run["updated"],"compare two seeds",[{"name":"seed","values":[1,2]}],1,1)
        claim=server.claim_next_execution(self.root,"pi-steward:manifest",run_id="R-manifest")
        self.assertFalse(claim["claimed"]); queued=next(item for item in server._outbox_read(self.root)["items"] if item["run_id"]=="R-manifest"); self.assertEqual(queued["status"],"queued"); self.assertIn("Trial manifest",queued["last_error"])
        wrong={"contract":"survey-tool.run-trial-manifest/v1","trials":[{"id":"T-001","parameters":{"seed":1}}]}
        with self.assertRaisesRegex(ValueError,"恰好包含 2"):
            server.prepare_managed_run_command(self.root,"R-manifest","python train.py","pi-steward:manifest",wrong)
        manifest={"contract":"survey-tool.run-trial-manifest/v1","trials":[{"id":"T-001","parameters":{"seed":1}},{"id":"T-002","parameters":{"seed":2}}]}
        command=server.prepare_managed_run_command(self.root,"R-manifest","python train.py","pi-steward:manifest",manifest)
        self.assertEqual(command["run"]["trial_manifest"],manifest); self.assertRegex(command["run"]["trial_manifest_hash"],r"^sha256:[0-9a-f]{64}$")
        self.assertEqual(command["run"]["trial_campaigns"][0]["manifest"],manifest); self.assertEqual(command["run"]["trial_campaigns"][0]["status"],"ready_to_start")
        claimed=server.claim_next_execution(self.root,"pi-steward:manifest",run_id="R-manifest"); self.assertTrue(claimed["claimed"])

    def test_ai_trial_manifest_must_match_requested_count(self):
        plan=server.build_run_trial_plan("choose useful trials",None,2,1,"ai_planned",3)
        with self.assertRaisesRegex(ValueError,"恰好包含 3"):
            experiment_domain._validated_run_trial_manifest(plan,{"contract":"survey-tool.run-trial-manifest/v1","trials":[{"id":"T-001","parameters":{"lr":0.1}}]})
        manifest={"contract":"survey-tool.run-trial-manifest/v1","trials":[{"id":f"T-{index:03d}","parameters":{"lr":value}} for index,value in enumerate((0.1,0.01,0.001),1)]}
        self.assertEqual(len(experiment_domain._validated_run_trial_manifest(plan,manifest)["trials"]),3)

    def test_trial_plan_tool_preview_validates_exact_set_without_writing(self):
        self.policy(); run=server.create_run(self.root,"E-001",{"workflow_version":2,"variant":"tool","purpose":"plan trials","research_question":"which setting","metric_plan":"accuracy","workspace_id":"W-01"},"R-tool")
        server.prepare_run_trials_for_steward(self.root,"R-tool",run["updated"],"compare two seeds",[{"name":"seed","values":[1,2]}],1,0)
        before=server.read_tool_json(self.root,"runs.json",[])
        inspected=server.run_trial_plan_status(self.root,"R-tool")
        self.assertEqual(inspected["expected_trials"],2); self.assertFalse(inspected["ready_to_prepare"]); self.assertTrue(inspected["read_only"])
        manifest={"contract":"survey-tool.run-trial-manifest/v1","trials":[{"id":"T-001","parameters":{"seed":1}},{"id":"T-002","parameters":{"seed":2}}]}
        preview=server.run_trial_plan_status(self.root,"R-tool",manifest)
        self.assertEqual(preview["planned_trials"],2); self.assertTrue(preview["ready_to_prepare"])
        self.assertEqual(server.read_tool_json(self.root,"runs.json",[]),before)

    def test_trial_plan_can_replace_old_concrete_single_run_command(self):
        self.policy(); run=server.create_run(self.root,"E-001",{"workflow_version":2,"variant":"batch-upgrade","purpose":"compare settings","research_question":"which setting","metric_plan":"accuracy","workspace_id":"W-01","command":"python train.py --seed 1"},"R-batch-upgrade")
        prepared=server.prepare_run_trials_for_steward(self.root,"R-batch-upgrade",run["updated"],"run two seeds",[{"name":"seed","values":[1,2]}],1,0)
        manifest={"contract":"survey-tool.run-trial-manifest/v1","trials":[{"id":"T-001","parameters":{"seed":1}},{"id":"T-002","parameters":{"seed":2}}]}
        result=server.prepare_managed_run_command(self.root,"R-batch-upgrade","bash tools/run_trials.sh","pi-steward:test",manifest)
        self.assertEqual(result["run"]["command"],"bash tools/run_trials.sh")
        self.assertEqual(result["run"]["implementation_history"][-1]["reason"],"trial_batch_launcher_replaced_single_command")
        item=next(row for row in server._outbox_read(self.root)["items"] if row["run_id"]=="R-batch-upgrade")
        self.assertEqual(item["history"][-1]["type"],"trial_batch_command_prepared")

    def test_completed_run_accepts_new_trial_campaign_without_new_run(self):
        self.policy(); run=server.create_run(self.root,"E-001",{"workflow_version":2,"variant":"smoke","purpose":"same capability question","research_question":"does it run","metric_plan":"accuracy","workspace_id":"W-01","command":"python smoke.py --batch-size 1"},"R-same")
        data=server.experiment_data(self.root); current=next(row for row in data["runs"] if row["id"]=="R-same"); current["workflow_stage"]="completed"; current["status"]="completed"; current["result_analysis"]="batch size 1 smoke passed"; current["updated"]="completed-v1"; server.write_tool_json(self.root,"runs.json",data["runs"]); server.save_run_spec(self.root,current)
        prepared=server.prepare_run_trials_for_steward(self.root,"R-same","completed-v1","scale physical batch",[{"name":"batch_size","values":[1,2,4,8]}],1,0)
        self.assertEqual(prepared["run"]["id"],"R-same"); self.assertEqual(prepared["campaign"]["id"],"C-001"); self.assertEqual(prepared["run"]["workflow_stage"],"ready_to_run")
        self.assertEqual(prepared["campaign"]["previous_result"]["result_analysis"],"batch size 1 smoke passed"); self.assertNotIn("result_analysis",prepared["run"])
        self.assertEqual(prepared["run"]["trial_plan"]["campaign_id"],"C-001"); self.assertEqual(prepared["trial_plan"]["trial_budget"],4)
        stored=next(row for row in server.experiment_data(self.root)["runs"] if row["id"]=="R-same"); campaign=stored["trial_campaigns"][0]
        self.assertEqual(campaign["request"],"scale physical batch"); self.assertEqual(campaign["plan"]["axes"],[{"name":"batch_size","values":[1,2,4,8]}])
        self.assertEqual([trial["parameters"]["batch_size"] for trial in campaign["plan"]["trials"]],[1,2,4,8])

    def test_normal_failed_restart_deactivates_trial_campaign_and_runs_single(self):
        self.policy(); run=server.create_run(self.root,"E-001",{"workflow_version":2,"variant":"single restart","purpose":"one experiment","research_question":"does one setting work","metric_plan":"accuracy","workspace_id":"W-01"},"R-single")
        prepared=server.prepare_run_trials_for_steward(self.root,"R-single",run["updated"],"temporary sweep",[{"name":"batch_size","values":[1,2]}],1,0)
        manifest={"contract":"survey-tool.run-trial-manifest/v1","trials":[{"id":"T-001","parameters":{"batch_size":1}},{"id":"T-002","parameters":{"batch_size":2}}]}
        server.prepare_managed_run_command(self.root,"R-single","python train.py --batch-size 1","pi-steward:single",manifest)
        claim=server.claim_next_execution(self.root,"pi-steward:single",run_id="R-single"); item=claim["task"]["dispatch"]
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"pi-steward:single","acknowledge",{"actual_agent":item["requested_agent"],"actual_model":item["requested_model"]})
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"pi-steward:single","running",{"managed_execution":True})
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"pi-steward:single","fail",{"failure_class":"runtime","reason":"retry once as a single experiment","retryable":True})
        failed=next(row for row in server.experiment_data(self.root)["runs"] if row["id"]=="R-single")
        restarted=server.restart_failed_run_execution(self.root,"R-single",failed["updated"],execution_mode="single")
        self.assertEqual(restarted["execution_mode"],"single"); self.assertNotIn("trial_plan",restarted["run"]); self.assertNotIn("active_trial_campaign_id",restarted["run"])
        self.assertEqual(restarted["run"]["trial_campaigns"][0]["status"],"cancelled_for_single_run")

    def test_failed_dispatch_can_restart_when_run_stage_projection_is_still_ready(self):
        self.policy(auto_queue_on_authorize=True)
        server.create_run(self.root,"E-001",{"variant":"restart-stale-stage","purpose":"p","workspace_id":"W-01","command":"python run.py","artifact_dir":"/exp/E-001/R-stale"},"R-stale")
        server.review_run(self.root,"R-stale","submit",actor="terminal_pi"); server.review_run(self.root,"R-stale","approve",actor="human")
        data=server.experiment_data(self.root); run=next(row for row in data["runs"] if row["id"]=="R-stale")
        run["workflow_version"]=2; run["workflow_stage"]="ready_to_run"; run["approved_spec"]=server._review_snapshot(run)
        server.write_tool_json(self.root,"runs.json",data["runs"]); server.save_run_spec(self.root,run)
        authorized=server.review_run(self.root,"R-stale","authorize_execution",actor="human")
        old_dispatch=authorized["execution_dispatch_enqueue_result"]["dispatch"]
        claim=server.claim_next_execution(self.root,"worker",run_id="R-stale"); item=claim["task"]["dispatch"]
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"worker","acknowledge",{"actual_agent":item["requested_agent"],"actual_model":item["requested_model"]})
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"worker","fail",{"failure_class":"prestart","reason":"Pi found unresolved implementation inputs","retryable":False})
        data=server.experiment_data(self.root); stale=next(row for row in data["runs"] if row["id"]=="R-stale")
        stale["workflow_stage"]="ready_to_run"; stale["status"]="approved"; server.write_tool_json(self.root,"runs.json",data["runs"]); server.save_run_spec(self.root,stale)
        restarted=server.restart_failed_run_execution(self.root,"R-stale",stale["updated"])
        self.assertEqual(restarted["run"]["workflow_stage"],"ready_to_run")
        self.assertNotEqual(restarted["dispatch"]["dispatch_id"],old_dispatch["dispatch_id"])
        self.assertEqual([row["status"] for row in server._outbox_read(self.root)["items"] if row["run_id"]=="R-stale"],["failed","queued"])

    def test_live_pi_delivery_busy_idempotent_and_never_claims(self):
        self.policy(auto_deliver_on_pi_live=True); self.authorized(); queued=server.enqueue_execution(self.root,"R-outbox")
        server.write_pi_binding(self.root,{"path":"","sessionId":"session-1","name":"pi","topic":""})
        class Proc:
            def poll(self): return None
        class Bridge:
            proc=Proc(); is_streaming=True; prompts=[]
            def state(self): return {"isStreaming":self.is_streaming}
            def prompt(self,text): self.prompts.append(text); return {"success":True}
        bridge=Bridge(); busy=server.dispatch_pending_to_live_pi(self.root,bridge); self.assertEqual(busy["error"],"pi_busy"); self.assertFalse(bridge.prompts)
        bridge.is_streaming=False; sent=server.dispatch_pending_to_live_pi(self.root,bridge); self.assertEqual(sent["delivered"],[queued["dispatch"]["dispatch_id"]]); self.assertEqual(len(bridge.prompts),1)
        again=server.dispatch_pending_to_live_pi(self.root,bridge); self.assertEqual(again["delivered"],[]); self.assertEqual(len(bridge.prompts),1)
        item=server.execution_outbox_public(self.root)["execution_outbox"]["items"][0]; self.assertEqual(item["status"],"delivered"); self.assertNotIn("lease_token",item)
        self.assertNotIn("lease_token",json.dumps(server.experiment_dashboard_data(self.root)))
        self.assertIn("claim-next",bridge.prompts[0]); self.assertIn("不得把收到本 Prompt 当作已消费",bridge.prompts[0])

    def test_delivered_redispatch_cooldown_new_session_and_claim_stop(self):
        self.policy(auto_deliver_on_pi_live=True); self.authorized(); queued=server.enqueue_execution(self.root,"R-outbox")
        class Proc:
            def poll(self): return None
        class Bridge:
            proc=Proc(); is_streaming=False
            def __init__(self): self.prompts=[]
            def state(self): return {"isStreaming":False}
            def prompt(self,text): self.prompts.append(text); return {"success":True}
        bridge=Bridge(); t0=datetime.datetime(2026,1,1,12,0,0)
        server.write_pi_binding(self.root,{"sessionId":"session-1"})
        self.assertEqual(server.dispatch_pending_to_live_pi(self.root,bridge,now=t0)["delivered"],[queued["dispatch"]["dispatch_id"]])
        self.assertEqual(server.dispatch_pending_to_live_pi(self.root,bridge,now=t0+datetime.timedelta(seconds=299))["delivered"],[])
        self.assertEqual(server.dispatch_pending_to_live_pi(self.root,bridge,now=t0+datetime.timedelta(seconds=300))["delivered"],[queued["dispatch"]["dispatch_id"]])
        server.write_pi_binding(self.root,{"sessionId":"session-2"})
        self.assertEqual(server.dispatch_pending_to_live_pi(self.root,bridge,now=t0+datetime.timedelta(seconds=301))["delivered"],[queued["dispatch"]["dispatch_id"]])
        claimed=server.claim_next_execution(self.root,"worker"); self.assertTrue(claimed["claimed"])
        self.assertEqual(server.dispatch_pending_to_live_pi(self.root,bridge,explicit=True,force=True,now=t0+datetime.timedelta(seconds=302))["delivered"],[])
        self.assertEqual(len(bridge.prompts),3)

    def test_force_redispatch_and_max_attempts(self):
        self.policy(auto_deliver_on_pi_live=True,max_delivery_attempts=2); self.authorized(); server.enqueue_execution(self.root,"R-outbox"); server.write_pi_binding(self.root,{"sessionId":"session-1"})
        class Proc:
            def poll(self): return None
        class Bridge:
            proc=Proc(); is_streaming=False
            def __init__(self): self.prompts=[]
            def state(self): return {"isStreaming":False}
            def prompt(self,text): self.prompts.append(text); return {"success":True}
        bridge=Bridge(); t0=datetime.datetime(2026,1,1)
        server.dispatch_pending_to_live_pi(self.root,bridge,now=t0)
        self.assertEqual(server.dispatch_pending_to_live_pi(self.root,bridge,explicit=True,force=True,now=t0)["delivered"],[server._outbox_read(self.root)["items"][0]["dispatch_id"]])
        self.assertEqual(server.dispatch_pending_to_live_pi(self.root,bridge,explicit=True,force=True,now=t0)["delivered"],[])

    def test_cancelled_policy_failure_can_be_edited_and_reauthorized(self):
        self.policy(); self.authorized()
        server.update_run(self.root,"R-outbox",{"output_dir":"relative/output"})
        blocked=server.enqueue_execution(self.root,"R-outbox")
        self.assertFalse(blocked["queued"])
        self.assertIn("output_dir=relative/output",blocked["dispatch"]["last_error"])
        self.assertIn("绝对路径",blocked["dispatch"]["last_error"])
        server.cancel_execution_dispatches(self.root,"R-outbox","policy repair")
        server.update_run(self.root,"R-outbox",{"output_dir":"/exp/R-outbox/output","metrics_path":"/exp/R-outbox/metrics.json"})
        old=server.enqueue_execution(self.root,"R-outbox")
        self.assertFalse(old["queued"])
        server.review_run(self.root,"R-outbox","authorize_execution",actor="human")
        fresh=server.enqueue_execution(self.root,"R-outbox")
        self.assertTrue(fresh["queued"])
        self.assertNotEqual(fresh["dispatch"]["dispatch_id"],blocked["dispatch"]["dispatch_id"])
        self.assertEqual(fresh["dispatch"]["status"],"queued")

    def test_same_authorization_terminal_is_idempotent_and_blocked_unblocks(self):
        self.policy(); self.authorized(); queued=server.enqueue_execution(self.root,"R-outbox"); claim=server.claim_next_execution(self.root,"worker"); item=claim["task"]["dispatch"]
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"worker","acknowledge",{"actual_agent":item["requested_agent"],"actual_model":item["requested_model"]})
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"worker","running")
        server._leased_transition(self.root,item["dispatch_id"],claim["lease_token"],"worker","complete",{"result_message":"done"})
        again=server.enqueue_execution(self.root,"R-outbox"); self.assertTrue(again["idempotent"]); self.assertFalse(again["queued"]); self.assertEqual(again["dispatch"]["dispatch_id"],queued["dispatch"]["dispatch_id"])
        server.review_run(self.root,"R-outbox","authorize_execution",actor="human"); reauthorized=server.enqueue_execution(self.root,"R-outbox")
        self.assertNotEqual(reauthorized["dispatch"]["dispatch_id"],queued["dispatch"]["dispatch_id"]); self.assertTrue(reauthorized["queued"])

        server.write_tool_json(self.root,"servers.json",[{"id":"S-01","ssh_host":""}]); self.authorized("R-blocked"); blocked=server.enqueue_execution(self.root,"R-blocked"); self.assertEqual(blocked["dispatch"]["status"],"blocked")
        server.write_tool_json(self.root,"servers.json",[{"id":"S-01","ssh_host":"test"}]); unblocked=server.enqueue_execution(self.root,"R-blocked"); self.assertTrue(unblocked["idempotent"]); self.assertTrue(unblocked["unblocked"]); self.assertEqual(unblocked["dispatch"]["dispatch_id"],blocked["dispatch"]["dispatch_id"])

    def test_public_structures_recursively_hide_tokens_and_hashes(self):
        self.policy(); self.authorized(); server.enqueue_execution(self.root,"R-outbox")
        box=server._outbox_read(self.root); box["items"][0]["debug"]={"nested_token":"secret","nested":{"spec_hash":"secret"}}; server.write_tool_json(self.root,"execution-outbox.json",box)
        def assert_clean(value):
            if isinstance(value,dict):
                for key,child in value.items():
                    self.assertNotIn("token",key.lower()); self.assertNotIn("hash",key.lower()); assert_clean(child)
            elif isinstance(value,list):
                for child in value: assert_clean(child)
        assert_clean(server.execution_outbox_public(self.root)); assert_clean(server.experiment_dashboard_data(self.root))

    def test_dispatch_policy_is_human_only(self):
        self.policy(auto_deliver_on_pi_live=True)
        with self.assertRaisesRegex(ValueError,"未声明字段"): server.update_experiment(self.root,"E-001",{"execution_dispatch_policy":{}})
        server.create_run(self.root,"E-001",{"variant":"isolation"},"R-isolation")
        with self.assertRaisesRegex(ValueError,"未声明字段"): server.update_run(self.root,"R-isolation",{"execution_dispatch_policy":{}})
        with self.assertRaisesRegex(ValueError,"boolean"): server.validate_execution_dispatch_policy({"enabled":"yes"})

    def test_cli_list_status_and_enqueue_json(self):
        self.policy(); self.authorized(); old_load=surveyctl.server.load_config; old_argv=sys.argv
        surveyctl.server.load_config=lambda:{"projects_root":str(self.root.parent),"projects":[str(self.root)],"skill_dir":"","port":7421}
        def invoke(*args):
            sys.argv=["surveyctl.py","--project",str(self.root),*args]; out=io.StringIO()
            with contextlib.redirect_stdout(out): surveyctl.main()
            return json.loads(out.getvalue())
        try:
            queued=invoke("outbox","enqueue","R-outbox"); did=queued["dispatch"]["dispatch_id"]
            self.assertEqual(invoke("outbox","status",did)["dispatch_id"],did)
            listing=invoke("outbox","list"); self.assertEqual(listing["items"][0]["dispatch_id"],did); self.assertNotIn("lease_token",json.dumps(listing))
        finally: surveyctl.server.load_config=old_load; sys.argv=old_argv


if __name__=="__main__": unittest.main()
