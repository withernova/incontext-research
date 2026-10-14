import {
  Activity,
  Archive,
  ArrowRight,
  Beaker,
  Bell,
  BookOpen,
  Bot,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  Clock3,
  Database,
  FileQuestion,
  FlaskConical,
  Inbox,
  Library,
  Lightbulb,
  PanelLeftClose,
  PanelLeftOpen,
  RefreshCw,
  Search,
  Settings,
  Sparkles,
  Workflow,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { listProjects, loadV2Objects, loadWorkspace } from "./api";
import type { V2ObjectIndex } from "./api";
import { buildAttentionItems, buildRecentActivity, projectSubtitle, type RecentActivityItem } from "./model";
import { PaperLibrary } from "./PaperLibrary";
import { QuestionWorkspace } from "./QuestionWorkspace";
import { ExperimentWorkspace } from "./ExperimentWorkspace";
import { ResearchAnalysisWorkspace } from "./ResearchAnalysisWorkspace";
import { AutomationWorkspace } from "./AutomationWorkspace";
import { IdeaWorkspace } from "./IdeaWorkspace";
import { IntakeWorkspace } from "./IntakeWorkspace";
import { AgentSettingsWorkspace } from "./AgentSettingsWorkspace";
import type { Project, WorkspaceData } from "./types";

const navGroups = [
  {
    label: "工作台",
    items: [
      { id: "inbox", label: "收件箱", icon: Inbox },
      { id: "activity", label: "最近活动", icon: Clock3 },
    ],
  },
  {
    label: "研究",
    items: [
      { id: "papers", label: "论文库", icon: Library },
      { id: "analysis", label: "研究分析", icon: BookOpen },
      { id: "ideas", label: "Ideas", icon: Lightbulb },
      { id: "questions", label: "Questions", icon: FileQuestion },
    ],
  },
  {
    label: "执行",
    items: [
      { id: "experiments", label: "实验", icon: FlaskConical },
      { id: "automation", label: "自动化", icon: Workflow },
    ],
  },
  {
    label: "系统",
    items: [{ id: "intake", label: "项目 Intake", icon: Settings },{id:"agent-settings",label:"Agent 配置",icon:Bot}],
  },
];
const workspaceNavIds=new Set(["papers","analysis","ideas","questions","experiments","automation","intake","agent-settings"]);

function shortState(state: string): string {
  return (state || "未登记").replaceAll("_", " ").toLowerCase();
}

function statusLabel(status: string | undefined): string {
  const labels: Record<string, string> = {
    implementing: "实现中",
    planned: "已规划",
    draft: "草稿",
    completed: "已完成",
    investigating: "调查中",
    open: "开放",
    active: "进行中",
  };
  return labels[status || ""] || (status || "未登记").replaceAll("_", " ");
}

export function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectPath, setProjectPath] = useState("");
  const [data, setData] = useState<WorkspaceData | null>(null);
  const [objectIndex, setObjectIndex] = useState<V2ObjectIndex | null>(null);
  const [loading, setLoading] = useState(true);
  const [viewRefreshing,setViewRefreshing]=useState(false);
  const [error, setError] = useState("");
  const [activeNav, setActiveNav] = useState(() => {
    const saved=window.localStorage.getItem("survey-v2-active-nav")||"inbox";
    return ["inbox","activity",...workspaceNavIds].includes(saved)?saved:"inbox";
  });
  const [query, setQuery] = useState("");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => window.localStorage.getItem("survey-v2-sidebar") === "collapsed");

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const available = await listProjects();
      setProjects(available);
      const selected = available.find((project) => project.path === projectPath) || available[0];
      if (!selected) {
        setData(null);
        setProjectPath("");
        return;
      }
      setProjectPath(selected.path);
      setData(await loadWorkspace(selected));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setLoading(false);
    }
  }, [projectPath]);

  useEffect(() => {
    void refresh();
  }, []); // Load once; project changes use the selector handler.

  useEffect(() => {
    if (!projectPath) { setObjectIndex(null); return; }
    let current = true;
    loadV2Objects(projectPath).then((result) => { if (current) setObjectIndex(result); }).catch(() => { if (current) setObjectIndex(null); });
    return () => { current = false; };
  }, [projectPath]);

  useEffect(()=>{window.localStorage.setItem("survey-v2-active-nav",activeNav)},[activeNav]);

  const chooseProject = async (path: string) => {
    const selected = projects.find((project) => project.path === path);
    if (!selected) return;
    setProjectPath(path);
    setLoading(true);
    setError("");
    try {
      setData(await loadWorkspace(selected));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setLoading(false);
    }
  };

  const refreshCurrentWorkspace = useCallback(async () => {
    const selected = projects.find((project) => project.path === projectPath);
    if (!selected) return;
    const [nextData, nextIndex] = await Promise.all([
      loadWorkspace(selected),
      loadV2Objects(selected.path).catch(() => null),
    ]);
    setData(nextData);
    setObjectIndex(nextIndex);
  }, [projectPath, projects]);

  const refreshVisibleWorkspace=useCallback(async()=>{setViewRefreshing(true);setError("");try{await refreshCurrentWorkspace()}catch(reason){setError(`当前视图刷新失败：${reason instanceof Error?reason.message:String(reason)}`)}finally{setViewRefreshing(false)}},[refreshCurrentWorkspace]);

  const attention = useMemo(() => (data ? buildAttentionItems(data) : []), [data]);
  const recentActivity = useMemo(() => data ? buildRecentActivity(data,objectIndex) : [], [data,objectIndex]);
  const searchResults = useMemo(() => {
    const needle = query.trim().toLocaleLowerCase();
    if (!needle || !data) return [];
    return [
      ...data.papers.filter((paper) => paper.title.toLocaleLowerCase().includes(needle)).map((paper) => ({ type: "论文", title: paper.title, target: "papers-section" })),
      ...data.questions.filter((question) => `${question.id} ${question.title}`.toLocaleLowerCase().includes(needle)).map((question) => ({ type: "Question", title: `${question.id} · ${question.title}`, target: "questions-section" })),
      ...data.dashboard.experiments.filter((experiment) => `${experiment.id} ${experiment.title}`.toLocaleLowerCase().includes(needle)).map((experiment) => ({ type: "Experiment", title: `${experiment.id} · ${experiment.title}`, target: "experiments-section" })),
    ].slice(0, 8);
  }, [data, query]);
  const runs = data?.dashboard.runs || [];
  const completedRuns = runs.filter((run) => (run.status || "").startsWith("completed")).length;
  const activeRuns = runs.filter(
    (run) => !["completed", "failed", "aborted", "cancelled"].some((status) =>
      (run.status || "").startsWith(status),
    ),
  ).length;

  const navigateTo = (navId: string, targetId: string) => {
    setActiveNav(navId);
    if (workspaceNavIds.has(navId)) {
      void refreshVisibleWorkspace();
    } else {
      requestAnimationFrame(() => document.getElementById(targetId)?.scrollIntoView({ behavior: "smooth", block: "start" }));
    }
  };

  const toggleSidebar = () => {
    setSidebarCollapsed((current) => {
      const next = !current;
      window.localStorage.setItem("survey-v2-sidebar", next ? "collapsed" : "expanded");
      return next;
    });
  };

  return (
    <div className={`app-shell ${sidebarCollapsed ? "sidebar-collapsed" : ""}`}>
      <aside className="sidebar">
        <div className="brand-row">
          <div className="brand-mark"><img src={`${import.meta.env.BASE_URL}survey-tool-icon.svg`} alt="" /></div>
          <div>
            <strong>Survey Tool</strong>
            <span>Research OS · 2.0</span>
          </div>
          <button className="icon-button sidebar-toggle" title={sidebarCollapsed ? "展开侧栏" : "收起侧栏"} aria-label={sidebarCollapsed ? "展开侧栏" : "收起侧栏"} onClick={toggleSidebar}>
            {sidebarCollapsed ? <PanelLeftOpen size={17} /> : <PanelLeftClose size={17} />}
          </button>
        </div>

        <div className="project-switcher">
          <label htmlFor="project-select">当前研究项目</label>
          <div className="select-wrap">
            <select
              id="project-select"
              value={projectPath}
              onChange={(event) => void chooseProject(event.target.value)}
            >
              {projects.map((project) => (
                <option key={project.path} value={project.path}>{project.label || project.name}</option>
              ))}
            </select>
            <ChevronDown size={15} />
          </div>
          {data && <span>{projectSubtitle(data.project)}</span>}
        </div>

        <nav aria-label="主导航">
          {navGroups.map((group) => (
            <div className="nav-group" key={group.label}>
              <div className="nav-label">{group.label}</div>
              {group.items.map((item) => {
                const Icon = item.icon;
                const count = item.id === "papers" ? data?.papers.length
                  : item.id === "ideas" ? data?.ideas.length
                  : item.id === "questions" ? data?.questions.length
                  : item.id === "experiments" ? data?.dashboard.experiments.length
                  : item.id === "inbox" ? attention.length
                  : item.id === "activity" ? recentActivity.length
                  : undefined;
                return (
                  <button
                    className={`nav-item ${activeNav === item.id ? "active" : ""}`}
                    key={item.id}
                    title={item.label}
                    onClick={() => navigateTo(item.id, item.id === "inbox" ? "attention-section" : item.id === "papers" ? "papers-section" : item.id === "questions" ? "questions-section" : item.id === "experiments" ? "experiments-section" : "objects-section")}
                  >
                    <Icon size={17} />
                    <span>{item.label}</span>
                    {typeof count === "number" && <b>{count}</b>}
                  </button>
                );
              })}
            </div>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <button className={`nav-item ${activeNav==="agent-settings"?"active":""}`} onClick={()=>setActiveNav("agent-settings")}><Bot size={17} /><span>Agent 配置</span></button>
          <button className={`nav-item ${activeNav==="intake"?"active":""}`} onClick={()=>setActiveNav("intake")}><Settings size={17} /><span>项目设置</span></button>
          <a className="legacy-link" href="/">返回 1.x 工作台 <ArrowRight size={14} /></a>
        </div>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div className="search-wrap">
            <div className="search-box">
              <Search size={17} />
              <input aria-label="全局搜索" placeholder="搜索论文、问题或实验" value={query} onChange={(event) => setQuery(event.target.value)} />
              <kbd>Ctrl K</kbd>
            </div>
            {query.trim() && (
              <div className="search-results">
                {searchResults.length ? searchResults.map((result, index) => (
                  <button key={`${result.type}-${index}`} onClick={() => { setQuery(""); navigateTo(result.type === "论文" ? "papers" : result.type === "Question" ? "questions" : "experiments", result.target); }}>
                    <span>{result.type}</span><strong>{result.title}</strong><ArrowRight size={14} />
                  </button>
                )) : <div className="search-empty">没有匹配的研究对象</div>}
              </div>
            )}
          </div>
          <div className="top-actions">
            <button className="persistent-refresh" title="刷新当前项目（保留当前页面）" aria-label="刷新当前项目" onClick={()=>void refreshVisibleWorkspace()} disabled={loading||viewRefreshing}><RefreshCw size={15} className={loading||viewRefreshing?"spin":""}/><span>{loading||viewRefreshing?"刷新中":"刷新"}</span></button>
            <button className="icon-button" title="帮助" aria-label="帮助"><CircleHelp size={18} /></button>
            <button className="icon-button notification" title="通知" aria-label="通知">
              <Bell size={18} />
              {attention.length > 0 && <span />}
            </button>
            <div className="agent-state"><span /> Agent 可用</div>
          </div>
        </header>

        <div className={`content ${["papers", "analysis", "ideas", "questions", "experiments", "automation", "intake", "agent-settings"].includes(activeNav) ? "paper-content" : ""}`}>
          {error && (
            <div className="error-banner">
              <strong>无法加载项目</strong><span>{error}</span>
              <button onClick={() => void refresh()}><RefreshCw size={15} />重试</button>
            </div>
          )}

          {activeNav === "activity" && data ? <RecentActivityView items={recentActivity} loading={loading} onRefresh={refreshCurrentWorkspace} onOpen={(navId)=>setActiveNav(navId)}/> : activeNav === "agent-settings" && data ? <AgentSettingsWorkspace projectPath={data.project.path} onBack={() => setActiveNav("inbox")}/> : activeNav === "intake" && data ? <IntakeWorkspace data={data} onChanged={refreshCurrentWorkspace} onBack={() => setActiveNav("inbox")} /> : activeNav === "ideas" && data ? <IdeaWorkspace data={data} onChanged={refreshCurrentWorkspace} onBack={() => setActiveNav("inbox")} /> : activeNav === "papers" && data ? <PaperLibrary data={data} objectIndex={objectIndex} onChanged={refreshCurrentWorkspace} onBack={() => setActiveNav("inbox")} /> : activeNav === "analysis" && data ? <ResearchAnalysisWorkspace data={data} objectIndex={objectIndex} onChanged={refreshCurrentWorkspace} onBack={() => setActiveNav("inbox")} /> : activeNav === "questions" && data ? <QuestionWorkspace data={data} objectIndex={objectIndex} onChanged={refreshCurrentWorkspace} onBack={() => setActiveNav("inbox")} /> : activeNav === "experiments" && data ? <ExperimentWorkspace data={data} onChanged={refreshCurrentWorkspace} onBack={() => setActiveNav("inbox")} /> : activeNav === "automation" && data ? <AutomationWorkspace data={data} onBack={() => setActiveNav("inbox")} /> : <>
          <section className="page-heading">
            <div>
              <div className="eyebrow">收件箱 · 研究总览</div>
              <h1>{data?.project.label || data?.project.name || "Survey Tool 2.0"}</h1>
              <p>从待处理事项进入工作，论文、问题与实验按各自语义组织。</p>
            </div>
            <div className="heading-actions">
              <button className="secondary-button" onClick={() => void refresh()} disabled={loading}>
                <RefreshCw size={16} className={loading ? "spin" : ""} />刷新
              </button>
              <a className="primary-button" href="/" title="在现有工作台中创建研究对象"><Sparkles size={16} />新建研究任务</a>
            </div>
          </section>

          <section className="status-strip" aria-label="项目摘要">
            <div><span className="status-dot green" /><small>研究状态</small><strong>{shortState(data?.project.state || "")}</strong></div>
            <div><small>论文</small><strong>{data?.papers.length ?? "-"}</strong><span>篇已登记</span></div>
            <div><small>开放问题</small><strong>{data?.questions.filter((q) => q.status !== "archived").length ?? "-"}</strong><span>项在跟进</span></div>
            <div><small>Run</small><strong>{activeRuns}</strong><span>项未归档</span></div>
            <div><small>证据完整 Run</small><strong>{completedRuns}</strong><span>项</span></div>
          </section>

          <div className="dashboard-grid">
            <section className="attention-panel" id="attention-section">
              <div className="section-heading">
                <div><h2>需要处理</h2><p>门禁、阻塞与需要人工判断的事项</p></div>
                <span className="count-badge">{attention.length}</span>
              </div>
              <div className="attention-list">
                {loading && !data ? <LoadingRows /> : attention.map((item, index) => (
                  <article className={`attention-item ${item.tone}`} key={`${item.eyebrow}-${index}`}>
                    <span className="tone-bar" />
                    <div className="attention-icon">
                      {item.tone === "danger" ? <Bell size={17} /> : item.tone === "warning" ? <Clock3 size={17} /> : <CheckCircle2 size={17} />}
                    </div>
                    <div className="attention-copy">
                      <small>{item.eyebrow}</small>
                      <strong>{item.title}</strong>
                      <span>{item.detail}</span>
                    </div>
                    <button onClick={()=>navigateTo(item.navId,item.targetId)}>{item.action}<ArrowRight size={15} /></button>
                  </article>
                ))}
              </div>
            </section>

            <aside className="system-panel">
              <div className="section-heading compact"><div><h2>系统状态</h2><p>2.0 基础设施</p></div></div>
              <div className="system-list">
                <div><Database size={17} /><span><strong>运行状态库</strong><small>{objectIndex?.initialized ? `已初始化 · ${objectIndex.objects.length} 个对象` : data?.capabilities.project_store?.initialized ? "已初始化" : "等待显式迁移"}</small></span><b className="neutral-dot" /></div>
                <div><Archive size={17} /><span><strong>研究正文</strong><small>Markdown canonical</small></span><b className="ok-dot" /></div>
                <div><Bot size={17} /><span><strong>Agent 会话</strong><small>现有 pi bridge 可用</small></span><b className="ok-dot" /></div>
              </div>
              <div className="system-note">
                <strong>迁移状态</strong>
                <p>{objectIndex?.initialized ? `Identity / Content 索引已接入：${objectIndex.objects.length} 个对象、${objectIndex.relations.length} 条关系；正文仍以 Markdown / kernel 为 authority。` : "SQLite 尚未初始化；页面只读使用 1.x 数据。"}</p>
              </div>
            </aside>
          </div>

          <section className="objects-section" id="objects-section">
            <div className="section-heading">
              <div><h2>研究对象</h2><p>按工作类型进入，不再强制以论文作为所有任务的左侧上下文</p></div>
            </div>
            <div className="object-grid">
              <ObjectTile icon={Library} label="论文库" value={data?.papers.length || 0} detail={`${data?.papers.filter((p) => p.has_mineru).length || 0} 篇已解析`} accent="teal" onClick={() => navigateTo("papers", "papers-section")} />
              <ObjectTile icon={BookOpen} label="研究分析" value={data?.comparisons.length || 0} detail="对比与 Findings" accent="violet" onClick={() => navigateTo("analysis", "objects-section")} />
              <ObjectTile icon={FileQuestion} label="Questions" value={data?.questions.length || 0} detail="跨论文与实验关联" accent="gold" onClick={() => navigateTo("questions", "questions-section")} />
              <ObjectTile icon={Beaker} label="Experiments" value={data?.dashboard.experiments.length || 0} detail={`${runs.length} 个 Run`} accent="red" onClick={() => navigateTo("experiments", "experiments-section")} />
              <ObjectTile icon={Workflow} label="自动化" value={0} detail="尚无自动化任务" accent="blue" muted onClick={() => navigateTo("automation", "objects-section")} />
            </div>
          </section>

          {objectIndex?.initialized && (
            <section className="list-section" id="v2-objects-section">
              <div className="section-heading compact"><div><h2>v2 对象索引</h2><p>SQLite 已迁移 identity 与关系；正文仍以 Markdown / kernel 为 authority</p></div><span className="count-badge">{objectIndex.objects.length} 对象 · {objectIndex.relations.length} 关系</span></div>
              <div className="experiment-list">
                {Object.entries(objectIndex.summary).sort(([left], [right]) => left.localeCompare(right)).map(([type, count]) => (
                  <div className="experiment-row" key={type}><span className="experiment-id">{type}</span><div><strong>{count}</strong><span>reference identity</span></div><span className="status-pill">indexed</span></div>
                ))}
              </div>
            </section>
          )}

          <section className="papers-section list-section" id="papers-section">
            <div className="section-heading compact"><div><h2>最近的论文</h2><p>已登记来源与解析状态</p></div><button className="text-button" onClick={() => setActiveNav("papers")}>进入论文库 <ArrowRight size={14} /></button></div>
            <div className="paper-grid">
              {(data?.papers || []).slice(0, 4).map((paper) => (
                <article className="paper-row" key={paper.title}>
                  <div className="paper-status"><BookOpen size={16} /></div>
                  <div><strong>{paper.title}</strong><span>{paper.date || "年份未登记"} · {paper.has_mineru ? "MinerU 已解析" : paper.has_pdf ? "PDF 已收录" : "文件待补充"}</span></div>
                  {paper.has_mineru && <CheckCircle2 size={15} />}
                </article>
              ))}
            </div>
          </section>

          <div className="lower-grid">
            <section className="list-section" id="experiments-section">
              <div className="section-heading compact"><div><h2>最近的实验</h2><p>按研究对象进入 Pipeline</p></div><button className="text-button" onClick={() => setActiveNav("experiments")}>查看全部 <ArrowRight size={14} /></button></div>
              <div className="experiment-list">
                {(data?.dashboard.experiments || []).slice(0, 4).map((experiment) => {
                  const runCount = runs.filter((run) => run.experiment_id === experiment.id).length;
                  return (
                    <div className="experiment-row" key={experiment.id}>
                      <span className="experiment-id">{experiment.id}</span>
                      <div><strong>{experiment.title}</strong><span>{runCount} 个 Run</span></div>
                      <span className={`status-pill ${experiment.status}`}>{statusLabel(experiment.status)}</span>
                      <button className="icon-button" title="打开实验" aria-label="打开实验"><ArrowRight size={16} /></button>
                    </div>
                  );
                })}
              </div>
            </section>

            <section className="list-section question-section" id="questions-section">
              <div className="section-heading compact"><div><h2>正在调查</h2><p>开放 Question</p></div><button className="text-button" onClick={() => setActiveNav("questions")}>查看全部 <ArrowRight size={14} /></button></div>
              <div className="question-list">
                {(data?.questions || []).slice(0, 3).map((question) => (
                  <div className="question-row" key={question.id}>
                    <span>{question.id}</span>
                    <strong>{question.title}</strong>
                    <small>{(question.papers?.length || 0) + (question.experiments?.length || 0)} 个关联对象</small>
                  </div>
                ))}
              </div>
            </section>
          </div>
          </>}
        </div>
      </main>
    </div>
  );
}

function ObjectTile({ icon: Icon, label, value, detail, accent, muted = false, onClick }: {
  icon: typeof Library;
  label: string;
  value: number;
  detail: string;
  accent: string;
  muted?: boolean;
  onClick: () => void;
}) {
  return (
    <button className={`object-tile ${accent} ${muted ? "muted" : ""}`} onClick={onClick}>
      <span className="object-icon"><Icon size={19} /></span>
      <span><small>{label}</small><strong>{value}</strong><em>{detail}</em></span>
      <ArrowRight size={16} />
    </button>
  );
}

function LoadingRows() {
  return <>{[1, 2, 3].map((row) => <div className="loading-row" key={row}><span /><div><i /><i /></div></div>)}</>;
}

function RecentActivityView({items,loading,onRefresh,onOpen}:{items:RecentActivityItem[];loading:boolean;onRefresh:()=>Promise<void>;onOpen:(navId:RecentActivityItem["navId"])=>void}) {
  const [filter,setFilter]=useState<"all"|RecentActivityItem["category"]>("all");
  const visible=filter==="all"?items:items.filter(item=>item.category===filter);
  const counts={research:items.filter(item=>item.category==="research").length,experiment:items.filter(item=>item.category==="experiment").length,system:items.filter(item=>item.category==="system").length};
  return <div className="activity-page"><section className="page-heading"><div><div className="eyebrow">Project timeline</div><h1>最近活动</h1><p>来自持久对象、Experiment / Run registry 和已有治理事件；不会因打开页面写入新事件。</p></div><button className="secondary-button" onClick={()=>void onRefresh()} disabled={loading}><RefreshCw size={15} className={loading?"spin":""}/>{loading?"刷新中…":"刷新"}</button></section><div className="activity-summary"><div><Activity size={17}/><span><small>全部记录</small><strong>{items.length}</strong></span></div><div><BookOpen size={17}/><span><small>研究对象</small><strong>{counts.research}</strong></span></div><div><FlaskConical size={17}/><span><small>实验与运行</small><strong>{counts.experiment}</strong></span></div></div><div className="paper-filters activity-filters"><button className={filter==="all"?"active":""} onClick={()=>setFilter("all")}>全部 <span>{items.length}</span></button><button className={filter==="research"?"active":""} onClick={()=>setFilter("research")}>研究对象 <span>{counts.research}</span></button><button className={filter==="experiment"?"active":""} onClick={()=>setFilter("experiment")}>Experiment / Run <span>{counts.experiment}</span></button><button className={filter==="system"?"active":""} onClick={()=>setFilter("system")}>系统事件 <span>{counts.system}</span></button></div><section className="activity-feed">{visible.length?visible.map(item=><button key={item.id} onClick={()=>onOpen(item.navId)}><span className={`activity-mark ${item.category}`}>{item.category==="experiment"?<FlaskConical size={15}/>:item.category==="system"?<Settings size={15}/>:<BookOpen size={15}/>}</span><span className="activity-copy"><small>{item.kind}</small><strong>{item.title}</strong><em>{item.detail}</em></span><time>{formatActivityTime(item.occurredAt)}</time><ArrowRight size={15}/></button>):<div className="activity-empty"><Clock3 size={24}/><strong>还没有可显示的持久活动</strong><span>创建或更新研究对象后会出现在这里；单纯浏览页面不会制造日志。</span></div>}</section></div>;
}

function formatActivityTime(value:string){const date=new Date(value);return Number.isNaN(date.getTime())?value:date.toLocaleString("zh-CN",{month:"short",day:"numeric",hour:"2-digit",minute:"2-digit"})}
