import json,pathlib,tempfile,unittest,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import server
class ExplorerTest(unittest.TestCase):
 def setUp(self):
  self.root=pathlib.Path(tempfile.mkdtemp(prefix="explorer-test-"));(self.root/"state.md").write_text("state: TEST\n");server.CFG={"projects_root":str(self.root.parent),"projects":[str(self.root)],"skill_dir":str(ROOT/"skills/research-survey"),"port":7421};server.SKILL=ROOT/"skills/research-survey";server.SKILL_SCRIPTS=server.SKILL/"scripts"
  server.write_tool_json(self.root,"servers.json",[{"id":"S-01","ssh_host":"test"}]);server.write_tool_json(self.root,"workspaces.json",[{"id":"W-01","server_id":"S-01","remote_repo":"/repo","remote_experiment_root":"/exp"}]);server.create_experiment(self.root,{"title":"实验","objective":"目标","workspace_id":"W-01","run_groups":[{"id":"keep","name":"保留","description":"已有","color":"#123456"}]},"E-001")
  (self.root/"shell/00_idea").mkdir(parents=True,exist_ok=True);(self.root/"shell/00_idea/idea.md").write_text("## I-001\n- title: 想法\n- hypothesis: H\n")
  (self.root/"shell/01_questions").mkdir(parents=True,exist_ok=True);server.create_question(self.root,{"title":"疑问","question":"为什么"})
  server.save_compares(self.root,[{"id":"cmp-one","name":"对比","mode":"structured","papers":[],"axes":[],"findings":[]}])
 def payload(self):return{"summary":"发现摘要","evidence":[{"source":"local","ref":"file.py:1","finding":"事实","verification_status":"partial"}],"contradictions":["可能混杂"],"uncertainties":["待确认"],"next_focus":"反证"}
 def test_targets_init_round_and_secrets(self):
  for typ,oid in (("experiment","E-001"),("idea","I-001"),("question","Q-001"),("comparison","cmp-one")):self.assertEqual(server.exploration_inspect_target(self.root,typ,oid)["target_id"],oid)
  with self.assertRaises(ValueError):server.exploration_inspect_target(self.root,"idea","I-999")
  b={"duration_minutes":30,"max_rounds":2,"hard_max_rounds":2,"interval_minutes":1,"round_wall_budget_minutes":10};a=server.exploration_init(self.root,"idea","I-001","idea-i-001-test",b);self.assertEqual(server.exploration_init(self.root,"idea","I-001","idea-i-001-test",b)["id"],a["id"])
  server.exploration_transition(self.root,a["id"],"round_running","start","active");r=server.exploration_record_round(self.root,a["id"],1,self.payload());self.assertFalse(r["idempotent"]);self.assertTrue(server.exploration_record_round(self.root,a["id"],1,self.payload())["idempotent"])
  bad=self.payload();bad["prompt"]="secret"
  with self.assertRaises(ValueError):server.exploration_record_round(self.root,a["id"],2,bad)
 def test_transition_budget_record_gate_and_markdown_escape(self):
  eid="idea-state-test";row=server.exploration_init(self.root,"idea","I-001",eid,{"duration_minutes":5,"max_rounds":2,"hard_max_rounds":2})
  with self.assertRaises(ValueError):server.exploration_record_round(self.root,eid,1,self.payload())
  with self.assertRaises(ValueError):server.exploration_transition(self.root,eid,"finalizing","bad","active")
  with self.assertRaises(ValueError):server.exploration_transition(self.root,eid,"paused","cas","round_running")
  server.exploration_transition(self.root,eid,"round_running","start","active");payload=self.payload();payload["evidence"][0]["source"]="a|b\nnext";server.exploration_record_round(self.root,eid,1,payload)
  text=(self.root/f"shell/07_explorations/{eid}/rounds/round-1.md").read_text();self.assertIn(r"a\|b<br>next",text)
  ctx=server.exploration_context(self.root,eid);self.assertNotIn("project_root",ctx["session"]);self.assertNotIn("round_hashes",ctx["session"])
  with self.assertRaises(ValueError):server.exploration_init(self.root,"idea","I-001",eid,{"max_rounds":3})
  with self.assertRaises(ValueError):server.exploration_init(self.root,"idea","I-001","bad-budget-id",{"max_rounds":3,"hard_max_rounds":2})
  with self.assertRaises(ValueError):server.exploration_init(self.root,"idea","I-001","bad-deadline-id",{"duration_minutes":5,"deadline":"2099-01-01T00:00:00+00:00"})
  nested=self.payload();nested["evidence"][0]["finding"]="password=oops"
  with self.assertRaises(ValueError):server._validate_exploration_payload(nested)
 def test_four_links_and_experiment_partial_drafts(self):
  for typ,oid in (("idea","I-001"),("question","Q-001"),("comparison","cmp-one")):
   eid=f"{typ}-link-test";server.exploration_init(self.root,typ,oid,eid,{"max_rounds":1});server.exploration_transition(self.root,eid,"stopped","test","active");server.exploration_transition(self.root,eid,"finalizing","test","stopped");out=server.exploration_finalize(self.root,eid,"# Final\n\n不是 validated synthesis。",{});self.assertEqual(out["session"]["status"],"completed");self.assertTrue(list((self.root/{"idea":"shell/00_idea/explorations","question":"shell/01_questions/explorations","comparison":"shell/04_comparisons/explorations"}[typ]/oid).glob("*.md")))
  server.update_experiment(self.root,"E-001",{"run_groups":[{"id":"keep","name":"保留","description":"已有","color":"#123456"},{"id":"exploration-candidates","name":"错误名","description":"错误说明","color":"#000000"}]});server.create_run(self.root,"E-001",{"variant":"锁定","group_id":"exploration-candidates"},"R-locked");server.review_run(self.root,"R-locked","submit",actor="terminal_pi");server.review_run(self.root,"R-locked","approve",actor="human")
  server.save_review_automation_policy(self.root,"E-001",{"enabled":True,"auto_review_on_create":True,"policy_version":server.REVIEW_AUTOMATION_POLICY_VERSION,"notes":"test"})
  eid="experiment-e-001-test";server.exploration_init(self.root,"experiment","E-001",eid,{"max_rounds":1});server.exploration_transition(self.root,eid,"stopped","test","active");server.exploration_transition(self.root,eid,"finalizing","test","stopped");base={"id":"R-explore","variant":"候选","research_question":"什么条件下有效","purpose":"比较候选处理与基线","hypothesis":"候选处理提高准确率","metric_plan":"复用 accuracy 衡量正确比例","data_definition":"固定数据","variables_controls":"只改变候选处理"};out=server.exploration_finalize(self.root,eid,"# Final",{"runs":[base,{"id":"bad"}]});self.assertEqual(len(out["applied"]),1);self.assertEqual(len(out["skipped"]),1);self.assertEqual(out["session"]["status"],"completed_with_warnings")
  data=server.experiment_data(self.root);exp=next(x for x in data["experiments"] if x["id"]=="E-001");self.assertTrue(any(g["id"]=="keep" for g in exp["run_groups"]));fixed=next(g for g in exp["run_groups"] if g["id"]=="exploration-candidates");self.assertEqual(fixed,server.EXPLORATION_GROUP);run=next(x for x in data["runs"] if x["id"]=="R-explore");self.assertEqual((run["group_id"],run["status"],run["review_status"],run["created_by"],run["metric_observations"]),("exploration-candidates","draft","draft","research_explorer",[]));self.assertFalse(run.get("automation_review_snapshot"));self.assertFalse(run.get("execution_authorized_at"));self.assertFalse((self.root/".survey-tool/execution-outbox.json").exists());self.assertTrue(server.exploration_finalize(self.root,eid,"# Final",{"runs":[base,{"id":"bad"}]})["idempotent"])
  with self.assertRaises(ValueError):server.exploration_finalize(self.root,eid,"different",{"runs":[]})
  with self.assertRaises(ValueError):server.exploration_transition(self.root,eid,"active","revive","completed_with_warnings")
if __name__=="__main__":unittest.main()
