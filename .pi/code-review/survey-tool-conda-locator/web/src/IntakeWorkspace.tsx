import { ArrowLeft, CheckCircle2, FileText, Play, Save, Settings, ShieldQuestion } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { ApiError, loadIntake, materializeV2Intake, updateV2Intake } from "./api";
import type { Intake, WorkspaceData } from "./types";

type IntakeData = Omit<Intake,"_canonical_rev" | "_exists">;
const scalarFields: Array<[keyof IntakeData,string,boolean]> = [
  ["repo_path","仓库路径",false],["project_slug","项目 slug",false],["project_name","项目名称",false],
  ["idea","研究想法",true],["domain","研究领域",false],["target_venue","目标 Venue",false],
  ["polite_email","联系邮箱",false],["notes","备注",true],
];
const toData=(intake:Intake):IntakeData => ({
  repo_path:intake.repo_path || "",project_slug:intake.project_slug || "",project_name:intake.project_name || "",
  idea:intake.idea || "",domain:intake.domain || "",target_venue:intake.target_venue || "",polite_email:intake.polite_email || "",
  seed_papers:intake.seed_papers || [],constraints:intake.constraints || [],notes:intake.notes || "",
});
const lines=(value:string) => value.split("\n").map((item) => item.trim()).filter(Boolean);

export function IntakeWorkspace({data,onBack,onChanged}:{data:WorkspaceData;onBack:()=>void;onChanged:()=>Promise<void>}) {
  const [intake,setIntake]=useState(data.intake);
  const [draft,setDraft]=useState<IntakeData>(() => toData(data.intake));
  const [saving,setSaving]=useState(false);
  const [materializing,setMaterializing]=useState(false);
  const [error,setError]=useState("");
  const [result,setResult]=useState<{returncode?:number;stdout?:string;stderr?:string}|null>(null);
  useEffect(() => { setIntake(data.intake); setDraft(toData(data.intake)); },[data.intake]);
  const dirty=useMemo(() => JSON.stringify(draft)!==JSON.stringify(toData(intake)),[draft,intake]);

  const reload=async () => { const current=await loadIntake(data.project.path); setIntake(current); setDraft(toData(current)); return current; };
  const save=async () => {
    if (saving || materializing) return;
    setSaving(true); setError(""); setResult(null);
    try { const response=await updateV2Intake(data.project.path,intake._canonical_rev,draft); setIntake(response.intake); setDraft(toData(response.intake)); await onChanged(); }
    catch(reason) {
      if (reason instanceof ApiError && reason.reason==="content_hash_conflict") { setError("内容已被其他写入修改，请刷新后重试"); await reload(); }
      else setError(reason instanceof Error ? reason.message : String(reason));
    } finally { setSaving(false); }
  };
  const materialize=async () => {
    if (dirty || saving || materializing) return;
    if (!window.confirm("这将执行 materialize.py，根据已保存的 INTAKE.md 生成项目结构并推进 state。确认继续？")) return;
    setMaterializing(true); setError(""); setResult(null);
    try {
      const response=await materializeV2Intake(data.project.path,intake._canonical_rev);
      setResult(response.materialize); await onChanged(); await reload();
    } catch(reason) {
      if (reason instanceof ApiError && reason.reason==="content_hash_conflict") { setError("INTAKE.md 已被其他写入修改，请刷新后重试"); await reload(); }
      else setError(reason instanceof Error ? reason.message : String(reason));
    } finally { setMaterializing(false); }
  };

  return <div className="intake-workspace-page">
    <div className="intake-page-heading"><div><button className="back-button" onClick={onBack}><ArrowLeft size={15}/>研究总览</button><div className="eyebrow">Project Operator Workflow</div><h1>项目 Intake</h1><p>INTAKE.md 是输入 authority；保存与 materialize 副作用明确分离。</p></div><Settings size={24}/></div>
    {error && <div className="detail-error">{error}</div>}
    <div className="intake-layout">
      <section className="intake-form-panel"><div className="intake-panel-title"><div><FileText size={17}/><span><strong>Canonical Intake</strong><small>{intake._exists ? "INTAKE.md 已存在" : "尚未创建 INTAKE.md"}</small></span></div>{dirty && <b>有未保存修改</b>}</div>
        <div className="intake-form-grid">{scalarFields.map(([key,label,multiline]) => <label key={key}>{label}{multiline ? <textarea value={String(draft[key])} onChange={(event) => setDraft({...draft,[key]:event.target.value})}/> : <input value={String(draft[key])} onChange={(event) => setDraft({...draft,[key]:event.target.value})}/>}</label>)}
          <label>种子论文（每行一项）<textarea value={draft.seed_papers.join("\n")} onChange={(event) => setDraft({...draft,seed_papers:lines(event.target.value)})}/></label>
          <label>约束（每行一项）<textarea value={draft.constraints.join("\n")} onChange={(event) => setDraft({...draft,constraints:lines(event.target.value)})}/></label>
        </div>
        <div className="intake-actions"><button className="secondary-button" onClick={() => setDraft(toData(intake))} disabled={!dirty || saving || materializing}>撤销修改</button><button className="primary-button" onClick={() => void save()} disabled={!dirty || saving || materializing}><Save size={14}/>{saving ? "保存中…" : "仅保存"}</button></div>
      </section>
      <aside className="intake-materialize-panel"><div className="intake-side-icon"><Play size={18}/></div><h2>物化并继续</h2><p>只读取已经保存且 revision 匹配的 INTAKE.md，不会隐式保存当前表单。</p><div className="intake-safety"><ShieldQuestion size={16}/><span>{dirty ? "请先保存或撤销修改" : "当前表单与 canonical 一致"}</span></div><button className="primary-button" onClick={() => void materialize()} disabled={dirty || saving || materializing}>{materializing ? "执行中…" : "运行 materialize.py"}</button>
        {result && <div className={`intake-result ${result.returncode===0 ? "ok" : "failed"}`}><strong>{result.returncode===0 ? <><CheckCircle2 size={14}/>执行完成</> : `执行返回 ${result.returncode ?? "unknown"}`}</strong><label>stdout<pre>{result.stdout || "（空）"}</pre></label><label>stderr<pre>{result.stderr || "（空）"}</pre></label></div>}
      </aside>
    </div>
  </div>;
}

