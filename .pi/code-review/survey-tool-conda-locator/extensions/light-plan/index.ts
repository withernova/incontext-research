import * as fs from "node:fs";
import * as path from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { isComplete, makePlan, renderPlan, type PlanState, type PlanStep } from "./core.js";

export default function lightPlan(pi: ExtensionAPI) {
  let cwd = process.cwd();
  let plan: PlanState | null = null;
  const planFile = () => path.join(cwd, ".pi", "plan.json");

  function load() {
    try {
      const raw = JSON.parse(fs.readFileSync(planFile(), "utf8"));
      plan = makePlan(raw.steps, raw.explanation || "", raw.updatedAt);
    } catch { plan = null; }
  }
  function save() {
    fs.mkdirSync(path.dirname(planFile()), { recursive: true });
    const tmp = `${planFile()}.tmp-${process.pid}`;
    fs.writeFileSync(tmp, JSON.stringify(plan, null, 2) + "\n", "utf8");
    fs.renameSync(tmp, planFile());
  }
  function clear() {
    plan = null;
    try { fs.unlinkSync(planFile()); } catch (error: any) { if (error?.code !== "ENOENT") throw error; }
  }

  const tool = {
    name: "update_plan",
    label: "Update Plan",
    description: "Create or update a small persistent execution plan. Use for multi-step coding tasks; skip it for trivial one-step work.",
    promptSnippet: "Keep a short execution plan with exactly zero or one in-progress step",
    promptGuidelines: [
      "For non-trivial tasks, create a 3-7 step plan after inspecting enough context to make it concrete.",
      "Update the plan when work advances or assumptions change. Never have more than one in_progress step.",
      "Do not mark a step completed until its work and proportionate verification are actually done.",
      "A plan tracks work; it does not grant permission for destructive or external actions.",
    ],
    parameters: Type.Object({
      explanation: Type.Optional(Type.String({ description: "Brief reason for this plan or revision" })),
      plan: Type.Array(Type.Object({
        step: Type.String(),
        status: Type.String({ description: "pending, in_progress, or completed" }),
      })),
    }),
    async execute(_id: string, params: { explanation?: string; plan: PlanStep[] }) {
      plan = makePlan(params.plan, params.explanation || "");
      save();
      return { content: [{ type: "text", text: renderPlan(plan) }], details: { plan, complete: isComplete(plan) } };
    },
  };
  pi.registerTool(tool as any);

  pi.registerCommand("plan", {
    description: "Show or clear the current lightweight coding plan",
    async handler(args: string, context: any) {
      const action = (args || "status").trim().toLowerCase();
      if (action === "clear") { clear(); context.ui.notify("Plan cleared.", "info"); return; }
      if (action !== "status" && action !== "") { context.ui.notify("Usage: /plan [status|clear]", "error"); return; }
      context.ui.notify(renderPlan(plan), "info");
    },
  });

  pi.on("session_start", async (_event: any, context: any) => {
    cwd = context.cwd;
    load();
    if (plan && !isComplete(plan)) context.ui?.setStatus("light-plan", `plan · ${plan.steps.filter(x => x.status === "completed").length}/${plan.steps.length}`);
  });
}
