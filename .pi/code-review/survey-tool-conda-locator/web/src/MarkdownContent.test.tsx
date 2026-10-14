import { describe,expect,it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { MarkdownContent,parseMarkdown } from "./MarkdownContent";
describe("MarkdownContent",()=>{it("parses tables lists and fenced code",()=>{const blocks=parseMarkdown("| A | B |\n|---|---|\n| 一 | 二 |\n\n- x\n- y\n\n```py\nprint(1)\n```");expect(blocks.map((x)=>x.type)).toEqual(["table","list","code"])});it("does not create unsafe links",()=>{const html=renderToStaticMarkup(<MarkdownContent>{"[safe](https://example.com) [bad](javascript:alert(1)) [also bad](//example.com)"}</MarkdownContent>);expect(html).toContain('href="https://example.com"');expect(html).not.toContain("javascript:");expect(html).not.toContain('href="//example.com"');expect(html).toContain("bad")})});
