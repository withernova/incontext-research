"""Offline tests: real disposable Git clones, never the user's code or SSH host."""
import json
import os
import pathlib
import subprocess
import tempfile
import unittest
from unittest import mock

import server
from survey_tool import code_workflow as flow
from survey_tool.code_git_worker import Blocked, github_identity, worker

URL = "https://github.com/withernova/iploc-szy"


class CodeWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = pathlib.Path(self.temp.name)
        self.root = self.base / "research"
        self.root.mkdir()
        self.upstream = self.base / "upstream"
        self.git("init", "-b", "main", str(self.upstream))
        self.git("-C", str(self.upstream), "config", "user.name", "Test")
        self.git("-C", str(self.upstream), "config", "user.email", "test@example.invalid")
        self.git("-C", str(self.upstream), "config", "receive.denyCurrentBranch", "updateInstead")
        self.a = self.commit("a")
        self.local = self.base / "local"
        self.remote = self.base / "remote"
        for repo in (self.local, self.remote):
            self.git("clone", str(self.upstream), str(repo))
            self.git("-C", str(repo), "remote", "set-url", "origin", URL)
            self.git("-C", str(repo), "config", "user.name", "Test")
            self.git("-C", str(repo), "config", "user.email", "test@example.invalid")
        self.b = self.commit("b")
        self.binding = {"mode": "local-git", "repository_url": URL, "branch": "main"}
        self.ws = {"id": "W", "server_id": "S", "remote_repo": str(self.remote), "code_development": self.binding,
                   "environment_policy": {"allowed_write_roots": [str(self.remote)], "read_only_roots": [], "forbidden_paths": [], "default_deny_write": True}}
        for name, rows in (("servers.json", [{"id": "S", "ssh_host": "fixture-host"}]), ("workspaces.json", [self.ws]), ("experiments.json", [{"id": "E-001", "workspace_id": "W"}]), ("runs.json", [])):
            server.write_tool_json(self.root, name, rows)
        flow.save_local_binding(self.root, "W", str(self.local))
        self.actual_run = subprocess.run
        self.calls = []
        self.proc_entries = [pathlib.Path('/proc') / str(os.getpid())]

    def git(self, *args):
        return subprocess.run(["git", *args], capture_output=True, check=True).stdout.decode().strip()

    def commit(self, content):
        (self.upstream / "code.py").write_text(content)
        self.git("-C", str(self.upstream), "add", "code.py")
        self.git("-C", str(self.upstream), "commit", "-m", content)
        return self.git("-C", str(self.upstream), "rev-parse", "HEAD")

    def invoke(self, host, spec):
        self.calls.append((host, spec["action"]))
        def offline_git(args, **kwargs):
            # Redirect all test network transport to the disposable upstream.
            if "fetch" in args or "push" in args:
                args = list(args)
                args[args.index("origin")] = str(self.upstream)
            return self.actual_run(args, **kwargs)
        actual_iterdir = pathlib.Path.iterdir
        def isolated_iterdir(path):
            return iter(self.proc_entries) if str(path) == '/proc' else actual_iterdir(path)
        with mock.patch("survey_tool.code_git_worker.subprocess.run", side_effect=offline_git), mock.patch.object(pathlib.Path, 'iterdir', isolated_iterdir):
            try:
                return {"ok": True, **worker(spec)}
            except Blocked as exc:
                raise ValueError(str(exc)) from exc

    def use_project_storage(self):
        self.binding={**self.binding,'storage':'project'}
        self.ws['code_development']=self.binding
        server.write_tool_json(self.root,'workspaces.json',[self.ws])
        self.project_clone=pathlib.Path(flow.project_repo_path(self.root,'W',self.binding))

    def offline_clone(self,root,wid,binding):
        def runner(args,**kwargs):
            args=list(args); clone_url=args[-2]; args[-2]=str(self.upstream)
            result=self.actual_run(args,**kwargs)
            if not result.returncode:
                self.git('-C',args[-1],'remote','set-url','origin',clone_url)
            return result
        return flow.ensure_project_clone(root,wid,binding,runner=runner)

    def unset_code_binding(self, mode=None):
        if mode is None:
            self.ws.pop('code_development',None)
        else:
            self.ws['code_development']={'mode':mode}
        server.write_tool_json(self.root,'workspaces.json',[self.ws])

    def test_prepare_automatically_discovers_binds_and_clones_missing_binding(self):
        self.unset_code_binding()
        before=server.workspace_execution_hash(self.ws)
        result=flow.prepare_code(self.root,'W',invoke=self.invoke,clone=self.offline_clone)
        ws=server.experiment_data(self.root)['workspaces'][0]
        self.assertEqual(ws['code_development'],{**self.binding,'storage':'project','transport':'https'})
        self.assertNotEqual(server.workspace_execution_hash(ws),before)
        self.assertTrue(result['binding_created'])
        self.assertTrue(result['local_clone_created'])
        self.assertEqual(result['local_repo'],str(self.root/'code-repositories'/'W'/'iploc-szy'))
        self.assertEqual(self.calls[0],('fixture-host','discover'))
        self.assertEqual(self.git('-C',result['local_repo'],'rev-parse','HEAD'),self.b)
        self.assertEqual(self.git('-C',str(self.local),'rev-parse','HEAD'),self.a,'old external clone is not moved')
        again=flow.prepare_code(self.root,'W',invoke=self.invoke,clone=mock.Mock(side_effect=AssertionError('second clone')))
        self.assertFalse(again['binding_created'])
        self.assertFalse(again['local_clone_created'])

    def test_auto_binding_preserves_ssh_transport_without_guessing_branch(self):
        self.unset_code_binding('auto')
        self.git('-C',str(self.remote),'remote','set-url','origin','git@github.com:withernova/iploc-szy.git')
        result=flow.prepare_code(self.root,'W',invoke=self.invoke,clone=self.offline_clone)
        ws=server.experiment_data(self.root)['workspaces'][0]
        self.assertEqual(ws['code_development']['transport'],'ssh')
        self.assertEqual(self.git('-C',result['local_repo'],'remote','get-url','origin'),'git@github.com:withernova/iploc-szy.git')
        self.assertFalse(result['push_performed'])
        self.assertFalse(result['execution_started'])
        # Discovery observes a non-main branch instead of assuming the default.
        self.git('-C',str(self.remote),'branch','-m','feature/actual')
        self.unset_code_binding('auto')
        self.assertTrue(flow.auto_bind_code(self.root,'W',invoke=self.invoke))
        self.assertEqual(server.experiment_data(self.root)['workspaces'][0]['code_development']['branch'],'feature/actual')

    def test_discovery_is_read_only_and_existing_binding_is_not_overwritten(self):
        head=self.git('-C',str(self.remote),'rev-parse','HEAD')
        self.assertFalse(flow.auto_bind_code(self.root,'W',invoke=self.invoke))
        self.assertEqual(self.calls,[])
        self.unset_code_binding()
        self.assertTrue(flow.auto_bind_code(self.root,'W',invoke=self.invoke))
        self.assertEqual(self.calls,[('fixture-host','discover')])
        self.assertEqual(self.git('-C',str(self.remote),'rev-parse','HEAD'),head)
        self.assertFalse((self.remote/'.git'/'survey-tool-code.lock').exists())
        self.assertFalse((self.root/'code-repositories').exists())

    def test_explicit_remote_prompt_stays_remote_but_local_prepare_can_auto_bind(self):
        self.unset_code_binding('remote')
        self.assertEqual(flow.code_workflow_prompt(self.root,self.ws,'/tool/surveyctl.py'),'')
        result=flow.prepare_code(self.root,'W',invoke=self.invoke,clone=self.offline_clone)
        self.assertTrue(result['binding_created'])

    def test_autobind_failure_keeps_registry_and_directories_unchanged(self):
        self.unset_code_binding()
        path=self.root/'.survey-tool'/'workspaces.json'
        for failure in ('auth unavailable','origin unavailable'):
            original=path.read_bytes()
            with self.assertRaisesRegex(ValueError,failure):
                flow.auto_bind_code(self.root,'W',invoke=mock.Mock(side_effect=ValueError(failure)))
            self.assertEqual(path.read_bytes(),original)
            self.assertFalse((self.root/'code-repositories').exists())
        self.git('-C',str(self.remote),'checkout','--detach')
        with self.assertRaisesRegex(ValueError,'symbolic-ref'):
            flow.auto_bind_code(self.root,'W',invoke=self.invoke)
        self.assertEqual(path.read_bytes(),original)

    def test_autobind_rejects_credentials_policy_collision_and_active_run(self):
        self.unset_code_binding()
        path=self.root/'.survey-tool'/'workspaces.json'; original=path.read_bytes()
        self.git('-C',str(self.remote),'remote','set-url','origin','https://private-value@github.com/a/b')
        with self.assertRaisesRegex(ValueError,'credential-free') as caught:
            flow.auto_bind_code(self.root,'W',invoke=self.invoke)
        self.assertNotIn('private-value',str(caught.exception))
        self.assertEqual(path.read_bytes(),original)
        self.git('-C',str(self.remote),'remote','set-url','origin',URL)
        target=self.root/'code-repositories'/'W'/'iploc-szy'; target.mkdir(parents=True); note=target/'user.md'; note.write_text('preserve')
        with self.assertRaisesRegex(ValueError,'no overwrite'):
            flow.auto_bind_code(self.root,'W',invoke=self.invoke)
        self.assertEqual(path.read_bytes(),original)
        self.assertEqual(note.read_text(),'preserve')
        self.ws['environment_policy']['forbidden_paths']=[str(self.remote/'.git')]
        server.write_tool_json(self.root,'workspaces.json',[self.ws])
        with self.assertRaisesRegex(ValueError,'write policy'):
            flow.auto_bind_code(self.root,'W',invoke=self.invoke)
        server.write_tool_json(self.root,'runs.json',[{'id':'R','experiment_id':'E-001','status':'running'}])
        self.calls.clear()
        with self.assertRaisesRegex(ValueError,'active Run'):
            flow.auto_bind_code(self.root,'W',invoke=self.invoke)
        self.assertEqual(self.calls,[])

    def test_autobind_concurrent_registry_change_does_not_overwrite(self):
        self.unset_code_binding()
        def race(host,spec):
            state=self.invoke(host,spec)
            self.ws['label']='other edit'
            server.write_tool_json(self.root,'workspaces.json',[self.ws])
            return state
        with self.assertRaisesRegex(ValueError,'changed during discovery'):
            flow.auto_bind_code(self.root,'W',invoke=race)
        ws=server.experiment_data(self.root)['workspaces'][0]
        self.assertNotIn('code_development',ws)
        self.assertEqual(ws['label'],'other edit')

    def test_auto_prompt_requires_no_manual_binding_or_network(self):
        self.unset_code_binding()
        with mock.patch('survey_tool.code_workflow._invoke',side_effect=AssertionError('network in prompt')):
            prompt=flow.code_workflow_prompt(self.root,self.ws,'/tool/surveyctl.py')
        self.assertIn('code prepare --workspace-id W',prompt)
        self.assertIn('无需手填绑定',prompt)
        self.assertIn('只改返回的 local_repo',prompt)
        self.assertNotIn('未绑定：停止',prompt)
        self.assertNotIn('code_development',server.experiment_data(self.root)['workspaces'][0])
        bindings=server.environment_bindings(self.root)
        saved=server.update_workspace_binding(self.root,'W',bindings['workspaces_hash'],{'code_development':{'mode':'auto'}})
        self.assertEqual(saved['workspace']['code_development'],{'mode':'auto'})
        self.assertFalse((self.root/'code-repositories').exists())

    def test_project_storage_clones_after_remote_inspection(self):
        self.use_project_storage()
        self.assertEqual(flow.local_binding(self.root,'W'),str(self.project_clone))
        with mock.patch.object(flow,'machine_key',return_value='other-machine'):
            self.assertEqual(flow.local_binding(self.root,'W'),str(self.project_clone))
        result=flow.prepare_code(self.root,'W',invoke=self.invoke,clone=self.offline_clone)
        self.assertTrue(result['local_clone_created'])
        self.assertEqual(self.calls[0],('fixture-host','checkpoint'))
        self.assertEqual(self.git('-C',str(self.project_clone),'rev-parse','HEAD'),self.b)
        self.assertTrue((self.local/'.git').exists())  # Original external clone was not moved.
        self.assertEqual(self.git('-C',str(self.local),'rev-parse','HEAD'),self.a)
        result=flow.prepare_code(self.root,'W',invoke=self.invoke,clone=mock.Mock(side_effect=AssertionError('second clone')))
        self.assertFalse(result['local_clone_created'])

    def test_project_clone_failure_preserves_reserved_path_and_redacts_stderr(self):
        self.use_project_storage()
        runner=mock.Mock(return_value=subprocess.CompletedProcess([],1,b'',b'private authentication value'))
        with self.assertRaisesRegex(ValueError,'clone failed') as caught:
            flow.ensure_project_clone(self.root,'W',self.binding,runner=runner)
        self.assertNotIn('private',str(caught.exception))
        self.assertTrue(self.project_clone.is_dir())
        runner.reset_mock()
        with self.assertRaisesRegex(ValueError,'already exists'):
            flow.ensure_project_clone(self.root,'W',self.binding,runner=runner)
        runner.assert_not_called()

    def test_project_storage_relocates_with_research_project(self):
        self.use_project_storage()
        moved=self.base/'moved-project'
        self.root.rename(moved)
        self.assertEqual(flow.local_binding(moved,'W'),str(moved/'code-repositories'/'W'/'iploc-szy'))
        self.assertFalse((moved/'code-repositories').exists())

    def test_project_storage_save_is_config_only_and_ignores_old_machine_path(self):
        bindings=server.environment_bindings(self.root)
        with mock.patch.object(flow,'ensure_project_clone',side_effect=AssertionError('clone on save')):
            saved=server.update_workspace_binding(self.root,'W',bindings['workspaces_hash'],{'code_development':{**self.binding,'storage':'project'}})
        path=saved['workspace']['local_code_repo']
        self.assertEqual(path,str(self.root/'code-repositories'/'W'/'iploc-szy'))
        self.assertFalse(pathlib.Path(path).exists())
        self.assertEqual(saved['project_code_root'],str(self.root/'code-repositories'))
        with self.assertRaisesRegex(ValueError,'由工具计算'):
            server.update_workspace_binding(self.root,'W',saved['workspaces_hash'],{'local_code_repo':str(self.local)})
        self.assertEqual(server.read_tool_json(self.root,'local-code-bindings.json',{})[flow.machine_key()]['W'],str(self.local))

    def test_project_path_collision_symlink_and_unsafe_identity_fail_closed(self):
        self.use_project_storage()
        self.project_clone.mkdir(parents=True)
        note=self.project_clone/'user.md'; note.write_text('preserve')
        with self.assertRaisesRegex(ValueError,'no overwrite'):
            flow.prepare_code(self.root,'W',invoke=self.invoke)
        self.assertEqual(note.read_text(),'preserve')
        with self.assertRaisesRegex(ValueError,'unsafe Workspace'):
            flow.project_repo_path(self.root,'../escape',self.binding)
        alias=self.base/'alias-project'; alias.mkdir()
        (alias/'code-repositories').symlink_to(self.base,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'symlink'):
            flow.project_repo_path(alias,'W',self.binding)
        with self.assertRaisesRegex(ValueError,'publish snapshot'):
            flow.project_repo_path(self.root/'.publish','W',self.binding)

    def test_unsafe_remote_does_not_clone(self):
        self.use_project_storage()
        clone=mock.Mock(side_effect=AssertionError('should not clone'))
        (self.remote/'.env').write_text('keep private')
        with self.assertRaisesRegex(ValueError,'credentials'):
            flow.prepare_code(self.root,'W',invoke=self.invoke,clone=clone)
        clone.assert_not_called()
        self.assertFalse(self.project_clone.exists())

    def test_prepare_syncs_remote_then_local_same_commit(self):
        result = flow.prepare_code(self.root, "W", invoke=self.invoke)
        self.assertEqual(result["baseline_commit"], self.b)
        self.assertEqual(self.calls, [("", "inspect"), ("fixture-host", "checkpoint"), ("", "inspect"), ("fixture-host", "advance"), ("", "advance")])
        self.assertFalse(result["push_performed"])
        self.assertFalse(result["execution_started"])
        for repo in (self.local, self.remote):
            self.assertEqual(self.git("-C", str(repo), "rev-parse", "HEAD"), self.b)

    def test_dirty_local_prevents_remote_write_and_invalidates_receipt(self):
        flow.prepare_code(self.root, "W", invoke=self.invoke)
        self.calls.clear()
        (self.local / "user.py").write_text("preserve")
        with self.assertRaisesRegex(ValueError, "dirty"):
            flow.prepare_code(self.root, "W", invoke=self.invoke)
        self.assertEqual(self.calls, [("", "inspect")])
        self.assertTrue((self.local / "user.py").exists())
        self.assertFalse(server.read_tool_json(self.root, "code-sync-receipts.json", {})[flow.machine_key()])

    def test_dirty_remote_is_committed_pushed_then_pulled(self):
        (self.remote / "user.py").write_text("preserve")
        result = flow.prepare_code(self.root, "W", invoke=self.invoke)
        self.assertTrue(result['remote_commit_created'])
        self.assertTrue(result['push_performed'])
        self.assertFalse(result['execution_started'])
        for repo in (self.local, self.remote, self.upstream):
            self.assertEqual(self.git('-C',str(repo),'rev-parse','HEAD'),result['baseline_commit'])
            self.assertEqual((repo/'user.py').read_text(),'preserve')
            self.assertEqual(self.git('-C',str(repo),'status','--porcelain'),'')
        again = flow.prepare_code(self.root, 'W', invoke=self.invoke)
        self.assertFalse(again['push_performed'])
        self.assertFalse(again['remote_commit_created'])

    def test_ahead_unpublished_commit_is_published_without_replacement(self):
        flow.prepare_code(self.root, 'W', invoke=self.invoke)
        (self.remote / "user.py").write_text("preserve")
        self.git("-C", str(self.remote), "add", "user.py")
        self.git("-C", str(self.remote), "commit", "-m", "user")
        original = self.git("-C", str(self.remote), "rev-parse", "HEAD")
        result = flow.prepare_code(self.root, "W", invoke=self.invoke)
        self.assertFalse(result['remote_commit_created'])
        self.assertTrue(result['push_performed'])
        for repo in (self.local, self.remote, self.upstream):
            self.assertEqual(self.git('-C',str(repo),'rev-parse','HEAD'),original)

    def local_checkpoint(self, text='local edit'):
        (self.local/'code.py').write_text(text)
        self.git('-C',str(self.local),'add','code.py')
        self.git('-C',str(self.local),'commit','-m','local implementation')
        return self.git('-C',str(self.local),'rev-parse','HEAD')

    def test_publish_exact_sha_then_explicit_deploy(self):
        flow.prepare_code(self.root, 'W', invoke=self.invoke)
        sha = self.local_checkpoint()
        result = flow.publish_code(self.root, 'W', sha, invoke=self.invoke)
        self.assertEqual(result['published_commit'],sha)
        self.assertTrue(result['push_performed'])
        self.assertFalse(result['execution_started'])
        self.assertEqual(self.git('-C',str(self.upstream),'rev-parse','HEAD'),sha)
        self.assertEqual(self.git('-C',str(self.remote),'rev-parse','HEAD'),self.b,'publish is not deployment')
        self.assertFalse(flow.publish_code(self.root,'W',sha,invoke=self.invoke)['push_performed'])
        result = flow.deploy_code(self.root,'W',sha,f'DEPLOY CODE W {sha}',invoke=self.invoke)
        self.assertEqual(result['deployed_commit'],sha)
        self.assertEqual(self.git('-C',str(self.remote),'rev-parse','HEAD'),sha)

    def test_publish_requires_prepare_exact_head_clean_state_and_same_binding(self):
        with self.assertRaisesRegex(ValueError,'40-character'):
            flow.publish_code(self.root,'W','main',invoke=self.invoke)
        with self.assertRaisesRegex(ValueError,'receipt'):
            flow.publish_code(self.root,'W',self.a,invoke=self.invoke)
        flow.prepare_code(self.root,'W',invoke=self.invoke)
        sha=self.local_checkpoint()
        with self.assertRaisesRegex(ValueError,'exact clean local HEAD'):
            flow.publish_code(self.root,'W',self.b,invoke=self.invoke)
        (self.local/'user.py').write_text('uncommitted')
        with self.assertRaisesRegex(ValueError,'dirty'):
            flow.publish_code(self.root,'W',sha,invoke=self.invoke)
        (self.local/'user.py').unlink()  # Fixture only.
        self.ws['code_development']={**self.binding,'branch':'other'}
        server.write_tool_json(self.root,'workspaces.json',[self.ws])
        with self.assertRaisesRegex(ValueError,'receipt'):
            flow.publish_code(self.root,'W',sha,invoke=self.invoke)

    def test_publish_stops_when_upstream_changes(self):
        flow.prepare_code(self.root,'W',invoke=self.invoke)
        sha=self.local_checkpoint()
        upstream_sha=self.commit('other task')
        with self.assertRaisesRegex(ValueError,'upstream changed'):
            flow.publish_code(self.root,'W',sha,invoke=self.invoke)
        self.assertEqual(self.git('-C',str(self.local),'rev-parse','HEAD'),sha)
        self.assertEqual(self.git('-C',str(self.upstream),'rev-parse','HEAD'),upstream_sha)
        self.assertEqual(server.read_tool_json(self.root,'code-sync-receipts.json',{})[flow.machine_key()]['W']['operation'],'prepare')

    def test_multiple_local_checkpoint_publications_use_previous_published_sha(self):
        flow.prepare_code(self.root,'W',invoke=self.invoke)
        first=self.local_checkpoint('first')
        flow.publish_code(self.root,'W',first,invoke=self.invoke)
        second=self.local_checkpoint('second')
        result=flow.publish_code(self.root,'W',second,invoke=self.invoke)
        self.assertEqual(result['baseline_commit'],self.b)
        self.assertEqual(result['published_commit'],second)
        self.assertEqual(self.git('-C',str(self.upstream),'rev-parse','HEAD'),second)

    def test_remote_divergence_and_dirty_fast_forward_conflict_are_preserved(self):
        (self.remote/'code.py').write_text('uncommitted competing edit')
        with self.assertRaisesRegex(ValueError,'Git command failed: merge'):
            flow.prepare_code(self.root,'W',invoke=self.invoke)
        self.assertEqual((self.remote/'code.py').read_text(),'uncommitted competing edit')
        self.assertEqual(self.git('-C',str(self.remote),'rev-parse','HEAD'),self.a)
        self.git('-C',str(self.remote),'add','code.py')
        self.git('-C',str(self.remote),'commit','-m','divergent')
        original=self.git('-C',str(self.remote),'rev-parse','HEAD')
        with self.assertRaisesRegex(ValueError,'diverged'):
            flow.prepare_code(self.root,'W',invoke=self.invoke)
        self.assertEqual(self.git('-C',str(self.remote),'rev-parse','HEAD'),original)
        self.assertEqual(self.git('-C',str(self.upstream),'rev-parse','HEAD'),self.b)

    def test_remote_checkpoint_tracks_deletion_and_literal_filenames(self):
        flow.prepare_code(self.root,'W',invoke=self.invoke)
        (self.remote/'code.py').unlink()
        name=' code [test] 新.py'
        (self.remote/name).write_text('new code')
        result=flow.prepare_code(self.root,'W',invoke=self.invoke)
        self.assertTrue(result['push_performed'])
        self.assertFalse((self.local/'code.py').exists())
        self.assertEqual((self.local/name).read_text(),'new code')

    def test_remote_checkpoint_excludes_credentials_artifacts_binary_and_symlinks(self):
        flow.prepare_code(self.root,'W',invoke=self.invoke)
        for name,content in [('.env',b'private'),('outputs/log.txt',b'log'),('model.pt',b'weights'),('secret.py',b'password="'+b'x'*24+b'"'),('binary.bin',b'\x00'),('large.txt',b'a'*1_000_001)]:
            with self.subTest(name=name):
                entry=self.remote/name; entry.parent.mkdir(parents=True,exist_ok=True); entry.write_bytes(content)
                with self.assertRaises(ValueError):
                    flow.prepare_code(self.root,'W',invoke=self.invoke)
                self.assertEqual(entry.read_bytes(),content)
                self.assertEqual(self.git('-C',str(self.remote),'rev-parse','HEAD'),self.b)
                self.assertEqual(self.git('-C',str(self.upstream),'rev-parse','HEAD'),self.b)
                entry.unlink()  # Fixture only.
        (self.remote/'alias.py').symlink_to(self.remote/'code.py')
        with self.assertRaisesRegex(ValueError,'symlinks'):
            flow.prepare_code(self.root,'W',invoke=self.invoke)

    def test_remote_checkpoint_respects_per_file_write_policy(self):
        flow.prepare_code(self.root,'W',invoke=self.invoke)
        target=self.remote/'protected.py'; target.write_text('preserve')
        self.ws['environment_policy']['forbidden_paths']=[str(target)]
        server.write_tool_json(self.root,'workspaces.json',[self.ws])
        with self.assertRaisesRegex(ValueError,'write policy'):
            flow.prepare_code(self.root,'W',invoke=self.invoke)
        self.assertEqual(self.git('-C',str(self.remote),'rev-parse','HEAD'),self.b)
        self.assertEqual(target.read_text(),'preserve')

    def test_push_failure_preserves_remote_commit_without_success_receipt(self):
        (self.remote/'new.py').write_text('code')
        actual=self.actual_run
        def failed_push(args,**kwargs):
            if 'push' in args:
                return subprocess.CompletedProcess(args,1,b'',b'private auth failure')
            return actual(args,**kwargs)
        self.actual_run=failed_push
        with self.assertRaisesRegex(ValueError,'push') as caught:
            flow.prepare_code(self.root,'W',invoke=self.invoke)
        self.assertNotIn('private',str(caught.exception))
        checkpoint=self.git('-C',str(self.remote),'rev-parse','HEAD')
        self.assertNotIn(checkpoint,{self.a,self.b})
        self.assertEqual(self.git('-C',str(self.local),'rev-parse','HEAD'),self.a)
        self.assertFalse(server.read_tool_json(self.root,'code-sync-receipts.json',{})[flow.machine_key()])
        self.actual_run=actual
        result=flow.prepare_code(self.root,'W',invoke=self.invoke)
        self.assertEqual(result['baseline_commit'],checkpoint)
        self.assertFalse(result['remote_commit_created'])
        self.assertTrue(result['push_performed'])

    def test_outgoing_history_checks_remote_and_local_secrets_even_if_deleted(self):
        saved_prepare=flow.prepare_code(self.root,'W',invoke=self.invoke)
        for repo in (self.remote,self.local):
            with self.subTest(repo=repo.name):
                target=repo/'secret.py'
                target.write_text('password="'+'x'*24+'"')
                self.git('-C',str(repo),'add','secret.py')
                self.git('-C',str(repo),'commit','-m','accidental credential fixture')
                target.unlink()
                self.git('-C',str(repo),'add','-A')
                self.git('-C',str(repo),'commit','-m','remove fixture credential')
                sha=self.git('-C',str(repo),'rev-parse','HEAD')
                with self.assertRaisesRegex(ValueError,'suspected credential') as caught:
                    if repo==self.remote:
                        flow.prepare_code(self.root,'W',invoke=self.invoke)
                    else:
                        # A failed remote prepare deliberately invalidated its receipt.
                        server.write_tool_json(self.root,'code-sync-receipts.json',{flow.machine_key():{'W':saved_prepare}})
                        flow.publish_code(self.root,'W',sha,invoke=self.invoke)
                self.assertNotIn('x'*24,str(caught.exception))
                self.assertEqual(self.git('-C',str(self.upstream),'rev-parse','HEAD'),self.b)

    def test_cli_publish_routes_exact_sha_without_deployment(self):
        import contextlib
        import io
        import surveyctl
        output=io.StringIO()
        with mock.patch.object(surveyctl,'root_for',return_value=self.root), mock.patch.object(flow,'publish_code',return_value={'operation':'publish'}) as publish, mock.patch.object(flow,'deploy_code') as deploy, mock.patch('sys.argv',['surveyctl','--project',str(self.root),'code','publish','--workspace-id','W','--commit',self.b]), contextlib.redirect_stdout(output):
            surveyctl.main()
        publish.assert_called_once_with(self.root,'W',self.b)
        deploy.assert_not_called()
        self.assertEqual(json.loads(output.getvalue())['operation'],'publish')

    def test_pushurl_redirect_and_mirror_are_rejected(self):
        flow.prepare_code(self.root,'W',invoke=self.invoke)
        sha=self.local_checkpoint()
        self.git('-C',str(self.local),'remote','set-url','--push','origin','https://github.com/other/repo')
        with self.assertRaisesRegex(ValueError,'push destination'):
            flow.publish_code(self.root,'W',sha,invoke=self.invoke)
        self.git('-C',str(self.local),'remote','set-url','--push','origin',URL)
        self.git('-C',str(self.local),'config','remote.origin.mirror','true')
        with self.assertRaisesRegex(ValueError,'mirror'):
            flow.publish_code(self.root,'W',sha,invoke=self.invoke)
        self.assertEqual(self.git('-C',str(self.upstream),'rev-parse','HEAD'),self.b)

    def test_policy_denies_git_metadata(self):
        self.ws["environment_policy"]["forbidden_paths"] = [str(self.remote / ".git")]
        server.write_tool_json(self.root, "workspaces.json", [self.ws])
        with self.assertRaisesRegex(ValueError, "write policy"):
            flow.prepare_code(self.root, "W", invoke=self.invoke)
        self.assertEqual(self.git("-C", str(self.remote), "rev-parse", "HEAD"), self.a)

    def test_origin_mismatch_and_wrong_branch(self):
        self.git("-C", str(self.local), "remote", "set-url", "origin", "https://github.com/other/repo")
        with self.assertRaisesRegex(ValueError, "origin repository"):
            flow.prepare_code(self.root, "W", invoke=self.invoke)
        self.git("-C", str(self.local), "remote", "set-url", "origin", URL)
        self.git("-C", str(self.local), "checkout", "-b", "other")
        with self.assertRaisesRegex(ValueError, "wrong branch"):
            flow.prepare_code(self.root, "W", invoke=self.invoke)

    def test_active_run_blocks_before_git_or_network(self):
        server.write_tool_json(self.root, "runs.json", [{"id": "R", "experiment_id": "E-001", "status": "running"}])
        with self.assertRaisesRegex(ValueError, "active Run"):
            flow.prepare_code(self.root, "W", invoke=self.invoke)
        self.assertFalse(self.calls)

    def test_process_in_remote_repo_blocks(self):
        process = subprocess.Popen(["sleep", "30"], cwd=self.remote)
        self.proc_entries.append(pathlib.Path('/proc') / str(process.pid))
        try:
            with self.assertRaisesRegex(ValueError, "in use"):
                flow.prepare_code(self.root, "W", invoke=self.invoke)
        finally:
            process.terminate()
            process.wait(timeout=10)

    def test_unobservable_same_user_process_blocks(self):
        entry=mock.MagicMock(); entry.name='999999'; entry.stat.return_value.st_uid=os.getuid()
        entry.__truediv__.return_value.resolve.side_effect=PermissionError('restricted proc')
        self.proc_entries.append(entry)
        with self.assertRaisesRegex(ValueError, 'idle state is unknown'):
            flow.prepare_code(self.root, 'W', invoke=self.invoke)
        self.assertNotIn(('fixture-host', 'advance'), self.calls)

    def test_deploy_requires_receipt_exact_sha_and_confirmation(self):
        with self.assertRaisesRegex(ValueError, "40-character"):
            flow.deploy_code(self.root, "W", "main", "", invoke=self.invoke)
        with self.assertRaisesRegex(ValueError, "human confirmation"):
            flow.deploy_code(self.root, "W", self.b, "", invoke=self.invoke)
        phrase = f"DEPLOY CODE W {self.b}"
        with self.assertRaisesRegex(ValueError, "receipt"):
            flow.deploy_code(self.root, "W", self.b, phrase, invoke=self.invoke)
        flow.prepare_code(self.root, "W", invoke=self.invoke)
        # Publish new code in the fixture's upstream; local HEAD matches that commit.
        c = self.commit("c")
        self.invoke("", flow._spec(self.binding, str(self.local), "inspect"))
        self.invoke("", flow._spec(self.binding, str(self.local), "advance", target=c, expected_head=self.b))
        result = flow.deploy_code(self.root, "W", c, f"DEPLOY CODE W {c}", invoke=self.invoke)
        self.assertEqual(result["deployed_commit"], c)
        self.assertEqual(self.git("-C", str(self.remote), "rev-parse", "HEAD"), c)
        self.assertFalse(result["execution_started"])

    def test_partial_failure_no_success_receipt(self):
        def failing(host, spec):
            if not host and spec["action"] == "advance":
                raise ValueError("concurrent local edit")
            return self.invoke(host, spec)
        with self.assertRaisesRegex(ValueError, "concurrent"):
            flow.prepare_code(self.root, "W", invoke=failing)
        self.assertEqual(self.git("-C", str(self.remote), "rev-parse", "HEAD"), self.b)
        self.assertEqual(self.git("-C", str(self.local), "rev-parse", "HEAD"), self.a)
        self.assertFalse(server.read_tool_json(self.root, "code-sync-receipts.json", {})[flow.machine_key()])

    def test_machine_path_separate_and_workspace_hash_covers_binding(self):
        original = server.workspace_execution_hash(self.ws)
        with mock.patch.object(flow, "machine_key", return_value="other-machine"):
            self.assertEqual(flow.local_binding(self.root, "W"), "")
        self.assertNotEqual(original, server.workspace_execution_hash({**self.ws, "code_development": {**self.binding, "branch": "other"}}))
        bindings = server.environment_bindings(self.root)
        with mock.patch.object(flow, "_invoke", side_effect=AssertionError("network at save")):
            saved = server.update_workspace_binding(self.root, "W", bindings["workspaces_hash"], {"code_development": self.binding, "local_code_repo": str(self.local)})
        self.assertEqual(saved["workspace"]["local_code_repo"], str(self.local))
        self.assertNotIn("local_code_repo", server.experiment_data(self.root)["workspaces"][0])

    def test_shared_run_lock_prevents_sync(self):
        import fcntl
        with open(self.remote/'.git'/'survey-tool-code.lock','a') as lock:
            fcntl.flock(lock.fileno(),fcntl.LOCK_SH | fcntl.LOCK_NB)
            with self.assertRaisesRegex(ValueError,'repository locked'):
                flow.prepare_code(self.root,'W',invoke=self.invoke)
        self.assertEqual(self.git('-C',str(self.remote),'rev-parse','HEAD'),self.a)

    def test_launcher_checks_sha_and_clean_state_before_outputs(self):
        from survey_tool.managed_execution import build_launcher
        preflight={'resolved':{'project_dir':str(self.remote),'run_dir':'/not-created','output_dir':'/not-created/out','log_file':'/not-created/log'},'write_roots':[str(self.remote)],'read_only_roots':[],'forbidden_roots':[],'dataset_bindings':[],'isolation':{'mode':'tmux-guarded','network':'host','deny_read_roots':[]},'activation':'true','command':'true','code_identity':{'head':self.a,'lock_file':str(self.remote/'.git'/'survey-tool-code.lock')}}
        script=build_launcher(preflight)
        prefix=script.split('mkdir -p -- ',1)[0]
        self.assertIn('flock -s -n 9',prefix)
        self.assertEqual(subprocess.run(['bash','-c',prefix+'echo verified'],capture_output=True).returncode,0)
        (self.remote/'code.py').write_text('dirty')
        self.assertEqual(subprocess.run(['bash','-c',prefix+'echo verified'],capture_output=True).returncode,73)
        self.assertFalse(pathlib.Path('/not-created').exists())

    def test_managed_identity_exact_and_dirty_guard(self):
        resolved = {"ssh_host": "fixture-host", "project_dir": str(self.remote)}
        with self.assertRaisesRegex(ValueError, "exact git_commit"):
            flow.verify_run_commit(self.root, self.ws, {"git_commit": "main"}, resolved, invoke=self.invoke)
        with self.assertRaisesRegex(ValueError, "does not match"):
            flow.verify_run_commit(self.root, self.ws, {"git_commit": self.b}, resolved, invoke=self.invoke)
        state = flow.verify_run_commit(self.root, self.ws, {"git_commit": self.a}, resolved, invoke=self.invoke)
        self.assertEqual(state["head"], self.a)
        (self.remote / "code.py").write_text("dirty")
        with self.assertRaisesRegex(ValueError, "dirty"):
            flow.verify_run_commit(self.root, self.ws, {"git_commit": self.a}, resolved, invoke=self.invoke)

    def test_validation_and_no_credential_echo(self):
        self.assertEqual(github_identity(URL + ".git"), github_identity("git@github.com:withernova/iploc-szy.git"))
        for bad in ({**self.binding, "branch": "../x"}, {**self.binding, "repository_url": "https://credential@github.com/a/b"}, {**self.binding, "command": "arbitrary"}):
            with self.assertRaises(ValueError):
                flow.validate_binding(bad)
        for path in ("/", "/project/.publish/code", "/p\nother"):
            with self.assertRaises(ValueError):
                flow.validate_local_path(path)
        fake = lambda *a, **kw: subprocess.CompletedProcess(a, 1, b'{"ok":false,"error":"Git command failed: fetch"}', b"private stderr")
        with self.assertRaisesRegex(ValueError, "fetch") as caught:
            flow._invoke("fixture-host", {"action": "inspect"}, runner=fake)
        self.assertNotIn("private", str(caught.exception))

    def test_both_web_code_prompts_use_local_workflow(self):
        for task in ('code_edit','run_implementation'):
            server.write_tool_json(self.root,'runs.json',[{'id':'R-code','experiment_id':'E-001','workflow_version':2,'workflow_stage':'code_planning','review_status':'draft'}])
            result=server.ai_discussion_prompt(self.root,'run','R-code','实现指标公式',task=task)
            self.assertIn('code prepare --workspace-id W',result['prompt'])
            self.assertIn('local_repo='+str(self.local),result['prompt'])
            self.assertFalse(result['execution_started'])

    def test_prompt_uses_bound_local_path_and_quoted_prepare(self):
        prompt = flow.code_workflow_prompt(self.root, self.ws, pathlib.Path("/tool path/surveyctl.py"))
        self.assertIn(str(self.local), prompt)
        self.assertIn("code prepare --workspace-id W", prompt)
        self.assertIn("'/tool path/surveyctl.py'", prompt)
        self.assertIn("禁止绕过改走 SSH patch", prompt)
        self.assertIn('code publish --workspace-id W --commit',prompt)
        self.assertIn('先检查本机干净与服务器空闲',prompt)
        self.assertIn('不需要另行询问 push',prompt)
        self.assertNotIn('命令不 push',prompt)
        self.assertEqual(flow.code_workflow_prompt(self.root, {"id": "W"}, "tool"), "")


if __name__ == "__main__":
    unittest.main()
