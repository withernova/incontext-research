import datetime
import hashlib
import os
import shlex
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import server
from survey_tool.experiments import managed_execution_heartbeat, managed_execution_readiness, update_workspace_binding, validate_dataset_bindings, validate_workspace_policy
from survey_tool.managed_execution import KNOWN_HOSTS_ENV, LAUNCH_STATE, MARKER, SSH_CONFIG_ENV, _managed_execution_preflight, _metric_rows, _ssh, activation_contract, build_launcher, managed_execution_complete, managed_execution_start, managed_execution_status


class ManagedExecutionTest(unittest.TestCase):
    def test_metrics_split_declared_and_auxiliary_without_discarding_results(self):
        declared,auxiliary=_metric_rows({"metrics":{"accuracy":0.91,"records":140,"latency_ms":12.5}},{"accuracy"},"/runs/metrics.json")
        self.assertEqual([row["metric_id"] for row in declared],["accuracy"])
        self.assertEqual([row["metric_id"] for row in auxiliary],["records","latency_ms"])
        with self.assertRaisesRegex(ValueError,"invalid IDs"):
            _metric_rows({"bad metric":1},set(),"/runs/metrics.json")

    def test_complete_moves_to_analysis_with_undeclared_metrics_as_auxiliary(self):
        run={"id":"R-1","experiment_id":"E-1","workflow_stage":"running"}; resolved={"ssh_host":"gpu","metrics_file":"/runs/metrics.json","log_file":"/runs/train.log"}
        item={"dispatch_id":"D-1","managed_execution":{"stable_observation":{"size":80,"mtime":2}}}
        data={"experiments":[{"id":"E-1","metric_definitions":[{"id":"accuracy"}]}]}
        status={"completion_candidate":True,"exit_code":"0","files":{"metrics_file":{"exists":True,"size":80,"mtime":2}}}
        runner=lambda *_args,**_kwargs:{"returncode":0,"stdout":'{"metrics":{"accuracy":0.91,"records":140}}',"stderr":""}
        transitioned={"status":"completed"}; updated={"id":"R-1","workflow_stage":"analysis_pending"}
        with mock.patch("survey_tool.managed_execution.managed_execution_status",return_value=status),mock.patch("survey_tool.managed_execution._lease_context",return_value=(data,item,run,resolved,{}, {},"",{})),mock.patch("survey_tool.managed_execution.prevalidate_managed_result_draft") as validate,mock.patch("survey_tool.managed_execution._leased_transition",return_value=transitioned),mock.patch("survey_tool.managed_execution.apply_managed_result_draft",return_value=updated) as apply:
            result=managed_execution_complete(Path("/project"),"D-1","secret","pi",runner)
        draft=apply.call_args.args[2]; self.assertEqual(draft["metric_observations"][0]["metric_id"],"accuracy"); self.assertEqual(draft["auxiliary_metric_observations"][0]["metric_id"],"records")
        self.assertEqual(result["run"]["workflow_stage"],"analysis_pending"); self.assertTrue(result["warnings"]); validate.assert_called_once()

    def test_readiness_refuses_missing_isolation(self):
        result=managed_execution_readiness({"id":"W-01","server_id":"M-01"},[{"id":"M-01","ssh_host":"gpu"}])
        self.assertFalse(result["ready"]); self.assertIn("isolation",result["reason"])

    def test_activation_contract_requires_conda_and_proves_prefix(self):
        contract=activation_contract("使用 IPLoc conda 环境")
        self.assertEqual(contract["name"],"IPLoc")
        self.assertIn("conda activate IPLoc",contract["script"])
        self.assertIn("SURVEY_TOOL_ENV_PROOF",contract["script"])
        with self.assertRaisesRegex(ValueError,"environment_activation"):
            activation_contract("")
        with self.assertRaisesRegex(ValueError,"environment_activation"):
            activation_contract("source /tmp/other/bin/activate")

    def test_szy_iploc_activation_pins_existing_installation_without_fallback(self):
        contract=activation_contract("conda:IPLoc",ssh_host="SZY-3090")
        script=contract["script"]
        self.assertEqual(contract["verified_installation"],"/songzhengyue/miniconda3")
        self.assertEqual(contract["expected_prefix"],"/songzhengyue/miniconda3/envs/IPLoc")
        self.assertIn("export CONDA_EXE=/songzhengyue/miniconda3/bin/conda",script)
        self.assertIn(". /songzhengyue/miniconda3/etc/profile.d/conda.sh",script)
        self.assertIn("verified_conda_installation_unavailable",script)
        self.assertIn("exit 88",script)
        self.assertIn("python is not in the verified environment installation",script)
        self.assertLess(script.index("verified_conda_installation_unavailable"),
                        script.index("$HOME/miniconda3"))
        self.assertLess(script.index(". /songzhengyue/miniconda3/etc/profile.d/conda.sh"),
                        script.index("conda activate IPLoc"))
        self.assertIn("python is outside CONDA_PREFIX",script)

    def test_conda_locator_is_scoped_to_verified_host_and_environment(self):
        for host,name in (("gpu","IPLoc"),("SZY-3090","other"),("","IPLoc")):
            with self.subTest(host=host,name=name):
                contract=activation_contract("conda:"+name,ssh_host=host)
                self.assertIsNone(contract["verified_installation"])
                self.assertEqual(contract["expected_prefix"],"")
                self.assertNotIn("/songzhengyue/miniconda3",contract["script"])
                self.assertIn("$HOME/miniconda3",contract["script"])
        with self.assertRaisesRegex(ValueError,"environment_activation"):
            activation_contract("conda:IPLoc; echo injected",ssh_host="SZY-3090")

    def test_guarded_launcher_reuses_the_pinned_activation_contract(self):
        activation=activation_contract("conda:IPLoc",ssh_host="SZY-3090")["script"]
        preflight={"resolved":{"project_dir":"/srv/repo","run_dir":"/srv/runs/R-1","output_dir":"/srv/runs/R-1/out","log_file":"/srv/runs/R-1/run.log"},"write_roots":["/srv/runs","/srv/repo"],"read_only_roots":["/srv/data"],"forbidden_roots":[],"dataset_bindings":[],"isolation":{"mode":"tmux-guarded","network":"host","deny_read_roots":[]},"activation":activation,"command":"python3 run.py"}
        script=build_launcher(preflight)
        self.assertIn("export CONDA_EXE=/songzhengyue/miniconda3/bin/conda",script)
        self.assertIn("verified_conda_installation_unavailable",script)
        self.assertLess(script.index("conda activate IPLoc"),script.index("2>&1 | tee"))

    def test_launcher_is_bounded_bubblewrap_template(self):
        preflight={"resolved":{"project_dir":"/srv/repo","run_dir":"/srv/runs/R-1","output_dir":"/srv/runs/R-1/out","log_file":"/srv/runs/R-1/run.log"},"write_roots":["/srv/runs","/srv/repo"],"read_only_roots":["/srv/data"],"forbidden_roots":["/srv/repo/.git"],"dataset_bindings":[{"id":"d","mode":"bind_ro","source_path":"/srv/data/set","target_path":"/srv/repo/data/set","target_state":"absent"}],"isolation":{"network":"none","deny_read_roots":["/home/runner/.ssh"]},"activation":activation_contract("conda:IPLoc"),"command":"python3 train.py --config approved.json"}
        script=build_launcher(preflight)
        for text in ("--ro-bind / /","--bind /srv/repo /srv/repo","--ro-bind /srv/data /srv/data","--tmpfs /tmp","--unshare-net",MARKER,"python3 train.py --config approved.json"):
            self.assertIn(text,script)
        self.assertNotIn("lease",script.lower())
        self.assertLess(script.index("--bind /srv/repo /srv/repo"),script.index("--ro-bind /srv/repo/.git /srv/repo/.git"))
        self.assertLess(script.index("--dir /srv/repo/data/set"),script.index("--ro-bind /srv/data/set /srv/repo/data/set"))
        self.assertLess(script.index("--tmpfs /home/runner/.ssh"),script.index("--ro-bind /srv/data/set /srv/repo/data/set"))

    def test_launcher_hides_denied_parent_then_remounts_allowed_child(self):
        preflight={"resolved":{"project_dir":"/archive/user/project","run_dir":"/archive/user/project/runs/R-1","output_dir":"/archive/user/project/runs/R-1/out","log_file":"/archive/user/project/runs/R-1/run.log"},"write_roots":["/archive/user/project"],"read_only_roots":["/archive/user/data"],"forbidden_roots":[],"dataset_bindings":[],"isolation":{"network":"none","deny_read_roots":["/archive"]},"activation":activation_contract("conda:IPLoc"),"command":"python3 run.py"}
        script=build_launcher(preflight)
        self.assertLess(script.index("--tmpfs /archive"),script.index("--bind /archive/user/project /archive/user/project"))
        self.assertIn("--dir /archive/user",script)

    def test_tmux_guarded_launcher_is_explicitly_degraded(self):
        preflight={"resolved":{"project_dir":"/srv/repo","run_dir":"/srv/runs/R-1","output_dir":"/srv/runs/R-1/out","log_file":"/srv/runs/R-1/run.log"},"write_roots":["/srv/runs","/srv/repo"],"read_only_roots":["/srv/data"],"forbidden_roots":[],"dataset_bindings":[],"isolation":{"mode":"tmux-guarded","network":"host","deny_read_roots":[]},"activation":activation_contract("conda:IPLoc")["script"],"command":"python3 run.py"}
        script=build_launcher(preflight)
        self.assertIn("tmux-guarded",script)
        self.assertNotIn("bwrap",script)
        self.assertIn("python3 run.py",script)
        self.assertIn(LAUNCH_STATE,script)
        self.assertLess(script.index("SURVEY_TOOL_LAUNCH_BOOTSTRAP"),script.index("conda activate IPLoc"))
        self.assertLess(script.index("conda activate IPLoc"),script.index("2>&1 | tee"))
        self.assertLess(script.index("cd -- /srv/repo"),script.index("python3 run.py"))
        self.assertGreater(script.index(".survey-tool-exit-code"),script.index("2>&1 | tee"))

    def test_ssh_serializes_one_quoted_remote_command(self):
        seen=[]
        def runner(argv,**_kwargs): seen.append(argv); return {"returncode":0,"stdout":"","stderr":""}
        args=["realpath","-m","--","/srv/a path; touch /tmp/pwned"]
        _ssh(runner,"host",args)
        self.assertEqual(len(seen[0]),8); self.assertEqual(shlex.split(seen[0][-1]),args)

    def test_ssh_uses_this_machines_config_instead_of_a_hardcoded_path(self):
        seen=[]
        def runner(argv,**_kwargs): seen.append(argv); return {"returncode":0,"stdout":"","stderr":""}
        with tempfile.TemporaryDirectory() as td:
            home=Path(td)/"home"; (home/".ssh").mkdir(parents=True); (home/".ssh"/"config").write_text("Host SZY-3090\n",encoding="utf-8")
            with mock.patch.dict(os.environ,{"HOME":str(home),SSH_CONFIG_ENV:"",KNOWN_HOSTS_ENV:""}):
                _ssh(runner,"SZY-3090",["true"])
        argv=seen[0]
        self.assertNotIn("/mnt/c"," ".join(argv))
        self.assertEqual(argv[argv.index("-F")+1],str(home/".ssh"/"config"))
        self.assertIn("StrictHostKeyChecking=yes",argv)
        self.assertEqual(argv[-3:],["SZY-3090","--","true"])

    def test_ssh_honors_per_machine_config_override_and_fails_loudly_when_absent(self):
        seen=[]
        def runner(argv,**_kwargs): seen.append(argv); return {"returncode":0,"stdout":"","stderr":""}
        with tempfile.TemporaryDirectory() as td:
            home=Path(td)/"home"; (home/".ssh").mkdir(parents=True)
            explicit=str(Path(td)/"operator-ssh-config"); known=str(Path(td)/"known_hosts")
            with mock.patch.dict(os.environ,{"HOME":str(home),SSH_CONFIG_ENV:explicit,KNOWN_HOSTS_ENV:known}):
                _ssh(runner,"SZY-3090",["true"])
                argv_override=seen[0]
                os.environ[SSH_CONFIG_ENV]=""; os.environ[KNOWN_HOSTS_ENV]=""
                _ssh(runner,"SZY-3090",["true"])
                argv_no_default=seen[1]
        # 显式配置即使文件不存在也要传，避免静默改用别的 host 配置
        self.assertEqual(argv_override[argv_override.index("-F")+1],explicit)
        self.assertIn(f"UserKnownHostsFile={known}",argv_override)
        # 本机没有 ~/.ssh/config 时不传 -F，让 ssh 退回自身默认行为
        self.assertNotIn("-F",argv_no_default)
        self.assertFalse(any(item.startswith("UserKnownHostsFile=") for item in argv_no_default))

    def test_heartbeat_rejects_stale_lease_and_public_state_has_no_token(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); token="raw-secret"; expired=(datetime.datetime.now()-datetime.timedelta(seconds=1)).isoformat(timespec="seconds")
            server.write_tool_json(root,"execution-outbox.json",{"schema":"survey-tool.execution-outbox/v1","version":1,"items":[{"dispatch_id":"D-1","status":"running","consumer":"pi","lease_token_hash":hashlib.sha256(token.encode()).hexdigest(),"lease_expires_at":expired}]})
            with self.assertRaisesRegex(ValueError,"过期"):
                managed_execution_heartbeat(root,"D-1",token,"pi")
            public=server.execution_outbox_public(root)["execution_outbox"]["items"][0]
            self.assertFalse(any("token" in key.lower() for key in public))

    def test_remote_launch_precedes_running_and_transition_failure_compensates(self):
        preflight={"dispatch_id":"D-1","run_id":"R-1","resolved":{"project_dir":"/srv/repo","run_dir":"/srv/runs/R-1","output_dir":"/srv/runs/R-1/out","log_file":"/srv/runs/R-1/run.log"},"write_roots":["/srv/runs","/srv/repo"],"read_only_roots":["/srv/data"],"isolation":{"network":"none","deny_read_roots":[]},"ssh_host":"gpu","tmux_session":"managed-r1","activation":"","command":"python3 train.py","_run":{"id":"R-1","workflow_stage":"ready_to_run"}}
        calls=[]
        def runner(argv,**_kwargs):
            calls.append(argv); remote=shlex.split(argv[-1])
            if remote[:2]==["python3","-c"] and "time.monotonic" in remote[2]: return {"returncode":0,"stdout":LAUNCH_STATE+"\n","stderr":""}
            return {"returncode":0,"stdout":"","stderr":""}
        def transition(*_args,**_kwargs):
            self.assertTrue(any("new-session" in " ".join(call) for call in calls)); raise RuntimeError("CAS changed")
        with mock.patch("survey_tool.managed_execution._managed_execution_preflight",return_value=preflight),mock.patch("survey_tool.managed_execution._leased_transition",side_effect=transition),mock.patch("survey_tool.managed_execution.update_managed_execution_metadata"):
            with self.assertRaisesRegex(RuntimeError,"CAS"):
                managed_execution_start(Path("/unused"),"D-1","secret","pi",runner)
        self.assertTrue(any("kill-session" in " ".join(call) for call in calls))

    def test_missing_launcher_bootstrap_never_transitions_running(self):
        preflight={"dispatch_id":"D-1","run_id":"R-1","resolved":{"project_dir":"/srv/repo","run_dir":"/srv/runs/R-1","output_dir":"/srv/runs/R-1/out","log_file":"/srv/runs/R-1/run.log","metrics_file":"/srv/runs/R-1/metrics.json"},"write_roots":["/srv/runs","/srv/repo"],"read_only_roots":["/srv/data"],"isolation":{"network":"none","deny_read_roots":[]},"ssh_host":"gpu","tmux_session":"managed-r1","activation":"","command":"python3 train.py","_run":{"id":"R-1","workflow_stage":"ready_to_run"}}
        calls=[]
        def runner(argv,**_kwargs):
            calls.append(argv); remote=shlex.split(argv[-1])
            if remote[:2]==["python3","-c"] and "time.monotonic" in remote[2]: return {"returncode":3,"stdout":"","stderr":""}
            return {"returncode":0,"stdout":"","stderr":""}
        with mock.patch("survey_tool.managed_execution._managed_execution_preflight",return_value=preflight),mock.patch("survey_tool.managed_execution._leased_transition") as transition,mock.patch("survey_tool.managed_execution.update_managed_execution_metadata") as update:
            with self.assertRaisesRegex(ValueError,"bootstrap evidence"):
                managed_execution_start(Path("/unused"),"D-1","secret","pi",runner)
        transition.assert_not_called()
        self.assertEqual(update.call_args.args[2]["started_evidence"],"launcher_bootstrap_missing")
        self.assertTrue(any("kill-session" in " ".join(call) for call in calls))

    def test_status_uses_preflight_host_not_path_projection(self):
        preflight={"run_id":"R-1","ssh_host":"gpu","tmux_session":"managed-r1","resolved":{"log_file":"/runs/log","metrics_file":"/runs/metrics.json","output_dir":"/runs/out","run_dir":"/runs"},"_run":{"id":"R-1"}}
        calls=[]
        def runner(argv,**_kwargs):
            calls.append(argv); remote=shlex.split(argv[-1])
            if remote[0]=="python3": return {"returncode":0,"stdout":'{"log_file":{"exists":true,"size":1,"mtime":1},"metrics_file":{},"output_dir":{},"run_dir":{},"exit_code":null,"marker":"","launch_state":"SURVEY_TOOL_LAUNCHER_STARTED"}',"stderr":""}
            return {"returncode":0,"stdout":"","stderr":""}
        with mock.patch("survey_tool.managed_execution._managed_execution_preflight",return_value=preflight),mock.patch("survey_tool.managed_execution._outbox_read",return_value={"items":[{"dispatch_id":"D-1","status":"running"}]}),mock.patch("survey_tool.managed_execution.update_managed_execution_metadata") as update:
            result=managed_execution_status(Path("/unused"),"D-1","token","pi",runner)
        self.assertTrue(result["tmux_alive"]); self.assertTrue(result["observed_at"]); self.assertTrue(all(call[5]=="gpu" for call in calls))
        self.assertEqual(result["launch_state"],LAUNCH_STATE)
        self.assertTrue(update.call_args.args[2]["status_observation"]["observed_at"])

    def test_structured_dataset_policy_and_partial_workspace_patch(self):
        ws={"id":"W-01","label":"kept","server_id":"M-01","environment_policy":{"allowed_write_roots":["/srv/project"],"read_only_roots":["/datasets"],"forbidden_paths":["/srv/project/.git"],"forbidden_operations":["sudo"],"default_deny_write":True}}
        valid={"id":"data-1","label":"Dataset","source_path":"/datasets/source","target_path":"/srv/project/data/source","mode":"bind_ro","required":True,"notes":"read only"}
        self.assertEqual(validate_dataset_bindings(ws,[valid])[0]["id"],"data-1")
        for changed,pattern in [({**valid,"source_path":"/outside"},"read_only"),({**valid,"target_path":"/other"},"allowed_write"),({**valid,"target_path":"/srv/project/.git/data"},"forbidden")]:
            with self.assertRaisesRegex(ValueError,pattern): validate_dataset_bindings(ws,[changed])
        with self.assertRaisesRegex(ValueError,"重复"): validate_dataset_bindings(ws,[valid,{**valid,"id":"data-2"}])
        nested=validate_workspace_policy(ws,{"allowed_write_roots":["/srv/project"],"read_only_roots":["/datasets"],"forbidden_paths":["/srv"],"forbidden_operations":[],"default_deny_write":True})
        self.assertEqual(nested["allowed_write_roots"],["/srv/project"])
        self.assertIn("/srv",nested["forbidden_paths"])
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); server.write_tool_json(root,"servers.json",[{"id":"M-01"}]); server.write_tool_json(root,"workspaces.json",[{**ws,"dataset_bindings":[valid]}])
            before=server.environment_bindings(root); result=update_workspace_binding(root,"W-01",before["workspaces_hash"],{"label":"changed"})
            self.assertEqual(result["workspace"]["dataset_bindings"],[valid]); self.assertEqual(result["workspace"]["server_id"],"M-01")

    def test_symlink_binding_mismatch_refuses_fake_remote_preflight(self):
        binding={"id":"data-1","label":"Data","source_path":"/datasets/source","target_path":"/srv/project/data/source","mode":"symlink_ro","required":True,"notes":""}
        ws={"id":"W-01","remote_data_root":"/datasets","environment_policy":{"allowed_write_roots":["/srv/project","/srv/runs"],"read_only_roots":["/datasets"],"forbidden_paths":["/tmp"],"forbidden_operations":["sudo"],"default_deny_write":True},"dataset_bindings":[binding]}
        resolved={"ssh_host":"gpu","project_dir":"/srv/project","run_dir":"/srv/runs/R-1","log_file":"/srv/runs/R-1/run.log","output_dir":"/srv/runs/R-1/out","metrics_file":"/srv/runs/R-1/metrics.json","remote_data_root":"/datasets","tmux_session":"run-r1","dataset_bindings":[binding]}
        context=({}, {"status":"acknowledged"},{"id":"R-1"},resolved,ws,{"mode":"bubblewrap","required":True,"network":"none","deny_read_roots":[]},"python3 train.py",activation_contract("conda:IPLoc"))
        def runner(argv,**_kwargs):
            remote=shlex.split(argv[-1])
            if remote[:2]==["bash","-lc"]: return {"returncode":0,"stdout":"SURVEY_TOOL_ENV_PROOF IPLoc /env/IPLoc /env/IPLoc/bin/python\n","stderr":""}
            if remote[:2]==["realpath","-m"]: return {"returncode":0,"stdout":remote[-1]+"\n","stderr":""}
            if remote and remote[0]=="python3": return {"returncode":0,"stdout":'{"source_kind":"dir","source_readable":true,"target_kind":"symlink_mismatch"}',"stderr":""}
            return {"returncode":0,"stdout":"","stderr":""}
        with mock.patch("survey_tool.managed_execution._lease_context",return_value=context):
            with self.assertRaisesRegex(ValueError,"symlink target mismatch"):
                _managed_execution_preflight(Path("/project"),"D-1","token","pi",runner)


if __name__=="__main__": unittest.main()
