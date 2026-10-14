"""Real HTTP checks for independent Experiment document search and read-only boundaries."""
import json
import pathlib
import tempfile
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer
from unittest import mock

import server
from survey_tool.experiment_document_api import list_documents, read_document


class ExperimentDocumentApiTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        (self.root / "state.md").write_text("state: TEST\n", encoding="utf-8")
        self.directory = self.root / "shell/06_experiments/E-001"
        self.directory.mkdir(parents=True)
        self.other = self.directory.parent / "E-002"
        self.other.mkdir()
        server.write_tool_json(self.root, "experiments.json", [{"id": "E-001", "title": "独立实验一"}, {"id": "E-002", "title": "独立实验二"}])
        server.write_tool_json(self.root, "runs.json", [])
        self.note("analysis/sub/report.md", "---\ndoc_topic: 定位误差\ndoc_status: current\n---\n# 定位误差报告\n正文一")
        self.note("diagnostics/report.md", "# 另一份诊断\n正文二")
        (self.other / "report.md").write_text("# 其他实验的报告\n其他正文", encoding="utf-8")
        self.config = mock.patch.object(server, "CFG", {"projects_root": str(self.root.parent), "projects": [str(self.root)], "skill_dir": "", "port": 0})
        self.config.start()
        self.addCleanup(self.config.stop)
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.H)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        self.api = f"/api/v2/p/{urllib.parse.quote(str(self.root), safe='')}/experiments/E-001/documents"

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=2)

    def note(self, relative, text):
        path = self.directory / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def request(self, path, method="GET", payload=None):
        request = urllib.request.Request(self.base + path, data=json.dumps(payload).encode() if payload is not None else None, method=method, headers={"Content-Type": "application/json", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as exc:
            try:
                return exc.code, json.loads(exc.read())
            finally:
                exc.close()

    def snapshot(self):
        return {str(path.relative_to(self.root)): path.read_bytes() for path in self.root.rglob("*") if path.is_file() and not path.is_symlink()}

    def test_search_directory_filter_and_read_are_live_and_write_free(self):
        before = self.snapshot()
        status, listing = self.request(self.api + "?" + urllib.parse.urlencode({"q": "误差", "directory": "analysis", "sort": "modified"}))
        self.assertEqual(status, 200, listing)
        self.assertEqual(listing["experiment_id"], "E-001")
        self.assertTrue(listing["read_only"])
        self.assertEqual([row["path"] for row in listing["documents"]], ["analysis/sub/report.md"])
        self.assertIn("analysis/sub", listing["directories"])
        self.assertNotIn("其他实验", json.dumps(listing, ensure_ascii=False))
        status, content = self.request(self.api + "/content?" + urllib.parse.urlencode({"path": "analysis/sub/report.md"}))
        self.assertEqual(status, 200, content)
        self.assertIn("正文一", content["content"])
        self.assertEqual(content["project_relative_path"], "shell/06_experiments/E-001/analysis/sub/report.md")
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.root / ".survey-tool/survey-tool-v2.sqlite3").exists())

    def test_nested_other_experiment_is_excluded_not_assigned_to_parent(self):
        self.note("E-012/analysis/report.md", "# 错误嵌套的独立实验\n不能归入E001")
        status, result = self.request(self.api)
        self.assertEqual(status, 200, result)
        self.assertFalse(any(row["path"].startswith("E-012/") for row in result["documents"]))
        self.assertFalse(any(path.startswith("E-012") for path in result["directories"]))
        self.assertTrue(any("跳过嵌套 Experiment" in warning for warning in result["warnings"]))
        status, _ = self.request(self.api + "/content?" + urllib.parse.urlencode({"path": "E-012/analysis/report.md"}))
        self.assertEqual(status, 400)

    def test_missing_or_moved_experiment_is_reported_not_recreated(self):
        moved = self.other / "E-001"
        self.directory.rename(moved)
        before = self.snapshot()
        status, result = self.request(self.api)
        self.assertEqual(status, 409, result)
        self.assertEqual(result["reason"], "experiment_directory_unavailable")
        self.assertIn("实验独立目录缺失", result["error"])
        self.assertEqual(before, self.snapshot())
        self.assertFalse(self.directory.exists())
        server.generate_obsidian_indexes(self.root)
        self.assertFalse(self.directory.exists())
        self.assertTrue(moved.exists())
        for path, content in before.items():
            if path.startswith("shell/06_experiments/E-002/E-001/"):
                self.assertEqual((self.root / path).read_bytes(), content)
        status, parent = self.request(self.api.replace("E-001/documents", "E-002/documents"))
        self.assertEqual(status, 200, parent)
        self.assertFalse(any(row["path"].startswith("E-001/") for row in parent["documents"]))

    def test_traversal_absolute_paths_and_invalid_filters_are_rejected(self):
        for path in ("../E-002/report.md", "/etc/passwd", "analysis/../../../E-002/report.md", "analysis\\report.md", "E-002/report.md"):
            status, _ = self.request(self.api + "/content?" + urllib.parse.urlencode({"path": path}))
            self.assertEqual(status, 400, path)
        for params in ({"directory": "../E-002"}, {"sort": "invented"}, {"kind": "anything"}, {"status": "approved"}, {"q": "x" * 301}):
            status, _ = self.request(self.api + "?" + urllib.parse.urlencode(params))
            self.assertEqual(status, 400, params)

    def test_hidden_worktree_and_symlink_content_cannot_be_read(self):
        self.note("review_worktree/README.md", "# 源码副本")
        self.note(".private.md", "不能读取")
        (self.directory / "outside.md").symlink_to(self.other / "report.md")
        for path in ("review_worktree/README.md", "outside.md"):
            status, _ = self.request(self.api + "/content?" + urllib.parse.urlencode({"path": path}))
            self.assertEqual(status, 404, path)
        status, _ = self.request(self.api + "/content?" + urllib.parse.urlencode({"path": ".private.md"}))
        self.assertEqual(status, 400)

    def test_refresh_needs_targeted_confirmation_and_preserves_other_experiment(self):
        before_other = (self.other / "report.md").read_bytes()
        before_registry = (self.root / ".survey-tool/experiments.json").read_bytes()
        for payload in ({}, {"confirmation": "REFRESH EXPERIMENT DOCUMENTS E-002"}, {"confirmation": "REFRESH EXPERIMENT DOCUMENTS E-001", "experiment_id": "E-002"}):
            status, _ = self.request(self.api + "/refresh", "POST", payload)
            self.assertEqual(status, 400)
        status, result = self.request(self.api + "/refresh", "POST", {"confirmation": "REFRESH EXPERIMENT DOCUMENTS E-001"})
        self.assertEqual(status, 200, result)
        self.assertEqual(len(result["paths"]), 3)
        self.assertTrue(all(path.startswith("shell/06_experiments/E-001/") for path in result["paths"]))
        self.assertEqual(before_other, (self.other / "report.md").read_bytes())
        self.assertEqual(before_registry, (self.root / ".survey-tool/experiments.json").read_bytes())

    def test_unknown_identity_and_unindexed_path_are_not_found(self):
        status, _ = self.request(self.api.replace("E-001", "E-999"))
        self.assertEqual(status, 404)
        status, _ = self.request(self.api + "/content?path=missing.md")
        self.assertEqual(status, 404)

    def test_metadata_filters_and_content_size_limit(self):
        result = list_documents(self.root, "E-001", status="current", kind="topic")
        self.assertEqual(result["total"], 1)
        self.note("large.md", "# 大文档\n" + "x" * 100)
        with mock.patch("survey_tool.experiment_document_api.CONTENT_BYTES", 50):
            with self.assertRaisesRegex(ValueError, "预览上限"):
                read_document(self.root, "E-001", "large.md")


if __name__ == "__main__":
    unittest.main()
