import type { V2ObjectIndex } from "./api";
import type { ExperimentDashboard, Project, WorkspaceData } from "./types";

export type AttentionItem = {
  tone: "danger" | "warning" | "info";
  eyebrow: string;
  title: string;
  detail: string;
  action: string;
  navId: "inbox" | "intake" | "experiments" | "automation" | "papers" | "questions";
  targetId: string;
};

export type RecentActivityItem = {
  id: string;
  category: "research" | "experiment" | "system";
  kind: string;
  title: string;
  detail: string;
  occurredAt: string;
  navId: "papers" | "analysis" | "ideas" | "questions" | "experiments" | "automation" | "inbox";
};

function openGovernanceTasks(dashboard: ExperimentDashboard): number {
  const source = dashboard.governance_tasks;
  const tasks = Array.isArray(source) ? source : source?.tasks || [];
  return tasks.filter((task) => !task.status || !["completed", "cancelled"].includes(task.status)).length;
}

export function buildAttentionItems(data: WorkspaceData): AttentionItem[] {
  const items: AttentionItem[] = [];
  for (const blocker of data.project.blockers || []) {
    items.push({
      tone: "danger",
      eyebrow: "项目阻塞",
      title: blocker.replace(/^[-\s]+/, ""),
      detail: `研究状态 · ${data.project.state || "未登记"}`,
      action: "查看项目",
      navId: "intake",
      targetId: "intake",
    });
  }

  const reviewRuns = data.dashboard.runs.filter((run) =>
    ["pending_review", "changes_requested"].includes(run.review_status || ""),
  );
  if (reviewRuns.length) {
    items.push({
      tone: "warning",
      eyebrow: "Run 审核",
      title: `${reviewRuns.length} 个 Run 等待确认`,
      detail: "批准规范与执行授权保持为两道独立门禁",
      action: "进入实验",
      navId: "experiments",
      targetId: "experiments-section",
    });
  }

  const outboxItems = data.dashboard.execution_outbox?.items || [];
  const executionAttention = outboxItems.filter((item) =>
    ["blocked", "failed", "running"].includes(item.status || ""),
  );
  if (executionAttention.length) {
    items.push({
      tone: "info",
      eyebrow: "执行管线",
      title: `${executionAttention.length} 个派发需要关注`,
      detail: "包括运行中、阻塞或失败的持久任务",
      action: "查看管线",
      navId: "experiments",
      targetId: "experiments-section",
    });
  }

  const governanceCount = openGovernanceTasks(data.dashboard);
  if (governanceCount) {
    items.push({
      tone: "info",
      eyebrow: "轻量整理",
      title: `${governanceCount} 个对象等待分类`,
      detail: "不会改变审核、授权或科研结论",
      action: "处理待办",
      navId: "automation",
      targetId: "objects-section",
    });
  }

  if (!items.length) {
    items.push({
      tone: "info",
      eyebrow: "当前平稳",
      title: "没有需要立即处理的门禁",
      detail: "可以继续论文阅读、问题分析或实验设计",
      action: "开始工作",
      navId: "questions",
      targetId: "questions-section",
    });
  }
  return items.slice(0, 4);
}

function activityTime(value: unknown): string {
  if (typeof value !== "string" || !value.trim()) return "";
  return Number.isNaN(new Date(value).getTime()) ? "" : value;
}

function activityNav(type: string): RecentActivityItem["navId"] {
  if (type === "paper") return "papers";
  if (type === "comparison" || type === "finding") return "analysis";
  if (type === "idea") return "ideas";
  if (type === "question" || type === "claim") return "questions";
  if (["experiment", "run", "herdr_execution"].includes(type)) return "experiments";
  if (["automation", "herdr_launch_request", "agent_session", "job"].includes(type)) return "automation";
  return "inbox";
}

export function buildRecentActivity(data: WorkspaceData, index: V2ObjectIndex | null): RecentActivityItem[] {
  const items: RecentActivityItem[] = [];
  for (const object of index?.objects || []) {
    const occurredAt=activityTime(object.updated_at || object.created_at);
    if (!occurredAt) continue;
    const category:RecentActivityItem["category"]=["experiment","run"].includes(object.type)?"experiment":["automation","herdr_execution","herdr_launch_request","agent_session","job"].includes(object.type)?"system":"research";
    items.push({id:`object:${object.id}`,category,kind:object.type,title:object.title||object.id,detail:`${object.id} · ${object.lifecycle_status||"current"}`,occurredAt,navId:activityNav(object.type)});
  }
  for (const experiment of data.dashboard.experiments) {
    const occurredAt=activityTime(experiment.updated);
    if (occurredAt) items.push({id:`experiment:${experiment.id}`,category:"experiment",kind:"Experiment",title:experiment.title||experiment.id,detail:`${experiment.id} · ${experiment.workflow_stage||experiment.status||"current"}`,occurredAt,navId:"experiments"});
  }
  for (const run of data.dashboard.runs) {
    const occurredAt=activityTime(run.updated || run.created);
    if (occurredAt) items.push({id:`run:${run.id}`,category:"experiment",kind:"Run",title:run.variant||run.id,detail:`${run.id} · ${run.workflow_stage||run.status||"current"}`,occurredAt,navId:"experiments"});
  }
  for (const dispatch of data.dashboard.execution_outbox?.items || []) {
    const occurredAt=activityTime(dispatch.updated_at);
    if (!occurredAt) continue;
    items.push({id:`dispatch:${dispatch.dispatch_id||dispatch.run_id}:${occurredAt}`,category:"experiment",kind:"Execution dispatch",title:`${dispatch.run_id||"Run"} · ${dispatch.status||"unknown"}`,detail:dispatch.last_error||dispatch.dispatch_id||"Outbox state updated",occurredAt,navId:"experiments"});
  }
  for (const [position,event] of (data.dashboard.events || []).entries()) {
    const occurredAt=activityTime(event.occurred_at || event.time || event.updated_at || event.created_at);
    if (!occurredAt) continue;
    const kind=String(event.kind||event.action||event.type||"Experiment event");
    const title=String(event.summary||event.title||kind);
    const identity=String(event.run_id||event.experiment_id||event.object_id||"");
    items.push({id:`event:${position}:${occurredAt}`,category:"experiment",kind,title,detail:identity||"Experiment governance event",occurredAt,navId:"experiments"});
  }
  const deduped=new Map<string,RecentActivityItem>();
  for (const item of items.sort((left,right)=>new Date(right.occurredAt).getTime()-new Date(left.occurredAt).getTime())) {
    const key=`${item.navId}:${item.title}:${item.occurredAt}`;
    if (!deduped.has(key)) deduped.set(key,item);
  }
  return [...deduped.values()].slice(0,80);
}

export function projectSubtitle(project: Project): string {
  if (project.blockers?.length) return `${project.blockers.length} 项阻塞待处理`;
  if (project.next_actions?.length) return `${project.next_actions.length} 项下一步行动`;
  return "研究上下文已同步";
}
