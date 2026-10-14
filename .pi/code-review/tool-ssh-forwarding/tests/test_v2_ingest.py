import pathlib
import tempfile
import unittest

from survey_tool.v2.ingest import ingest_staged_candidate
from survey_tool.v2.store import V2Store


class V2IngestTest(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp(prefix="v2-ingest-"))
        self.store = V2Store(self.root); self.store.initialize()
        candidate = self.store.create_paper_candidate(
            object_id="PC-001", project_id="PROJECT-test", citekey="paper2026",
            title="Canonical Paper", year="2026", source_url="https://openalex.org/W1", oa_url="https://example.org/paper.pdf",
        )
        pipeline = self.store.create_candidate_acquisition_pipeline("PC-001", expected_revision=candidate["revision"])
        pdf = self.root / ".survey-tool/staging/PC-001/paper2026.pdf"; pdf.parent.mkdir(parents=True); pdf.write_bytes(b"%PDF-test")
        md = self.root / ".survey-tool/staging/PC-001/mineru/paper/hybrid_auto/paper.md"; md.parent.mkdir(parents=True); md.write_text("parsed", encoding="utf-8")
        download = self.store.claim_next_job(worker_id="worker")
        self.store.finish_claimed_job(download["id"], lease_token=download["lease_token"], succeeded=True, result={"staged_pdf": str(pdf.relative_to(self.root))})
        mineru = self.store.claim_next_job(worker_id="worker")
        self.store.finish_claimed_job(mineru["id"], lease_token=mineru["lease_token"], succeeded=True, result={"staged_mineru_dir": str((md.parents[2]).relative_to(self.root)), "markdown": str(md.relative_to(self.root))})

    def runner(self, pdf, candidate):
        import hashlib
        digest = "sha256:" + hashlib.sha256(pdf.read_bytes()).hexdigest()
        citations = self.root / "kernel/citations.md"; citations.parent.mkdir(parents=True, exist_ok=True); citations.write_text(f"## [{candidate['citekey']}]\n- content_hash: {digest}\n", encoding="utf-8")
        note = self.root / "shell/03_evidence/papers" / f"{candidate['citekey']}.md"; note.parent.mkdir(parents=True, exist_ok=True); note.write_text("note", encoding="utf-8")
        return {"ok": True, "content_hash": digest}

    def test_ingest_requires_successful_pipeline_and_promotes_with_hash(self):
        result = ingest_staged_candidate(self.root, self.store, "PC-001", expected_revision=2, actor_id="reviewer", ingest_runner=self.runner)
        self.assertEqual(result["verification_status"], "ingested")
        self.assertTrue(result["content_hash"].startswith("sha256:"))
        self.assertTrue((self.root / result["canonical_paper_path"]).is_file())
        self.assertTrue((self.root / "papers/Canonical Paper_2026/hybrid_auto/paper.md").is_file())
        self.assertTrue((self.root / "kernel/citations.md").is_file())
        self.assertEqual(self.store.list_events("PC-001")[-1]["kind"], "paper_candidate.ingested")
        reference = self.store.get_object(result["citekey"])
        self.assertEqual(reference["type"], "paper")
        self.assertEqual(reference["title"], result["title"])
        self.assertEqual(reference["canonical_path"], result["canonical_paper_path"])
        self.assertEqual(self.store.index_ingested_papers(), {"indexed":0,"already_indexed":1})

    def test_backfill_indexes_old_ingests_without_promoting_candidates(self):
        with self.store.transaction() as conn:
            conn.execute("UPDATE paper_candidates SET verification_status='ingested',canonical_paper_path='papers/old.pdf' WHERE object_id='PC-001'")
        self.assertEqual(self.store.index_ingested_papers(), {"indexed":1,"already_indexed":0})
        self.assertEqual(len(self.store.list_objects(object_type="paper")), 1)

    def test_index_conflict_rolls_back_ingest(self):
        candidate = self.store.get_paper_candidate("PC-001")
        self.store.create_object(object_id=candidate["citekey"],object_type="question",project_id="PROJECT-test",title="Unrelated")
        with self.assertRaisesRegex(ValueError, "identity conflict"):
            ingest_staged_candidate(self.root,self.store,"PC-001",expected_revision=2,actor_id="reviewer",ingest_runner=self.runner)
        self.assertNotEqual(self.store.get_paper_candidate("PC-001")["verification_status"], "ingested")
        self.assertFalse((self.root / "papers/Canonical Paper_2026.pdf").exists())

    def test_ingest_refuses_conflict_without_overwrite(self):
        existing = self.root / "papers/Canonical Paper_2026.pdf"; existing.parent.mkdir(); existing.write_bytes(b"original")
        with self.assertRaisesRegex(FileExistsError, "already exists"):
            ingest_staged_candidate(self.root, self.store, "PC-001", expected_revision=2, actor_id="reviewer", ingest_runner=self.runner)
        self.assertEqual(existing.read_bytes(), b"original")

    def test_ingest_failure_rolls_back_canonical_files_and_kernel(self):
        citations = self.root / "kernel/citations.md"; citations.parent.mkdir(parents=True); citations.write_text("# existing\n", encoding="utf-8")
        def failing(pdf, candidate):
            citations.write_text("damaged", encoding="utf-8")
            note = self.root / "shell/03_evidence/papers/paper2026.md"; note.parent.mkdir(parents=True, exist_ok=True); note.write_text("partial", encoding="utf-8")
            return {"ok": False, "error": "simulated failure"}
        with self.assertRaisesRegex(RuntimeError, "simulated"):
            ingest_staged_candidate(self.root, self.store, "PC-001", expected_revision=2, actor_id="reviewer", ingest_runner=failing)
        self.assertEqual(citations.read_text(encoding="utf-8"), "# existing\n")
        self.assertFalse((self.root / "papers/Canonical Paper_2026.pdf").exists())
        self.assertFalse((self.root / "papers/Canonical Paper_2026").exists())
        self.assertFalse((self.root / "shell/03_evidence/papers/paper2026.md").exists())
        self.assertEqual(self.store.get_paper_candidate("PC-001")["verification_status"], "unverified")


if __name__ == "__main__": unittest.main()
