import { afterEach, describe, expect, it, vi } from "vitest";
import { createHerdrLaunchRequestDraft, loadEnvironmentBindings, loadHerdrLaunchRequests, previewWorkspaceRuleDraft, reviewV2Run, transitionHerdrLaunchRequest, updateV2WorkspaceBinding } from "./api";
import type { HerdrLaunchRequest } from "./api";

const request: HerdrLaunchRequest = {
  id: "HLR-test", lifecycle_status: "draft", revision: 1, target_object_id: "Q-test",
  agent_kind: "codex", task_type: "analysis", task_summary: "Review evidence",
  safe_config: { reasoning_effort: "medium", max_turns: 3 },
  created_at: "2026-08-16T00:00:00Z", updated_at: "2026-08-16T00:00:00Z",
};

describe("Herdr launch request API helpers", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("uses only governance endpoints and exact confirmation phrases", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ initialized: true, launch_requests: [request], launch_request: request }) });
    vi.stubGlobal("fetch", fetchMock);
    await loadHerdrLaunchRequests("/safe project");
    await createHerdrLaunchRequestDraft("/safe project", { target_object_id: "Q-test", agent_kind: "codex", task_type: "analysis", task_summary: "Review evidence", safe_config: { reasoning_effort: "medium", max_turns: 3 } });
    await transitionHerdrLaunchRequest("/safe project", request, "awaiting_approval");
    await transitionHerdrLaunchRequest("/safe project", { ...request, lifecycle_status: "awaiting_approval", revision: 2 }, "approved");
    await transitionHerdrLaunchRequest("/safe project", request, "cancelled");

    expect(fetchMock.mock.calls[0][0]).toBe("/api/v2/p/%2Fsafe%20project/herdr-launch-requests");
    const bodies = fetchMock.mock.calls.slice(1).map((call) => JSON.parse(String(call[1]?.body)));
    expect(bodies.map((body) => body.confirmation)).toEqual([
      "CREATE HERDR LAUNCH REQUEST DRAFT",
      "SUBMIT HERDR LAUNCH REQUEST FOR APPROVAL",
      "APPROVE HERDR LAUNCH REQUEST",
      "CANCEL HERDR LAUNCH REQUEST",
    ]);
    expect(bodies[0].launch_request).toEqual({ target_object_id: "Q-test", agent_kind: "codex", task_type: "analysis", task_summary: "Review evidence", safe_config: { reasoning_effort: "medium", max_turns: 3 } });
    expect(bodies.some((body) => "command" in body || "prompt" in body || "cwd" in body || "environment" in body)).toBe(false);
  });

  it("reports the exact method and path for missing Run and Workspace routes", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: false, status: 404, statusText: "Not Found", json: async () => ({ error: "not found" }) });
    vi.stubGlobal("fetch", fetchMock);
    await expect(reviewV2Run("/safe project", { id: "R-safe", experiment_id: "E-safe", updated: "v1" }, "submit")).rejects.toThrow("not found（POST /api/v2/p/%2Fsafe%20project/runs/R-safe/review）");
    await expect(updateV2WorkspaceBinding("/safe project", "W-01", "hash", {})).rejects.toThrow("not found（PUT /api/v2/p/%2Fsafe%20project/workspaces/W-01）");
    await expect(loadEnvironmentBindings("/safe project")).rejects.toThrow("not found（GET /api/v2/p/%2Fsafe%20project/environment-bindings）");
    await expect(previewWorkspaceRuleDraft("/safe project","research_safe","数据只读",{server_id:"S-01"})).rejects.toThrow("not found（POST /api/v2/p/%2Fsafe%20project/rule-drafts/preview）");
  });

  it("requests AI-first organization without coupling it to Workspace save", async () => {
    const payload={contract:"survey-tool.rule-draft/v1",scope:"workspace",original_request:"隔绝外界",preset:{id:"custom",label:"自定义",description:""},rules:[],structured_preview:{environment_policy:{},execution_isolation:{mode:"none",required:true,network:"none",deny_read_roots:[],notes:""},dataset_bindings:[]},warnings:[],questions:[],read_only:true,organizer:{requested:"ai_auto",used:"ai",reason:"validated"}};
    const fetchMock=vi.fn().mockResolvedValue({ok:true,json:async()=>payload});vi.stubGlobal("fetch",fetchMock);
    await previewWorkspaceRuleDraft("/safe project","custom","隔绝外界",{server_id:"S-01"});
    const body=JSON.parse(String(fetchMock.mock.calls[0][1]?.body));expect(body.organizer).toBe("ai_auto");expect(body).not.toHaveProperty("confirmation");
  });
});
