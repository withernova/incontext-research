"""Pure Run research-lifecycle contracts. This module has no storage imports."""

WORKFLOW_VERSION = 2
STAGES = (
    "research_design", "code_planning", "ready_for_review", "awaiting_review",
    "ready_to_run", "running", "analysis_pending", "completed", "failed",
)
ACTIONS = {
    "confirm-design": ({"research_design"}, "code_planning"),
    "implementation-ready": ({"code_planning"}, "ready_for_review"),
    "submit-review": ({"ready_for_review"}, "awaiting_review"),
    "request-changes": ({"awaiting_review", "ready_to_run"}, "code_planning"),
    "approve": ({"awaiting_review"}, "ready_to_run"),
    "running": ({"ready_to_run"}, "running"),
    "begin-analysis": ({"running", "analysis_pending"}, "analysis_pending"),
    "finalize-results": ({"analysis_pending"}, "completed"),
    "mark-failed": ({"running", "analysis_pending"}, "failed"),
}


def effective_run_workflow(run):
    if run.get("workflow_version") != WORKFLOW_VERSION:
        return {"version": 1, "stage": "legacy", "legacy": True}
    stage = str(run.get("workflow_stage") or "research_design")
    if stage not in STAGES:
        raise ValueError(f"Run workflow_stage 非法：{stage}")
    return {"version": WORKFLOW_VERSION, "stage": stage, "legacy": False}


def transition(current, action):
    if action == "request-changes" and current == "failed":
        # Keep the terminal outcome visible while review_status opens the same
        # Run for revision. A later direct-Steward authorization snapshots the
        # edited spec and creates a new independent execution attempt.
        return "failed"
    if action == "reopen-design":
        if current not in {"research_design", "code_planning", "ready_for_review", "awaiting_review", "ready_to_run"}:
            raise ValueError(f"运行开始后不能用 reopen-design 回到研究设计：{current}")
        return "research_design"
    if action not in ACTIONS:
        raise ValueError(f"未知 Run workflow action：{action}")
    allowed, target = ACTIONS[action]
    if current not in allowed:
        raise ValueError(f"Run workflow 不能从 {current} 执行 {action}")
    return target


def progress_model(run):
    workflow = effective_run_workflow(run)
    if workflow["legacy"]:
        return {**workflow, "step": 0, "total": 6, "label": "历史 Run"}
    stage = workflow["stage"]
    step = {
        "research_design": 1, "code_planning": 2, "ready_for_review": 2,
        "awaiting_review": 2, "ready_to_run": 3, "running": 3,
        "analysis_pending": 4, "completed": 6, "failed": 3,
    }[stage]
    labels = {
        "research_design": "研究设计", "code_planning": "代码方案",
        "ready_for_review": "代码方案待审核", "awaiting_review": "等待审核",
        "ready_to_run": "等待执行授权", "running": "运行与监控",
        "analysis_pending": "结果分析", "completed": "结果已保存",
        "failed": "运行失败",
    }
    return {**workflow, "step": step, "total": 6, "label": labels[stage]}
