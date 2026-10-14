import { describe, expect, it } from "vitest";
import { discussionPreviewPayload, initialDiscussionRequest, RUN_IMPLEMENTATION_DEFAULT_REQUEST } from "./aiDiscussionModel";

describe("discussionPreviewPayload",()=>{
  it("preserves paper candidate target and bounded focus selection",()=>{
    expect(discussionPreviewPayload("paper_candidate","PC-safe","terminal_pi","review","核验证据","evidence")).toEqual({target_type:"paper_candidate",target_id:"PC-safe",mode:"terminal_pi",task:"review",request:"核验证据",focus:"evidence",reference_ids:[],discussion_summary:""});
    expect(discussionPreviewPayload("experiment","E-1","terminal_pi","code_edit","修改代码","whole",["Q-1","paper-x"],"采用 A")).toMatchObject({reference_ids:["Q-1","paper-x"],discussion_summary:"采用 A"});
    expect(discussionPreviewPayload("run","R-1","terminal_pi","run_implementation","实现并调试","whole")).toMatchObject({target_type:"run",task:"run_implementation",request:"实现并调试"});
    expect(discussionPreviewPayload("experiment","E-1","external_gpt","review","看真实代码","whole",[],"","W-code")).toMatchObject({code_repository_id:"W-code"});
  });
  it("gives the direct Run implementation entry a concrete concise intent",()=>{
    expect(initialDiscussionRequest("run_implementation")).toBe(RUN_IMPLEMENTATION_DEFAULT_REQUEST);
    expect(initialDiscussionRequest("code_edit")).toBe("");
    expect(RUN_IMPLEMENTATION_DEFAULT_REQUEST).toContain("当前 Run");
  });
});
