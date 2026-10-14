import {
  Archive,
  ArrowLeft,
  Bot,
  CheckCircle2,
  ChevronDown,
  CircleAlert,
  Clipboard,
  Clock3,
  FileQuestion,
  FlaskConical,
  Library,
  LoaderCircle,
  PauseCircle,
  RefreshCw,
  RotateCcw,
  XCircle,
  PlayCircle,
  ShieldAlert,
  Sparkles,
  Workflow,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { applyContentIndexMigration, applyIdentityIndexMigration, bindCurrentPiSession, cancelV2Job, createAutomationDraft, createHerdrLaunchRequestDraft, initializeV2Store, loadAgentSessions, loadArchivableObjects, loadAutomations, loadHerdrLaunchRequests, loadMigrationDryRun, loadV2Jobs, retryV2Job, setObjectsArchived, transitionAutomation, transitionHerdrLaunchRequest } from "./api";
import type { AgentSessionIndex, ArchivableObject, CurrentPiSummary, HerdrLaunchRequest, HerdrReasoningEffort, HerdrTaskType, MigrationInventory, StoredAutomation, StoredJob } from "./api";
import type { WorkspaceData } from "./types";

type AutomationMode = "research" | "experiment" | "hybrid";

const modeInfo = {
  research: { label: "调研自动化", detail: "围绕目标检索、获取并阅读论文，形成候选结论。", icon: Library },
  experiment: { label: "实验自动化", detail: "围绕已有 Experiment 规划候选 Run，仍遵守审核与执行授权。", icon: FlaskConical },
  hybrid: { label: "调研 + 实验", detail: "先完成有边界调研，再经人工检查点进入实验阶段。", icon: Workflow },
};

export function AutomationWorkspace({ data, onBack }: { data: WorkspaceData; onBack: () => void }) {
  const [mode, setMode] = useState<AutomationMode>("research");
  const targets = mode === "experiment"
    ? data.dashboard.experiments.map((experiment) => ({ type: "experiment", id: experiment.id, label: `${experiment.id} · ${experiment.title}` }))
    : [
        ...data.questions.map((question) => ({ type: "question", id: question.id, label: `${question.id} · ${question.title}` })),
        ...data.dashboard.experiments.map((experiment) => ({ type: "experiment", id: experiment.id, label: `${experiment.id} · ${experiment.title}` })),
      ];
  const [targetKey, setTargetKey] = useState(targets[0] ? `${targets[0].type}:${targets[0].id}` : "");
  const [duration, setDuration] = useState(30);
  const [rounds, setRounds] = useState(5);
  const [interval, setInterval] = useState(1);
  const [copied, setCopied] = useState(false);
  const [migrationOpen, setMigrationOpen] = useState(false);
  const [migrationLoading, setMigrationLoading] = useState(false);
  const [migration, setMigration] = useState<MigrationInventory | null>(null);
  const [migrationError, setMigrationError] = useState("");
  const [migrationApplying, setMigrationApplying] = useState(false);
  const [migrationApplyResult, setMigrationApplyResult] = useState("");
  const [contentApplying, setContentApplying] = useState(false);
  const [contentApplyResult, setContentApplyResult] = useState("");
  const [storedAutomations, setStoredAutomations] = useState<StoredAutomation[]>([]);
  const [storedAutomation, setStoredAutomation] = useState<StoredAutomation | null>(null);
  const [governanceLoading, setGovernanceLoading] = useState(true);
  const [governanceBusy, setGovernanceBusy] = useState(false);
  const [governanceError, setGovernanceError] = useState("");
  const [jobs, setJobs] = useState<StoredJob[]>([]);
  const [jobsLoading, setJobsLoading] = useState(true);
  const [jobBusy, setJobBusy] = useState("");
  const [jobError, setJobError] = useState("");
  const [agentSessions, setAgentSessions] = useState<AgentSessionIndex[]>([]);
  const [currentPi, setCurrentPi] = useState<CurrentPiSummary | null>(null);
  const [sessionTarget, setSessionTarget] = useState("");
  const [sessionTaskType, setSessionTaskType] = useState("research");
  const [sessionLoading, setSessionLoading] = useState(true);
  const [sessionBusy, setSessionBusy] = useState(false);
  const [sessionError, setSessionError] = useState("");
  const [launchRequests, setLaunchRequests] = useState<HerdrLaunchRequest[]>([]);
  const [launchRequest, setLaunchRequest] = useState<HerdrLaunchRequest | null>(null);
  const [launchTarget, setLaunchTarget] = useState("");
  const [launchTaskType, setLaunchTaskType] = useState<HerdrTaskType>("research");
  const [launchAgentKind, setLaunchAgentKind] = useState<"pi" | "codex">("codex");
  const [launchSummary, setLaunchSummary] = useState("");
  const [launchEffort, setLaunchEffort] = useState<HerdrReasoningEffort>("medium");
  const [launchMaxTurns, setLaunchMaxTurns] = useState(5);
  const [launchLoading, setLaunchLoading] = useState(true);
  const [launchBusy, setLaunchBusy] = useState(false);
  const [launchError, setLaunchError] = useState("");
  const [archivable, setArchivable] = useState<ArchivableObject[]>([]);
  const [archiveSelected, setArchiveSelected] = useState<Set<string>>(new Set());
  const [archiveFilter, setArchiveFilter] = useState<"current" | "archived">("current");
  const [archiveLoading, setArchiveLoading] = useState(true);
  const [archiveBusy, setArchiveBusy] = useState(false);
  const [archiveError, setArchiveError] = useState("");
  const sessionTargets = [...storedAutomations.map((item) => ({ id: item.id, label: `Automation · ${item.title || item.id}` })), ...data.questions.map((item) => ({ id: item.id, label: `Question · ${item.id} · ${item.title}` })), ...data.dashboard.experiments.map((item) => ({ id: item.id, label: `Experiment · ${item.id} · ${item.title}` }))];
  const target = targets.find((item) => `${item.type}:${item.id}` === targetKey) || targets[0];
  const command = useMemo(() => target ? `/explore start --project-root ${JSON.stringify(data.project.path)} --target-type ${target.type} --target-id ${target.id} --duration-minutes ${duration} --max-rounds ${rounds} --interval-minutes ${interval}` : "", [data.project.path, duration, interval, rounds, target]);
  useEffect(() => {
    let current = true;
    setGovernanceLoading(true); setJobsLoading(true); setSessionLoading(true); setLaunchLoading(true); setArchiveLoading(true);
    loadAutomations(data.project.path).then((result) => { if (current) { setStoredAutomations(result.automations); setStoredAutomation((selected) => result.automations.find((item) => item.id === selected?.id) || result.automations.at(-1) || null); } }).catch((reason) => { if (current) setGovernanceError(reason instanceof Error ? reason.message : String(reason)); }).finally(() => { if (current) setGovernanceLoading(false); });
    loadV2Jobs(data.project.path).then((result) => { if (current) setJobs(result.jobs); }).catch((reason) => { if (current) setJobError(reason instanceof Error ? reason.message : String(reason)); }).finally(() => { if (current) setJobsLoading(false); });
    loadAgentSessions(data.project.path).then((result) => { if (current) { setAgentSessions(result.sessions); setCurrentPi(result.current_pi); } }).catch((reason) => { if (current) setSessionError(reason instanceof Error ? reason.message : String(reason)); }).finally(() => { if (current) setSessionLoading(false); });
    loadHerdrLaunchRequests(data.project.path).then((result) => { if (current) { setLaunchRequests(result.launch_requests); setLaunchRequest((selected) => result.launch_requests.find((item) => item.id === selected?.id) || result.launch_requests.at(-1) || null); } }).catch((reason) => { if (current) setLaunchError(reason instanceof Error ? reason.message : String(reason)); }).finally(() => { if (current) setLaunchLoading(false); });
    loadArchivableObjects(data.project.path).then((result) => { if (current) setArchivable(result.objects); }).catch((reason) => { if (current) setArchiveError(reason instanceof Error ? reason.message : String(reason)); }).finally(() => { if (current) setArchiveLoading(false); });
    return () => { current = false; };
  }, [data.project.path]);
  const inspectMigration = async () => {
    setMigrationOpen((open) => !open);
    if (migration || migrationLoading) return;
    setMigrationLoading(true); setMigrationError("");
    try { setMigration(await loadMigrationDryRun(data.project.path)); }
    catch (reason) { setMigrationError(reason instanceof Error ? reason.message : String(reason)); }
    finally { setMigrationLoading(false); }
  };
  const applyMigration = async () => {
    if (!migration?.identity_index_plan || migration.identity_index_plan.blocked) return;
    if (!window.confirm("第一阶段只写入 Question/Experiment identity 与明确关系索引；不会复制正文、修改 canonical 文件或切换 Markdown/JSON authority。是否继续？")) return;
    setMigrationApplying(true); setMigrationError("");
    try {
      if (!data.capabilities.project_store?.initialized) await initializeV2Store(data.project.path);
      const result=await applyIdentityIndexMigration(data.project.path);
      setMigrationApplyResult(`已索引 ${result.created}，复用 ${result.existing}，新增关系 ${result.relations_created} · ${result.checkpoint_hash}`);
      setMigration(await loadMigrationDryRun(data.project.path));
    } catch (reason) { setMigrationError(reason instanceof Error ? reason.message : String(reason)); }
    finally { setMigrationApplying(false); }
  };
  const applyContentMigration = async () => {
    if (!migration?.content_index_plan || migration.content_index_plan.blocked) return;
    if (!window.confirm("第二阶段只写入 Paper/Comparison/Finding/Claim 的 identity 与明确关系索引；不会复制正文、修改 canonical 文件或切换 Markdown/kernel authority。是否继续？")) return;
    setContentApplying(true); setMigrationError("");
    try {
      if (!data.capabilities.project_store?.initialized) await initializeV2Store(data.project.path);
      const result=await applyContentIndexMigration(data.project.path);
      setContentApplyResult(`已索引 ${result.created}，复用 ${result.existing}，新增关系 ${result.relations_created} · ${result.checkpoint_hash}`);
      setMigration(await loadMigrationDryRun(data.project.path));
    } catch (reason) { setMigrationError(reason instanceof Error ? reason.message : String(reason)); }
    finally { setContentApplying(false); }
  };
  const persistDraft = async () => {
    if (!target || !window.confirm("仅保存 Automation 治理草稿和预算，不启动 Agent、不发送命令。若项目尚未启用 v2 store，将先显式初始化。是否继续？")) return;
    setGovernanceBusy(true); setGovernanceError("");
    try {
      if (!data.capabilities.project_store?.initialized) await initializeV2Store(data.project.path);
      const result = await createAutomationDraft(data.project.path, { title: `${modeInfo[mode].label} · ${target.id}`, automation_type: mode, target_type: target.type, target_id: target.id, budget: { duration_minutes: duration, max_rounds: rounds, interval_minutes: interval } });
      setStoredAutomation(result.automation);
      setStoredAutomations((items) => [...items, result.automation]);
    } catch (reason) { setGovernanceError(reason instanceof Error ? reason.message : String(reason)); }
    finally { setGovernanceBusy(false); }
  };
  const advanceGovernance = async (status: string, phase?: string, approveExperimentPhase = false) => {
    if (!storedAutomation) return;
    const descriptions: Record<string, string> = { awaiting_approval: "提交审批不会启动任务。", active: approveExperimentPhase ? "这是 Hybrid 进入实验阶段的第二次独立批准；只改变治理状态，不执行实验。" : "批准激活只改变治理状态，仍不会自动发送命令或执行。", checkpoint: "进入检查点后必须再次批准才能继续。", paused: "暂停只改变治理状态，不控制外部 Agent 进程。", completed: "完成标记不会自动生成 validated synthesis。", completed_with_warnings: "将以有预警状态完成，未解决问题仍需保留。", failed: "失败标记将终止此治理对象，不删除任何产物。", cancelled: "取消不会删除事件和产物。" };
    if (!window.confirm(descriptions[status] || "确认治理状态变更？")) return;
    setGovernanceBusy(true); setGovernanceError("");
    try {
      const result = await transitionAutomation(data.project.path, storedAutomation, status, phase, approveExperimentPhase);
      const refreshed = await loadAutomations(data.project.path);
      setStoredAutomations(refreshed.automations);
      setStoredAutomation(refreshed.automations.find((item) => item.id === result.automation.id) || result.automation);
    } catch (reason) { setGovernanceError(reason instanceof Error ? reason.message : String(reason)); }
    finally { setGovernanceBusy(false); }
  };
  useEffect(() => { if (!sessionTarget && sessionTargets.length) setSessionTarget(sessionTargets[0].id); }, [sessionTarget, sessionTargets]);
  useEffect(() => { if (!launchTarget && sessionTargets.length) setLaunchTarget(sessionTargets[0].id); }, [launchTarget, sessionTargets]);
  const refreshArchive = async () => {
    setArchiveLoading(true); setArchiveError("");
    try { setArchivable((await loadArchivableObjects(data.project.path)).objects); setArchiveSelected(new Set()); }
    catch (reason) { setArchiveError(reason instanceof Error ? reason.message : String(reason)); }
    finally { setArchiveLoading(false); }
  };
  const applyArchive = async (restore: boolean) => {
    const selected=archivable.filter((item) => archiveSelected.has(item.id)); if (!selected.length) return;
    const reason=window.prompt(restore ? "请输入恢复理由：" : "请输入归档理由。不会删除 canonical 文件、staging 或事件：")?.trim(); if (!reason) return;
    if (!restore && selected.some((item) => item.impact.blockers.length)) { setArchiveError("所选对象包含归档阻塞项，请先解除 active 状态或 Job。 "); return; }
    setArchiveBusy(true); setArchiveError("");
    try { await setObjectsArchived(data.project.path,selected,reason,restore); await refreshArchive(); const auto=await loadAutomations(data.project.path); setStoredAutomations(auto.automations); setStoredAutomation((current) => auto.automations.find((item) => item.id===current?.id) || null); }
    catch (reasonValue) { setArchiveError(reasonValue instanceof Error ? reasonValue.message : String(reasonValue)); }
    finally { setArchiveBusy(false); }
  };
  const refreshSessions = async () => {
    setSessionLoading(true); setSessionError("");
    try { const result=await loadAgentSessions(data.project.path); setAgentSessions(result.sessions); setCurrentPi(result.current_pi); }
    catch (reason) { setSessionError(reason instanceof Error ? reason.message : String(reason)); }
    finally { setSessionLoading(false); }
  };
  const bindSession = async () => {
    if (!sessionTarget || !currentPi?.available) return;
    if (!window.confirm("仅保存不可逆 session identity 索引与目标关联；不会复制消息、Prompt、上下文或 session 文件路径。是否继续？")) return;
    setSessionBusy(true); setSessionError("");
    try {
      if (!data.capabilities.project_store?.initialized) await initializeV2Store(data.project.path);
      await bindCurrentPiSession(data.project.path,sessionTarget,sessionTaskType); await refreshSessions();
    } catch (reason) { setSessionError(reason instanceof Error ? reason.message : String(reason)); }
    finally { setSessionBusy(false); }
  };
  const refreshLaunchRequests = async (selectedId = launchRequest?.id) => {
    setLaunchLoading(true); setLaunchError("");
    try { const result=await loadHerdrLaunchRequests(data.project.path); setLaunchRequests(result.launch_requests); setLaunchRequest(result.launch_requests.find((item) => item.id===selectedId) || result.launch_requests.at(-1) || null); }
    catch (reason) { setLaunchError(reason instanceof Error ? reason.message : String(reason)); }
    finally { setLaunchLoading(false); }
  };
  const createLaunchRequest = async () => {
    if (!data.capabilities.project_store?.initialized) { setLaunchError("项目 v2 Store 尚未初始化。请使用现有显式初始化流程；此面板不会自动初始化。"); return; }
    const summary=launchSummary.trim();
    if (!launchTarget || !summary) { setLaunchError("请选择已有 identity，并填写简短任务摘要。"); return; }
    if (!window.confirm("确认 CREATE HERDR LAUNCH REQUEST DRAFT？仅保存治理草稿；不启动 Agent、不保存 Prompt 或命令。")) return;
    setLaunchBusy(true); setLaunchError("");
    try { const result=await createHerdrLaunchRequestDraft(data.project.path,{target_object_id:launchTarget,agent_kind:launchAgentKind,task_type:launchTaskType,task_summary:summary,safe_config:{reasoning_effort:launchEffort,max_turns:launchMaxTurns}}); setLaunchRequest(result.launch_request); setLaunchRequests((items)=>[...items,result.launch_request]); setLaunchSummary(""); }
    catch (reason) { setLaunchError(reason instanceof Error ? reason.message : String(reason)); }
    finally { setLaunchBusy(false); }
  };
  const advanceLaunchRequest = async (status: "awaiting_approval" | "approved" | "cancelled") => {
    if (!launchRequest) return;
    const copy={awaiting_approval:"确认 SUBMIT HERDR LAUNCH REQUEST FOR APPROVAL？提交只改变治理状态，不启动 Agent。",approved:"确认 APPROVE HERDR LAUNCH REQUEST？批准不等于启动；execution_started 仍为 false。",cancelled:"确认 CANCEL HERDR LAUNCH REQUEST？取消保留事件记录，不控制任何 Agent。"}[status];
    if (!window.confirm(copy)) return;
    setLaunchBusy(true); setLaunchError("");
    try { const result=await transitionHerdrLaunchRequest(data.project.path,launchRequest,status); await refreshLaunchRequests(result.launch_request.id); }
    catch (reason) { setLaunchError(reason instanceof Error ? reason.message : String(reason)); }
    finally { setLaunchBusy(false); }
  };
  const refreshJobs = async () => {
    setJobsLoading(true); setJobError("");
    try { setJobs((await loadV2Jobs(data.project.path)).jobs); }
    catch (reason) { setJobError(reason instanceof Error ? reason.message : String(reason)); }
    finally { setJobsLoading(false); }
  };
  const retryJob = async (job: StoredJob) => {
    const reason = window.prompt("请输入重试理由。此操作只把失败 Job 放回队列，不会启动 Worker：")?.trim();
    if (!reason) return;
    setJobBusy(job.id); setJobError("");
    try { await retryV2Job(data.project.path, job, reason); await refreshJobs(); }
    catch (error) { setJobError(error instanceof Error ? error.message : String(error)); }
    finally { setJobBusy(""); }
  };
  const cancelJob = async (job: StoredJob) => {
    const reason = window.prompt("请输入取消理由。只允许取消 queued Job；running Worker 不会被强制终止：")?.trim();
    if (!reason) return;
    setJobBusy(job.id); setJobError("");
    try { await cancelV2Job(data.project.path, job, reason); await refreshJobs(); }
    catch (error) { setJobError(error instanceof Error ? error.message : String(error)); }
    finally { setJobBusy(""); }
  };
  const copyCommand = async () => {
    if (!command) return;
    await navigator.clipboard.writeText(command);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  };

  return <div className="automation-workspace-page">
    <div className="automation-page-heading"><div><button className="back-button" onClick={onBack}><ArrowLeft size={15} />研究总览</button><div className="eyebrow">Bounded Automation</div><h1>自动化</h1><p>围绕 Question 或 Experiment 运行有预算、有停止条件的 Agent 流程。</p></div><label className="herdr-agent-default"><span>Herdr 新会话 Agent</span><select value={launchAgentKind} onChange={(event)=>setLaunchAgentKind(event.target.value as "pi"|"codex")}><option value="codex">Codex（实现代码推荐）</option><option value="pi">Pi（讨论 / Steward）</option></select><small>应用于下方新建的 Launch Request。</small></label></div>
    <div className="automation-status-strip"><div><Workflow size={17} /><span><small>持久治理对象</small><strong>{governanceLoading ? "…" : storedAutomations.length}</strong></span></div><div><PlayCircle size={17} /><span><small>已批准 active</small><strong>{storedAutomations.filter((item) => item.lifecycle_status === "active").length}</strong></span></div><div><PauseCircle size={17} /><span><small>暂停 / 检查点</small><strong>{storedAutomations.filter((item) => ["paused", "checkpoint"].includes(item.lifecycle_status)).length}</strong></span></div><div><ShieldAlert size={17} /><span><small>默认门禁</small><strong>人工确认</strong></span></div></div>
    <div className="automation-grid">
      <section className="automation-builder">
        <div className="automation-section-head"><div><h2>配置一个有边界的任务</h2><p>当前生成协调命令，不会在浏览器中伪装成已启动。</p></div><Bot size={18} /></div>
        <div className="mode-grid">{(Object.keys(modeInfo) as AutomationMode[]).map((id) => { const item = modeInfo[id]; const Icon = item.icon; return <button key={id} className={mode === id ? "selected" : ""} onClick={() => { setMode(id); const next = id === "experiment" ? data.dashboard.experiments[0] && `experiment:${data.dashboard.experiments[0].id}` : data.questions[0] && `question:${data.questions[0].id}`; setTargetKey(next || ""); }}><span><Icon size={18} /></span><strong>{item.label}</strong><small>{item.detail}</small></button>; })}</div>
        <div className="automation-form-grid"><label><span>目标对象</span><select value={target ? `${target.type}:${target.id}` : ""} onChange={(event) => setTargetKey(event.target.value)}>{targets.map((item) => <option key={`${item.type}:${item.id}`} value={`${item.type}:${item.id}`}>{item.label}</option>)}</select></label><label><span>最长时间</span><div className="number-input"><input type="number" min="5" max="240" value={duration} onChange={(event) => setDuration(Number(event.target.value))} /><em>分钟</em></div></label><label><span>最大轮次</span><div className="number-input"><input type="number" min="1" max="20" value={rounds} onChange={(event) => setRounds(Number(event.target.value))} /><em>轮</em></div></label><label><span>轮次间隔</span><div className="number-input"><input type="number" min="1" max="60" value={interval} onChange={(event) => setInterval(Number(event.target.value))} /><em>分钟</em></div></label></div>
        <div className="automation-command"><div><small>Terminal pi 协调命令</small><code>{command || "当前没有可用目标"}</code></div><button onClick={() => void copyCommand()} disabled={!command}><Clipboard size={15} />{copied ? "已复制" : "复制命令"}</button></div>
        <div className="automation-governance"><div><small>持久治理状态</small><strong>{governanceLoading ? "加载中…" : storedAutomation ? `${storedAutomation.lifecycle_status} · ${storedAutomation.phase}` : "尚未保存草稿"}</strong><span>保存、审批与实际命令执行是三个独立动作。</span>{storedAutomation?.deadline_at && <span>Deadline：{new Date(storedAutomation.deadline_at).toLocaleString()}</span>}</div><div>{!storedAutomation && !governanceLoading && <button onClick={() => void persistDraft()} disabled={governanceBusy}>保存治理草稿</button>}{storedAutomation?.lifecycle_status === "draft" && <><button onClick={() => void advanceGovernance("awaiting_approval")} disabled={governanceBusy}>提交审批</button><button onClick={() => void advanceGovernance("cancelled")} disabled={governanceBusy}>取消</button></>}{storedAutomation?.lifecycle_status === "awaiting_approval" && <><button onClick={() => void advanceGovernance("active", storedAutomation.automation_type === "experiment" ? "experiment_planning" : "research")} disabled={governanceBusy}>人工批准激活</button><button onClick={() => void advanceGovernance("cancelled")} disabled={governanceBusy}>取消</button></>}{storedAutomation?.lifecycle_status === "active" && <><button onClick={() => void advanceGovernance("checkpoint", storedAutomation.phase.startsWith("experiment") ? storedAutomation.phase : "research_review")} disabled={governanceBusy}>进入检查点</button><button onClick={() => void advanceGovernance("paused")} disabled={governanceBusy}>暂停</button><button onClick={() => void advanceGovernance("completed", "synthesis")} disabled={governanceBusy}>完成</button><button onClick={() => void advanceGovernance("completed_with_warnings", "synthesis")} disabled={governanceBusy}>有预警完成</button><button onClick={() => void advanceGovernance("failed")} disabled={governanceBusy}>标记失败</button></>}{storedAutomation?.lifecycle_status === "paused" && <><button onClick={() => void advanceGovernance("active", storedAutomation.phase)} disabled={governanceBusy}>人工批准恢复</button><button onClick={() => void advanceGovernance("cancelled")} disabled={governanceBusy}>取消</button></>}{storedAutomation?.lifecycle_status === "checkpoint" && <><button onClick={() => void advanceGovernance("active", storedAutomation.automation_type === "hybrid" && storedAutomation.phase === "research_review" ? "experiment_planning" : storedAutomation.phase, storedAutomation.automation_type === "hybrid" && storedAutomation.phase === "research_review")} disabled={governanceBusy}>{storedAutomation.automation_type === "hybrid" && storedAutomation.phase === "research_review" ? "批准进入实验阶段" : "人工批准继续"}</button><button onClick={() => void advanceGovernance("completed", "synthesis")} disabled={governanceBusy}>完成</button><button onClick={() => void advanceGovernance("cancelled")} disabled={governanceBusy}>取消</button></>}</div></div>
        {governanceError && <div className="detail-error">{governanceError}</div>}
      </section>
      <aside className="automation-guardrails"><div className="automation-section-head"><div><h2>门禁与停止条件</h2><p>任何模式都不能绕过这些边界</p></div><ShieldAlert size={18} /></div><div className="guardrail-list"><div><CheckCircle2 size={15} /><span><strong>调研证据</strong><small>论文只有实际获取、hash 并读取后才可标为 verified。</small></span></div><div><CheckCircle2 size={15} /><span><strong>阶段转换</strong><small>混合模式默认在调研完成后等待人工批准实验阶段。</small></span></div><div><CheckCircle2 size={15} /><span><strong>Run 治理</strong><small>候选 Run 保持 draft，不自动审核、授权、入队或执行。</small></span></div><div><Clock3 size={15} /><span><strong>有界停止</strong><small>达到 deadline、轮次上限、连续无新证据或需要用户判断时停止。</small></span></div></div><div className="automation-warning"><ShieldAlert size={17} /><div><strong>不是 validated synthesis</strong><p>Research Explorer 是 proposal 生成器。最终报告必须标明覆盖范围、degraded 来源和未解决问题。</p></div></div></aside>
    </div>
    <section className="archive-console"><div className="automation-section-head"><div><h2>软归档与恢复</h2><p>仅 v2 原生 Candidate / Automation；批量预检，整批原子，不提供硬删除</p></div><div className="archive-head-actions"><button className={archiveFilter==="current"?"selected":""} onClick={() => { setArchiveFilter("current"); setArchiveSelected(new Set()); }}>当前</button><button className={archiveFilter==="archived"?"selected":""} onClick={() => { setArchiveFilter("archived"); setArchiveSelected(new Set()); }}>已归档</button><button onClick={() => void refreshArchive()} disabled={archiveLoading}><RefreshCw className={archiveLoading?"spin":""} size={13} />刷新</button></div></div>{archiveError && <div className="detail-error"><CircleAlert size={15} />{archiveError}</div>}<div className="archive-safety"><Archive size={15} /><span><strong>只改变 lifecycle status</strong><small>canonical 文件、staging、事件、Job、关系和 session 索引均保留。</small></span><b>Hard delete unavailable</b></div><div className="archive-list">{archivable.filter((item) => archiveFilter==="archived" ? item.lifecycle_status==="archived" : item.lifecycle_status!=="archived").map((item) => <label key={item.id} className={item.impact.blockers.length?"blocked":""}><input type="checkbox" checked={archiveSelected.has(item.id)} onChange={(event) => setArchiveSelected((current) => { const next=new Set(current); if(event.target.checked) next.add(item.id); else next.delete(item.id); return next; })} /><span className="archive-type">{item.type==="paper_candidate"?"Candidate":"Automation"}</span><div><strong>{item.title || item.id}</strong><small>{item.id} · {item.lifecycle_status} · revision {item.revision}</small><small>{item.impact.relations} relations · {item.impact.agent_sessions} sessions · {Object.entries(item.impact.jobs).map(([key,value]) => `${key} ${value}`).join(" · ") || "0 jobs"}</small>{item.impact.blockers.map((blocker) => <em key={blocker}>{blocker}</em>)}</div></label>)}{!archiveLoading && !archivable.some((item) => archiveFilter==="archived" ? item.lifecycle_status==="archived" : item.lifecycle_status!=="archived") && <div className="job-empty">当前筛选没有可治理对象。</div>}</div><div className="archive-actions"><span>已选择 {archiveSelected.size} 项；任何 revision/blocker 冲突都会整批拒绝。</span>{archiveFilter==="current"?<button onClick={() => void applyArchive(false)} disabled={!archiveSelected.size||archiveBusy}>确认软归档</button>:<button onClick={() => void applyArchive(true)} disabled={!archiveSelected.size||archiveBusy}>恢复原状态</button>}</div></section>
    <section className="agent-session-console"><div className="automation-section-head"><div><h2>Agent Session 索引</h2><p>只关联已验证 pi identity；不读取消息、不复制 Prompt、不暴露 session 路径</p></div><div className="job-console-actions"><span>{agentSessions.length}</span><button onClick={() => void refreshSessions()} disabled={sessionLoading}><RefreshCw className={sessionLoading ? "spin" : ""} size={14} />刷新</button></div></div>{sessionError && <div className="detail-error"><CircleAlert size={15} />{sessionError}</div>}<div className="current-pi-summary"><span className={`pi-state ${currentPi?.status || "unavailable"}`}><Bot size={16} /></span><div><small>当前已验证 pi 快照</small><strong>{sessionLoading ? "读取中…" : currentPi?.available ? currentPi.session_name || currentPi.identity_fingerprint : "不可用"}</strong><span>{currentPi?.available ? `${currentPi.status} · ${currentPi.identity_fingerprint} · 最后核验 ${currentPi.last_verified_at ? new Date(currentPi.last_verified_at).toLocaleString() : "未知"}` : "请先在旧版 pi 控制面明确绑定或恢复一个 session"}</span></div><div className="privacy-badges"><b>消息不暴露</b><b>Prompt 不复制</b><b>路径不暴露</b></div></div><div className="session-bind-form"><label><span>绑定目标</span><select value={sessionTarget} onChange={(event) => setSessionTarget(event.target.value)} disabled={!sessionTargets.length}>{sessionTargets.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}</select></label><label><span>任务类型</span><select value={sessionTaskType} onChange={(event) => setSessionTaskType(event.target.value)}><option value="research">Research</option><option value="discussion">Discussion</option><option value="implementation">Implementation</option><option value="monitoring">Monitoring</option><option value="analysis">Analysis</option></select></label><button onClick={() => void bindSession()} disabled={sessionBusy || !currentPi?.available || !sessionTarget}>绑定当前已验证 pi</button></div><div className="session-authority-note"><ShieldAlert size={14} />Question/Experiment 只创建最小 reference identity；正文 authority 仍分别是 Markdown / legacy JSON。</div>{agentSessions.length ? <div className="session-index-list">{agentSessions.map((session) => <article key={session.id}><span className={`session-status ${session.status}`}><Bot size={15} /></span><div><strong>{session.object_id}</strong><small>{session.provider} · {session.task_type} · {session.identity_fingerprint}</small><small>last seen {session.last_seen_at ? new Date(session.last_seen_at).toLocaleString() : "未知"} · revision {session.revision}</small></div><b>{session.status}</b></article>)}</div> : <div className="job-empty">{sessionLoading ? <><LoaderCircle className="spin" size={18} />读取 session 索引</> : <>尚未建立 v2 session 索引。</>}</div>}</section>
    <details className="herdr-launch-console"><summary><span><Bot size={17} /></span><div><strong>Herdr Launch Requests</strong><small>持久人工治理；批准不等于启动</small></div><b>{launchLoading ? "…" : launchRequests.length}</b><ChevronDown size={16} /></summary><div className="herdr-launch-body"><div className="herdr-capability"><span>Herdr capability</span><b>{data.capabilities.herdr?.managed ? "managed" : "not managed"}</b><b>{data.capabilities.herdr?.cli_available ? "CLI available" : "CLI unavailable"}</b><b>{data.capabilities.herdr?.codex_supported ? "codex supported" : "codex unavailable"}</b><em>discovery only</em></div>{!data.capabilities.project_store?.initialized && <div className="herdr-store-note"><ShieldAlert size={14} /><span><strong>需要显式初始化 v2 Store</strong><small>请使用现有初始化流程。此面板不会静默创建 SQLite。</small></span></div>}{launchError && <div className="detail-error"><CircleAlert size={15} />{launchError}</div>}<div className="herdr-launch-form"><label><span>已有 identity 目标</span><select value={launchTarget} onChange={(event)=>setLaunchTarget(event.target.value)} disabled={!sessionTargets.length}>{sessionTargets.map((item)=><option key={item.id} value={item.id}>{item.label}</option>)}</select></label><label><span>任务类型</span><select value={launchTaskType} onChange={(event)=>setLaunchTaskType(event.target.value as HerdrTaskType)}><option value="research">Research</option><option value="analysis">Analysis</option><option value="discussion">Discussion</option><option value="implementation">Implementation</option><option value="monitoring">Monitoring</option></select></label><label><span>Reasoning</span><select value={launchEffort} onChange={(event)=>setLaunchEffort(event.target.value as HerdrReasoningEffort)}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="xhigh">XHigh</option></select></label><label><span>最大轮次</span><input type="number" min="1" max="20" value={launchMaxTurns} onChange={(event)=>setLaunchMaxTurns(Math.max(1,Math.min(20,Number(event.target.value)||1)))} /></label><label className="herdr-summary-field"><span>简短任务摘要（最多 500 字符；不要填写 Prompt、命令、路径或秘密）</span><input maxLength={500} value={launchSummary} onChange={(event)=>setLaunchSummary(event.target.value)} placeholder="例如：复核证据映射并列出缺口" /></label><button onClick={()=>void createLaunchRequest()} disabled={launchBusy||!launchTarget||!launchSummary.trim()||!data.capabilities.project_store?.initialized}>保存 Launch Request 草稿</button></div><div className="herdr-no-execution"><ShieldAlert size={15} /><strong>execution_started: false · 批准不等于启动</strong><span>这里只保存和审核请求；没有 execute、start 或 prompt 操作。</span></div>{launchRequests.length ? <div className="herdr-request-list">{[...launchRequests].reverse().map((item)=><button key={item.id} className={launchRequest?.id===item.id?"selected":""} onClick={()=>setLaunchRequest(item)}><span>{item.lifecycle_status}</span><div><strong>{item.task_summary}</strong><small>{item.id} · target {item.target_object_id} · revision {item.revision}</small><small>codex · {item.task_type} · {item.safe_config.reasoning_effort} · max {item.safe_config.max_turns} turns</small></div></button>)}</div> : <div className="job-empty">{launchLoading?"读取 Launch Requests…":"尚无 Launch Request。"}</div>}{launchRequest && <div className="herdr-request-detail"><div><small>当前请求</small><strong>{launchRequest.lifecycle_status} · revision {launchRequest.revision}</strong><span>target {launchRequest.target_object_id} · {launchRequest.safe_config.reasoning_effort} · max {launchRequest.safe_config.max_turns} turns</span></div><div>{launchRequest.lifecycle_status==="draft"&&<><button onClick={()=>void advanceLaunchRequest("awaiting_approval")} disabled={launchBusy}>提交审批</button><button onClick={()=>void advanceLaunchRequest("cancelled")} disabled={launchBusy}>取消</button></>}{launchRequest.lifecycle_status==="awaiting_approval"&&<><button onClick={()=>void advanceLaunchRequest("approved")} disabled={launchBusy}>人工批准</button><button onClick={()=>void advanceLaunchRequest("cancelled")} disabled={launchBusy}>取消</button></>}</div></div>}{launchRequest?.events?.length ? <div className="herdr-event-log"><strong>事件时间线</strong>{[...launchRequest.events].reverse().map((event)=><div key={event.id}><time>{new Date(event.occurred_at).toLocaleString()}</time><b>{event.kind}</b><span>{event.summary}</span></div>)}</div> : null}</div></details>
    <section className="job-console"><div className="automation-section-head"><div><h2>持久 Job 队列</h2><p>只读观察 Worker lease；人工操作不会启动或强制终止 Worker</p></div><div className="job-console-actions"><span>{jobs.length}</span><button onClick={() => void refreshJobs()} disabled={jobsLoading}><RefreshCw className={jobsLoading ? "spin" : ""} size={14} />刷新</button></div></div>{jobError && <div className="detail-error"><CircleAlert size={15} />{jobError}</div>}<div className="job-kpis"><div><small>Queued</small><strong>{jobs.filter((job) => job.status === "queued").length}</strong></div><div><small>Running</small><strong>{jobs.filter((job) => job.status === "running").length}</strong></div><div><small>Failed</small><strong>{jobs.filter((job) => job.status === "failed").length}</strong></div><div><small>Succeeded</small><strong>{jobs.filter((job) => job.status === "succeeded").length}</strong></div></div>{jobs.length ? <div className="job-list">{[...jobs].reverse().map((job) => { const dependency=jobs.find((item) => item.id===job.depends_on_job_id); return <article key={job.id} className={`job-row ${job.status}`}><span className="job-kind">{job.kind === "paper_download" ? "PDF" : job.kind === "mineru" ? "MinerU" : job.kind}</span><div className="job-copy"><strong>{job.id}</strong><small>目标 {job.target_object_id || "—"} · attempt {job.attempt || 0} · revision {job.revision}</small>{job.depends_on_job_id && <small>依赖 {job.depends_on_job_id} · {dependency?.status || "missing"}</small>}{job.status === "running" && <small>Worker {job.lease_owner || "unknown"} · heartbeat {job.last_heartbeat_at ? new Date(job.last_heartbeat_at).toLocaleString() : "无"} · lease 至 {job.lease_expires_at ? new Date(job.lease_expires_at).toLocaleString() : "无"}</small>}{job.error_message && <span className="job-error">{job.error_class || "Error"}：{job.error_message}</span>}</div><div className="job-state"><b>{job.status}</b>{typeof job.progress === "number" && <small>{Math.round(job.progress * 100)}%</small>}</div><div className="job-actions">{job.status === "failed" && <button onClick={() => void retryJob(job)} disabled={jobBusy === job.id}><RotateCcw size={13} />重试</button>}{job.status === "queued" && <button onClick={() => void cancelJob(job)} disabled={jobBusy === job.id}><XCircle size={13} />取消</button>}</div></article>; })}</div> : <div className="job-empty">{jobsLoading ? <><LoaderCircle className="spin" size={18} />读取队列</> : <>当前没有 v2 Job；浏览页面不会创建任务。</>}</div>}<div className="job-boundary"><ShieldAlert size={15} />Running Job 不提供网页强制取消；必须由 lease/Worker 协议安全结束，避免进程继续写 staging。</div></section>
    <section className={`migration-inspector ${migrationOpen ? "open" : ""}`}><button className="migration-toggle" onClick={() => void inspectMigration()} aria-expanded={migrationOpen}><span><ShieldAlert size={17} /></span><div><strong>迁移 Dry-run</strong><small>只读扫描旧数据 authority、hash 与冲突，不创建 v2 数据库</small></div>{migration ? <b>{migration.summary.warnings + migration.identity_index_plan.summary.warnings + migration.content_index_plan.summary.warnings} 个预警</b> : <b>未执行</b>}{migrationLoading ? <LoaderCircle className="spin" size={16} /> : <ChevronDown size={16} />}</button>{migrationOpen && <div className="migration-body">{migrationError && <div className="detail-error">{migrationError}</div>}{migration && <><div className="migration-kpis"><div><small>来源文件</small><strong>{migration.summary.source_files}</strong></div><div><small>论文 PDF</small><strong>{migration.summary.paper_pdfs}</strong></div><div><small>预警</small><strong>{migration.summary.warnings + migration.identity_index_plan.summary.warnings + migration.content_index_plan.summary.warnings}</strong></div><div><small>写入动作</small><strong>{migration.will_write ? "存在" : "无"}</strong></div></div><div className="migration-warnings">{[...migration.warnings, ...migration.identity_index_plan.warnings, ...migration.content_index_plan.warnings].length ? [...migration.warnings, ...migration.identity_index_plan.warnings, ...migration.content_index_plan.warnings].map((warning, index) => <div key={`${warning.path}-${index}`}><code>{warning.kind}</code><strong>{warning.path}</strong><span>{warning.message}</span></div>) : <p>未发现迁移冲突；正式迁移仍需单独人工批准。</p>}</div><div className="migration-apply"><div><strong>Identity Index · Phase 1</strong><span>Question {migration.identity_index_plan.summary.questions} · Experiment {migration.identity_index_plan.summary.experiments} · 明确关系 {migration.identity_index_plan.summary.relations}</span><small>Markdown / legacy JSON authority 保持不变；不复制正文。</small></div><button onClick={() => void applyMigration()} disabled={migrationApplying || migration.identity_index_plan.blocked}>{migrationApplying ? "应用中" : migration.identity_index_plan.blocked ? "存在阻塞" : "显式应用索引"}</button></div>{migrationApplyResult && <div className="migration-result">{migrationApplyResult}</div>}<div className="migration-apply"><div><strong>Content Index · Phase 2</strong><span>Paper {migration.content_index_plan.summary.papers} · Comparison {migration.content_index_plan.summary.comparisons} · Finding {migration.content_index_plan.summary.findings} · Claim {migration.content_index_plan.summary.claims} · 关系 {migration.content_index_plan.summary.relations}</span><small>PDF / Markdown / kernel authority 保持不变；不复制正文。</small></div><button onClick={() => void applyContentMigration()} disabled={contentApplying || migration.content_index_plan.blocked}>{contentApplying ? "应用中" : migration.content_index_plan.blocked ? "存在阻塞" : "显式应用内容索引"}</button></div>{contentApplyResult && <div className="migration-result">{contentApplyResult}</div>}<div className="migration-history"><strong>持久迁移检查点</strong>{migration.identity_index_history.length ? migration.identity_index_history.map((item) => <div key={`${item.checkpoint_hash}-${item.applied_at}`}><time>{item.applied_at}</time><code>{item.checkpoint_hash}</code><span>{item.status} · 新建 {item.details.created ?? "?"} · 复用 {item.details.existing ?? "?"} · 关系 {item.details.relations_created ?? "?"}</span></div>) : <p>尚无已应用记录</p>}</div><div className="migration-history"><strong>内容索引检查点</strong>{migration.content_index_history.length ? migration.content_index_history.map((item) => <div key={`${item.checkpoint_hash}-${item.applied_at}`}><time>{item.applied_at}</time><code>{item.checkpoint_hash}</code><span>{item.status} · 新建 {item.details.created ?? "?"} · 复用 {item.details.existing ?? "?"} · 关系 {item.details.relations_created ?? "?"}</span></div>) : <p>尚无内容索引记录</p>}</div><div className="migration-excluded">已排除：{migration.excluded.join("、")}</div></>}</div>}</section>
    <section className="automation-history"><div className="automation-section-head"><div><h2>持久治理记录</h2><p>页面刷新后从 v2 store 恢复；选择记录不会启动 Agent</p></div><div className="automation-history-actions"><span>{storedAutomations.length}</span><button onClick={() => { setStoredAutomation(null); setGovernanceError(""); }}>配置新草稿</button></div></div>{storedAutomations.length ? <div className="automation-history-list">{[...storedAutomations].reverse().map((item) => <article key={item.id} className={storedAutomation?.id === item.id ? "selected" : ""} onClick={() => setStoredAutomation(item)}><span><Workflow size={16} /></span><div><strong>{item.title || item.id}</strong><small>{item.id} · {item.automation_type} · {item.lifecycle_status} / {item.phase}</small><small>预算 {String(item.budget.duration_minutes || "–")} 分钟 · {String(item.budget.max_rounds || "–")} 轮 · revision {item.revision}</small></div><b>{item.events?.length || 0} events</b></article>)}</div> : <div className="automation-empty"><Sparkles size={23} /><strong>{governanceLoading ? "正在加载持久记录" : "还没有持久治理记录"}</strong><span>保存草稿不会发送命令；复制命令也不会被系统标记为已执行。</span></div>}{storedAutomation && <div className="automation-event-log"><h3>审计时间线 · {storedAutomation.id}</h3>{storedAutomation.events?.length ? [...storedAutomation.events].reverse().map((event) => <div key={event.id}><time>{new Date(event.occurred_at).toLocaleString()}</time><strong>{event.kind}</strong><span>{event.summary}</span></div>) : <p>暂无事件。</p>}</div>}</section>
  </div>;
}
