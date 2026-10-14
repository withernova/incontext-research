import { createHash } from "node:crypto";

export interface ChangedFile {
  path: string;
  status: string;
  untracked?: boolean;
  binary?: boolean;
}

export interface ReviewFinding {
  severity: "blocking" | "warning";
  code: string;
  path?: string;
  line?: number;
  message: string;
}

export interface TestEvidence {
  command: string;
  exit_code: number;
  summary?: string;
}

export interface RecordedReview {
  id: string;
  userEntryId: string | null;
  currentUserEntryId: string | null;
  params: { allowed_paths?: string[]; forbidden_paths?: string[] };
  result: Record<string, any> | null;
}

export function latestUserEntryId(entries: readonly any[]): string | null {
  let latest: string | null = null;
  for (const entry of entries) if (entry?.type === "message" && entry.message?.role === "user") latest = String(entry.id || "");
  return latest;
}

/** Replay only the active branch. A newer failed/malformed result revokes an older pass. */
export function latestBranchReview(entries: readonly any[]): RecordedReview | null {
  const calls = new Map<string, Record<string, any>>();
  let latest: RecordedReview | null = null;
  let currentUserEntryId: string | null = null;
  const scope = (value: any) => {
    const out: RecordedReview["params"] = {};
    for (const key of ["allowed_paths", "forbidden_paths"] as const) {
      if (value?.[key] === undefined) continue;
      if (!Array.isArray(value[key]) || value[key].some((item: any) => typeof item !== "string")) return null;
      out[key] = [...value[key]];
    }
    return out;
  };
  for (const entry of entries) {
    if (entry?.type !== "message") continue;
    const msg = entry.message;
    if (msg?.role === "user") currentUserEntryId = String(entry.id || "");
    if (msg?.role === "assistant" && Array.isArray(msg.content)) {
      for (const block of msg.content) {
        if (block?.type === "toolCall" && block.name === "code_change_review") calls.set(block.id, block.arguments || {});
      }
    }
    if (msg?.role !== "toolResult" || msg.toolName !== "code_change_review") continue;
    latest = { id: String(entry.id || msg.toolCallId), userEntryId: currentUserEntryId, currentUserEntryId, params: {}, result: null };
    if (msg.isError) continue;
    let result = msg.details;
    if (result === undefined && Array.isArray(msg.content)) {
      try { result = JSON.parse(msg.content.find((item: any) => item.type === "text")?.text || ""); }
      catch { continue; }
    }
    const params = scope(calls.get(msg.toolCallId) ?? result?.review_scope);
    if (!params || (!calls.has(msg.toolCallId) && !result?.review_scope)
        || result?.contract !== "pi.code-change-review/v1"
        || !/^[a-f0-9]{64}$/.test(result.diff_fingerprint || "")
        || !/^(?:[a-f0-9]{40}|[a-f0-9]{64})$/.test(result.base_revision || "")
        || typeof result.passed !== "boolean" || typeof result.review_current !== "boolean"
        || typeof result.repository?.path !== "string") continue;
    latest = { id: latest.id, userEntryId: latest.userEntryId, currentUserEntryId, params, result };
  }
  if (latest) latest.currentUserEntryId = currentUserEntryId;
  return latest;
}

const normalizePath = (value: string) => value.replaceAll("\\", "/").replace(/^\.\//, "").replace(/\/+/g, "/");

export function parsePorcelainZ(raw: string): ChangedFile[] {
  const fields = raw.split("\0");
  const result: ChangedFile[] = [];
  for (let index = 0; index < fields.length; index += 1) {
    const entry = fields[index];
    if (!entry) continue;
    const status = entry.slice(0, 2);
    let filePath = entry.slice(3);
    if ((status.includes("R") || status.includes("C")) && fields[index + 1]) {
      index += 1;
    }
    result.push({ path: normalizePath(filePath), status, untracked: status === "??" });
  }
  return result;
}

export function parseAddedLines(diff: string) {
  const added: Array<{ path: string; line: number; text: string }> = [];
  let filePath = "";
  let newLine = 0;
  for (const line of diff.split("\n")) {
    if (line.startsWith("+++ b/")) { filePath = normalizePath(line.slice(6)); continue; }
    const hunk = line.match(/^@@ -\d+(?:,\d+)? \+(\d+)/);
    if (hunk) { newLine = Number(hunk[1]); continue; }
    if (!filePath || line.startsWith("+++")) continue;
    if (line.startsWith("+")) { added.push({ path: filePath, line: newLine, text: line.slice(1) }); newLine += 1; }
    else if (!line.startsWith("-")) newLine += 1;
  }
  return added;
}

function insidePrefix(filePath: string, candidate: string) {
  const prefix = normalizePath(candidate).replace(/^\/+|\/+$/g, "");
  return prefix === "" || filePath === prefix || filePath.startsWith(`${prefix}/`);
}

const SECRET_RULES: Array<[string, RegExp]> = [
  ["private-key", /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/],
  ["aws-access-key", /\bAKIA[0-9A-Z]{16}\b/],
  ["github-token", /\bgh[opusr]_[A-Za-z0-9_]{20,}\b/],
  ["generic-secret", /\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*["'][^"'\s]{12,}["']/i],
];

const DANGER_RULES: Array<[string, RegExp, string]> = [
  ["destructive-command", /\brm\s+-[^\n]*r[^\n]*f\b|\bgit\s+reset\s+--hard\b/, "新增了高风险破坏性命令"],
  ["download-execute", /\b(?:curl|wget)\b[^\n|]*\|\s*(?:ba)?sh\b/, "新增了下载后直接执行的命令"],
  ["world-writable", /\bchmod\s+(?:-R\s+)?777\b/, "新增了全局可写权限"],
  ["conflict-marker", /^(?:<{7}|={7}|>{7})(?:\s|$)/, "存在未解决的合并冲突标记"],
];

export function reviewChanges(input: {
  files: ChangedFile[];
  diff: string;
  untrackedText?: Record<string, string>;
  allowedPaths?: string[];
  forbiddenPaths?: string[];
  testEvidence?: TestEvidence[];
  truncated?: boolean;
  whitespaceErrors?: string;
}) {
  const findings: ReviewFinding[] = [];
  const allowed = (input.allowedPaths || []).map(normalizePath);
  const forbidden = [".git", ...(input.forbiddenPaths || [])].map(normalizePath);
  for (const file of input.files) {
    const filePath = normalizePath(file.path);
    if (forbidden.some((prefix) => insidePrefix(filePath, prefix))) findings.push({ severity: "blocking", code: "forbidden-path", path: filePath, message: "改动触及禁止路径" });
    if (allowed.length && !allowed.some((prefix) => insidePrefix(filePath, prefix))) findings.push({ severity: "blocking", code: "outside-allowed-path", path: filePath, message: "改动超出本任务允许路径" });
    if (file.binary) findings.push({ severity: "warning", code: "binary-change", path: filePath, message: "二进制改动无法进行逐行审阅" });
  }
  const additions = parseAddedLines(input.diff);
  for (const [filePath, content] of Object.entries(input.untrackedText || {})) {
    content.split("\n").forEach((text, index) => additions.push({ path: normalizePath(filePath), line: index + 1, text }));
  }
  for (const item of additions) {
    for (const [code, pattern] of SECRET_RULES) if (pattern.test(item.text)) findings.push({ severity: "blocking", code, path: item.path, line: item.line, message: "新增内容疑似包含凭据；review 不回显其值" });
    for (const [code, pattern, message] of DANGER_RULES) if (pattern.test(item.text)) findings.push({ severity: "blocking", code, path: item.path, line: item.line, message });
  }
  if (input.truncated) findings.push({ severity: "blocking", code: "review-truncated", message: "改动过大，review 输入被截断，无法证明完整性" });
  if (input.whitespaceErrors?.trim()) findings.push({ severity: "blocking", code: "diff-check", message: "git diff --check 报告空白或冲突标记问题" });
  const tests = input.testEvidence || [];
  for (const test of tests) if (!Number.isInteger(test.exit_code) || test.exit_code !== 0) findings.push({ severity: "blocking", code: "test-failed", message: `检查未通过：${test.command}` });
  if (!tests.length) findings.push({ severity: "warning", code: "test-evidence-missing", message: "未提供测试或静态检查证据" });
  const unique = findings.filter((item, index, all) => index === all.findIndex((other) => other.code === item.code && other.path === item.path && other.line === item.line && other.message === item.message));
  return {
    passed: !unique.some((item) => item.severity === "blocking"),
    blocking_findings: unique.filter((item) => item.severity === "blocking"),
    warnings: unique.filter((item) => item.severity === "warning"),
    changed_files: input.files,
    tests,
  };
}

export function reviewFingerprint(status: string, diff: string, untrackedHashes: Record<string, string> = {}) {
  const ordered = Object.fromEntries(Object.entries(untrackedHashes).sort(([a], [b]) => a.localeCompare(b)));
  return createHash("sha256").update(status).update("\0").update(diff).update("\0").update(JSON.stringify(ordered)).digest("hex");
}
