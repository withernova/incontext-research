import { useState } from "react";
import type { Experiment } from "./types";
import { MarkdownContent } from "./MarkdownContent";

export function ExperimentHandoffPanel({experiment,saving,onConfirm}:{experiment:Experiment;saving:boolean;onConfirm:(proposal:Record<string,string>,answers:Record<string,string>)=>void}){
  const handoff=experiment.agent_handoff;
  const pending=experiment.workflow_stage==="awaiting_confirmation";
  const [proposal,setProposal]=useState<Record<string,string>>(()=>Object.fromEntries((["objective","implementation_scope","evaluation"] as const).map(key=>[key,String((pending?handoff?.proposal?.[key]:experiment[key])||handoff?.proposal?.[key]||"")])));
  const [answers,setAnswers]=useState<Record<string,string>>(()=>experiment.user_answers||{});
  if(!handoff)return pending?<section className="experiment-handoff"><h2>等待方案确认</h2><p>当前未找到已登记的 handoff。请让 Agent 使用 experiment handoff 命令登记，单独保存 JSON 文件不会提交方案。</p></section>:null;
  const valid=handoff.contract==="survey-tool.experiment-handoff/v1"&&handoff.experiment_id===experiment.id;
  const questions=handoff.questions||[];
  const ready=valid&&Object.values(proposal).every(value=>value.trim())&&questions.every(q=>answers[q.key]?.trim());
  return <section className="experiment-handoff" aria-label="实验方案确认">
    <header><h2>{pending?"待确认方案":"已提交的勘察方案"}</h2><span>{experiment.id} · {pending?"需要你确认":experiment.workflow_stage==="confirmed"?"已确认":"历史记录"}</span></header>
    {!valid&&<p role="alert">handoff 身份或格式不匹配，请让 Agent 重新提交。</p>}
    <details><summary>查看勘察事实与证据（{handoff.verified_facts?.length||0}）</summary>{(handoff.verified_facts||[]).map((fact,index)=><article key={index}><strong>{fact.label}</strong><MarkdownContent>{fact.value}</MarkdownContent><small>{fact.evidence}</small></article>)}</details>
    {[["objective","研究目标"],["implementation_scope","实现范围"],["evaluation","评估方式"]].map(([key,label])=><label key={key}>{label}<textarea value={proposal[key]} readOnly={!pending} disabled={saving} onChange={e=>setProposal(current=>({...current,[key]:e.target.value}))}/></label>)}
    {!!handoff.risks?.length&&<details open={pending}><summary>风险与局限</summary><ul>{handoff.risks.map((risk,index)=><li key={index}>{risk}</li>)}</ul></details>}
    {questions.map(q=><label key={q.key}>{q.label}<small>{q.why}</small>{q.suggested&&<small>Agent 建议：{q.suggested}</small>}<textarea value={answers[q.key]||""} readOnly={!pending} disabled={saving} onChange={e=>setAnswers(current=>({...current,[q.key]:e.target.value}))}/></label>)}
    {pending?<><p>{questions.length?"请填写上方问题的决定。":"没有额外待答问题，核对方案后可直接确认。"}确认后可继续规划和实现；Run 审核与执行授权仍独立处理。</p><button className="primary-button" disabled={saving||!ready} onClick={()=>onConfirm(proposal,Object.fromEntries(questions.map(q=>[q.key,answers[q.key]])))}>{saving?"保存中…":"确认方案，继续准备 Run"}</button></>:<p>该方案已提交。当前阶段：{experiment.workflow_stage}；本面板不会启动实验。</p>}
  </section>;
}
