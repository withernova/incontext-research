import { createHash } from "node:crypto";

export type TargetType = "experiment" | "idea" | "question" | "comparison";
export type ExplorerStatus =
  | "active"
  | "round_running"
  | "paused"
  | "finalizing"
  | "completed"
  | "completed_with_warnings"
  | "stopped"
  | "needs_attention"
  | "expired";

export interface BudgetInput {
  durationMinutes?: number;
  maxRounds?: number;
  intervalMinutes?: number;
  roundWallBudgetMinutes?: number;
  now?: number;
}

export function validateBudget(input: BudgetInput) {
  const now = input.now ?? Date.now();
  if (input.durationMinutes == null && input.maxRounds == null) {
    throw new Error("duration/maxRounds 至少一个必填");
  }
  const values: Array<[string, number | undefined, number, number]> = [
    ["duration", input.durationMinutes, 1, 10080],
    ["maxRounds", input.maxRounds, 1, 1000],
    ["interval", input.intervalMinutes ?? 1, 1, 60],
    ["roundWallBudget", input.roundWallBudgetMinutes ?? 10, 1, 60],
  ];
  for (const [name, value, low, high] of values) {
    if (value != null && (!Number.isInteger(value) || value < low || value > high)) {
      throw new Error(`${name} 越界`);
    }
  }
  return {
    deadline: input.durationMinutes
      ? new Date(now + input.durationMinutes * 60_000).toISOString()
      : "",
    maxRounds: input.maxRounds ?? null,
    hardMaxRounds: input.maxRounds ?? 20,
    intervalMinutes: input.intervalMinutes ?? 1,
    roundWallBudgetMinutes: input.roundWallBudgetMinutes ?? 10,
  };
}

export function budgetDecision(
  state: { deadline?: string; maxRounds?: number | null; hardMaxRounds: number; completedRounds: number },
  now = Date.now(),
) {
  const deadlineReached = !!state.deadline && Date.parse(state.deadline) <= now;
  const roundReached =
    state.completedRounds >= (state.maxRounds ?? state.hardMaxRounds) ||
    state.completedRounds >= state.hardMaxRounds;
  return {
    stop: deadlineReached || roundReached,
    reason: deadlineReached ? "deadline_reached" : roundReached ? "round_budget_reached" : "continue",
  };
}

export function restartState<T extends { status: ExplorerStatus }>(state: T): T & { pausedAfterRestart?: boolean } {
  if (state.status === "active" || state.status === "round_running") {
    return { ...state, status: "paused", pausedAfterRestart: true };
  }
  return state;
}

export function retryAllowed(failureClass: string, retryBasis: string[], attempts: number) {
  return (
    attempts < 1 &&
    ["transient", "environment"].includes(failureClass) &&
    retryBasis.some((item) => item === "changed_environment" || item === "new_evidence")
  );
}

export function remainingLeaseMs(roundDeadline: string | undefined, now = Date.now()) {
  if (!roundDeadline) return 0;
  return Math.max(0, Date.parse(roundDeadline) - now);
}

export function safeExplorationId(type: TargetType, targetId: string, now = Date.now()) {
  const stamp = new Date(now).toISOString().replace(/[-:TZ.]/g, "").slice(0, 14);
  const safe = targetId.toLowerCase().replace(/[^a-z0-9._-]+/g, "-").slice(0, 48);
  const hash = createHash("sha256").update(`${type}|${targetId}|${now}`).digest("hex").slice(0, 8);
  return `${type}-${safe}-${stamp}-${hash}`;
}

export function corruptStatePath(filePath: string, now = Date.now()) {
  const timestamp = new Date(now).toISOString().replace(/[:.]/g, "-");
  return `${filePath}.corrupt-${timestamp}`;
}

function tokenize(command: string) {
  const tokens: string[] = [];
  let current = "";
  let quote = "";
  let escaped = false;
  for (const char of command.trim()) {
    if (escaped) {
      current += char;
      escaped = false;
    } else if (char === "\\" && quote !== "'") {
      escaped = true;
    } else if (quote) {
      if (char === quote) quote = "";
      else current += char;
    } else if (char === "'" || char === '"') {
      quote = char;
    } else if (/\s/.test(char)) {
      if (current) tokens.push(current);
      current = "";
    } else {
      current += char;
    }
  }
  if (escaped || quote) throw new Error("命令包含未闭合引号或转义");
  if (current) tokens.push(current);
  return tokens;
}

export function parseCommandArgs(command: string): Record<string, string | number> {
  const tokens = tokenize(command);
  const action = tokens.shift() || "status";
  if (!["start", "pause", "resume", "stop", "status", "finalize"].includes(action)) {
    throw new Error(`未知 action：${action}`);
  }
  const result: Record<string, string | number> = { action };
  const allowed: Record<string, [string, boolean]> = {
    "--project-root": ["project_root", false],
    "--target-type": ["target_type", false],
    "--target-id": ["target_id", false],
    "--duration-minutes": ["duration_minutes", true],
    "--max-rounds": ["max_rounds", true],
    "--interval-minutes": ["interval_minutes", true],
    "--round-wall-budget-minutes": ["round_wall_budget_minutes", true],
  };
  while (tokens.length) {
    const flag = tokens.shift()!;
    const spec = allowed[flag];
    if (!spec) throw new Error(`未知参数：${flag}`);
    const value = tokens.shift();
    if (value == null || value.startsWith("--")) throw new Error(`${flag} 缺少值`);
    if (spec[1]) {
      const numeric = Number(value);
      if (!Number.isInteger(numeric)) throw new Error(`${flag} 必须是整数`);
      result[spec[0]] = numeric;
    } else {
      result[spec[0]] = value;
    }
  }
  return result;
}
