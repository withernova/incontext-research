#!/usr/bin/env python3
"""Regression tests for publish/export copying (junk dirs and dangling symlinks)."""
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import server  # noqa: F401  (must be imported before survey_tool.integrations; see server's domain module wiring)
from survey_tool import integrations


REMOTE = "/defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy"


class ExportRepoCopyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="publish-export-")
        self.root = pathlib.Path(self.tmp.name) / "project"
        self.root.mkdir()
        (self.root / "state.md").write_text("state: TEST\niteration: 1\n", encoding="utf-8")
        (self.root / "kernel").mkdir()
        (self.root / ".survey-tool").mkdir()
        self.dest = self.root / ".publish"

    def tearDown(self):
        self.tmp.cleanup()

    def test_export_skips_task_dirs_and_dangling_symlinks(self):
        worktree = self.root / "shell" / "06_experiments" / "E-012" / "review_worktree_zero"
        backups = worktree / ".task-backups" / "config-management" / "pytest-new"
        backups.mkdir(parents=True)
        (backups / "test_new_runs_are_isolated_and0").mkdir()
        # mirrors the real artifact: pytest's *-current link points at the remote host checkout
        (backups / "test_new_runs_are_isolated_andcurrent").symlink_to(
            f"{REMOTE}/.task-backups/config-management/pytest-new/test_new_runs_are_isolated_and0"
        )
        checks = worktree / ".task-checks" / "E011-R-001-smoke" / "pytest_tmp"
        checks.mkdir(parents=True)
        (checks / "test_smoke_current").symlink_to(f"{REMOTE}/.task-checks/E011-R-001-smoke/pytest_tmp/test_smoke0")
        # an unrelated dangling link in normal content must not abort the publish either
        (self.root / "stray-link").symlink_to(f"{REMOTE}/missing.py")

        result = integrations.export_repo(self.root, self.dest, {"initGit": False, "pushGithub": False})

        self.assertTrue(result["ok"], result)
        self.assertTrue((self.dest / "state.md").is_file())
        self.assertFalse((self.dest / "shell" / "06_experiments" / "E-012" / "review_worktree_zero" / ".task-backups").exists())
        self.assertFalse((self.dest / "shell" / "06_experiments" / "E-012" / "review_worktree_zero" / ".task-checks").exists())
        self.assertFalse((self.dest / "stray-link").exists())
        self.assertFalse((self.dest / ".task-backups").exists())

    def test_export_excludes_project_code_and_aliases_but_preserves_source(self):
        code=self.root/'code-repositories'/'W'/'iploc-szy'; code.mkdir(parents=True)
        (code/'code.py').write_text('private experimental code')
        (self.root/'code-alias').symlink_to(code,target_is_directory=True)
        (self.root/'file-alias.py').symlink_to(code/'code.py')
        result=integrations.export_repo(self.root,self.dest,{'initGit':False,'pushGithub':False})
        self.assertTrue(result['ok'])
        self.assertFalse((self.dest/'code-repositories').exists())
        self.assertFalse((self.dest/'code-alias').exists())
        self.assertFalse((self.dest/'file-alias.py').exists())
        self.assertTrue((code/'code.py').exists())
        self.assertIn('/code-repositories/',(self.dest/'.gitignore').read_text())

    def test_export_refuses_old_snapshot_code_without_deleting_it(self):
        code=self.dest/'code-repositories'; code.mkdir(parents=True)
        (code/'preserve.py').write_text('preserve')
        with self.assertRaisesRegex(ValueError,'不会自动删除'):
            integrations.export_repo(self.root,self.dest,{'initGit':False,'pushGithub':False})
        self.assertEqual((code/'preserve.py').read_text(),'preserve')

    def test_export_keeps_regular_symlink_content(self):
        (self.root / "real.md").write_text("content\n", encoding="utf-8")
        (self.root / "link-to-real.md").symlink_to(self.root / "real.md")

        result = integrations.export_repo(self.root, self.dest, {"initGit": False, "pushGithub": False})

        self.assertTrue(result["ok"], result)
        self.assertEqual((self.dest / "link-to-real.md").read_text(encoding="utf-8"), "content\n")


if __name__ == "__main__":
    unittest.main()
