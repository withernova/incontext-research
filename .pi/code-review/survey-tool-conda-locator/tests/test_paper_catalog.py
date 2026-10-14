import pathlib
import sys
import tempfile
import unittest
from unittest import mock

import server


class PaperCatalogTest(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp(prefix="paper-catalog-"))
        (self.root / "state.md").write_text("state: TEST\n", encoding="utf-8")
        (self.root / "papers").mkdir()

    def test_catalog_exposes_stable_citekeys_for_all_source_shapes(self):
        processed = self.root / "papers" / "A Study_2026"
        (processed / "hybrid_auto" / "images").mkdir(parents=True)
        (processed / "hybrid_auto" / "A Study_2026.md").write_text("# A Study", encoding="utf-8")
        (self.root / "papers" / "A Study_2026.pdf").write_bytes(b"%PDF-test")
        (self.root / "papers" / "Loose Paper_2025.pdf").write_bytes(b"%PDF-test")
        (self.root / "papers" / "INDEX.md").write_text(
            "| # | Title | Date | Venue | Link | File |\n"
            "|---|---|---|---|---|---|\n"
            "| 1 | Missing Paper | 2024 | Test | https://example.test | ⚠️ no PDF |\n",
            encoding="utf-8",
        )

        papers = server.read_papers(self.root)
        self.assertEqual(len(papers), 3)
        self.assertTrue(all(paper.get("citekey") for paper in papers))
        self.assertEqual(
            {paper["citekey"] for paper in papers},
            {server.citekey_for(paper) for paper in papers},
        )

    def test_web_search_parses_structured_output_larger_than_legacy_limit(self):
        payload = '{"source":"openalex","query":"q","hits":[' + ",".join(
            '{"title":"%s","citekey":"c%s"}' % ("x" * 600, index) for index in range(10)
        ) + "]}"
        self.assertGreater(len(payload), 4000)
        command = [sys.executable, "-c", f"print('x' * {len(payload)})"]
        self.assertGreater(len(server.run_script(command)["stdout"]), 4000)

        with mock.patch.object(server, "paper_skill_script", return_value=pathlib.Path("search.py")), mock.patch.object(
            server,
            "run_script",
            return_value={"returncode": 0, "stdout": payload, "stderr": ""},
        ):
            result = server.web_paper_search(self.root, "q", 10)
        self.assertEqual(len(result["hits"]), 10)
        self.assertNotIn("error", result)


if __name__ == "__main__":
    unittest.main()
