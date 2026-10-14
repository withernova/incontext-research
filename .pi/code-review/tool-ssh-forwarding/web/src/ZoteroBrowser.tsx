import { useState } from "react";
import type { StoredPaperCandidate } from "./api";
import type { ZoteroItem } from "./types";

export function ZoteroBrowser({items, loading, enabled, saved, onAdd, onView}: {
  items: ZoteroItem[]; loading: boolean; enabled: boolean;
  saved: Map<string, StoredPaperCandidate>;
  onAdd: (item: ZoteroItem) => Promise<boolean>; onView: (id: string) => void;
}) {
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [onlyPdf, setOnlyPdf] = useState(false);
  const [onlyNew, setOnlyNew] = useState(false);
  const stored = (item: ZoteroItem) => saved.get(`https://www.zotero.org/items/${item.id}`);
  const available = (item: ZoteroItem) => !item.already_in && !stored(item);
  const visible = items.filter(item => (!onlyPdf || item.has_pdf) && (!onlyNew || available(item)));
  const selectable = visible.filter(available);
  const picked = selectable.filter(item => selected.has(item.id));
  const add = async (rows: ZoteroItem[]) => {
    if (busy || !enabled || loading) return;
    setBusy(true); let count = 0; const succeeded = new Set<number>();
    try {
      for (const [index, item] of rows.entries()) {
        setMessage(`正在添加 ${index + 1} / ${rows.length}：${item.title}`);
        try { if (await onAdd(item)) { count++; succeeded.add(item.id); } } catch { /* Keep other selections available to retry. */ }
      }
      setSelected(current => new Set([...current].filter(id => !succeeded.has(id))));
      setMessage(`已添加 ${count} 篇${count < rows.length ? `，${rows.length - count} 篇未成功，可重试` : ""}。在“候选与本地任务”中准备 PDF 并纳入论文库。`);
    } finally { setBusy(false); }
  };
  return <section className="zotero-browser" aria-label="Zotero 本地论文">
    <div className="zotero-toolbar">
      <label><input type="checkbox" checked={onlyPdf} disabled={busy} onChange={e => setOnlyPdf(e.target.checked)}/>仅有本地 PDF</label>
      <label><input type="checkbox" checked={onlyNew} disabled={busy} onChange={e => setOnlyNew(e.target.checked)}/>仅未添加</label>
      <span>{visible.length} 篇 · 已选 {picked.length} 篇</span>
      <button disabled={!enabled || busy || loading || !selectable.length} onClick={() => setSelected(picked.length === selectable.length ? new Set() : new Set(selectable.map(item => item.id)))}>{picked.length && picked.length === selectable.length ? "取消选择" : "选择当前结果"}</button>
      <button disabled={!enabled || busy || loading || !picked.length} onClick={() => void add(picked)}>{busy ? "添加中…" : `添加所选（${picked.length}）`}</button>
    </div>
    {message && <p role="status" className="candidate-notice">{message}</p>}
    {loading ? <p role="status" className="catalog-empty">正在读取本地 Zotero 库…</p> : !visible.length ? <div className="catalog-empty">没有符合条件的论文。可调整分类、关键词或筛选条件；在 Zotero 新增论文后点击“刷新本地库”。</div> : visible.map(item => {
      const candidate = stored(item); const inLibrary = item.already_in || candidate?.verification_status === "ingested";
      return <article key={item.id} className="zotero-paper-row">
        <input type="checkbox" aria-label={`选择 ${item.title}`} checked={selected.has(item.id) && available(item)} disabled={!enabled || busy || !available(item)} onChange={e => setSelected(current => {const next = new Set(current); if(e.target.checked) next.add(item.id); else next.delete(item.id); return next;})}/>
        <div className="candidate-copy"><h3>{item.title}</h3><p>{item.authors.join("、") || "作者未登记"}</p><div>{item.date || "年份未知"}{item.venue && ` · ${item.venue}`}</div>{item.doi && <small>DOI {item.doi}</small>}</div>
        <div className="candidate-actions"><span className={item.has_pdf ? "oa" : "closed"}>{item.has_pdf ? "本地 PDF 可用" : "未找到本地 PDF"}</span>
          {inLibrary ? <button disabled>已在论文库</button> : candidate ? <button onClick={() => onView(candidate.id)}>已添加 · 查看任务</button> : <button disabled={!enabled || busy} onClick={() => void add([item])}>{busy ? "添加中…" : item.has_pdf ? "添加到候选" : "仅添加文献信息"}</button>}
        </div>
      </article>;
    })}
  </section>;
}
