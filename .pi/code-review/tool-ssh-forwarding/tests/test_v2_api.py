import json
import hashlib
import pathlib
import tempfile
import threading
import unittest
from unittest import mock
import urllib.error
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer

import server


class V2ApiTest(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp(prefix="v2-api-project-"))
        (self.root / "state.md").write_text("state: TEST\n", encoding="utf-8")
        server.CFG = {"projects_root": str(self.root.parent), "projects": [str(self.root)], "skill_dir": "", "port": 0}
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.H)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        self.project = urllib.parse.quote(str(self.root), safe="")

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=2)

    def request(self, method, path, payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        request = urllib.request.Request(
            self.base + path, data=data, method=method,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as error:
            try:
                return error.code, json.loads(error.read())
            finally:
                error.close()

    def test_reads_do_not_initialize_and_confirmation_is_required(self):
        status, payload = self.request("GET", f"/api/v2/p/{self.project}/paper-candidates")
        self.assertEqual(status, 200)
        self.assertFalse(payload["initialized"])
        self.assertFalse((self.root / ".survey-tool/survey-tool-v2.sqlite3").exists())

        status, _ = self.request("POST", f"/api/v2/p/{self.project}/initialize", {"confirmation": "yes"})
        self.assertEqual(status, 400)
        self.assertFalse((self.root / ".survey-tool/survey-tool-v2.sqlite3").exists())

        status, payload = self.request(
            "POST", f"/api/v2/p/{self.project}/initialize",
            {"confirmation": "INITIALIZE SURVEY TOOL 2.0"},
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload["schema_version"], 7)

    def test_experiment_run_archive_facade_is_reversible_and_keeps_records(self):
        server.write_tool_json(self.root,"servers.json",[{"id":"S-01","ssh_host":"test"}])
        server.write_tool_json(self.root,"workspaces.json",[{"id":"W-01","server_id":"S-01","remote_repo":"/repo","remote_worktree_root":"/worktrees","remote_data_root":"/data","remote_experiment_root":"/exp"}])
        exp=server.create_experiment(self.root,{"title":"archive","objective":"keep history","workspace_id":"W-01"},"E-001")
        run=server.create_run(self.root,"E-001",{"variant":"old","purpose":"retained"},"R-old")
        path=f"/api/v2/p/{self.project}/runs/R-old/archive"
        status,_=self.request("POST",path,{"confirmation":"ARCHIVE V2 RUN R-old","expected_updated":"stale","reason":"obsolete"}); self.assertEqual(status,409)
        status,payload=self.request("POST",path,{"confirmation":"ARCHIVE V2 RUN R-old","expected_updated":run["updated"],"reason":"obsolete"}); self.assertEqual(status,200,payload); self.assertTrue(payload["archived"]); self.assertEqual(payload["run"]["purpose"],"retained")
        status,payload=self.request("POST",path,{"confirmation":"RESTORE V2 RUN R-old","expected_updated":payload["run"]["updated"],"restore":True}); self.assertEqual(status,200,payload); self.assertFalse(payload["archived"])
        exp=next(item for item in payload["dashboard"]["experiments"] if item["id"]=="E-001")
        exp_path=f"/api/v2/p/{self.project}/experiments/E-001/archive"
        status,payload=self.request("POST",exp_path,{"confirmation":"ARCHIVE V2 EXPERIMENT E-001","expected_updated":exp["updated"],"reason":"superseded"}); self.assertEqual(status,200,payload); self.assertTrue(payload["archived"])

    def test_run_solid_evidence_label_facade_does_not_change_claim_verdict(self):
        server.write_tool_json(self.root,"servers.json",[{"id":"S-01","ssh_host":"test"}]); server.write_tool_json(self.root,"workspaces.json",[{"id":"W-01","server_id":"S-01","remote_repo":"/repo"}])
        server.create_experiment(self.root,{"title":"evidence","objective":"judge","workspace_id":"W-01"},"E-001"); run=server.create_run(self.root,"E-001",{"variant":"solid","result_summary":"stable"},"R-solid")
        path=f"/api/v2/p/{self.project}/runs/R-solid/evidence-label"
        status,_=self.request("POST",path,{"confirmation":"SET V2 RUN EVIDENCE LABEL R-solid","expected_updated":"stale","label":"solid"}); self.assertEqual(status,409)
        status,payload=self.request("POST",path,{"confirmation":"SET V2 RUN EVIDENCE LABEL R-solid","expected_updated":run["updated"],"label":"solid","note":"repeated"}); self.assertEqual(status,200,payload); self.assertEqual(payload["evidence_label"],"solid"); self.assertFalse(payload["claim_verdict_changed"]); self.assertNotIn("claim_verdict",payload["run"])

    def test_steward_start_facade_requires_confirmation_and_never_returns_lease(self):
        path=f"/api/v2/p/{self.project}/runs/R-1/steward/start"
        with mock.patch.object(server,"prepare_steward_handoff",return_value={"run_id":"R-1","handoff_command":"SAFE COMMAND","execution_started":False,"herdr_invoked":False,"lease_exposed":False,"prompt_used":False}) as start:
            status,_=self.request("POST",path,{"expected_updated":"u1"}); self.assertEqual(status,400); start.assert_not_called()
            status,payload=self.request("POST",path,{"confirmation":"PREPARE V2 RUN STEWARD","expected_updated":"u1"})
        self.assertEqual(status,200,payload); self.assertFalse(payload["execution_started"]); self.assertFalse(payload["herdr_invoked"]); self.assertEqual(payload["handoff_command"],"SAFE COMMAND"); self.assertNotIn("token",json.dumps(payload).lower()); start.assert_called_once_with(self.root,"R-1","u1")

    def test_trial_matrix_prepares_one_direct_steward_attempt(self):
        path=f"/api/v2/p/{self.project}/runs/R-1/trials/prepare-steward"; plan={"contract":"survey-tool.run-trial-plan/v1","request":"compare seeds","axes":[{"name":"seed","values":[1,2]}],"trials":[{"id":"T-001"},{"id":"T-002"}],"concurrency":1,"max_retries":1}
        prepared={"run":{"id":"R-1","updated":"u2","trial_plan":plan},"dispatch":{"dispatch_id":"D-new","status":"queued"},"trial_plan":plan}; handoff={"run_id":"R-1","handoff_command":"SAFE TRIAL COMMAND","execution_started":False,"herdr_invoked":False,"lease_exposed":False}
        body={"confirmation":"PREPARE V2 RUN TRIALS","expected_updated":"u1","request":"compare seeds","axes":[{"name":"seed","values":[1,2]}],"concurrency":1,"max_retries":1}
        with mock.patch.object(server,"prepare_run_trials_for_steward",return_value=prepared) as prepare, mock.patch.object(server,"prepare_steward_handoff",return_value=handoff) as launch:
            status,_=self.request("POST",path,{**body,"confirmation":"wrong"}); self.assertEqual(status,400); prepare.assert_not_called()
            status,payload=self.request("POST",path,body)
        self.assertEqual(status,200,payload); self.assertEqual(payload["trial_plan"]["contract"],"survey-tool.run-trial-plan/v1"); self.assertEqual(payload["handoff_command"],"SAFE TRIAL COMMAND"); self.assertFalse(payload["execution_started"])
        prepare.assert_called_once_with(self.root,"R-1","u1","compare seeds",body["axes"],1,1,"human:web-v2","matrix",None); launch.assert_called_once_with(self.root,"R-1","u2")

        ai_plan={**plan,"planning_mode":"ai_planned","trial_budget":7,"axes":[],"trials":[],"planning_status":"awaiting_ai"}; prepared["trial_plan"]=ai_plan; prepared["run"]["trial_plan"]=ai_plan
        ai_body={"confirmation":"PREPARE V2 RUN TRIALS","expected_updated":"u1","request":"find an efficient setting","planning_mode":"ai_planned","trial_budget":7,"concurrency":2,"max_retries":1}
        with mock.patch.object(server,"prepare_run_trials_for_steward",return_value=prepared) as prepare_ai, mock.patch.object(server,"prepare_steward_handoff",return_value=handoff):
            status,payload=self.request("POST",path,ai_body)
        self.assertEqual(status,200,payload); self.assertEqual(payload["trial_plan"]["planning_mode"],"ai_planned"); self.assertEqual(payload["handoff_command"],"SAFE TRIAL COMMAND")
        prepare_ai.assert_called_once_with(self.root,"R-1","u1","find an efficient setting",None,2,1,"human:web-v2","ai_planned",7)

    def test_failed_steward_restart_creates_new_attempt_then_returns_handoff(self):
        path=f"/api/v2/p/{self.project}/runs/R-1/steward/restart"
        restarted={"run":{"id":"R-1","updated":"u2","workflow_stage":"ready_to_run","review_status":"approved"},"dispatch":{"dispatch_id":"dispatch-new","status":"queued"}}
        handoff={"run_id":"R-1","handoff_command":"SAFE RESTART COMMAND","execution_started":False,"herdr_invoked":False,"lease_exposed":False,"prompt_used":False}
        with mock.patch.object(server,"restart_failed_run_execution",return_value=restarted) as restart, mock.patch.object(server,"prepare_steward_handoff",return_value=handoff) as prepare:
            status,_=self.request("POST",path,{"expected_updated":"u1"}); self.assertEqual(status,400); restart.assert_not_called()
            status,payload=self.request("POST",path,{"confirmation":"RESTART V2 FAILED RUN","expected_updated":"u1"})
        self.assertEqual(status,200,payload); self.assertEqual(payload["handoff_command"],"SAFE RESTART COMMAND"); self.assertFalse(payload["execution_started"])
        self.assertEqual(payload["dispatch"]["dispatch_id"],"dispatch-new"); self.assertNotIn("token",json.dumps(payload).lower())
        restart.assert_called_once_with(self.root,"R-1","u1","human:web-v2","single"); prepare.assert_called_once_with(self.root,"R-1","u2")

    def test_force_steward_restart_requires_confirmation_and_only_returns_handoff(self):
        path=f"/api/v2/p/{self.project}/runs/R-1/steward/force-restart"; value={"run_id":"R-1","dispatch":{"dispatch_id":"dispatch-safe","status":"running"},"handoff_command":"SAFE REATTACH COMMAND","execution_started":False,"execution_restarted":False,"herdr_invoked":False,"lease_exposed":False,"prompt_used":False}
        with mock.patch.object(server,"force_restart_steward_handoff",return_value=value) as force:
            status,_=self.request("POST",path,{"expected_updated":"u1"}); self.assertEqual(status,400); force.assert_not_called()
            status,payload=self.request("POST",path,{"confirmation":"FORCE RESTART V2 RUN STEWARD","expected_updated":"u1"})
        self.assertEqual(status,200,payload); self.assertEqual(payload["handoff_command"],"SAFE REATTACH COMMAND"); self.assertFalse(payload["execution_started"]); self.assertFalse(payload["execution_restarted"]); self.assertNotIn("token",json.dumps(payload).lower()); force.assert_called_once_with(self.root,"R-1","u1","human:web-v2")

    def test_human_steward_failure_decision_requires_explicit_confirmation(self):
        path=f"/api/v2/p/{self.project}/runs/R-1/steward/mark-failed"; value={"run":{"id":"R-1","workflow_stage":"failed"},"dispatch":{"dispatch_id":"dispatch-safe","status":"failed"},"execution_stopped":False,"remote_process_changed":False}
        with mock.patch.object(server,"mark_steward_attempt_failed",return_value=value) as mark:
            status,_=self.request("POST",path,{"expected_updated":"u1","reason":"人工确认"}); self.assertEqual(status,400); mark.assert_not_called()
            status,payload=self.request("POST",path,{"confirmation":"MARK V2 STEWARD ATTEMPT FAILED","expected_updated":"u1","reason":"人工确认"})
        self.assertEqual(status,200,payload); self.assertFalse(payload["execution_stopped"]); self.assertFalse(payload["remote_process_changed"]); self.assertNotIn("token",json.dumps(payload).lower()); mark.assert_called_once_with(self.root,"R-1","u1","人工确认","human:web-v2")

    def test_failed_run_status_correction_requires_confirmation_and_evidence(self):
        path=f"/api/v2/p/{self.project}/runs/R-1/steward/correct-failed"; value={"run":{"id":"R-1","workflow_stage":"analysis_pending"},"dispatch":{"dispatch_id":"dispatch-safe","status":"completed"},"execution_started":False,"execution_stopped":False,"remote_process_changed":False,"requires_reattach":False}
        body={"confirmation":"CORRECT V2 FAILED RUN STATUS","expected_updated":"u1","target_stage":"analysis_pending","reason":"原失败为监控误判","evidence":"exit 0 and metrics.json"}
        with mock.patch.object(server,"correct_failed_run_state",return_value=value) as correct:
            status,_=self.request("POST",path,{**body,"confirmation":"wrong"}); self.assertEqual(status,400); correct.assert_not_called()
            status,payload=self.request("POST",path,body)
        self.assertEqual(status,200,payload); self.assertEqual(payload["run"]["workflow_stage"],"analysis_pending"); self.assertFalse(payload["remote_process_changed"]); self.assertNotIn("token",json.dumps(payload).lower())
        correct.assert_called_once_with(self.root,"R-1","u1","analysis_pending","原失败为监控误判","exit 0 and metrics.json","human:web-v2")

    def test_project_steward_monitor_is_read_only_and_safe(self):
        value={"items":[{"run_id":"R-1","supervisor":{"phase":"running"},"supervisor_active":True}],"summary":{"total":1,"active":1,"attention":0,"phases":{"running":1}},"remote_probe_performed":False,"lease_exposed":False}
        with mock.patch.object(server,"list_steward_statuses",return_value=value) as listed:
            status,payload=self.request("GET",f"/api/v2/p/{self.project}/stewards")
        self.assertEqual(status,200,payload); self.assertEqual(payload["summary"]["active"],1); self.assertFalse(payload["remote_probe_performed"]); self.assertNotIn("token",json.dumps(payload).lower()); listed.assert_called_once_with(self.root)

    def test_steward_console_delegates_bounded_read(self):
        value={"run_id":"R-1","available":True,"connected":True,"output":"step 2/10\n","source":"owned_tmux_stdout"}
        with mock.patch.object(server,"steward_console",return_value=value) as console:
            status,payload=self.request("GET",f"/api/v2/p/{self.project}/runs/R-1/steward/console")
        self.assertEqual(status,200,payload); self.assertEqual(payload["output"],"step 2/10\n"); console.assert_called_once_with(self.root,"R-1")

    def test_removed_legacy_questions_write_returns_gone_but_keeps_read(self):
        status, payload = self.request("POST", f"/api/p/{self.project}/questions", {"title": "Removed", "question": "Must not write"})
        self.assertEqual(status, 410)
        self.assertEqual(payload["reason"], "legacy_write_removed")
        self.assertEqual(payload["migrated_to"], "/api/v2/p/<project>/questions")
        status, payload = self.request("GET", f"/api/p/{self.project}/questions")
        self.assertEqual(status, 200)
        self.assertIsInstance(payload, list)

    def test_legacy_web_and_codespace_clone_are_removed(self):
        with urllib.request.urlopen(self.base + "/", timeout=5) as response:
            html=response.read().decode("utf-8")
        self.assertEqual(response.status,200); self.assertIn("/v2/assets/",html)
        status,payload=self.request("GET","/static/app.js"); self.assertEqual(status,410); self.assertEqual(payload["migrated_to"],"/v2/")
        status,_=self.request("POST",f"/api/p/{self.project}/clone",{"repo":"example.invalid/repo.git"}); self.assertEqual(status,404)
        self.assertFalse((self.root/"codespace").exists())

    def test_v2_paper_update_hash_merge_and_legacy_freeze(self):
        notes=self.root/"shell/03_evidence/papers"; notes.mkdir(parents=True)
        citekey="doe2026paper"; note=notes/f"{citekey}.md"
        note.write_text(f"# [[{citekey}]] — Paper\n\nOriginal prose.\n",encoding="utf-8")
        expected="sha256:"+hashlib.sha256(note.read_text(encoding="utf-8").encode()).hexdigest()
        seven={key:("Method details" if index==1 else "") for index,key in enumerate(server.SEVENQ)}
        annotation={"citekey":citekey,"fig":"Fig.1","src":"images/figure.png","note":"Key result","boxes":[[1,2,3,4]]}
        path=f"/api/v2/p/{self.project}/papers/{citekey}"
        status,payload=self.request("PUT",path,{"confirmation":"UPDATE V2 PAPER","expected_hash":expected,"seven":seven,"annotations":[annotation],"state":{"triage":"deep"}})
        self.assertEqual(status,200,payload); self.assertEqual(payload["paper"]["seven"][server.SEVENQ[1]],"Method details"); self.assertEqual(payload["paper"]["annotations"][0]["note"],"Key result")
        status,conflict=self.request("PUT",path,{"confirmation":"UPDATE V2 PAPER","expected_hash":expected,"seven":seven})
        self.assertEqual(status,409); self.assertEqual(conflict["reason"],"content_hash_conflict")
        current=payload["paper"]["_canonical_rev"]; before=note.read_text(encoding="utf-8")
        status,state_only=self.request("PUT",path,{"confirmation":"UPDATE V2 PAPER","expected_hash":current,"state":{"triage":"skim"}})
        self.assertEqual(status,200,state_only); self.assertEqual(note.read_text(encoding="utf-8"),before); self.assertEqual(state_only["paper"]["seven"][server.SEVENQ[1]],"Method details")
        status,removed=self.request("PUT",f"/api/p/{self.project}/paper/{citekey}",{"state":{"triage":"deep"}})
        self.assertEqual(status,410); self.assertEqual(removed["reason"],"legacy_write_removed")
        status,_=self.request("GET",f"/api/p/{self.project}/paper/{citekey}"); self.assertEqual(status,200)

    def test_paper_seven_import_preview_is_parse_only(self):
        citekey="preview2026"; note=server.note_path(self.root,citekey)
        text=f"""---
target_type: question
target_id: other-paper
target_address: paper:other-paper
---
### {server.SEVENQ[0]}
First parsed answer.
### {server.SEVENQ[3]}
Fourth parsed answer.
"""
        path=f"/api/v2/p/{self.project}/papers/{citekey}/seven/import-preview"
        status,payload=self.request("POST",path,{"text":text})
        self.assertEqual(status,200,payload); self.assertEqual(payload["parsed_count"],2); self.assertEqual(payload["answers"][server.SEVENQ[0]],"First parsed answer."); self.assertTrue(payload["warnings"]); self.assertFalse(note.exists())
        status,_=self.request("POST",path,{"text":""}); self.assertEqual(status,400)
        status,_=self.request("POST",path,{"text":"x"*(256*1024+1)}); self.assertEqual(status,400); self.assertFalse(note.exists())

    def test_v2_idea_write_conflict_and_legacy_freeze(self):
        path=f"/api/v2/p/{self.project}/ideas"
        status,payload=self.request("POST",path,{"confirmation":"CREATE V2 IDEA","idea":{"title":"Native idea","hypothesis":"Initial hypothesis"}})
        self.assertEqual(status,200,payload); idea=payload["idea"]; self.assertTrue(idea["id"].startswith("I-")); self.assertTrue(idea["_canonical_rev"].startswith("sha256:"))
        update=f"{path}/{idea['id']}"
        status,updated=self.request("PUT",update,{"confirmation":"UPDATE V2 IDEA","expected_hash":idea["_canonical_rev"],"fields":{"title":"Updated idea","method":"Test method","created":"client override"}})
        self.assertEqual(status,200,updated); self.assertEqual(updated["idea"]["title"],"Updated idea"); self.assertEqual(updated["idea"]["method"],"Test method"); self.assertNotEqual(updated["idea"].get("created"),"client override")
        status,conflict=self.request("PUT",update,{"confirmation":"UPDATE V2 IDEA","expected_hash":idea["_canonical_rev"],"fields":{"title":"Stale"}})
        self.assertEqual(status,409); self.assertEqual(conflict["reason"],"content_hash_conflict")
        status,removed=self.request("POST",f"/api/p/{self.project}/ideas",{"title":"Legacy"}); self.assertEqual(status,410); self.assertEqual(removed["reason"],"legacy_write_removed")
        status,removed=self.request("PUT",f"/api/p/{self.project}/idea/{idea['id']}",{"fields":{"title":"Legacy"}}); self.assertEqual(status,410); self.assertEqual(removed["reason"],"legacy_write_removed")
        status,ideas=self.request("GET",f"/api/p/{self.project}/ideas"); self.assertEqual(status,200); self.assertEqual(ideas[0]["title"],"Updated idea")

    def test_v2_intake_save_materialize_and_legacy_freeze(self):
        status,initial=self.request("GET",f"/api/p/{self.project}/intake"); self.assertEqual(status,200)
        path=f"/api/v2/p/{self.project}/intake"
        data={"project_name":"Native intake","project_slug":"native-intake","repo_path":"/repo","idea":"Test intake","domain":"systems","target_venue":"Venue","polite_email":"contact@example.com","seed_papers":["paper-a"],"constraints":["none"],"notes":"operator note"}
        status,saved=self.request("PUT",path,{"confirmation":"UPDATE V2 INTAKE","expected_hash":initial["_canonical_rev"],"data":data})
        self.assertEqual(status,200,saved); self.assertEqual(saved["intake"]["seed_papers"],["paper-a"]); self.assertEqual(saved["intake"]["notes"],"operator note")
        status,conflict=self.request("PUT",path,{"confirmation":"UPDATE V2 INTAKE","expected_hash":initial["_canonical_rev"],"data":data})
        self.assertEqual(status,409); self.assertEqual(conflict["reason"],"content_hash_conflict")
        materialize=f"{path}/materialize"
        with mock.patch("server.materialize",return_value={"returncode":0,"stdout":"done","stderr":""}) as runner:
            status,_=self.request("POST",materialize,{"confirmation":"wrong","expected_hash":saved["intake"]["_canonical_rev"]}); self.assertEqual(status,400)
            status,_=self.request("POST",materialize,{"confirmation":"MATERIALIZE V2 INTAKE","expected_hash":initial["_canonical_rev"]}); self.assertEqual(status,409)
            status,result=self.request("POST",materialize,{"confirmation":"MATERIALIZE V2 INTAKE","expected_hash":saved["intake"]["_canonical_rev"]})
            self.assertEqual(status,200,result); self.assertEqual(result["materialize"]["stdout"],"done"); runner.assert_called_once_with(self.root)
        status,removed=self.request("POST",f"/api/p/{self.project}/intake",{"data":data,"action":"materialize"}); self.assertEqual(status,410); self.assertEqual(removed["reason"],"legacy_write_removed")
        status,current=self.request("GET",f"/api/p/{self.project}/intake"); self.assertEqual(status,200); self.assertEqual(current["project_name"],"Native intake")

    def test_experiment_handoff_confirmation_is_visible_and_scoped(self):
        proposal={"objective":"Test mechanism","implementation_scope":"Add focused hook","evaluation":"Compare clean and patched"}
        handoff={"contract":"survey-tool.experiment-handoff/v1","experiment_id":"E-012","proposal":proposal,"verified_facts":[],"questions":[{"key":"budget","label":"Budget?"}],"risks":[]}
        server.write_tool_json(self.root,"experiments.json",[{"id":"E-012","title":"Handoff","workflow_stage":"awaiting_confirmation","updated":"v1","agent_handoff":handoff}])
        server.write_tool_json(self.root,"runs.json",[])
        url=f"/api/v2/p/{self.project}/experiments/E-012/handoff/confirm"
        payload={"confirmation":"CONFIRM EXPERIMENT HANDOFF","expected_updated":"v1","expected_handoff":handoff,"proposal":proposal,"answers":{}}
        status,_=self.request("POST",url,payload); self.assertEqual(status,400)
        payload["answers"]={"budget":"20 samples"}
        status,_=self.request("POST",url,{**payload,"expected_handoff":{**handoff,"risks":["stale"]}}); self.assertEqual(status,409)
        status,result=self.request("POST",url,payload); self.assertEqual(status,200,result)
        self.assertEqual(result["experiment"]["workflow_stage"],"confirmed")
        self.assertEqual(result["experiment"]["user_answers"],{"budget":"20 samples"})
        self.assertEqual(result["experiment"]["implementation_scope"],proposal["implementation_scope"])
        self.assertEqual(result["dashboard"]["runs"],[])
        self.assertFalse(result["execution_started"])
        status,_=self.request("POST",url,payload); self.assertEqual(status,409)

    def test_v2_experiment_and_run_create_update_with_cas(self):
        server.write_tool_json(self.root,"servers.json",[])
        server.write_tool_json(self.root,"workspaces.json",[{"id":"W","server_id":"","remote_repo":"/repo","remote_experiment_root":"/experiments"}])
        path=f"/api/v2/p/{self.project}/experiments"
        status,payload=self.request("POST",path,{"confirmation":"CREATE V2 EXPERIMENT","experiment":{"id":"E-101","title":"Facade experiment","objective":"Test facade","workspace_id":"W","run_groups":[{"id":"base","name":"Baseline","description":"Control","color":"#336699"}]}})
        self.assertEqual(status,200,payload); exp=payload["experiment"]; self.assertEqual(exp["id"],"E-101")
        status,updated=self.request("PUT",f"{path}/E-101",{"confirmation":"UPDATE V2 EXPERIMENT","expected_updated":exp["updated"],"fields":{"objective":"Updated objective","status":"completed"}})
        self.assertEqual(status,200,updated); self.assertEqual(updated["experiment"]["objective"],"Updated objective"); self.assertNotEqual(updated["experiment"]["status"],"completed")
        status,conflict=self.request("PUT",f"{path}/E-101",{"confirmation":"UPDATE V2 EXPERIMENT","expected_updated":"stale","fields":{"title":"stale"}}); self.assertEqual(status,409); self.assertEqual(conflict["reason"],"registry_version_conflict")
        run_path=f"{path}/E-101/runs"; run_spec={"id":"run-facade","variant":"baseline","group_id":"base","research_question":"Does it work?","purpose":"Test one change","hypothesis":"It works","metric_plan":"Inspect registered metric","data_definition":"Fixed sample","variables_controls":"One variable","workspace_id":"W"}
        status,created=self.request("POST",run_path,{"confirmation":"CREATE V2 RUN","run":run_spec})
        self.assertEqual(status,200,created); run=created["run"]; self.assertEqual(run["workflow_version"],2)
        status,run_updated=self.request("PUT",f"/api/v2/p/{self.project}/runs/run-facade",{"confirmation":"UPDATE V2 RUN","expected_updated":run["updated"],"fields":{"notes":"Facade note","status":"done","review_status":"approved"}})
        self.assertEqual(status,200,run_updated); self.assertEqual(run_updated["run"]["notes"],"Facade note"); self.assertEqual(run_updated["run"]["review_status"],"draft")
        status,_=self.request("PUT",f"/api/v2/p/{self.project}/runs/run-facade",{"confirmation":"UPDATE V2 RUN","expected_updated":"stale","fields":{"notes":"stale"}}); self.assertEqual(status,409)

    def test_v2_run_review_real_state_machine_returns_fresh_dashboard(self):
        server.write_tool_json(self.root,"servers.json",[{"id":"S-01","ssh_host":"gpu"}])
        server.write_tool_json(self.root,"workspaces.json",[{"id":"W-01","server_id":"S-01","remote_repo":"/repo","remote_data_root":"/data","remote_worktree_root":"/repo","remote_experiment_root":"/experiments","environment_policy":{"allowed_write_roots":["/repo","/experiments"],"read_only_roots":["/data"],"forbidden_paths":["/repo/.git"],"forbidden_operations":[],"default_deny_write":True}}])
        server.create_experiment(self.root,{"title":"Lifecycle","objective":"Validate API","workspace_id":"W-01","metric_definitions":[{"id":"accuracy","name":"Accuracy","formula":"correct / total","meaning":"Correct sample ratio","direction":"higher","unit":"ratio","aggregation":"mean","scope":"fixed evaluation set"}]},"E-401")
        run=server.create_run(self.root,"E-401",{"workflow_version":2,"variant":"Facade","purpose":"Compare a controlled condition","research_question":"Does it improve accuracy?","metric_plan":"Use accuracy","data_definition":"Fixed set","variables_controls":"One changed variable","workspace_id":"W-01"},"R-real-review")
        server.update_run(self.root,run["id"],{"architecture_plan":"Shared package plus thin launcher","implementation_ref":{"schema":"survey-tool.run-implementation/v1","package_root":"pkg","entrypoint":"pkg.train","config_path":"configs/run.yaml","launcher_path":"scripts/run.sh","reused_modules":[],"added_modules":[],"tests":["tests/test_train.py"]},"command":"python3 train.py","project_dir":"/repo","artifact_dir":"/experiments/R-real-review"}); run=next(item for item in server.experiment_data(self.root)["runs"] if item["id"]==run["id"])
        review=f"/api/v2/p/{self.project}/runs/{run['id']}/review"
        status,payload=self.request("POST",review,{"action":"authorize_execution","confirmation":"AUTHORIZE V2 RUN EXECUTION","expected_updated":run["updated"]}); self.assertEqual(status,200,payload); run=payload["run"]
        self.assertTrue(payload["direct_steward"]); self.assertEqual((run["review_status"],run["workflow_stage"]),("approved","ready_to_run")); self.assertTrue(run["execution_authorized_at"]); self.assertEqual(payload["dispatch"]["status"],"queued")

    def test_v2_run_review_facade_confirmation_cas_and_call(self):
        server.write_tool_json(self.root,"experiments.json",[{"id":"E-201","title":"Mock facade","objective":"Test response"}])
        server.write_tool_json(self.root,"runs.json",[{"id":"run-review","experiment_id":"E-201","updated":"v1","review_status":"draft"}])
        path=f"/api/v2/p/{self.project}/runs/run-review/review"
        with mock.patch("server.review_run",return_value={"runs":[{"id":"run-review","updated":"v2","review_status":"pending_review"}]}) as review:
            status,_=self.request("POST",path,{"action":"submit","confirmation":"wrong","expected_updated":"v1"}); self.assertEqual(status,400)
            status,conflict=self.request("POST",path,{"action":"submit","confirmation":"SUBMIT V2 RUN REVIEW","expected_updated":"stale"}); self.assertEqual(status,409); self.assertEqual(conflict["reason"],"registry_version_conflict")
            status,payload=self.request("POST",path,{"action":"submit","confirmation":"SUBMIT V2 RUN REVIEW","expected_updated":"v1","requirements":"","questions":""})
            self.assertEqual(status,200,payload); self.assertEqual(payload["run"]["review_status"],"draft"); self.assertIn("runs",payload["dashboard"])
            review.assert_called_once_with(self.root,"run-review","submit","","","human:web-v2","")
        workflow_path=f"/api/v2/p/{self.project}/runs/run-review/workflow"
        with mock.patch("server.advance_run_workflow",return_value={"run":{"id":"run-review","updated":"v2","workflow_stage":"code_planning"},"runs":[]}) as advance:
            status,_=self.request("POST",workflow_path,{"action":"confirm-design","confirmation":"wrong","expected_updated":"v1"}); self.assertEqual(status,400)
            status,payload=self.request("POST",workflow_path,{"action":"confirm-design","confirmation":"CONFIRM V2 RUN DESIGN","expected_updated":"v1","result_fields":{"result_analysis":"ignored","forbidden":"ignored"}})
            self.assertEqual(status,200,payload); self.assertEqual(payload["run"]["workflow_stage"],"code_planning")
            advance.assert_called_once_with(self.root,"run-review","confirm-design","human:web-v2",{"result_analysis":"ignored"})
            status,conflict=self.request("POST",workflow_path,{"action":"confirm-design","confirmation":"CONFIRM V2 RUN DESIGN","expected_updated":"stale"}); self.assertEqual(status,409); self.assertEqual(conflict["reason"],"registry_version_conflict")

    def test_v2_ai_run_grouping_preview_and_safe_apply(self):
        server.write_tool_json(self.root,"experiments.json",[{"id":"E-302","title":"Grouping","objective":"Separate duties","updated":"v1","run_groups":[{"id":"base","name":"基线"}]}])
        server.write_tool_json(self.root,"runs.json",[{"id":"R-free","experiment_id":"E-302","group_id":"","review_status":"draft"},{"id":"R-locked","experiment_id":"E-302","group_id":"base","review_status":"approved"}])
        preview=f"/api/v2/p/{self.project}/experiments/E-302/run-grouping/ai-prompt-preview"; offline=mock.Mock(); offline.proc=None; offline.is_streaming=False
        with mock.patch("server.bridge_for",return_value=offline):
            status,payload=self.request("POST",preview,{})
        self.assertEqual(status,200,payload); self.assertEqual(payload["contract"],"survey-tool.run-grouping/v1"); self.assertTrue(payload["read_only"]); self.assertIn("R-free",payload["prompt"]); self.assertIn("不可信研究数据",payload["prompt"])
        apply=f"/api/v2/p/{self.project}/experiments/E-302/run-grouping/ai-apply"; proposal={"groups":[{"id":"analysis","name":"分析"}],"assignments":{"R-free":"analysis","R-locked":"analysis"}}
        status,payload=self.request("PUT",apply,{"confirmation":"wrong","expected_updated":"v1",**proposal}); self.assertEqual(status,400)
        status,payload=self.request("PUT",apply,{"confirmation":"APPLY V2 AI RUN GROUPING","expected_updated":"stale",**proposal}); self.assertEqual(status,409); self.assertEqual(payload["reason"],"registry_version_conflict")
        status,payload=self.request("PUT",apply,{"confirmation":"APPLY V2 AI RUN GROUPING","expected_updated":"v1",**proposal}); self.assertEqual(status,200,payload)
        self.assertEqual(payload["grouping_result"]["totals"]["applied"],1); self.assertEqual(payload["grouping_result"]["totals"]["skipped"],1)
        runs={item["id"]:item for item in server.experiment_data(self.root)["runs"]}; self.assertEqual(runs["R-free"]["group_id"],"analysis"); self.assertEqual(runs["R-locked"]["group_id"],"base")

    def test_v2_ai_discussion_publish_sync_and_pi_facades(self):
        server.write_tool_json(self.root,"experiments.json",[{"id":"E-301","title":"AI discussion","workflow_stage":"draft"}])
        server.write_tool_json(self.root,"runs.json",[{"id":"run-ai","experiment_id":"E-301","workflow_version":2,"workflow_stage":"research_design","review_status":"draft"}])
        preview_path=f"/api/v2/p/{self.project}/ai/discussion-prompt-preview"
        published={"githubUrl":"https://github.com/example/research","commitSha":"abc123","publishedAt":"2026-08-16T00:00:00"}
        with mock.patch("server.read_publish",return_value=published), mock.patch("server.gpt_assistant_instruction",return_value={"ok":True,"instruction":"PINNED","repository":published["githubUrl"],"commitSha":"abc123","publish":published}) as instruction:
            status,payload=self.request("POST",preview_path,{"target_type":"run","target_id":"run-ai","mode":"external_gpt","task":"review","request":"Check evidence"})
            self.assertEqual(status,200,payload); self.assertEqual(payload["prompt"],"PINNED"); self.assertTrue(payload["read_only"])
            instruction.assert_called_once(); self.assertEqual(instruction.call_args.args[1],["run:run-ai"]); self.assertEqual(instruction.call_args.args[4]["index"],"field:result")
        with mock.patch("server.read_publish",return_value=published), mock.patch("server.export_repo",return_value={"ok":True,"githubUrl":published["githubUrl"],"commitSha":"abc123"}) as export:
            status,payload=self.request("POST",f"/api/v2/p/{self.project}/publish/sync",{"confirmation":"SYNC V2 PROJECT TO GITHUB","setup":{"github_token":"secret-that-must-not-echo"}})
            self.assertEqual(status,200,payload); self.assertNotIn("secret",json.dumps(payload)); self.assertNotIn("githubToken",export.call_args.args[2]); self.assertTrue(export.call_args.args[2]["includePdfs"])
            status,_=self.request("POST",f"/api/v2/p/{self.project}/publish/sync",{"confirmation":"SYNC V2 PROJECT TO GITHUB","setup":{"repo_name":"--upload-pack=bad","visibility":"internal"}}); self.assertEqual(status,400)
        offline=mock.Mock(); offline.proc=None; offline.is_streaming=False
        with mock.patch("server.bridge_for",return_value=offline), mock.patch("server.ai_discussion_prompt",return_value={"prompt":"SAFE"}) as discussion:
            status,payload=self.request("POST",preview_path,{"target_type":"experiment","target_id":"E-301","mode":"terminal_pi","request":"Next step"}); self.assertEqual(status,200,payload); self.assertFalse(payload["bridge"]["live_bound"])
            status,payload=self.request("POST",preview_path,{"target_type":"experiment","target_id":"E-301","mode":"terminal_pi","task":"code_edit","request":"Change one file"}); self.assertEqual(status,200,payload)
            self.assertEqual(discussion.call_args.args[4],"code_edit")
            status,payload=self.request("POST",preview_path,{"target_type":"run","target_id":"run-ai","mode":"terminal_pi","task":"run_implementation","request":"Implement and debug"}); self.assertEqual(status,200,payload)
            self.assertEqual(discussion.call_args.args[4],"run_implementation")
            status,_=self.request("POST",preview_path,{"target_type":"experiment","target_id":"E-301","mode":"terminal_pi","task":"run_implementation","request":"bad target"}); self.assertEqual(status,400)
            status,_=self.request("POST",preview_path,{"target_type":"experiment","target_id":"E-301","mode":"external_gpt","task":"code_edit","request":"Change one file"}); self.assertEqual(status,400)
        self.request("POST",f"/api/v2/p/{self.project}/initialize",{"confirmation":"INITIALIZE SURVEY TOOL 2.0"})
        status,payload=self.request("POST",f"/api/v2/p/{self.project}/herdr-launch-requests",{"confirmation":"CREATE HERDR LAUNCH REQUEST DRAFT","launch_request":{"target_object_id":"run-ai","agent_kind":"pi","task_type":"run_implementation","task_summary":"Implement and debug this Run","safe_config":{"reasoning_effort":"medium","max_turns":6,"reference_ids":["R-explicit"]}}})
        self.assertEqual(status,201,payload); self.assertEqual(payload["launch_request"]["target_object_id"],"run-ai"); self.assertEqual(payload["launch_request"]["task_type"],"run_implementation")
        self.assertEqual(payload["launch_request"]["safe_config"]["reference_ids"],["R-explicit"])

    def test_external_gpt_can_select_experiment_code_repository_without_research_publish(self):
        server.write_tool_json(self.root,"servers.json",[{"id":"S-code","ssh_host":"gpu"}])
        server.write_tool_json(self.root,"workspaces.json",[{"id":"W-code","server_id":"S-code","remote_repo":"/private/real-code","external_code_url":"https://github.com/example/real-code","external_code_ref":"deadbeef"}])
        server.create_experiment(self.root,{"title":"Code context","objective":"private conclusion must not leak","workspace_id":"W-code","code_repository_workspace_id":"W-code"},"E-401")
        path=f"/api/v2/p/{self.project}/ai/discussion-prompt-preview"
        status,payload=self.request("POST",path,{"target_type":"experiment","target_id":"E-401","mode":"external_gpt","task":"review","request":"Inspect the loader","code_repository_id":"associated"})
        self.assertEqual(status,200,payload); self.assertEqual(payload["context_mode"],"code_repository_only"); self.assertTrue(payload["read_only"])
        self.assertIn("https://github.com/example/real-code",payload["prompt"]); self.assertNotIn("private conclusion",payload["prompt"]); self.assertNotIn("/private/real-code",payload["prompt"])
        status,payload=self.request("POST",path,{"target_type":"experiment","target_id":"E-401","mode":"external_gpt","task":"review","request":"x","code_repository_id":"W-other"})
        self.assertEqual(status,400); self.assertIn("只能引用",payload["error"])
        status,_=self.request("POST",f"/api/v2/p/{self.project}/pi/prompt",{"confirmation":"SEND V2 PROMPT TO PI","message":"SAFE"}); self.assertEqual(status,404)

    def test_v2_paper_and_candidate_ai_discussion_boundaries(self):
        citekey="paper2026"; notes=self.root/"shell/03_evidence/papers"; notes.mkdir(parents=True)
        note=notes/f"{citekey}.md"; note.write_text(f"# [[{citekey}]]\n\n## 七问细读（survey-tool 管理）\n### {server.SEVENQ[0]}\nObserved answer.\n",encoding="utf-8")
        path=f"/api/v2/p/{self.project}/ai/discussion-prompt-preview"; offline=mock.Mock(); offline.proc=None; offline.is_streaming=False
        paper_row={"citekey":citekey,"title":"Real Paper"}
        with mock.patch("survey_tool.integrations.read_papers",return_value=[paper_row]), mock.patch("server.read_papers",return_value=[paper_row]), mock.patch("server.bridge_for",return_value=offline):
            status,payload=self.request("POST",path,{"target_type":"paper","target_id":citekey,"mode":"terminal_pi","task":"question","focus":"seven","request":"What is supported?"})
            self.assertEqual(status,200,payload); self.assertIn(citekey,payload["prompt"]); self.assertIn(str(note),payload["prompt"]); self.assertIn("只读",payload["prompt"]); self.assertIn("不得写 canonical",payload["prompt"])
            status,create_prompt=self.request("POST",path,{"target_type":"paper","target_id":citekey,"mode":"terminal_pi","task":"experiment","focus":"whole","request":"请基于这篇论文创建并登记 E-008 实验"})
            self.assertEqual(status,200,create_prompt); self.assertFalse(create_prompt["read_only"]); self.assertEqual(create_prompt["authority_mode"],"governed_experiment_draft"); self.assertEqual(create_prompt["governed_writes"],["experiment.create_draft"])
            self.assertIn("surveyctl.py",create_prompt["prompt"]); self.assertIn("experiment create",create_prompt["prompt"]); self.assertIn("没有可用 Workspace",create_prompt["prompt"]); self.assertIn("不要再要求",create_prompt["prompt"]); self.assertIn("不得确认方案",create_prompt["prompt"])
            status,read_prompt=self.request("POST",path,{"target_type":"paper","target_id":citekey,"mode":"terminal_pi","task":"experiment","focus":"whole","request":"请规划一个可能的实验"})
            self.assertEqual(status,200,read_prompt); self.assertTrue(read_prompt["read_only"]); self.assertEqual(read_prompt["governed_writes"],[])
            status,_=self.request("POST",path,{"target_type":"paper","target_id":"missing","mode":"terminal_pi","task":"question","focus":"whole","request":"x"}); self.assertEqual(status,404)
            published={"githubUrl":"https://github.com/example/research","commitSha":"abc"}
            with mock.patch("server.read_publish",return_value=published), mock.patch("server.gpt_assistant_instruction",return_value={"ok":True,"instruction":"PINNED"}) as gpt:
                status,payload=self.request("POST",path,{"target_type":"paper","target_id":citekey,"mode":"external_gpt","task":"rewrite","focus":"seven","request":"Draft seven"})
                self.assertEqual(status,200,payload); self.assertEqual(gpt.call_args.args[1],[f"paper:{citekey}"]); self.assertEqual(gpt.call_args.args[4]["index"],"seven:all")
        self.request("POST",f"/api/v2/p/{self.project}/initialize",{"confirmation":"INITIALIZE SURVEY TOOL 2.0"})
        from survey_tool.v2 import V2Store
        V2Store(self.root).create_paper_candidate(object_id="PC-discuss",project_id="PROJECT-test",citekey="candidate",title="Candidate title",source_url="https://example.org/paper",source="openalex")
        with mock.patch("server.bridge_for",return_value=offline):
            status,payload=self.request("POST",path,{"target_type":"paper_candidate","target_id":"PC-discuss","mode":"terminal_pi","task":"review","focus":"evidence","request":"Verify it"})
            self.assertEqual(status,200,payload); self.assertTrue(payload["noncanonical"]); self.assertIn("检索 metadata 不是证据",payload["prompt"])
            status,candidate_create=self.request("POST",path,{"target_type":"paper_candidate","target_id":"PC-discuss","mode":"terminal_pi","task":"experiment","focus":"whole","request":"创建并登记一个实验"})
            self.assertEqual(status,200,candidate_create); self.assertTrue(candidate_create["read_only"]); self.assertEqual(candidate_create["governed_writes"],[])
            status,payload=self.request("POST",path,{"target_type":"paper_candidate","target_id":"PC-discuss","mode":"external_gpt","task":"review","focus":"whole","request":"x"})
            self.assertEqual(status,409); self.assertEqual(payload["reason"],"candidate_not_published")

    def test_v2_question_create_requires_confirmation_and_refreshes_index(self):
        self.request("POST", f"/api/v2/p/{self.project}/initialize", {"confirmation": "INITIALIZE SURVEY TOOL 2.0"})
        path=f"/api/v2/p/{self.project}/questions"
        status,_=self.request("POST",path,{"confirmation":"wrong","question":{"title":"Native question"}})
        self.assertEqual(status,400)
        status,payload=self.request("POST",path,{"confirmation":"CREATE V2 QUESTION","question":{"title":"Native question","question":"What changes?"}})
        self.assertEqual(status,200); self.assertTrue(payload["question"]["id"].startswith("Q-")); self.assertEqual(payload["authority"],"markdown"); self.assertTrue(payload["indexed"])
        status,objects=self.request("GET",f"/api/v2/p/{self.project}/objects")
        self.assertEqual(status,200); self.assertTrue(any(item["id"]==payload["question"]["id"] and item["type"]=="question" for item in objects["objects"]))

    def test_v2_question_update_enforces_canonical_content_hash(self):
        self.request("POST", f"/api/v2/p/{self.project}/initialize", {"confirmation": "INITIALIZE SURVEY TOOL 2.0"})
        status,created=self.request("POST",f"/api/v2/p/{self.project}/questions",{"confirmation":"CREATE V2 QUESTION","question":{"title":"Before","question":"Original"}})
        self.assertEqual(status,200); qid=created["question"]["id"]
        status,questions=self.request("GET",f"/api/p/{self.project}/questions"); self.assertEqual(status,200); self.assertTrue(any(item["id"]==qid for item in questions))
        update=f"/api/v2/p/{self.project}/questions/{qid}"
        status,payload=self.request("PUT",update,{"confirmation":"UPDATE V2 QUESTION","expected_hash":"sha256:wrong","fields":{"title":"After"}})
        self.assertEqual(status,409); self.assertEqual(payload["reason"],"content_hash_conflict")
        canonical=self.root/"shell/01_questions"/f"{qid}.md"; expected="sha256:"+hashlib.sha256(canonical.read_text(encoding="utf-8").encode()).hexdigest()
        status,payload=self.request("PUT",update,{"confirmation":"UPDATE V2 QUESTION","expected_hash":expected,"fields":{"title":"After"}})
        self.assertEqual(status,200); self.assertEqual(payload["question"]["title"],"After"); self.assertEqual(payload["authority"],"markdown"); self.assertTrue(payload["indexed"])

    def test_v2_question_full_fields_and_relation_authorities(self):
        self.request("POST",f"/api/v2/p/{self.project}/initialize",{"confirmation":"INITIALIZE SURVEY TOOL 2.0"})
        base=f"/api/v2/p/{self.project}/questions"; fields={"title":"Relations","question":"What connects?","status":"investigating","current_judgement":"Tentative","investigation":"Check sources","papers":[],"comparisons":[],"findings":[],"experiments":[]}
        status,payload=self.request("POST",base,{"confirmation":"CREATE V2 QUESTION","question":fields}); self.assertEqual(status,200,payload); question=payload["question"]
        status,_=self.request("PUT",f"{base}/{question['id']}",{"confirmation":"UPDATE V2 QUESTION","expected_hash":question["_canonical_rev"],"fields":{"status":"validated","path":"bad"}}); self.assertEqual(status,400)
        papers=self.root/"papers"; papers.mkdir(); (papers/"Relation_Paper_2026.pdf").write_bytes(b"%PDF-test"); citekey=server.read_papers(self.root)[0]["citekey"]; relations=f"{base}/{question['id']}/relations"
        status,added=self.request("POST",relations,{"confirmation":"ADD V2 QUESTION RELATION","expected_hash":question["_canonical_rev"],"target_id":citekey}); self.assertEqual(status,200,added); self.assertIn(citekey,added["question"]["papers"]); self.assertEqual(added["authority"],"question_frontmatter")
        status,stale=self.request("POST",relations,{"confirmation":"ADD V2 QUESTION RELATION","expected_hash":question["_canonical_rev"],"target_id":citekey}); self.assertEqual(status,409,stale)
        status,duplicate=self.request("POST",relations,{"confirmation":"ADD V2 QUESTION RELATION","expected_hash":added["question"]["_canonical_rev"],"target_id":citekey}); self.assertEqual(status,200,duplicate); self.assertEqual(duplicate["relation"]["id"],added["relation"]["id"])
        status,removed=self.request("DELETE",f"{relations}/{added['relation']['id']}",{"confirmation":"REMOVE V2 QUESTION RELATION","expected_hash":added["question"]["_canonical_rev"]}); self.assertEqual(status,200,removed); self.assertNotIn(citekey,removed["question"]["papers"])
        idea_dir=self.root/"shell/00_idea"; idea_dir.mkdir(parents=True); (idea_dir/"idea.md").write_text("# Ideas\n\n## I-01\n- title: Navigation idea\n- status: draft\n",encoding="utf-8"); before=(self.root/question["path"]).read_text(encoding="utf-8")
        status,idea=self.request("POST",relations,{"confirmation":"ADD V2 QUESTION RELATION","expected_hash":removed["question"]["_canonical_rev"],"target_id":"I-01"}); self.assertEqual(status,200,idea); self.assertFalse(idea["canonical_question_modified"]); self.assertEqual((self.root/question["path"]).read_text(encoding="utf-8"),before)
        kernel=self.root/"kernel"; kernel.mkdir(); (kernel/"claims.md").write_text("# Claims\n\n## C01\n- text: Governed claim\n- status: draft\n- human_verdict: pending\n",encoding="utf-8")
        status,claim=self.request("POST",relations,{"confirmation":"ADD V2 QUESTION RELATION","expected_hash":idea["question"]["_canonical_rev"],"target_id":"C01"}); self.assertEqual(status,200,claim); self.assertEqual(server.read_claims(self.root)[0]["status"],"draft")
        offline=mock.Mock(); offline.proc=None; offline.is_streaming=False
        question_before_prompt=(self.root/question["path"]).read_bytes(); claims_before_prompt=(kernel/"claims.md").read_bytes()
        with mock.patch("server.bridge_for",return_value=offline):
            status,prompt=self.request("POST",f"/api/v2/p/{self.project}/ai/discussion-prompt-preview",{"target_type":"question","target_id":question["id"],"mode":"terminal_pi","task":"review","focus":"relations","request":"Review links"})
            self.assertEqual(status,200,prompt); self.assertIn("I-01",prompt["prompt"]); self.assertIn("C01",prompt["prompt"])
            linked={source["source_id"] for source in prompt["context_manifest"]["sources"] if source["role"]=="linked_reference"}
            self.assertIn("idea:I-01",linked); self.assertIn("claim:C01",linked)
        self.assertEqual((self.root/question["path"]).read_bytes(),question_before_prompt); self.assertEqual((kernel/"claims.md").read_bytes(),claims_before_prompt)
        published={"githubUrl":"https://github.com/example/research","commitSha":"abc"}
        with mock.patch("server.read_publish",return_value=published), mock.patch("server.gpt_assistant_instruction",return_value={"ok":True,"instruction":"PINNED"}) as gpt:
            status,payload=self.request("POST",f"/api/v2/p/{self.project}/ai/discussion-prompt-preview",{"target_type":"question","target_id":question["id"],"mode":"external_gpt","task":"review","focus":"relations","request":"Review links"})
            self.assertEqual(status,200,payload); addresses=gpt.call_args.args[1]
            self.assertEqual(addresses[0],f"question:{question['id']}"); self.assertIn("idea:I-01",addresses); self.assertIn("claim:C01",addresses)
        other=self.request("POST",base,{"confirmation":"CREATE V2 QUESTION","question":{"title":"Other","question":"Other question"}})[1]["question"]
        status,foreign=self.request("DELETE",f"{base}/{other['id']}/relations/{claim['relation']['id']}",{"confirmation":"REMOVE V2 QUESTION RELATION","expected_hash":other["_canonical_rev"]}); self.assertEqual(status,404,foreign)
        status,_=self.request("POST",relations,{"confirmation":"ADD V2 QUESTION RELATION","expected_hash":claim["question"]["_canonical_rev"],"target_id":"run-unsupported"}); self.assertEqual(status,404)

    def test_v2_question_ai_discussion_local_and_external(self):
        status,created=self.request("POST",f"/api/v2/p/{self.project}/questions",{"confirmation":"CREATE V2 QUESTION","question":{"title":"AI question","question":"What evidence?","current_judgement":"Uncertain","investigation":"Read sources"}}); self.assertEqual(status,200,created); qid=created["question"]["id"]
        path=f"/api/v2/p/{self.project}/ai/discussion-prompt-preview"; offline=mock.Mock(); offline.proc=None; offline.is_streaming=False
        with mock.patch("server.bridge_for",return_value=offline):
            status,payload=self.request("POST",path,{"target_type":"question","target_id":qid,"mode":"terminal_pi","task":"question","focus":"investigation","request":"What next?"}); self.assertEqual(status,200,payload); self.assertIn("read_only",payload["prompt"]); self.assertIn("Read sources",payload["prompt"]); self.assertIn("不得把草稿晋升为 Finding",payload["prompt"])
        published={"githubUrl":"https://github.com/example/research","commitSha":"abc"}
        with mock.patch("server.read_publish",return_value=published),mock.patch("server.gpt_assistant_instruction",return_value={"ok":True,"instruction":"PINNED"}) as gpt:
            status,payload=self.request("POST",path,{"target_type":"question","target_id":qid,"mode":"external_gpt","task":"review","focus":"judgement","request":"Review"}); self.assertEqual(status,200,payload); self.assertEqual(gpt.call_args.args[1],[f"question:{qid}"]); self.assertEqual(gpt.call_args.args[4]["index"],"field:current_judgement")

    def test_v2_comparison_create_requires_confirmation_and_refreshes_index(self):
        self.request("POST",f"/api/v2/p/{self.project}/initialize",{"confirmation":"INITIALIZE SURVEY TOOL 2.0"})
        path=f"/api/v2/p/{self.project}/comparisons"
        status,_=self.request("POST",path,{"confirmation":"wrong","comparison":{"name":"Native comparison"}}); self.assertEqual(status,400)
        status,payload=self.request("POST",path,{"confirmation":"CREATE V2 COMPARISON","comparison":{"name":"Native comparison","papers":[],"axes":["quality"]}})
        self.assertEqual(status,200); self.assertTrue(payload["comparison"]["id"].startswith("cmp-")); self.assertEqual(payload["authority"],"markdown")
        status,objects=self.request("GET",f"/api/v2/p/{self.project}/objects"); self.assertEqual(status,200)
        self.assertTrue(any(item["id"]==payload["comparison"]["id"] and item["type"]=="comparison" for item in objects["objects"]))

    def test_v2_comparison_update_enforces_canonical_content_hash(self):
        self.request("POST",f"/api/v2/p/{self.project}/initialize",{"confirmation":"INITIALIZE SURVEY TOOL 2.0"})
        status,created=self.request("POST",f"/api/v2/p/{self.project}/comparisons",{"confirmation":"CREATE V2 COMPARISON","comparison":{"name":"Before"}}); self.assertEqual(status,200)
        cid=created["comparison"]["id"]; status,comparisons=self.request("GET",f"/api/p/{self.project}/compares"); self.assertEqual(status,200)
        current=next(item for item in comparisons if item["id"]==cid); path=f"/api/v2/p/{self.project}/comparisons/{cid}"
        status,payload=self.request("PUT",path,{"confirmation":"UPDATE V2 COMPARISON","expected_hash":"wrong","fields":{"name":"After"}})
        self.assertEqual(status,409); self.assertEqual(payload["reason"],"content_hash_conflict")
        status,payload=self.request("PUT",path,{"confirmation":"UPDATE V2 COMPARISON","expected_hash":current["_canonical_rev"],"fields":{"name":"After","mode":"ignored"}})
        self.assertEqual(status,200); self.assertEqual(payload["comparison"]["name"],"After"); self.assertEqual(payload["comparison"]["mode"],"structured")

    def test_v2_finding_create_and_update_enforce_content_hash(self):
        self.request("POST",f"/api/v2/p/{self.project}/initialize",{"confirmation":"INITIALIZE SURVEY TOOL 2.0"})
        status,created=self.request("POST",f"/api/v2/p/{self.project}/comparisons",{"confirmation":"CREATE V2 COMPARISON","comparison":{"name":"Finding parent"}}); self.assertEqual(status,200)
        cid=created["comparison"]["id"]; create_path=f"/api/v2/p/{self.project}/comparisons/{cid}/findings"
        status,payload=self.request("POST",create_path,{"confirmation":"CREATE V2 FINDING","finding":{"text":"Initial finding","source":"paper"}})
        self.assertEqual(status,200); self.assertTrue(payload["finding"]["id"].startswith("F-")); fid=payload["finding"]["id"]
        status,comparisons=self.request("GET",f"/api/p/{self.project}/compares"); self.assertEqual(status,200)
        current=next(finding for comp in comparisons for finding in comp.get("findings",[]) if finding["id"]==fid); update_path=f"/api/v2/p/{self.project}/findings/{fid}"
        status,payload=self.request("PUT",update_path,{"confirmation":"UPDATE V2 FINDING","expected_hash":"wrong","fields":{"text":"Updated finding"}})
        self.assertEqual(status,409); self.assertEqual(payload["reason"],"content_hash_conflict")
        status,payload=self.request("PUT",update_path,{"confirmation":"UPDATE V2 FINDING","expected_hash":current["_canonical_rev"],"fields":{"text":"Updated finding"}})
        self.assertEqual(status,200); self.assertEqual(payload["finding"]["text"],"Updated finding")

    def test_capabilities_expose_only_safe_herdr_discovery_without_initializing(self):
        safe = {"managed": True, "cli_available": True, "codex_supported": True,
                "probe_status": "available", "access": "discovery_only"}
        with mock.patch("survey_tool.v2.store.herdr_capability", return_value=safe):
            status, payload = self.request("GET", f"/api/v2/p/{self.project}/capabilities")
        self.assertEqual(status, 200)
        self.assertEqual(payload["herdr"], safe)
        self.assertEqual(set(payload["herdr"]), {"managed", "cli_available", "codex_supported", "probe_status", "access"})
        self.assertFalse((self.root / ".survey-tool/survey-tool-v2.sqlite3").exists())

    def test_acquisition_requires_confirmation_and_only_queues_staged_jobs(self):
        self.request("POST", f"/api/v2/p/{self.project}/initialize", {"confirmation": "INITIALIZE SURVEY TOOL 2.0"})
        candidate = {
            "citekey": "oa2026candidate", "title": "OA Candidate", "year": "2026",
            "url": "https://openalex.org/W-oa", "oa_url": "https://example.org/paper.pdf", "source": "openalex",
        }
        status, payload = self.request("POST", f"/api/v2/p/{self.project}/paper-candidates", {"candidate": candidate})
        self.assertEqual(status, 201)
        object_id = payload["candidate"]["id"]
        path = f"/api/v2/p/{self.project}/paper-candidates/{object_id}/acquisition"
        status, _ = self.request("POST", path, {"confirmation": "yes", "expected_revision": 1})
        self.assertEqual(status, 400)
        status, payload = self.request("POST", path, {"confirmation": "STAGE PAPER ACQUISITION", "expected_revision": 1})
        self.assertEqual(status, 202)
        self.assertEqual(payload["download_job"]["status"], "queued")
        self.assertEqual(payload["mineru_job"]["depends_on_job_id"], payload["download_job"]["id"])
        self.assertEqual(payload["download_job"]["request"]["destination"], "staging")
        status, jobs = self.request("GET", f"/api/v2/p/{self.project}/jobs?target_object_id={object_id}")
        self.assertEqual(status, 200)
        self.assertEqual(len(jobs["jobs"]), 2)

    def test_canonical_ingest_requires_citekey_confirmation(self):
        self.request("POST", f"/api/v2/p/{self.project}/initialize", {"confirmation": "INITIALIZE SURVEY TOOL 2.0"})
        status, payload = self.request("POST", f"/api/v2/p/{self.project}/paper-candidates", {"candidate": {
            "citekey": "gate2026paper", "title": "Gate", "url": "https://openalex.org/W-gate", "oa_url": "https://example.org/paper.pdf",
        }})
        self.assertEqual(status, 201); candidate = payload["candidate"]
        path = f"/api/v2/p/{self.project}/paper-candidates/{candidate['id']}/ingest"
        with mock.patch("server.ingest_staged_candidate") as ingest:
            status, _ = self.request("POST", path, {"confirmation": "INGEST wrong", "expected_revision": 1})
            self.assertEqual(status, 400); ingest.assert_not_called()
            ingest.return_value = {**candidate, "verification_status": "ingested"}
            status, payload = self.request("POST", path, {"confirmation": "INGEST gate2026paper", "expected_revision": 1})
            self.assertEqual(status, 200)
            self.assertTrue(payload["canonical_write"])
            ingest.assert_called_once()

    def test_job_retry_and_cancel_api_never_start_or_stop_worker(self):
        self.request("POST",f"/api/v2/p/{self.project}/initialize",{"confirmation":"INITIALIZE SURVEY TOOL 2.0"})
        from survey_tool.v2 import V2Store
        store=V2Store(self.root); store.create_object(object_id="PC-api-job",object_type="paper_candidate",project_id="PROJECT-test")
        failed=store.create_job(kind="paper_download",target_object_id="PC-api-job",idempotency_key="api-retry")
        failed=store.transition_job(failed["id"],expected_revision=1,status="running"); failed=store.transition_job(failed["id"],expected_revision=failed["revision"],status="failed",error_message="timeout")
        base=f"/api/v2/p/{self.project}/jobs/{failed['id']}"
        status,_=self.request("POST",base+"/retry",{"confirmation":"yes","expected_revision":failed["revision"],"reason":"network restored"}); self.assertEqual(status,400)
        status,payload=self.request("POST",base+"/retry",{"confirmation":"RETRY FAILED JOB","expected_revision":failed["revision"],"reason":"network restored"})
        self.assertEqual(status,200); self.assertFalse(payload["worker_started"]); queued=payload["jobs"][0]; self.assertEqual(queued["status"],"queued")
        status,payload=self.request("POST",base+"/cancel",{"confirmation":"CANCEL QUEUED JOB","expected_revision":queued["revision"],"reason":"operator cancelled"})
        self.assertEqual(status,200); self.assertFalse(payload["running_process_stopped"]); self.assertEqual(payload["jobs"][0]["status"],"cancelled")

    def test_archive_api_is_soft_confirmed_and_deletes_no_files(self):
        self.request("POST", f"/api/v2/p/{self.project}/initialize", {"confirmation": "INITIALIZE SURVEY TOOL 2.0"})
        from survey_tool.v2 import V2Store
        store=V2Store(self.root); canonical=self.root/"papers/candidate.pdf"; canonical.parent.mkdir(); canonical.write_text("keep",encoding="utf-8")
        store.create_paper_candidate(object_id="PC-archive",project_id="PROJECT-test",citekey="archive",title="Archive",source_url="https://openalex.org/archive")
        path=f"/api/v2/p/{self.project}/objects/archive"; body={"items":[{"id":"PC-archive","expected_revision":1}],"reason":"completed"}
        status,_=self.request("POST",path,{**body,"confirmation":"yes"}); self.assertEqual(status,400)
        status,payload=self.request("POST",path,{**body,"confirmation":"ARCHIVE V2 OBJECTS"})
        self.assertEqual(status,200); self.assertFalse(payload["hard_delete"]); self.assertFalse(payload["canonical_files_deleted"]); self.assertTrue(canonical.exists())
        status,payload=self.request("GET",path); self.assertEqual(status,200); self.assertFalse(payload["hard_delete_available"]); self.assertEqual(payload["objects"][0]["lifecycle_status"],"archived"); self.assertFalse(payload["objects"][0]["impact"]["canonical_files_deleted"])
        status,payload=self.request("POST",path,{"items":[{"id":"PC-archive","expected_revision":2}],"reason":"reopen","restore":True,"confirmation":"RESTORE V2 OBJECTS"})
        self.assertEqual(status,200); self.assertEqual(payload["objects"][0]["lifecycle_status"],"proposed"); self.assertTrue(canonical.exists())

    def test_automation_draft_and_activation_are_separate_confirmed_actions(self):
        self.request("POST", f"/api/v2/p/{self.project}/initialize", {"confirmation": "INITIALIZE SURVEY TOOL 2.0"})
        path = f"/api/v2/p/{self.project}/automations"
        spec = {"automation_type": "research", "target_type": "question", "target_id": "Q-001", "budget": {"duration_minutes": 30, "max_rounds": 5, "interval_minutes": 1}}
        status, _ = self.request("POST", path, {"confirmation": "yes", "automation": spec})
        self.assertEqual(status, 400)
        status, payload = self.request("POST", path, {"confirmation": "CREATE AUTOMATION DRAFT", "automation": spec})
        self.assertEqual(status, 201); self.assertFalse(payload["started"]); automation = payload["automation"]
        transition = f"{path}/{automation['id']}/transition"
        status, payload = self.request("POST", transition, {"confirmation": "SUBMIT AUTOMATION FOR APPROVAL", "expected_revision": 1, "status": "awaiting_approval"})
        self.assertEqual(status, 200); self.assertFalse(payload["execution_started"])
        status, payload = self.request("POST", transition, {"confirmation": "APPROVE AUTOMATION", "expected_revision": 2, "status": "active", "phase": "research"})
        self.assertEqual(status, 200); self.assertEqual(payload["automation"]["lifecycle_status"], "active"); self.assertFalse(payload["execution_started"])
        status, payload = self.request("GET", path)
        self.assertEqual(status, 200); self.assertEqual(len(payload["automations"]), 1)
        self.assertIsNotNone(payload["automations"][0]["deadline_at"])
        self.assertGreaterEqual(len(payload["automations"][0]["events"]), 3)
        status, payload = self.request("POST", transition, {"confirmation": "COMPLETE AUTOMATION", "expected_revision": 3, "status": "completed", "phase": "synthesis"})
        self.assertEqual(status, 200); self.assertEqual(payload["automation"]["lifecycle_status"], "completed"); self.assertFalse(payload["execution_started"])

    def test_herdr_launch_request_requires_human_approval_and_never_executes(self):
        path = f"/api/v2/p/{self.project}/herdr-launch-requests"
        status, payload = self.request("GET", path)
        self.assertEqual(status, 200); self.assertFalse(payload["initialized"])
        self.assertFalse((self.root / ".survey-tool/survey-tool-v2.sqlite3").exists())
        self.request("POST", f"/api/v2/p/{self.project}/initialize", {"confirmation": "INITIALIZE SURVEY TOOL 2.0"})
        from survey_tool.v2 import V2Store
        V2Store(self.root).create_object(object_id="Q-herdr", object_type="question", project_id="PROJECT-test", lifecycle_status="reference")
        spec = {"target_object_id": "Q-herdr", "agent_kind": "codex", "task_type": "analysis", "task_summary": "Check the evidence map", "safe_config": {"reasoning_effort": "medium", "max_turns": 3}}
        status, _ = self.request("POST", path, {"confirmation": "yes", "launch_request": spec})
        self.assertEqual(status, 400)
        status, payload = self.request("POST", path, {"confirmation": "CREATE HERDR LAUNCH REQUEST DRAFT", "launch_request": spec})
        self.assertEqual(status, 201); request = payload["launch_request"]
        self.assertFalse(payload["execution_started"]); self.assertFalse(payload["prompt_stored"]); self.assertFalse(payload["command_stored"])
        transition = f"{path}/{request['id']}/transition"
        status, payload = self.request("POST", transition, {"confirmation": "SUBMIT HERDR LAUNCH REQUEST FOR APPROVAL", "expected_revision": 1, "status": "awaiting_approval"})
        self.assertEqual(status, 200); self.assertFalse(payload["execution_started"]); self.assertFalse(payload["herdr_invoked"])
        status, _ = self.request("POST", transition, {"confirmation": "yes", "expected_revision": 2, "status": "approved"})
        self.assertEqual(status, 400)
        with mock.patch("server.subprocess.Popen") as popen, mock.patch("server.subprocess.run") as run:
            status, payload = self.request("POST", transition, {"confirmation": "APPROVE HERDR LAUNCH REQUEST", "expected_revision": 2, "status": "approved"})
        self.assertEqual(status, 200); self.assertEqual(payload["launch_request"]["lifecycle_status"], "approved")
        self.assertFalse(payload["execution_started"]); self.assertFalse(payload["herdr_invoked"]); popen.assert_not_called(); run.assert_not_called()
        status, payload = self.request("GET", path)
        self.assertEqual(status, 200); self.assertEqual(len(payload["launch_requests"][0]["events"]), 3)
        forbidden = {"prompt", "messages", "pane_id", "workspace_id", "tab_id", "session_id", "cwd", "environment", "command"}
        self.assertTrue(forbidden.isdisjoint(payload["launch_requests"][0]))
        self.assertEqual(set(payload["launch_requests"][0]) - {"events"}, {"id", "lifecycle_status", "revision", "target_object_id", "agent_kind", "task_type", "task_summary", "safe_config", "approved_at", "created_at", "updated_at"})

    def test_herdr_execution_authorize_list_and_revoke_are_record_only(self):
        executions=f"/api/v2/p/{self.project}/herdr-executions"
        status,payload=self.request("GET",executions); self.assertEqual(status,200); self.assertFalse(payload["initialized"])
        self.assertFalse((self.root/".survey-tool/survey-tool-v2.sqlite3").exists())
        self.request("POST",f"/api/v2/p/{self.project}/initialize",{"confirmation":"INITIALIZE SURVEY TOOL 2.0"})
        from survey_tool.v2 import V2Store
        store=V2Store(self.root); store.create_object(object_id="Q-authorize",object_type="question",project_id="PROJECT-test")
        store.create_herdr_launch_request(object_id="HLR-authorize",project_id="PROJECT-test",target_object_id="Q-authorize",agent_kind="codex",task_type="analysis",task_summary="Review evidence")
        store.transition_herdr_launch_request("HLR-authorize",expected_revision=1,status="awaiting_approval"); store.transition_herdr_launch_request("HLR-authorize",expected_revision=2,status="approved")
        authorize=f"/api/v2/p/{self.project}/herdr-launch-requests/HLR-authorize/authorize"
        status,_=self.request("POST",authorize,{"confirmation":"wrong","expected_request_revision":3}); self.assertEqual(status,400)
        unavailable={"herdr":{"managed":False,"cli_available":True,"codex_supported":True}}
        with mock.patch("server.v2_capabilities",return_value=unavailable):
            status,_=self.request("POST",authorize,{"confirmation":"AUTHORIZE HERDR EXECUTION HLR-authorize","expected_request_revision":3})
        self.assertEqual(status,409)
        available={"herdr":{"managed":True,"cli_available":True,"codex_supported":True}}
        with mock.patch("server.v2_capabilities",return_value=available),mock.patch("server.subprocess.Popen") as popen,mock.patch("server.subprocess.run") as run:
            status,payload=self.request("POST",authorize,{"confirmation":"AUTHORIZE HERDR EXECUTION HLR-authorize","expected_request_revision":3,"ttl_seconds":120})
        self.assertEqual(status,201); execution=payload["execution"]; self.assertFalse(payload["execution_started"]); self.assertFalse(payload["herdr_invoked"]); popen.assert_not_called(); run.assert_not_called()
        allowed={"id","state","revision","launch_request_id","target_object_id","approved_request_revision","not_after","attempt","safe_runtime","authorized_at","revoked_at","created_at","updated_at"}
        self.assertEqual(set(execution),allowed); self.assertEqual(execution["state"],"authorized"); self.assertEqual(execution["approved_request_revision"],3)
        self.assertFalse({"authorization_nonce_hash","approved_snapshot_hash","lease_owner","lease_token_hash","internal_agent_name","session_fingerprint","project_id","created_by_id"}&set(execution))
        with mock.patch("server.v2_capabilities",return_value=available):
            status,_=self.request("POST",authorize,{"confirmation":"AUTHORIZE HERDR EXECUTION HLR-authorize","expected_request_revision":3})
        self.assertEqual(status,409)
        revoke=f"{executions}/{execution['id']}/revoke"
        status,_=self.request("POST",revoke,{"confirmation":f"REVOKE HERDR EXECUTION {execution['id']}","expected_execution_revision":2}); self.assertEqual(status,409)
        with mock.patch("server.subprocess.Popen") as popen,mock.patch("server.subprocess.run") as run:
            status,payload=self.request("POST",revoke,{"confirmation":f"REVOKE HERDR EXECUTION {execution['id']}","expected_execution_revision":1})
        self.assertEqual(status,200); self.assertEqual(payload["execution"]["state"],"revoked"); self.assertFalse(payload["execution_started"]); self.assertFalse(payload["herdr_invoked"]); popen.assert_not_called(); run.assert_not_called()
        status,payload=self.request("GET",executions); self.assertEqual(status,200); self.assertEqual(len(payload["executions"][0]["events"]),2)
        self.assertEqual(set(payload["executions"][0]["events"][0]),{"id","kind","occurred_at","from_revision","to_revision","summary","details"})

    def test_agent_binding_uses_verified_snapshot_and_copies_no_conversation(self):
        self.request("POST", f"/api/v2/p/{self.project}/initialize", {"confirmation": "INITIALIZE SURVEY TOOL 2.0"})
        from survey_tool.v2 import V2Store
        store = V2Store(self.root)
        store.create_object(object_id="Q-bind", object_type="question", project_id="PROJECT-test")
        path = f"/api/v2/p/{self.project}/agent-sessions/bind-current-pi"
        with mock.patch("server.read_pi_binding", return_value={"session_id": "stable-pi-id", "messages": ["secret"], "prompt": "secret"}):
            status, _ = self.request("POST", path, {"confirmation": "yes", "object_id": "Q-bind", "task_type": "research"})
            self.assertEqual(status, 400)
            status, payload = self.request("POST", path, {"confirmation": "BIND CURRENT PI SESSION", "object_id": "Q-bind", "task_type": "research"})
            self.assertEqual(status, 201, payload)
            self.assertFalse(payload["messages_copied"]); self.assertFalse(payload["prompt_copied"])
            self.assertTrue(payload["session"]["identity_fingerprint"].startswith("sha256:"))
            self.assertNotIn("external_ref",payload["session"])
            self.assertNotIn("messages", payload["session"]); self.assertNotIn("prompt", payload["session"])
            self.assertFalse(payload["session_path_copied"])
        status, payload = self.request("GET", f"/api/v2/p/{self.project}/agent-sessions")
        self.assertEqual(status, 200); self.assertEqual(len(payload["sessions"]), 1)
        self.assertNotIn("external_ref",payload["sessions"][0]); self.assertFalse(payload["current_pi"]["messages_exposed"])

    def test_agent_binding_creates_reference_identity_without_copying_legacy_authority(self):
        self.request("POST",f"/api/v2/p/{self.project}/initialize",{"confirmation":"INITIALIZE SURVEY TOOL 2.0"})
        questions=self.root/"shell/01_questions"; questions.mkdir(parents=True); source=questions/"Q-legacy.md"; original="---\nid: Q-legacy\ntitle: Legacy Question\n---\n# Legacy\n\nsecret prose\n"; source.write_text(original,encoding="utf-8")
        with mock.patch("server.read_pi_binding",return_value={"session_id":"legacy-session","session_name":"Verified"}):
            status,payload=self.request("POST",f"/api/v2/p/{self.project}/agent-sessions/bind-current-pi",{"confirmation":"BIND CURRENT PI SESSION","object_id":"Q-legacy","task_type":"research"})
        self.assertEqual(status,201,payload); self.assertTrue(payload["target"]["reference_identity_only"]); self.assertEqual(payload["target"]["authority"],"markdown"); self.assertEqual(source.read_text(encoding="utf-8"),original)
        from survey_tool.v2 import V2Store
        target=V2Store(self.root).get_object("Q-legacy"); self.assertEqual(target["lifecycle_status"],"reference"); self.assertEqual(target["canonical_path"],"shell/01_questions/Q-legacy.md")

    def test_agent_binding_requires_existing_verified_snapshot(self):
        self.request("POST", f"/api/v2/p/{self.project}/initialize", {"confirmation": "INITIALIZE SURVEY TOOL 2.0"})
        with mock.patch("server.read_pi_binding", return_value={}):
            status, payload = self.request("POST", f"/api/v2/p/{self.project}/agent-sessions/bind-current-pi", {"confirmation": "BIND CURRENT PI SESSION", "object_id": "Q-none"})
        self.assertEqual(status, 409); self.assertIn("verified", payload["error"])

    def test_migration_dry_run_does_not_initialize_store(self):
        status, payload = self.request("GET", f"/api/v2/p/{self.project}/migration/dry-run")
        self.assertEqual(status, 200)
        self.assertFalse(payload["will_write"])
        self.assertFalse(payload["v2_store"]["initialized"])
        self.assertEqual(payload["identity_index_history"], [])
        self.assertFalse((self.root / ".survey-tool/survey-tool-v2.sqlite3").exists())

    def test_identity_index_apply_requires_initialized_store_and_confirmation(self):
        questions = self.root / "shell/01_questions"
        questions.mkdir(parents=True)
        source = questions / "Q-api-migration.md"
        original = "---\nid: Q-api-migration\ntitle: API migration\n---\nprivate prose\n"
        source.write_text(original, encoding="utf-8")
        path = f"/api/v2/p/{self.project}/migration/identity-index/apply"

        status, _ = self.request("POST", path, {"confirmation": "APPLY IDENTITY INDEX MIGRATION"})
        self.assertEqual(status, 409)
        self.assertFalse((self.root / ".survey-tool/survey-tool-v2.sqlite3").exists())
        self.request("POST", f"/api/v2/p/{self.project}/initialize", {"confirmation": "INITIALIZE SURVEY TOOL 2.0"})
        status, _ = self.request("POST", path, {"confirmation": "yes"})
        self.assertEqual(status, 400)

        status, payload = self.request("POST", path, {"confirmation": "APPLY IDENTITY INDEX MIGRATION"})
        self.assertEqual(status, 200)
        self.assertEqual(payload["created"], 1)
        self.assertFalse(payload["authority_changed"])
        self.assertFalse(payload["canonical_files_modified"])
        self.assertEqual(source.read_text(encoding="utf-8"), original)
        status, repeated = self.request("POST", path, {"confirmation": "APPLY IDENTITY INDEX MIGRATION"})
        self.assertEqual(status, 200)
        self.assertEqual(repeated["created"], 0)
        self.assertEqual(repeated["existing"], 1)

    def test_content_index_apply_requires_initialized_store_and_confirmation(self):
        (self.root / "papers").mkdir(exist_ok=True)
        (self.root / "papers" / "Zeta Paper_2024.pdf").write_bytes(b"%PDF-zeta")
        path = f"/api/v2/p/{self.project}/migration/content-index/apply"
        status, _ = self.request("POST", path, {"confirmation": "APPLY CONTENT INDEX MIGRATION"})
        self.assertEqual(status, 409)
        self.request("POST", f"/api/v2/p/{self.project}/initialize", {"confirmation": "INITIALIZE SURVEY TOOL 2.0"})
        status, _ = self.request("POST", path, {"confirmation": "wrong"})
        self.assertEqual(status, 400)
        status, payload = self.request("POST", path, {"confirmation": "APPLY CONTENT INDEX MIGRATION"})
        self.assertEqual(status, 200)
        self.assertGreaterEqual(payload["created"], 1)
        self.assertFalse(payload["authority_changed"])
        self.assertFalse(payload["canonical_files_modified"])

    def test_objects_endpoint_is_read_only_and_lists_native_objects(self):
        status, payload = self.request("GET", f"/api/v2/p/{self.project}/objects")
        self.assertEqual(status, 200)
        self.assertFalse(payload["initialized"])
        self.assertEqual(payload["objects"], [])
        self.request("POST", f"/api/v2/p/{self.project}/initialize", {"confirmation": "INITIALIZE SURVEY TOOL 2.0"})
        (self.root / "papers").mkdir(exist_ok=True)
        (self.root / "papers" / "Zeta Paper_2024.pdf").write_bytes(b"%PDF-zeta")
        (self.root / ".survey-tool" / "compares.json").write_text(json.dumps([{"id": "cmp-zeta", "name": "Zeta", "papers": ["zetapape2024"]}]), encoding="utf-8")
        status, applied = self.request("POST", f"/api/v2/p/{self.project}/migration/content-index/apply", {"confirmation": "APPLY CONTENT INDEX MIGRATION"})
        self.assertEqual(status, 200)
        self.assertGreaterEqual(applied["created"], 2)
        status, payload = self.request("GET", f"/api/v2/p/{self.project}/objects")
        self.assertEqual(status, 200)
        self.assertTrue(payload["initialized"])
        self.assertIn("paper", payload["summary"])
        self.assertIn("comparison", payload["summary"])
        self.assertGreaterEqual(len(payload["relations"]), 1)

    def test_candidate_requires_initialized_store_and_persists(self):
        candidate = {
            "citekey": "doe2026candidate",
            "title": "Candidate",
            "authors": ["Jane Doe"],
            "year": "2026",
            "url": "https://openalex.org/W1",
            "source": "openalex",
        }
        status, _ = self.request(
            "POST", f"/api/v2/p/{self.project}/paper-candidates", {"candidate": candidate}
        )
        self.assertEqual(status, 409)
        self.request(
            "POST", f"/api/v2/p/{self.project}/initialize",
            {"confirmation": "INITIALIZE SURVEY TOOL 2.0"},
        )
        status, payload = self.request(
            "POST", f"/api/v2/p/{self.project}/paper-candidates",
            {"candidate": candidate, "recommendation_reason": "Matches Q-001"},
        )
        self.assertEqual(status, 201)
        self.assertEqual(payload["candidate"]["lifecycle_status"], "proposed")
        status, payload = self.request("GET", f"/api/v2/p/{self.project}/paper-candidates")
        self.assertEqual(status, 200)
        self.assertEqual(len(payload["candidates"]), 1)
        self.assertEqual(payload["candidates"][0]["recommendation_reason"], "Matches Q-001")

    def test_v2_agent_routing_uses_full_codex_model_ids_and_persists(self):
        path=f"/api/v2/p/{self.project}/agent-routing"
        status,current=self.request("GET",path); self.assertEqual(status,200,current)
        self.assertEqual(current["routing"]["routes"]["experiment_code_edit"]["model"],"gpt-5.6-sol")
        routing=current["routing"]; routing["routes"]["local_tool_edit"]["model"]="gpt-5.6-terra"
        status,_=self.request("PUT",path,{"confirmation":"wrong","routing":routing}); self.assertEqual(status,400)
        status,saved=self.request("PUT",path,{"confirmation":"UPDATE V2 AGENT ROUTING","routing":routing}); self.assertEqual(status,200,saved)
        self.assertEqual(saved["routing"]["routes"]["local_tool_edit"]["model"],"gpt-5.6-terra"); self.assertEqual(saved["applies_to"],"future_dispatches_only")
        self.assertTrue((self.root/".survey-tool/agent-routing.json").exists())
        status,reloaded=self.request("GET",path); self.assertEqual(status,200); self.assertEqual(reloaded["routing"],saved["routing"])

    def test_environment_bindings_cas_policy_and_legacy_machine_preservation(self):
        server.write_tool_json(self.root, "machines.json", [{"id": "M-01", "label": "Legacy GPU", "ssh_host": "gpu.example"}])
        status, bindings = self.request("GET", f"/api/v2/p/{self.project}/environment-bindings")
        self.assertEqual(status, 200, bindings)
        self.assertEqual(bindings["servers"][0]["id"], "M-01")
        status, updated = self.request("PUT", f"/api/v2/p/{self.project}/servers/M-02", {
            "confirmation": "UPDATE V2 SERVER", "expected_hash": bindings["servers_hash"],
            "fields": {"label": "Mechanism", "ssh_host": "featurize", "project_root": "/workspace/project", "status": "forbidden"},
        })
        self.assertEqual(status, 200, updated)
        self.assertEqual({row["id"] for row in updated["servers"]}, {"M-01", "M-02"})
        self.assertNotIn("status", updated["server"])
        self.assertTrue((self.root / ".survey-tool/machines.json").exists())
        self.assertEqual({row["id"] for row in server.read_tool_json(self.root, "servers.json", [])}, {"M-01", "M-02"})
        status, conflict = self.request("PUT", f"/api/v2/p/{self.project}/servers/M-03", {
            "confirmation": "UPDATE V2 SERVER", "expected_hash": bindings["servers_hash"], "fields": {"label": "stale"},
        })
        self.assertEqual(status, 409); self.assertEqual(conflict["reason"], "content_hash_conflict")
        status, missing = self.request("PUT", f"/api/v2/p/{self.project}/workspaces/W-01", {
            "confirmation": "UPDATE V2 WORKSPACE", "expected_hash": updated["workspaces_hash"],
            "fields": {"label": "Workspace", "server_id": "M-missing", "remote_repo": "/workspace/repo"},
        })
        self.assertEqual(status, 400); self.assertIn("Server", missing["error"])
        status, invalid_policy = self.request("PUT", f"/api/v2/p/{self.project}/workspaces/W-01", {
            "confirmation": "UPDATE V2 WORKSPACE", "expected_hash": updated["workspaces_hash"],
            "fields": {"label": "Workspace", "server_id": "M-02", "remote_repo": "/workspace/repo",
                       "environment_policy": {"allowed_write_roots": ["relative"]}},
        })
        self.assertEqual(status, 400); self.assertIn("绝对路径", invalid_policy["error"])
        dataset={"id":"corpus","label":"Corpus","source_path":"/datasets/corpus","target_path":"/workspace/repo/data/corpus","mode":"bind_ro","required":True,"notes":"operator binding"}
        status, saved = self.request("PUT", f"/api/v2/p/{self.project}/workspaces/W-01", {
            "confirmation":"UPDATE V2 WORKSPACE","expected_hash":updated["workspaces_hash"],"fields":{"label":"Workspace","server_id":"M-02","remote_repo":"/workspace/repo","remote_data_root":"/datasets","environment_policy":{"allowed_write_roots":["/workspace/repo"],"read_only_roots":["/datasets"],"forbidden_paths":["/tmp"],"forbidden_operations":["sudo"],"default_deny_write":True},"execution_isolation":{"mode":"bubblewrap","required":True,"network":"none","deny_read_roots":["/home/runner/.ssh"],"notes":""},"dataset_bindings":[dataset]}
        })
        self.assertEqual(status,200,saved); self.assertTrue(saved["workspace"]["environment_policy"]["default_deny_write"]); self.assertEqual(saved["workspace"]["dataset_bindings"],[dataset])
        status, partial = self.request("PUT", f"/api/v2/p/{self.project}/workspaces/W-01", {"confirmation":"UPDATE V2 WORKSPACE","expected_hash":saved["workspaces_hash"],"fields":{"label":"Renamed only"}})
        self.assertEqual(status,200,partial); self.assertEqual(partial["workspace"]["dataset_bindings"],[dataset]); self.assertEqual(partial["workspace"]["remote_repo"],"/workspace/repo")

    def test_workspace_rule_draft_preview_does_not_write_or_execute_and_server_is_required(self):
        server.write_tool_json(self.root,"servers.json",[{"id":"S-01","label":"Compute","ssh_host":"compute"}])
        before=server.environment_bindings(self.root); workspace_file=self.root/".survey-tool/workspaces.json"; before_bytes=workspace_file.read_bytes() if workspace_file.exists() else None
        request="  数据只读，不要联网，代码目录可写，禁止 sudo。  "
        with mock.patch("server.start_local_worker") as worker:
            status,preview=self.request("POST",f"/api/v2/p/{self.project}/rule-drafts/preview",{"scope":"workspace","preset":"research_safe","request":request,"draft":{"server_id":"S-01","remote_repo":"/work/repo","remote_data_root":"/data","environment_policy":{"notes":"keep"}}})
        self.assertEqual(status,200,preview); self.assertEqual(preview["original_request"],request); self.assertTrue(preview["read_only"]); worker.assert_not_called()
        self.assertIn("/data",preview["structured_preview"]["environment_policy"]["read_only_roots"])
        self.assertEqual(workspace_file.read_bytes() if workspace_file.exists() else None,before_bytes)
        valid_ai=json.dumps({"contract":"survey-tool.workspace-rule-intent/v1","requirements":{"network":"none","data_read_only":True,"workspace_write":True,"forbid_sudo":True,"forbid_delete":None},"concise_rules":[{"label":"隔离","detail":"不使用外部网络"}]},ensure_ascii=False)
        live=mock.Mock(); live.proc.poll.return_value=None; live.prompt_completion.return_value={"success":True,"text":valid_ai}
        with mock.patch("server.bridge_for",return_value=live):
            status,ai=self.request("POST",f"/api/v2/p/{self.project}/rule-drafts/preview",{"scope":"workspace","preset":"custom","organizer":"ai_auto","request":"保持与外界隔绝并完成常规研究","draft":{"server_id":"S-01","remote_repo":"/private/repo","remote_data_root":"/private/data"}})
        self.assertEqual(status,200,ai); self.assertEqual(ai["organizer"]["used"],"ai"); self.assertEqual(ai["structured_preview"]["execution_isolation"]["network"],"none"); self.assertNotIn("/private/repo",live.prompt_completion.call_args.args[0])
        invalid=mock.Mock(); invalid.proc.poll.return_value=None; invalid.prompt_completion.return_value={"success":True,"text":json.dumps({"contract":"survey-tool.workspace-rule-intent/v1","requirements":{"network":"host","data_read_only":None,"workspace_write":None,"forbid_sudo":None,"forbid_delete":None},"concise_rules":[],"path":"/evil"})}
        with mock.patch("server.bridge_for",return_value=invalid):
            status,fallback=self.request("POST",f"/api/v2/p/{self.project}/rule-drafts/preview",{"scope":"workspace","preset":"custom","organizer":"ai_auto","request":"ambiguous","draft":{"server_id":"S-01"}})
        self.assertEqual(status,200,fallback); self.assertEqual(fallback["organizer"]["used"],"basic_fallback"); self.assertTrue(any("AI 不可用" in warning for warning in fallback["warnings"])); self.assertNotIn("/evil",json.dumps(fallback["structured_preview"]))
        offline=mock.Mock(); offline.proc=None
        with mock.patch("server.bridge_for",return_value=offline):
            status,offline_result=self.request("POST",f"/api/v2/p/{self.project}/rule-drafts/preview",{"scope":"workspace","preset":"custom","organizer":"ai_auto","request":"x","draft":{"server_id":"S-01"}})
        self.assertEqual(status,200,offline_result); self.assertEqual(offline_result["organizer"]["used"],"basic_fallback")
        self.assertEqual(workspace_file.read_bytes() if workspace_file.exists() else None,before_bytes)
        status,payload=self.request("PUT",f"/api/v2/p/{self.project}/workspaces/W-new",{"confirmation":"UPDATE V2 WORKSPACE","expected_hash":before["workspaces_hash"],"fields":{"label":"Detached"}})
        self.assertEqual(status,400,payload); self.assertIn("必须选择",payload["error"])
        profile={"contract":"survey-tool.workspace-rule-profile/v1","original_request":preview["original_request"],"preset":preview["preset"]["id"],"rules":preview["rules"],"warnings":preview["warnings"],"questions":preview["questions"],"updated_at":"client-time","organizer":preview["organizer"]}
        direct_input={"contract":"survey-tool.workspace-rule-input/v1","original_request":"只保存原文，不先整理","preset":"custom","updated_at":"client-time"}
        status,payload=self.request("PUT",f"/api/v2/p/{self.project}/workspaces/W-new",{"confirmation":"UPDATE V2 WORKSPACE","expected_hash":before["workspaces_hash"],"fields":{"label":"Attached","server_id":"S-01","rule_input":direct_input,"rule_profile":profile}})
        self.assertEqual(status,200,payload); self.assertEqual(payload["workspace"]["server_id"],"S-01"); self.assertEqual(payload["workspace"]["rule_input"]["original_request"],"只保存原文，不先整理"); self.assertNotEqual(payload["workspace"]["rule_input"]["updated_at"],"client-time"); self.assertEqual(payload["workspace"]["rule_profile"]["original_request"],request); self.assertEqual(payload["workspace"]["rule_profile"]["organizer"]["used"],"basic")
        status,reloaded=self.request("GET",f"/api/v2/p/{self.project}/environment-bindings"); self.assertEqual(status,200); restored=next(row for row in reloaded["workspaces"] if row["id"]=="W-new"); self.assertEqual(restored["rule_input"]["original_request"],"只保存原文，不先整理"); self.assertEqual(restored["rule_profile"]["rules"],preview["rules"])
        status,partial=self.request("PUT",f"/api/v2/p/{self.project}/workspaces/W-new",{"confirmation":"UPDATE V2 WORKSPACE","expected_hash":reloaded["workspaces_hash"],"fields":{"label":"Still attached"}}); self.assertEqual(status,200); self.assertEqual(partial["workspace"]["rule_profile"]["original_request"],request)
        bad={**profile,"rules":[{"id":"x","label":"x","detail":"x","source":"client-authority"}]}
        status,invalid=self.request("PUT",f"/api/v2/p/{self.project}/workspaces/W-new",{"confirmation":"UPDATE V2 WORKSPACE","expected_hash":partial["workspaces_hash"],"fields":{"rule_profile":bad}}); self.assertEqual(status,400,invalid); self.assertIn("rule_profile",invalid["error"])

    def test_zotero_stage_is_safe_preview_and_does_not_write_canonical(self):
        self.request("POST", f"/api/v2/p/{self.project}/initialize", {"confirmation": "INITIALIZE SURVEY TOOL 2.0"})
        safe_item = {"id": 42, "key": "ABCD1234", "title": "Local Zotero Paper", "authors": ["Ada Lovelace"],
                     "date": "2025", "venue": "Journal", "doi": "10.1/example", "has_pdf": True, "already_in": False}
        with mock.patch("server.zotero_collections", return_value={"ok": True, "collections": [{"id": 7, "name": "Lab", "count": 1}]}), \
             mock.patch("server.zotero_collection_items", return_value={"ok": True, "items": [safe_item]}) as item_reader:
            status, collections = self.request("GET", f"/api/v2/p/{self.project}/zotero/collections")
            self.assertEqual(status, 200); self.assertEqual(collections["collections"][0]["id"], 7)
            status, listed = self.request("GET", f"/api/v2/p/{self.project}/zotero/collections/0/items")
            self.assertEqual(status, 200); self.assertNotIn("path", json.dumps(listed).lower())
            status, staged = self.request("POST", f"/api/v2/p/{self.project}/zotero/items/42/stage", {
                "confirmation": "STAGE ZOTERO PAPER CANDIDATE"})
            repeat_status, repeated = self.request("POST", f"/api/v2/p/{self.project}/zotero/items/42/stage", {
                "confirmation": "STAGE ZOTERO PAPER CANDIDATE"})
            self.assertEqual(repeat_status, 201)
            self.assertEqual(staged["candidate"]["id"], repeated["candidate"]["id"])
            item_reader.assert_any_call(self.root, 0, item_id=42)
            safe_item["already_in"] = True
            duplicate_status, duplicate = self.request("POST", f"/api/v2/p/{self.project}/zotero/items/42/stage", {
                "confirmation": "STAGE ZOTERO PAPER CANDIDATE"})
            self.assertEqual(duplicate_status, 409)
            self.assertIn("已在项目论文库", duplicate["error"])
        self.assertEqual(status, 201, staged)
        self.assertFalse(staged["canonical_write"]); self.assertFalse(staged["local_path_exposed"])
        self.assertNotIn("canonical_path", staged["candidate"]); self.assertNotIn("canonical_paper_path", staged["candidate"])
        self.assertGreaterEqual(item_reader.call_count, 2)
        self.assertFalse(server.note_path(self.root, staged["candidate"]["citekey"]).exists())
        status,pipeline=self.request("POST",f"/api/v2/p/{self.project}/paper-candidates/{staged['candidate']['id']}/acquisition",{"confirmation":"STAGE PAPER ACQUISITION","expected_revision":staged["candidate"]["revision"]})
        self.assertEqual(status,202,pipeline); self.assertEqual(pipeline["download_job"]["kind"],"zotero_copy"); self.assertEqual(pipeline["mineru_job"]["depends_on_job_id"],pipeline["download_job"]["id"])
        self.assertNotIn("path",json.dumps(pipeline["download_job"]["request"]).lower()); self.assertFalse(server.note_path(self.root,staged["candidate"]["citekey"]).exists())

    def test_arxiv_search_normalizes_and_stages_http_acquisition(self):
        raw={"source":"arxiv","query":"mechanism","hits":[{"citekey":"valid2026","title":"Valid","authors":["Ada"],"year":"2026","arxiv_id":"2608.12345v2","url":"http://arxiv.org/abs/2608.12345v2"},{"title":"Old","authors":[],"year":"1999","arxiv_id":"hep-th/9901001"},{"title":"Unsafe","arxiv_id":"../../etc/passwd","oa_url":"https://evil.example/file.pdf"}]}
        with mock.patch("server.paper_skill_script",return_value=pathlib.Path("/safe/search_arxiv.py")),mock.patch("server.run_script",return_value={"returncode":0,"stdout":json.dumps(raw),"stderr":""}):
            normalized=server.arxiv_paper_search(self.root,"mechanism",10)
        self.assertEqual(len(normalized["hits"]),2); self.assertEqual(normalized["hits"][0]["oa_url"],"https://arxiv.org/pdf/2608.12345v2.pdf"); self.assertEqual(normalized["hits"][1]["oa_url"],"https://arxiv.org/pdf/hep-th/9901001.pdf")
        with mock.patch("server.paper_skill_script",return_value=pathlib.Path("/safe/search_arxiv.py")),mock.patch("server.run_script",return_value={"returncode":1,"stdout":json.dumps({"source":"arxiv","hits":[],"error":"SSL handshake timed out"}),"stderr":""}),mock.patch("survey_tool.integrations.web_paper_search",return_value={"source":"openalex","hits":[{"citekey":"fallback","title":"Fallback","authors":[],"year":"2026","arxiv_id":"2608.54321"}]}):
            fallback=server.arxiv_paper_search(self.root,"mechanism",10)
        self.assertEqual(fallback["source"],"arxiv-openalex-fallback"); self.assertTrue(fallback["hits"]); self.assertIn("SSL handshake",fallback["warning"])
        with mock.patch("server.arxiv_paper_search",return_value=normalized):
            status,payload=self.request("GET",f"/api/v2/p/{self.project}/papers/arxiv-search?q=mechanism")
        self.assertEqual(status,200,payload); candidate=payload["hits"][0]; self.assertEqual(candidate["source"],"arxiv")
        with mock.patch("server.arxiv_paper_search",return_value={"ok":False,"source":"arxiv","hits":[],"error":"upstream timeout"}):
            status,failed=self.request("GET",f"/api/v2/p/{self.project}/papers/arxiv-search?q=timeout")
        self.assertEqual(status,502); self.assertIn("timeout",failed["error"])
        self.request("POST",f"/api/v2/p/{self.project}/initialize",{"confirmation":"INITIALIZE SURVEY TOOL 2.0"})
        status,saved=self.request("POST",f"/api/v2/p/{self.project}/paper-candidates",{"candidate":candidate})
        self.assertEqual(status,201,saved); self.assertEqual(saved["candidate"]["source"],"arxiv")
        status,pipeline=self.request("POST",f"/api/v2/p/{self.project}/paper-candidates/{saved['candidate']['id']}/acquisition",{"confirmation":"STAGE PAPER ACQUISITION","expected_revision":saved["candidate"]["revision"]})
        self.assertEqual(status,202,pipeline); self.assertEqual(pipeline["download_job"]["kind"],"paper_download"); self.assertEqual(pipeline["download_job"]["request"]["url"],candidate["oa_url"]); self.assertFalse(server.note_path(self.root,candidate["citekey"]).exists())
        from survey_tool.v2 import V2Store
        claimed=V2Store(self.root).claim_next_job(worker_id="secret-worker",lease_seconds=60)
        status,listed=self.request("GET",f"/api/v2/p/{self.project}/jobs"); self.assertEqual(status,200); self.assertNotIn("lease_token",listed["jobs"][0])
        status,_=self.request("POST",f"/api/v2/p/{self.project}/jobs/run-local",{"confirmation":"wrong"}); self.assertEqual(status,400)
        with mock.patch("server.start_local_worker",return_value={"worker_started":True,"already_running":False,"worker_id":"local-test"}) as starter:
            status,started=self.request("POST",f"/api/v2/p/{self.project}/jobs/run-local",{"confirmation":"RUN LOCAL PAPER WORKER","target_object_id":saved["candidate"]["id"],"max_jobs":2})
        self.assertEqual(status,202,started); self.assertTrue(started["worker_started"]); starter.assert_called_once()
        V2Store(self.root).finish_claimed_job(claimed["id"],lease_token=claimed["lease_token"],succeeded=False,error_class="Test",error_message="cleanup")


if __name__ == "__main__":
    unittest.main()
