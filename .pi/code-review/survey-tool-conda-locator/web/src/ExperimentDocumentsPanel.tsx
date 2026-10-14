import { Copy, FileText, RefreshCw, Search } from "lucide-react";
import { useEffect, useState } from "react";
import { loadExperimentDocument, loadExperimentDocuments, refreshExperimentDocuments, type ExperimentDocumentContent, type ExperimentDocumentList } from "./api";
import { MarkdownContent } from "./MarkdownContent";
import { resolveExperimentDocumentLink, stripDocumentProperties } from "./experimentDocumentModel";
import "./experimentDocuments.css";

const versions:Record<string,string>={current:"当前版本（显式标记）",superseded:"已被替代",draft:"草稿",archived:"已归档"};
export function ExperimentDocumentsPanel({projectPath,experimentId}:{projectPath:string;experimentId:string}){
  const [query,setQuery]=useState("");
  const [directory,setDirectory]=useState("");
  const [kind,setKind]=useState("all");
  const [sort,setSort]=useState("modified");
  const [status,setStatus]=useState("all");
  const [revision,setRevision]=useState(0);
  const [result,setResult]=useState<ExperimentDocumentList|null>(null);
  const [selected,setSelected]=useState("");
  const [document,setDocument]=useState<ExperimentDocumentContent|null>(null);
  const [loading,setLoading]=useState(true);
  const [reading,setReading]=useState(false);
  const [refreshing,setRefreshing]=useState(false);
  const [error,setError]=useState("");
  const [readError,setReadError]=useState("");
  const [notice,setNotice]=useState("");
  const [raw,setRaw]=useState(false);

  useEffect(()=>{
    const controller=new AbortController();
    setLoading(true);setError("");
    const timer=window.setTimeout(()=>{
      loadExperimentDocuments(projectPath,experimentId,{q:query,directory,kind,sort,status},controller.signal)
        .then(value=>{if(controller.signal.aborted)return;if(value.experiment_id!==experimentId)throw new Error("文档列表所属 Experiment 不匹配");setResult(value)})
        .catch(reason=>{if(!controller.signal.aborted){setResult(null);setError(reason instanceof Error?reason.message:String(reason))}})
        .finally(()=>{if(!controller.signal.aborted)setLoading(false)});
    },200);
    return()=>{window.clearTimeout(timer);controller.abort()};
  },[projectPath,experimentId,query,directory,kind,sort,status,revision]);

  useEffect(()=>{
    if(!selected)return;
    const controller=new AbortController();
    setReading(true);setReadError("");setRaw(false);
    loadExperimentDocument(projectPath,experimentId,selected,controller.signal)
      .then(value=>{if(controller.signal.aborted)return;if(value.experiment_id!==experimentId||value.path!==selected)throw new Error("文档所属 Experiment 或路径不匹配");setDocument(value)})
      .catch(reason=>{if(!controller.signal.aborted){setDocument(null);setReadError(reason instanceof Error?reason.message:String(reason))}})
      .finally(()=>{if(!controller.signal.aborted)setReading(false)});
    return()=>controller.abort();
  },[projectPath,experimentId,selected,revision]);

  const refreshNavigation=async()=>{
    if(!window.confirm(`只更新 ${experimentId} 的实验入口、文档目录和结果页，保留自由笔记与审计正文。不移动目录，不修改 Run 或执行授权。确认继续？`))return;
    setRefreshing(true);setNotice("");setError("");
    try{const value=await refreshExperimentDocuments(projectPath,experimentId);if(value.experiment_id!==experimentId)throw new Error("刷新目标不匹配");setNotice(`已更新 ${experimentId} 的 ${value.paths.length} 个导航/结果文件。`);setRevision(value=>value+1)}
    catch(reason){setError(reason instanceof Error?reason.message:String(reason))}
    finally{setRefreshing(false)}
  };
  const copyPath=async(path:string)=>{try{await navigator.clipboard.writeText(path);setNotice(`已复制：${path}`)}catch{setNotice(`无法自动复制，请手动复制：${path}`)}};
  const active=document?.path===selected&&document.experiment_id===experimentId?document:null;
  return <section className="experiment-documents-panel" aria-label={`${experimentId} 文档检索`}>
    <header><div><h3>{experimentId} · 文档</h3><p>只检索本实验，包含子目录；标题、路径和专题匹配，不进行全文检索。每次查询读取当前文件，不依赖已生成的 Obsidian 目录。</p></div><div><button onClick={()=>setRevision(value=>value+1)} disabled={loading}><RefreshCw size={14}/>重新检索</button><button onClick={()=>void refreshNavigation()} disabled={refreshing||loading||Boolean(error)}>更新 Obsidian 导航</button></div></header>
    <div className="experiment-document-filters">
      <label className="document-search"><Search size={15}/><input aria-label="搜索实验文档" maxLength={300} value={query} onChange={event=>setQuery(event.target.value)} placeholder="搜索标题、文件路径或专题（包含子目录）"/></label>
      <label>子目录<select aria-label="文档子目录" value={directory} onChange={event=>setDirectory(event.target.value)}><option value="">全部目录（含子目录）</option>{result?.directories.filter(Boolean).map(path=><option key={path} value={path}>{path}（含子目录）</option>)}</select></label>
      <label>类型<select aria-label="文档类型" value={kind} onChange={event=>setKind(event.target.value)}><option value="all">全部</option><option value="topic">专题文档</option><option value="core">核心文档</option><option value="run">Run 文档</option></select></label>
      <label>版本<select aria-label="文档版本" value={status} onChange={event=>setStatus(event.target.value)}><option value="all">全部版本</option>{Object.entries(versions).map(([value,label])=><option key={value} value={value}>{label}</option>)}<option value="unmarked">未标记</option></select></label>
      <label>排序<select aria-label="文档排序" value={sort} onChange={event=>setSort(event.target.value)}><option value="modified">最近修改（专题优先）</option><option value="path">按路径</option></select></label>
    </div>
    <p className="document-recency-note">最近修改 ≠ 当前有效版本。目录缺失或嵌套其他 E-ID 时会提示，不会自动移动或创建实验目录。</p>
    {error&&<div role="alert" className="detail-error">{error}</div>}
    {notice&&<p role="status" className="document-notice">{notice}</p>}
    {result?.warnings.length? <ul className="document-warnings">{result.warnings.map((warning,index)=><li key={index}>{warning}</li>)}</ul>:null}
    <div className="experiment-document-layout">
      <aside className="document-results"><strong>{loading?"正在检索…":`${result?.total||0} 个匹配文档 / ${result?.indexed_count||0} 个已索引文档`}</strong>
        {!loading&&result?.documents.length===0&&<p>本实验没有匹配文档。请更换关键词或子目录。</p>}
        {result?.documents.map(row=><button key={row.path} disabled={loading} className={selected===row.path?"selected":""} onClick={()=>{setSelected(row.path);setNotice("")}}><span><FileText size={14}/><b>{row.title}</b></span><code>{row.path}</code><small>{row.topic?`${row.topic} · `:""}{versions[row.status]||"未标记"}</small><small>{row.generated?"工具生成页；以登记记录为准":`文件修改：${row.modified}`}</small></button>)}
      </aside>
      <article className="document-reader">
        {!selected?<p>选择左侧文档进行只读阅读。文件的完整相对路径可复制到 Obsidian 查找。</p>:<>
          <header><div><strong>{active?.title||selected}</strong><code>{`shell/06_experiments/${experimentId}/${selected}`}</code></div><button onClick={()=>void copyPath(`shell/06_experiments/${experimentId}/${selected}`)}><Copy size={14}/>复制路径</button><button onClick={()=>setRaw(value=>!value)}>{raw?"阅读视图":"Markdown 原文"}</button></header>
          {reading?<p>读取中…</p>:readError?<div role="alert" className="detail-error">{readError}</div>:active&&(raw?<pre className="document-raw">{active.content}</pre>:<div onClick={event=>{const anchor=(event.target as HTMLElement).closest("a");if(!anchor)return;const href=anchor.getAttribute("href")||"";if(/^https?:\/\//i.test(href))return;event.preventDefault();const path=resolveExperimentDocumentLink(selected,href);if(path)setSelected(path);else setNotice("该链接不是本实验内可读取的 Markdown 文档。请复制路径，在 Obsidian 查看其他资料。")}}><MarkdownContent>{stripDocumentProperties(active.content)}</MarkdownContent></div>)}
        </>}
      </article>
    </div>
  </section>;
}
