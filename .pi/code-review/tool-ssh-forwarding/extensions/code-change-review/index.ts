import * as fs from "node:fs";
import * as path from "node:path";
import { createHash } from "node:crypto";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { latestBranchReview, latestUserEntryId as branchUserEntryId, parsePorcelainZ, reviewChanges, reviewFingerprint, type TestEvidence } from "./core.js";

const runFile = promisify(execFile);
const MAX_DIFF_BYTES = 1_500_000;
const MAX_UNTRACKED_BYTES = 256_000;

type ReviewParams = {
  intent?: string;
  task_id?: string;
  base_revision?: string;
  repository_path?: string;
  ssh_host?: string;
  allowed_paths?: string[];
  forbidden_paths?: string[];
  test_evidence?: TestEvidence[];
  only_paths?: string[]; // Internal path filter for non-authorizing automatic diagnostics.
  commit_message?: string;
  commit_paths?: string[];
};

export default function codeChangeReview(pi: ExtensionAPI) {
  let cwd = process.cwd();
  let reviewedFingerprint = "";
  let reviewedPassed = false;
  let reviewedBase = "HEAD";
  let reviewedTarget: { repositoryPath: string; sshHost: string } | null = null;
  let reviewedTaskBoundary: { target: { repositoryPath: string; sshHost: string }; base: string; files: Set<string>; contentHashes: Record<string, string>; taskId: string } | null = null;
  let reviewedPaths: string[] = [];
  let restoredReviewId = "";
  let reviewEpoch = 0;
  let notifiedFailure = "";
  let explicitReviewInFlight = false;
  let taskBaseline: { target: { repositoryPath: string; sshHost: string }; base: string; files: Set<string>; contentHashes: Record<string, string>; id: string; taskId: string } | null = null;
  let latestUserEntryId = "";

  function adoptReview(params: ReviewParams, result: any, userEntryId = "") {
    reviewEpoch += 1;
    reviewedFingerprint = "";
    reviewedPassed = false;
    reviewedTarget = null;
    reviewedTaskBoundary = null;
    reviewedPaths = [];
    reviewedBase = "HEAD";
    if (!result) return;
    const target = resolveTarget({ repository_path: result.repository.path, ssh_host: result.repository.ssh_host });
    reviewedFingerprint = result.diff_fingerprint;
    reviewedPassed = result.passed === true && result.review_current === true;
    reviewedTarget = target;
    reviewedBase = result.base_revision;
    if (result.task_scoped === true && result.task_boundary && Array.isArray(result.task_boundary.files) && result.task_boundary.content_hashes && typeof result.task_boundary.content_hashes === "object") {
      reviewedTaskBoundary = { target, base: result.task_boundary.base, files: new Set(result.task_boundary.files), contentHashes: result.task_boundary.content_hashes, taskId: result.task_boundary.task_id };
      reviewedPaths = Array.isArray(result.changed_files) ? result.changed_files.map((file: any) => file.path).filter((item: any) => typeof item === "string") : [];
    }
    latestUserEntryId = userEntryId;
  }

  function restoreReview(context: any) {
    const branch = context.sessionManager.getBranch();
    const latest = latestBranchReview(branch);
    const userId = branchUserEntryId(branch) || "";
    const id = `${latest?.id || "no-branch-review"}:${userId}`;
    if (id === restoredReviewId) return;
    restoredReviewId = id;
    const sameTask = Boolean(latest && latest.userEntryId === userId);
    adoptReview(sameTask ? latest.params : {}, sameTask ? latest.result : null, sameTask ? userId : "");
  }

  function resolveTarget(params: ReviewParams = {}) {
    const repositoryPath = params.repository_path || cwd;
    const sshHost = params.ssh_host || "";
    if (!path.isAbsolute(repositoryPath) || /[\0\r\n]/.test(repositoryPath)) throw new Error("repository_path 必须是安全的绝对路径");
    if (sshHost && !/^[A-Za-z0-9._:@-]{1,255}$/.test(sshHost)) throw new Error("ssh_host 格式不安全");
    if (sshHost && !/^\/[A-Za-z0-9._/@+-]+$/.test(repositoryPath)) throw new Error("远端 repository_path 只能包含安全路径字符");
    return { repositoryPath: path.normalize(repositoryPath), sshHost };
  }

  async function git(target: { repositoryPath: string; sshHost: string }, args: string[], maxBuffer = MAX_DIFF_BYTES + 100_000) {
    const commandArgs = ["-C", target.repositoryPath, ...args];
    const executable = target.sshHost ? "ssh" : "git";
    const quote = (value: string) => "'" + value.replaceAll("'", "'\\''") + "'";
    const finalArgs = target.sshHost ? ["-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "--", target.sshHost, ["git", ...commandArgs].map(quote).join(" ")] : commandArgs;
    const result = await runFile(executable, finalArgs, { encoding: "utf8", maxBuffer });
    return result.stdout;
  }

  async function contentHashes(target: { repositoryPath: string; sshHost: string }, files: string[]) {
    if (files.length > 5000) throw new Error("任务基线文件过多，无法安全判定变更归属");
    const hashes: Record<string, string> = {};
    for (const file of files) {
      try { hashes[file] = (await git(target, ["hash-object", "--", file], 10_000)).trim(); }
      catch { hashes[file] = "missing"; }
    }
    return hashes;
  }

  async function snapshot(baseRevision = "HEAD", target = resolveTarget(), onlyPaths?: string[]) {
    if (!/^[A-Za-z0-9._/@{}^~:+-]{1,200}$/.test(baseRevision)) throw new Error("base_revision 不是安全的 Git revision");
    await git(target, ["rev-parse", "--is-inside-work-tree"]);
    const base = (await git(target, ["rev-parse", "--verify", `${baseRevision}^{commit}`])).trim();
    if (onlyPaths && onlyPaths.length === 0) {
      const identity = `${target.sshHost || "local"}:${target.repositoryPath}\0${base}`;
      return { base, status: "", files: [], diff: "", untrackedText: {}, untrackedHashes: {}, fileHashes: {}, truncated: false, whitespaceErrors: "", fingerprint: reviewFingerprint(identity, "", {}) };
    }
    const pathspec = onlyPaths ? ["--", ...onlyPaths] : [];
    const status = await git(target, ["status", "--porcelain=v1", "-z", "--untracked-files=all", ...pathspec]);
    const files = parsePorcelainZ(status);
    // Include committed changes when the caller supplies an earlier baseline.
    const changed = (await git(target, ["diff", "--name-only", "-z", base, "--", ...(onlyPaths || [])])).split("\0").filter(Boolean);
    for (const filePath of changed) if (!files.some((item) => item.path === filePath)) files.push({ path: filePath, status: " M", untracked: false });
    let rawDiff = await git(target, ["diff", "--no-ext-diff", "--no-textconv", "--binary", "--find-renames", "--unified=3", base, "--", ...(onlyPaths || [])]);
    const truncated = Buffer.byteLength(rawDiff) > MAX_DIFF_BYTES;
    const untrackedText: Record<string, string> = {};
    const untrackedHashes: Record<string, string> = {};
    for (const file of files.filter((item) => item.untracked)) {
      const absolute = path.resolve(target.repositoryPath, file.path);
      const relative = path.relative(target.repositoryPath, absolute);
      if (relative.startsWith("..") || path.isAbsolute(relative)) throw new Error(`untracked path 越界：${file.path}`);
      if (target.sshHost) {
        if (!/^[A-Za-z0-9._@+/-]+$/.test(file.path)) throw new Error(`远端未跟踪文件名无法安全审阅：${file.path}`);
        untrackedHashes[file.path] = (await git(target, ["hash-object", "--", file.path], 10_000)).trim();
        const untrackedDiff = await git(target, ["diff", "--no-index", "--unified=3", "--", "/dev/null", file.path]).catch((error: any) => String(error?.stdout || ""));
        if (Buffer.byteLength(untrackedDiff) > MAX_UNTRACKED_BYTES || untrackedDiff.includes("Binary files ")) file.binary = true;
        else rawDiff += `\n${untrackedDiff}`;
      } else {
        const stat = fs.lstatSync(absolute);
        if (!stat.isFile()) continue;
        const data = fs.readFileSync(absolute);
        untrackedHashes[file.path] = createHash("sha256").update(data).digest("hex");
        if (data.length > MAX_UNTRACKED_BYTES || data.includes(0)) file.binary = true;
        else untrackedText[file.path] = data.toString("utf8");
      }
    }
    const fullTruncated = truncated || Buffer.byteLength(rawDiff) > MAX_DIFF_BYTES;
    const diff = fullTruncated ? rawDiff.slice(0, MAX_DIFF_BYTES) : rawDiff;
    const whitespaceErrors = await git(target, ["diff", "--check", base, "--", ...(onlyPaths || [])]).catch((error: any) => String(error?.stdout || error?.stderr || error?.message || error));
    const identity = `${target.sshHost || "local"}:${target.repositoryPath}\0${base}`;
    // Index/worktree status changes alone do not change reviewed content.
    const fileHashes = await contentHashes(target, files.map((file) => file.path));
    return { base, status, files, diff, untrackedText, untrackedHashes, fileHashes, truncated: fullTruncated, whitespaceErrors, fingerprint: reviewFingerprint(identity, rawDiff, untrackedHashes) };
  }

  async function performReview(params: ReviewParams = {}, automatic = false) {
    if (!automatic) { reviewEpoch += 1; reviewedPassed = false; }
    const target = resolveTarget(params);
    let reviewBase = params.base_revision || "HEAD";
    let onlyPaths = automatic ? params.only_paths : undefined;
    let taskScoped = false;
    let preexistingConflicts: string[] = [];
    const boundary = taskBaseline;
    if (!automatic && boundary && target.repositoryPath === boundary.target.repositoryPath && target.sshHost === boundary.target.sshHost
        && (!params.base_revision || params.base_revision === "HEAD" || params.base_revision === boundary.base)) {
      if (params.task_id && params.task_id !== boundary.taskId) throw new Error("task_id 不属于当前用户任务");
      reviewBase = boundary.base;
      taskScoped = true;
      const allCurrent = await snapshot(boundary.base, target);
      onlyPaths = allCurrent.files.map((file) => file.path).filter((file) => !boundary.files.has(file));
      preexistingConflicts = allCurrent.files.map((file) => file.path).filter((file) => boundary.files.has(file) && boundary.contentHashes[file] !== allCurrent.fileHashes[file]);
    }
    const commitPaths = params.commit_paths || [];
    if (taskScoped && commitPaths.some((item) => !onlyPaths?.includes(item))) throw new Error("commit_paths 必须只包含当前任务开始后发生变化的文件；拒绝提交既有用户改动");
    if (params.commit_message !== undefined || params.commit_paths !== undefined) {
      if (!params.commit_message?.trim() || !commitPaths.length) throw new Error("提交需要非空 commit_message 和本任务的精确 commit_paths");
      for (const item of commitPaths) {
        if (!item || path.isAbsolute(item) || item.split("/").some((part) => [".", "..", ".git", ""].includes(part)) || /[\0\r\n*?\[\]:\\]/.test(item)) throw new Error("commit_paths 必须是精确仓库相对文件路径，不接受目录或通配符");
      }
      const changed = parsePorcelainZ(await git(target, ["status", "--porcelain=v1", "-z", "--untracked-files=all"]));
      if (commitPaths.some((item) => !changed.some((file) => file.path === item && !/[RC]/.test(file.status)))) throw new Error("commit_paths 只能包含当前有改动的文件；重命名请先独立核验并提交");
      const entries = await git(target, ["ls-files", "--stage", "--", ...commitPaths]);
      if (entries.split("\n").some((line) => line.startsWith("160000 "))) throw new Error("commit_paths 不接受子模块目录");
      // Explicit files only; unrelated staged changes remain outside the commit.
      await git(target, ["add", "--", ...commitPaths]);
    }
    const current = await snapshot(reviewBase, target, onlyPaths);
    const scopePaths = (items?: string[]) => items?.map((item) => {
      if (!path.isAbsolute(item)) return item;
      const relative = path.relative(target.repositoryPath, item);
      return relative === "" ? "" : relative;
    });
    const result = reviewChanges({
      files: current.files,
      diff: current.diff,
      untrackedText: current.untrackedText,
      allowedPaths: scopePaths(params.allowed_paths),
      forbiddenPaths: scopePaths(params.forbidden_paths),
      testEvidence: params.test_evidence,
      truncated: current.truncated,
      whitespaceErrors: current.whitespaceErrors,
    });
    if (preexistingConflicts.length) {
      result.passed = false;
      result.blocking_findings.push({ severity: "blocking", code: "preexisting-change-overlap", path: preexistingConflicts.slice(0,40).join(", "), message: "这些文件在任务开始前已有改动，无法从 Git diff 中分离本轮内容。请先由用户处理既有改动，再重新开始任务审阅。" });
    }
    let reviewCurrent = result.passed;
    let commit: { sha: string; paths: string[] } | undefined;
    if (!automatic && result.passed && params.commit_message) {
      if ((await snapshot(current.base, target, onlyPaths)).fingerprint !== current.fingerprint) throw new Error("审阅期间代码发生变化，请重新审阅后提交");
      await git(target, ["commit", "--only", "-m", params.commit_message, "--", ...commitPaths]);
      commit = { sha: (await git(target, ["rev-parse", "HEAD"])).trim(), paths: commitPaths };
      // Hooks may change content: keep the original fingerprint so the gate
      // detects those changes rather than silently approving a new snapshot.
      reviewCurrent = (await snapshot(current.base, target, onlyPaths)).fingerprint === current.fingerprint;
    }
    const receipt = { contract: "pi.code-change-review/v1", review_id: current.fingerprint.slice(0, 16), diff_fingerprint: current.fingerprint, base_revision: current.base, task_id: boundary?.taskId || params.task_id || "", task_scoped: taskScoped, task_boundary: taskScoped && boundary ? { task_id: boundary.taskId, base: boundary.base, files: [...boundary.files], content_hashes: boundary.contentHashes } : null, commit, review_current: reviewCurrent, repository: { ssh_host: target.sshHost || undefined, path: target.repositoryPath }, review_scope: { allowed_paths: params.allowed_paths, forbidden_paths: params.forbidden_paths }, intent: params.intent || "", ...result };
    // Automatic observations never replace a model-requested review or authorize Run start.
    if (!automatic) adoptReview(params, receipt);
    return receipt;
  }

  pi.registerTool({
    name: "code_change_review",
    label: "Code Change Review",
    executionMode: "sequential",
    description: "Review Git changes against a fixed baseline. Optionally stage exact task files and commit them after a passing review; never push. Content changes invalidate review; committing unchanged reviewed content does not.",
    promptSnippet: "After changing code, run code_change_review before reporting completion or starting a managed Run",
    promptGuidelines: [
      "Review at a coherent checkpoint before committing, reporting completion, or starting a Run; batch edits and focused checks before review.",
      "For authorized remote code work, checkpoint each tested change with commit_message and exact commit_paths. Inspect initial Git status, preserve existing user edits, and exclude data, outputs and secrets. Report commit SHA; do not wait for an experiment to finish to commit its implementation. Never auto-push.",
      "Pass the current task's allowed_paths and forbidden_paths when supplied, plus exact test evidence. The tool scopes current-task changes against its before_agent_start Git baseline and excludes unchanged pre-existing edits. A file already dirty at task start that changes again blocks for ownership review; do not widen paths to hide it.",
      "Fix blocking findings and review the new diff again. Never expose a suspected secret value in the response.",
      "For Run implementation, a passing review of the current diff is required before survey_run_execution continue/start.",
      "A code review verifies engineering changes; it never approves research design or grants execution authorization.",
    ],
    parameters: Type.Object({
      intent: Type.Optional(Type.String({ description: "Short statement of the requested code change" })),
      task_id: Type.Optional(Type.String({ description: "Optional current user-task identity; defaults to the active user message and Git baseline" })),
      base_revision: Type.Optional(Type.String({ description: "Git commit/ref to compare against; defaults to HEAD" })),
      repository_path: Type.Optional(Type.String({ description: "Absolute local or remote Git repository path; defaults to Pi cwd" })),
      ssh_host: Type.Optional(Type.String({ description: "Fixed SSH host for a remote repository; omit for local review" })),
      allowed_paths: Type.Optional(Type.Array(Type.String())),
      forbidden_paths: Type.Optional(Type.Array(Type.String())),
      test_evidence: Type.Optional(Type.Array(Type.Object({
        command: Type.String(), exit_code: Type.Number(), summary: Type.Optional(Type.String()),
      }))),
      commit_message: Type.Optional(Type.String({ description: "Commit the reviewed task files with this message; requires commit_paths. No push." })),
      commit_paths: Type.Optional(Type.Array(Type.String({ description: "Exact relative changed file owned by this task; no directories/globs or unrelated user changes" }))),
    }),
    async execute(_id: string, params: ReviewParams) {
      const result = await performReview(params);
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }], details: result };
    },
  } as any);

  pi.on("tool_call", async (event: any, context: any) => {
    const name = String(event.toolName || event.name || "");
    const input = event.input || event.params || {};
    if (name === "code_change_review") {
      explicitReviewInFlight = true;
      reviewEpoch += 1;
      reviewedPassed = false;
      return;
    }
    if (name !== "survey_run_execution" || !["continue", "start"].includes(String(input.action || ""))) return;
    try {
      restoreReview(context);
      if (explicitReviewInFlight) return { block: true, reason: "code_change_review 尚未完成。" };
      if (!reviewedTarget) return { block: true, reason: "尚未对实现仓库调用 code_change_review。" };
      const epoch = reviewEpoch;
      let current: any;
      if (reviewedTaskBoundary) {
        const boundary = reviewedTaskBoundary;
        const allCurrent = await snapshot(boundary.base, reviewedTarget);
        const currentPaths = allCurrent.files.map((file: any) => file.path).filter((file: string) => !boundary.files.has(file));
        const conflicts = allCurrent.files.filter((file: any) => boundary.files.has(file.path) && boundary.contentHashes[file.path] !== allCurrent.fileHashes[file.path]);
        if (conflicts.length || currentPaths.slice().sort().join("\0") !== reviewedPaths.slice().sort().join("\0")) return { block: true, reason: "当前任务改动集合已变化或与任务前改动重叠；请重新审阅。" };
        current = await snapshot(boundary.base, reviewedTarget, reviewedPaths);
      } else current = await snapshot(reviewedBase, reviewedTarget);
      restoreReview(context);
      if (epoch !== reviewEpoch) return { block: true, reason: "检查期间审阅状态变化，请重新核对当前 review。" };
      if (!reviewedPassed || current.fingerprint !== reviewedFingerprint) {
        return { block: true, reason: "当前代码改动尚未通过 code_change_review，或 review 后又发生了变化。请先审阅当前完整 diff；修复后重新审阅。" };
      }
    } catch (error: any) {
      return { block: true, reason: `无法验证当前代码 review：${String(error?.message || error).slice(0, 500)}` };
    }
  });

  pi.on("tool_result", async (event: any, context: any) => {
    if (event.toolName !== "code_change_review") return;
    explicitReviewInFlight = false;
    const recorded = latestBranchReview([
      { type: "message", message: { role: "assistant", content: [{ type: "toolCall", name: "code_change_review", id: event.toolCallId, arguments: event.input || {} }] } },
      { type: "message", id: event.toolCallId, message: { role: "toolResult", toolName: "code_change_review", toolCallId: event.toolCallId, details: event.details, content: event.content, isError: event.isError } },
    ]);
    const userEntryId = context ? branchUserEntryId(context.sessionManager.getBranch()) || "" : "";
    adoptReview(recorded?.params || {}, recorded?.result || null, userEntryId);
    restoredReviewId = "";
  });

  pi.on("session_start", async (_event: any, context: any) => {
    cwd = context.cwd;
    taskBaseline = null;
    latestUserEntryId = "";
    restoredReviewId = "";
    explicitReviewInFlight = false;
    restoreReview(context);
  });

  pi.on("session_tree", async (_event: any, context: any) => { taskBaseline = null; restoreReview(context); });

  pi.on("before_agent_start", async (_event: any, context: any) => {
    restoreReview(context);
    latestUserEntryId = branchUserEntryId(context.sessionManager.getBranch()) || "";
    taskBaseline = null;
    try {
      const target = resolveTarget();
      const baseline = await snapshot("HEAD", target);
      const taskId=`${latestUserEntryId}:${baseline.base}`;
      taskBaseline = { target, base: baseline.base, files: new Set(baseline.files.map((file) => file.path)), contentHashes: baseline.fileHashes, id: `${taskId}:${baseline.fingerprint}`, taskId };
    } catch { /* Non-Git working directory: explicit review can still target another repository. */ }
  });

  pi.on("agent_end", async (_event: any, context: any) => {
    try {
      restoreReview(context);
      if (explicitReviewInFlight || !taskBaseline) return;
      const baseline = taskBaseline;
      const epoch = reviewEpoch;
      // Automatic diagnostics are scoped to files newly changed in this agent run.
      // Never inherit the previous review's paths, baseline, or repository.
      const current = await snapshot(baseline.base, baseline.target);
      restoreReview(context);
      if (epoch !== reviewEpoch || baseline !== taskBaseline) return;
      const newPaths = current.files.map((file) => file.path).filter((file) => !baseline.files.has(file));
      const overlappingPaths = current.files.map((file) => file.path).filter((file) => baseline.files.has(file) && baseline.contentHashes[file] !== current.fileHashes[file]);
      if (!newPaths.length && !overlappingPaths.length) return;
      let result: any;
      if (newPaths.length) {
        if (reviewedTarget?.repositoryPath === baseline.target.repositoryPath && reviewedTarget.sshHost === baseline.target.sshHost && reviewedBase === baseline.base && reviewedPassed && reviewedFingerprint === current.fingerprint) return;
        result = await performReview({ repository_path: baseline.target.repositoryPath, ssh_host: baseline.target.sshHost, base_revision: baseline.base, only_paths: newPaths }, true);
        // Diagnostic review only: current task boundaries decide authorization.
      } else {
        result = { passed: false, diff_fingerprint: current.fingerprint, blocking_findings: [{ severity: "blocking", code: "preexisting-change-overlap", path: overlappingPaths.slice(0, 40).join(", "), message: "这些文件在当前任务开始前已有 Git 改动；自动审阅无法判定本轮归属。请按当前任务边界显式调用 code_change_review。" }] };
      }
      restoreReview(context);
      if (epoch !== reviewEpoch || baseline !== taskBaseline) return;
      if (overlappingPaths.length) {
        result.passed = false;
        result.blocking_findings = [...(result.blocking_findings || []), { severity: "blocking", code: "preexisting-change-overlap", path: overlappingPaths.slice(0, 40).join(", "), message: "这些文件在当前任务开始前已有 Git 改动；自动审阅无法判定本轮归属。请按当前任务边界显式调用 code_change_review。" }];
      }
      if (!result.passed) {
        const findingKey=(result.blocking_findings||[]).map((item:any)=>`${item.code}:${item.path||""}`).sort().join("|");
        const noticeKey=`${current.fingerprint}:${findingKey}`;
        if (noticeKey===notifiedFailure) return;
        notifiedFailure = noticeKey;
        pi.sendUserMessage(`自动 Code Change Review 发现阻塞项。请按当前任务范围检查，并再次调用 code_change_review：\n${JSON.stringify(result.blocking_findings, null, 2)}`, { deliverAs: "followUp" });
      }
    } catch { /* 非 Git 工作区或不可读 diff：通用扩展不干扰纯文本任务。 */ }
  });
}
