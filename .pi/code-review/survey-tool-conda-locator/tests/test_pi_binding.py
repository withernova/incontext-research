#!/usr/bin/env python3
"""Regression tests for persisted pi bindings without a real pi process."""
import json
import pathlib
import tempfile
import threading
import unittest

import server


class _OfflineBridge:
    proc=None
    session_file=None
    session_name=None
    is_streaming=False

    def state(self):
        raise AssertionError("offline state must not call RPC")


class PiBindingTest(unittest.TestCase):
    def test_prompt_completion_waits_for_one_agent_turn_and_refuses_busy(self):
        bridge=object.__new__(server.PiBridge); bridge._completion_lock=threading.Lock(); bridge._completion_pending=False; bridge.event_cv=threading.Condition(); bridge.events=[]; bridge._seq=0; bridge._cur_text=""; bridge.is_streaming=False
        class Proc:
            def poll(self): return None
        bridge.proc=Proc()
        def prompt(_message):
            bridge._handle_event({"type":"agent_start"}); bridge._handle_event({"type":"message_update","assistantMessageEvent":{"type":"text_delta","delta":"one "}}); bridge._handle_event({"type":"message_update","assistantMessageEvent":{"type":"text_delta","delta":"answer"}}); bridge._handle_event({"type":"agent_end"}); return {"success":True}
        bridge.send=lambda _command,timeout=0:prompt("organize")
        self.assertEqual(server.PiBridge.prompt_completion(bridge,"organize",2),{"success":True,"text":"one answer"})
        bridge.is_streaming=True; result=server.PiBridge.prompt_completion(bridge,"busy",2); self.assertFalse(result["success"]); self.assertIn("streaming",result["error"])

    def setUp(self):
        self.base=pathlib.Path(tempfile.mkdtemp(prefix="survey-pi-binding-"))
        self.root=self.base/"project"; self.root.mkdir(); (self.root/"state.md").write_text("state: TEST\n",encoding="utf-8")
        self.sessions=self.base/"pi-sessions"; self.sessions.mkdir()
        self.old_sessions_root=server.pi_sessions_root; server.pi_sessions_root=lambda:self.sessions

    def tearDown(self):
        server.pi_sessions_root=self.old_sessions_root

    def session(self,directory,name,sid="sid-1",cwd=None,names=()):
        folder=self.sessions/directory; folder.mkdir(parents=True,exist_ok=True); path=folder/name
        rows=[{"type":"session","id":sid,"cwd":str(cwd or self.root),"name":"first"},{"type":"message","message":{"role":"user","content":"研究问题"}}]
        rows.extend({"type":"session_info","name":value} for value in names)
        path.write_text("".join(json.dumps(x,ensure_ascii=False)+"\n" for x in rows),encoding="utf-8")
        return path

    def test_session_meta_last_name_and_binding_roundtrip(self):
        path=self.session("old","a.jsonl",names=("second","最终名称")); meta=server._session_meta(path)
        self.assertEqual(meta["name"],"最终名称"); self.assertEqual(meta["sessionId"],"sid-1"); self.assertEqual(meta["topic"],"研究问题")
        saved=server.write_pi_binding(self.root,meta)
        self.assertEqual(server.read_pi_binding(self.root),saved); self.assertNotIn("messages",saved)
        self.assertEqual(saved["project"],str(self.root.resolve()))
        other=self.base/"other"; other.mkdir(); (other/"state.md").write_text("state: TEST\n",encoding="utf-8")
        server.write_tool_json(other,"pi-binding.json",saved)
        self.assertEqual(server.read_pi_binding(other),{},"项目切换不得串用其他项目快照")

    def test_moved_path_recovers_by_unique_session_id(self):
        old=self.sessions/"gone"/"old.jsonl"
        new=self.session("moved","new.jsonl",sid="stable-id")
        server.write_tool_json(self.root,"pi-binding.json",{"schema":server.PI_BINDING_SCHEMA,"version":1,"project":str(self.root.resolve()),"session_file":str(old),"session_id":"stable-id","session_name":"保存名","topic":"topic","bound_at":"then","updated_at":"then","last_verified_at":"then"})
        resolved=server.resolve_persisted_session(self.root)
        self.assertTrue(resolved["ok"]); self.assertEqual(resolved["path"],str(new.resolve()))
        self.assertEqual(server.read_pi_binding(self.root)["session_file"],str(new.resolve()))

    def test_ambiguous_rejected_and_external_path_invalid(self):
        self.session("one","a.jsonl",sid="duplicate"); self.session("two","b.jsonl",sid="duplicate")
        snapshot={"schema":server.PI_BINDING_SCHEMA,"version":1,"project":str(self.root.resolve()),"session_file":str(self.sessions/"missing.jsonl"),"session_id":"duplicate","session_name":"","topic":"","bound_at":"x","updated_at":"x","last_verified_at":"x"}
        server.write_tool_json(self.root,"pi-binding.json",snapshot)
        result=server.resolve_persisted_session(self.root); self.assertFalse(result["ok"]); self.assertEqual(result["reason"],"ambiguous"); self.assertEqual(len(result["candidates"]),2)
        outside=self.base/"outside.jsonl"; outside.write_text("{}\n",encoding="utf-8")
        snapshot["session_file"]=str(outside); snapshot["session_id"]=""; server.write_tool_json(self.root,"pi-binding.json",snapshot)
        result=server.resolve_persisted_session(self.root); self.assertEqual(result["reason"],"invalid_path")
        with self.assertRaisesRegex(ValueError,"必须位于"): server._safe_session_path(outside)

    def test_offline_state_distinguishes_persisted_from_live(self):
        path=self.session("offline","s.jsonl",sid="offline-id",names=("离线名称",)); server.write_pi_binding(self.root,server._session_meta(path))
        payload=server.pi_state_payload(self.root,_OfflineBridge())
        self.assertFalse(payload["live_bound"]); self.assertFalse(payload["bound"]); self.assertTrue(payload["persisted_bound"]); self.assertTrue(payload["recoverable"])
        self.assertEqual(payload["sessionName"],"离线名称"); self.assertIsNone(payload["state"])

    def test_set_name_waits_for_refresh_then_can_persist(self):
        path=self.session("rename","s.jsonl",sid="rename-id")
        class Fake:
            session_file=str(path); session_name=None; calls=[]
            def send(self,cmd,timeout=0): self.calls.append(cmd["type"]); return {"success":True}
            def state(self): self.calls.append("get_state"); self.session_name="刷新后的名称"; return {"sessionFile":str(path),"sessionName":self.session_name,"isStreaming":False}
        fake=Fake(); result=server.PiBridge.set_name(fake,"刷新后的名称")
        self.assertEqual(fake.calls,["set_session_name","get_state"]); self.assertEqual(result["state"]["sessionName"],"刷新后的名称")
        server.persist_bridge_state(self.root,fake,result["state"])
        self.assertEqual(server.read_pi_binding(self.root)["session_name"],"刷新后的名称")

    def test_list_sessions_merges_header_cwd_and_marks_current_by_id(self):
        current=self.session("unexpected-encoding","one.jsonl",sid="same"); self.session("unexpected-encoding","other.jsonl",sid="other")
        rows=server.list_sessions(self.root,current)
        self.assertEqual({x["sessionId"] for x in rows},{"same","other"}); self.assertTrue(next(x for x in rows if x["sessionId"]=="same")["isCurrent"])
        self.assertTrue(all("recoverable" in x and "topic" in x for x in rows))


if __name__=="__main__": unittest.main()
