import { ArrowLeft, FileSearch, Lightbulb, Pencil, Plus, Save, Search, ShieldQuestion, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { ApiError, createV2Idea, loadIdeas, updateV2Idea } from "./api";
import type { Idea, WorkspaceData } from "./types";

type Props = { data: WorkspaceData; onBack: () => void; onChanged: () => Promise<void> };
const editable = ["title","hypothesis","motivation","method","key_experiments","risks","related_diff","falsification","status","novelty","novelty_note","support_claims","contra_claims","sources"] as const;
type Draft = Record<(typeof editable)[number], string>;
const labels: Record<keyof Draft,string> = {
  title:"标题", hypothesis:"假设", motivation:"动机", method:"方法", key_experiments:"关键实验",
  risks:"风险", related_diff:"与相关工作的差异", falsification:"可证伪条件", status:"状态",
  novelty:"新颖性判断", novelty_note:"新颖性说明", support_claims:"支持 Claims",
  contra_claims:"反对 Claims", sources:"来源",
};
const makeDraft = (idea?: Partial<Idea>): Draft => Object.fromEntries(editable.map((key) => [key,String(idea?.[key] || "")])) as Draft;
const normalizeRefs = (value: string) => value.split(/[\n,]/).map((item) => item.trim()).filter(Boolean).join(", ");

export function IdeaWorkspace({ data, onBack, onChanged }: Props) {
  const [ideas,setIdeas]=useState(data.ideas);
  const [selectedId,setSelectedId]=useState(data.ideas[0]?.id || "");
  const [query,setQuery]=useState("");
  const [creating,setCreating]=useState(false);
  const [createDraft,setCreateDraft]=useState<Draft>(makeDraft());
  const [saving,setSaving]=useState(false);
  const [error,setError]=useState("");
  useEffect(() => setIdeas(data.ideas),[data.ideas]);
  const filtered=useMemo(() => { const needle=query.trim().toLowerCase(); return ideas.filter((idea) => !needle || `${idea.id} ${idea.title} ${idea.hypothesis || ""}`.toLowerCase().includes(needle)); },[ideas,query]);
  const selected=ideas.find((idea) => idea.id===selectedId) || filtered[0];

  const reload=async () => { const rows=await loadIdeas(data.project.path); setIdeas(rows); return rows; };
  const create=async () => {
    if (!createDraft.title.trim() || saving) return;
    setSaving(true); setError("");
    try {
      const result=await createV2Idea(data.project.path,{...createDraft,title:createDraft.title.trim(),support_claims:normalizeRefs(createDraft.support_claims),contra_claims:normalizeRefs(createDraft.contra_claims)});
      setSelectedId(result.idea.id); setCreating(false); setCreateDraft(makeDraft()); await onChanged(); await reload();
    } catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)); }
    finally { setSaving(false); }
  };

  return <div className="idea-workspace-page">
    <div className="idea-page-heading"><div><button className="back-button" onClick={onBack}><ArrowLeft size={15}/>研究总览</button><div className="eyebrow">Research Proposals</div><h1>Ideas</h1><p>记录可检验的研究提案；Idea 不是经过验证的 Claim。</p></div><button className="primary-button" onClick={() => setCreating(true)} disabled={saving}><Plus size={15}/>创建 Idea</button></div>
    {error && <div className="detail-error">{error}</div>}
    {creating && <IdeaForm draft={createDraft} setDraft={setCreateDraft} saving={saving} title="创建 Idea" onCancel={() => { setCreating(false); setCreateDraft(makeDraft()); }} onSave={() => void create()} />}
    <div className="idea-layout">
      <section className="idea-list-panel"><div className="comparison-list-tools"><div className="catalog-search"><Search size={15}/><input aria-label="搜索 Ideas" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="ID、标题或假设"/></div></div><div className="idea-list">{filtered.map((idea) => <button key={idea.id} className={selected?.id===idea.id ? "selected" : ""} onClick={() => setSelectedId(idea.id)}><Lightbulb size={15}/><span><strong>{idea.title || idea.id}</strong><small>{idea.id} · {idea.status || "draft"}</small></span></button>)}{!filtered.length && <div className="catalog-empty">没有匹配的 Idea</div>}</div></section>
      <section className="idea-detail-panel">{selected ? <IdeaDetail key={`${selected.id}:${selected._canonical_rev}`} idea={selected} projectPath={data.project.path} saving={saving} setSaving={setSaving} setError={setError} reload={reload} onChanged={onChanged}/> : <div className="question-detail-empty"><FileSearch size={24}/><strong>选择或创建一个 Idea</strong></div>}</section>
    </div>
  </div>;
}

function IdeaDetail({idea,projectPath,saving,setSaving,setError,reload,onChanged}: { idea:Idea; projectPath:string; saving:boolean; setSaving:(value:boolean)=>void; setError:(value:string)=>void; reload:()=>Promise<Idea[]>; onChanged:()=>Promise<void> }) {
  const [editing,setEditing]=useState(false);
  const [draft,setDraft]=useState<Draft>(makeDraft(idea));
  const save=async () => {
    if (!draft.title.trim() || saving) return;
    setSaving(true); setError("");
    try {
      await updateV2Idea(projectPath,idea.id,idea._canonical_rev,{...draft,title:draft.title.trim(),support_claims:normalizeRefs(draft.support_claims),contra_claims:normalizeRefs(draft.contra_claims)});
      await onChanged(); await reload(); setEditing(false);
    } catch (reason) {
      if (reason instanceof ApiError && reason.reason==="content_hash_conflict") { setError("内容已被其他写入修改，请刷新后重试"); await reload(); }
      else setError(reason instanceof Error ? reason.message : String(reason));
    } finally { setSaving(false); }
  };
  if (editing) return <IdeaForm draft={draft} setDraft={setDraft} saving={saving} title={`编辑 ${idea.id}`} onCancel={() => { setDraft(makeDraft(idea)); setEditing(false); }} onSave={() => void save()}/>;
  return <><div className="idea-detail-head"><div><code>{idea.id}</code><span>{idea.status || "draft"}</span><h2>{idea.title}</h2></div><button className="secondary-button" onClick={() => setEditing(true)}><Pencil size={14}/>编辑</button></div><div className="idea-detail-body">{(["hypothesis","motivation","method","key_experiments","risks","related_diff","falsification","novelty","novelty_note","sources","support_claims","contra_claims"] as const).map((key) => <section key={key}><h3>{labels[key]}</h3><p>{idea[key] || "尚未填写"}</p></section>)}<div className="idea-proposal-note"><ShieldQuestion size={17}/><div><strong>Proposal 边界</strong><p>Idea 中引用的支持或反对 Claim 不会改变 Claim 状态；验证仍受独立人工门禁控制。</p></div></div></div></>;
}

function IdeaForm({draft,setDraft,saving,title,onCancel,onSave}: { draft:Draft; setDraft:(draft:Draft)=>void; saving:boolean; title:string; onCancel:()=>void; onSave:()=>void }) {
  return <section className="idea-form"><div className="idea-form-head"><strong>{title}</strong><button aria-label="取消" onClick={onCancel} disabled={saving}><X size={14}/></button></div><div className="idea-form-grid">{editable.map((key) => <label key={key} className={key==="title" ? "wide" : ""}>{labels[key]}{key==="title" && "（必填）"}{key==="status" || key==="novelty" ? <input value={draft[key]} onChange={(event) => setDraft({...draft,[key]:event.target.value})}/> : <textarea value={draft[key]} onChange={(event) => setDraft({...draft,[key]:event.target.value})}/>}</label>)}</div><div className="analysis-form-actions"><button className="secondary-button" onClick={onCancel} disabled={saving}>取消</button><button className="primary-button" onClick={onSave} disabled={saving || !draft.title.trim()}><Save size={14}/>{saving ? "保存中…" : "保存"}</button></div></section>;
}

