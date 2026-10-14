import pathlib
import tempfile
import unittest
from unittest import mock

from survey_tool.v2.capabilities import herdr_capability
from survey_tool.v2.store import v2_capabilities


class HerdrCapabilityTest(unittest.TestCase):
    def test_reports_only_safe_capability_fields(self):
        calls = []

        def runner(command, **kwargs):
            calls.append((command, kwargs))
            return 2, b"herdr agent commands:\n  herdr agent list\n  kinds: pi|codex|claude\n"

        result = herdr_capability(
            environ={"HERDR_ENV": "1", "HERDR_PANE_ID": "private-pane"},
            which=lambda _name: "/private/bin/herdr",
            runner=runner,
        )
        self.assertEqual(result, {
            "managed": True,
            "cli_available": True,
            "pi_supported": True,
            "codex_supported": True,
            "probe_status": "available",
            "access": "discovery_only",
        })
        self.assertEqual(calls[0][0], ["/private/bin/herdr", "agent"])
        self.assertLessEqual(calls[0][1]["timeout"], 1)
        self.assertLessEqual(calls[0][1]["output_limit"], 4096)
        self.assertNotIn("private", repr(result))

    def test_missing_cli_and_probe_failures_degrade_safely(self):
        missing = herdr_capability(environ={}, which=lambda _name: None)
        self.assertFalse(missing["managed"])
        self.assertFalse(missing["cli_available"])
        self.assertEqual(missing["probe_status"], "unavailable")

        failed = herdr_capability(
            environ={"HERDR_ENV": "1"},
            which=lambda _name: "/bin/herdr",
            runner=mock.Mock(side_effect=TimeoutError("secret path /tmp/session")),
        )
        self.assertTrue(failed["managed"])
        self.assertTrue(failed["cli_available"])
        self.assertFalse(failed["codex_supported"])
        self.assertNotIn("secret", repr(failed))

        misleading = herdr_capability(
            environ={"HERDR_ENV": "1"},
            which=lambda _name: "/bin/herdr",
            runner=lambda *_args, **_kwargs: (2, b"error starting codex"),
        )
        self.assertEqual(misleading["probe_status"], "unavailable")
        self.assertFalse(misleading["codex_supported"])

    @mock.patch("survey_tool.v2.store.herdr_capability", side_effect=RuntimeError("probe failed"))
    def test_capability_endpoint_builder_never_initializes_store(self, probe):
        root = pathlib.Path(tempfile.mkdtemp(prefix="v2-capabilities-"))
        # The API builder owns the final fail-safe so a probe regression cannot break GETs.
        result = v2_capabilities(root)
        self.assertEqual(result["herdr"]["probe_status"], "unavailable")
        self.assertFalse((root / ".survey-tool/survey-tool-v2.sqlite3").exists())
        probe.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
