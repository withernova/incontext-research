import type { StoredJob,StoredPaperCandidate } from "./api";

export type CandidateStatusFilter="all"|"active"|"failed"|"ready"|"ingested";
export function candidateStatus(candidate:StoredPaperCandidate,jobs:StoredJob[]):CandidateStatusFilter{
  if(candidate.verification_status==="ingested")return "ingested";
  if(jobs.some((job)=>job.status==="failed"))return "failed";
  const acquisition=jobs.find((job)=>["paper_download","zotero_copy"].includes(job.kind));const mineru=jobs.find((job)=>job.kind==="mineru");
  if(acquisition?.status==="succeeded"&&mineru?.status==="succeeded")return "ready";
  return "active";
}
export function filterCandidates(candidates:StoredPaperCandidate[],jobs:StoredJob[],query:string,status:CandidateStatusFilter){const needle=query.trim().toLocaleLowerCase();return candidates.filter((candidate)=>{const own=jobs.filter((job)=>job.target_object_id===candidate.id);if(status!=="all"&&candidateStatus(candidate,own)!==status)return false;return !needle||`${candidate.title||""} ${candidate.citekey||""} ${candidate.doi||""} ${candidate.source||""}`.toLocaleLowerCase().includes(needle)})}
export function candidateSourceLabel(candidate:StoredPaperCandidate){if(candidate.source?.startsWith("arxiv"))return "arXiv";if(candidate.source==="zotero-local")return "Zotero";if(candidate.source==="openalex")return "OpenAlex";return candidate.source||"未知来源"}
