export type PlanStatus = "pending" | "in_progress" | "completed";

export interface PlanStep { step: string; status: PlanStatus }
export interface PlanState {
  version: 1;
  explanation?: string;
  steps: PlanStep[];
  updatedAt: string;
}

export function validatePlan(steps: PlanStep[]) {
  if (!Array.isArray(steps) || steps.length === 0) throw new Error("plan 至少需要一个步骤");
  if (steps.length > 12) throw new Error("plan 最多 12 个步骤；请合并过细的步骤");
  let active = 0;
  for (const [index, item] of steps.entries()) {
    if (!item.step?.trim()) throw new Error(`第 ${index + 1} 步缺少内容`);
    if (!["pending", "in_progress", "completed"].includes(item.status)) throw new Error(`第 ${index + 1} 步状态无效`);
    if (item.status === "in_progress") active += 1;
  }
  if (active > 1) throw new Error("同一时间最多一个步骤可以是 in_progress");
  const firstIncomplete = steps.findIndex((item) => item.status !== "completed");
  if (firstIncomplete >= 0 && steps.slice(firstIncomplete + 1).some((item) => item.status === "completed")) {
    throw new Error("不能跳过未完成步骤；如依赖关系变化，请先重写 plan");
  }
  return steps.map((item) => ({ step: item.step.trim(), status: item.status }));
}

export function makePlan(steps: PlanStep[], explanation = "", now = new Date().toISOString()): PlanState {
  return { version: 1, explanation: explanation.trim() || undefined, steps: validatePlan(steps), updatedAt: now };
}

export function isComplete(plan: PlanState) {
  return plan.steps.length > 0 && plan.steps.every((item) => item.status === "completed");
}

export function renderPlan(plan: PlanState | null) {
  if (!plan) return "No active plan.";
  const icon = { pending: "○", in_progress: "◉", completed: "✓" } as const;
  const lines = plan.steps.map((item, index) => `${icon[item.status]} ${index + 1}. ${item.step}`);
  return [`Plan${isComplete(plan) ? " (complete)" : ""}`, plan.explanation || "", ...lines].filter(Boolean).join("\n");
}
