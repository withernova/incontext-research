import { expect, test } from "@playwright/test";
import type { Locator, Page } from "@playwright/test";

async function expectNoHorizontalOverflow(page: Page) {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(1);
}

async function expectVerticallyStacked(first: Locator, second: Locator) {
  const [firstBox, secondBox] = await Promise.all([first.boundingBox(), second.boundingBox()]);
  expect(firstBox).not.toBeNull();
  expect(secondBox).not.toBeNull();
  expect(secondBox!.y).toBeGreaterThan(firstBox!.y + firstBox!.height);
}

test("workspace renders real project data without horizontal overflow", async ({ page }) => {
  const errors: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  page.on("pageerror", (error) => errors.push(error.message));

  await page.goto("/v2/");
  await expect(page.getByRole("heading", { name: "26-CVPR/incontext" })).toBeVisible();
  await expect(page.getByText("需要处理", { exact: true })).toBeVisible();
  await expect(page.getByText("最近的论文", { exact: true })).toBeVisible();

  const overflow = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    document: document.documentElement.scrollWidth,
  }));
  expect(overflow.document).toBeLessThanOrEqual(overflow.viewport + 1);
  expect(errors).toEqual([]);
});

test("global sidebar can collapse without hiding workspace content", async ({ page }) => {
  await page.goto("/v2/");
  await page.getByRole("button", { name: "收起侧栏" }).click();
  await expect(page.locator(".app-shell")).toHaveClass(/sidebar-collapsed/);
  await expect(page.getByRole("textbox", { name: "全局搜索" })).toBeVisible();
  await expect(page.locator("main.workspace")).toContainText("研究总览");
  await page.getByRole("button", { name: "展开侧栏" }).click();
  await expect(page.locator(".app-shell")).not.toHaveClass(/sidebar-collapsed/);
});

test("global search finds and navigates to an experiment", async ({ page }) => {
  await page.goto("/v2/");
  const search = page.getByRole("textbox", { name: "全局搜索" });
  await search.fill("IPLoc-ID");
  const result = page.locator(".search-results button").filter({ hasText: "Experiment" }).first();
  await expect(result).toContainText("IPLoc-ID");
  await result.click();
  await expect(search).toHaveValue("");
  await expect(page.getByRole("heading", { name: "实验", exact: true })).toBeVisible();
});

test("paper library filters catalog and loads canonical detail", async ({ page }) => {
  await page.goto("/v2/");
  await page.getByRole("button", { name: /论文库/ }).first().click();
  await expect(page.getByRole("heading", { name: "论文库" })).toBeVisible();
  await expect(page.locator(".catalog-paper")).toHaveCount(7);
  await expect(page.locator(".paper-detail-head code")).not.toBeEmpty();
  await page.getByRole("button", { name: "收起论文选择" }).click();
  await expect(page.locator(".paper-workspace")).toHaveClass(/selector-collapsed/);
  await expect(page.getByRole("button", { name: "展开论文选择" })).toBeVisible();
  await page.getByRole("button", { name: "展开论文选择" }).click();
  await expect(page.getByRole("button", { name: /七问细读/ })).toHaveAttribute("aria-expanded", "false");
  await expect(page.getByRole("button", { name: /证据产物/ })).toHaveAttribute("aria-expanded", "false");
  await expect(page.locator(".seven-rows")).toHaveCount(0);
  await page.getByRole("button", { name: /七问细读/ }).click();
  await expect(page.locator(".seven-rows>div")).toHaveCount(7);
  await page.getByRole("button", { name: /七问细读/ }).click();
  await expect(page.locator(".seven-rows")).toHaveCount(0);
  await page.getByRole("textbox", { name: "搜索论文库" }).fill("Mechanisms");
  await expect(page.locator(".catalog-paper")).toHaveCount(1);
  await expect(page.locator(".paper-detail-head")).toContainText("Mechanisms");
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(1);
});

test("question workspace keeps judgement separate from claim validation", async ({ page }) => {
  await page.goto("/v2/");
  await page.getByRole("button", { name: /Questions/ }).first().click();
  await expect(page.getByRole("heading", { name: "Questions" })).toBeVisible();
  await expect(page.locator(".question-queue-item")).toHaveCount(4);
  await expect(page.locator(".question-detail-head")).toContainText("Q-001");
  await expect(page.locator(".related-section")).toContainText("E-002");
  await expect(page.locator(".question-trust-note")).toContainText("不会自动晋升为 Finding");
  await page.getByRole("textbox", { name: "搜索 Questions" }).fill("negative rejection");
  await expect(page.locator(".question-queue-item")).toHaveCount(1);
  await expect(page.locator(".question-detail-head")).toContainText("Q-003");
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(1);
});

test("research analysis keeps findings distinct from validated claims", async ({ page }) => {
  await page.goto("/v2/");
  await page.locator(".object-tile.violet").click();
  await expect(page.getByRole("heading", { name: "研究分析" })).toBeVisible();
  await expect(page.locator(".comparison-list-items button")).toHaveCount(4);
  await page.getByRole("button", { name: "收起对比项目选择" }).click();
  await expect(page.locator(".analysis-layout")).toHaveClass(/selector-collapsed/);
  await expect(page.getByRole("button", { name: "展开对比项目选择" })).toBeVisible();
  await page.getByRole("button", { name: "展开对比项目选择" }).click();
  await expect(page.locator(".comparison-detail-panel")).toContainText("test-cmp");
  await expect(page.locator(".comparison-paper-grid article")).toHaveCount(2);
  await expect(page.locator(".analysis-trust-note")).toContainText("R2 对抗审查");
  await expect(page.locator(".finding-list")).toContainText("尚未形成 Finding");
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(1);
});

test("research analysis reflows within a narrow desktop workspace", async ({ page }) => {
  await page.setViewportSize({ width: 940, height: 800 });
  await page.goto("/v2/");
  await page.locator(".object-tile.violet").click();

  const layout = page.locator(".analysis-layout");
  const list = page.locator(".comparison-list-panel");
  const detail = page.locator(".comparison-detail-panel");
  const cards = page.locator(".analysis-two-column .analysis-card");
  await expect(layout).toBeVisible();

  const [layoutBox, listBox, detailBox, firstCard, secondCard] = await Promise.all([
    layout.boundingBox(), list.boundingBox(), detail.boundingBox(),
    cards.nth(0).boundingBox(), cards.nth(1).boundingBox(),
  ]);
  expect(layoutBox).not.toBeNull();
  expect(listBox).not.toBeNull();
  expect(detailBox).not.toBeNull();
  expect(firstCard).not.toBeNull();
  expect(secondCard).not.toBeNull();
  expect(Math.abs(listBox!.width - layoutBox!.width)).toBeLessThanOrEqual(1);
  expect(detailBox!.y).toBeGreaterThan(listBox!.y + listBox!.height);
  expect(secondCard!.y).toBeGreaterThan(firstCard!.y + firstCard!.height);

  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(1);
});

test("master-detail workspaces reflow at a medium desktop width", async ({ page }) => {
  await page.setViewportSize({ width: 1024, height: 850 });
  await page.goto("/v2/");

  await page.locator(".sidebar .nav-item").filter({ hasText: "Ideas" }).click();
  await expect(page.getByRole("heading", { name: "Ideas" })).toBeVisible();
  await expectVerticallyStacked(page.locator(".idea-list-panel"), page.locator(".idea-detail-panel"));
  await expectNoHorizontalOverflow(page);

  await page.locator(".sidebar .nav-item").filter({ hasText: "Questions" }).click();
  await expect(page.getByRole("heading", { name: "Questions" })).toBeVisible();
  await expectVerticallyStacked(page.locator(".question-queue-panel"), page.locator(".question-detail-panel"));
  await expectNoHorizontalOverflow(page);

  await page.locator(".sidebar .nav-item").filter({ hasText: "项目 Intake" }).click();
  await expect(page.getByRole("heading", { name: "项目 Intake" })).toBeVisible();
  await expectVerticallyStacked(page.locator(".intake-form-panel"), page.locator(".intake-materialize-panel"));
  await expectNoHorizontalOverflow(page);

  await page.locator(".sidebar .nav-item").filter({ hasText: "实验" }).click();
  await expect(page.getByRole("heading", { name: "实验", exact: true })).toBeVisible();
  await expectVerticallyStacked(page.locator(".experiment-list-panel"), page.locator(".experiment-v2-main"));
  await expectNoHorizontalOverflow(page);
});

test("run detail subpages reflow independently of the experiment list", async ({ page }) => {
  await page.setViewportSize({ width: 940, height: 850 });
  await page.goto("/v2/");
  await page.locator(".sidebar .nav-item").filter({ hasText: "实验" }).click();
  const runCard = page.locator(".run-folder-card").first();
  await expect(runCard).toBeVisible();
  await runCard.click();
  await expect(page.locator(".run-detail-page")).toBeVisible();
  await expectVerticallyStacked(page.locator(".run-journey-copy"), page.locator(".run-journey ol"));
  await expectVerticallyStacked(page.locator(".run-record-sections>section").nth(0), page.locator(".run-record-sections>section").nth(1));
  await expectNoHorizontalOverflow(page);
});

test("utility workspaces remain usable just above the mobile breakpoint", async ({ page }) => {
  await page.setViewportSize({ width: 800, height: 850 });
  await page.goto("/v2/");

  await page.locator(".sidebar .nav-item").filter({ hasText: "自动化" }).click();
  await expect(page.getByRole("heading", { name: "自动化" })).toBeVisible();
  await expectNoHorizontalOverflow(page);

  await page.locator(".sidebar .nav-item").filter({ hasText: "Agent 配置" }).click();
  await expect(page.getByRole("heading", { name: /Agent 配置/ })).toBeVisible();
  const routeFields = page.locator(".agent-route-fields label");
  await expect(routeFields.first()).toBeVisible();
  await expectVerticallyStacked(routeFields.nth(0), routeFields.nth(1));
  await expectNoHorizontalOverflow(page);

  await page.locator(".sidebar .nav-item").filter({ hasText: "最近活动" }).click();
  await expect(page.getByRole("heading", { name: "最近活动" })).toBeVisible();
  await expectNoHorizontalOverflow(page);
});

test("experiment workspace separates review authorization execution and analysis", async ({ page }) => {
  await page.goto("/v2/");
  await page.locator(".object-tile.red").click();
  await expect(page.getByRole("heading", { name: "实验", exact: true })).toBeVisible();
  await expect(page.locator(".experiment-list-items button")).toHaveCount(7);
  await page.locator(".experiment-list-items button").filter({ hasText: "E-005" }).click();
  await expect(page.locator(".experiment-header")).toContainText("Attention-derived localization-head discovery");
  await page.getByRole("button", { name: /科研完成/ }).click();
  await expect(page.locator(".pipeline-lane.green .run-card").first()).toBeVisible();
  await page.locator(".pipeline-lane.green .run-card").first().click();
  await expect(page.locator(".run-audit-panel")).toContainText("完整性门槛");
  await expect(page.locator(".run-audit-panel")).toContainText("Claim 边界");
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(1);
});

test("automation builder generates bounded commands without claiming execution", async ({ page, context }) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  let automationRevision = 1;
  let automationStatus = "draft";
  let automationPhase = "intake";
  let automationSaved = false;
  let jobStatus = "failed";
  let jobRevision = 3;
  let sessionBound = false;
  let archivedStatus = "completed";
  let archivedRevision = 5;
  const archiveRecords = () => [{ id:"AUTO-archive",type:"automation",title:"Completed research",lifecycle_status:archivedStatus,revision:archivedRevision,impact:{id:"AUTO-archive",type:"automation",title:"Completed research",lifecycle_status:archivedStatus,revision:archivedRevision,jobs:{succeeded:2},relations:1,agent_sessions:1,blockers:[],hard_delete:false,canonical_files_deleted:false,staging_deleted:false}},{id:"PC-busy",type:"paper_candidate",title:"Busy candidate",lifecycle_status:"accepted",revision:2,impact:{id:"PC-busy",type:"paper_candidate",title:"Busy candidate",lifecycle_status:"accepted",revision:2,jobs:{running:1},relations:0,agent_sessions:0,blockers:["object has 1 queued/running jobs"],hard_delete:false,canonical_files_deleted:false,staging_deleted:false}}];
  const sessionRecord = () => ({ id: "AS-test", provider: "pi", status: "stale", object_id: "Q-test", task_type: "research", identity_fingerprint: "sha256:1234567890abcdef", created_at: "2026-08-15T19:30:00+00:00", last_seen_at: "2026-08-15T19:30:00+00:00", revision: 1 });
  const jobRecords = () => [{ id: "JOB-download", kind: "paper_download", status: jobStatus, revision: jobRevision, target_object_id: "PC-test", attempt: 1, error_class: jobStatus === "failed" ? "NetworkError" : "", error_message: jobStatus === "failed" ? "upstream timeout" : "" }, { id: "JOB-mineru", kind: "mineru", status: "queued", revision: 1, target_object_id: "PC-test", depends_on_job_id: "JOB-download", attempt: 0 }];
  const automationRecord = () => ({ id: "AUTO-test", title: "实验自动化 · EXP-001", revision: automationRevision, lifecycle_status: automationStatus, automation_type: "experiment", phase: automationPhase, budget: { duration_minutes: 30, max_rounds: 7, interval_minutes: 1 }, approval: {}, deadline_at: automationStatus === "active" ? "2026-08-15T20:30:00+00:00" : null, events: automationSaved ? [{ id: "EV-test", kind: "automation.transitioned", summary: `Automation AUTO-test -> ${automationStatus}`, occurred_at: "2026-08-15T19:30:00+00:00" }] : [] });
  await page.route("**/api/v2/p/*/initialize", async (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify({ initialized: true, schema_version: 5 }) }));
  await page.route("**/api/v2/p/*/automations", async (route) => {
    if (route.request().method() === "GET") return route.fulfill({ contentType: "application/json", body: JSON.stringify({ initialized: automationSaved, automations: automationSaved ? [automationRecord()] : [] }) });
    automationSaved = true;
    await route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify({ started: false, automation: automationRecord() }) });
  });
  await page.route("**/api/v2/p/*/automations/*/transition", async (route) => {
    const body = route.request().postDataJSON(); automationStatus = body.status; automationPhase = body.phase || automationPhase; automationRevision += 1;
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ execution_started: false, automation: automationRecord() }) });
  });
  await page.route("**/api/v2/p/*/objects/archive", async (route) => { if(route.request().method()==="GET") return route.fulfill({contentType:"application/json",body:JSON.stringify({initialized:true,objects:archiveRecords(),hard_delete_available:false})}); const body=route.request().postDataJSON(); archivedStatus=body.restore?"completed":"archived"; archivedRevision+=1; await route.fulfill({contentType:"application/json",body:JSON.stringify({objects:[{id:"AUTO-archive",type:"automation",lifecycle_status:archivedStatus,revision:archivedRevision}],hard_delete:false,canonical_files_deleted:false})}); });
  await page.route("**/api/v2/p/*/agent-sessions", async (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify({ initialized: sessionBound, sessions: sessionBound ? [sessionRecord()] : [], current_pi: { available: true, status: "stale", session_name: "Verified research session", last_verified_at: "2026-08-15T19:00:00+00:00", identity_fingerprint: "sha256:1234567890abcdef", messages_exposed: false, prompt_exposed: false, session_path_exposed: false } }) }));
  await page.route("**/api/v2/p/*/agent-sessions/bind-current-pi", async (route) => { const body=route.request().postDataJSON(); sessionBound=true; const session={...sessionRecord(),object_id:body.object_id,task_type:body.task_type}; await route.fulfill({ status:201,contentType:"application/json",body:JSON.stringify({session,target:{id:body.object_id,type:"question",authority:"markdown",reference_identity_only:true},messages_copied:false,prompt_copied:false,session_path_copied:false})}); });
  await page.route("**/api/v2/p/*/jobs", async (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify({ initialized: true, jobs: jobRecords() }) }));
  await page.route("**/api/v2/p/*/jobs/JOB-download/retry", async (route) => { jobStatus = "queued"; jobRevision += 1; await route.fulfill({ contentType: "application/json", body: JSON.stringify({ jobs: [jobRecords()[0]], worker_started: false }) }); });
  await page.route("**/api/v2/p/*/jobs/JOB-download/cancel", async (route) => { jobStatus = "cancelled"; jobRevision += 1; await route.fulfill({ contentType: "application/json", body: JSON.stringify({ jobs: jobRecords(), running_process_stopped: false }) }); });
  await page.route("**/api/v2/p/*/migration/dry-run", async (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify({ will_write: false, v2_store: { initialized: false, schema_version: 0 }, summary: { source_groups: 12, existing_groups: 8, source_files: 15, paper_pdfs: 6, warnings: 1 }, identity_index_plan: { will_write: true, blocked: false, summary: { questions: 3, experiments: 2, relations: 1, warnings: 0 }, warnings: [], authority: { question: "markdown", experiment: "legacy_json", sqlite: "identity_and_relation_index_only" } }, identity_index_history: [{ checkpoint_hash: "sha256:checkpoint", status: "applied", applied_at: "2026-08-15T20:00:00+00:00", details: { created: 5, existing: 0, relations_created: 1 } }], warnings: [{ kind: "paper_citation_count_mismatch", path: "papers", message: "requires human reconciliation" }], excluded: [".publish/"] }) }));
  await page.goto("/v2/");
  await page.locator(".object-tile.blue").click();
  await expect(page.getByRole("heading", { name: "自动化", exact: true })).toBeVisible();
  await expect(page.locator(".automation-warning")).toContainText("不是 validated synthesis");
  await expect(page.locator(".archive-safety")).toContainText("Hard delete unavailable");
  await expect(page.locator(".archive-list")).toContainText("object has 1 queued/running jobs");
  page.on("dialog", (dialog) => dialog.type() === "prompt" ? dialog.accept(dialog.message().includes("归档理由") ? "completed and reviewed" : dialog.message().includes("恢复理由") ? "reopened" : "network restored") : dialog.accept());
  await page.locator(".archive-list label").filter({ hasText:"Completed research" }).getByRole("checkbox").check();
  await page.getByRole("button", { name:"确认软归档" }).click();
  await page.getByRole("button", { name:"已归档" }).click();
  await expect(page.locator(".archive-list")).toContainText("Completed research");
  await page.locator(".archive-list label").filter({ hasText:"Completed research" }).getByRole("checkbox").check();
  await page.getByRole("button", { name:"恢复原状态" }).click();
  await page.getByRole("button", { name:"当前", exact:true }).click();
  await expect(page.locator(".archive-list").filter({ hasText:"Completed research" })).toContainText("completed");
  await expect(page.locator(".current-pi-summary")).toContainText("Verified research session");
  await expect(page.locator(".privacy-badges")).toContainText("消息不暴露");
  await expect(page.locator(".privacy-badges")).toContainText("Prompt 不复制");
  await expect(page.locator(".privacy-badges")).toContainText("路径不暴露");
  await expect(page.locator(".agent-session-console")).not.toContainText(".jsonl");
  await page.getByRole("button", { name: "绑定当前已验证 pi" }).click();
  await expect(page.locator(".session-index-list")).toContainText("sha256:1234567890abcdef");
  await expect(page.locator(".session-authority-note")).toContainText("Markdown / legacy JSON");
  await expect(page.locator(".job-console")).toContainText("NetworkError：upstream timeout");
  await expect(page.locator(".job-console")).toContainText("依赖 JOB-download · failed");
  await expect(page.locator(".job-boundary")).toContainText("不提供网页强制取消");
  await page.getByRole("button", { name: "重试" }).click();
  const downloadJob = page.locator(".job-row").filter({ has: page.locator(".job-copy strong", { hasText: /^JOB-download$/ }) });
  await expect(downloadJob).toContainText("queued");
  await downloadJob.getByRole("button", { name: "取消" }).click();
  await expect(downloadJob).toContainText("cancelled");
  await expect(page.locator(".automation-command code")).toContainText("--target-type question");
  await page.getByRole("button", { name: "实验自动化" }).click();
  await expect(page.locator(".automation-command code")).toContainText("--target-type experiment");
  await page.getByLabel("最大轮次").fill("7");
  await expect(page.locator(".automation-command code")).toContainText("--max-rounds 7");
  await page.getByRole("button", { name: "复制命令" }).click();
  await expect(page.getByRole("button", { name: "已复制" })).toBeVisible();
  await expect(page.locator(".guardrail-list")).toContainText("不自动审核、授权、入队或执行");
  await page.getByRole("button", { name: /迁移 Dry-run/ }).click();
  await expect(page.locator(".migration-kpis")).toContainText("15");
  await expect(page.locator(".migration-body")).toContainText("写入动作");
  await expect(page.locator(".migration-body")).toContainText("无");
  await expect(page.locator(".migration-history")).toContainText("sha256:checkpoint");
  await page.getByRole("button", { name: "保存治理草稿" }).click();
  await expect(page.locator(".automation-governance")).toContainText("draft · intake");
  await page.getByRole("button", { name: "提交审批" }).click();
  await expect(page.locator(".automation-governance")).toContainText("awaiting_approval");
  await page.getByRole("button", { name: "人工批准激活" }).click();
  await expect(page.locator(".automation-governance")).toContainText("active · experiment_planning");
  await expect(page.locator(".automation-governance")).toContainText("保存、审批与实际命令执行是三个独立动作");
  await expect(page.locator(".automation-governance")).toContainText("Deadline");
  await expect(page.locator(".automation-history")).toContainText("revision 3");
  await expect(page.locator(".automation-event-log")).toContainText("automation.transitioned");
  await page.reload();
  await page.locator(".object-tile.blue").click();
  await expect(page.locator(".automation-governance")).toContainText("active · experiment_planning");
  await page.getByRole("button", { name: "暂停" }).click();
  await expect(page.locator(".automation-governance")).toContainText("paused · experiment_planning");
  await page.getByRole("button", { name: "人工批准恢复" }).click();
  await expect(page.locator(".automation-governance")).toContainText("active · experiment_planning");
});

test("paper finder keeps search hits visibly unverified", async ({ page }) => {
  let initialized = false;
  let saved = false;
  let staged = false;
  await page.route("**/api/v2/p/*/initialize", async (route) => {
    initialized = true;
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ initialized: true, schema_version: 5 }) });
  });
  await page.route("**/api/v2/p/*/paper-candidates", async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({ contentType: "application/json", body: JSON.stringify({ initialized: true, candidates: saved ? [{ id: "PC-1", citekey: "doe2026causal", source_url: "https://openalex.org/W1", revision: staged ? 2 : 1, lifecycle_status: staged ? "accepted" : "proposed" }] : [] }) });
      return;
    }
    saved = true;
    await route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify({ candidate: { id: "PC-1", citekey: "doe2026causal", source_url: "https://openalex.org/W1", revision: 1, lifecycle_status: "proposed" } }) });
  });
  await page.route("**/api/v2/p/*/jobs", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ initialized: true, jobs: [] }) });
  });
  await page.route("**/api/v2/p/*/paper-candidates/*/acquisition", async (route) => {
    staged = true;
    await route.fulfill({ status: 202, contentType: "application/json", body: JSON.stringify({ candidate: { id: "PC-1", citekey: "doe2026causal", source_url: "https://openalex.org/W1", revision: 2, lifecycle_status: "accepted" }, download_job: { id: "JOB-D", kind: "paper_download", status: "queued", target_object_id: "PC-1" }, mineru_job: { id: "JOB-M", kind: "mineru", status: "queued", target_object_id: "PC-1", depends_on_job_id: "JOB-D" } }) });
  });
  await page.route("**/papers/web-search?*", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        source: "openalex",
        query: "causal localization",
        hits: [{ citekey: "doe2026causal", title: "Causal Localization", authors: ["Jane Doe"], year: "2026", url: "https://openalex.org/W1", oa_url: "https://example.org/paper.pdf", is_oa: true, cited_by_count: 4 }],
      }),
    });
  });
  await page.goto("/v2/");
  await page.getByRole("button", { name: /论文库/ }).first().click();
  await page.getByRole("button", { name: "检索新论文" }).click();
  await page.getByRole("textbox", { name: "候选论文检索词" }).fill("causal localization");
  await page.getByRole("button", { name: "检索", exact: true }).click();
  const candidate = page.locator(".candidate-card");
  await expect(candidate).toContainText("未核验");
  await expect(candidate).toContainText("Causal Localization");
  await expect(candidate.getByRole("link", { name: /查看来源/ })).toHaveAttribute("href", "https://openalex.org/W1");
  await expect(candidate.getByRole("button", { name: "登记候选" })).toBeDisabled();
  page.on("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "启用候选登记" }).click();
  expect(initialized).toBe(true);
  await candidate.getByRole("button", { name: "登记候选" }).click();
  expect(saved).toBe(true);
  await expect(candidate.getByRole("button", { name: "准备 PDF + MinerU" })).toBeVisible();
  await candidate.getByRole("button", { name: "准备 PDF + MinerU" }).click();
  expect(staged).toBe(true);
  await expect(candidate.getByRole("button", { name: "任务已排队" })).toBeVisible();
});
