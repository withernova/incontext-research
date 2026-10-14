import unittest
import shlex
import subprocess

from survey_tool.v2.herdr_adapter import HerdrAdapter, HerdrCommandError, HerdrStartError, TaskEnvelope, build_task_envelope


def shell_ready():
    return {"result":{"process_info":{"shell_pid":42,"foreground_processes":[{"pid":42,"name":"bash"}]}}}


class HerdrAdapterTest(unittest.TestCase):
    def test_remote_code_map_reads_only_bounded_git_paths_and_reuses_revision(self):
        calls=[]
        def remote_runner(command,**kwargs):
            calls.append((command,kwargs))
            return subprocess.CompletedProcess(command,0,b"SURVEY_TOOL_CODE_MAP_FILE:src/main.py\nSURVEY_TOOL_CODE_MAP_FILE:pyproject.toml\nSURVEY_TOOL_CODE_MAP_CHANGE:src/main.py\nSURVEY_TOOL_CODE_MAP_REV:abc123\n")
        snapshot=HerdrAdapter(remote_runner=remote_runner).inspect_remote_workspace(ssh_host="user@gpu",remote_repo="/srv/repo",known_revision="old")
        self.assertEqual(snapshot,{"revision":"abc123","files":["src/main.py","pyproject.toml"],"changed_files":["src/main.py"],"unchanged":False})
        script=shlex.split(calls[0][0][-1])[2]
        self.assertIn("git -C /srv/repo rev-parse HEAD",script); self.assertIn("git -C /srv/repo ls-files --cached --others --exclude-standard",script); self.assertIn("status --porcelain=v1",script)
        self.assertNotIn("cat ",script); self.assertNotIn("find ",script); self.assertLessEqual(int(script.split("head -n ",1)[1].split()[0]),400)

    def test_remote_tmux_is_provisioned_then_pi_starts_locally(self):
        calls=[]; remote_calls=[]
        def runner(command,**_kwargs):
            calls.append(command)
            if command[1:3]==["tab","create"]: return {"result":{"root_pane":{"pane_id":"private-pane"}}}
            if command[1:3]==["pane","process-info"]: return shell_ready()
            if command[1:3]==["agent","start"]: return {"result":{"agent":{"name":"pi-code-safe","pane_id":"private-pane"}}}
            raise AssertionError(command)
        def remote_runner(command,**kwargs):
            remote_calls.append((command,kwargs)); return subprocess.CompletedProcess(command,0,b"SURVEY_TOOL_REMOTE_TMUX_READY\n")
        result=HerdrAdapter(runner=runner,remote_runner=remote_runner,sleeper=lambda _seconds:None).start_remote_owned(
            local_project_root="/survey/project",ssh_host="user@gpu-host",remote_repo="/srv/repo with space;still-path",
            agent_name="pi-code-safe",tab_label="Pi · 修改代码",session_name="修改代码",
        )
        self.assertEqual(result.agent_name,"pi-code-safe")
        argv=remote_calls[0][0]; self.assertEqual(argv[:6],["ssh","-o","BatchMode=yes","-o","ConnectTimeout=10","user@gpu-host"])
        login=shlex.split(argv[-1]); self.assertEqual(login[:2],["bash","-lc"]); script=login[2]
        self.assertIn("tmux new-session",script); self.assertIn("-c '/srv/repo with space;still-path'",script)
        self.assertIn("SURVEY_TOOL_REMOTE_TMUX_BUSY",script); self.assertNotIn("touch /tmp",script)
        self.assertNotIn("command -v pi",script); self.assertNotIn(" pi --name",script)
        self.assertTrue(any(call[1:3]==["agent","start"] and call[5]=="pi" for call in calls))

    def test_remote_pi_rejects_untrusted_host_before_creating_tab(self):
        calls=[]
        with self.assertRaises(HerdrStartError):
            HerdrAdapter(runner=lambda command,**_kwargs:calls.append(command) or {}).start_remote_owned(
                local_project_root="/survey",ssh_host="gpu;touch /tmp/pwn",remote_repo="/repo",agent_name="pi-safe",
            )
        self.assertEqual(calls,[])

    def test_creates_clean_tab_and_waits_long_enough_for_pi(self):
        calls=[]
        def runner(command,**kwargs):
            calls.append((command,kwargs))
            if command[1:3]==["tab","create"]: return {"result":{"root_pane":{"pane_id":"private-pane"}}}
            if command[1:3]==["pane","process-info"]: return shell_ready()
            return {"result":{"agent":{"name":"st-hex-test-1234567890","pane_id":"private-pane"}}}
        result=HerdrAdapter(runner=runner,binary="herdr",sleeper=lambda _seconds:None).start_owned(project_root="/approved/project",agent_name="st-hex-test-1234567890",agent_kind="pi")
        self.assertEqual(result.agent_name,"st-hex-test-1234567890")
        self.assertEqual(calls[0][0],["herdr","tab","create","--cwd","/approved/project","--label","st-hex-test-1234567890","--no-focus"])
        self.assertEqual(calls[3][0],["herdr","agent","start","st-hex-test-1234567890","--kind","pi","--pane","private-pane","--timeout","60000","--","--name","st-hex-test-1234567890"])
        self.assertLessEqual(calls[0][1]["timeout"],20)
        self.assertGreater(calls[3][1]["timeout"],60)
        self.assertTrue(all(call[1]["output_limit"]<=8192 for call in calls))
        forbidden={"prompt","send-keys","read","focus","close","workspace"}
        self.assertTrue(forbidden.isdisjoint(word for call,_ in calls for word in call))

    def test_explicit_split_uses_new_shell_pane(self):
        calls=[]
        def runner(command,**kwargs):
            calls.append((command,kwargs))
            if command[1:3]==["pane","split"]: return {"result":{"pane":{"pane_id":"private-pane"}}}
            if command[1:3]==["pane","process-info"]: return shell_ready()
            return {"result":{"agent":{"name":"pi","pane_id":"private-pane"}}}
        HerdrAdapter(runner=runner,sleeper=lambda _seconds:None).start_owned(
            project_root="/approved/project",agent_name="st-owned-1234567890",
            agent_kind="pi",topology="split",
        )
        self.assertEqual(calls[0][0],["herdr","pane","split","--current","--direction","right","--cwd","/approved/project","--no-focus"])

    def test_start_timeout_is_safely_classified(self):
        def runner(command,**_kwargs):
            if command[1:3]==["tab","create"]: return {"result":{"root_pane":{"pane_id":"private-pane"}}}
            if command[1:3]==["pane","process-info"]: return shell_ready()
            raise TimeoutError("private output")
        with self.assertRaises(HerdrStartError) as raised:
            HerdrAdapter(runner=runner,sleeper=lambda _seconds:None).start_owned(project_root="/approved/project",agent_name="st-owned-1234567890",agent_kind="pi")
        self.assertEqual(raised.exception.failure_class,"agent_start_timeout")
        self.assertNotIn("private output",str(raised.exception))

    def test_rejects_ambiguous_agent_attestation_without_cleanup(self):
        calls=[]
        def runner(command,**_kwargs):
            calls.append(command)
            if command[1:3]==["tab","create"]: return {"result":{"root_pane":{"pane_id":"private-pane"}}}
            if command[1:3]==["pane","process-info"]: return shell_ready()
            return {"result":{"agent":{"name":"neighbor-agent","pane_id":"private-pane"}}}
        with self.assertRaises(HerdrStartError) as raised:
            HerdrAdapter(runner=runner,sleeper=lambda _seconds:None).start_owned(project_root="/approved/project",agent_name="st-owned-1234567890")
        self.assertTrue(raised.exception.split_succeeded); self.assertEqual(len(calls),4)
        self.assertFalse(any(word in {"close","focus","send-keys","prompt","read"} for call in calls for word in call))

    def test_prompt_uses_only_owned_agent_surface_and_fixed_envelope(self):
        calls=[]
        def runner(command,**kwargs):
            calls.append((command,kwargs))
            return {"result":{"type":"agent_prompted","agent":{"name":"st-owned-1234567890","agent_status":"done"}}}
        envelope=build_task_envelope(target_type="question",target_id="Q-001",target_title="Test",
            task_type="analysis",task_summary="Review evidence",reasoning_effort="medium",max_turns=4)
        result=HerdrAdapter(runner=runner).prompt_owned(agent_name="st-owned-1234567890",envelope=envelope)
        self.assertEqual(result.agent_status,"done")
        command=calls[0][0]
        self.assertEqual(command[:4],["herdr","agent","prompt","st-owned-1234567890"])
        self.assertEqual(command[-3:],["--wait","--timeout","240000"])
        self.assertIn("Q-001",command[4]); self.assertIn("Review evidence",command[4])
        self.assertNotIn("environment",command[4].lower())
        self.assertLessEqual(len(command[4].encode("utf-8")),12000)
        self.assertGreater(calls[0][1]["timeout"],240)

    def test_code_tasks_include_remote_commit_checkpoint(self):
        for task_type in ("implementation", "code_edit", "run_implementation"):
            with self.subTest(task_type=task_type):
                envelope = build_task_envelope(
                    target_type="run", target_id="R-001", target_title="Checkpoint",
                    task_type=task_type, task_summary="Implement and check the change",
                    reasoning_effort="medium", max_turns=5,
                )
                self.assertIn("commit_paths", envelope.text)
                self.assertIn("commit_message", envelope.text)
                self.assertIn("commit SHA", envelope.text)
                self.assertIn("已有用户改动不混入提交", envelope.text)
                self.assertIn("准备工作不重复索要批准", envelope.text)

    def test_run_implementation_envelope_is_bounded_and_keeps_execution_gates(self):
        envelope=build_task_envelope(target_type="run",target_id="R-008",target_title="baseline",
            task_type="run_implementation",task_summary="Implement the metric adapter",reasoning_effort="medium",max_turns=6,
            run_state={"workflow_stage":"code_planning","review_status":"draft","execution_authorized":False,"dispatch_status":"cancelled"})
        self.assertIn("实现并调试 Run",envelope.text); self.assertIn("实现/聚焦检查/修复",envelope.text)
        self.assertIn("不走提交审核/批准循环",envelope.text)
        self.assertIn("survey_run_execution",envelope.text)
        self.assertIn("空 Shell launcher 不是 blocker",envelope.text)
        self.assertIn("不得自行批准、授权",envelope.text)
        self.assertLessEqual(len(envelope.text.encode("utf-8")),12000)
        execution=envelope=build_task_envelope(target_type="run",target_id="R-008",target_title="baseline",
            task_type="run_implementation",task_summary="Start the approved Run",reasoning_effort="medium",max_turns=5,
            run_state={"experiment_id":"E-008","workflow_stage":"ready_to_run","review_status":"approved","execution_authorized":True,"dispatch_status":"claimed"})
        self.assertIn("Mandatory managed-execution action",execution.text)
        self.assertIn('survey_run_execution {action:"continue",run_id:"R-008"',execution.text)
        self.assertIn("自动解析最新授权并原子完成 prepare/claim/ack/start",execution.text)
        self.assertIn("不得查询、记忆、展示或要求用户提供 dispatch ID",execution.text)
        self.assertIn("只有 status 才能证明运行",execution.text)
        resumed=build_task_envelope(target_type="run",target_id="R-008",target_title="baseline",
            task_type="run_implementation",task_summary="Resume the approved Run",reasoning_effort="medium",max_turns=5,
            run_state={"experiment_id":"E-008","workflow_stage":"running","review_status":"approved","execution_authorized":True,"dispatch_status":"running","resume_dispatch_id":"dispatch-1234567890abcdef12345678"},
            run_context={"experiment":{"id":"E-008"},"run":{"id":"R-008","command":"python train.py"},"workspace":{"id":"W-01","remote_repo":"/srv/repo"}})
        self.assertIn("interrupted-Steward recovery",resumed.text); self.assertIn('action:"reattach"',resumed.text); self.assertIn("python train.py",resumed.text); self.assertLessEqual(len(resumed.text.encode("utf-8")),12000)
        adaptive=build_task_envelope(target_type="run",target_id="R-008",target_title="adaptive",
            task_type="run_implementation",task_summary="Plan useful trials",reasoning_effort="medium",max_turns=8,
            run_state={"experiment_id":"E-008","workflow_stage":"ready_to_run","review_status":"approved","execution_authorized":True,"dispatch_status":"queued"},
            run_context={"experiment":{"id":"E-008"},"run":{"id":"R-008","command":"python train.py","trial_plan":{"contract":"survey-tool.run-trial-plan/v1","planning_mode":"ai_planned","request":"find settings that matter","trial_budget":8,"axes":[],"trials":[],"concurrency":2,"max_retries":1}},"workspace":{"id":"W-01","remote_repo":"/srv/repo"}})
        self.assertIn('"planning_mode":"ai_planned"',adaptive.text); self.assertIn("最有信息量",adaptive.text); self.assertIn("trial_budget",adaptive.text)
        huge="复杂的批准上下文"*2000
        bounded=build_task_envelope(target_type="run",target_id="R-008",target_title=huge,
            task_type="run_implementation",task_summary=huge,reasoning_effort="medium",max_turns=20,
            run_state={"experiment_id":"E-008","workflow_stage":"ready_to_run","review_status":"approved","execution_authorized":True,"dispatch_status":"queued"},
            run_context={"experiment":{"id":"E-008","title":huge,"objective":huge},"run":{"id":"R-008","command":"python train.py "+huge,"purpose":huge,"implementation_ref":{"files":[huge]*20}},"workspace":{"id":"W-01","server_id":"S-01","remote_repo":"/srv/repo/"+huge}})
        self.assertLessEqual(len(bounded.text.encode("utf-8")),12000)
        self.assertIn('"run":{"id":"R-008"',bounded.text)
        self.assertIn("python train.py",bounded.text)
        self.assertIn('"canonical_reread_required":true',bounded.text)
        remote_trials=build_task_envelope(target_type="run",target_id="R-008",target_title=huge,
            task_type="run_implementation",task_summary=huge,reasoning_effort="medium",max_turns=20,
            run_state={"experiment_id":"E-008","workflow_stage":"ready_to_run","review_status":"approved","execution_authorized":True,"dispatch_status":"queued"},
            run_context={"experiment":{"id":"E-008","title":huge,"objective":huge},"run":{"id":"R-008","command":"python train.py "+huge,"purpose":huge,"trial_plan":{"contract":"survey-tool.run-trial-plan/v1","planning_mode":"ai_planned","request":huge,"trial_budget":16,"axes":[],"trials":[],"concurrency":4,"max_retries":1}},"workspace":{"id":"W-01","server_id":"S-01","remote_repo":"/srv/repo"}},
            remote_workspace={"ssh_host":"compute-1","remote_repo":"/srv/repo","tmux_session":"st-run-008","code_map_summary":huge})
        self.assertLessEqual(len(remote_trials.text.encode("utf-8")),12000)
        self.assertIn("参数批量实验",remote_trials.text); self.assertIn("trial_manifest_json",remote_trials.text)
        with self.assertRaisesRegex(ValueError,"Run target"):
            build_task_envelope(target_type="experiment",target_id="E-008",target_title="bad",
                task_type="run_implementation",task_summary="bad",reasoning_effort="medium",max_turns=6)

    def test_busy_new_shell_is_rechecked_and_started_once(self):
        starts=0
        def runner(command,**_kwargs):
            nonlocal starts
            if command[1:3]==["tab","create"]: return {"result":{"root_pane":{"pane_id":"private-pane"}}}
            if command[1:3]==["pane","process-info"]: return shell_ready()
            starts+=1
            if starts==1: raise HerdrCommandError("agent_pane_busy")
            return {"result":{"agent":{"name":"st-owned-1234567890","pane_id":"private-pane"}}}
        result=HerdrAdapter(runner=runner,sleeper=lambda _seconds:None).start_owned(
            project_root="/approved/project",agent_name="st-owned-1234567890",agent_kind="pi")
        self.assertEqual(result.agent_name,"st-owned-1234567890"); self.assertEqual(starts,2)

    def test_sets_distinct_human_tab_and_pi_session_names(self):
        calls=[]
        def runner(command,**_kwargs):
            calls.append(command)
            if command[1:3]==["tab","create"]: return {"result":{"root_pane":{"pane_id":"private-pane"}}}
            if command[1:3]==["pane","process-info"]: return shell_ready()
            return {"result":{"agent":{"name":"pi-e-008-code-a13f2c","pane_id":"private-pane"}}}
        HerdrAdapter(runner=runner,sleeper=lambda _seconds:None).start_owned(
            project_root="/approved/project",agent_name="pi-e-008-code-a13f2c",agent_kind="pi",
            tab_label="Pi · E-008 · 修改代码",session_name="E-008 · 修改代码")
        self.assertIn("Pi · E-008 · 修改代码",calls[0])
        self.assertEqual(calls[-1][-3:],["--","--name","E-008 · 修改代码"])

    def test_prompt_rejects_browser_like_raw_text(self):
        with self.assertRaises(HerdrStartError):
            HerdrAdapter(runner=lambda *_args,**_kwargs:{}).prompt_owned(
                agent_name="st-owned-1234567890",envelope="raw prompt"  # type: ignore[arg-type]
            )

    def test_async_prompt_and_console_use_only_owned_agent(self):
        calls=[]
        def runner(command,**_kwargs):
            calls.append(command)
            if command[1:3]==["agent","prompt"]: return {"result":{"type":"agent_prompted","agent":{"name":"st-owned-1234567890","agent_status":"working"}}}
            if command[1:3]==["agent","get"]: return {"result":{"agent":{"name":"st-owned-1234567890","agent_status":"working"}}}
            return {"result":{"type":"pane_read","read":{"text":"monitoring epoch 2\n","truncated":False}}}
        adapter=HerdrAdapter(runner=runner); envelope=TaskEnvelope("fixed internal envelope")
        prompted=adapter.prompt_owned_async(agent_name="st-owned-1234567890",envelope=envelope)
        console=adapter.read_owned(agent_name="st-owned-1234567890",lines=400)
        status=adapter.owned_status(agent_name="st-owned-1234567890")
        self.assertEqual(prompted.agent_status,"working"); self.assertEqual(console.agent_status,"working"); self.assertEqual(status,"working"); self.assertIn("epoch 2",console.text)
        self.assertEqual(calls[0],["herdr","agent","prompt","st-owned-1234567890","fixed internal envelope"])
        self.assertEqual(calls[-1],["herdr","agent","get","st-owned-1234567890"])


if __name__ == "__main__": unittest.main()
