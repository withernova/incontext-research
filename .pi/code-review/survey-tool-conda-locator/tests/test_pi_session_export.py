import importlib.util
import pathlib
import tempfile
import unittest


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "pi_session_export.py"
SPEC = importlib.util.spec_from_file_location("pi_session_export", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class PiSessionExportTest(unittest.TestCase):
    def test_enhance_is_idempotent_and_injects_copy_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            html = pathlib.Path(directory) / "session.html"
            html.write_text("<html><head><title>Pi</title></head><body><div id='messages'></div><script id='session-data'>e30=</script></body></html>", encoding="utf-8")
            self.assertTrue(MODULE.enhance_html(html))
            output = html.read_text(encoding="utf-8")
            self.assertIn(MODULE.MARKER, output)
            self.assertIn("复制文本", output)
            self.assertIn("复制所选内容", output)
            self.assertIn('block.type === "text"', output)
            self.assertFalse(MODULE.enhance_html(html))

    def test_rejects_non_html_export(self):
        with tempfile.TemporaryDirectory() as directory:
            html = pathlib.Path(directory) / "broken.html"
            html.write_text("not an HTML document", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "complete Pi HTML"):
                MODULE.enhance_html(html)
