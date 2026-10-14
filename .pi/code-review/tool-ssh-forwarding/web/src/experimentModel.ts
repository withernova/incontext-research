import type { Dispatch, ExperimentDashboard, Run } from "./types";

export type PipelineLane = "design" | "review" | "approved" | "queued" | "running" | "analysis" | "completed" | "failed" | "legacy";
export type RunJourneyStep = "implement" | "run" | "results";

export const runJourneySteps: Array<{ id: RunJourneyStep; label: string }> = [
  { id: "implement", label: "与 AI 讨论并实现" },
  { id: "run", label: "Steward 运行" },
  { id: "results", label: "查看结果" },
];

export function describeRunJourney(run: Run): { current: RunJourneyStep; title: string; guidance: string } {
  const stage = run.workflow_stage || "research_design";
  if (["completed", "failed"].includes(stage) || ["completed", "failed", "cancelled"].includes(run.status || ""))
    return { current: "results", title: stage === "failed" || run.status === "failed" ? "检查失败与保留证据" : "实验已完成", guidance: "结果和边界是最终产出；日志只作为诊断材料。" };
  if (stage === "analysis_pending") return { current: "results", title: "整理并确认结果", guidance: "核对指标、关键结果与限制，然后完成人工确认。" };
  if (stage === "running") return { current: "run", title: "等待运行产出", guidance: "关注指标和产物；只有失败时再展开技术日志。" };
  if (stage === "ready_to_run") return { current: "run", title: "交给 Steward 运行", guidance: "Steward 会先核验实现和真实命令，再启动、监控并收集结果。" };
  return { current: "implement", title: "与 AI 讨论并实现", guidance: "让 Pi 直接在绑定仓库完成最小实现和测试；不需要提交审核。" };
}

export const laneLabels: Record<PipelineLane, string> = {
  design: "设计与实现",
  review: "等待审核",
  approved: "批准待授权",
  queued: "已授权待派发",
  running: "运行与监控",
  analysis: "待结果分析",
  completed: "科研完成",
  failed: "失败或中止",
  legacy: "历史不可追溯",
};

function latestDispatchFor(runId: string, dispatches: Dispatch[]): Dispatch | undefined {
  return dispatches
    .filter((dispatch) => dispatch.run_id === runId)
    .sort((left, right) => String(right.updated_at || "").localeCompare(String(left.updated_at || "")))[0];
}

export function classifyRun(run: Run, dashboard: ExperimentDashboard): PipelineLane {
  const dispatches = dashboard.execution_outbox?.items || [];
  const operationalStatus=run.status||"draft";
  const historicalWithoutReview=run.workflow_version!==2&&!run.review_status&&!["draft","planned"].includes(operationalStatus);
  const dispatch = latestDispatchFor(run.id, dispatches);
  const anomaly = dashboard.reconciliation?.anomalies?.some((item) => item.run_id === run.id);
  const reconcileAction = dashboard.reconciliation?.actions?.some((item) => item.run_id === run.id);
  if (anomaly || historicalWithoutReview || (run.execution_authorization_consumed_at && !dispatch)) return "legacy";
  if (dispatch?.status === "running") return "running";
  if (["queued", "blocked", "delivered", "claimed", "acknowledged"].includes(dispatch?.status || "") || reconcileAction) return "queued";
  if (["failed", "cancelled", "superseded"].includes(dispatch?.status || "")) return "failed";
  if (dispatch?.status === "completed" || run.workflow_stage === "analysis_pending") return "analysis";
  if (run.workflow_stage === "running") return "running";
  if ((run.status || "").startsWith("completed") || ["done", "succeeded"].includes(run.status || "")) return "completed";
  if (["failed", "cancelled", "aborted", "incomplete"].includes(run.status || "")) return "failed";
  if (run.review_status === "approved") return run.execution_authorized_at ? "queued" : "approved";
  if (["pending_review", "changes_requested", "needs_human_review"].includes(run.review_status || "")) return "review";
  return "design";
}

export function pipelineCounts(runs: Run[], dashboard: ExperimentDashboard): Record<PipelineLane, number> {
  const counts = Object.fromEntries(Object.keys(laneLabels).map((lane) => [lane, 0])) as Record<PipelineLane, number>;
  for (const run of runs) counts[classifyRun(run, dashboard)] += 1;
  return counts;
}

export function runEvidenceFields(run: Run): Array<{ label: string; value: string }> {
  return [
    { label: "目的", value: run.purpose || "" },
    { label: "必要性", value: run.necessity || "" },
    { label: "证据依据", value: run.evidence_basis || "" },
    { label: "数据定义", value: run.data_definition || "" },
    { label: "模型配置", value: run.model_config || "" },
    { label: "指标定义", value: run.metric_definition || "" },
    { label: "完整性门槛", value: run.integrity_gates || "" },
  ].filter((field) => field.value.trim());
}
