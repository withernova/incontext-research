import {expect,test} from "@playwright/test";

test.describe("Local code repository binding",()=>{
 test.skip(process.env.SURVEY_TOOL_COMPONENT_TESTS!=="1","Requires Vite fixtures");
 test("saves real repository and per-machine path without network sync or execution",async({page})=>{
  const writes:{path:string;body:any}[]=[];
  const data={servers:[{id:"S",label:"GPU",ssh_host:"fixture-host"}],workspaces:[{id:"W",label:"实验环境",server_id:"S",remote_repo:"/srv/code"}],servers_hash:"servers",workspaces_hash:"workspaces",authority:"legacy-json"};
  await page.route("**/api/v2/**",route=>{
   if(route.request().method()==="GET")return route.fulfill({contentType:"application/json",body:JSON.stringify(data)});
   writes.push({path:new URL(route.request().url()).pathname,body:route.request().postDataJSON()});
   return route.fulfill({contentType:"application/json",body:JSON.stringify(data)});
  });
  await page.goto("/v2/e2e/code-binding-fixture.html");
  await page.getByLabel("开发方式").selectOption("local-git");
  await expect(page.getByLabel("代码仓库 GitHub 地址")).toHaveValue("https://github.com/withernova/iploc-szy");
  await expect(page.getByText("远端代码改动自动 commit/push",{exact:false})).toBeVisible();
  await expect(page.getByText("立即 code publish 到绑定分支，不另行确认 push",{exact:false})).toBeVisible();
  await expect(page.getByRole("button",{name:"保存配置",exact:true})).toBeDisabled();
  await page.getByLabel("同步分支（必填，不猜默认分支）").fill("main");
  await page.getByLabel("代码存放位置").selectOption("external");
  await page.getByLabel("本机代码目录（Survey Tool 服务所在机器）").fill("/Users/saul/Projects/iploc-szy");
  await expect(page.getByText("路径按机器保存。",{exact:false})).toBeVisible();
  expect(writes).toHaveLength(0);
  await page.getByRole("button",{name:"保存配置",exact:true}).click();
  await expect(page.locator(".binding-form")).toHaveCount(0);
  expect(writes).toHaveLength(1);
  expect(writes[0].path).toMatch(/\/workspaces\/W$/);
  expect(writes[0].body.fields.code_development).toEqual({mode:"local-git",repository_url:"https://github.com/withernova/iploc-szy",branch:"main",storage:"external"});
  expect(writes[0].body.fields.local_code_repo).toBe("/Users/saul/Projects/iploc-szy");
 });
 test("defaults to automatic discovery without requiring manual repository fields",async({page})=>{
  const writes:any[]=[];
  const data={servers:[{id:"S",ssh_host:"fixture-host"}],workspaces:[{id:"W",server_id:"S",remote_repo:"/srv/code"}],servers_hash:"servers",workspaces_hash:"workspaces",authority:"legacy-json"};
  await page.route("**/api/v2/**",route=>{
   if(route.request().method()!=="GET")writes.push(route.request().postDataJSON());
   return route.fulfill({contentType:"application/json",body:JSON.stringify(data)});
  });
  await page.goto("/v2/e2e/code-binding-fixture.html");
  await expect(page.getByLabel("开发方式")).toHaveValue("auto");
  await expect(page.getByText("无需手填仓库、分支和本机路径。",{exact:false})).toBeVisible();
  await expect(page.getByLabel("代码仓库 GitHub 地址")).toHaveCount(0);
  await expect(page.getByRole("button",{name:"保存配置",exact:true})).toBeEnabled();
  expect(writes).toHaveLength(0);
  await page.getByRole("button",{name:"保存配置",exact:true}).click();
  await expect(page.locator(".binding-form")).toHaveCount(0);
  expect(writes).toHaveLength(1);
  expect(writes[0].fields.code_development).toEqual({mode:"auto"});
  expect(writes[0].fields.local_code_repo).toBeUndefined();
 });
 test("defaults to a read-only project directory and does not clone on save",async({page})=>{
  const writes:any[]=[];
  const data={project_code_root:"/fixture/code-repositories",servers:[{id:"S",ssh_host:"fixture-host"}],workspaces:[{id:"W",server_id:"S",remote_repo:"/srv/code"}],servers_hash:"servers",workspaces_hash:"workspaces",authority:"legacy-json"};
  await page.route("**/api/v2/**",route=>{
   if(route.request().method()!=="GET")writes.push(route.request().postDataJSON());
   return route.fulfill({contentType:"application/json",body:JSON.stringify(data)});
  });
  await page.goto("/v2/e2e/code-binding-fixture.html");
  await page.getByLabel("开发方式").selectOption("local-git");
  await expect(page.getByLabel("代码存放位置")).toHaveValue("project");
  await expect(page.getByLabel("项目内代码目录")).toHaveValue("/fixture/code-repositories/W/iploc-szy");
  await expect(page.getByLabel("项目内代码目录")).toHaveAttribute("readonly","");
  await expect(page.getByRole("button",{name:"保存配置",exact:true})).toBeDisabled();
  await page.getByLabel("同步分支（必填，不猜默认分支）").fill("main");
  await page.getByRole("button",{name:"保存配置",exact:true}).click();
  await expect(page.locator(".binding-form")).toHaveCount(0);
  expect(writes).toHaveLength(1);
  expect(writes[0].fields.code_development.storage).toBe("project");
  expect(writes[0].fields.local_code_repo).toBeUndefined();
 });
});
