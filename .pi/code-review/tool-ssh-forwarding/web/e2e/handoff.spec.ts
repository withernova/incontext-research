import {expect,test} from "@playwright/test";
test("handoff with no questions shows proposal and confirms without Run execution",async({page})=>{
  test.skip(process.env.SURVEY_TOOL_COMPONENT_TESTS!=="1","Requires Vite component fixtures");
  await page.goto("/v2/e2e/handoff-fixture.html");
  await expect(page.getByRole("heading",{name:"待确认方案"})).toBeVisible();
  await expect(page.getByText("没有额外待答问题",{exact:false})).toBeVisible();
  await page.getByRole("textbox",{name:"研究目标"}).fill("修订后目标");
  await page.getByRole("button",{name:"确认方案，继续准备 Run"}).click();
  await expect(page.getByText("E-012 · 已确认",{exact:true})).toBeVisible();
  await expect(page.getByRole("textbox",{name:"研究目标"})).toHaveValue("修订后目标");
  await expect(page.getByRole("button",{name:"确认方案，继续准备 Run"})).toHaveCount(0);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth)).toBeLessThanOrEqual(1);
});
