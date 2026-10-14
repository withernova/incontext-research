#!/usr/bin/env python3
"""Stdlib regression tests for the Experiment/Run registry contract."""
import json
import datetime
import contextlib
import io
import pathlib
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import server
import surveyctl
from survey_tool.rule_drafts import preview_rule_draft
from survey_tool.experiments import validate_execution_isolation


class ContractTest(unittest.TestCase):
    def test_run_workspace_inheritance_override_and_validation(self):
        rows=server.read_tool_json(self.root,"workspaces.json",[]); rows.append({"id":"W-02","label":"second","server_id":"S-01","remote_repo":"/repo-two","remote_data_root":"/datasets","remote_worktree_root":"/worktrees-two","remote_experiment_root":"/exp-two"}); server.write_tool_json(self.root,"workspaces.json",rows)
        inherited=server.create_run(self.root,"E-001",{"variant":"inherit","workspace_id":""},"R-inherit")
        override=server.create_run(self.root,"E-001",{"variant":"override","workspace_id":"W-02"},"R-override")
        data=server.experiment_data(self.root)
        self.assertEqual(server.resolve_run_config(self.root,inherited,data)["workspace_id"],"W-01")
        self.assertEqual(server.resolve_run_config(self.root,override,data)["workspace_id"],"W-02")
        with self.assertRaisesRegex(ValueError,"Workspace 不存在"):
            server.create_run(self.root,"E-001",{"variant":"bad","workspace_id":"W-missing"},"R-bad")
        with self.assertRaisesRegex(ValueError,"Workspace 不存在"):
            server.update_run(self.root,"R-inherit",{"workspace_id":"W-missing"})
        server.update_experiment(self.root,"E-001",{"workspace_id":"W-02"})
        refreshed={row["id"]:row for row in server.experiment_data(self.root)["runs"]}
        self.assertEqual(refreshed["R-inherit"].get("workspace_id",""),""); self.assertEqual(refreshed["R-override"]["workspace_id"],"W-02")

    def test_external_workspace_ai_response_only_accepts_explicit_paths(self):
        from survey_tool.rule_drafts import external_intent_preview, workspace_external_prompt
        request="仅仅操作/defaultShare/archive/liuwenchu/projects/IPLoc下的文件。数据集在/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/dataset-test下的软连接。"
        draft={"id":"02","label":"lwc","server_id":"S-01","environment_policy":{},"execution_isolation":{"mode":"none","required":True,"network":"none","deny_read_roots":[],"notes":""},"dataset_bindings":[]}
        self.assertIn("workspace-rule-external/v1",workspace_external_prompt(request,draft))
        valid={"contract":"survey-tool.workspace-rule-external/v1","remote_repo":"/defaultShare/archive/liuwenchu/projects/IPLoc","remote_data_root":"/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/dataset-test","remote_worktree_root":"/defaultShare/archive/liuwenchu/projects/IPLoc","remote_experiment_root":"","environment_activation":"IPLoc conda 环境","allowed_write_roots":["/defaultShare/archive/liuwenchu/projects/IPLoc"],"read_only_roots":["/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/dataset-test"],"forbidden_paths":[],"deny_read_roots":[],"network":"unspecified","forbidden_operations":["sudo"],"dataset_candidates":[],"questions":[]}
        preview=external_intent_preview(request,"research_safe",draft,json.dumps(valid,ensure_ascii=False),{"available_server_ids":["S-01"]})
        self.assertEqual(preview["structured_preview"]["environment_policy"]["allowed_write_roots"],["/defaultShare/archive/liuwenchu/projects/IPLoc"])
        profile={"contract":"survey-tool.workspace-rule-profile/v1","original_request":request,"preset":"research_safe","rules":preview["rules"],"warnings":preview["warnings"],"questions":preview["questions"],"updated_at":"client","organizer":preview["organizer"]}
        self.assertEqual(server.validate_workspace_rule_profile(profile)["organizer"]["requested"],"external")
        bad={**valid,"remote_repo":"/tmp/evil"}
        with self.assertRaisesRegex(ValueError,"原文明确"):
            external_intent_preview(request,"research_safe",draft,json.dumps(bad,ensure_ascii=False),{"available_server_ids":["S-01"]})

    def test_policy_allows_narrow_child_of_denied_parent_but_keeps_deeper_deny(self):
        ws={"id":"W-01","remote_repo":"/archive/user/project"}
        policy=server.validate_workspace_policy(ws,{"allowed_write_roots":["/archive/user/project"],"read_only_roots":["/archive/user/data"],"forbidden_paths":["/archive","/archive/user/project/.git"],"forbidden_operations":["sudo"],"default_deny_write":True})
        resolved={"project_dir":"/archive/user/project","run_dir":"/archive/user/project/runs/R","log_file":"/archive/user/project/runs/R/log","output_dir":"/archive/user/project/runs/R/out","metrics_file":"/archive/user/project/runs/R/metrics"}
        self.assertEqual(server.run_policy_violations(resolved,policy),[])
        blocked={**resolved,"run_dir":"/archive/user/project/.git/x"}
        self.assertIn("命中禁止路径",server.run_policy_violations(blocked,policy)[0]["reason"])

    def test_tmux_guarded_requires_explicit_host_network(self):
        guarded=server.validate_execution_isolation({"mode":"tmux-guarded","required":True,"network":"host","deny_read_roots":[]})
        self.assertEqual(guarded["mode"],"tmux-guarded")
        with self.assertRaisesRegex(ValueError,"network"):
            server.validate_execution_isolation({"mode":"tmux-guarded","required":True,"network":"none","deny_read_roots":[]})

    def test_workspace_rule_input_validates_and_uses_server_timestamp(self):
        value=server.validate_workspace_rule_input({"contract":"survey-tool.workspace-rule-input/v1","original_request":"保留原文","preset":"custom","updated_at":"client-time"})
        self.assertEqual(value["original_request"],"保留原文"); self.assertNotEqual(value["updated_at"],"client-time")
        with self.assertRaisesRegex(ValueError,"rule_input"): server.validate_workspace_rule_input({"contract":"bad","original_request":"x","preset":"custom","updated_at":"x"})

    def test_workspace_rule_draft_is_generic_read_only_and_fail_closed(self):
        request="  数据只读，不要联网；代码目录可写，禁止 sudo 和删除。\n保留原话。  "
        workspace={"server_id":"S-01","remote_repo":"/repo","remote_data_root":"/datasets","environment_policy":{"notes":"keep","temp_policy":"keep advanced","forbidden_paths":["/repo/.git"]},"execution_isolation":{"mode":"bubblewrap","required":True,"network":"host","deny_read_roots":[],"notes":"keep"},"dataset_bindings":[]}
        result=preview_rule_draft("workspace",request,"research_safe",workspace)
        self.assertEqual(result["contract"],"survey-tool.rule-draft/v1"); self.assertEqual(result["original_request"],request); self.assertTrue(result["read_only"])
        self.assertEqual(result["structured_preview"]["execution_isolation"]["network"],"none")
        self.assertIn("/repo",result["structured_preview"]["environment_policy"]["allowed_write_roots"]); self.assertIn("/datasets",result["structured_preview"]["environment_policy"]["read_only_roots"])
        self.assertEqual(result["structured_preview"]["environment_policy"]["temp_policy"],"keep advanced")
        self.assertTrue(server.validate_workspace_policy(workspace,result["structured_preview"]["environment_policy"])["default_deny_write"])
        self.assertEqual(validate_execution_isolation(result["structured_preview"]["execution_isolation"])["network"],"none")
        missing=preview_rule_draft("workspace","数据只读，工作目录可写","research_safe",{"server_id":"S-01"})
        self.assertTrue(missing["questions"]); self.assertNotIn("/tmp",str(missing["structured_preview"]))
        with self.assertRaisesRegex(ValueError,"必须选择"): preview_rule_draft("workspace","只读","research_safe",{})
        with self.assertRaisesRegex(ValueError,"不存在"): preview_rule_draft("workspace","只读","research_safe",{"server_id":"missing"},{"available_server_ids":["S-01"]})

    def test_ai_context_firewall_scopes_experiment_and_preserves_intent(self):
        server.update_experiment(self.root,"E-001",{"metric_definitions":[]})
        server.create_run(self.root,"E-001",{"variant":"a","purpose":"A-only purpose"},"R-A")
        server.create_experiment(self.root,{"title":"Secret B","objective":"B-only objective","workspace_id":"W-01"},"E-002")
        server.create_run(self.root,"E-002",{"variant":"b","purpose":"B-only run content"},"R-B")
        paths=(self.root/".survey-tool/experiments.json",self.root/".survey-tool/runs.json")
        before=tuple(path.read_bytes() if path.exists() else None for path in paths)
        intent="  请逐字保留：只分析 A；不要执行。\n第二行  "
        result=server.ai_discussion_prompt(self.root,"experiment","E-001",intent)
        self.assertEqual(result["context_manifest"]["current_user_intent"],intent)
        self.assertIn("metric_definitions",result["context_manifest"]["missing_authoritative_fields"])
        self.assertIn("跨 Experiment",result["prompt"]); self.assertIn("reference_only",result["prompt"])
        self.assertNotIn("B-only objective",result["prompt"]); self.assertNotIn("B-only run content",result["prompt"])
        self.assertNotIn("A-only purpose",result["prompt"])
        self.assertFalse(any(source["source_id"] in {"experiment:E-002","run:R-B"} for source in result["context_manifest"]["sources"]))
        self.assertIn('"ssh_host": "test"',result["prompt"]); self.assertIn("不要连接其他 alias",result["prompt"]); self.assertIn("环境切换后重新运行 experiment context",result["prompt"]); self.assertIn("nvidia-smi",result["prompt"])
        self.assertLess(len(result["prompt"].encode("utf-8")),6000)
        self.assertEqual(before,tuple(path.read_bytes() if path.exists() else None for path in paths))

    def test_code_edit_prompt_is_bounded_and_does_not_create_run(self):
        paths=(self.root/".survey-tool/experiments.json",self.root/".survey-tool/runs.json")
        before=tuple(path.read_bytes() if path.exists() else None for path in paths)
        request="在远程代码目录新增 smoke.txt，只检查内容。"
        from survey_tool.v2 import V2Store
        store=V2Store(self.root); store.initialize(); store.create_object(object_id="Q-9",object_type="question",project_id="PROJECT-test",title="相关问题",canonical_path="shell/01_questions/Q-9.md")
        result=server.ai_discussion_prompt(self.root,"experiment","E-001",request,"code_edit","whole",["Q-9"],"采用 A，不采用 B")
        self.assertEqual(result["authority_mode"],"bounded_code_edit"); self.assertFalse(result["read_only"])
        self.assertEqual(result["context_manifest"]["current_user_intent"],request)
        self.assertIn('"remote_repo":"/repo"',result["prompt"]); self.assertIn("不创建或运行 Run",result["prompt"]); self.assertIn("Q-9",result["prompt"]); self.assertIn("采用 A，不采用 B",result["prompt"])
        self.assertIn("question:Q-9",[item["source_id"] for item in result["context_manifest"]["sources"]])
        self.assertNotIn("claim-next",result["prompt"]); self.assertLess(len(result["prompt"].encode("utf-8")),2000)
        # firewall 与 manifest 只保留机器可读版本，不再灌进 prompt 正文（避免门禁信息挤占目标注意力）。
        self.assertNotIn("context_manifest=",result["prompt"]); self.assertNotIn("policy_version",result["prompt"])
        self.assertEqual(before,tuple(path.read_bytes() if path.exists() else None for path in paths))

    def test_run_implementation_prompt_is_bounded_and_keeps_governance(self):
        run=server.create_run(self.root,"E-001",{"variant":"impl","research_question":"Does it work?","purpose":"Implement the check","metric_plan":"focused metric","architecture_plan":"reuse existing module","command":"python -m pytest -q"},"R-impl")
        before=server.read_tool_json(self.root,"runs.json",[])
        request="实现数据加载和指标计算，运行聚焦测试并修复到通过。"
        result=server.ai_discussion_prompt(self.root,"run",run["id"],request,"run_implementation")
        self.assertEqual(result["authority_mode"],"bounded_run_implementation"); self.assertFalse(result["read_only"])
        self.assertNotIn("max_debug_cycles",result)
        self.assertEqual(result["context_manifest"]["current_user_intent"],request)
        self.assertIn("实现 → 聚焦检查 → 修复",result["prompt"]); self.assertIn("最多 5 轮",result["prompt"])
        self.assertIn("本 Run 自己的日志与产物可直接读",result["prompt"]); self.assertIn("tail / grep / rg",result["prompt"])
        self.assertIn("不调用 survey_run_execution",result["prompt"]); self.assertIn("交给 Steward",result["prompt"])
        self.assertIn("code_change_review",result["prompt"]); self.assertNotIn("claim-next",result["prompt"])
        # 治理信息只声明一次：firewall 正文与 manifest JSON 不再注入 prompt。
        self.assertNotIn("context_manifest=",result["prompt"]); self.assertNotIn("policy_version",result["prompt"])
        self.assertNotIn("linked_reference 只供分析/证据",result["prompt"])
        self.assertLess(len(result["prompt"].encode("utf-8")),3500)
        self.assertEqual(before,server.read_tool_json(self.root,"runs.json",[]))
        with self.assertRaisesRegex(ValueError,"Run target"):
            server.ai_discussion_prompt(self.root,"experiment","E-001",request,"run_implementation")

    def test_external_context_marks_nonprimary_addresses_reference_only(self):
        server.create_run(self.root,"E-001",{"variant":"ref"},"R-ref")
        published={"githubUrl":"https://github.com/example/snapshot","commitSha":"fixed"}
        with mock.patch("survey_tool.integrations.read_publish",return_value=published):
            result=server.gpt_assistant_instruction(self.root,["experiment:E-001","run:R-ref"],"review","verbatim request",{"address":"experiment:E-001"})
        roles={source["source_id"]:(source["role"],source["reference_only"]) for source in result["context_manifest"]["sources"]}
        self.assertEqual(roles["experiment:E-001"],("authoritative_target",False))
        self.assertEqual(roles["run:R-ref"],("retrieved_reference",True))
        self.assertIn("reference_only",result["instruction"])

    def test_steward_process_pattern_is_conservative(self):
        self.assertEqual(server.steward_process_pattern("CUDA_VISIBLE_DEVICES=0 python /work/train.py --epochs 2"), r"train\.py")
        self.assertEqual(server.steward_process_pattern("env CUDA_VISIBLE_DEVICES=0 torchrun --nproc_per_node=2 scripts/train.py"), r"train\.py")
        self.assertEqual(server.steward_process_pattern("python3 train.py"), r"train\.py")
        self.assertEqual(server.steward_process_pattern(""), "")
        self.assertEqual(server.steward_process_pattern("cd /work"), "")

    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp(prefix="survey-contract-"))
        (self.root / "state.md").write_text("state: TEST\n", encoding="utf-8")
        server.CFG = {"projects_root": str(self.root.parent), "projects": [str(self.root)], "skill_dir": str(ROOT / "skills/research-survey"), "port": 7421}
        server.SKILL = ROOT / "skills/research-survey"
        server.SKILL_SCRIPTS = server.SKILL / "scripts"
        server.write_tool_json(self.root, "servers.json", [{"id": "S-01", "ssh_host": "test"}])
        server.write_tool_json(self.root, "workspaces.json", [{"id": "W-01", "server_id": "S-01", "remote_repo": "/repo", "remote_worktree_root":"/worktrees", "remote_data_root":"/datasets", "remote_experiment_root": "/exp"}])
        server.create_experiment(self.root, {"title": "contract", "objective": "round trip", "workspace_id": "W-01"}, "E-001")

    def test_experiment_code_repository_binding_and_code_only_external_prompt(self):
        created=next(item for item in server.experiment_data(self.root)["experiments"] if item["id"]=="E-001")
        self.assertEqual(created["code_repository_workspace_id"],"W-01")
        bindings=server.environment_bindings(self.root)
        updated=server.update_workspace_binding(self.root,"W-01",bindings["workspaces_hash"],{"external_code_url":"https://github.com/example/real-code.git","external_code_ref":"abc1234"})
        self.assertEqual(updated["workspace"]["external_code_url"],"https://github.com/example/real-code")
        result=server.gpt_assistant_instruction(self.root,["experiment:E-001"],"review","检查 loader",{"address":"experiment:E-001"},{"workspace_id":"W-01","url":"https://github.com/example/real-code","ref":"abc1234"})
        self.assertTrue(result["ok"]); self.assertEqual(result["context_mode"],"code_repository_only")
        self.assertIn("path:line",result["instruction"]); self.assertNotIn("round trip",result["instruction"]); self.assertEqual(result["objects"],[])
        with self.assertRaisesRegex(ValueError,"GitHub HTTPS"):
            server.update_workspace_binding(self.root,"W-01",updated["workspaces_hash"],{"external_code_url":"ssh://secret/repo"})
        with self.assertRaisesRegex(ValueError,"代码仓库 Workspace 不存在"):
            server.update_experiment(self.root,"E-001",{"code_repository_workspace_id":"W-missing"})

    def test_rich_run_round_trip_and_unknown_rejection(self):
        rich = {"variant": "treatment", "run_type": "treatment", "purpose": "p", "necessity": "n", "evidence_basis": "e", "implementation_summary": "change", "implementation_details": "details", "data_definition": "split + sampling", "data_scale": "n=2", "model_config": "m", "variables_controls": "v", "metric_definition": "metric", "integrity_gates": "count=2", "expected_outcome": "signature", "acceptance_criteria": "gate pass", "dependencies": "baseline", "workspace_id": "W-01", "git_commit": "abc", "config": "x=1", "command": "python x.py", "seed": "42", "log_path": "/exp/E-001/R-rich/log", "output_dir": "/exp/E-001/R-rich/outputs", "artifact_dir": "/exp/E-001/R-rich", "artifacts": "metrics.json", "limitations": "lim", "claim_boundary": "not causal", "audit_paths": "a"}
        server.create_run(self.root, "E-001", rich, "R-rich")
        loaded = next(x for x in server.experiment_data(self.root)["runs"] if x["id"] == "R-rich")
        for key, value in rich.items(): self.assertEqual(loaded[key], value)
        for bad in ({"mystery": "x"}, {"id": "evil"}, {"experiment_id": "E-999"}):
            with self.assertRaises(ValueError): server.update_run(self.root, "R-rich", bad)

    def test_experiment_and_run_soft_archive_preserve_workflow_and_block_active_execution(self):
        run=server.create_run(self.root,"E-001",{"variant":"obsolete","purpose":"retain me"},"R-archive")
        original_status=run.get("status"); original_stage=run.get("workflow_stage")
        archived=server.archive_run(self.root,"R-archive",run["updated"],"已由新方案替代")
        self.assertTrue(archived["archived_at"]); self.assertEqual(archived.get("status"),original_status); self.assertEqual(archived.get("workflow_stage"),original_stage)
        restored=server.archive_run(self.root,"R-archive",archived["updated"],restore=True)
        self.assertNotIn("archived_at",restored); self.assertEqual(restored["archive_history"][-1]["action"],"restore")
        server.write_tool_json(self.root,"execution-outbox.json",{"schema":server.OUTBOX_SCHEMA,"items":[{"dispatch_id":"dispatch-active","experiment_id":"E-001","run_id":"R-archive","status":"running","history":[]}]})
        with self.assertRaisesRegex(RuntimeError,"active_execution"): server.archive_run(self.root,"R-archive",restored["updated"],"暂时停用")
        exp=server.experiment_data(self.root)["experiments"][0]
        with self.assertRaisesRegex(RuntimeError,"active_execution"): server.archive_experiment(self.root,"E-001",exp["updated"],"整体失效")
        box=server.read_tool_json(self.root,"execution-outbox.json",{}); box["items"][0]["status"]="failed"; server.write_tool_json(self.root,"execution-outbox.json",box)
        archived_exp=server.archive_experiment(self.root,"E-001",exp["updated"],"整体失效")
        self.assertTrue(archived_exp["archived_at"]); self.assertEqual(server.experiment_data(self.root)["runs"][0]["purpose"],"retain me")
        restored_exp=server.archive_experiment(self.root,"E-001",archived_exp["updated"],restore=True)
        self.assertNotIn("archived_at",restored_exp)

    def test_solid_run_label_is_reversible_and_enters_same_experiment_ai_context(self):
        first=server.create_run(self.root,"E-001",{"variant":"solid result","purpose":"measure stability","result_summary":"accuracy 0.91 across seeds","result_analysis":"three seeds agree","limitations":"small validation set","claim_boundary":"no domain transfer claim"},"R-solid")
        before={key:first.get(key) for key in ("status","workflow_stage","review_status","execution_authorized_at")}
        labeled=server.set_run_evidence_label(self.root,"R-solid",first["updated"],"solid","三个 seed 一致")
        self.assertEqual(labeled["evidence_label"],"solid"); self.assertEqual({key:labeled.get(key) for key in before},before)
        preview=server.ai_discussion_prompt(self.root,"experiment","E-001","请判断现有证据")
        self.assertIn("R-solid",preview["prompt"]); self.assertIn("accuracy 0.91 across seeds",preview["prompt"]); self.assertIn("不等于 Claim verdict",preview["prompt"])
        source=next(item for item in preview["context_manifest"]["sources"] if item["source_id"]=="run:R-solid")
        self.assertEqual(source["role"],"linked_reference"); self.assertIn("solid",source["label"].lower())
        cleared=server.set_run_evidence_label(self.root,"R-solid",labeled["updated"],"")
        self.assertNotIn("evidence_label",cleared); self.assertEqual(cleared["evidence_label_history"][-1]["action"],"clear")

    def test_non_solid_run_requires_explicit_reference_for_planning_and_implementation(self):
        solid=server.create_run(self.root,"E-001",{"variant":"trusted","result_summary":"SOLID-RESULT-91"},"R-solid-context")
        server.set_run_evidence_label(self.root,solid["id"],solid["updated"],"solid","verified")
        server.create_run(self.root,"E-001",{"variant":"untrusted","result_summary":"NON-SOLID-RESULT-13"},"R-nonsolid-context")
        target=server.create_run(self.root,"E-001",{"variant":"target","research_question":"next?","purpose":"plan","metric_plan":"score"},"R-target-context")
        automatic=server.ai_discussion_prompt(self.root,"experiment","E-001","规划下一个 Run","experiment")
        self.assertIn("SOLID-RESULT-91",automatic["prompt"]); self.assertNotIn("NON-SOLID-RESULT-13",automatic["prompt"])
        explicit=server.ai_discussion_prompt(self.root,"run",target["id"],"实现目标","run_implementation","whole",["R-nonsolid-context"])
        self.assertIn("SOLID-RESULT-91",explicit["prompt"]); self.assertIn("NON-SOLID-RESULT-13",explicit["prompt"])
        self.assertIn("explicit_reference_only",explicit["prompt"]); self.assertIn("Agent memory",explicit["prompt"])
        sources={item["source_id"]:item.get("label","") for item in explicit["context_manifest"]["sources"]}
        self.assertIn("solid",sources["run:R-solid-context"].lower()); self.assertIn("显式",sources["run:R-nonsolid-context"])

    def test_concurrent_updates_are_serialized(self):
        server.create_run(self.root, "E-001", {"variant": "a"}, "R-a")
        server.create_run(self.root, "E-001", {"variant": "b"}, "R-b")
        barrier = threading.Barrier(3)
        errors = []
        def worker(rid, purpose):
            try:
                barrier.wait(); server.update_run(self.root, rid, {"purpose": purpose})
            except Exception as exc: errors.append(exc)
        threads = [threading.Thread(target=worker, args=("R-a", "A")), threading.Thread(target=worker, args=("R-b", "B"))]
        for thread in threads: thread.start()
        barrier.wait()
        for thread in threads: thread.join()
        self.assertFalse(errors)
        rows = {x["id"]: x for x in server.experiment_data(self.root)["runs"]}
        self.assertEqual((rows["R-a"]["purpose"], rows["R-b"]["purpose"]), ("A", "B"))

    def test_corruption_is_explicit_and_quarantined(self):
        path = self.root / ".survey-tool/runs.json"
        path.write_text("{broken", encoding="utf-8")
        with self.assertRaises(server.ToolStateCorruptionError): server.read_tool_json(self.root, "runs.json", [])
        self.assertTrue(list(path.parent.glob("runs.json.corrupt-*")))

    def test_state_transitions_and_structured_proposal(self):
        server.create_run(self.root, "E-001", {"variant": "x"}, "R-x")
        server.update_run(self.root, "R-x", {"status": "running"})
        server.update_run(self.root, "R-x", {"status": "completed_passed_integrity"})
        with self.assertRaises(ValueError): server.update_run(self.root, "R-x", {"status": "running"})
        with self.assertRaises(ValueError): server.update_experiment(self.root, "E-001", {"workflow_stage": "runs_ready"})
        server.update_experiment(self.root, "E-001", {"workflow_stage": "awaiting_confirmation"})
        server.update_experiment(self.root, "E-001", {"workflow_stage": "confirmed", "variables": {"independent": ["routing"], "controls": ["budget"]}})
        self.assertIsInstance(server.experiment_data(self.root)["experiments"][0]["variables"], dict)

    def test_run_review_flow_keeps_authorization_separate_without_blocking_edits(self):
        server.create_run(self.root, "E-001", {"variant": "reviewed", "purpose": "distinguish H1/H2", "command": "python run.py"}, "R-review")
        with self.assertRaisesRegex(ValueError, "尚未审核通过"):
            server.activate_run(self.root, "R-review")
        submitted = server.review_run(self.root, "R-review", "submit", actor="terminal_pi")
        self.assertEqual(submitted["review_status"], "pending_review")
        # 审核中也能改：不再阻断，只记录漂移字段。
        pending_edit = server.update_run(self.root, "R-review", {"purpose": "changed while pending"})
        self.assertEqual(pending_edit["spec_drift_fields"], ["purpose"])
        server.review_run(self.root, "R-review", "request_changes", requirements="固定 split", questions="为何可证伪？")
        revised = server.update_run(self.root, "R-review", {"data_definition": "fixed split", "agent_review_questions": "H1/H2 signatures differ"})
        self.assertEqual(revised["review_status"], "changes_requested")
        server.review_run(self.root, "R-review", "submit", actor="terminal_pi")
        approved = server.review_run(self.root, "R-review", "approve", actor="human")
        self.assertEqual(approved["review_status"], "approved")
        with self.assertRaisesRegex(ValueError, "尚未获得本次执行授权"):
            server.activate_run(self.root, "R-review")
        drifted = server.update_run(self.root, "R-review", {"seed": "99"})
        self.assertIn("seed", drifted["spec_drift_fields"])
        self.assertEqual(drifted["workflow_history"][-1]["action"], "spec_edited_after_approved")
        implementation=server.update_run(self.root,"R-review",{"git_commit":"abc123"})
        self.assertEqual(implementation["review_status"],"approved"); self.assertEqual(implementation["approved_spec"]["git_commit"],"abc123")
        server.review_run(self.root, "R-review", "authorize_execution", actor="human", authorization_note="only this run")
        active = server.activate_run(self.root, "R-review")
        self.assertFalse(active["legacy_activation"]); self.assertEqual(active["outbox_enqueue_result"]["dispatch"]["run_id"], "R-review")
        steward=json.loads((self.root/".pi"/"experiment-steward.json").read_text())
        self.assertEqual(steward["version"],2); self.assertEqual(steward["identity"]["runId"],"R-review"); self.assertEqual(steward["identity"]["experimentId"],"E-001")
        self.assertEqual(steward["experiment"]["processPattern"],r"run\.py"); self.assertEqual(steward["completion"]["exitCodeFile"],"")
        self.assertFalse(steward["identity"]["managedExecution"]); self.assertFalse(steward["completion"]["enabled"]); self.assertFalse(steward["remediation"]["enabled"]); self.assertFalse(steward["archive"]["enabled"])
        self.assertFalse((self.root/".pi"/"experiment-watchdog.json").exists())
        again=server.activate_run(self.root,"R-review"); self.assertTrue(again["outbox_enqueue_result"]["idempotent"])

    def test_workspace_binding_change_after_authorization_blocks_claim(self):
        server.create_run(self.root,"E-001",{"variant":"snapshot","purpose":"binding snapshot","command":"python run.py"},"R-binding")
        server.review_run(self.root,"R-binding","submit",actor="terminal_pi"); server.review_run(self.root,"R-binding","approve",actor="human"); server.review_run(self.root,"R-binding","authorize_execution",actor="human",authorization_note="one snapshot")
        active=server.activate_run(self.root,"R-binding"); self.assertTrue(active["outbox_enqueue_result"]["queued"])
        workspaces=server.experiment_data(self.root)["workspaces"]; workspaces[0]["environment_activation"]="source /changed-after-authorization"
        server.write_tool_json(self.root,"workspaces.json",workspaces)
        claimed=server.claim_next_execution(self.root,"consumer")
        self.assertFalse(claimed["claimed"])
        item=next(x for x in server.execution_outbox_public(self.root)["execution_outbox"]["items"] if x["run_id"]=="R-binding")
        self.assertEqual(item["status"],"cancelled"); self.assertIn("Workspace binding/policy changed",item["last_error"])

    def test_managed_reattach_rotates_only_expired_owned_running_dispatch(self):
        server.create_run(self.root,"E-001",{"variant":"reattach","purpose":"lease recovery","command":"python run.py"},"R-reattach")
        server.review_run(self.root,"R-reattach","submit",actor="terminal_pi"); server.review_run(self.root,"R-reattach","approve",actor="human"); server.review_run(self.root,"R-reattach","authorize_execution",actor="human",authorization_note="managed")
        claim=server.claim_next_execution(self.root,"old-pi"); token=claim["lease_token"]; dispatch=claim["task"]["dispatch"]
        server._leased_transition(self.root,dispatch["dispatch_id"],token,"old-pi","acknowledge",{"actual_agent":dispatch["requested_agent"],"actual_model":dispatch["requested_model"]})
        server._leased_transition(self.root,dispatch["dispatch_id"],token,"old-pi","running",{"managed_execution":True})
        box=server._outbox_read(self.root); box["items"][0]["lease_expires_at"]=(datetime.datetime.now()-datetime.timedelta(seconds=1)).isoformat(); server.write_tool_json(self.root,"execution-outbox.json",box)
        with self.assertRaisesRegex(ValueError,"不是受控 managed start"): server.reattach_managed_execution(self.root,dispatch["dispatch_id"],"new-pi")
        server.update_managed_execution_metadata(self.root,dispatch["dispatch_id"],{"started_evidence":"tmux_new_session_ok"}); box=server._outbox_read(self.root); box["items"][0]["lease_expires_at"]=(datetime.datetime.now()+datetime.timedelta(minutes=1)).isoformat(); server.write_tool_json(self.root,"execution-outbox.json",box)
        with self.assertRaisesRegex(ValueError,"尚未过期"): server.reattach_managed_execution(self.root,dispatch["dispatch_id"],"new-pi")
        data=server.experiment_data(self.root); stale=next(row for row in data["runs"] if row["id"]=="R-reattach"); stale["workflow_stage"]="failed"; stale["status"]="failed"; stale["execution_dispatch_latest_status"]="failed"; stale["execution_dispatch_failure"]={"failure_class":"stale_ui_projection"}; server.write_tool_json(self.root,"runs.json",data["runs"])
        box=server._outbox_read(self.root); box["items"][0]["lease_expires_at"]=(datetime.datetime.now()-datetime.timedelta(seconds=1)).isoformat(); server.write_tool_json(self.root,"execution-outbox.json",box)
        attached=server.reattach_managed_execution(self.root,dispatch["dispatch_id"],"new-pi"); self.assertTrue(attached["reattached"]); self.assertTrue(attached["run_projection_repaired"]); self.assertTrue(attached["lease_token"]); self.assertNotIn("token",json.dumps(attached["dispatch"]).lower())
        repaired=next(row for row in server.experiment_data(self.root)["runs"] if row["id"]=="R-reattach"); self.assertEqual(repaired["workflow_stage"],"running"); self.assertEqual(repaired["execution_dispatch_latest_status"],"running"); self.assertNotIn("execution_dispatch_failure",repaired)
        public=server.execution_outbox_public(self.root); self.assertNotIn("token",json.dumps(public).lower())
        box=server._outbox_read(self.root); box["items"][0]["lease_expires_at"]=(datetime.datetime.now()-datetime.timedelta(seconds=1)).isoformat(); server.write_tool_json(self.root,"execution-outbox.json",box)
        workspaces=server.experiment_data(self.root)["workspaces"]; workspaces[0]["environment_activation"]="source /changed"; server.write_tool_json(self.root,"workspaces.json",workspaces)
        with self.assertRaisesRegex(ValueError,"Workspace binding/policy changed"): server.reattach_managed_execution(self.root,dispatch["dispatch_id"],"third-pi")

    def test_run_script_honors_timeout(self):
        started = time.monotonic()
        result = server.run_script([sys.executable, "-c", "import time;time.sleep(1)"], timeout=.1)
        self.assertLess(time.monotonic() - started, .7)
        self.assertIn("timed out", result["stderr"].lower())

    def test_groups_metrics_policy_and_read_only_constraints(self):
        metric={"id":"accuracy","name":"准确率","formula":"正确数/样本数","meaning":"回答正确比例","direction":"higher","unit":"ratio","aggregation":"mean","scope":"evaluation split"}
        server.update_experiment(self.root,"E-001",{"run_groups":[{"id":"baseline","name":"基线","description":"基准责任组"}],"metric_definitions":[metric]})
        run=server.create_run(self.root,"E-001",{"variant":"基线","group_id":"baseline","metric_observations":[{"metric_id":"accuracy","value":0.75,"sample_count":20,"uncertainty":"95% CI ±0.1","artifact":"metrics.json","interpretation":"高于随机水平"}]},"R-metric")
        note=self.root/"shell/06_experiments/E-001/runs/baseline/R-metric.md"
        self.assertTrue(note.exists()); self.assertIn("样本数：20",note.read_text(encoding="utf-8"))
        result=(self.root/"shell/06_experiments/E-001/result.md").read_text(encoding="utf-8")
        for expected in ("### 基线 (`baseline`)","准确率=0.75 ratio","指标含义：回答正确比例","本轮解释：高于随机水平","来源/产物：metrics.json"):
            self.assertIn(expected,result)
        self.assertEqual(server.object_path(self.root,"run","R-metric"),note)
        context=server.experiment_constraints(self.root,"E-001","R-metric")
        self.assertEqual(context["run_groups"][0]["id"],"baseline")
        self.assertIn("forbidden_operations",context); self.assertIn("policy_violations",context["target_run"]["resolved"])
        self.assertNotIn("resolved",context["runs"][0]); self.assertIn("detail_hint",context)
        full=server.experiment_constraints(self.root,"E-001",full=True)
        self.assertIn("resolved",full["runs"][0]); self.assertNotIn("target_run",full)
        with self.assertRaisesRegex(ValueError,"未在 Experiment 注册"):
            server.update_run(self.root,run["id"],{"group_id":"unknown"})
        with self.assertRaisesRegex(ValueError,"不能删除已有观测引用的指标"):
            server.update_experiment(self.root,"E-001",{"metric_definitions":[]})
        changed={**metric,"id":"accuracy-v2"}
        with self.assertRaisesRegex(ValueError,"不能删除已有观测引用的指标"):
            server.update_experiment(self.root,"E-001",{"metric_definitions":[changed]})
        renamed=server.update_experiment(self.root,"E-001",{"metric_definitions":[{**metric,"name":"正确率"}]})
        self.assertEqual(renamed["metric_definitions"][0]["name"],"正确率")
        for key,value in (("formula","hits/n"),("meaning","另一种含义"),("direction","lower"),("unit","percent"),("aggregation","median"),("scope","train")):
            with self.assertRaisesRegex(ValueError,"指标语义不可修改"):
                server.update_experiment(self.root,"E-001",{"metric_definitions":[{**renamed["metric_definitions"][0],key:value}]})
        mission=(self.root/"shell/06_experiments/E-001/mission.md").read_text(encoding="utf-8")
        self.assertIn("若环境中可用 Herdr",mission); self.assertIn("local_tool_edit",mission); self.assertIn("experiment_code_edit",mission)
        self.assertNotIn("E-001-handoff.json",mission); self.assertIn("shell/06_experiments/E-001/handoff.json",mission)
        policy=context["workspace"]["environment_policy"]
        self.assertNotIn("/datasets",policy["allowed_write_roots"]); self.assertIn("/datasets",policy["read_only_roots"])
        self.assertEqual(policy["allowed_write_roots"],["/repo","/worktrees","/exp"])

    def test_tmp_is_forbidden_for_persistent_run_paths(self):
        run=server.create_run(self.root,"E-001",{"variant":"bad path","artifact_dir":"/tmp/R-tmp"},"R-tmp")
        resolved=server.resolve_run_config(self.root,run)
        self.assertFalse(resolved["policy_ok"])
        self.assertTrue(any("/tmp" in x["reason"] for x in resolved["policy_violations"]))
        # Historical review compatibility does not bypass the environment policy.
        run["status"]="running"; run.pop("review_status",None); server.write_tool_json(self.root,"runs.json",[run])
        with self.assertRaisesRegex(ValueError,"环境策略"):
            server.activate_run(self.root,"R-tmp")

    def test_workspace_repo_is_default_project_dir_not_synthetic_experiment_worktree(self):
        run=server.create_run(self.root,"E-001",{"variant":"repo cwd","artifact_dir":"/exp/E-001/R-cwd"},"R-cwd")
        resolved=server.resolve_run_config(self.root,run)
        self.assertEqual(resolved["project_dir"],"/repo")
        self.assertNotEqual(resolved["project_dir"],"/worktrees/E-001")
        data=server.experiment_data(self.root); exp=next(row for row in data["experiments"] if row["id"]=="E-001"); exp["remote_worktree"]="/worktrees/explicit-E-001"; server.write_tool_json(self.root,"experiments.json",data["experiments"])
        self.assertEqual(server.resolve_run_config(self.root,run)["project_dir"],"/worktrees/explicit-E-001")

    def test_run_trial_plan_expands_bounded_cartesian_matrix(self):
        plan=server.build_run_trial_plan("比较参数组合",[{"name":"variant","values":["base","permute"]},{"name":"seed","values":[1,2,3]}],2,1)
        self.assertEqual(plan["contract"],"survey-tool.run-trial-plan/v1"); self.assertEqual(len(plan["trials"]),6); self.assertEqual(plan["trials"][4]["parameters"],{"variant":"permute","seed":2}); self.assertEqual(plan["concurrency"],2)
        ai=server.build_run_trial_plan("根据代码和已有结果规划",None,2,1,"ai_planned",9)
        self.assertEqual(ai["planning_mode"],"ai_planned"); self.assertEqual(ai["trial_budget"],9); self.assertEqual(ai["trials"],[]); self.assertEqual(ai["planning_status"],"awaiting_ai")
        with self.assertRaisesRegex(ValueError,"预算"): server.build_run_trial_plan("bad",None,1,0,"ai_planned",65)
        with self.assertRaisesRegex(ValueError,"不接受"): server.build_run_trial_plan("bad",[{"name":"seed","values":[1]}],1,0,"ai_planned",4)
        with self.assertRaisesRegex(ValueError,"64"): server.build_run_trial_plan("too many",[{"name":"a","values":list(range(9))},{"name":"b","values":list(range(9))}],1,0)
        with self.assertRaisesRegex(ValueError,"安全且唯一"): server.build_run_trial_plan("bad",[{"name":"x;rm","values":[1]}],1,0)

    def test_workspace_policy_presets_and_backend_danger_detection(self):
        ws=server.experiment_data(self.root)["workspaces"][0]
        safe=server.validate_workspace_policy(ws,{"policy_preset":"research-safe","allowed_write_roots":["/repo","/worktrees","/exp"],"read_only_roots":["/datasets"],"forbidden_paths":["/tmp"],"forbidden_operations":["删除数据"],"temp_policy":"分类临时目录","notes":"safe","dangerous_exceptions":["客户端伪造"]})
        self.assertEqual(safe["policy_preset"],"research-safe"); self.assertEqual(safe["dangerous_exceptions"],[])
        dangerous=server.validate_workspace_policy(ws,{"policy_preset":"research-safe","allowed_write_roots":["/tmp","/datasets"],"read_only_roots":[],"forbidden_paths":[],"forbidden_operations":[],"temp_policy":"自由","notes":"human accepted","dangerous_exceptions":[]})
        self.assertEqual(dangerous["policy_preset"],"custom")
        self.assertEqual(len(dangerous["dangerous_exceptions"]),4)
        self.assertTrue(any("数据根可写" in x for x in dangerous["dangerous_exceptions"]))
        nested=server.validate_workspace_policy(ws,{"policy_preset":"custom","allowed_write_roots":["/tmp/job","/datasets/cache"],"read_only_roots":[],"forbidden_paths":["/tmp"],"forbidden_operations":["删除数据"]})
        self.assertIn("/tmp/job",nested["allowed_write_roots"])
        self.assertIn("/tmp",nested["forbidden_paths"])
        with self.assertRaisesRegex(ValueError,"未声明字段"): server.validate_workspace_policy(ws,{"mystery":True})
        with self.assertRaisesRegex(ValueError,"字符串数组"): server.validate_workspace_policy(ws,{"allowed_write_roots":"/repo"})
        server.create_run(self.root,"E-001",{"variant":"policy isolation"},"R-policy")
        with self.assertRaisesRegex(ValueError,"未声明字段"): server.update_experiment(self.root,"E-001",{"environment_policy":{}})
        with self.assertRaisesRegex(ValueError,"未声明字段"): server.update_run(self.root,"R-policy",{"environment_policy":{}})

    def test_agent_routing_defaults_validation_context_and_mission(self):
        default=server.agent_routing_policy(self.root)
        self.assertEqual(default["routes"]["local_tool_edit"]["model"],"gpt-5.6-luna")
        self.assertEqual(default["routes"]["experiment_code_edit"]["model"],"gpt-5.6-sol")
        aliased=server.validate_agent_routing({"version":1,"routes":{"local_tool_edit":{"enabled":True,"agent_kind":"codex","model":"luna","fallback_agent_kind":"pi","fallback_model":""},"experiment_code_edit":{"enabled":True,"agent_kind":"codex","model":"sol","fallback_agent_kind":"pi","fallback_model":""}}})
        self.assertEqual(aliased["routes"]["experiment_code_edit"]["model"],"gpt-5.6-sol")
        custom={"version":1,"routes":{"local_tool_edit":{"enabled":True,"agent_kind":"codex","model":"custom-luna","fallback_agent_kind":"pi","fallback_model":""},"experiment_code_edit":{"enabled":True,"agent_kind":"codex","model":"custom-sol","fallback_agent_kind":"pi","fallback_model":"safe"}}}
        server.write_agent_routing(self.root,custom)
        context=server.experiment_constraints(self.root,"E-001")
        self.assertEqual(context["agent_routing"]["routes"]["local_tool_edit"],custom["routes"]["local_tool_edit"])
        self.assertEqual(context["agent_routing"]["routes"]["lightweight_governance"]["inherited_from"],"local_tool_edit")
        mission=(self.root/"shell/06_experiments/E-001/mission.md").read_text(encoding="utf-8")
        self.assertIn("local_tool_edit",mission); self.assertIn("custom-luna",mission); self.assertIn("custom-sol",mission)
        with self.assertRaisesRegex(ValueError,"未声明字段"): server.validate_agent_routing({**custom,"command":"rm -rf"})
        with self.assertRaisesRegex(ValueError,"必须声明"): server.validate_agent_routing({"version":1,"routes":{"local_tool_edit":custom["routes"]["local_tool_edit"]}})
        with self.assertRaisesRegex(ValueError,"未声明字段"): server.update_run(self.root,server.create_run(self.root,"E-001",{"variant":"routing"},"R-routing")["id"],{"agent_routing":custom})

    def test_atomic_run_grouping_and_review_lock(self):
        server.update_experiment(self.root,"E-001",{"run_groups":[{"id":"old","name":"旧组","description":"旧职责"}]})
        server.create_run(self.root,"E-001",{"variant":"A","group_id":"old"},"R-group-a")
        server.create_run(self.root,"E-001",{"variant":"B","group_id":"old"},"R-group-b")
        out=server.apply_run_grouping(self.root,"E-001",[{"id":"baseline","name":"基线","description":"建立基准","color":"#4f7cff"},{"id":"analysis","name":"分析","description":"机制分析","color":"#22a06b"}],{"R-group-a":"baseline","R-group-b":"analysis"})
        rows={r["id"]:r for r in out["runs"]}; self.assertEqual(rows["R-group-a"]["group_id"],"baseline")
        self.assertTrue((self.root/"shell/06_experiments/E-001/runs/baseline/R-group-a.md").exists())
        self.assertEqual(next(e for e in out["experiments"] if e["id"]=="E-001")["run_groups"][0]["color"],"#4f7cff")
        with self.assertRaisesRegex(ValueError,"color"):
            server.update_experiment(self.root,"E-001",{"run_groups":[{"id":"bad","name":"Bad","color":"red"}]})
        server.review_run(self.root,"R-group-a","submit",actor="terminal_pi")
        with self.assertRaisesRegex(ValueError,"正在审核或已批准"):
            server.apply_run_grouping(self.root,"E-001",[{"id":"baseline","name":"基线"},{"id":"analysis","name":"分析"}],{"R-group-a":"analysis","R-group-b":"analysis"})

    def test_run_grouping_allows_empty_groups_and_ungrouped_but_requires_complete_apply(self):
        server.update_experiment(self.root,"E-001",{"run_groups":[{"id":"temporary","name":"临时组"}]})
        server.create_run(self.root,"E-001",{"variant":"A","group_id":"temporary"},"R-loose-a")
        server.create_run(self.root,"E-001",{"variant":"B"},"R-loose-b")
        self.assertTrue((self.root/"shell/06_experiments/E-001/runs/temporary/R-loose-a.md").exists())
        with self.assertRaisesRegex(ValueError,"未覆盖 Run"):
            server.apply_run_grouping(self.root,"E-001",[],{"R-loose-a":""})
        out=server.apply_run_grouping(self.root,"E-001",[],{"R-loose-a":"","R-loose-b":""})
        exp=next(x for x in out["experiments"] if x["id"]=="E-001")
        self.assertEqual(exp["run_groups"],[])
        self.assertTrue(all(r.get("group_id","")=="" for r in out["runs"] if r["id"].startswith("R-loose")))
        self.assertTrue((self.root/"shell/06_experiments/E-001/runs/R-loose-a.md").exists())

    def test_cli_structured_json_round_trip(self):
        metric={"id":"loss","name":"损失","formula":"sum(loss)/n","meaning":"平均误差","direction":"lower","unit":"point","aggregation":"mean","scope":"validation"}
        old_load=surveyctl.server.load_config; old_argv=sys.argv
        surveyctl.server.load_config=lambda:{"projects_root":str(self.root.parent),"projects":[str(self.root)],"skill_dir":str(ROOT/"skills/research-survey"),"port":7421}
        def invoke(*args):
            sys.argv=["surveyctl.py","--project",str(self.root),*args]
            out=io.StringIO()
            with contextlib.redirect_stdout(out): surveyctl.main()
            return json.loads(out.getvalue())
        try:
            invoke("experiment","governance","E-001","--run-groups-json",json.dumps([{"id":"eval","name":"评测"}]),"--metric-definitions-json",json.dumps([metric]))
            created=invoke("run","create","E-001","--id","R-cli","--variant","CLI","--group-id","eval","--metric-observations",json.dumps([{"metric_id":"loss","value":1.2,"sample_count":8,"provenance":"eval.json","interpretation":"仍需降低"}]))
            self.assertEqual(created["metric_observations"][0]["sample_count"],8)
            updated=invoke("run","update","R-cli","--metric-observations",json.dumps([{"metric_id":"loss","value":0.9,"sample_count":9,"uncertainty":"±0.1","artifact":"metrics.json","interpretation":"改善"}]))
            self.assertEqual(updated["metric_observations"][0]["value"],0.9)
        finally:
            surveyctl.server.load_config=old_load; sys.argv=old_argv

    def _review_ready_fields(self, rid, **extra):
        fields={"variant":"透明评分","purpose":"比较处理组和固定对照","necessity":"区分两个竞争假设","implementation_summary":"运行固定脚本并保存审计产物","data_definition":"固定 validation split，数据集版本 v1","data_scale":"n=128","variables_controls":"仅改变 treatment；baseline 配置保持不变","metric_definition":"使用 Experiment 注册的 accuracy，按样本均值统计","integrity_gates":"样本数必须为 128，缺失或 silent zero 立即失败","acceptance_criteria":"accuracy >= 0.8 且完整性门槛通过","conclusion_scope":"仅支持该固定 split 上的比较","claim_boundary":"不支持因果结论或外推到其他数据集","workspace_id":"W-01","command":"python run.py --config fixed.json","artifact_dir":f"/exp/E-001/{rid}","metric_observations":[{"metric_id":"accuracy","value":0.9,"sample_count":128,"uncertainty":"95% CI ±0.02","provenance":"metrics.json","interpretation":"达到预设验收条件"}]}
        fields.update(extra); return fields

    def _review_ready_run(self, rid, **extra):
        return server.create_run(self.root,"E-001",self._review_ready_fields(rid,**extra),rid)

    def test_review_policy_is_human_only_and_has_no_scoring_surface(self):
        exp=server.experiment_data(self.root)["experiments"][0]
        self.assertFalse(server.effective_review_automation_policy(exp)["enabled"])
        # Legacy score-era policies stay readable and normalize to the score-free shape.
        migrated=server.validate_review_automation_policy({"enabled":True,"auto_approve_threshold":90,"auto_authorize_execution":True,"auto_authorize_threshold":80,"policy_version":server.RUN_REVIEW_SCORE_VERSION})
        self.assertEqual(migrated["policy_version"],server.REVIEW_AUTOMATION_POLICY_VERSION)
        for legacy in ("auto_approve_threshold","auto_authorize_threshold","auto_authorize_execution"):
            self.assertNotIn(legacy,migrated)
        with self.assertRaisesRegex(ValueError,"boolean"):
            server.validate_review_automation_policy({"auto_review_on_create":"yes"})
        with self.assertRaisesRegex(ValueError,"未声明字段"):
            server.validate_review_automation_policy({"enabled":True,"score_threshold":3})
        with self.assertRaisesRegex(ValueError,"未声明字段"):
            server.update_experiment(self.root,"E-001",{"review_automation_policy":{"enabled":True}})
        server.create_run(self.root,"E-001",{"variant":"isolation"},"R-policy-isolation")
        with self.assertRaisesRegex(ValueError,"未声明字段"):
            server.update_run(self.root,"R-policy-isolation",{"review_automation_policy":{"enabled":True}})
        # The scoring machinery is gone, not merely hidden.
        for name in ("review_score_for_run","review_score_map","run_review_score","run_review_score_v2"):
            self.assertFalse(hasattr(server,name),name)
        payload=server.create_run_dashboard_response(self.root,next(r for r in server.experiment_data(self.root)["runs"] if r["id"]=="R-policy-isolation"))
        self.assertNotIn("review_scores",payload); self.assertNotIn("review_scores",server.experiment_dashboard_data(self.root))

    def test_auto_review_only_submits_for_human_review(self):
        metric={"id":"accuracy","name":"准确率","formula":"correct/n","meaning":"正确样本比例","direction":"higher","unit":"ratio","aggregation":"mean","scope":"validation"}
        server.update_experiment(self.root,"E-001",{"metric_definitions":[metric]})
        self._review_ready_run("R-auto-ok")
        server.create_run(self.root,"E-001",{"variant":"含占位符","purpose":"待确认","command":"python run.py"},"R-auto-human")
        self._review_ready_run("R-auto-complete"); server.update_run(self.root,"R-auto-complete",{"status":"completed_passed_integrity"})
        disabled=server.auto_review_run(self.root,"R-auto-ok")
        self.assertTrue(disabled["needs_human_review"]); self.assertFalse(disabled["changed"])
        policy={"enabled":True,"policy_version":server.REVIEW_AUTOMATION_POLICY_VERSION,"notes":"人类开启自动提交"}
        server.save_review_automation_policy(self.root,"E-001",policy)
        blocked=server.auto_review_run(self.root,"R-auto-human")
        self.assertTrue(blocked["needs_human_review"]); self.assertEqual(blocked["review_status"],"draft")
        self.assertTrue(any("待确认" in x for x in blocked["blockers"]))
        applied=server.auto_review_run(self.root,"R-auto-ok")
        self.assertEqual(applied["actions"],["submit"]); self.assertTrue(applied["needs_human_review"])
        self.assertEqual(applied["review_status"],"pending_review"); self.assertEqual(applied["reason"],"submitted_for_human_review")
        run=next(r for r in server.experiment_data(self.root)["runs"] if r["id"]=="R-auto-ok")
        self.assertEqual(run["review_status"],"pending_review"); self.assertNotIn("approved_at",run); self.assertNotIn("execution_authorized_at",run)
        self.assertEqual(run["automation_review_snapshot"]["actor"],"automation_policy")
        again=server.auto_review_run(self.root,"R-auto-ok")
        self.assertFalse(again["changed"]); self.assertEqual(again["reason"],"already_submitted_for_review")
        batch=server.auto_review_experiment(self.root,"E-001")
        self.assertTrue(any(x["run_id"]=="R-auto-human" for x in batch["human_review_queue"]))
        self.assertTrue(any(x["run_id"]=="R-auto-ok" for x in batch["human_review_queue"]))
        self.assertTrue(all(x["review_status"]!="approved" for x in batch["human_review_queue"]))
        self.assertTrue(any(x["run_id"]=="R-auto-complete" for x in batch["skipped"]))

    def test_cli_auto_review_submits_only(self):
        metric={"id":"accuracy","name":"准确率","formula":"correct/n","meaning":"正确样本比例","direction":"higher","unit":"ratio","aggregation":"mean","scope":"validation"}
        server.update_experiment(self.root,"E-001",{"metric_definitions":[metric]}); self._review_ready_run("R-cli-review")
        server.save_review_automation_policy(self.root,"E-001",{"enabled":True,"policy_version":server.REVIEW_AUTOMATION_POLICY_VERSION,"notes":"CLI"})
        old_load=surveyctl.server.load_config; old_argv=sys.argv
        surveyctl.server.load_config=lambda:{"projects_root":str(self.root.parent),"projects":[str(self.root)],"skill_dir":str(ROOT/"skills/research-survey"),"port":7421}
        def invoke(*args):
            sys.argv=["surveyctl.py","--project",str(self.root),*args]; out=io.StringIO()
            with contextlib.redirect_stdout(out): surveyctl.main()
            return json.loads(out.getvalue())
        try:
            action=invoke("run","auto-review","R-cli-review")
            self.assertEqual(action["actions"],["submit"]); self.assertNotIn("approve",action["actions"])
            bulk=invoke("experiment","auto-review","E-001"); self.assertIn("human_review_queue",bulk)
        finally:
            surveyctl.server.load_config=old_load; sys.argv=old_argv

    def test_create_time_automation_submits_but_never_approves(self):
        metric={"id":"accuracy","name":"准确率","formula":"correct/n","meaning":"正确样本比例","direction":"higher","unit":"ratio","aggregation":"mean","scope":"validation"}
        server.update_experiment(self.root,"E-001",{"metric_definitions":[metric]})
        policy={"enabled":True,"auto_review_on_create":True,"policy_version":server.REVIEW_AUTOMATION_POLICY_VERSION,"notes":"create-time"}
        server.save_review_automation_policy(self.root,"E-001",policy)
        # Human creation never triggers automation.
        human=self._review_ready_run("R-create-human",created_by="human")
        self.assertEqual(human["review_status"],"draft"); self.assertNotIn("create_time_review_evaluation",human)
        manual=self._review_ready_run("R-create-manual",created_by="manual")
        self.assertNotIn("create_time_review_evaluation",manual)
        server.save_review_automation_policy(self.root,"E-001",{**policy,"enabled":False})
        off=self._review_ready_run("R-create-off",created_by="terminal_pi")
        self.assertEqual(off["review_status"],"draft"); self.assertNotIn("create_time_review_evaluation",off)
        # Enabled agent Run is submitted for human review, never approved or authorized.
        server.save_review_automation_policy(self.root,"E-001",policy)
        high=self._review_ready_run("R-create-high",created_by="agent")
        self.assertEqual(high["review_status"],"pending_review"); self.assertNotIn("approved_at",high)
        self.assertNotIn("execution_authorized_at",high)
        self.assertTrue(high["create_time_review_evaluation"]["applied"]); self.assertTrue(high["create_time_review_evaluation"]["needs_human_review"])
        api_payload=server.create_run_dashboard_response(self.root,high)
        self.assertEqual(api_payload["run"]["review_status"],"pending_review"); self.assertTrue(api_payload["auto_review_result"]["applied"])
        self.assertNotIn("review_scores",api_payload)
        # An incomplete agent Run stays draft and records why.
        low=server.create_run(self.root,"E-001",{"variant":"不完整","created_by":"ai_import","purpose":"待确认"},"R-create-low")
        self.assertEqual(low["review_status"],"draft"); self.assertTrue(low["create_time_review_evaluation"]["needs_human_review"])
        self.assertFalse(low["create_time_review_evaluation"]["applied"]); self.assertTrue(low["create_time_review_evaluation"]["blockers"])
        events=server.read_tool_json(self.root,"experiment-events.jsonl",[])
        self.assertTrue(any(e.get("type")=="run_create_auto_review_evaluation" and e.get("run_id")=="R-create-low" for e in events))
        stamp=low["automation_reviewed_at"]
        updated=server.update_run(self.root,"R-create-low",{"notes":"普通更新不重新评估"})
        self.assertEqual(updated["automation_reviewed_at"],stamp)
        original=server.auto_review_run
        server.auto_review_run=lambda *_args,**_kwargs: (_ for _ in ()).throw(RuntimeError("synthetic automation failure"))
        try: failed=self._review_ready_run("R-create-error",created_by="automation")
        finally: server.auto_review_run=original
        self.assertEqual(failed["review_status"],"draft"); self.assertEqual(failed["create_time_review_evaluation"]["decision"],"error")
        self.assertIn("synthetic automation failure",failed["create_time_review_evaluation"]["reason"])

    def test_create_time_automation_never_authorizes_execution_and_cli_final_output(self):
        metric={"id":"accuracy","name":"准确率","formula":"correct/n","meaning":"正确样本比例","direction":"higher","unit":"ratio","aggregation":"mean","scope":"validation"}
        server.update_experiment(self.root,"E-001",{"metric_definitions":[metric]})
        policy={"enabled":True,"auto_review_on_create":True,"policy_version":server.REVIEW_AUTOMATION_POLICY_VERSION,"notes":"preauth"}
        server.save_review_automation_policy(self.root,"E-001",policy)
        submitted=self._review_ready_run("R-create-authorized",created_by="codex")
        self.assertEqual(submitted["review_status"],"pending_review")
        self.assertNotIn("execution_authorized_at",submitted); self.assertNotIn("execution_started_at",submitted)
        old_load=surveyctl.server.load_config; old_argv=sys.argv
        surveyctl.server.load_config=lambda:{"projects_root":str(self.root.parent),"projects":[str(self.root)],"skill_dir":str(ROOT/"skills/research-survey"),"port":7421}
        try:
            sys.argv=["surveyctl.py","--project",str(self.root),"run","create","E-001","--id","R-create-cli","--variant","CLI","--purpose","比较处理组和对照","--necessity","区分竞争假设","--implementation-summary","执行固定脚本","--data-definition","固定 validation split","--data-scale","n=128","--variables-controls","仅改变 treatment","--metric-definition","accuracy correct/n","--integrity-gates","样本数 128","--acceptance-criteria","accuracy >= 0.8","--claim-boundary","不外推","--workspace-id","W-01","--command","python run.py","--artifact-dir","/exp/E-001/R-create-cli","--metric-observations",json.dumps([{"metric_id":"accuracy","value":0.9,"sample_count":128}])]
            out=io.StringIO()
            with contextlib.redirect_stdout(out): surveyctl.main()
            final=json.loads(out.getvalue())
            self.assertEqual(final["review_status"],"draft"); self.assertEqual(final["workflow_version"],2); self.assertEqual(final["workflow_stage"],"code_planning"); self.assertIn("automation_review_snapshot",final); self.assertNotIn("execution_authorized_at",final)
        finally:
            surveyctl.server.load_config=old_load; sys.argv=old_argv

    def test_agent_grouping_partial_success_locks_conflicts_keep_and_idempotency(self):
        server.update_experiment(self.root,"E-001",{"run_groups":[{"id":"old","name":"原组"}]})
        for rid in ("R-move","R-lock","R-conflict","R-stay","R-unmentioned"):
            server.create_run(self.root,"E-001",{"variant":rid,"group_id":"old"},rid)
        server.review_run(self.root,"R-lock","submit",actor="terminal_pi")
        conflict=self.root/"shell/06_experiments/E-001/runs/new/R-conflict.md"; conflict.parent.mkdir(parents=True,exist_ok=True); conflict.write_text("stale\n",encoding="utf-8")
        out=server.apply_agent_run_grouping(self.root,"E-001",[
            {"id":"new","name":"新组"},{"id":"unused","name":"未用组"},
            {"id":"kept","name":"保留空组","keep":True},{"id":"locked-only","name":"仅锁定引用"}],
            {"R-move":"new","R-lock":"locked-only","R-conflict":"new","R-stay":"old","R-unknown":"new","R-move-bad":"missing-group"})
        result=out["grouping_result"]; self.assertEqual(result["totals"],{"applied":1,"skipped":4,"unchanged":1,"groups_added":2})
        self.assertEqual(result["applied"],[{"run_id":"R-move","from":"old","to":"new"}])
        reasons={x["run_id"]:x["reason"] for x in result["skipped"]}
        self.assertEqual(reasons["R-lock"],"locked"); self.assertEqual(reasons["R-conflict"],"note_conflict"); self.assertEqual(reasons["R-unknown"],"unknown"); self.assertEqual(reasons["R-move-bad"],"unknown")
        # Exercise invalid_group on a known Run independently of the successful move.
        invalid=server.apply_agent_run_grouping(self.root,"E-001",[],{"R-stay":"missing-group"})["grouping_result"]
        self.assertEqual(invalid["skipped"][0]["reason"],"invalid_group")
        data=server.experiment_data(self.root); exp=data["experiments"][0]; groups={g["id"]:g for g in exp["run_groups"]}
        self.assertEqual(set(groups),{"old","new","kept"}); self.assertNotIn("keep",groups["kept"])
        rows={r["id"]:r for r in data["runs"]}; self.assertEqual(rows["R-move"]["group_id"],"new"); self.assertEqual(rows["R-lock"]["group_id"],"old"); self.assertEqual(rows["R-stay"]["group_id"],"old")
        self.assertEqual(rows["R-unmentioned"]["group_id"],"old")
        self.assertTrue((self.root/"shell/06_experiments/E-001/runs/new/R-move.md").exists())
        repeated=server.apply_agent_run_grouping(self.root,"E-001",[{"id":"new","name":"新组"}],{"R-move":"new"})["grouping_result"]
        self.assertEqual(repeated["totals"]["applied"],0); self.assertEqual(repeated["totals"]["unchanged"],1)
        events=server.read_tool_json(self.root,"experiment-events.jsonl",[])
        self.assertTrue(any(e.get("type")=="agent_run_grouping" for e in events))
        locked=next(r for r in server.experiment_data(self.root)["runs"] if r["id"]=="R-lock")
        self.assertEqual(locked["review_status"],"pending_review"); self.assertNotIn("claim_verdict",locked); self.assertNotIn("execution_authorized_at",locked)

    def test_cli_agent_grouping_json_and_file(self):
        server.update_experiment(self.root,"E-001",{"run_groups":[{"id":"old","name":"原组"}]})
        server.create_run(self.root,"E-001",{"variant":"CLI","group_id":"old"},"R-cli-group")
        old_load=surveyctl.server.load_config; old_argv=sys.argv
        surveyctl.server.load_config=lambda:{"projects_root":str(self.root.parent),"projects":[str(self.root)],"skill_dir":str(ROOT/"skills/research-survey"),"port":7421}
        def invoke(*args):
            sys.argv=["surveyctl.py","--project",str(self.root),*args]; out=io.StringIO()
            with contextlib.redirect_stdout(out): surveyctl.main()
            return json.loads(out.getvalue())
        try:
            proposal={"experiment_id":"E-001","groups":[{"id":"cli","name":"CLI 组"}],"assignments":{"R-cli-group":"cli"}}
            first=invoke("experiment","agent-grouping","E-001","--proposal-json",json.dumps(proposal)); self.assertEqual(first["grouping_result"]["totals"]["applied"],1)
            path=self.root/"shell/06_experiments/E-001/grouping-proposal.json"; path.write_text(json.dumps(proposal),encoding="utf-8")
            second=invoke("experiment","agent-grouping","E-001","--file",str(path)); self.assertEqual(second["grouping_result"]["totals"]["unchanged"],1)
        finally:
            surveyctl.server.load_config=old_load; sys.argv=old_argv


if __name__ == "__main__":
    unittest.main()
