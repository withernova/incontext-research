import datetime as dt
import pathlib
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor

from survey_tool.v2 import V2Store, v2_capabilities


class V2StoreTest(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp(prefix="survey-v2-store-"))
        (self.root / "state.md").write_text("state: TEST\n", encoding="utf-8")
        self.store = V2Store(self.root)

    def authorized_execution(self, suffix: str, *, ttl_seconds: int = 300):
        capability={"managed":True,"cli_available":True,"codex_supported":True}
        self.store.initialize(); target=f"Q-{suffix}"; request=f"HLR-{suffix}"; execution=f"HEX-{suffix}"
        self.store.create_object(object_id=target,object_type="question",project_id="PROJECT-test")
        self.store.create_herdr_launch_request(object_id=request,project_id="PROJECT-test",target_object_id=target,agent_kind="codex",task_type="analysis",task_summary=f"Review evidence {suffix}")
        self.store.transition_herdr_launch_request(request,expected_revision=1,status="awaiting_approval")
        self.store.transition_herdr_launch_request(request,expected_revision=2,status="approved")
        row=self.store.authorize_herdr_execution(execution_id=execution,project_id="PROJECT-test",launch_request_id=request,expected_request_revision=3,capability=capability,ttl_seconds=ttl_seconds)
        return execution,request,target,row,capability

    def test_initialization_is_explicit_and_idempotent(self):
        self.assertFalse(self.store.exists())
        self.assertEqual(self.store.initialize(), 7)
        self.assertEqual(self.store.initialize(), 7)
        self.assertTrue(self.store.exists())
        self.assertEqual(v2_capabilities(self.root)["project_store"]["schema_version"], 7)

    def test_existing_version_one_store_upgrades_to_version_two(self):
        self.store.path.parent.mkdir(parents=True, exist_ok=True)
        original = dict(__import__("survey_tool.v2.store", fromlist=["_MIGRATIONS"])._MIGRATIONS)
        module = __import__("survey_tool.v2.store", fromlist=["_MIGRATIONS"])
        migration_two = module._MIGRATIONS.pop(2)
        migration_three = module._MIGRATIONS.pop(3)
        migration_four = module._MIGRATIONS.pop(4)
        migration_five = module._MIGRATIONS.pop(5)
        migration_six = module._MIGRATIONS.pop(6)
        migration_seven = module._MIGRATIONS.pop(7)
        try:
            self.assertEqual(self.store.initialize(), 1)
        finally:
            module._MIGRATIONS[2] = migration_two
            module._MIGRATIONS[3] = migration_three
            module._MIGRATIONS[4] = migration_four
            module._MIGRATIONS[5] = migration_five
            module._MIGRATIONS[6] = migration_six
            module._MIGRATIONS[7] = migration_seven
        self.assertEqual(self.store.initialize(), 7)
        candidate = self.store.create_paper_candidate(
            object_id="PC-upgrade", project_id="PROJECT-test", citekey="up2026paper",
            title="Upgrade", source_url="https://openalex.org/W-upgrade",
        )
        self.assertEqual(candidate["citekey"], "up2026paper")
        module._MIGRATIONS.clear(); module._MIGRATIONS.update(original)

    def test_version_six_store_upgrades_without_losing_launch_requests(self):
        module = __import__("survey_tool.v2.store", fromlist=["_MIGRATIONS"])
        migration_seven = module._MIGRATIONS.pop(7)
        try:
            self.assertEqual(self.store.initialize(), 6)
            self.store.create_object(object_id="Q-v6", object_type="question", project_id="PROJECT-test")
            self.store.create_herdr_launch_request(object_id="HLR-v6",project_id="PROJECT-test",target_object_id="Q-v6",agent_kind="codex",task_type="research",task_summary="Preserve this request")
        finally:
            module._MIGRATIONS[7] = migration_seven
        self.assertEqual(self.store.initialize(), 7)
        self.assertEqual(self.store.get_herdr_launch_request("HLR-v6")["task_summary"], "Preserve this request")
        self.assertEqual(self.store.list_herdr_executions(), [])

    def test_object_revision_events_and_conflict(self):
        self.store.initialize()
        created = self.store.create_object(
            object_id="Q-001",
            object_type="question",
            project_id="PROJECT-test",
            title="Initial question",
            canonical_path="shell/01_questions/Q-001.md",
        )
        self.assertEqual(created["revision"], 1)
        updated = self.store.update_object(
            "Q-001", expected_revision=1, fields={"title": "Updated question"}
        )
        self.assertEqual(updated["revision"], 2)
        self.assertEqual(updated["title"], "Updated question")
        with self.assertRaisesRegex(ValueError, "revision conflict"):
            self.store.update_object(
                "Q-001", expected_revision=1, fields={"title": "Stale overwrite"}
            )
        events = self.store.list_events("Q-001")
        self.assertEqual([event["kind"] for event in events], ["question.created", "object.updated"])

    def test_relations_are_typed_and_foreign_keyed(self):
        self.store.initialize()
        for object_id, object_type in (("P-paper", "paper"), ("Q-question", "question")):
            self.store.create_object(
                object_id=object_id,
                object_type=object_type,
                project_id="PROJECT-test",
            )
        relation = self.store.add_relation(
            from_object_id="Q-question",
            relation_type="discusses",
            to_object_id="P-paper",
            metadata={"section": "seven-q-2"},
        )
        self.assertEqual(relation["metadata"], {"section": "seven-q-2"})
        with self.assertRaisesRegex(ValueError, "invalid relation_type"):
            self.store.add_relation(
                from_object_id="Q-question",
                relation_type="arbitrary",
                to_object_id="P-paper",
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.add_relation(
                from_object_id="Q-question",
                relation_type="supports",
                to_object_id="P-missing",
            )

    def test_job_idempotency_transitions_and_revision(self):
        self.store.initialize()
        job = self.store.create_job(
            kind="mineru",
            idempotency_key="paper-1-sha",
            request={"pdf": "papers/a.pdf"},
            timeout_seconds=600,
        )
        duplicate = self.store.create_job(
            kind="mineru",
            idempotency_key="paper-1-sha",
            request={"pdf": "different.pdf"},
        )
        self.assertEqual(duplicate["id"], job["id"])
        running = self.store.transition_job(
            job["id"], expected_revision=1, status="running", progress=0.1
        )
        self.assertEqual(running["attempt"], 1)
        completed = self.store.transition_job(
            job["id"],
            expected_revision=2,
            status="succeeded",
            progress=1,
            result={"markdown": "parsed/a.md"},
        )
        self.assertEqual(completed["result"], {"markdown": "parsed/a.md"})
        with self.assertRaisesRegex(ValueError, "invalid job transition"):
            self.store.transition_job(
                job["id"], expected_revision=3, status="running", progress=0.5
            )

    def test_worker_claim_dependency_lease_and_recovery(self):
        self.store.initialize()
        first = self.store.create_job(kind="paper_download", idempotency_key="download-1")
        second = self.store.create_job(kind="mineru", idempotency_key="mineru-1", depends_on_job_id=first["id"])
        claimed = self.store.claim_next_job(worker_id="worker-1", kinds=["mineru", "paper_download"], lease_seconds=30)
        self.assertEqual(claimed["id"], first["id"])
        self.assertTrue(claimed["lease_token"])
        with self.assertRaisesRegex(ValueError, "lease mismatch"):
            self.store.finish_claimed_job(first["id"], lease_token="wrong", succeeded=True)
        heartbeat = self.store.heartbeat_job(first["id"], lease_token=claimed["lease_token"], progress=.5)
        self.assertEqual(heartbeat["progress"], .5)
        self.store.finish_claimed_job(first["id"], lease_token=claimed["lease_token"], succeeded=True, result={"pdf": "papers/a.pdf"})
        mineru = self.store.claim_next_job(worker_id="worker-1", kinds=["mineru"], lease_seconds=30)
        self.assertEqual(mineru["id"], second["id"])
        recovered = self.store.recover_expired_jobs(now="9999-01-01T00:00:00+00:00")
        self.assertEqual(recovered, 1)
        self.assertEqual(self.store.get_job(second["id"])["status"], "queued")

    def test_concurrent_workers_claim_a_job_only_once(self):
        import concurrent.futures
        self.store.initialize()
        job = self.store.create_job(kind="paper_download", idempotency_key="only-once")
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            claims = list(executor.map(lambda number: self.store.claim_next_job(worker_id=f"worker-{number}"), range(4)))
        claimed = [item for item in claims if item]
        self.assertEqual([item["id"] for item in claimed], [job["id"]])

    def test_human_job_retry_and_cancellation_preserve_worker_boundaries(self):
        self.store.initialize()
        self.store.create_object(object_id="PC-jobs",object_type="paper_candidate",project_id="PROJECT-test")
        download=self.store.create_job(kind="paper_download",target_object_id="PC-jobs",idempotency_key="retry-download")
        mineru=self.store.create_job(kind="mineru",target_object_id="PC-jobs",idempotency_key="retry-mineru",depends_on_job_id=download["id"])
        failed=self.store.transition_job(download["id"],expected_revision=1,status="running")
        failed=self.store.transition_job(download["id"],expected_revision=failed["revision"],status="failed",error_class="NetworkError",error_message="timeout")
        retried=self.store.retry_failed_job(download["id"],expected_revision=failed["revision"],reason="network restored",actor_id="reviewer")
        self.assertEqual(retried["status"],"queued"); self.assertEqual(retried["attempt"],1); self.assertEqual(retried["error_message"],"")
        cancelled=self.store.cancel_queued_job(download["id"],expected_revision=retried["revision"],reason="stop acquisition",actor_id="reviewer")
        self.assertEqual({item["id"] for item in cancelled},{download["id"],mineru["id"]})
        self.assertTrue(all(item["status"]=="cancelled" for item in cancelled))
        events=self.store.list_events("PC-jobs"); self.assertEqual(events[-2]["kind"],"job.retry_requested"); self.assertFalse(events[-2]["details"]["worker_started"]); self.assertFalse(events[-1]["details"]["running_process_stopped"])

    def test_job_retry_rejects_dependency_failure_and_running_cancellation(self):
        self.store.initialize()
        dependency=self.store.create_job(kind="paper_download",idempotency_key="dep")
        child=self.store.create_job(kind="mineru",idempotency_key="child",depends_on_job_id=dependency["id"])
        child=self.store.transition_job(child["id"],expected_revision=1,status="running")
        child=self.store.transition_job(child["id"],expected_revision=child["revision"],status="failed",error_message="parse")
        with self.assertRaisesRegex(ValueError,"dependency is not succeeded"):
            self.store.retry_failed_job(child["id"],expected_revision=child["revision"],reason="retry")
        running=self.store.transition_job(dependency["id"],expected_revision=1,status="running")
        with self.assertRaisesRegex(ValueError,"only queued"):
            self.store.cancel_queued_job(dependency["id"],expected_revision=running["revision"],reason="unsafe")
        with self.assertRaisesRegex(ValueError,"reason"):
            self.store.retry_failed_job(child["id"],expected_revision=child["revision"],reason="")

    def test_agent_session_binding_is_minimal_idempotent_and_revisioned(self):
        self.store.initialize()
        self.store.create_object(object_id="Q-agent", object_type="question", project_id="PROJECT-test", title="Agent target")
        bound = self.store.bind_agent_session(
            session_id="AS-001", provider="pi", object_id="Q-agent", task_type="research",
            external_ref="session-id:stable-123", status="live", agent="pi", model="openai/gpt-5",
        )
        self.assertEqual(bound["external_ref"], "session-id:stable-123")
        self.assertNotIn("messages", bound); self.assertNotIn("prompt", bound)
        refreshed = self.store.bind_agent_session(
            session_id="AS-ignored", provider="pi", object_id="Q-agent", task_type="analysis",
            external_ref="session-id:stable-123", status="paused", agent="pi", model="openai/gpt-5",
        )
        self.assertEqual(refreshed["id"], "AS-001")
        self.assertEqual(refreshed["revision"], 2)
        completed = self.store.update_agent_session_status("AS-001", expected_revision=2, status="completed")
        self.assertEqual(completed["status"], "completed")
        self.assertEqual(len(self.store.list_agent_sessions(object_id="Q-agent")), 1)

    def test_agent_session_rejects_sensitive_refs_and_cross_object_rebind(self):
        self.store.initialize()
        for object_id in ("Q-one", "Q-two"):
            self.store.create_object(object_id=object_id, object_type="question", project_id="PROJECT-test")
        with self.assertRaisesRegex(ValueError, "sensitive"):
            self.store.bind_agent_session(session_id="AS-bad", provider="pi", object_id="Q-one", task_type="research", external_ref="Bearer secret")
        self.store.bind_agent_session(session_id="AS-one", provider="pi", object_id="Q-one", task_type="research", external_ref="session-id:one")
        with self.assertRaisesRegex(ValueError, "another object"):
            self.store.bind_agent_session(session_id="AS-two", provider="pi", object_id="Q-two", task_type="research", external_ref="session-id:one")

    def test_herdr_launch_request_is_persistent_revisioned_and_evented(self):
        self.store.initialize()
        self.store.create_object(object_id="Q-launch", object_type="question", project_id="PROJECT-test", lifecycle_status="reference")
        request = self.store.create_herdr_launch_request(
            object_id="HLR-001", project_id="PROJECT-test", target_object_id="Q-launch",
            agent_kind="codex", task_type="research", task_summary="Review the evidence map",
            safe_config={"reasoning_effort": "high", "max_turns": 4},
        )
        self.assertEqual(request["lifecycle_status"], "draft")
        self.assertEqual(request["safe_config"], {"reasoning_effort": "high", "max_turns": 4})
        submitted = self.store.transition_herdr_launch_request("HLR-001", expected_revision=1, status="awaiting_approval")
        self.assertEqual(submitted["revision"], 2)
        with self.assertRaisesRegex(ValueError, "revision conflict"):
            self.store.transition_herdr_launch_request("HLR-001", expected_revision=1, status="approved")
        approved = self.store.transition_herdr_launch_request("HLR-001", expected_revision=2, status="approved")
        self.assertIsNotNone(approved["approved_at"])
        self.assertEqual(self.store.list_herdr_launch_requests()[0]["id"], "HLR-001")
        events = self.store.list_events("HLR-001")
        self.assertEqual([item["kind"] for item in events], ["herdr_launch_request.created", "herdr_launch_request.transitioned", "herdr_launch_request.transitioned"])
        self.assertTrue(all(item["details"].get("execution_started") is False for item in events))

    def test_herdr_launch_request_rejects_unsafe_or_unbounded_input(self):
        self.store.initialize()
        self.store.create_object(object_id="Q-safe", object_type="question", project_id="PROJECT-test")
        base = dict(object_id="HLR-bad", project_id="PROJECT-test", target_object_id="Q-safe", agent_kind="codex", task_type="analysis", task_summary="Analyze results")
        with self.assertRaisesRegex(ValueError, "agent_kind"):
            self.store.create_herdr_launch_request(**{**base, "agent_kind": "arbitrary"})
        with self.assertRaisesRegex(ValueError, "sensitive"):
            self.store.create_herdr_launch_request(**{**base, "task_summary": "Use bearer private-value"})
        with self.assertRaisesRegex(ValueError, "unsupported launch configuration"):
            self.store.create_herdr_launch_request(**base, safe_config={"cwd": "/private"})
        with self.assertRaisesRegex(ValueError, "Herdr topology"):
            self.store.create_herdr_launch_request(**base, safe_config={"topology": "existing_pane"})
        with self.assertRaisesRegex(KeyError, "target not found"):
            self.store.create_herdr_launch_request(**{**base, "target_object_id": "Q-missing"})
        with self.assertRaisesRegex(ValueError,"requires a Run target"):
            self.store.create_herdr_launch_request(**{**base,"object_id":"HLR-wrong-run","agent_kind":"pi","task_type":"run_implementation","task_summary":"Implement this target"})
        self.store.create_object(object_id="R-safe",object_type="run",project_id="PROJECT-test")
        run_request=self.store.create_herdr_launch_request(**{**base,"object_id":"HLR-run","target_object_id":"R-safe","agent_kind":"pi","task_type":"run_implementation","task_summary":"Implement and debug the approved Run"})
        self.assertEqual(run_request["task_type"],"run_implementation")

    def test_herdr_execution_authorization_snapshot_duplicate_and_revoke(self):
        self.store.initialize(); capability={"managed":True,"cli_available":True,"codex_supported":True}
        self.store.create_object(object_id="Q-exec",object_type="question",project_id="PROJECT-test")
        self.store.create_herdr_launch_request(object_id="HLR-exec",project_id="PROJECT-test",target_object_id="Q-exec",agent_kind="codex",task_type="analysis",task_summary="Review evidence",safe_config={"reasoning_effort":"high","max_turns":4})
        self.store.transition_herdr_launch_request("HLR-exec",expected_revision=1,status="awaiting_approval")
        request=self.store.transition_herdr_launch_request("HLR-exec",expected_revision=2,status="approved")
        with self.assertRaisesRegex(ValueError,"capability preflight"):
            self.store.authorize_herdr_execution(execution_id="HEX-off",project_id="PROJECT-test",launch_request_id="HLR-exec",expected_request_revision=request["revision"],capability={"managed":False,"cli_available":True,"codex_supported":True})
        with self.assertRaisesRegex(ValueError,"revision conflict"):
            self.store.authorize_herdr_execution(execution_id="HEX-stale",project_id="PROJECT-test",launch_request_id="HLR-exec",expected_request_revision=2,capability=capability)
        execution=self.store.authorize_herdr_execution(execution_id="HEX-one",project_id="PROJECT-test",launch_request_id="HLR-exec",expected_request_revision=3,capability=capability,ttl_seconds=120)
        self.assertEqual(execution["state"],"authorized"); self.assertEqual(execution["approved_request_revision"],3); self.assertEqual(execution["attempt"],0)
        self.assertTrue(execution["approved_snapshot_hash"].startswith("sha256:"))
        self.assertEqual(execution["safe_runtime"],{"execution_started":False,"herdr_invoked":False,"phase":"record_only"})
        with self.assertRaisesRegex(ValueError,"active Herdr execution"):
            self.store.authorize_herdr_execution(execution_id="HEX-two",project_id="PROJECT-test",launch_request_id="HLR-exec",expected_request_revision=3,capability=capability)
        with self.assertRaisesRegex(ValueError,"revision conflict"):
            self.store.revoke_herdr_execution("HEX-one",expected_revision=2)
        revoked=self.store.revoke_herdr_execution("HEX-one",expected_revision=1)
        self.assertEqual(revoked["state"],"revoked"); self.assertEqual(revoked["revision"],2)
        events=self.store.list_events("HEX-one")
        self.assertEqual([item["kind"] for item in events],["herdr_execution.authorized","herdr_execution.revoked"])
        self.assertNotIn("nonce",repr(events).lower())
        repeated=self.store.authorize_herdr_execution(execution_id="HEX-repeat",project_id="PROJECT-test",launch_request_id="HLR-exec",expected_request_revision=3,capability=capability)
        self.assertEqual(repeated["approved_snapshot_hash"],execution["approved_snapshot_hash"])

    def test_herdr_execution_rejects_unapproved_and_archived_targets(self):
        self.store.initialize(); capability={"managed":True,"cli_available":True,"codex_supported":True}
        self.store.create_object(object_id="Q-archived",object_type="question",project_id="PROJECT-test",lifecycle_status="archived")
        self.store.create_herdr_launch_request(object_id="HLR-archived",project_id="PROJECT-test",target_object_id="Q-archived",agent_kind="codex",task_type="research",task_summary="Review archive")
        with self.assertRaisesRegex(ValueError,"must be approved"):
            self.store.authorize_herdr_execution(execution_id="HEX-draft",project_id="PROJECT-test",launch_request_id="HLR-archived",expected_request_revision=1,capability=capability)
        self.store.transition_herdr_launch_request("HLR-archived",expected_revision=1,status="awaiting_approval")
        self.store.transition_herdr_launch_request("HLR-archived",expected_revision=2,status="approved")
        with self.assertRaisesRegex(ValueError,"archived launch target"):
            self.store.authorize_herdr_execution(execution_id="HEX-archived",project_id="PROJECT-test",launch_request_id="HLR-archived",expected_request_revision=3,capability=capability)

    def test_herdr_execution_atomic_claim_lease_heartbeat_and_safe_finish(self):
        execution,_,_,authorized,capability=self.authorized_execution("claim")
        def claim():
            try: return V2Store(self.root).claim_herdr_execution(execution,expected_revision=authorized["revision"],owner="executor-one",capability=capability,lease_seconds=30)
            except Exception as error: return error
        with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(lambda _item:claim(),range(2)))
        claims=[item for item in results if isinstance(item,dict)]; failures=[item for item in results if isinstance(item,Exception)]
        self.assertEqual(len(claims),1); self.assertEqual(len(failures),1)
        claimed=claims[0]; token=claimed["lease_token"]; row=claimed["execution"]
        self.assertEqual(row["state"],"claimed"); self.assertEqual(row["attempt"],1); self.assertEqual(row["revision"],2)
        self.assertNotEqual(row["lease_token_hash"],token); self.assertEqual(row["lease_token_hash"],__import__("hashlib").sha256(token.encode()).hexdigest())
        with self.assertRaisesRegex(ValueError,"token or owner mismatch"): self.store.heartbeat_herdr_execution(execution,lease_token="wrong",owner="executor-one")
        with self.assertRaisesRegex(ValueError,"token or owner mismatch"): self.store.finish_herdr_preflight(execution,lease_token=token,owner="executor-two",status="completed")
        heartbeat=self.store.heartbeat_herdr_execution(execution,lease_token=token,owner="executor-one",lease_seconds=45)
        self.assertEqual(heartbeat["revision"],3)
        after_lease=dt.datetime.fromisoformat(heartbeat["lease_expires_at"])+dt.timedelta(seconds=1)
        with self.assertRaisesRegex(ValueError,"lease has expired"):
            self.store.finish_herdr_preflight(execution,lease_token=token,owner="executor-one",status="completed",now=after_lease)
        with self.assertRaisesRegex(ValueError,"unsupported execution runtime"):
            self.store.finish_herdr_preflight(execution,lease_token=token,owner="executor-one",status="completed",runtime={"prompt":"forbidden"})
        finished=self.store.finish_herdr_preflight(execution,lease_token=token,owner="executor-one",status="completed",runtime={"checks":{"authorization_current":True},"duration_ms":12})
        self.assertEqual(finished["state"],"completed"); self.assertEqual(finished["revision"],4); self.assertEqual(finished["lease_token_hash"],""); self.assertEqual(finished["lease_owner"],"")
        self.assertEqual(finished["safe_runtime"]["execution_started"],False); self.assertLessEqual(len(__import__("json").dumps(finished["safe_runtime"])),2000)

    def test_herdr_execution_claim_rechecks_all_authorization_gates(self):
        execution,request,target,row,capability=self.authorized_execution("gates",ttl_seconds=60)
        with self.assertRaisesRegex(ValueError,"capability preflight"):
            self.store.claim_herdr_execution(execution,expected_revision=1,owner="executor",capability={**capability,"codex_supported":False})
        expired=dt.datetime.fromisoformat(row["not_after"])+dt.timedelta(seconds=1)
        with self.assertRaisesRegex(ValueError,"authorization has expired"):
            self.store.claim_herdr_execution(execution,expected_revision=1,owner="executor",capability=capability,now=expired)
        self.store.update_object(request,expected_revision=3,fields={"title":"changed"})
        with self.assertRaisesRegex(ValueError,"revision/status changed"):
            self.store.claim_herdr_execution(execution,expected_revision=1,owner="executor",capability=capability)
        with self.store.transaction() as conn: conn.execute("UPDATE objects SET revision=3 WHERE id=?",(request,)); conn.execute("UPDATE herdr_launch_requests SET task_summary='tampered' WHERE object_id=?",(request,))
        with self.assertRaisesRegex(ValueError,"snapshot changed"):
            self.store.claim_herdr_execution(execution,expected_revision=1,owner="executor",capability=capability)
        with self.store.transaction() as conn: conn.execute("UPDATE herdr_launch_requests SET task_summary='Review evidence gates' WHERE object_id=?",(request,)); conn.execute("UPDATE objects SET lifecycle_status='archived' WHERE id=?",(target,))
        with self.assertRaisesRegex(ValueError,"archived"):
            self.store.claim_herdr_execution(execution,expected_revision=1,owner="executor",capability=capability)

    def test_herdr_execution_concurrency_and_expired_lease_observations(self):
        first,_,_,_,capability=self.authorized_execution("concurrency-one")
        second,_,_,_,_=self.authorized_execution("concurrency-two")
        first_claim=self.store.claim_herdr_execution(first,expected_revision=1,owner="executor-one",capability=capability,lease_seconds=15)
        with self.assertRaisesRegex(ValueError,"concurrency limit"):
            self.store.claim_herdr_execution(second,expected_revision=1,owner="executor-two",capability=capability)
        claimed_at=dt.datetime.fromisoformat(first_claim["execution"]["lease_expires_at"])
        with self.assertRaisesRegex(ValueError,"not expired"):
            self.store.reconcile_expired_herdr_execution(first,expected_revision=2,ownership_observation="absent",now=claimed_at-dt.timedelta(seconds=1))
        # A new launch automatically recovers an expired pre-start claim: it
        # owns no Herdr resource and must not block unrelated execution.
        auto_recovered=self.store.claim_herdr_execution(second,expected_revision=1,owner="executor-two",capability=capability,now=claimed_at+dt.timedelta(seconds=1))
        self.assertEqual(auto_recovered["execution"]["state"],"claimed")
        first_after=self.store.get_herdr_execution(first); self.assertEqual(first_after["state"],"authorized"); self.assertEqual(first_after["lease_token_hash"],"")
        self.store.finish_herdr_preflight(second,lease_token=auto_recovered["lease_token"],owner="executor-two",status="completed",now=claimed_at+dt.timedelta(seconds=2))
        for suffix,observation in (("live","live"),("ambiguous","ambiguous")):
            execution,_,_,_,_=self.authorized_execution(suffix)
            claim=self.store.claim_herdr_execution(execution,expected_revision=1,owner=f"executor-{suffix}",capability=capability,lease_seconds=15)
            expiry=dt.datetime.fromisoformat(claim["execution"]["lease_expires_at"])+dt.timedelta(seconds=1)
            reconciled=self.store.reconcile_expired_herdr_execution(execution,expected_revision=2,ownership_observation=observation,now=expiry)
            self.assertEqual(reconciled["state"],"attention_required"); self.assertIsNotNone(reconciled["terminal_at"]); self.assertEqual(reconciled["safe_runtime"]["ownership_observation"],observation)

    def test_automation_budget_and_human_activation_gate(self):
        self.store.initialize()
        automation = self.store.create_automation(
            object_id="AUTO-001", project_id="PROJECT-test", title="Bounded research", automation_type="research",
            target_type="question", target_id="Q-001", budget={"duration_minutes": 30, "max_rounds": 5, "interval_minutes": 2},
        )
        self.assertEqual(automation["lifecycle_status"], "draft")
        awaiting = self.store.transition_automation("AUTO-001", expected_revision=1, status="awaiting_approval")
        with self.assertRaisesRegex(ValueError, "human approval"):
            self.store.transition_automation("AUTO-001", expected_revision=2, status="active", phase="research")
        active = self.store.transition_automation("AUTO-001", expected_revision=2, status="active", phase="research", approval={"approved_by": "human:test"})
        self.assertEqual(active["phase"], "research")
        self.assertIsNotNone(active["deadline_at"])
        deadline = __import__("datetime").datetime.fromisoformat(active["deadline_at"])
        started = __import__("datetime").datetime.fromisoformat(active["started_at"])
        self.assertEqual((deadline - started).total_seconds(), 30 * 60)
        checkpoint = self.store.transition_automation("AUTO-001", expected_revision=3, status="checkpoint", phase="research_review")
        self.assertEqual(checkpoint["lifecycle_status"], "checkpoint")
        self.assertEqual(len(self.store.list_automations()), 1)
        with self.assertRaisesRegex(ValueError, "max_rounds"):
            self.store.create_automation(object_id="AUTO-bad", project_id="PROJECT-test", title="Bad", automation_type="research", target_type="question", target_id="Q-1", budget={"duration_minutes": 30, "max_rounds": 0, "interval_minutes": 1})

    def test_hybrid_automation_requires_separate_experiment_approval(self):
        self.store.initialize()
        self.store.create_automation(
            object_id="AUTO-hybrid", project_id="PROJECT-test", title="Hybrid", automation_type="hybrid",
            target_type="question", target_id="Q-001", budget={"duration_minutes": 60, "max_rounds": 5, "interval_minutes": 1},
        )
        self.store.transition_automation("AUTO-hybrid", expected_revision=1, status="awaiting_approval")
        active = self.store.transition_automation("AUTO-hybrid", expected_revision=2, status="active", phase="research", approval={"approved_by": "human:test"})
        self.store.transition_automation("AUTO-hybrid", expected_revision=active["revision"], status="checkpoint", phase="research_review")
        with self.assertRaisesRegex(ValueError, "separate human approval"):
            self.store.transition_automation("AUTO-hybrid", expected_revision=4, status="active", phase="experiment_planning")
        resumed = self.store.transition_automation("AUTO-hybrid", expected_revision=4, status="active", phase="experiment_planning", approval={"experiment_phase_approved_by": "human:test"})
        self.assertEqual(resumed["phase"], "experiment_planning")

    def test_archive_is_soft_audited_reversible_and_atomic(self):
        self.store.initialize()
        for index in (1,2):
            self.store.create_paper_candidate(object_id=f"PC-archive-{index}",project_id="PROJECT-test",citekey=f"archive{index}",title=f"Candidate {index}",source_url=f"https://openalex.org/W{index}")
        self.store.update_paper_candidate_status("PC-archive-1",expected_revision=1,lifecycle_status="dismissed")
        archived = self.store.archive_objects([{"id":"PC-archive-1","expected_revision":2},{"id":"PC-archive-2","expected_revision":1}],reason="No longer active",actor_id="reviewer")
        self.assertEqual([item["lifecycle_status"] for item in archived],["archived","archived"])
        event=self.store.list_events("PC-archive-1")[-1]; self.assertFalse(event["details"]["hard_delete"]); self.assertEqual(event["details"]["previous_status"],"dismissed")
        restored=self.store.archive_objects([{"id":"PC-archive-1","expected_revision":3}],reason="Reopened",actor_id="reviewer",restore=True)
        self.assertEqual(restored[0]["lifecycle_status"],"dismissed")
        with self.assertRaisesRegex(ValueError,"revision conflict"):
            self.store.archive_objects([{"id":"PC-archive-1","expected_revision":4},{"id":"PC-archive-2","expected_revision":1}],reason="Atomic conflict")
        self.assertEqual(self.store.get_object("PC-archive-1")["lifecycle_status"],"dismissed"); self.assertEqual(self.store.get_object("PC-archive-2")["lifecycle_status"],"archived")

    def test_archive_impact_blocks_legacy_active_automation_and_active_jobs(self):
        self.store.initialize(); self.store.create_object(object_id="RUN-legacy",object_type="run",project_id="PROJECT-test")
        self.store.create_automation(object_id="AUTO-archive",project_id="PROJECT-test",title="Active",automation_type="research",target_type="question",target_id="Q-1",budget={"duration_minutes":30,"max_rounds":5,"interval_minutes":1})
        self.store.transition_automation("AUTO-archive",expected_revision=1,status="awaiting_approval")
        candidate=self.store.create_paper_candidate(object_id="PC-busy",project_id="PROJECT-test",citekey="busy",title="Busy",source_url="https://openalex.org/busy")
        self.store.create_job(kind="paper_download",target_object_id=candidate["id"],idempotency_key="busy")
        impacts={item["id"]:item for item in self.store.archive_impact(["RUN-legacy","AUTO-archive","PC-busy"])}
        self.assertIn("only native",impacts["RUN-legacy"]["blockers"][0]); self.assertIn("awaiting_approval",impacts["AUTO-archive"]["blockers"][0]); self.assertIn("queued/running",impacts["PC-busy"]["blockers"][0])
        with self.assertRaisesRegex(ValueError,"archive blocked"):
            self.store.archive_objects([{"id":"PC-busy","expected_revision":1}],reason="unsafe")
        with self.assertRaisesRegex(ValueError,"reason"):
            self.store.archive_objects([{"id":"RUN-legacy","expected_revision":1}],reason="")

    def test_inbox_is_an_idempotent_projection(self):
        self.store.initialize()
        self.store.create_object(
            object_id="PC-001",
            object_type="paper_candidate",
            project_id="PROJECT-test",
            title="Candidate",
        )
        first = self.store.create_inbox_item(
            kind="candidate_review",
            target_object_id="PC-001",
            title="Review candidate",
        )
        second = self.store.create_inbox_item(
            kind="candidate_review",
            target_object_id="PC-001",
            title="Duplicate request",
        )
        self.assertEqual(first["id"], second["id"])
        self.assertEqual(len(self.store.list_inbox()), 1)

    def test_paper_candidate_lifecycle_and_job_linkage(self):
        self.store.initialize()
        candidate = self.store.create_paper_candidate(
            object_id="PC-001",
            project_id="PROJECT-test",
            citekey="doe2026paper",
            title="Candidate Paper",
            source_url="https://openalex.org/W1",
            authors=["Jane Doe"],
            year="2026",
            source="openalex",
            recommendation_reason="Matches the active question",
        )
        self.assertEqual(candidate["authors"], ["Jane Doe"])
        self.assertEqual(candidate["lifecycle_status"], "proposed")
        job = self.store.create_job(
            kind="paper_download", target_object_id="PC-001", idempotency_key="PC-001-download"
        )
        linked = self.store.attach_candidate_job("PC-001", job["id"])
        self.assertEqual(linked["acquisition_job_id"], job["id"])
        accepted = self.store.update_paper_candidate_status(
            "PC-001", expected_revision=1, lifecycle_status="accepted"
        )
        self.assertEqual(accepted["lifecycle_status"], "accepted")
        self.assertEqual(len(self.store.list_paper_candidates()), 1)

    def test_candidate_acquisition_pipeline_is_staged_dependent_and_idempotent(self):
        self.store.initialize()
        candidate = self.store.create_paper_candidate(
            object_id="PC-pipeline", project_id="PROJECT-test", citekey="pipe2026paper",
            title="Pipeline", source_url="https://openalex.org/W2", oa_url="https://example.org/paper.pdf",
        )
        pipeline = self.store.create_candidate_acquisition_pipeline("PC-pipeline", expected_revision=candidate["revision"], actor_id="reviewer")
        self.assertEqual(pipeline["candidate"]["lifecycle_status"], "accepted")
        self.assertEqual(pipeline["download_job"]["request"]["destination"], "staging")
        self.assertEqual(pipeline["mineru_job"]["depends_on_job_id"], pipeline["download_job"]["id"])
        self.assertNotIn("ingest", pipeline["download_job"]["request"])
        repeated = self.store.create_candidate_acquisition_pipeline("PC-pipeline", expected_revision=2, actor_id="reviewer")
        self.assertEqual(repeated["download_job"]["id"], pipeline["download_job"]["id"])
        self.assertEqual(len(self.store.list_jobs(target_object_id="PC-pipeline")), 2)
        event = self.store.list_events("PC-pipeline")[-1]
        self.assertFalse(event["details"]["canonical_write"])

    def test_candidate_pipeline_requires_oa_pdf_and_current_revision(self):
        self.store.initialize()
        candidate = self.store.create_paper_candidate(
            object_id="PC-no-oa", project_id="PROJECT-test", citekey="nooa2026paper",
            title="No OA", source_url="https://openalex.org/W3",
        )
        with self.assertRaisesRegex(ValueError, "OA PDF"):
            self.store.create_candidate_acquisition_pipeline("PC-no-oa", expected_revision=candidate["revision"])
        with self.assertRaisesRegex(ValueError, "revision conflict"):
            self.store.create_candidate_acquisition_pipeline("PC-no-oa", expected_revision=99)

    def test_zotero_candidate_pipeline_uses_local_copy_job(self):
        self.store.initialize()
        candidate=self.store.create_paper_candidate(object_id="PC-zotero",project_id="PROJECT-test",citekey="local2026",title="Local",source_url="https://www.zotero.org/items/42",source="zotero-local")
        pipeline=self.store.create_candidate_acquisition_pipeline("PC-zotero",expected_revision=candidate["revision"])
        self.assertEqual(pipeline["download_job"]["kind"],"zotero_copy")
        self.assertEqual(pipeline["download_job"]["request"]["item_id"],42)
        self.assertNotIn("url",pipeline["download_job"]["request"])
        self.assertEqual(pipeline["mineru_job"]["depends_on_job_id"],pipeline["download_job"]["id"])

    def test_candidate_rejects_untrusted_url_and_duplicate_source(self):
        self.store.initialize()
        with self.assertRaisesRegex(ValueError, "http"):
            self.store.create_paper_candidate(
                object_id="PC-bad", project_id="PROJECT-test", citekey="bad2026paper",
                title="Bad", source_url="file:///etc/passwd",
            )
        self.store.create_paper_candidate(
            object_id="PC-001", project_id="PROJECT-test", citekey="one2026paper",
            title="One", source_url="https://openalex.org/W1",
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.create_paper_candidate(
                object_id="PC-002", project_id="PROJECT-test", citekey="two2026paper",
                title="Two", source_url="https://openalex.org/W1",
            )

    def test_store_rejects_unknown_object_type_and_oversized_metadata(self):
        self.store.initialize()
        with self.assertRaisesRegex(ValueError, "invalid object_type"):
            self.store.create_object(
                object_id="X-001", object_type="unknown", project_id="PROJECT-test"
            )
        self.store.create_object(
            object_id="P-001", object_type="paper", project_id="PROJECT-test"
        )
        self.store.create_object(
            object_id="Q-001", object_type="question", project_id="PROJECT-test"
        )
        with self.assertRaisesRegex(ValueError, "exceeds 64 KiB"):
            self.store.add_relation(
                from_object_id="Q-001",
                relation_type="discusses",
                to_object_id="P-001",
                metadata={"large": "x" * (65 * 1024)},
            )


if __name__ == "__main__":
    unittest.main()
