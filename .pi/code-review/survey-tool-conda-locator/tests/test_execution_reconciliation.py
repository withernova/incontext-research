import ast,pathlib,tempfile,unittest
import server

class ReconciliationTest(unittest.TestCase):
 def setUp(self):
  self.root=pathlib.Path(tempfile.mkdtemp(prefix="reconcile-"));(self.root/"state.md").write_text("state: TEST\n");server.CFG={"projects_root":str(self.root.parent),"projects":[str(self.root)],"skill_dir":"","port":7421};server.write_tool_json(self.root,"servers.json",[{"id":"S","ssh_host":"host"}]);server.write_tool_json(self.root,"workspaces.json",[{"id":"W","server_id":"S","remote_repo":"/repo","remote_experiment_root":"/exp"}]);server.create_experiment(self.root,{"title":"x","objective":"x","workspace_id":"W"},"E-001")
 def auth(self,rid):
  server.create_run(self.root,"E-001",{"variant":rid,"workspace_id":"W","command":"python x.py"},rid);server.review_run(self.root,rid,"submit",actor="terminal_pi");server.review_run(self.root,rid,"approve",actor="human");return server.review_run(self.root,rid,"authorize_execution",actor="human")
 def test_authorize_always_dispatch_activate_never_consumes_and_claim_reconciles(self):
  run=self.auth("R-one");self.assertTrue(run["execution_dispatch_enqueue_result"]["dispatch"]);activated=server.activate_run(self.root,"R-one");self.assertFalse(activated["legacy_activation"]);self.assertFalse(next(x for x in server.experiment_data(self.root)["runs"] if x["id"]=="R-one").get("execution_authorization_consumed_at"))
  server.write_tool_json(self.root,"execution-outbox.json",{"schema":server.OUTBOX_SCHEMA,"version":1,"items":[]});claimed=server.claim_next_execution(self.root,"worker");self.assertTrue(claimed["claimed"])
 def test_anomalies_and_idempotency(self):
  self.auth("R-old");data=server.experiment_data(self.root);run=next(x for x in data["runs"] if x["id"]=="R-old");run["execution_authorization_consumed_at"]="old";run.pop("execution_dispatch_id",None);server.write_tool_json(self.root,"runs.json",data["runs"]);plan=server.reconcile_execution_outbox(self.root,dry_run=True);self.assertEqual(plan["anomalies"][0]["type"],"legacy_consumed_untracked");self.assertEqual(server.reconcile_execution_outbox(self.root,dry_run=True)["totals"],plan["totals"])
  run["execution_dispatch_id"]="missing";server.write_tool_json(self.root,"runs.json",data["runs"]);self.assertEqual(server.reconcile_execution_outbox(self.root,dry_run=True)["anomalies"][0]["type"],"consumed_dispatch_missing")
 def test_unique_consumption_assignment(self):
  tree=ast.parse(pathlib.Path(server.__file__).read_text());owners=[]
  for node in ast.walk(tree):
   if isinstance(node,(ast.Assign,ast.AugAssign)):
    targets=node.targets if isinstance(node,ast.Assign) else [node.target]
    if any(isinstance(t,ast.Subscript) and isinstance(t.slice,ast.Constant) and t.slice.value=="execution_authorization_consumed_at" for t in targets):owners.append(node.lineno)
  self.assertEqual(len(owners),1)
 def test_legacy_activate_keeps_compatibility(self):
  server.create_run(self.root,"E-001",{"variant":"legacy","workspace_id":"W","command":"python x.py","status":"prepared"},"R-legacy")
  data=server.experiment_data(self.root); run=next(x for x in data["runs"] if x["id"]=="R-legacy"); run.pop("review_status",None); server.write_tool_json(self.root,"runs.json",data["runs"])
  result=server.activate_run(self.root,"R-legacy"); self.assertTrue(result["legacy_activation"]); self.assertEqual(server.read_tool_json(self.root,"active-run.json",{})["run_id"],"R-legacy")
 def test_internal_enqueue_failure_still_creates_blocked_dispatch(self):
  server.create_run(self.root,"E-001",{"variant":"broken","workspace_id":"W","command":"python x.py"},"R-broken"); server.review_run(self.root,"R-broken","submit",actor="terminal_pi"); server.review_run(self.root,"R-broken","approve",actor="human")
  original=server.agent_routing_policy; server.agent_routing_policy=lambda root: (_ for _ in ()).throw(RuntimeError("routing unavailable"))
  try: run=server.review_run(self.root,"R-broken","authorize_execution",actor="human")
  finally: server.agent_routing_policy=original
  dispatch=run["execution_dispatch_enqueue_result"]["dispatch"]; self.assertEqual(dispatch["status"],"blocked"); self.assertIn("internal enqueue failure",dispatch["last_error"]); self.assertEqual(len(server._outbox_read(self.root)["items"]),1)
  self.assertTrue(server.ensure_authorization_dispatch(self.root,"R-broken")["idempotent"])
 def test_reconcile_post_plan_and_newest_authorization_claimed_first(self):
  self.auth("R-old"); self.auth("R-new"); data=server.experiment_data(self.root); box=server._outbox_read(self.root)
  for rid,stamp in (("R-old","2026-01-01T00:00:00"),("R-new","2026-01-02T00:00:00")):
   next(x for x in data["runs"] if x["id"]==rid)["execution_authorized_at"]=stamp; next(x for x in box["items"] if x["run_id"]==rid)["authorization_timestamp"]=stamp
  server.write_tool_json(self.root,"runs.json",data["runs"]); server.write_tool_json(self.root,"execution-outbox.json",box)
  claimed=server.claim_next_execution(self.root,"worker"); self.assertEqual(claimed["task"]["dispatch"]["run_id"],"R-new")
  server.write_tool_json(self.root,"execution-outbox.json",{"schema":server.OUTBOX_SCHEMA,"version":1,"items":[]}); result=server.reconcile_execution_outbox(self.root); self.assertEqual(result["post_plan"]["totals"]["actions"],0)
