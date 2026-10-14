"""Experiment document readability, time semantics and preservation regressions."""
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import server
import surveyctl
from survey_tool.experiment_docs import (
    ordered_runs, refresh_experiment_docs, render_experiment_index,
    render_experiment_result, snapshot_time,
)


class ExperimentDocsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.directory = self.root / "shell/06_experiments/E-001"
        self.directory.mkdir(parents=True)
        self.exp = {"id": "E-001", "title": "比较方案", "objective": "检查参考区域是否有帮助", "created": "2026-01-01T09:00:00", "updated": "2026-01-02T09:00:00", "workspace_id": "W-01"}
        self.runs = [{"id": "later", "experiment_id": "E-001", "variant": "后续验证", "created": "2026-01-03T09:00:00", "updated": "2026-01-04T09:00:00", "status": "completed"}, {"id": "earlier", "experiment_id": "E-001", "variant": "初始比较", "created": "2026-01-01T10:00:00", "updated": "2026-01-01T11:00:00", "status": "draft"}]

    def seed_registry(self):
        server.write_tool_json(self.root, "experiments.json", [self.exp])
        server.write_tool_json(self.root, "runs.json", self.runs)
        server.write_tool_json(self.root, "servers.json", [{"id": "S-01", "ssh_host": "test"}])
        server.write_tool_json(self.root, "workspaces.json", [{"id": "W-01", "server_id": "S-01", "remote_repo": "/repo", "remote_experiment_root": "/exp", "remote_data_root": "/data"}])

    def file_snapshot(self):
        return {str(path.relative_to(self.root)): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}

    def test_entry_summary_before_chronology_and_scoped_links(self):
        (self.directory / "plan.md").write_text("方案", encoding="utf-8")
        page = render_experiment_index(self.exp, self.runs, self.directory)
        self.assertLess(page.index("## 先读这一页"), page.index("## Run 登记时间线"))
        self.assertLess(page.index("[earlier]"), page.index("[later]"))
        self.assertIn("(plan.md)", page)
        self.assertIn("结果与审计（文件缺失）", page)
        self.assertIn("2026-01-04T09:00:00", page)
        self.assertIn("登记时间不等于实际运行时间", page)
        self.assertIn("不代表没有实验结果", page)

    def test_missing_invalid_times_and_explicit_offsets(self):
        rows = [{"id": "unknown"}, {"id": "bad", "created": "nonsense"}, {"id": "first", "created": "2026-01-01T09:00:00+08:00"}, {"id": "second", "created": "2026-01-01T02:00:00Z"}]
        self.assertEqual([row["id"] for row in ordered_runs(rows)], ["first", "second", "bad", "unknown"])
        self.assertEqual(snapshot_time({}, []), "未登记")
        self.assertEqual(snapshot_time({}, [{"updated": "invalid"}]), "未登记")
        self.assertEqual(snapshot_time({}, [{"updated": "invalid", "created": "2026-01-01T02:00:00Z"}]), "2026-01-01T02:00:00Z")
        self.assertEqual(snapshot_time({}, rows), "2026-01-01T02:00:00Z")

    def test_supplementary_navigation_without_symlink_or_artifact_traversal(self):
        (self.directory / "分析 (v2).md").write_text("原始研究证据", encoding="utf-8")
        (self.directory / "analysis").mkdir()
        (self.directory / "analysis/hidden.md").write_text("不扫描深层正文", encoding="utf-8")
        (self.directory / "__pycache__").mkdir()
        (self.directory / "remote.md").symlink_to(self.root / "not-present")
        page = render_experiment_index(self.exp, self.runs, self.directory)
        self.assertIn("%E5%88%86%E6%9E%90%20%28v2%29.md", page)
        self.assertIn("(analysis/hidden.md)", page)
        for excluded in ("remote.md", "__pycache__", "原始研究证据", "不扫描深层正文"):
            self.assertNotIn(excluded, page)

    def test_markdown_cells_and_group_links_are_safe(self):
        run = {**self.runs[0], "id": "run(1)", "group_id": "baseline", "variant": "a|b\n<script>[x]"}
        page = render_experiment_index(self.exp, [run], self.directory)
        self.assertIn("(runs/baseline/run%281%29.md)", page)
        self.assertIn("a&#124;b<br>&lt;script&gt;&#91;x&#93;", page)
        self.assertNotIn("<script>", page)

    def test_v2_results_values_comparisons_and_provenance_survive(self):
        run = {**self.runs[0], "seed": 0, "key_results": [{"metric_id": "acc", "value": 0, "comparison": "control=0", "delta": 0, "uncertainty": "±0.01", "artifact": "metrics.json", "interpretation": "未改善"}], "result_analysis": "两个条件相同", "limitations": "只有一组数据"}
        page = render_experiment_result(self.exp, [run], "原始审计论证")
        self.assertLess(page.index("## 结果摘要"), page.index("## 运行汇总"))
        for expected in ("关键结果：acc=0", "比较对象：control=0", "差值：0", "不确定性：±0.01", "来源/产物：metrics.json", "两个条件相同", "只有一组数据", "原始审计论证", "| 0 |"):
            self.assertIn(expected, page)
        self.assertNotIn("（尚无结构化观测）", page)

    def test_legacy_observations_keep_sample_count_and_do_not_promote_auxiliary(self):
        exp = {**self.exp, "run_groups": [{"id": "base", "name": "基线"}], "metric_definitions": [{"id": "acc", "name": "准确率", "unit": "ratio", "meaning": "正确比例"}]}
        run = {**self.runs[0], "group_id": "base", "archived_at": "2026-01-05", "metric_observations": [{"metric_id": "acc", "value": 0.75, "sample_count": 0, "provenance": "audit.json"}], "auxiliary_metric_observations": [{"metric_id": "not-main", "value": 99}]}
        page = render_experiment_result(exp, [run], "")
        for expected in ("### 基线 (`base`)", "准确率=0.75 ratio", "样本数：0", "指标含义：正确比例", "来源/产物：audit.json", "（已归档）"):
            self.assertIn(expected, page)
        self.assertNotIn("not-main", page)

    def test_refresh_preserves_research_notes_and_is_idempotent(self):
        self.seed_registry()
        (self.directory / "result.md").write_text("# old\n## 详细审计正文（canonical）\n原始引文\n\n## 子节\n数值与限制\n", encoding="utf-8")
        (self.directory / "E-001.md").write_text("# old\n## 自由笔记（Obsidian）\n手写阅读提示\n", encoding="utf-8")
        topic = self.directory / "topic.md"
        topic.write_text("不能改写的研究文档", encoding="utf-8")
        state_before = {path.name: path.read_bytes() for path in (self.root / ".survey-tool").iterdir() if path.is_file()}
        refresh_experiment_docs(self.root, "E-001")
        once = self.file_snapshot()
        refresh_experiment_docs(self.root, "E-001")
        self.assertEqual(once, self.file_snapshot())
        self.assertIn("原始引文\n\n## 子节\n数值与限制", (self.directory / "result.md").read_text(encoding="utf-8"))
        self.assertIn("手写阅读提示", (self.directory / "E-001.md").read_text(encoding="utf-8"))
        self.assertEqual(topic.read_text(encoding="utf-8"), "不能改写的研究文档")
        self.assertEqual(state_before, {path.name: path.read_bytes() for path in (self.root / ".survey-tool").iterdir() if path.is_file() and path.name in state_before})

    def test_dry_run_writes_nothing_even_with_missing_directory(self):
        self.seed_registry()
        self.directory.rmdir()
        before = self.file_snapshot()
        with self.assertRaisesRegex(ValueError, "实验独立目录缺失"):
            refresh_experiment_docs(self.root, "E-001", dry_run=True)
        self.assertEqual(before, self.file_snapshot())
        self.assertFalse(self.directory.exists())

    def test_dry_run_existing_directory_previews_three_pages_without_writes(self):
        self.seed_registry()
        before = self.file_snapshot()
        result = refresh_experiment_docs(self.root, "E-001", dry_run=True)
        self.assertFalse(result["writes"])
        self.assertEqual(len(result["pages"]), 3)
        self.assertIn("[结果与审计](result.md)", result["pages"]["shell/06_experiments/E-001/E-001.md"])
        self.assertEqual(before, self.file_snapshot())

    def test_unknown_experiment_is_rejected_without_writes(self):
        self.seed_registry()
        before = self.file_snapshot()
        with self.assertRaisesRegex(ValueError, "Experiment 不存在"):
            refresh_experiment_docs(self.root, "E-999", dry_run=True)
        self.assertEqual(before, self.file_snapshot())

    def test_obsidian_refresh_preserves_entry_notes_and_does_not_refresh_results(self):
        self.seed_registry()
        (self.root / "state.md").write_text("state: TEST\n", encoding="utf-8")
        entry = self.directory / "E-001.md"
        entry.write_text("# old\n## 自由笔记（Obsidian）\n入口提示\n", encoding="utf-8")
        result = self.directory / "result.md"
        result.write_text("不在重建索引时覆盖结果", encoding="utf-8")
        server.generate_obsidian_indexes(self.root)
        self.assertIn("入口提示", entry.read_text(encoding="utf-8"))
        self.assertIn("## Run 登记时间线", entry.read_text(encoding="utf-8"))
        self.assertIn("E-001-documents.md", entry.read_text(encoding="utf-8"))
        self.assertTrue((self.directory / "E-001-documents.md").exists())
        global_index = (self.root / "index/Experiments.md").read_text(encoding="utf-8")
        self.assertIn("../shell/06_experiments/E-001/E-001-documents.md", global_index)
        self.assertIn("../shell/06_experiments/E-001/runs/later.md", (self.root / "index/Runs.md").read_text(encoding="utf-8"))
        self.assertEqual(result.read_text(encoding="utf-8"), "不在重建索引时覆盖结果")

    def test_cli_preview_and_refresh(self):
        self.seed_registry()
        before = self.file_snapshot()
        args = ["surveyctl.py", "--project", str(self.root), "experiment", "docs", "E-001"]
        for extra in (["--dry-run"], []):
            output = io.StringIO()
            with mock.patch.object(sys, "argv", args + extra), mock.patch.object(surveyctl, "root_for", return_value=self.root), contextlib.redirect_stdout(output):
                surveyctl.main()
            result = json.loads(output.getvalue())
            self.assertEqual(result["writes"], not bool(extra))
            if extra:
                self.assertEqual(before, self.file_snapshot())
        self.assertTrue((self.directory / "result.md").exists())

    def test_normal_run_update_refreshes_entry_and_keeps_audit(self):
        self.exp["metric_definitions"] = [{"id": "acc", "name": "准确率", "formula": "correct/n", "meaning": "正确比例", "direction": "higher", "unit": "ratio", "aggregation": "mean", "scope": "evaluation"}]
        self.seed_registry()
        server.save_experiment_result(self.root, self.exp, self.runs)
        with (self.directory / "result.md").open("a", encoding="utf-8") as handle:
            handle.write("\n保留论证\n")
        server.update_run(self.root, "later", {"result_analysis": "已核对产物", "key_results": [{"metric_id": "acc", "value": 0.5, "artifact": "metrics.json"}]})
        self.assertIn("关键结果：准确率=0.5", (self.directory / "result.md").read_text(encoding="utf-8"))
        self.assertIn("保留论证", (self.directory / "result.md").read_text(encoding="utf-8"))
        entry = (self.directory / "E-001.md").read_text(encoding="utf-8")
        updated = next(row for row in server.experiment_data(self.root)["runs"] if row["id"] == "later")
        self.assertIn(updated["updated"], entry)
        self.assertIn("[later]", entry)


if __name__ == "__main__":
    unittest.main()
