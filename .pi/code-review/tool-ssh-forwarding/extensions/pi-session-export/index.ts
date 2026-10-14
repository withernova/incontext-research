import { spawn } from "node:child_process";
import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

function run(command:string,args:string[]):Promise<{code:number;stderr:string}> {
  return new Promise((resolve,reject) => {
    const child=spawn(command,args,{stdio:["ignore","ignore","pipe"],shell:false}); let stderr="";
    child.stderr.on("data",chunk => { stderr+=String(chunk); });
    child.on("error",reject); child.on("close",code => resolve({code:code??1,stderr}));
  });
}

export default function(pi:ExtensionAPI) {
  const entry=fileURLToPath(import.meta.url);
  const exporter=path.resolve(path.dirname(entry),"..","..","scripts","pi_session_export.py");

  pi.registerCommand("export-copyable",{
    description:"Export the current Pi session as copy-friendly HTML (per-message raw Markdown copy)",
    async handler(args:string,ctx:any) {
      const session=ctx.sessionManager.getSessionFile();
      if(!session || !fs.existsSync(session)) {
        ctx.ui.notify("当前会话尚未保存；先发送一条消息后再导出。","error"); return;
      }
      if(!fs.existsSync(exporter)) {
        ctx.ui.notify("Survey Tool 的 pi_session_export.py 不存在，无法导出。","error"); return;
      }
      const requested=String(args||"").trim();
      if(requested.startsWith("-")) {
        ctx.ui.notify("用法：/export-copyable [相对或绝对输出.html路径]","warn"); return;
      }
      const output=requested
        ? path.resolve(ctx.cwd,requested)
        : path.resolve(ctx.cwd,`${path.basename(session,".jsonl")}.copyable.html`);
      if(path.extname(output).toLowerCase()!==".html") {
        ctx.ui.notify("输出文件必须以 .html 结尾。","error"); return;
      }
      const result=await run(process.env.PYTHON||"python3",[exporter,session,output]);
      if(result.code!==0) {
        ctx.ui.notify(`导出失败：${result.stderr.trim().slice(-800)||"unknown error"}`,"error"); return;
      }
      ctx.ui.notify(`已导出可复制 Markdown 的 session：${output}`,"info");
    },
  });
}
