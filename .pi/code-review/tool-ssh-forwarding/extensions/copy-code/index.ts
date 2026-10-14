import { copyToClipboard, type ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { bashSingleLine, recentCodeBlocks, shellWarnings } from "./core.js";

export default function(pi: ExtensionAPI) {
  pi.registerCommand("copy-code", {
    description: "Copy original code blocks without terminal wrapping; optional Bash single-line conversion",
    async handler(args: string, ctx: any) {
      if (!ctx.hasUI) { ctx.ui.notify("/copy-code 需要交互终端。", "error"); return; }
      const blocks = recentCodeBlocks(ctx.sessionManager.getBranch());
      if (!blocks.length) { ctx.ui.notify("当前会话分支尚无完整的助手代码块。", "warn"); return; }
      const requested = args.trim();
      if (requested && !/^[1-9]\d*$/.test(requested)) { ctx.ui.notify("用法：/copy-code [代码块序号]", "warn"); return; }
      let index = requested ? Number(requested) - 1 : -1;
      if (!requested) {
        const labels = blocks.map((block, i) => `${i+1}. ${block.language || "text"} · ${block.text.split("\n")[0].slice(0,100)}`);
        const choice = await ctx.ui.select("选择原始代码块（最近回复优先）", labels);
        if (!choice) return;
        index = labels.indexOf(choice);
      }
      const block = blocks[index];
      if (!block) { ctx.ui.notify("代码块序号超出范围。", "error"); return; }
      const shell = ["bash", "sh", "shell", "zsh", "console", ""].includes(block.language.toLowerCase());
      const modes = ["原样复制", ...(shell ? ["Bash 单行复制（仅合并明确续行）"] : []), "编辑后复制"];
      const mode = await ctx.ui.select("复制方式（只复制，不执行）", modes);
      if (!mode) return;
      try {
        let text = block.text;
        if (mode.startsWith("Bash")) text = bashSingleLine(text);
        if (mode === "编辑后复制") {
          const edited = await ctx.ui.editor("检查并编辑原始代码；提交后复制，不执行", text);
          if (edited === undefined) return;
          text = edited;
        }
        const warnings = shell ? shellWarnings(text) : [];
        if (warnings.length && !await ctx.ui.confirm("原文存在可疑换行", warnings.join("\n") + "\n仍按当前内容复制？")) return;
        await copyToClipboard(text);
        ctx.ui.notify(`已发送到剪贴板（${text.length} 字符），未执行。${text.endsWith("\n") ? "保留了末尾换行；粘贴到 shell 时请留意终端行为。" : ""}`, "info");
      } catch (error: any) { ctx.ui.notify(`未复制：${error.message || error}`, "error"); }
    },
  });
}
