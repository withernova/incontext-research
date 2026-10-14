import {
  ArrowLeft,
  ArrowUpRight,
  BookOpen,
  CheckCircle2,
  ChevronDown,
  ClipboardCopy,
  CircleAlert,
  FileCheck2,
  FileText,
  Filter,
  FolderArchive,
  Image,
  Library,
  LoaderCircle,
  MessageCircle,
  PanelLeftClose,
  PanelLeftOpen,
  Pencil,
  Plus,
  Save,
  Search,
  ShieldQuestion,
  Tags,
  Upload,
  X,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { ApiError, ingestPaperCandidate, initializeV2Store, loadCandidateRegistry, loadPaperBundle, loadV2Jobs, loadZoteroCollections, loadZoteroItems, previewSevenQuestionImport, retryV2Job, runLocalPaperWorker, savePaperCandidate, searchArxivPapers, searchPapers, stagePaperAcquisition, stageZoteroCandidate, updateV2Paper } from "./api";
import type { StoredJob, StoredPaperCandidate, V2ObjectIndex } from "./api";
import { ZoteroBrowser } from "./ZoteroBrowser";
import type { Paper, PaperAnnotation, PaperBundle, PaperCandidate, PaperSearchResult, WorkspaceData, ZoteroCollection, ZoteroItem } from "./types";
import { V2IndexNote } from "./V2IndexNote";
import {candidateSourceLabel,filterCandidates,type CandidateStatusFilter} from "./paperCandidateModel";
import { AiDiscussionPanel } from "./AiDiscussionPanel";

type PaperFilter = "all" | "parsed" | "pdf" | "missing";

const sevenLabels = [
  "① 解决了什么问题？",
  "② 方法具体怎么做？",
  "③ 真正的创新点是什么？",
  "④ 实验说明了什么？",
  "⑤ 依赖哪些前提，边界在哪里？",
  "⑥ 作为审稿人，最关键的质疑是什么？",
  "⑦ 对当前项目有什么启发？",
];

function paperStatus(paper: Paper): { label: string; tone: string } {
  if (paper.has_mineru) return { label: "已解析", tone: "parsed" };
  if (paper.has_pdf) return { label: "待解析", tone: "pdf" };
  return { label: "缺少 PDF", tone: "missing" };
}

function sevenProgress(bundle: PaperBundle | null): number {
  if (!bundle) return 0;
  return sevenLabels.filter((label) => {
    const value = bundle.seven[label];
    return typeof value === "string" ? value.trim().length > 0 : Boolean(value);
  }).length;
}

export function PaperLibrary({ data, objectIndex, onBack, onChanged }: { data: WorkspaceData; objectIndex: V2ObjectIndex | null; onBack: () => void; onChanged?: () => Promise<void> }) {
  const [filter, setFilter] = useState<PaperFilter>("all");
  const [query, setQuery] = useState("");
  const [selectedCitekey, setSelectedCitekey] = useState(data.papers[0]?.citekey || "");
  const [bundle, setBundle] = useState<PaperBundle | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState("");
  const [finderOpen, setFinderOpen] = useState(false);
  const [finderQuery, setFinderQuery] = useState("");
  const [finderLoading, setFinderLoading] = useState(false);
  const [finderResult, setFinderResult] = useState<PaperSearchResult | null>(null);
  const [finderSource,setFinderSource]=useState<"online"|"arxiv"|"zotero">("online");const [zoteroCollections,setZoteroCollections]=useState<ZoteroCollection[]>([]);const [zoteroCollection,setZoteroCollection]=useState(0);const [zoteroItems,setZoteroItems]=useState<ZoteroItem[]>([]);const [zoteroQuery,setZoteroQuery]=useState("");
  const [v2Initialized, setV2Initialized] = useState(Boolean(data.capabilities.project_store?.initialized));
  const [zoteroRefresh, setZoteroRefresh] = useState(0);
  const [initializing, setInitializing] = useState(false);
  const [candidateList,setCandidateList]=useState<StoredPaperCandidate[]>([]);
  const [finderMode,setFinderMode]=useState<"discovery"|"catalog">("discovery");
  const [candidateQuery,setCandidateQuery]=useState("");const [candidateStatusFilter,setCandidateStatusFilter]=useState<CandidateStatusFilter>("all");const [highlightCandidate,setHighlightCandidate]=useState("");
  const [candidateError, setCandidateError] = useState("");
  const [queueMessage,setQueueMessage]=useState("");
  const [jobs, setJobs] = useState<StoredJob[]>([]);
  const [sevenOpen, setSevenOpen] = useState(true);
  const [assetsOpen, setAssetsOpen] = useState(false);
  const [catalogCollapsed, setCatalogCollapsed] = useState(false);
  const [canonicalSaving, setCanonicalSaving] = useState(false);
  const [discussion,setDiscussion]=useState<{type:"paper"|"paper_candidate";id:string;label:string}|null>(null);
  const savedCandidates=useMemo(()=>new Map(candidateList.map((item)=>[item.source_url||item.id,item])),[candidateList]);
  const incompleteCandidateCount=candidateList.filter((item)=>item.verification_status!=="ingested").length;
  const visibleCandidates=useMemo(()=>filterCandidates(candidateList,jobs,candidateQuery,candidateStatusFilter),[candidateList,jobs,candidateQuery,candidateStatusFilter]);
  const upsertCandidate=(candidate:StoredPaperCandidate)=>setCandidateList((current)=>[candidate,...current.filter((item)=>item.id!==candidate.id)]);

  const filtered = useMemo(() => {
    const needle = query.trim().toLocaleLowerCase();
    return data.papers.filter((paper) => {
      if (needle && !`${paper.title} ${paper.citekey} ${paper.date || ""}`.toLocaleLowerCase().includes(needle)) return false;
      if (filter === "parsed") return paper.has_mineru;
      if (filter === "pdf") return paper.has_pdf && !paper.has_mineru;
      if (filter === "missing") return !paper.has_pdf;
      return true;
    });
  }, [data.papers, filter, query]);

  const selected = filtered.find((paper) => paper.citekey === selectedCitekey) || filtered[0];

  const reloadBundle = async () => {
    if (!selected?.citekey) return null;
    const result = await loadPaperBundle(data.project.path, selected.citekey);
    setBundle(result);
    return result;
  };

  const saveCanonical = async (fields: { seven?: PaperBundle["seven"]; annotations?: PaperAnnotation[] }) => {
    if (!selected || !bundle || canonicalSaving) return false;
    setCanonicalSaving(true);
    setDetailError("");
    try {
      const result = await updateV2Paper(data.project.path, selected.citekey, bundle._canonical_rev, fields);
      setBundle(result.paper);
      await onChanged?.();
      return true;
    } catch (reason) {
      if (reason instanceof ApiError && reason.reason === "content_hash_conflict") {
        setDetailError("内容已被其他写入修改，请刷新后重试");
        await reloadBundle().catch(() => undefined);
      } else {
        setDetailError(reason instanceof Error ? reason.message : String(reason));
      }
      return false;
    } finally {
      setCanonicalSaving(false);
    }
  };

  useEffect(() => {
    if (!selected?.citekey) {
      setBundle(null);
      return;
    }
    let cancelled = false;
    setSevenOpen(true);
    setAssetsOpen(false);
    setDetailLoading(true);
    setDetailError("");
    loadPaperBundle(data.project.path, selected.citekey)
      .then((result) => { if (!cancelled) setBundle(result); })
      .catch((reason) => { if (!cancelled) setDetailError(reason instanceof Error ? reason.message : String(reason)); })
      .finally(() => { if (!cancelled) setDetailLoading(false); });
    return () => { cancelled = true; };
  }, [data.project.path, selected?.citekey]);

  useEffect(() => {
    if (!finderOpen || !v2Initialized) return;
    let cancelled=false;const refresh=()=>Promise.all([loadCandidateRegistry(data.project.path),loadV2Jobs(data.project.path)]).then(([registry,jobResult])=>{if(!cancelled){setCandidateList(registry.candidates);setJobs(jobResult.jobs)}}).catch((reason)=>{if(!cancelled)setCandidateError(reason instanceof Error?reason.message:String(reason))});
    void refresh();const timer=window.setInterval(()=>void refresh(),2000);return()=>{cancelled=true;window.clearInterval(timer)};
  }, [data.project.path, finderOpen, v2Initialized]);
  useEffect(()=>{if(!v2Initialized)return;loadCandidateRegistry(data.project.path).then((result)=>setCandidateList(result.candidates)).catch(()=>undefined)},[data.project.path,v2Initialized]);
  useEffect(()=>{if(!finderOpen||finderSource!=="zotero")return;let cancelled=false;setFinderLoading(true);setZoteroItems([]);setCandidateError("");Promise.all([loadZoteroCollections(data.project.path),loadZoteroItems(data.project.path,zoteroCollection)]).then(([collections,items])=>{if(cancelled)return;if(!collections.ok||!items.ok)throw new Error(collections.error||items.error||"Zotero 库读取失败");setZoteroCollections(collections.collections||[]);setZoteroItems(items.items||[])}).catch((reason)=>{if(!cancelled)setCandidateError(reason instanceof Error?reason.message:String(reason))}).finally(()=>{if(!cancelled)setFinderLoading(false)});return()=>{cancelled=true}},[data.project.path,finderOpen,finderSource,zoteroCollection,zoteroRefresh]);

  const enableCandidates = async () => {
    setInitializing(true); setCandidateError("");
    try { await initializeV2Store(data.project.path); setV2Initialized(true); }
    catch (reason) { setCandidateError(reason instanceof Error ? reason.message : String(reason)); }
    finally { setInitializing(false); }
  };

  const saveCandidate = async (candidate: PaperCandidate) => {
    setCandidateError("");
    try {
      const saved = await savePaperCandidate(data.project.path, candidate, `由用户在论文检索中登记；query=${finderResult?.query || ""}`);
      upsertCandidate(saved.candidate);setHighlightCandidate(saved.candidate.id);setCandidateQuery("");setCandidateStatusFilter("all");setFinderMode("catalog");setQueueMessage("候选已登记，可在此继续准备与纳入。");
    } catch (reason) { setCandidateError(reason instanceof Error ? reason.message : String(reason)); }
  };

  const stageCandidate = async (stored:StoredPaperCandidate) => {
    setCandidateError("");
    try {
      const pipeline = await stagePaperAcquisition(data.project.path, stored) as { candidate?: StoredPaperCandidate; download_job?: StoredJob; mineru_job?: StoredJob };
      if (pipeline.candidate) upsertCandidate(pipeline.candidate);
      setJobs((current) => [...current.filter((job) => job.target_object_id !== stored.id), ...[pipeline.download_job, pipeline.mineru_job].filter(Boolean) as StoredJob[]]);
      setQueueMessage("两项任务已排队，Worker 尚未启动。请点击“在本机开始准备”。");
    } catch (reason) { setCandidateError(reason instanceof Error ? reason.message : String(reason)); }
  };

  const ingestCandidate = async (stored:StoredPaperCandidate) => {
    const expected = `INGEST ${stored.citekey || "paper"}`;
    setCandidateError("");
    try {
      const result = await ingestPaperCandidate(data.project.path, stored, expected);
      upsertCandidate(result.candidate);await onChanged?.();
    } catch (reason) { setCandidateError(reason instanceof Error ? reason.message : String(reason)); }
  };

  const findCandidates = async () => {
    const value = finderQuery.trim();
    if (!value) return;
    setFinderLoading(true);
    setFinderResult(null);
    try {
      setFinderResult(finderSource==="arxiv"?await searchArxivPapers(data.project.path,value):await searchPapers(data.project.path, value));
    } catch (reason) {
      setFinderResult({ source: "openalex", query: value, hits: [], error: reason instanceof Error ? reason.message : String(reason) });
    } finally {
      setFinderLoading(false);
    }
  };
  const stageZotero=async(item:ZoteroItem):Promise<boolean>=>{if(!v2Initialized)return false;setCandidateError("");try{const result=await stageZoteroCandidate(data.project.path,item.id);upsertCandidate(result.candidate);setHighlightCandidate(result.candidate.id);setCandidateQuery("");setCandidateStatusFilter("all");return true;}catch(reason){setCandidateError(reason instanceof Error?reason.message:String(reason));return false;}};
  const runWorker=async(candidate:StoredPaperCandidate)=>{setCandidateError("");try{const result=await runLocalPaperWorker(data.project.path,candidate.id,2);setQueueMessage(result.already_running?"本项目 Worker 已在处理中。":"本地 Worker 已启动，状态将每 2 秒刷新。");const latest=await loadV2Jobs(data.project.path);setJobs(latest.jobs)}catch(reason){setCandidateError(reason instanceof Error?reason.message:String(reason))}};
  const retryJob=async(job:StoredJob,candidate:StoredPaperCandidate)=>{setCandidateError("");try{await retryV2Job(data.project.path,job,"用户从候选任务界面重试");await runWorker(candidate)}catch(error){setCandidateError(error instanceof Error?error.message:String(error))}};

  const counts = {
    all: data.papers.length,
    parsed: data.papers.filter((paper) => paper.has_mineru).length,
    pdf: data.papers.filter((paper) => paper.has_pdf && !paper.has_mineru).length,
    missing: data.papers.filter((paper) => !paper.has_pdf).length,
  };

  return (
    <div className="paper-library-page">
      <div className="paper-page-heading">
        <div>
          <button className="back-button" onClick={onBack}><ArrowLeft size={15} />研究总览</button>
          <div className="eyebrow">Evidence Library</div>
          <h1>论文库</h1>
          <p>先区分来源与核验状态，再进入七问、对比或正式 Claim。</p>
        </div>
        <div className="paper-heading-actions"><button className="primary-button" onClick={() => {setFinderMode("discovery");setFinderOpen(true)}}><Search size={16} />检索新论文</button>{incompleteCandidateCount>0&&<button className="secondary-button" onClick={()=>{setFinderMode("catalog");setFinderOpen(true)}}>候选任务 ({incompleteCandidateCount})</button>}</div>
      </div>

      <div className="paper-summary-strip">
        <div><Library size={17} /><span><small>全部论文</small><strong>{counts.all}</strong></span></div>
        <div><FileCheck2 size={17} /><span><small>MinerU 已解析</small><strong>{counts.parsed}</strong></span></div>
        <div><FileText size={17} /><span><small>PDF 待解析</small><strong>{counts.pdf}</strong></span></div>
        <div><CircleAlert size={17} /><span><small>来源待补充</small><strong>{counts.missing}</strong></span></div>
      </div>

      <V2IndexNote index={objectIndex} type="paper" legacyCount={data.papers.length} />

      <div className={`paper-workspace ${catalogCollapsed ? "selector-collapsed" : ""}`}>
        <section className={`paper-catalog-panel ${catalogCollapsed ? "collapsed" : ""}`}>
          {catalogCollapsed ? <button className="selector-restore" aria-label="展开论文选择" title="展开论文选择" onClick={() => setCatalogCollapsed(false)}><PanelLeftOpen size={17} /><span>论文</span></button> : <>
          <div className="catalog-tools">
            <div className="catalog-search"><Search size={15} /><input aria-label="搜索论文库" placeholder="标题、citekey 或年份" value={query} onChange={(event) => setQuery(event.target.value)} /></div>
            <Filter size={15} />
            <button className="selector-collapse-button" aria-label="收起论文选择" title="收起论文选择" onClick={() => setCatalogCollapsed(true)}><PanelLeftClose size={16} /></button>
          </div>
          <div className="paper-filters" role="tablist" aria-label="论文状态筛选">
            {([
              ["all", "全部"],
              ["parsed", "已解析"],
              ["pdf", "待解析"],
              ["missing", "待补充"],
            ] as Array<[PaperFilter, string]>).map(([id, label]) => (
              <button key={id} className={filter === id ? "active" : ""} onClick={() => setFilter(id)}>{label}<span>{counts[id]}</span></button>
            ))}
          </div>
          <div className="paper-catalog-list">
            {filtered.map((paper) => {
              const status = paperStatus(paper);
              return (
                <button className={`catalog-paper ${selected?.citekey === paper.citekey ? "selected" : ""}`} key={paper.citekey} onClick={() => setSelectedCitekey(paper.citekey)}>
                  <span className={`paper-file-icon ${status.tone}`}><FileText size={16} /></span>
                  <span className="catalog-paper-copy">
                    <strong>{paper.title}</strong>
                    <small>{paper.date || "年份未登记"} · {paper.citekey}</small>
                  </span>
                  <span className={`paper-status-pill ${status.tone}`}>{status.label}</span>
                </button>
              );
            })}
            {!filtered.length && <div className="catalog-empty">当前筛选下没有论文</div>}
          </div>
          </>}
        </section>

        <section className="paper-detail-panel">
          {detailLoading && !bundle ? <div className="paper-detail-loading"><LoaderCircle className="spin" size={20} />读取论文信息</div> : selected ? (
            <>
              <div className="paper-detail-head">
                <div className={`large-paper-icon ${paperStatus(selected).tone}`}><BookOpen size={22} /></div>
                <div>
                  <div className="paper-detail-meta"><span>{selected.date || "年份未登记"}</span><span>{paperStatus(selected).label}</span></div>
                  <h2>{selected.title}</h2>
                  <code>{selected.citekey}</code>
                </div>
                <div className="paper-detail-actions"><button className="secondary-button" onClick={()=>setDiscussion({type:"paper",id:selected.citekey,label:selected.title})}><MessageCircle size={15}/>与 AI 讨论</button><a className="secondary-button" href={`/file/${encodeURIComponent(data.project.path)}/papers/${encodeURIComponent(selected.file || "")}`} target="_blank" rel="noreferrer" aria-disabled={!selected.has_pdf} onClick={(event) => { if (!selected.has_pdf) event.preventDefault(); }}><FileText size={15} />查看 PDF</a></div>
              </div>

              {detailError && <div className="detail-error"><CircleAlert size={16} />{detailError}</div>}

              <div className="paper-facts">
                <div><small>本地文件</small><strong>{selected.has_pdf ? "已核验存在" : "尚未获取"}</strong></div>
                <div><small>解析产物</small><strong>{selected.has_mineru ? "Markdown + Images" : "尚未完成"}</strong></div>
                <div><small>图片</small><strong>{selected.images_count || 0} 张</strong></div>
                <div><small>Claims</small><strong>{bundle?.claims.length || 0} 条</strong></div>
              </div>

              <div className="paper-detail-disclosures">
                <section className={`paper-disclosure ${sevenOpen ? "open" : ""}`}>
                  <button className="paper-disclosure-toggle" aria-expanded={sevenOpen} onClick={() => setSevenOpen((open) => !open)}>
                    <span className="disclosure-icon"><BookOpen size={16} /></span><span><strong>七问细读</strong><small>正文保存在 canonical 论文笔记</small></span><b>{sevenProgress(bundle)} / 7</b><ChevronDown size={16} />
                  </button>
                  {sevenOpen && <div className="paper-disclosure-body">
                    <div className="seven-progress-bar"><span style={{ width: `${(sevenProgress(bundle) / 7) * 100}%` }} /></div>
                    {bundle && <SevenEditor bundle={bundle} saving={canonicalSaving} projectPath={data.project.path} citekey={selected.citekey} onSave={(seven) => saveCanonical({ seven, annotations: bundle.annotations })} />}
                  </div>}
                </section>

                <section className={`paper-disclosure ${assetsOpen ? "open" : ""}`}>
                  <button className="paper-disclosure-toggle" aria-expanded={assetsOpen} onClick={() => setAssetsOpen((open) => !open)}>
                    <span className="disclosure-icon"><FolderArchive size={16} /></span><span><strong>证据产物</strong><small>PDF、解析正文、图片与标注</small></span><b>{[selected.has_pdf, Boolean(bundle?.mineru_md), selected.has_images].filter(Boolean).length} / 3</b><ChevronDown size={16} />
                  </button>
                  {assetsOpen && <div className="paper-disclosure-body">
                    <div className="asset-row"><FileText size={17} /><span><strong>论文 PDF</strong><small>{selected.file || "文件待补充"}</small></span>{selected.has_pdf ? <CheckCircle2 size={15} /> : <CircleAlert size={15} />}</div>
                    <div className="asset-row"><FileCheck2 size={17} /><span><strong>MinerU Markdown</strong><small>{bundle?.mineru_md ? "解析正文可用" : "尚未生成"}</small></span>{bundle?.mineru_md ? <CheckCircle2 size={15} /> : <CircleAlert size={15} />}</div>
                    <div className="asset-row"><Image size={17} /><span><strong>图像资产</strong><small>{selected.images_count || 0} 张已登记</small></span>{selected.has_images ? <CheckCircle2 size={15} /> : <CircleAlert size={15} />}</div>
                    <div className="asset-row"><Tags size={17} /><span><strong>图片标注</strong><small>{bundle?.annotations.length || 0} 条</small></span><span className="asset-count">{bundle?.annotations.length || 0}</span></div>
                    {bundle && <AnnotationEditor citekey={selected.citekey} annotations={bundle.annotations} saving={canonicalSaving} onSave={(annotations) => saveCanonical({ annotations })} />}
                    <div className="trust-note"><ShieldQuestion size={18} /><div><strong>证据边界</strong><p>“已解析”只表示文件可读，不等于论文结论已被项目验证。</p></div></div>
                  </div>}
                </section>
              </div>
            </>
          ) : <div className="paper-detail-loading">选择一篇论文查看详情</div>}
        </section>
      </div>

      {finderOpen && (
        <div className="finder-overlay" role="dialog" aria-modal="true" aria-label="检索新论文">
          <div className="finder-dialog">
            <div className="finder-head"><div><div className="eyebrow">Paper Candidate Sources</div><h2>检索 / 添加论文</h2><p>在线与 Zotero 条目都先进入候选预览，不会静默写 canonical。</p></div><button className="icon-button" onClick={() => setFinderOpen(false)} aria-label="关闭"><X size={18} /></button></div>
            <div className="paper-filters candidate-mode-filters"><button className={finderMode==="discovery"?"active":""} onClick={()=>setFinderMode("discovery")}>检索发现</button><button className={finderMode==="catalog"?"active":""} onClick={()=>setFinderMode("catalog")}>候选与本地任务 <span>{incompleteCandidateCount}</span></button></div>
            {finderMode==="discovery"&&<><div className="finder-source-tabs"><button className={finderSource==="online"?"active":""} onClick={()=>{setFinderSource("online");setFinderResult(null)}}>综合 / OpenAlex</button><button className={finderSource==="arxiv"?"active":""} onClick={()=>{setFinderSource("arxiv");setFinderResult(null)}}>arXiv</button><button className={finderSource==="zotero"?"active":""} onClick={()=>{setFinderSource("zotero");setFinderResult(null)}}>Zotero 本地库</button></div>
            {finderSource!=="zotero"&&<form className="finder-form" onSubmit={(event) => { event.preventDefault(); void findCandidates(); }}>
              <Search size={17} /><input autoFocus aria-label="候选论文检索词" placeholder={finderSource==="arxiv"?"arXiv 标题、作者或主题":"方法、任务、数据集或论文标题"} value={finderQuery} onChange={(event) => setFinderQuery(event.target.value)} /><button type="submit" disabled={finderLoading || !finderQuery.trim()}>{finderLoading ? <LoaderCircle className="spin" size={16} /> : "检索"}</button>
            </form>}
            {finderSource==="zotero"&&<div className="zotero-finder-controls"><label>文献分类（含子分类）<select value={zoteroCollection} onChange={(e)=>setZoteroCollection(Number(e.target.value))}><option value={0}>全部文献</option>{zoteroCollections.map((collection)=><option key={collection.id} value={collection.id}>{collection.name} ({collection.count})</option>)}</select></label><div className="catalog-search"><Search size={15}/><input aria-label="筛选 Zotero 文献" placeholder="标题、作者、年份或 DOI" value={zoteroQuery} onChange={(e)=>setZoteroQuery(e.target.value)}/></div><button disabled={finderLoading} onClick={()=>setZoteroRefresh(value=>value+1)}>刷新本地库</button></div>}
            <div className="candidate-legend"><span /> 未核验候选 · {finderSource==="arxiv"?"检索会按既有语义记录 search_log，但不会下载或纳入论文":"登记候选不会下载 PDF，也不会进入正式证据库"}</div>
            <div className="candidate-store-state"><div><strong>{v2Initialized ? "候选登记已启用" : "候选登记尚未启用"}</strong><span>{v2Initialized ? "候选将保存到项目 v2 状态库" : "点击启用即初始化候选状态库，不改研究正文"}</span></div>{!v2Initialized && <button onClick={() => void enableCandidates()} disabled={initializing}>{initializing ? "初始化中" : "启用候选登记"}</button>}</div>
            </>}
            {candidateError && <div className="detail-error"><CircleAlert size={16} />{candidateError}</div>}
            {queueMessage&&<div className="candidate-notice">{queueMessage}</div>}
            <div className="candidate-list">
              {finderMode==="discovery"&&finderSource!=="zotero"&&<>{finderResult?.warning&&<div className="candidate-warning"><CircleAlert size={16}/>{finderResult.warning}</div>}{finderResult?.error && <div className="detail-error"><CircleAlert size={16} />{finderResult.error}</div>}{finderResult?.hits.map((candidate) => { const stored = savedCandidates.get(candidate.url);return <CandidateCard key={`${candidate.citekey}-${candidate.url}`} candidate={candidate} stored={stored} jobs={[]} canSave={v2Initialized} staged={false} discoveryOnly onViewTasks={()=>{setHighlightCandidate(stored?.id||"");setFinderMode("catalog")}} onSave={() => void saveCandidate(candidate)} onStage={()=>{}} onIngest={()=>{}} />; })}{finderResult && !finderResult.error && !finderResult.hits.length && <div className="catalog-empty">没有检索到候选论文</div>}{!finderResult && !finderLoading && <div className="finder-placeholder"><Search size={24} /><strong>从一个具体研究问题开始</strong><span>候选卡片会明确标出开放获取与引用信息。</span></div>}</>}
              {finderMode==="discovery"&&finderSource==="zotero"&&<ZoteroBrowser key={data.project.path} items={zoteroItems.filter(item=>`${item.title} ${item.authors.join(" ")} ${item.date||""} ${item.doi||""}`.toLowerCase().includes(zoteroQuery.trim().toLowerCase()))} loading={finderLoading} enabled={v2Initialized} saved={savedCandidates} onAdd={stageZotero} onView={id=>{setHighlightCandidate(id);setFinderMode("catalog")}}/>}
              {finderMode==="catalog"&&<div className="candidate-task-catalog"><div className="catalog-tools candidate-tools"><div className="catalog-search"><Search size={14}/><input autoFocus placeholder="按标题、citekey、DOI 或来源过滤" value={candidateQuery} onChange={(event)=>setCandidateQuery(event.target.value)}/></div><select value={candidateStatusFilter} onChange={(event)=>setCandidateStatusFilter(event.target.value as CandidateStatusFilter)}><option value="all">全部状态</option><option value="active">待准备 / 处理中</option><option value="failed">失败</option><option value="ready">可核验纳入</option><option value="ingested">已纳入</option></select></div><div className="candidate-canonical-hint">准备和解析只写 staging；点击“纳入正式论文库”才会执行 canonical 写入。</div>{visibleCandidates.map((stored)=>{const ownJobs=jobs.filter((job)=>job.target_object_id===stored.id);const presentation:PaperCandidate={citekey:stored.citekey||"",title:stored.title||stored.citekey||stored.id,authors:stored.authors||[],year:stored.year||"",doi:stored.doi,url:stored.source_url||"#",oa_url:stored.oa_url||null,is_oa:Boolean(stored.oa_url),source:stored.source};return <div key={stored.id} data-highlighted={highlightCandidate===stored.id||undefined}><CandidateCard candidate={presentation} stored={stored} jobs={ownJobs} canSave={false} staged={ownJobs.length>0} localSource={stored.source==="zotero-local"} arxivSource={stored.source?.startsWith("arxiv")} sourceLabel={candidateSourceLabel(stored)} onSave={()=>{}} onDiscuss={()=>setDiscussion({type:"paper_candidate",id:stored.id,label:stored.title||stored.citekey||stored.id})} onStage={()=>void stageCandidate(stored)} onIngest={()=>void ingestCandidate(stored)} onRunWorker={()=>void runWorker(stored)} onRetry={(job)=>void retryJob(job,stored)}/></div>})}{!visibleCandidates.length&&<div className="catalog-empty">没有符合筛选条件的持久候选；更换检索词不会删除这里的任务。</div>}</div>}
            </div>
          </div>
        </div>
      )}
      {discussion&&<AiDiscussionPanel targetType={discussion.type} targetId={discussion.id} targetLabel={discussion.label} projectPath={data.project.path} onClose={()=>setDiscussion(null)}/>}
    </div>
  );
}

function CandidateCard({ candidate, stored, jobs, canSave, localSource=false, arxivSource=false,discoveryOnly=false,sourceLabel,onSave,onViewTasks=()=>{},onDiscuss=()=>{}, onStage, onIngest,onRunWorker=()=>{},onRetry=()=>{} }: { candidate: PaperCandidate; stored?: StoredPaperCandidate; jobs: StoredJob[]; canSave: boolean; staged: boolean; localSource?:boolean;arxivSource?:boolean;discoveryOnly?:boolean;sourceLabel?:string; onSave: () => void;onViewTasks?:()=>void;onDiscuss?:()=>void; onStage: () => void; onIngest: () => void;onRunWorker?:()=>void;onRetry?:(job:StoredJob)=>void }) {
  const acquisition = jobs.find((job) => ["paper_download", "zotero_copy"].includes(job.kind));
  const mineru = jobs.find((job) => job.kind === "mineru");
  const ready = acquisition?.status === "succeeded" && mineru?.status === "succeeded";
  const failed=jobs.filter((job)=>job.status==="failed"),queued=jobs.some((job)=>job.status==="queued"),running=jobs.some((job)=>job.status==="running");
  const stateLabel=(job:StoredJob|undefined,mineruJob=false)=>!job?"未排队":mineruJob&&acquisition?.status!=="succeeded"&&job.status==="queued"?"等待 PDF 准备":({queued:"等待本地 Worker",running:"处理中",succeeded:"已完成",failed:"失败",cancelled:"已取消"}[job.status]||job.status);
  return (
    <article className="candidate-card">
      <span className="candidate-flag">{sourceLabel||candidate.source||"未核验"}</span>
      <div className="candidate-copy">
        <h3>{candidate.title}</h3>
        <p>{candidate.authors.slice(0, 4).join("、") || "作者未登记"}{candidate.authors.length > 4 ? " 等" : ""}</p>
        <div><span>{candidate.year || "年份未知"}</span>{candidate.doi && <span>DOI {candidate.doi}</span>}<span>被引 {candidate.cited_by_count || 0}</span></div>
      </div>
      <div className="candidate-actions">
        <span className={candidate.is_oa ? "oa" : "closed"}>{localSource?"Zotero 本地":candidate.is_oa ? "开放获取" : "来源受限"}</span>
        <a href={candidate.url} target="_blank" rel="noreferrer">查看来源 <ArrowUpRight size={14} /></a>
        {!discoveryOnly&&candidate.url&&candidate.url!=="#"&&<small className="candidate-source-meta" title={candidate.url}>{candidate.url}</small>}
        {!stored ? <button onClick={onSave} disabled={!canSave}>登记候选</button>:discoveryOnly?<button onClick={onViewTasks}>已登记，在候选任务查看</button>:stored.verification_status === "ingested" ? <button disabled>已纳入正式论文</button> : !jobs.length?<button onClick={onStage} disabled={!stored.oa_url&&stored.source!=="zotero-local"}>{localSource?"准备本地 PDF":arxivSource?"准备 arXiv PDF + MinerU":stored.oa_url ? "准备 PDF + MinerU" : "无开放 PDF"}</button>:ready?<><small className="canonical-write-note">下一步会写入 canonical 论文库</small><button className="ingest-action" onClick={onIngest}>纳入正式论文库</button></>:queued?<button onClick={onRunWorker}>在本机开始准备</button>:running?<button disabled>Worker 处理中…</button>:null}
        {!discoveryOnly&&stored&&<button className="secondary-button" onClick={onDiscuss}><MessageCircle size={13}/>与 AI 讨论</button>}
      </div>
      {jobs.length>0&&<div className="candidate-task-steps"><div><strong>{localSource?"本地 PDF":"PDF"}</strong><span>{stateLabel(acquisition)}{acquisition?.status==="running"&&` · attempt ${acquisition.attempt||1}`}</span></div><div><strong>MinerU</strong><span>{stateLabel(mineru,true)}{mineru?.status==="running"&&` · attempt ${mineru.attempt||1}`}</span></div>{failed.map((job)=><div className="candidate-task-error" key={job.id}><span>{job.error_class||"任务失败"}：{String(job.error_message||"无错误详情").slice(0,300)}</span><button onClick={()=>onRetry(job)}>重试并启动</button></div>)}</div>}
    </article>
  );
}

function SevenEditor({ bundle, saving, projectPath, citekey, onSave }: { bundle: PaperBundle; saving: boolean; projectPath: string; citekey: string; onSave: (seven: PaperBundle["seven"]) => Promise<boolean> }) {
  const [mode,setMode]=useState<"read"|"edit"|"import">("read");
  const [draft,setDraft]=useState<Record<string,string>>(() => Object.fromEntries(sevenLabels.map((label) => [label,String(bundle.seven[label] || "")])));
  const [expanded,setExpanded]=useState<Set<number>>(new Set());
  const [importText,setImportText]=useState("");
  const [importAnswers,setImportAnswers]=useState<Record<string,string>|null>(null);
  const [importMeta,setImportMeta]=useState<{parsed_count:number;missing:string[];warnings:string[]}|null>(null);
  const [importError,setImportError]=useState("");
  const [parsing,setParsing]=useState(false);
  const [strategy,setStrategy]=useState<"fill"|"overwrite">("fill");
  const [importApplied,setImportApplied]=useState(false);
  const template=`---
format: survey-gpt-response
version: 1
target_type: paper
target_id: ${citekey}
target_address: paper:${citekey}
---
${sevenLabels.map((label) => `### ${label}\n<回答；无可靠证据则写 <待确认>>`).join("\n\n")}`;

  const beginEdit=(next?:Record<string,string>) => { setDraft(next || Object.fromEntries(sevenLabels.map((label) => [label,String(bundle.seven[label] || "")]))); setMode("edit"); };
  const save=async () => { if (await onSave({ ...bundle.seven,...draft })) { setImportApplied(false); setMode("read"); } };
  const parseImport=async () => {
    setParsing(true); setImportError("");
    try { const result=await previewSevenQuestionImport(projectPath,citekey,importText); setImportAnswers(result.answers); setImportMeta({parsed_count:result.parsed_count,missing:result.missing,warnings:result.warnings}); }
    catch(reason) { setImportError(reason instanceof Error ? reason.message : String(reason)); }
    finally { setParsing(false); }
  };
  const applyImport=() => {
    if (!importAnswers) return;
    const next={...draft};
    sevenLabels.forEach((label) => { const imported=String(importAnswers[label] || "").trim(); if (imported && (strategy==="overwrite" || !next[label].trim())) next[label]=imported; });
    setImportApplied(true); beginEdit(next);
  };

  if (mode==="edit") return <div className="paper-canonical-editor">{importApplied && <div className="seven-unsaved-note">AI 解析结果仅已应用到本地草稿，尚未保存到 canonical Markdown。</div>}{sevenLabels.map((label) => <label key={label}><strong>{label}</strong><textarea value={draft[label]} onChange={(event) => setDraft({ ...draft,[label]:event.target.value })}/></label>)}<div><button className="secondary-button" onClick={() => { setDraft(Object.fromEntries(sevenLabels.map((label) => [label,String(bundle.seven[label] || "")]))); setImportApplied(false); setMode("read"); }} disabled={saving}>取消</button><button className="primary-button" onClick={() => void save()} disabled={saving}><Save size={14}/>{saving ? "保存中…" : "保存七问"}</button></div></div>;

  if (mode==="import") return <div className="seven-import-panel"><div className="seven-import-head"><div><strong>从 AI 输出导入</strong><small>这里只解析预览，不调用外部 AI，也不写 canonical。</small></div><button onClick={() => setMode("read")}><X size={14}/></button></div><textarea className="seven-import-source" value={importText} onChange={(event) => setImportText(event.target.value)} placeholder="粘贴带 YAML 头和七问三级标题的 Markdown"/><div className="seven-import-actions"><button className="secondary-button" onClick={() => void navigator.clipboard.writeText(template)}><ClipboardCopy size={13}/>复制 AI 输出模板</button><button className="primary-button" onClick={() => void parseImport()} disabled={parsing || !importText.trim()}>{parsing ? "解析中…" : "解析预览"}</button></div>{importError && <div className="detail-error">{importError}</div>}{importAnswers && importMeta && <><div className="seven-import-summary"><strong>识别 {importMeta.parsed_count}/7</strong>{importMeta.missing.length>0 && <span>缺少：{importMeta.missing.join("、")}</span>}{importMeta.warnings.map((warning) => <b key={warning}>{warning}</b>)}</div><div className="seven-import-preview">{sevenLabels.map((label) => <label key={label}><strong>{label}</strong><textarea value={importAnswers[label] || ""} onChange={(event) => setImportAnswers({...importAnswers,[label]:event.target.value})}/></label>)}</div><div className="seven-merge-options"><label><input type="radio" checked={strategy==="fill"} onChange={() => setStrategy("fill")}/>仅填充当前空白问题（推荐）</label><label><input type="radio" checked={strategy==="overwrite"} onChange={() => setStrategy("overwrite")}/>用导入内容覆盖已识别问题</label></div><button className="primary-button full-action" onClick={applyImport}>应用到编辑草稿（尚未保存）</button></>}</div>;

  return <div className="seven-reading"><div className="seven-reading-toolbar"><nav aria-label="七问目录">{sevenLabels.map((label,index) => <button key={label} className={String(bundle.seven[label] || "").trim() ? "done" : ""} onClick={() => document.getElementById(`seven-question-${index+1}`)?.scrollIntoView({behavior:"smooth",block:"center"})}>{index+1}</button>)}</nav><div><button className="secondary-button" onClick={() => setMode("import")}><Upload size={13}/>从 AI 导入</button><button className="secondary-button" onClick={() => beginEdit()}><BookOpen size={13}/>编辑七问</button></div></div><div className="seven-answer-list">{sevenLabels.map((label,index) => { const text=String(bundle.seven[label] || "").trim(); const long=text.length>500; const open=expanded.has(index); return <article id={`seven-question-${index+1}`} key={label} className={text ? "filled" : "empty"}><span>{index+1}</span><div><h3>{label}</h3><p>{text ? (long && !open ? text.slice(0,500)+"…" : text) : "尚未填写"}</p>{long && <button onClick={() => setExpanded((current) => { const next=new Set(current); if (next.has(index)) next.delete(index); else next.add(index); return next; })}>{open ? "收起" : "展开全文"}</button>}</div></article>; })}</div></div>;
}

function AnnotationEditor({ citekey, annotations, saving, onSave }: { citekey: string; annotations: PaperAnnotation[]; saving: boolean; onSave: (annotations: PaperAnnotation[]) => Promise<boolean> }) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [draft, setDraft] = useState<PaperAnnotation>({ citekey, fig: "", src: "", note: "", boxes: [] });
  const open = (index: number) => { setEditingIndex(index); setDraft(index === -1 ? { citekey, fig: "", src: "", note: "", boxes: [] } : { ...annotations[index], citekey, boxes: annotations[index].boxes || [] }); };
  const close = () => setEditingIndex(null);
  const save = async () => { const next=editingIndex === -1 ? [...annotations, draft] : annotations.map((item,index) => index === editingIndex ? draft : item); if (await onSave(next)) close(); };
  const remove = async (index: number) => { if (window.confirm("删除这条图片标注？canonical 论文笔记会同步更新。")) await onSave(annotations.filter((_,itemIndex) => itemIndex !== index)); };
  return <div className="annotation-editor"><div className="annotation-toolbar"><strong>Canonical 图片标注</strong><button onClick={() => open(-1)} disabled={saving || editingIndex !== null}><Plus size={12} />新增标注</button></div>{annotations.map((annotation,index) => <div className="annotation-record" key={`${annotation.fig || "annotation"}-${index}`}><span><strong>{annotation.fig || "未编号"}</strong><small>{annotation.src || "来源未登记"}</small><p>{annotation.note || "标注说明待补充"}</p></span><button onClick={() => open(index)} disabled={saving}><Pencil size={12} /></button><button onClick={() => void remove(index)} disabled={saving}><X size={12} /></button></div>)}{editingIndex !== null && <div className="annotation-form"><label>Fig<input value={draft.fig || ""} onChange={(event) => setDraft({ ...draft, fig: event.target.value })} /></label><label>图片来源 src<input value={draft.src || ""} onChange={(event) => setDraft({ ...draft, src: event.target.value })} /></label><label>标注说明<textarea value={draft.note || ""} onChange={(event) => setDraft({ ...draft, note: event.target.value })} /></label><div><button onClick={close} disabled={saving}>取消</button><button onClick={() => void save()} disabled={saving || !String(draft.fig || draft.src || draft.note || "").trim()}>{saving ? "保存中…" : "保存标注"}</button></div></div>}</div>;
}
