import io
import pathlib
import tempfile
import unittest
from unittest import mock

from survey_tool.v2.store import V2Store
from survey_tool.v2.worker import execute_download, execute_mineru, execute_zotero_copy, run_once, start_local_worker


class FakeResponse:
    def __init__(self, data, url="https://example.org/paper.pdf", headers=None):
        self.stream = io.BytesIO(data); self.url = url; self.headers = headers or {}
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, amount=-1): return self.stream.read(amount)
    def geturl(self): return self.url


class V2WorkerTest(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp(prefix="v2-worker-"))
        self.store = V2Store(self.root); self.store.initialize()
        candidate = self.store.create_paper_candidate(
            object_id="PC-001", project_id="PROJECT-test", citekey="paper2026",
            title="Paper", source_url="https://openalex.org/W1", oa_url="https://example.org/paper.pdf",
        )
        self.pipeline = self.store.create_candidate_acquisition_pipeline("PC-001", expected_revision=candidate["revision"])

    @mock.patch("survey_tool.v2.worker.socket.getaddrinfo", return_value=[(2, 1, 6, "", ("93.184.216.34", 443))])
    def test_download_writes_only_staging_and_validates_pdf(self, _dns):
        job = self.store.claim_next_job(worker_id="worker")
        result = execute_download(self.root, job, opener=lambda *args, **kwargs: FakeResponse(b"%PDF-test"))
        staged = self.root / result["staged_pdf"]
        self.assertTrue(staged.is_file())
        self.assertIn(".survey-tool/staging/PC-001", staged.as_posix())
        self.assertFalse((self.root / "papers").exists())
        self.assertFalse((self.root / "kernel/citations.md").exists())
        with self.assertRaisesRegex(ValueError, "did not return a PDF"):
            execute_download(self.root, job, opener=lambda *args, **kwargs: FakeResponse(b"<html>"))

    @mock.patch("survey_tool.v2.worker.socket.getaddrinfo", return_value=[(2, 1, 6, "", ("127.0.0.1", 443))])
    def test_download_rejects_private_network(self, _dns):
        job = self.store.claim_next_job(worker_id="worker")
        with self.assertRaisesRegex(ValueError, "non-public"):
            execute_download(self.root, job)

    def test_mineru_uses_staged_download_and_stays_in_staging(self):
        download = self.store.claim_next_job(worker_id="worker")
        pdf = self.root / ".survey-tool/staging/PC-001/paper2026.pdf"
        pdf.parent.mkdir(parents=True); pdf.write_bytes(b"%PDF-test")
        self.store.finish_claimed_job(download["id"], lease_token=download["lease_token"], succeeded=True, result={"staged_pdf": str(pdf.relative_to(self.root))})
        mineru = self.store.claim_next_job(worker_id="worker")
        captured = []
        def runner(args, **kwargs):
            captured.append(args)
            output = pathlib.Path(args[args.index("-o") + 1]) / "paper" / "hybrid_auto"
            output.mkdir(parents=True); (output / "paper.md").write_text("parsed", encoding="utf-8")
            return mock.Mock(returncode=0, stdout="ok", stderr="")
        result = execute_mineru(self.root, self.store, mineru, runner=runner)
        self.assertIn("-b", captured[0])
        self.assertEqual(captured[0][captured[0].index("-b") + 1], "pipeline")
        self.assertTrue((self.root / result["markdown"]).is_file())
        self.assertTrue(result["markdown"].startswith(".survey-tool/staging/"))
        self.assertFalse((self.root / "papers").exists())

    def test_zotero_copy_is_bounded_atomic_and_does_not_expose_source_path(self):
        source=self.root/"local.pdf"; source.write_bytes(b"%PDF-local")
        job={"target_object_id":"PC-local","request":{"candidate_id":"PC-local","item_id":42,"citekey":"local2026"}}
        result=execute_zotero_copy(self.root,job,resolver=lambda root,item_id:{"path":source,"item_id":item_id,"bytes":source.stat().st_size})
        self.assertEqual((self.root/result["staged_pdf"]).read_bytes(),b"%PDF-local")
        self.assertNotIn(str(source),str(result)); self.assertFalse(result["canonical_write"])
        bad=self.root/"bad.pdf"; bad.write_bytes(b"not-pdf")
        with self.assertRaisesRegex(ValueError,"not a PDF"):
            execute_zotero_copy(self.root,job,resolver=lambda *_:{"path":bad})
        with mock.patch("survey_tool.v2.worker.MAX_PDF_BYTES",5), self.assertRaisesRegex(ValueError,"exceeds"):
            execute_zotero_copy(self.root,job,resolver=lambda *_:{"path":source})

    def test_run_once_uses_bounded_long_lease_without_recovery_for_local_drain(self):
        with mock.patch("survey_tool.v2.worker.V2Store",return_value=self.store),mock.patch.object(self.store,"claim_next_job",return_value=None) as claim,mock.patch.object(self.store,"recover_expired_jobs") as recover:
            self.assertEqual(run_once(self.root,"worker",recover=False,target_object_id="PC-001")["status"],"idle")
        recover.assert_not_called(); self.assertEqual(claim.call_args.kwargs["lease_seconds"],3600); self.assertEqual(claim.call_args.kwargs["target_object_id"],"PC-001")

    def test_local_worker_is_singleton_per_project(self):
        entered=__import__("threading").Event(); release=__import__("threading").Event()
        def runner(*args,**kwargs): entered.set(); release.wait(2); return {"status":"idle"}
        first=start_local_worker(self.root,target_object_id="PC-001",runner=runner); self.assertTrue(first["worker_started"]); self.assertTrue(entered.wait(1))
        second=start_local_worker(self.root,target_object_id="PC-001",runner=runner); self.assertTrue(second["already_running"]); self.assertFalse(second["worker_started"])
        release.set()


if __name__ == "__main__": unittest.main()
