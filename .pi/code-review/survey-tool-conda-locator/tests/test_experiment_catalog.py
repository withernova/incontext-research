"""Obsidian document discovery, recency and explicit-version navigation."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import server
from survey_tool.experiment_catalog import collect_documents, recent_documents, render_catalog
from survey_tool.experiment_docs import refresh_experiment_docs, render_experiment_index


class ExperimentCatalogTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.directory = self.root / "shell/06_experiments/E-001"
        self.directory.mkdir(parents=True)
        self.exp = {"id": "E-001", "title": "文档导航"}

    def note(self, relative, text, modified=100):
        path = self.directory / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        os.utime(path, (modified, modified))
        return path

    def test_directory_identity_mismatch_never_scans_foreign_documents(self):
        self.note("report.md", "# 不应归给其他实验")
        catalog = collect_documents(self.directory, "E-002")
        self.assertEqual(catalog["documents"], [])
        self.assertTrue(any("Experiment ID 不匹配" in warning for warning in catalog["warnings"]))

    def test_nested_titles_same_names_and_exact_relative_links(self):
        self.note("analysis/report.md", "# 定位误差分析\n正文不复制")
        self.note("diagnostics/report.md", "# 第二框诊断\n")
        catalog = collect_documents(self.directory, "E-001")
        page = render_catalog("E-001", catalog)
        for expected in ("定位误差分析", "第二框诊断", "(analysis/report.md)", "(diagnostics/report.md)", "<code>analysis/report.md</code>", "(E-001.md)"):
            self.assertIn(expected, page)
        self.assertNotIn("正文不复制", page)
        self.assertIn("E-001 文档目录", page)

    def test_newest_topics_exclude_regenerated_core_run_and_index_files(self):
        self.note("older.md", "# 较早分析", 100)
        self.note("nested/newer.md", "# 新分析", 200)
        for path in ("result.md", "events.md", "runs/R.md", "E-001.md", "E-001-documents.md"):
            self.note(path, "# 不应排在最近专题列表中", 999)
        self.note("other-generated.md", "---\nsurvey_tool_generated: true\n---\n# 自动页", 999)
        catalog = collect_documents(self.directory, "E-001")
        self.assertEqual([row["path"] for row in recent_documents(catalog)], ["nested/newer.md", "older.md"])
        entry = render_experiment_index(self.exp, [], self.directory, catalog=catalog)
        self.assertLess(entry.index("[新分析]"), entry.index("[较早分析]"))
        self.assertIn("不是“当前有效版本”", entry)
        self.assertIn("文件复制可能改变修改时间", entry)
        self.assertNotIn("不应排在最近专题列表中", entry)

    def test_current_version_is_explicit_and_not_selected_by_mtime(self):
        self.note("current.md", '---\ntitle: "当前指标定义"\ndoc_topic: 指标定义\ndoc_status: current\n---\n# 备用标题', 100)
        self.note("newer-draft.md", "---\ndoc_topic: 指标定义\ndoc_status: draft\n---\n# 新草稿", 200)
        self.note("old.md", "---\ndoc_status: superseded\nsuperseded_by: current.md\n---\n# 旧定义", 150)
        page = render_catalog("E-001", collect_documents(self.directory, "E-001"))
        current_section = page.split("## 当前版本", 1)[1].split("## 找文档", 1)[0]
        self.assertIn("(current.md)", current_section)
        self.assertNotIn("(newer-draft.md)", current_section)
        self.assertNotIn("(old.md)", current_section)
        self.assertIn("[替代文档](current.md)", page)
        self.assertIn("已被替代", page)

    def test_duplicate_current_topic_and_invalid_replacement_are_not_resolved_by_guessing(self):
        for name in ("one.md", "two.md"):
            self.note(name, "---\ndoc_topic: 模型验证\ndoc_status: current\n---\n# 当前定义")
        self.note("old.md", "---\ndoc_status: superseded\nsuperseded_by: ../../outside.md\n---\n# 旧定义")
        page = render_catalog("E-001", collect_documents(self.directory, "E-001"))
        self.assertIn("同一专题存在多个当前版本", page)
        self.assertIn("(one.md)", page)
        self.assertIn("(two.md)", page)
        self.assertIn("替代目标未找到或无效", page)
        self.assertNotIn("(../../outside.md)", page)

    def test_unmarked_and_unknown_status_do_not_become_current(self):
        self.note("latest-final.md", "# 文件名不是版本依据", 999)
        self.note("unknown.md", "---\ndoc_status: automatically-approved\n---\n# 未知标记")
        catalog = collect_documents(self.directory, "E-001")
        page = render_catalog("E-001", catalog)
        self.assertIn("暂无显式标记的当前版本", page)
        self.assertIn("未知 doc_status", page)
        self.assertTrue(all(row["status"] == "" for row in catalog["documents"]))

    def test_links_worktrees_hidden_caches_and_research_tmp_are_excluded(self):
        self.note("analysis/report.md", "# 保留报告")
        for folder in ("review_worktree", "review_worktree_zero_fp32", "research_tmp", "codespace", "node_modules", "__pycache__", ".task-backups", "checkpoints"):
            self.note(folder + "/README.md", "# 不应索引")
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "secret.md").write_text("私密内容", encoding="utf-8")
        (self.directory / "linked-dir").symlink_to(outside, target_is_directory=True)
        (self.directory / "linked.md").symlink_to(outside / "secret.md")
        catalog = collect_documents(self.directory, "E-001")
        self.assertEqual([row["path"] for row in catalog["documents"]], ["analysis/report.md"])

    def test_scan_limits_are_visible_and_header_reading_is_bounded(self):
        for i in range(4):
            self.note(f"note{i}.md", f"# 标题 {i}\n" + "不能复制正文" * 5000)
        with mock.patch("survey_tool.experiment_catalog.MAX_DOCUMENTS", 2):
            catalog = collect_documents(self.directory, "E-001")
        self.assertEqual(len(catalog["documents"]), 2)
        self.assertTrue(any("扫描上限" in warning for warning in catalog["warnings"]))
        self.assertNotIn("不能复制正文", render_catalog("E-001", catalog))
        with mock.patch("survey_tool.experiment_catalog.MAX_ENTRIES", 1):
            limited = collect_documents(self.directory, "E-001")
        self.assertTrue(limited["warnings"])
        self.note("nested/deeper/report.md", "# 深层报告")
        with mock.patch("survey_tool.experiment_catalog.MAX_DEPTH", 0):
            shallow = collect_documents(self.directory, "E-001")
        self.assertTrue(any("深度超限" in warning for warning in shallow["warnings"]))

    def test_markdown_aliases_titles_and_paths_are_escaped(self):
        self.note("分析 (v2).md", '# 标题|<script>[x]\n')
        page = render_catalog("E-001", collect_documents(self.directory, "E-001"))
        self.assertIn("标题&#124;&lt;script&gt;&#91;x&#93;", page)
        self.assertIn("%E5%88%86%E6%9E%90%20%28v2%29.md", page)
        self.assertNotIn("<script>", page)

    def test_collision_refuses_explicit_refresh_and_normal_update_preserves_user_note(self):
        server.write_tool_json(self.root, "experiments.json", [self.exp])
        server.write_tool_json(self.root, "runs.json", [])
        target = self.note("E-001-documents.md", "# 用户现有文档\n不能覆盖")
        with self.assertRaisesRegex(ValueError, "拒绝覆盖"):
            refresh_experiment_docs(self.root, "E-001")
        self.assertFalse((self.directory / "result.md").exists())
        server.save_experiment_result(self.root, self.exp, [])
        self.assertEqual(target.read_text(encoding="utf-8"), "# 用户现有文档\n不能覆盖")
        self.assertIn("同名文件冲突", (self.directory / "E-001.md").read_text(encoding="utf-8"))

    def test_catalogue_symlink_is_never_followed_for_writes(self):
        server.write_tool_json(self.root, "experiments.json", [self.exp])
        server.write_tool_json(self.root, "runs.json", [])
        outside = self.root / "outside.md"
        outside.write_text("不能改写", encoding="utf-8")
        (self.directory / "E-001-documents.md").symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "符号链接"):
            refresh_experiment_docs(self.root, "E-001", dry_run=True)
        server.save_experiment_result(self.root, self.exp, [])
        self.assertEqual(outside.read_text(encoding="utf-8"), "不能改写")


if __name__ == "__main__":
    unittest.main()
