export type CodeBlock = { language: string; text: string };

export function codeBlocks(markdown: string): CodeBlock[] {
  const lines = markdown.replace(/\r\n/g, "\n").split("\n");
  const blocks: CodeBlock[] = [];
  let fence = "", language = "", body: string[] = [];
  for (const line of lines) {
    if (!fence) {
      const match = line.match(/^ {0,3}(`{3,}|~{3,})([^\r\n]*)$/);
      if (match) { fence = match[1]; language = match[2].trim().split(/\s/)[0]; body = []; }
    } else if (new RegExp(`^ {0,3}${fence[0]}{${fence.length},}[ \\t]*$`).test(line)) {
      if (body.length) blocks.push({language, text: body.join("\n") + "\n"});
      fence = "";
    } else body.push(line);
  }
  // An unfinished streamed fence is not a complete command.
  return blocks;
}

export function recentCodeBlocks(entries: any[]): CodeBlock[] {
  const result: CodeBlock[] = [];
  for (const entry of [...entries].reverse()) {
    if (entry.type !== "message" || entry.message?.role !== "assistant") continue;
    const content = entry.message.content;
    const text = typeof content === "string" ? content : (content || []).filter((part: any) => part.type === "text").map((part: any) => part.text).join("\n");
    result.push(...codeBlocks(text));
    if (result.length >= 30) break;
  }
  return result.slice(0, 30);
}

export function shellWarnings(text: string): string[] {
  const warnings: string[] = [];
  if (/\\[ \t]+\n/.test(text)) warnings.push("反斜杠后有空格，不能作为 Bash 续行。");
  if (/\\\n[ \t]*\n/.test(text)) warnings.push("反斜杠续行后有空行，可能导致命令提前结束。");
  if (/=\/[^\s]+\n[ \t]*[A-Za-z0-9_.\/-]+/.test(text)) warnings.push("路径参数疑似被硬换行截断；请对照原始路径编辑，不能自动猜测拼接。");
  return warnings;
}

export function bashSingleLine(text: string): string {
  const lines = text.replace(/\r\n/g, "\n").replace(/\n$/, "").split("\n");
  const parts: string[] = [];
  for (const [index, line] of lines.entries()) {
    let quote = "", escaped = false;
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      if (escaped) { escaped = false; continue; }
      if (char === "\\" && quote !== "'") { escaped = true; continue; }
      if (char === quote) { quote = ""; continue; }
      if (!quote && (char === "'" || char === '"')) { quote = char; continue; }
      if (quote === "'") continue;
      if (char === "`" || (char === "$" && line[i + 1] === "(")) throw new Error("包含命令替换，请使用原样复制。");
      if (!quote && ((char === "#" && (i === 0 || /\s/.test(line[i-1]))) || (char === "<" && line[i+1] === "<"))) throw new Error("包含注释或 heredoc，请使用原样复制。");
    }
    if (quote) throw new Error("包含跨行或未闭合引号，请使用原样复制或编辑。");
    if (index < lines.length - 1) {
      if (!escaped) throw new Error("存在没有反斜杠续行的换行（可能是空行、断开的路径或多条命令），无法安全转换。");
      // Remove only backslash-newline: adding a space can split a wrapped token.
      parts.push(line.slice(0, -1));
    } else {
      if (escaped || !line.trim()) throw new Error("代码块以未完成的续行结束。");
      parts.push(line);
    }
  }
  return parts.join("");
}
