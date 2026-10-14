import pathlib
import tempfile
import unittest

import server


class CitationIdentityTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        (self.root / "kernel").mkdir()
        (self.root / "papers").mkdir()

    def citations(self, text):
        (self.root / "kernel/citations.md").write_text(text, encoding="utf-8")

    def test_multiple_records_and_empty_fields_are_independent(self):
        self.citations("# Citations\n## [first]\n- title: First\n- year: \n- doi: 10/first\n"
                       "\n## [second]\n- title: Second\n- year: 2024\n- doi: \n"
                       "## [last]\n- title: Last\n- year: 2025\n")
        rows = server.read_citations(self.root)
        self.assertEqual(list(rows), ["first", "second", "last"])
        self.assertEqual(rows["first"]["year"], "")
        self.assertEqual(rows["second"]["doi"], "")
        self.assertEqual(rows["last"]["title"], "Last")

    def test_registered_key_survives_filename_normalization(self):
        (self.root / "papers/Devils in Middle Layers  Object Hallucinations_2024.pdf").write_bytes(b"%PDF fixture")
        self.citations("## [jiang2024devilsin]\n- title: Devils in Middle Layers: Object Hallucinations\n"
                       "- year: 2024\n- local_pdf: shell/03_evidence/papers/jiang2024devilsin.pdf\n")
        paper = server.read_papers(self.root)[0]
        self.assertEqual(paper["citekey"], "jiang2024devilsin")
        self.assertEqual(paper["title"], "Devils in Middle Layers: Object Hallucinations")

    def test_ambiguous_titles_do_not_reassign_identity(self):
        (self.root / "papers/Same Title_2024.pdf").write_bytes(b"%PDF fixture")
        self.citations("## [one]\n- title: Same Title\n- year: 2024\n"
                       "## [two]\n- title: Same Title\n- year: 2024\n")
        self.assertEqual(server.read_papers(self.root)[0]["citekey"], "sametitl2024")

    def test_exact_pdf_path_takes_precedence_over_title(self):
        (self.root / "papers/Short Filename_2024.pdf").write_bytes(b"%PDF fixture")
        self.citations("## [author2024]\n- title: Complete Scientific Title\n- year: 2024\n"
                       "- local_pdf: papers/Short Filename_2024.pdf\n")
        self.assertEqual(server.read_papers(self.root)[0]["citekey"], "author2024")
