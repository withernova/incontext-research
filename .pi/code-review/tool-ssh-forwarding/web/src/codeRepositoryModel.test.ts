import {describe,expect,it} from "vitest";
import {projectRepositoryPath} from "./codeRepositoryModel";

describe("project-owned code repository path",()=>{
 it("places the clone under the selected research project and Workspace",()=>{
  expect(projectRepositoryPath("/Users/saul/Projects/incontext/code-repositories/","03","https://github.com/withernova/iploc-szy.git")).toBe("/Users/saul/Projects/incontext/code-repositories/03/iploc-szy");
 });
 it("rejects traversal identities and invalid repositories",()=>{
  expect(projectRepositoryPath("/project/code-repositories","../other","https://github.com/owner/repo")).toBe("");
  expect(projectRepositoryPath("/project/code-repositories","W","https://github.com/owner/..")).toBe("");
  expect(projectRepositoryPath("/project/code-repositories","W","https://credential@github.com/owner/repo")).toBe("");
  expect(projectRepositoryPath("relative","W","https://github.com/owner/repo")).toBe("");
 });
});
