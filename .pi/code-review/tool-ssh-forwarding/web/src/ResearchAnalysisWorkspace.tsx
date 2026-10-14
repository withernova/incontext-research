import {
  ArrowLeft, ArrowRight, BookOpen, CheckCircle2, FileSearch, GitCompare,
  Lightbulb, PanelLeftClose, PanelLeftOpen, Pencil, Plus, Save, Search,
  ShieldQuestion, Sparkles, X,
} from "lucide-react";
import { useMemo, useState } from "react";
import {
  ApiError, createV2Comparison, createV2Finding, updateV2Comparison,
  updateV2Finding,
} from "./api";
import type { V2ObjectIndex } from "./api";
import type { Comparison, ComparisonFinding, WorkspaceData } from "./types";
import { V2IndexNote } from "./V2IndexNote";
import { MarkdownContent } from "./MarkdownContent";

type ChangeHandler = () => Promise<void>;
type ComparisonDraft = { name: string; papers: string; axes: string; analysis: string };
const emptyDraft: ComparisonDraft = { name: "", papers: "", axes: "", analysis: "" };
const values = (text: string) => text.split(/[\n,]/).map((value) => value.trim()).filter(Boolean);
const conflictMessage = "内容已被其他写入修改，请刷新后重试";

function errorText(reason: unknown) {
  if (reason instanceof ApiError && reason.reason === "content_hash_conflict") return conflictMessage;
  return reason instanceof Error ? reason.message : String(reason);
}

export function ResearchAnalysisWorkspace({ data, objectIndex, onBack, onChanged }: {
  data: WorkspaceData;
  objectIndex: V2ObjectIndex | null;
  onBack: () => void;
  onChanged: ChangeHandler;
}) {
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState(data.comparisons[0]?.id || "");
  const [listCollapsed, setListCollapsed] = useState(false);
  const [creating, setCreating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [draft, setDraft] = useState<ComparisonDraft>(emptyDraft);
  const comparisons = useMemo(() => {
    const needle = query.trim().toLocaleLowerCase();
    return data.comparisons.filter((comparison) => !needle || `${comparison.name} ${comparison.analysis || ""} ${(comparison.axes || []).join(" ")}`.toLocaleLowerCase().includes(needle));
  }, [data.comparisons, query]);
  const selected = data.comparisons.find((comparison) => comparison.id === selectedId) || comparisons[0];
  const findingCount = data.comparisons.reduce((sum, comparison) => sum + (comparison.findings?.length || 0), 0);
  const paperCount = new Set(data.comparisons.flatMap((comparison) => comparison.papers || [])).size;

  const createComparison = async () => {
    if (!draft.name.trim() || saving) return;
    setSaving(true);
    try {
      const result = await createV2Comparison(data.project.path, {
        name: draft.name.trim(), papers: values(draft.papers), axes: values(draft.axes), analysis: draft.analysis,
      });
      setSelectedId(result.comparison.id);
      await onChanged();
      setDraft(emptyDraft);
      setCreating(false);
    } catch (reason) {
      window.alert(errorText(reason));
    } finally {
      setSaving(false);
    }
  };

  return <div className="analysis-workspace-page">
    <div className="analysis-page-heading"><div><button className="back-button" onClick={onBack}><ArrowLeft size={15} />研究总览</button><div className="eyebrow">Comparative Analysis</div><h1>研究分析</h1><p>把多论文对比、综合分析与 Finding 组织为可追踪研究对象。</p></div><button className="primary-button" onClick={() => setCreating(true)} disabled={saving}><Sparkles size={16} />新建对比</button></div>
    {creating && <section className="analysis-write-form">
      <div className="analysis-write-head"><div><strong>创建 Comparison</strong><small>保存到 canonical Markdown，并同步 v2 对象索引</small></div><button aria-label="取消创建" onClick={() => { setCreating(false); setDraft(emptyDraft); }} disabled={saving}><X size={15} /></button></div>
      <div className="analysis-form-grid">
        <label>名称（必填）<input autoFocus value={draft.name} onChange={(event) => setDraft({ ...draft, name: event.target.value })} /></label>
        <label>论文 citekey（逗号或换行分隔）<textarea value={draft.papers} onChange={(event) => setDraft({ ...draft, papers: event.target.value })} placeholder={data.papers.slice(0, 3).map((paper) => paper.citekey).join(", ")} /></label>
        <label>分析轴（逗号或换行分隔）<textarea value={draft.axes} onChange={(event) => setDraft({ ...draft, axes: event.target.value })} /></label>
        <label>综合分析<textarea value={draft.analysis} onChange={(event) => setDraft({ ...draft, analysis: event.target.value })} /></label>
      </div>
      <div className="analysis-form-actions"><button className="secondary-button" onClick={() => setCreating(false)} disabled={saving}>取消</button><button className="primary-button" onClick={() => void createComparison()} disabled={saving || !draft.name.trim()}>{saving ? "创建中…" : "创建 Comparison"}</button></div>
    </section>}
    <div className="analysis-summary-strip"><div><GitCompare size={17} /><span><small>对比项目</small><strong>{data.comparisons.length}</strong></span></div><div><BookOpen size={17} /><span><small>参与论文</small><strong>{paperCount}</strong></span></div><div><Lightbulb size={17} /><span><small>Findings</small><strong>{findingCount}</strong></span></div><div><CheckCircle2 size={17} /><span><small>Validated Claims</small><strong>独立门禁</strong></span></div></div>
    <V2IndexNote index={objectIndex} type="comparison" legacyCount={data.comparisons.length} />
    <div className={`analysis-layout ${listCollapsed ? "selector-collapsed" : ""}`}>
      <section className={`comparison-list-panel ${listCollapsed ? "collapsed" : ""}`}>{listCollapsed ? <button className="selector-restore" aria-label="展开对比项目选择" title="展开对比项目选择" onClick={() => setListCollapsed(false)}><PanelLeftOpen size={17} /><span>对比</span></button> : <><div className="comparison-list-tools"><div className="catalog-search"><Search size={15} /><input aria-label="搜索对比项目" placeholder="标题、分析轴或正文" value={query} onChange={(event) => setQuery(event.target.value)} /></div><button className="selector-collapse-button" aria-label="收起对比项目选择" title="收起对比项目选择" onClick={() => setListCollapsed(true)}><PanelLeftClose size={16} /></button></div><div className="comparison-list-items">{comparisons.map((comparison) => <button key={comparison.id} className={selected?.id === comparison.id ? "selected" : ""} onClick={() => setSelectedId(comparison.id)}><span className="comparison-list-icon"><GitCompare size={16} /></span><span><strong>{comparison.name}</strong><small>{comparison.papers.length} 篇论文 · {(comparison.axes || []).length} 个分析轴</small></span><ArrowRight size={14} /></button>)}{!comparisons.length && <div className="catalog-empty">没有匹配的对比项目</div>}</div></>}
      </section>
      <section className="comparison-detail-panel">{selected ? <ComparisonDetail key={`${selected.id}:${selected._canonical_rev || ""}`} comparison={selected} data={data} onChanged={onChanged} /> : <div className="question-detail-empty"><FileSearch size={25} /><strong>选择一个对比项目</strong></div>}</section>
    </div>
  </div>;
}

function ComparisonDetail({ comparison, data, onChanged }: { comparison: Comparison; data: WorkspaceData; onChanged: ChangeHandler }) {
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [findingOpen, setFindingOpen] = useState(false);
  const [draft, setDraft] = useState<ComparisonDraft>({
    name: comparison.name, papers: comparison.papers.join(", "), axes: (comparison.axes || []).join("\n"), analysis: comparison.analysis || "",
  });
  const paperMap = new Map(data.papers.map((paper) => [paper.citekey, paper]));
  const axes = [...(comparison.axes || []), ...(comparison.customAxes || [])];

  const saveComparison = async () => {
    if (!draft.name.trim() || saving) return;
    setSaving(true);
    try {
      await updateV2Comparison(data.project.path, comparison.id, comparison._canonical_rev || "", {
        name: draft.name.trim(), papers: values(draft.papers), axes: values(draft.axes), analysis: draft.analysis,
      });
      await onChanged();
      setEditing(false);
    } catch (reason) {
      if (reason instanceof ApiError && reason.reason === "content_hash_conflict") await onChanged();
      window.alert(errorText(reason));
    } finally {
      setSaving(false);
    }
  };

  return <>
    <div className="comparison-detail-head"><div><div className="comparison-meta"><code>{comparison.id}</code><span>{comparison.mode || "structured"}</span></div><h2>{comparison.name}</h2><p>{comparison.papers.length} 篇论文参与本次比较</p></div><button className="secondary-button" onClick={() => setEditing(true)} disabled={saving}><Pencil size={15} />编辑 Comparison</button></div>
    {editing && <section className="analysis-write-form detail-form">
      <div className="analysis-form-grid">
        <label>名称（必填）<input value={draft.name} onChange={(event) => setDraft({ ...draft, name: event.target.value })} /></label>
        <label>论文 citekey<textarea value={draft.papers} onChange={(event) => setDraft({ ...draft, papers: event.target.value })} /></label>
        <label>分析轴<textarea value={draft.axes} onChange={(event) => setDraft({ ...draft, axes: event.target.value })} /></label>
        <label>综合分析<textarea value={draft.analysis} onChange={(event) => setDraft({ ...draft, analysis: event.target.value })} /></label>
      </div>
      <div className="analysis-form-actions"><button className="secondary-button" onClick={() => setEditing(false)} disabled={saving}>取消</button><button className="primary-button" onClick={() => void saveComparison()} disabled={saving || !draft.name.trim()}><Save size={14} />{saving ? "保存中…" : "保存"}</button></div>
    </section>}
    <div className="comparison-detail-body">
      <section className="comparison-paper-section"><div className="analysis-section-title"><div><h3>参与论文</h3><p>明确本次分析覆盖的证据范围</p></div><BookOpen size={17} /></div><div className="comparison-paper-grid">{comparison.papers.map((citekey) => { const paper = paperMap.get(citekey); return <article key={citekey}><span><BookOpen size={15} /></span><div><strong>{paper?.title || citekey}</strong><small>{citekey} · {paper?.has_mineru ? "已解析" : paper?.has_pdf ? "PDF 已收录" : "来源待补充"}</small></div></article>; })}</div></section>
      <div className="analysis-two-column"><section className="analysis-card"><div className="analysis-section-title"><div><h3>分析轴</h3><p>用于回答跨论文差异</p></div><span>{axes.length}</span></div><div className="axis-list">{axes.length ? axes.map((axis, index) => <div key={`${axis}-${index}`}><span>{String(index + 1).padStart(2, "0")}</span><strong>{axis}</strong></div>) : <div className="analysis-empty">尚未登记分析轴</div>}</div></section>
        <section className="analysis-card"><div className="analysis-section-title"><div><h3>Findings</h3><p>可检索的结论草稿</p></div><button className="analysis-inline-action" onClick={() => setFindingOpen(true)} disabled={saving}><Plus size={13} />新增</button></div>
          {findingOpen && <FindingEditor comparisonId={comparison.id} projectPath={data.project.path} onChanged={onChanged} onClose={() => setFindingOpen(false)} />}
          <div className="finding-list">{comparison.findings?.length ? comparison.findings.map((finding, index) => <FindingRow key={finding.id || index} finding={finding} projectPath={data.project.path} onChanged={onChanged} />) : <div className="analysis-empty">尚未形成 Finding</div>}</div>
        </section></div>
      <section className="analysis-prose-section"><div className="analysis-section-title"><div><h3>关联分析</h3><p>canonical Markdown 中的当前综合判断</p></div><FileSearch size={17} /></div><MarkdownContent className="analysis-prose">{(comparison.analysis || comparison.piAnalysis || "尚未形成综合分析。").trim()}</MarkdownContent></section>
      <div className="analysis-trust-note"><ShieldQuestion size={18} /><div><strong>结论边界</strong><p>Comparison 的综合分析和 Finding 可以支撑后续 Question 或 Claim 草稿，但只有通过来源 hash、R2 对抗审查和人工批准的 Claim 才能成为 validated synthesis 的依据。</p></div></div>
    </div>
  </>;
}

function FindingRow({ finding, projectPath, onChanged }: { finding: ComparisonFinding; projectPath: string; onChanged: ChangeHandler }) {
  const [editing, setEditing] = useState(false);
  return editing ? <FindingEditor finding={finding} projectPath={projectPath} onChanged={onChanged} onClose={() => setEditing(false)} /> : <article className="finding-row"><span>{finding.id || "draft"}</span><div><MarkdownContent>{finding.text || "Finding 正文待补充"}</MarkdownContent>{finding.source && <MarkdownContent className="finding-source-markdown">{finding.source}</MarkdownContent>}</div>{finding.id && <button aria-label={`编辑 ${finding.id}`} onClick={() => setEditing(true)}><Pencil size={12} /></button>}</article>;
}

function FindingEditor({ comparisonId, finding, projectPath, onChanged, onClose }: {
  comparisonId?: string; finding?: ComparisonFinding; projectPath: string; onChanged: ChangeHandler; onClose: () => void;
}) {
  const [text, setText] = useState(finding?.text || "");
  const [source, setSource] = useState(finding?.source || "");
  const [saving, setSaving] = useState(false);
  const save = async () => {
    if (!text.trim() || saving) return;
    setSaving(true);
    try {
      if (finding?.id) await updateV2Finding(projectPath, finding.id, finding._canonical_rev || "", { text: text.trim(), source });
      else if (comparisonId) await createV2Finding(projectPath, comparisonId, { text: text.trim(), source });
      await onChanged();
      onClose();
    } catch (reason) {
      if (reason instanceof ApiError && reason.reason === "content_hash_conflict") await onChanged();
      window.alert(errorText(reason));
    } finally {
      setSaving(false);
    }
  };
  return <div className="finding-editor"><label>Finding（必填）<textarea autoFocus value={text} onChange={(event) => setText(event.target.value)} /></label><label>来源<input value={source} onChange={(event) => setSource(event.target.value)} /></label><div><button onClick={onClose} disabled={saving}>取消</button><button onClick={() => void save()} disabled={saving || !text.trim()}>{saving ? "保存中…" : "保存"}</button></div></div>;
}
