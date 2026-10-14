import json
import pathlib
import tempfile
import unittest

from survey_tool.v2 import V2Store
from survey_tool.v2.migration import (
    apply_content_index_migration,
    apply_identity_index_migration,
    build_content_index_plan,
    build_identity_index_plan,
    build_migration_inventory,
    content_index_history,
    identity_index_history,
    refresh_v2_index,
)


class V2MigrationInventoryTest(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp(prefix="v2-migration-"))
        (self.root / "kernel").mkdir(); (self.root / ".survey-tool").mkdir(); (self.root / "papers").mkdir(); (self.root / ".publish/kernel").mkdir(parents=True)
        (self.root / "state.md").write_text("state: TEST\n", encoding="utf-8")
        (self.root / "kernel/citations.md").write_text("## [a2026]\n- content_hash: sha256:x\n", encoding="utf-8")
        (self.root / "kernel/claims.md").write_text("## [C01] Claim\n", encoding="utf-8")
        (self.root / ".survey-tool/experiments.json").write_text(json.dumps({"experiments": [{"id": "E-1"}]}), encoding="utf-8")
        (self.root / ".survey-tool/runs.json").write_text("{broken", encoding="utf-8")
        (self.root / "papers/a.pdf").write_bytes(b"%PDF-test")
        (self.root / ".publish/kernel/citations.md").write_text("## [mirror]\n", encoding="utf-8")

    def test_inventory_is_read_only_hashed_and_excludes_publish_mirror(self):
        before = sorted(path.relative_to(self.root) for path in self.root.rglob("*"))
        result = build_migration_inventory(self.root)
        after = sorted(path.relative_to(self.root) for path in self.root.rglob("*"))
        self.assertEqual(before, after)
        self.assertFalse(result["will_write"])
        self.assertFalse(result["v2_store"]["initialized"])
        self.assertFalse((self.root / ".survey-tool/survey-tool-v2.sqlite3").exists())
        self.assertEqual(result["papers"]["records"], 1)
        self.assertTrue(result["papers"]["files"][0]["sha256"].startswith("sha256:"))
        scanned_paths = [item["path"] for source in result["sources"] for item in source["files"]] + [item["path"] for item in result["papers"]["files"]]
        self.assertFalse(any(path.startswith(".publish/") for path in scanned_paths))
        self.assertTrue(any(warning["kind"] == "excluded_mirror" for warning in result["warnings"]))

    def test_identity_apply_indexes_only_identity_and_explicit_relations(self):
        questions=self.root/"shell/01_questions"; questions.mkdir(parents=True)
        question=questions/"Q-001.md"; original="---\nid: Q-001\ntitle: Why?\nexperiments:\n  - EXP-001\n---\n# Why\n\nprivate prose\n"; question.write_text(original,encoding="utf-8")
        (self.root/".survey-tool/experiments.json").write_text(json.dumps([{"id":"EXP-001","title":"Test"}]),encoding="utf-8")
        plan=build_identity_index_plan(self.root); self.assertEqual(plan["summary"],{"questions":1,"experiments":1,"relations":1,"warnings":0})
        V2Store(self.root).initialize(); result=apply_identity_index_migration(self.root,actor_id="test")
        self.assertEqual(result["created"],2); self.assertEqual(result["relations_created"],1); self.assertFalse(result["authority_changed"]); self.assertFalse(result["prose_copied"]); self.assertEqual(question.read_text(encoding="utf-8"),original)
        store=V2Store(self.root); self.assertEqual(store.get_object("Q-001")["canonical_path"],"shell/01_questions/Q-001.md"); self.assertEqual(store.get_object("EXP-001")["lifecycle_status"],"reference"); self.assertEqual(len(store.list_relations(from_object_id="Q-001")),1)
        again=apply_identity_index_migration(self.root,actor_id="test"); self.assertEqual(again["created"],0); self.assertEqual(again["existing"],2); self.assertEqual(again["relations_created"],0)
        history=identity_index_history(self.root); self.assertEqual(len(history),1); self.assertEqual(history[0]["checkpoint_hash"],again["checkpoint_hash"]); self.assertEqual(history[0]["details"]["existing"],2)

    def test_identity_plan_reports_existing_store_conflict_before_apply(self):
        questions=self.root/"shell/01_questions"; questions.mkdir(parents=True)
        (questions/"Q-conflict.md").write_text("---\nid: Q-conflict\ntitle: Conflict\n---\nbody\n",encoding="utf-8")
        store=V2Store(self.root); store.initialize(); store.create_object(object_id="Q-conflict",object_type="experiment",project_id="PROJECT-test",canonical_path="")
        plan=build_identity_index_plan(self.root)
        self.assertTrue(plan["blocked"])
        conflict=next(item for item in plan["warnings"] if item["kind"]=="existing_identity_conflict")
        self.assertEqual(conflict["path"],"Q-conflict"); self.assertIn("type is 'experiment'",conflict["message"]); self.assertIn("canonical_path",conflict["message"])

    def test_invalid_registry_is_reported_not_silently_zeroed(self):
        result = build_migration_inventory(self.root)
        runs = next(source for source in result["sources"] if source["name"] == "runs")
        self.assertEqual(runs["files"][0]["parse_status"], "invalid")
        self.assertEqual(runs["records"], 0)
        self.assertTrue(any(warning["kind"] == "parse_error" and warning["path"].endswith("runs.json") for warning in result["warnings"]))


class V2ContentIndexMigrationTest(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp(prefix="v2-content-migration-"))
        (self.root / "kernel").mkdir(); (self.root / ".survey-tool").mkdir(); (self.root / "papers").mkdir()
        (self.root / "papers" / "Test Paper_2024.pdf").write_bytes(b"%PDF-test-paper")
        (self.root / "papers" / "Other Paper_2025.pdf").write_bytes(b"%PDF-other-paper")
        (self.root / ".survey-tool" / "compares.json").write_text(json.dumps([
            {"id": "cmp-test", "name": "Test Comparison", "papers": ["testpape2024", "otherpap2025"]},
        ]), encoding="utf-8")
        findings = self.root / "shell" / "04_comparisons" / "findings"; findings.mkdir(parents=True)
        (findings / "F-001.md").write_text("---\nid: F-001\ntitle: Test finding\ncomparison: cmp-test\n---\nbody\n", encoding="utf-8")
        (self.root / "kernel" / "claims.md").write_text("## C01\n- text: Test claim\n- citekey: testpape2024\n- status: draft\n", encoding="utf-8")

    def test_plan_indexes_papers_comparisons_findings_claims_with_relations(self):
        plan = build_content_index_plan(self.root)
        self.assertFalse(plan["blocked"])
        self.assertEqual(plan["summary"], {"papers": 2, "comparisons": 1, "findings": 1, "claims": 1, "relations": 4, "warnings": 0})
        self.assertEqual(plan["authority"]["claim"], "kernel_gate")
        paper = next(item for item in plan["objects"] if item["id"] == "testpape2024")
        self.assertEqual(paper["canonical_path"], "papers/Test Paper_2024.pdf")
        kinds = sorted(item["relation_type"] for item in plan["relations"])
        self.assertEqual(kinds, ["compares", "compares", "derived_from", "derived_from"])

    def test_apply_indexes_only_identity_and_does_not_modify_canonical(self):
        claims_path = self.root / "kernel" / "claims.md"
        finding_path = self.root / "shell" / "04_comparisons" / "findings" / "F-001.md"
        claims_before = claims_path.read_text(encoding="utf-8")
        finding_before = finding_path.read_text(encoding="utf-8")
        V2Store(self.root).initialize()
        result = apply_content_index_migration(self.root, actor_id="test")
        self.assertEqual(result["created"], 5)
        self.assertEqual(result["relations_created"], 4)
        self.assertFalse(result["authority_changed"]); self.assertFalse(result["prose_copied"]); self.assertFalse(result["canonical_files_modified"])
        self.assertEqual(claims_path.read_text(encoding="utf-8"), claims_before)
        self.assertEqual(finding_path.read_text(encoding="utf-8"), finding_before)
        store = V2Store(self.root)
        self.assertEqual(store.get_object("testpape2024")["lifecycle_status"], "reference")
        self.assertEqual(store.get_object("cmp-test")["type"], "comparison")
        self.assertEqual(len(store.list_relations(from_object_id="cmp-test")), 2)
        again = apply_content_index_migration(self.root, actor_id="test")
        self.assertEqual(again["created"], 0); self.assertEqual(again["existing"], 5); self.assertEqual(again["relations_created"], 0)
        history = content_index_history(self.root)
        self.assertEqual(len(history), 1); self.assertEqual(history[0]["checkpoint_hash"], again["checkpoint_hash"])

    def test_plan_reports_conflict_when_id_already_bound_to_other_type(self):
        store = V2Store(self.root); store.initialize()
        store.create_object(object_id="testpape2024", object_type="experiment", project_id="PROJECT-test", canonical_path="")
        plan = build_content_index_plan(self.root)
        self.assertTrue(plan["blocked"])
        self.assertTrue(any(item["kind"] == "existing_identity_conflict" and item["path"] == "testpape2024" for item in plan["warnings"]))

    def test_missing_paper_target_skips_relation_without_blocking(self):
        (self.root / ".survey-tool" / "compares.json").write_text(json.dumps([
            {"id": "cmp-test", "name": "Test", "papers": ["testpape2024", "missing2026"]},
        ]), encoding="utf-8")
        plan = build_content_index_plan(self.root)
        self.assertFalse(plan["blocked"])
        self.assertEqual(plan["summary"]["relations"], 3)
        self.assertTrue(any(item["kind"] == "missing_relation_target" and "missing2026" in item["message"] for item in plan["warnings"]))

    def test_no_pdf_catalog_row_is_indexed_as_reference_paper(self):
        (self.root / "papers" / "INDEX.md").write_text(
            "| # | Title | Date | Venue | DOI/URL | File |\n"
            "|---|-------|------|-------|---------|------|\n"
            "| 1 | PromptHub: Enhancing Multi-Prompt | 2026-03-19 2026-03-19 |  | doi:x | ⚠️ no local PDF |\n",
            encoding="utf-8",
        )
        plan = build_content_index_plan(self.root)
        papers = [item for item in plan["objects"] if item["type"] == "paper"]
        self.assertEqual(len(papers), 3)
        no_pdf = next(item for item in papers if item["canonical_path"] == "")
        self.assertEqual(no_pdf["id"], "prompthu2026")
        self.assertEqual(no_pdf["title"], "PromptHub: Enhancing Multi-Prompt")


class V2IndexRefreshTest(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp(prefix="v2-index-refresh-"))
        (self.root / "kernel").mkdir(); (self.root / ".survey-tool").mkdir(); (self.root / "papers").mkdir()
        (self.root / "papers" / "Test Paper_2024.pdf").write_bytes(b"%PDF-test-paper")
        (self.root / "papers" / "Other Paper_2025.pdf").write_bytes(b"%PDF-other-paper")
        (self.root / ".survey-tool" / "compares.json").write_text(json.dumps([
            {"id": "cmp-test", "name": "Test Comparison", "papers": ["testpape2024", "otherpap2025"]},
        ]), encoding="utf-8")
        findings = self.root / "shell" / "04_comparisons" / "findings"; findings.mkdir(parents=True)
        (findings / "F-001.md").write_text("---\nid: F-001\ntitle: Test finding\ncomparison: cmp-test\n---\nbody\n", encoding="utf-8")
        (self.root / "kernel" / "claims.md").write_text("## C01\n- text: Test claim\n- citekey: testpape2024\n- status: draft\n", encoding="utf-8")

    def test_uninitialized_store_is_skipped_without_creation(self):
        result = refresh_v2_index(self.root)
        self.assertEqual(result, {"status": "skipped", "reason": "v2 store not initialized"})
        self.assertFalse(V2Store(self.root).exists())

    def test_initialized_refresh_is_idempotent(self):
        V2Store(self.root).initialize()
        first = refresh_v2_index(self.root, actor_id="test")
        second = refresh_v2_index(self.root, actor_id="test")
        self.assertEqual(first["status"], "ok")
        self.assertEqual(first["content"]["created"], 5)
        self.assertEqual(second["identity"]["created"], 0)
        self.assertEqual(second["content"]["created"], 0)
        self.assertGreater(second["content"]["existing"], first["content"]["existing"])

    def test_blocked_plan_returns_warnings_without_raising(self):
        store = V2Store(self.root); store.initialize()
        store.create_object(object_id="testpape2024", object_type="experiment", project_id="PROJECT-test", canonical_path="")
        result = refresh_v2_index(self.root, identity=False)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["content"]["status"], "blocked")
        self.assertTrue(any(item["kind"] == "existing_identity_conflict" for item in result["warnings"]))


if __name__ == "__main__": unittest.main()
