import { spawn } from "node:child_process";
import { randomBytes } from "node:crypto";
import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import { StringEnum } from "@earendil-works/pi-ai";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import {
  budgetDecision,
  corruptStatePath,
  parseCommandArgs,
  remainingLeaseMs,
  retryAllowed,
  safeExplorationId,
  validateBudget,
  type ExplorerStatus,
  type TargetType,
} from "./core.js";

const TARGET_TYPES = ["experiment", "idea", "question", "comparison"] as const;
const CONTROL_ACTIONS = ["start", "pause", "resume", "stop", "status"] as const;
const ROUND_ACTIONS = ["complete", "fail"] as const;
const VERIFY_STATUSES = ["verified", "partial", "unverified_lead", "degraded"] as const;
const FAILURE_CLASSES = [
  "transient",
  "environment",
  "invalid_target",
  "evidence_unavailable",
  "authorization",
  "external_dependency",
] as const;
const RETRY_BASES = ["changed_environment", "new_evidence"] as const;
const OUTPUT_LIMIT = 1024 * 1024;

interface ExplorerState {
  schema: "survey-tool.research-explorer-state/v1";
  version: 1;
  explorationId: string;
  projectRoot: string;
  targetType: TargetType;
  targetId: string;
  status: ExplorerStatus;
  created: string;
  deadline: string;
  maxRounds: number | null;
  hardMaxRounds: number;
  completedRounds: number;
  currentRound: number;
  intervalMinutes: number;
  roundWallBudgetMinutes: number;
  lastEvidenceCount: number;
  lastEvidenceSummary: string;
  nextRound: string;
  lastReason: string;
  sessionDir: string;
  roundStartedAt?: string;
  roundDeadline?: string;
  retryAttempts?: number;
  pausedAfterRestart?: boolean;
}

interface CommandResult {
  [key: string]: any;
}

function atomicJson(filePath: string, value: unknown) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  const temporary = `${filePath}.${process.pid}.${randomBytes(5).toString("hex")}.tmp`;
  fs.writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, { mode: 0o600 });
  fs.renameSync(temporary, filePath);
}

function appendEvent(filePath: string, type: string, details: Record<string, unknown> = {}) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.appendFileSync(filePath, `${JSON.stringify({ time: new Date().toISOString(), type, details })}\n`);
}

function runProcess(command: string, args: string[]): Promise<CommandResult> {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { stdio: ["ignore", "pipe", "pipe"] });
    let stdout = "";
    let stderr = "";
    let overflow = false;
    const collect = (kind: "stdout" | "stderr", chunk: Buffer) => {
      if (overflow) return;
      if (kind === "stdout") stdout += chunk.toString();
      else stderr += chunk.toString();
      if (Buffer.byteLength(stdout) + Buffer.byteLength(stderr) > OUTPUT_LIMIT) {
        overflow = true;
        child.kill();
      }
    };
    child.stdout.on("data", (chunk) => collect("stdout", chunk));
    child.stderr.on("data", (chunk) => collect("stderr", chunk));
    child.on("error", reject);
    child.on("close", (code) => {
      if (overflow) return reject(new Error("surveyctl 输出超过 1MB 限制"));
      if (code !== 0) return reject(new Error((stderr || `surveyctl exit ${code}`).slice(-8192)));
      try {
        resolve(JSON.parse(stdout));
      } catch (error: any) {
        reject(new Error(`surveyctl 返回非 JSON：${error.message}`));
      }
    });
  });
}

export default function researchExplorer(pi: ExtensionAPI) {
  let cwd = process.cwd();
  let state: ExplorerState | null = null;
  let timer: ReturnType<typeof setTimeout> | null = null;

  const stateFile = () => path.join(cwd, ".pi", "research-explorer-state.json");
  const eventsFile = () => path.join(cwd, ".pi", "research-explorer-events.jsonl");
  const surveyctl = () => path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "surveyctl.py");
  const python = () => process.env.PYTHON || "python3";

  function saveLocal(eventType?: string, details?: Record<string, unknown>) {
    if (state) atomicJson(stateFile(), state);
    if (eventType) appendEvent(eventsFile(), eventType, details);
  }

  function clearTimer() {
    if (timer) clearTimeout(timer);
    timer = null;
  }

  function publicState() {
    if (!state) return {};
    return {
      ...state,
      lastEvidence: {
        count: state.lastEvidenceCount,
        summary: state.lastEvidenceSummary,
      },
      lastEvidenceCount: undefined,
      lastEvidenceSummary: undefined,
    };
  }

  async function survey(args: string[]) {
    if (!state) throw new Error("没有 exploration");
    return runProcess(python(), [surveyctl(), "--project", state.projectRoot, "exploration", ...args]);
  }

  async function transition(next: ExplorerStatus, reason: string, expected: ExplorerStatus) {
    if (!state) throw new Error("没有 exploration");
    const result = await survey([
      "transition",
      state.explorationId,
      "--status",
      next,
      "--reason",
      reason,
      "--expected-status",
      expected,
    ]);
    state.status = result.session.status;
    state.lastReason = reason;
    saveLocal("transition", { from: expected, to: next, reason });
    return result;
  }

  function isBudgetExhausted() {
    return !!state && budgetDecision({
      deadline: state.deadline,
      maxRounds: state.maxRounds,
      hardMaxRounds: state.hardMaxRounds,
      completedRounds: state.completedRounds,
    }).stop;
  }

  function roundMessage() {
    return `[RESEARCH EXPLORER ROUND ${state!.currentRound}]
先加载 research-explorer skill。
运行 python3 ${surveyctl()} --project "${state!.projectRoot}" exploration context ${state!.explorationId}，
获取最新目标、预算和前轮摘要。复用已记录证据，做一轮有界探索并主动寻找反证/混杂。
每次外部检索写 shell/02_search/search_log.md；失败/no hits 标 degraded。
最后必须调用 research_explorer_round complete（含 summary、evidence、contradictions、uncertainties、next_focus）或 fail。
不得执行 Run/SSH/长实验、改实验代码、Claim verdict 或正式 synthesis。`;
  }

  async function roundTimeout() {
    if (!state || state.status !== "round_running") return;
    try {
      await transition("needs_attention", "round wall budget exceeded", "round_running");
      clearTimer();
      pi.sendUserMessage("Research Explorer 当前轮次超过 wall budget，已停止并需要人工处理；不会并发开启下一轮。", { deliverAs: "followUp" });
    } catch (error: any) {
      state.status = "needs_attention";
      state.lastReason = `round timeout transition failed: ${error.message}`;
      saveLocal("transition_failed", { operation: "round_timeout" });
    }
  }

  function restoreRoundTimer() {
    if (!state || state.status !== "round_running") return;
    const remaining = remainingLeaseMs(state.roundDeadline);
    if (remaining <= 0) void roundTimeout();
    else {
      clearTimer();
      timer = setTimeout(() => void roundTimeout(), remaining);
    }
  }

  async function beginRound() {
    if (!state || state.status !== "active") return;
    if (isBudgetExhausted()) {
      await transition("expired", "预算到期", "active");
      clearTimer();
      pi.sendUserMessage("Research Explorer 预算已到期，请调用 /explore finalize 进入最终综合。", { deliverAs: "followUp" });
      return;
    }
    await transition("round_running", `round ${state.currentRound} started`, "active");
    state.roundStartedAt = new Date().toISOString();
    state.roundDeadline = new Date(Date.now() + state.roundWallBudgetMinutes * 60_000).toISOString();
    saveLocal("round_started", { round: state.currentRound, deadline: state.roundDeadline });
    pi.sendUserMessage(roundMessage(), { deliverAs: "followUp" });
    restoreRoundTimer();
  }

  function scheduleNext(delayMs?: number) {
    clearTimer();
    if (!state || state.status !== "active") return;
    const delay = delayMs ?? state.intervalMinutes * 60_000;
    state.nextRound = new Date(Date.now() + delay).toISOString();
    saveLocal();
    timer = setTimeout(() => void beginRound().catch(async (error: any) => {
      if (!state) return;
      try {
        await transition("needs_attention", `scheduler failed: ${error.message}`, state.status);
      } catch {
        state.status = "needs_attention";
        state.lastReason = "scheduler/canonical transition failed";
        saveLocal("transition_failed", { operation: "begin_round" });
      }
      pi.sendUserMessage(`Research Explorer 调度失败，需要人工处理：${String(error.message).slice(0, 1000)}`, { deliverAs: "followUp" });
    }), delay);
  }

  async function inspectTarget() {
    if (!state) throw new Error("没有 exploration");
    return survey([
      "inspect-target",
      "--target-type",
      state.targetType,
      "--target-id",
      state.targetId,
    ]);
  }

  const controlTool = {
    name: "research_explorer_control",
    label: "Research Explorer Control",
    description: "Start, pause, resume, stop, or inspect one bounded Research Explorer session.",
    parameters: Type.Object({
      action: StringEnum(CONTROL_ACTIONS),
      project_root: Type.Optional(Type.String()),
      target_type: Type.Optional(StringEnum(TARGET_TYPES)),
      target_id: Type.Optional(Type.String()),
      duration_minutes: Type.Optional(Type.Integer()),
      max_rounds: Type.Optional(Type.Integer()),
      interval_minutes: Type.Optional(Type.Integer()),
      round_wall_budget_minutes: Type.Optional(Type.Integer()),
    }),
    async execute(_id: string, params: any) {
      if (params.action === "status") {
        return { content: [{ type: "text", text: JSON.stringify(publicState(), null, 2) }], details: publicState() };
      }
      if (params.action === "start") {
        if (state && ["active", "round_running", "paused", "needs_attention", "finalizing"].includes(state.status)) {
          throw new Error("已有未停止 exploration");
        }
        const supplied = String(params.project_root || "");
        if (!path.isAbsolute(supplied) || !fs.existsSync(supplied) || fs.realpathSync(supplied) !== path.resolve(supplied) || !params.target_id) {
          throw new Error("project_root 必须是存在的 canonical 绝对路径且 target_id 必填");
        }
        const root = path.resolve(supplied);
        const targetType = params.target_type as TargetType;
        await runProcess(python(), [surveyctl(), "--project", root, "exploration", "inspect-target", "--target-type", targetType, "--target-id", params.target_id]);
        const budget = validateBudget({
          durationMinutes: params.duration_minutes,
          maxRounds: params.max_rounds,
          intervalMinutes: params.interval_minutes,
          roundWallBudgetMinutes: params.round_wall_budget_minutes,
        });
        let initialized: any;
        for (let attempt = 0; attempt < 3; attempt += 1) {
          const explorationId = safeExplorationId(targetType, params.target_id, Date.now() + attempt);
          try {
            initialized = await runProcess(python(), [
              surveyctl(), "--project", root, "exploration", "init",
              "--target-type", targetType, "--target-id", params.target_id,
              "--exploration-id", explorationId,
              "--budget-json", JSON.stringify({
                duration_minutes: params.duration_minutes,
                max_rounds: params.max_rounds,
                hard_max_rounds: budget.hardMaxRounds,
                interval_minutes: budget.intervalMinutes,
                round_wall_budget_minutes: budget.roundWallBudgetMinutes,
                deadline: budget.deadline,
              }),
            ]);
            break;
          } catch (error) {
            if (attempt === 2) throw error;
          }
        }
        state = {
          schema: "survey-tool.research-explorer-state/v1",
          version: 1,
          explorationId: initialized.id,
          projectRoot: root,
          targetType,
          targetId: params.target_id,
          status: initialized.status,
          created: initialized.created,
          deadline: initialized.deadline,
          maxRounds: initialized.max_rounds,
          hardMaxRounds: initialized.hard_max_rounds,
          completedRounds: initialized.completed_rounds,
          currentRound: initialized.current_round,
          intervalMinutes: initialized.interval_minutes,
          roundWallBudgetMinutes: initialized.round_wall_budget_minutes,
          lastEvidenceCount: 0,
          lastEvidenceSummary: "",
          nextRound: "",
          lastReason: "started",
          sessionDir: path.join(root, "shell", "07_explorations", initialized.id),
        };
        saveLocal("started");
        scheduleNext(0);
      } else if (params.action === "pause") {
        if (!state || !["active", "round_running"].includes(state.status)) throw new Error("当前不可暂停");
        const previous = state.status;
        await transition("paused", "human pause", previous);
        clearTimer();
      } else if (params.action === "resume") {
        if (!state || !["paused", "needs_attention"].includes(state.status)) throw new Error("当前不可恢复");
        await inspectTarget();
        const previous = state.status;
        if (isBudgetExhausted()) {
          await transition("expired", "deadline reached on resume", previous);
          clearTimer();
          pi.sendUserMessage("Research Explorer deadline 已到，不再继续轮次；请调用 /explore finalize。", { deliverAs: "followUp" });
        } else {
          await transition("active", "human resume", previous);
          state.pausedAfterRestart = false;
          saveLocal("resumed");
          scheduleNext(0);
        }
      } else if (params.action === "stop") {
        if (!state) throw new Error("没有 exploration");
        const previous = state.status;
        await transition("stopped", "human stop", previous);
        clearTimer();
      }
      return { content: [{ type: "text", text: JSON.stringify(publicState(), null, 2) }], details: publicState() };
    },
  };
  pi.registerTool(controlTool);

  pi.registerTool({
    name: "research_explorer_round",
    label: "Research Explorer Round",
    description: "Complete or fail exactly the current leased exploration round.",
    parameters: Type.Object({
      action: StringEnum(ROUND_ACTIONS),
      summary: Type.Optional(Type.String()),
      evidence: Type.Optional(Type.Array(Type.Object({
        source: Type.String(),
        ref: Type.String(),
        finding: Type.String(),
        verification_status: StringEnum(VERIFY_STATUSES),
      }))),
      contradictions: Type.Optional(Type.Array(Type.String())),
      uncertainties: Type.Optional(Type.Array(Type.String())),
      next_focus: Type.Optional(Type.String()),
      failure_class: Type.Optional(StringEnum(FAILURE_CLASSES)),
      reason: Type.Optional(Type.String()),
      retry_basis: Type.Optional(Type.Array(StringEnum(RETRY_BASES))),
    }),
    async execute(_id: string, params: any) {
      if (!state || state.status !== "round_running") throw new Error("没有正在运行的 round");
      if (params.action === "fail") {
        if (!FAILURE_CLASSES.includes(params.failure_class) || !String(params.reason || "").trim()) {
          throw new Error("fail 必须提供合法 failure_class 和非空 reason");
        }
        const retry = retryAllowed(params.failure_class, params.retry_basis || [], state.retryAttempts || 0);
        const next = retry ? "active" : params.failure_class === "authorization" ? "paused" : "needs_attention";
        await transition(next, String(params.reason), "round_running");
        clearTimer();
        if (retry) {
          state.retryAttempts = (state.retryAttempts || 0) + 1;
          scheduleNext(0);
        }
        return { content: [{ type: "text", text: state.status }], details: publicState() };
      }

      const temporary = path.join(state.projectRoot, ".pi", `.research-explorer-round-${process.pid}-${randomBytes(6).toString("hex")}.json`);
      fs.mkdirSync(path.dirname(temporary), { recursive: true });
      fs.writeFileSync(temporary, JSON.stringify(params), { mode: 0o600 });
      let recorded: any;
      try {
        recorded = await survey(["record-round", state.explorationId, "--round", String(state.currentRound), "--payload-file", temporary]);
      } catch (error: any) {
        saveLocal("record_failed", { round: state.currentRound, error: String(error.message).slice(0, 1000) });
        restoreRoundTimer();
        throw error;
      } finally {
        try { fs.unlinkSync(temporary); } catch { /* already removed */ }
      }
      const canonical = recorded.session;
      if (canonical.status !== "round_running" || canonical.completed_rounds !== state.currentRound || canonical.current_round !== state.currentRound + 1) {
        await transition("needs_attention", "record-round canonical/local mismatch", "round_running");
        clearTimer();
        throw new Error("record-round 返回的 canonical round 与本地 lease 不一致");
      }
      state.completedRounds = canonical.completed_rounds;
      state.currentRound = canonical.current_round;
      state.lastEvidenceCount = params.evidence.length;
      state.lastEvidenceSummary = String(params.summary).slice(0, 1000);
      state.retryAttempts = 0;
      const exhausted = isBudgetExhausted();
      await transition(exhausted ? "finalizing" : "active", exhausted ? "budget complete" : "round complete", "round_running");
      clearTimer();
      if (exhausted) {
        pi.sendUserMessage("Research Explorer 预算已完成。请做最终综合并调用 research_explorer_finalize。", { deliverAs: "followUp" });
      } else {
        scheduleNext();
      }
      return { content: [{ type: "text", text: `round ${state.completedRounds} recorded` }], details: publicState() };
    },
  });

  pi.registerTool({
    name: "research_explorer_finalize",
    label: "Research Explorer Finalize",
    description: "Persist a final draft report and target-specific review proposal.",
    parameters: Type.Object({
      final_report: Type.String(),
      proposal: Type.Record(Type.String(), Type.Unknown()),
    }),
    async execute(_id: string, params: any) {
      if (!state) throw new Error("没有 exploration");
      if (["expired", "stopped", "paused", "needs_attention"].includes(state.status)) {
        await transition("finalizing", "finalize requested", state.status);
      }
      if (state.status !== "finalizing") throw new Error("当前不可 finalize");
      const directory = path.join(state.projectRoot, ".pi");
      const suffix = `${process.pid}-${randomBytes(6).toString("hex")}`;
      const reportFile = path.join(directory, `.research-explorer-final-${suffix}.md`);
      const proposalFile = path.join(directory, `.research-explorer-proposal-${suffix}.json`);
      fs.mkdirSync(directory, { recursive: true });
      fs.writeFileSync(reportFile, params.final_report, { mode: 0o600 });
      fs.writeFileSync(proposalFile, JSON.stringify(params.proposal), { mode: 0o600 });
      let result: any;
      try {
        result = await survey(["finalize", state.explorationId, "--final-report-file", reportFile, "--proposal-file", proposalFile]);
      } finally {
        for (const filePath of [reportFile, proposalFile]) {
          try { fs.unlinkSync(filePath); } catch { /* already removed */ }
        }
      }
      state.status = result.session.status;
      state.lastReason = "finalized";
      clearTimer();
      saveLocal("finalized", { applied: result.applied?.length || 0, skipped: result.skipped?.length || 0 });
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }], details: result };
    },
  });

  pi.registerCommand("explore", {
    description: "Research Explorer: start|pause|resume|stop|status|finalize",
    async handler(args: string, context: any) {
      let params: Record<string, string | number>;
      try {
        params = parseCommandArgs(args);
      } catch (error: any) {
        context.ui.notify(error.message, "error");
        return;
      }
      if (params.action === "finalize") {
        if (!state) return context.ui.notify("没有 exploration。", "error");
        try {
          if (["expired", "stopped", "paused", "needs_attention"].includes(state.status)) {
            await transition("finalizing", "finalize command requested", state.status);
          }
          if (state.status !== "finalizing") throw new Error("当前状态不能 finalize");
          pi.sendUserMessage(
            "请加载 research-explorer skill，读取最新 exploration context，完成最终综合，" +
            "并调用 research_explorer_finalize 提交 final_report 与 target-specific proposal。",
            { deliverAs: "followUp" },
          );
          context.ui.notify("已进入 finalizing 并排入最终综合；尚未写入完成结果。", "info");
        } catch (error: any) {
          context.ui.notify(error.message, "error");
        }
        return;
      }
      try {
        const result = await (controlTool.execute as any)("command", params);
        context.ui.notify(result.content[0].text, "info");
      } catch (error: any) {
        context.ui.notify(error.message, "error");
      }
    },
  });

  pi.on("session_start", async (_event: any, context: any) => {
    cwd = context.cwd;
    if (!fs.existsSync(stateFile())) return;
    let loaded: ExplorerState;
    try {
      loaded = JSON.parse(fs.readFileSync(stateFile(), "utf8"));
    } catch {
      const corrupt = corruptStatePath(stateFile());
      fs.renameSync(stateFile(), corrupt);
      context.ui?.setStatus("research-explorer", "needs_attention · state 损坏");
      context.ui?.notify("Research Explorer state 损坏，已隔离为 .corrupt-*；未泄露其内容。", "error");
      appendEvent(eventsFile(), "state_corrupt_quarantined", { file: path.basename(corrupt) });
      return;
    }
    state = loaded;
    if ((loaded.status === "active" || loaded.status === "round_running") && !loaded.pausedAfterRestart) {
      try {
        await transition("paused", "pi restart requires explicit resume", loaded.status);
        state.pausedAfterRestart = true;
        saveLocal("paused_after_restart");
      } catch (error: any) {
        state.status = "needs_attention";
        state.lastReason = "restart pause canonical sync failed";
        saveLocal("restart_pause_failed");
        context.ui?.notify(`Research Explorer 重启暂停同步失败：${error.message}`, "error");
      }
    }
    context.ui?.setStatus("research-explorer", `${state.status} · ${state.explorationId}`);
  });

  pi.on("session_shutdown", clearTimer);
}
