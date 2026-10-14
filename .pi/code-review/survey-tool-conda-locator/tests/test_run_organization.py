import datetime,pathlib,tempfile,threading,unittest
import server
class OrganizationTest(unittest.TestCase):
 def setUp(self):
  self.root=pathlib.Path(tempfile.mkdtemp(prefix="org-"));(self.root/"state.md").write_text("state: T\n");server.CFG={"projects_root":str(self.root.parent),"projects":[str(self.root)],"skill_dir":"","port":1};server.write_tool_json(self.root,"servers.json",[]);server.write_tool_json(self.root,"workspaces.json",[{"id":"W","server_id":"","remote_repo":"/repo","remote_experiment_root":"/exp"}])
 def exp(self,groups):server.create_experiment(self.root,{"title":"x","objective":"x","workspace_id":"W","run_groups":groups},"E-001")
 def test_single_unique_and_ambiguous_task(self):
  self.exp([{"id":"analysis","name":"分析","description":"analysis jobs","color":"#111111"}]);run=server.create_run(self.root,"E-001",{"variant":"a"},"R-a");self.assertEqual(next(x for x in server.experiment_data(self.root)["runs"] if x["id"]=="R-a")["group_id"],"analysis")
  server.update_experiment(self.root,"E-001",{"run_groups":[{"id":"analysis","name":"分析","description":"analysis jobs","color":"#111111"},{"id":"a","name":"A","description":"x","color":"#333333"},{"id":"b","name":"B","description":"y","color":"#222222"}]});run=server.create_run(self.root,"E-001",{"variant":"b"},"R-b");self.assertTrue(run["organization_result"]["microtask"]);tid=run["organization_result"]["microtask"]["task_id"];self.assertEqual(tid,server._organize_created_run(self.root,"R-b")["microtask"]["task_id"])
  claim=server.claim_governance_task(self.root,"pi");done=server.complete_governance_task(self.root,tid,claim["lease_token"],"pi","a","fits");self.assertEqual(done["status"],"completed")
 def test_token_match_locked_and_unsupported_route(self):
  self.exp([{"id":"train","name":"训练","description":"training","color":"#111111"},{"id":"eval","name":"评测","description":"evaluation","color":"#222222"}])
  server.create_run(self.root,"E-001",{"variant":"a","run_type":"evaluation"},"R-token")
  self.assertEqual(next(x for x in server.experiment_data(self.root)["runs"] if x["id"]=="R-token")["group_id"],"eval")
  ambiguous=server.create_run(self.root,"E-001",{"variant":"b"},"R-lock"); task=ambiguous["organization_result"]["microtask"]
  server.review_run(self.root,"R-lock","submit",actor="terminal_pi")
  claim=server.claim_governance_task(self.root,"pi"); done=server.complete_governance_task(self.root,task["task_id"],claim["lease_token"],"pi","train","late")
  self.assertEqual(done["status"],"cancelled")
  again=server.create_run(self.root,"E-001",{"variant":"c"},"R-health"); route=server.agent_routing_policy(self.root)["routes"]["lightweight_governance"]
  server.record_agent_route_event(self.root,{"route":"lightweight_governance","subject":"requested","requested_agent":route["agent_kind"],"requested_model":route.get("model","") ,"result":"unsupported","message":"400 not supported"})
  blocked=server.claim_governance_task(self.root,"pi2"); self.assertFalse(blocked["claimed"]); self.assertTrue(blocked["blocked"]); self.assertTrue(again["organization_result"]["microtask"])
 def test_snapshot_refresh_lease_expiry_empty_and_cas(self):
  self.exp([{"id":"a","name":"A","description":"one","color":"#111111"},{"id":"b","name":"B","description":"two","color":"#222222"}]); created=server.create_run(self.root,"E-001",{"variant":"ambiguous"},"R-task"); tid=created["organization_result"]["microtask"]["task_id"]
  refreshed=next(x for x in server.experiment_dashboard_data(self.root)["runs"] if x["id"]=="R-task"); self.assertEqual(refreshed["organization_result"]["microtask"]["task_id"],tid)
  claim=server.claim_governance_task(self.root,"one"); self.assertEqual(claim["task"]["status"],"claimed"); self.assertLessEqual(len(claim["prompt"]),4096)
  tasks=server._governance_tasks(self.root); item=next(x for x in tasks["items"] if x["task_id"]==tid); item["lease_expires_at"]=(datetime.datetime.now()-datetime.timedelta(seconds=1)).isoformat(); server.write_tool_json(self.root,"governance-tasks.json",tasks)
  again=server.claim_governance_task(self.root,"two"); self.assertTrue(again["claimed"]); self.assertEqual(again["task"]["status"],"claimed")
  with self.assertRaisesRegex(ValueError,"过期|无效"): server.complete_governance_task(self.root,tid,claim["lease_token"],"one","a","stale")
  done=server.complete_governance_task(self.root,tid,again["lease_token"],"two","","保持未分组"); self.assertEqual(done["status"],"completed"); self.assertNotIn("consumer",done); self.assertEqual(done["result"]["group_id"],"")
 def test_invalid_group_and_organization_error_persist(self):
  self.exp([{"id":"a","name":"A","description":"one","color":"#111111"},{"id":"b","name":"B","description":"two","color":"#222222"}]); created=server.create_run(self.root,"E-001",{"variant":"ambiguous"},"R-invalid"); claim=server.claim_governance_task(self.root,"pi")
  with self.assertRaisesRegex(ValueError,"不在 task"): server.complete_governance_task(self.root,created["organization_result"]["microtask"]["task_id"],claim["lease_token"],"pi","unknown","bad")
  original=server.agent_routing_policy; server.agent_routing_policy=lambda root: (_ for _ in ()).throw(RuntimeError("route broken"))
  try: failed=server.create_run(self.root,"E-001",{"variant":"error"},"R-error")
  finally: server.agent_routing_policy=original
  persisted=next(x for x in server.experiment_data(self.root)["runs"] if x["id"]=="R-error"); self.assertEqual(persisted["organization_snapshot"]["action"],"error"); self.assertEqual(failed["organization_result"]["snapshot"]["action"],"error")
 def test_complete_final_cas_rejects_intervening_state_change(self):
  self.exp([{"id":"a","name":"A","description":"one","color":"#111111"},{"id":"b","name":"B","description":"two","color":"#222222"}]); created=server.create_run(self.root,"E-001",{"variant":"ambiguous"},"R-cas"); tid=created["organization_result"]["microtask"]["task_id"]; claim=server.claim_governance_task(self.root,"pi")
  original=server.apply_agent_run_grouping
  def racing(*args,**kwargs):
   result=original(*args,**kwargs); tasks=server._governance_tasks(self.root); next(x for x in tasks["items"] if x["task_id"]==tid)["status"]="failed"; server.write_tool_json(self.root,"governance-tasks.json",tasks); return result
  server.apply_agent_run_grouping=racing
  try:
   with self.assertRaisesRegex(ValueError,"已变化"): server.complete_governance_task(self.root,tid,claim["lease_token"],"pi","a","race")
  finally: server.apply_agent_run_grouping=original
 def test_governance_claim_is_unique_under_concurrency(self):
  self.exp([{"id":"a","name":"A","description":"one","color":"#111111"},{"id":"b","name":"B","description":"two","color":"#222222"}]); server.create_run(self.root,"E-001",{"variant":"ambiguous"},"R-concurrent")
  barrier=threading.Barrier(3); results=[]
  def claim(name): barrier.wait(); results.append(server.claim_governance_task(self.root,name))
  threads=[threading.Thread(target=claim,args=(f"pi-{i}",)) for i in range(2)]
  for thread in threads: thread.start()
  barrier.wait()
  for thread in threads: thread.join()
  self.assertEqual(sum(bool(x.get("claimed")) for x in results),1)
