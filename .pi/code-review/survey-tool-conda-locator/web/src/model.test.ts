import { describe, expect, it } from "vitest";
import { buildAttentionItems, buildRecentActivity } from "./model";
import type { WorkspaceData } from "./types";

const base: WorkspaceData = {
  project: {
    name: "demo",
    label: "Demo",
    path: "/demo",
    state: "ACTIVE",
    iteration: 1,
    blockers: [],
    next_actions: [],
  },
  papers: [],
  questions: [],
  ideas: [],
  intake: { repo_path:"",project_slug:"",project_name:"",idea:"",domain:"",target_venue:"",polite_email:"",seed_papers:[],constraints:[],notes:"",_canonical_rev:"sha256:" },
  comparisons: [],
  explorations: [],
  dashboard: { experiments: [], runs: [] },
  capabilities: { api_version: 2, storage_schema_version: 1, features: {} },
};

describe("buildAttentionItems", () => {
  it("shows a calm state when no gate needs attention", () => {
    expect(buildAttentionItems(base)[0].title).toContain("没有需要立即处理");
  });

  it("prioritizes project blockers and review gates", () => {
    const data: WorkspaceData = {
      ...base,
      project: { ...base.project, blockers: ["- 数据定义待确认"] },
      dashboard: {
        experiments: [],
        runs: [{ id: "R-1", experiment_id: "E-1", review_status: "pending_review" }],
      },
    };
    const items = buildAttentionItems(data);
    expect(items.map((item) => item.eyebrow)).toEqual(["项目阻塞", "Run 审核"]);
    expect(items[1].navId).toBe("experiments");
  });

  it("builds a sorted activity feed from persistent objects and runs", () => {
    const data:WorkspaceData={...base,dashboard:{experiments:[],runs:[{id:"R-1",experiment_id:"E-1",variant:"New run",updated:"2026-08-27T10:00:00Z"}]}};
    const activity=buildRecentActivity(data,{initialized:true,relations:[],summary:{question:1},objects:[{id:"Q-1",type:"question",title:"Older question",lifecycle_status:"current",canonical_path:"questions/Q-1.md",revision:1,created_at:"2026-08-26T10:00:00Z",updated_at:"2026-08-26T10:00:00Z"}]});
    expect(activity.map(item=>item.id)).toEqual(["run:R-1","object:Q-1"]);
    expect(activity[0]).toMatchObject({navId:"experiments",kind:"Run"});
  });
});
