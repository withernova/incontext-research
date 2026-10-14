import { describe, expect, it } from "vitest";
import { resolveExperimentDocumentLink, stripDocumentProperties } from "./experimentDocumentModel";

describe("Experiment-local document navigation",()=>{
  it("resolves nested reports and valid parent links inside the same Experiment",()=>{
    expect(resolveExperimentDocumentLink("analysis/report.md","../diagnostics/report.md#result")).toBe("diagnostics/report.md");
    expect(resolveExperimentDocumentLink("report.md","analysis/%E6%96%B0%E6%8A%A5%E5%91%8A.md")).toBe("analysis/新报告.md");
    expect(resolveExperimentDocumentLink("analysis/report.md","current.md")).toBe("analysis/current.md");
  });
  it("rejects other experiments, root escape, hidden files and external schemes",()=>{
    for(const href of ["../../E-012/report.md","../E-012/report.md","E-013/report.md","../../report.md","/report.md","%2Freport.md","https://example.org/report.md","javascript:alert(1)",".private.md","report.pdf","%not-valid","a%5Cb.md"]){
      expect(resolveExperimentDocumentLink("analysis/report.md",href),href).toBeNull();
    }
  });
  it("hides properties only in the display, without changing the original Markdown",()=>{
    const source="---\ndoc_status: current\n---\n# 报告\n正文";
    expect(stripDocumentProperties(source)).toBe("# 报告\n正文");
    expect(source).toContain("doc_status: current");
    expect(stripDocumentProperties("# 报告\n---\n正文")).toBe("# 报告\n---\n正文");
  });
});
