import { describe, expect, it } from "vitest";
import { classifyRun, describeRunJourney, pipelineCounts } from "./experimentModel";
import type { ExperimentDashboard, Run } from "./types";

function dashboard(runs: Run[], extra: Partial<ExperimentDashboard> = {}): ExperimentDashboard {
  return { experiments: [], runs, ...extra };
}

describe("experiment pipeline classification", () => {
  it("keeps approval, authorization, execution and analysis distinct", () => {
    const runs: Run[] = [
      { id: "draft", experiment_id: "E", review_status: "draft" },
      { id: "review", experiment_id: "E", review_status: "pending_review" },
      { id: "approved", experiment_id: "E", review_status: "approved" },
      { id: "queued", experiment_id: "E", review_status: "approved", execution_authorized_at: "now" },
      { id: "analysis", experiment_id: "E", workflow_version: 2, workflow_stage: "analysis_pending" },
    ];
    const data = dashboard(runs);
    expect(runs.map((run) => classifyRun(run, data))).toEqual(["design", "review", "approved", "queued", "analysis"]);
  });

  it("prioritizes durable dispatch and historical legacy records", () => {
    const runs: Run[] = [
      { id: "running", experiment_id: "E" },
      { id: "legacy", experiment_id: "E", execution_authorization_consumed_at: "old" },
      { id: "historical-failure", experiment_id: "E", status: "failed_implementation_no_scientific_output" },
    ];
    const data = dashboard(runs, {
      execution_outbox: { items: [{ run_id: "running", status: "running" }] },
      reconciliation: { anomalies: [{ run_id: "legacy", type: "legacy_consumed_untracked" }] },
    });
    expect(classifyRun(runs[0], data)).toBe("running");
    expect(classifyRun(runs[1], data)).toBe("legacy");
    expect(classifyRun(runs[2], data)).toBe("legacy");
    const counts = pipelineCounts(runs, data);
    expect(counts.running).toBe(1);
    expect(counts.legacy).toBe(2);
  });
});

describe("run journey", () => {
  it("reduces workflow states to the direct implementation and Steward flow", () => {
    expect(describeRunJourney({ id: "R-1", workflow_stage: "research_design" } as Run).current).toBe("implement");
    expect(describeRunJourney({ id: "R-2", workflow_stage: "code_planning" } as Run).current).toBe("implement");
    expect(describeRunJourney({ id: "R-3", workflow_stage: "analysis_pending" } as Run).current).toBe("results");
  });
});
