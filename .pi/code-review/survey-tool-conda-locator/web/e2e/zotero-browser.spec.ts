import { expect, test } from "@playwright/test";

test("Zotero batch keeps successful rows, retries failures and distinguishes local PDFs", async ({page}) => {
  test.skip(process.env.SURVEY_TOOL_COMPONENT_TESTS !== "1", "Requires the Vite component fixture server");
  // Run with SURVEY_TOOL_URL pointing to a Vite dev server.
  await page.goto("/v2/e2e/zotero-fixture.html");
  await expect(page.getByRole("button",{name:"已在论文库"})).toBeDisabled();
  await expect(page.getByRole("button",{name:"仅添加文献信息"})).toBeVisible();
  await page.getByRole("checkbox",{name:"仅有本地 PDF"}).check();
  await expect(page.getByText("Metadata Only",{exact:true})).toHaveCount(0);
  await page.getByRole("button",{name:"选择当前结果"}).click();
  await page.getByRole("button",{name:"添加所选（2）"}).click();
  await expect(page.getByRole("status")).toContainText("已添加 1 篇，1 篇未成功");
  await expect(page.getByRole("button",{name:"已添加 · 查看任务"})).toHaveCount(1);
  await page.getByRole("button",{name:"添加所选（1）"}).click();
  await expect(page.getByRole("button",{name:"已添加 · 查看任务"})).toHaveCount(2);
  await page.getByRole("checkbox",{name:"仅未添加"}).check();
  await expect(page.getByText(/没有符合条件的论文/)).toBeVisible();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth)).toBeLessThanOrEqual(1);
});
