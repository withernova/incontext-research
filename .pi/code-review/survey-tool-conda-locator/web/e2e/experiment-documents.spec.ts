import { expect, test } from "@playwright/test";

test.describe("Experiment document search interface",()=>{
  test.skip(process.env.SURVEY_TOOL_COMPONENT_TESTS!=="1","Requires Vite component fixtures");
  test("offers a real document tab, nested directory search, reading and independent Experiment switching",async({page})=>{
    const requests:string[]=[];
    const writes:string[]=[];
    await page.route("**/api/v2/p/*/experiments/*/documents**",async route=>{
      const url=new URL(route.request().url());
      const eid=url.pathname.includes("/E-012/")?"E-012":"E-013";
      requests.push(url.pathname+url.search);
      if(route.request().method()!=="GET")writes.push(url.pathname);
      if(url.pathname.endsWith("/refresh"))return route.fulfill({contentType:"application/json",body:JSON.stringify({experiment_id:eid,writes:true,paths:["entry","catalogue","result"]})});
      if(url.pathname.endsWith("/content")){
        const path=url.searchParams.get("path")||"";
        return route.fulfill({contentType:"application/json",body:JSON.stringify({experiment_id:eid,read_only:true,path,project_relative_path:`shell/06_experiments/${eid}/${path}`,title:`${eid} 诊断报告`,content:`# ${eid} 诊断报告\n\n${eid} 专属正文`})});
      }
      const doc={path:"diagnostics/deeper/report.md",title:`${eid} 定位诊断`,kind:"topic",modified:"2026-01-01T01:00:00+00:00",generated:false,topic:"定位误差",status:"current",superseded_by:""};
      const q=url.searchParams.get("q")||"";
      const docs=q&&!`${doc.title}${doc.path}${doc.topic}`.includes(q)?[]:[doc];
      return route.fulfill({contentType:"application/json",body:JSON.stringify({experiment_id:eid,read_only:true,root:`shell/06_experiments/${eid}`,documents:docs,directories:["","diagnostics","diagnostics/deeper"],total:docs.length,indexed_count:1,warnings:[],recency_note:"最近修改不等于有效版本"})});
    });
    await page.goto("/v2/e2e/experiment-documents-fixture.html");
    await page.getByRole("button",{name:"文档",exact:true}).click();
    await expect(page.getByRole("region",{name:"E-012 文档检索"})).toBeVisible();
    await page.getByLabel("文档子目录").selectOption("diagnostics");
    await page.getByLabel("搜索实验文档").fill("定位误差");
    await page.locator(".document-results button").filter({hasText:"E-012 定位诊断"}).click();
    await expect(page.locator(".document-reader")).toContainText("E-012 专属正文");
    await expect(page.locator(".document-reader")).toContainText("shell/06_experiments/E-012/diagnostics/deeper/report.md");
    expect(requests.some(path=>path.includes("directory=diagnostics"))).toBeTruthy();
    expect(requests.some(path=>path.includes("/documents/content?"))).toBeTruthy();
    expect(writes).toEqual([]);
    await page.locator(".experiment-list-items button").filter({hasText:"E-013"}).click();
    await expect(page.getByRole("region",{name:"E-013 文档检索"})).toBeVisible();
    await expect(page.locator(".document-reader")).not.toContainText("E-012 专属正文");
    await expect(page.getByLabel("搜索实验文档")).toHaveValue("");
    await page.locator(".document-results button").filter({hasText:"E-013 定位诊断"}).click();
    await expect(page.locator(".document-reader")).toContainText("E-013 专属正文");
    page.once("dialog",dialog=>dialog.accept());
    await page.getByRole("button",{name:"更新 Obsidian 导航"}).click();
    await expect(page.getByRole("status")).toContainText("已更新 E-013");
    expect(writes).toHaveLength(1);
    expect(writes[0]).toContain("/E-013/documents/refresh");
  });
  test("rejects a response belonging to a different Experiment",async({page})=>{
    await page.route("**/api/v2/p/*/experiments/*/documents**",route=>route.fulfill({contentType:"application/json",body:JSON.stringify({experiment_id:"E-013",read_only:true,root:"shell/06_experiments/E-013",documents:[{path:"foreign.md",title:"外来文档不应显示"}],directories:[""],total:1,indexed_count:1,warnings:[]})}));
    await page.goto("/v2/e2e/experiment-documents-fixture.html");
    await page.getByRole("button",{name:"文档",exact:true}).click();
    await expect(page.getByRole("alert")).toContainText("所属 Experiment 不匹配");
    await expect(page.locator(".document-results button")).toHaveCount(0);
    await expect(page.locator(".experiment-documents-panel")).not.toContainText("外来文档不应显示");
  });
});
