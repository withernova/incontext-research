import { expect, test } from "@playwright/test";

test("discussion reference search refreshes new paper identities and submits selected citekey", async ({page})=>{
  test.skip(process.env.SURVEY_TOOL_COMPONENT_TESTS!=="1","Requires Vite component fixtures");
  let indexed=false; let submitted:string[]=[];
  await page.route("**/api/**",async route=>{
    const url=route.request().url();
    if(url.endsWith("/objects"))return route.fulfill({json:{objects:indexed?[
      {id:"jiang2024devilsin",type:"paper",title:"Devils in Middle Layers of Large Vision-Language Models",canonical_path:"papers/devils.pdf"},
      {id:"makelvlm2025",type:"paper",title:"Make LVLMs Focus: Context-Aware Attention Modulation",canonical_path:"papers/focus.pdf"},
    ]:[]}});
    if(route.request().method()==="POST"){submitted=route.request().postDataJSON().reference_ids||[];return route.fulfill({json:{prompt:"Test preview"}})}
    return route.fulfill({json:{}});
  });
  await page.goto("/v2/e2e/reference-fixture.html");
  const search=page.getByRole("textbox",{name:"搜索 Run、Question、Paper、Finding 等"});
  await search.fill("Devils in Middle");
  await expect(page.getByText("没有匹配对象。",{exact:true})).toBeVisible();
  indexed=true;await page.evaluate(()=>window.dispatchEvent(new Event("focus")));
  await page.getByRole("button",{name:/Devils in Middle Layers/}).click();
  await search.fill("Make LVLMs");
  await page.getByRole("button",{name:/Make LVLMs Focus/}).click();
  await page.getByRole("textbox",{name:"具体讨论问题"}).fill("比较两篇新论文");
  await page.getByRole("button",{name:"生成轻量讨论 Prompt"}).click();
  await expect.poll(()=>submitted).toEqual(["jiang2024devilsin","makelvlm2025"]);
});
