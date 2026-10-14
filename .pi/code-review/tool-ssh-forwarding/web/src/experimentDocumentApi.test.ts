import { afterEach, describe, expect, it, vi } from "vitest";
import { loadExperimentDocument, loadExperimentDocuments, refreshExperimentDocuments } from "./api";

describe("Experiment document API helpers",()=>{
  afterEach(()=>vi.unstubAllGlobals());
  it("scopes search, directory filters and content reads to the selected Experiment",async()=>{
    const fetchMock=vi.fn().mockResolvedValue({ok:true,json:async()=>({experiment_id:"E-013"})});
    vi.stubGlobal("fetch",fetchMock);
    const controller=new AbortController();
    await loadExperimentDocuments("/project with spaces","E-013",{q:"定位误差",directory:"analysis/sub",kind:"topic",sort:"modified"},controller.signal);
    await loadExperimentDocument("/project with spaces","E-013","analysis/sub/report.md",controller.signal);
    const listing=new URL(fetchMock.mock.calls[0][0],"http://localhost");
    expect(listing.pathname).toBe("/api/v2/p/%2Fproject%20with%20spaces/experiments/E-013/documents");
    expect(listing.searchParams.get("directory")).toBe("analysis/sub");
    expect(listing.searchParams.get("q")).toBe("定位误差");
    expect(fetchMock.mock.calls[0][1].signal).toBe(controller.signal);
    const content=new URL(fetchMock.mock.calls[1][0],"http://localhost");
    expect(content.pathname).toContain("/experiments/E-013/documents/content");
    expect(content.searchParams.get("path")).toBe("analysis/sub/report.md");
    expect(fetchMock.mock.calls.every(call=>!call[1].method&&!call[1].body)).toBe(true);
  });
  it("requires a confirmation tied to exactly one Experiment for navigation refresh",async()=>{
    const fetchMock=vi.fn().mockResolvedValue({ok:true,json:async()=>({experiment_id:"E-013",writes:true,paths:[]})});vi.stubGlobal("fetch",fetchMock);
    await refreshExperimentDocuments("/project","E-013");
    expect(fetchMock.mock.calls[0][0]).toContain("/experiments/E-013/documents/refresh");
    expect(fetchMock.mock.calls[0][1].method).toBe("POST");
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({confirmation:"REFRESH EXPERIMENT DOCUMENTS E-013"});
  });
});
