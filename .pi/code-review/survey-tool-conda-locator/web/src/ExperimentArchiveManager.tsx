import { Archive, RotateCcw, Search, X } from "lucide-react";
import { useMemo, useState } from "react";
import { ApiError, archiveV2Experiment, archiveV2Run } from "./api";
import type { Experiment, ExperimentDashboard, Run } from "./types";

type Props={projectPath:string;dashboard:ExperimentDashboard;onDashboard:(value:ExperimentDashboard)=>void;onChanged:()=>Promise<void>;onClose:()=>void};
type Selection={kind:"experiment";item:Experiment}|{kind:"run";item:Run};

const time=(value?:string)=>value?new Date(value).toLocaleString("zh-CN",{dateStyle:"medium",timeStyle:"short"}):"";
const matches=(value:Experiment|Run,query:string)=>{
  if(!query)return true;
  const content="title" in value?[value.id,value.title,value.objective,value.archive_reason]:[value.id,value.variant,value.purpose,value.archive_reason];
  return content.some(item=>String(item||"").toLowerCase().includes(query));
};

export function ExperimentArchiveManager({projectPath,dashboard,onDashboard,onChanged,onClose}:Props){
  const [view,setView]=useState<"active"|"archived">("active");
  const [query,setQuery]=useState("");
  const [selection,setSelection]=useState<Selection|null>(null);
  const [reason,setReason]=useState("");
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState("");
  const archived=view==="archived";
  const normalized=query.trim().toLowerCase();
  const archivedCount=dashboard.experiments.filter(item=>item.archived_at).length+dashboard.runs.filter(item=>item.archived_at).length;
  const groups=useMemo(()=>dashboard.experiments.map(experiment=>{
    const experimentVisible=Boolean(experiment.archived_at)===archived&&matches(experiment,normalized);
    const runs=dashboard.runs.filter(run=>run.experiment_id===experiment.id&&Boolean(run.archived_at)===archived&&matches(run,normalized));
    return {experiment,experimentVisible,runs};
  }).filter(group=>group.experimentVisible||group.runs.length),[dashboard,archived,normalized]);

  const choose=(next:Selection)=>{setSelection(next);setReason(next.item.archive_reason||"");setError("")};
  const submit=async()=>{
    if(!selection)return;
    const restore=Boolean(selection.item.archived_at);
    if(!restore&&!reason.trim()){setError("请写一句失效原因，之后才能知道为什么被隐藏。");return}
    setBusy(true);setError("");
    try{
      const result=selection.kind==="experiment"
        ?await archiveV2Experiment(projectPath,selection.item,reason,restore)
        :await archiveV2Run(projectPath,selection.item,reason,restore);
      onDashboard(result.dashboard);setSelection(null);setReason("");await onChanged();
    }catch(value){setError(value instanceof ApiError&&value.reason==="registry_version_conflict"?"记录刚刚发生了变化，请刷新后重试。":value instanceof Error?value.message:String(value))}
    finally{setBusy(false)}
  };

  return <div className="archive-manager-backdrop" role="presentation">
    <section className="archive-manager" role="dialog" aria-modal="true" aria-label="Experiment 与 Run 失效管理">
      <header className="archive-manager-head">
        <div><small>EXPERIMENT RECORDS</small><h2>失效与恢复</h2><p>失效只从日常工作区隐藏，不会删除实验、结果或执行历史。</p></div>
        <button className="icon-button" onClick={onClose} aria-label="关闭"><X size={16}/></button>
      </header>

      <div className="archive-toolbar">
        <div className="paper-filters" role="tablist">
          <button className={view==="active"?"active":""} onClick={()=>{setView("active");setSelection(null)}}>有效</button>
          <button className={view==="archived"?"active":""} onClick={()=>{setView("archived");setSelection(null)}}>已失效 {archivedCount>0&&<span>{archivedCount}</span>}</button>
        </div>
        <label className="archive-search"><Search size={13}/><input value={query} onChange={event=>setQuery(event.target.value)} placeholder="搜索编号或名称"/></label>
      </div>

      {error&&<div className="detail-error">{error}</div>}
      <div className="archive-tree">
        {groups.length===0&&<div className="archive-empty"><Archive size={19}/><strong>{archived?"没有已失效记录":"没有匹配的有效记录"}</strong></div>}
        {groups.map(({experiment,experimentVisible,runs})=><article className="archive-experiment" key={experiment.id}>
          <header>
            <div><code>{experiment.id}</code><span><strong>{experiment.title}</strong><small>{experiment.archived_at?`已失效 · ${time(experiment.archived_at)}`:`${dashboard.runs.filter(run=>run.experiment_id===experiment.id&&!run.archived_at).length} 个有效 Run`}</small></span></div>
            {experimentVisible&&<button className="archive-row-action" onClick={()=>choose({kind:"experiment",item:experiment})}>{experiment.archived_at?<><RotateCcw size={13}/>恢复 Experiment</>:<><Archive size={13}/>设为失效</>}</button>}
          </header>
          {experiment.archived_at&&experiment.archive_reason&&<p className="archive-reason">{experiment.archive_reason}</p>}
          {runs.length>0&&<div className="archive-run-list">{runs.map(run=><div className="archive-run-row" key={run.id}>
            <div><code>{run.id}</code><span><strong>{run.variant||"未命名 Run"}</strong><small>{run.archived_at?`已失效 · ${time(run.archived_at)}`:run.workflow_stage||run.status||"状态未登记"}</small>{run.archive_reason&&<em>{run.archive_reason}</em>}</span></div>
            <button className="archive-row-action" onClick={()=>choose({kind:"run",item:run})}>{run.archived_at?<><RotateCcw size={13}/>恢复</>:<><Archive size={13}/>失效</>}</button>
          </div>)}</div>}
          {!runs.length&&<div className="archive-no-runs">本组没有{archived?"已失效":"有效"} Run</div>}
        </article>)}
      </div>

      {selection&&<section className="archive-action-sheet">
        <div><small>{selection.kind==="experiment"?"EXPERIMENT":"RUN"}</small><strong>{selection.item.id} · {selection.item.archived_at?"恢复记录":"设为失效"}</strong><p>{selection.item.archived_at?"恢复后重新出现在工作区，原科研状态保持不变。":"仍在排队、领取或运行的 execution 不允许被隐藏。"}</p></div>
        {!selection.item.archived_at&&<label>失效原因<textarea autoFocus value={reason} onChange={event=>setReason(event.target.value)} placeholder="例如：被后续方案替代"/></label>}
        <div><button className="secondary-button" onClick={()=>{setSelection(null);setError("")}}>取消</button><button className="primary-button" disabled={busy||(!selection.item.archived_at&&!reason.trim())} onClick={()=>void submit()}>{selection.item.archived_at?<RotateCcw size={14}/>:<Archive size={14}/>} {busy?"保存中…":selection.item.archived_at?"恢复":"确认失效"}</button></div>
      </section>}
    </section>
  </div>;
}
