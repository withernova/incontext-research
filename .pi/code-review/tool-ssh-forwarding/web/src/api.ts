import type {
  Capabilities,
  Comparison,
  ComparisonFinding,
  ExperimentDashboard,
  Experiment,
  Run,
  Idea,
  Intake,
  ExplorationRegistry,
  Paper,
  PaperBundle,
  PaperCandidate,
  PaperSearchResult,
  Project,
  Question,
  WorkspaceData,
  EnvironmentBindings,
  ExperimentServer,
  ExperimentWorkspaceBinding,
  ZoteroCollection,
  ZoteroItem,
  AgentRouting,
  AgentRoutingConfig,
} from "./types";
import { discussionPreviewPayload } from "./aiDiscussionModel";

async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(path, { headers: { Accept: "application/json" }, ...(signal ? { signal } : {}) });
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const payload = (await response.json()) as { error?: string; path?: string };
      detail = payload.error || detail;
    } catch {
      // Keep the HTTP detail when the body is not JSON.
    }
    throw new ApiError(`${detail}（GET ${path}）`, response.status);
  }
  return (await response.json()) as T;
}

export class ApiError extends Error {
  status: number;
  reason?: string;

  constructor(message: string, status: number, reason?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.reason = reason;
  }
}

async function mutation<T>(path: string, method: "POST" | "PUT" | "DELETE", body: object): Promise<T> {
  const response = await fetch(path, {
    method,
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  const payload = await response.json() as { error?: string; reason?: string; path?: string };
  if (!response.ok) throw new ApiError(`${payload.error || `${response.status} ${response.statusText}`}（${method} ${path}）`, response.status, payload.reason);
  return payload as T;
}

export type ExperimentDocument = {path:string;title:string;kind:"core"|"run"|"topic";modified:string;generated:boolean;topic:string;status:string;superseded_by:string};
export type ExperimentDocumentList = {experiment_id:string;read_only:true;root:string;documents:ExperimentDocument[];directories:string[];total:number;indexed_count:number;warnings:string[];recency_note:string};
export type ExperimentDocumentContent = {experiment_id:string;read_only:true;path:string;project_relative_path:string;title:string;content:string};
export type ExperimentDocumentFilters = {q?:string;directory?:string;kind?:string;sort?:string;status?:string};
const experimentDocumentsPath=(projectPath:string,experimentId:string)=>`/api/v2/p/${encodeURIComponent(projectPath)}/experiments/${encodeURIComponent(experimentId)}/documents`;
export function loadExperimentDocuments(projectPath:string,experimentId:string,filters:ExperimentDocumentFilters={},signal?:AbortSignal){
  const query=new URLSearchParams(Object.entries(filters).filter(([,value])=>value!==undefined) as Array<[string,string]>);
  return request<ExperimentDocumentList>(`${experimentDocumentsPath(projectPath,experimentId)}?${query}`,signal);
}
export function loadExperimentDocument(projectPath:string,experimentId:string,path:string,signal?:AbortSignal){
  return request<ExperimentDocumentContent>(`${experimentDocumentsPath(projectPath,experimentId)}/content?${new URLSearchParams({path})}`,signal);
}
export function refreshExperimentDocuments(projectPath:string,experimentId:string){
  return mutation<{experiment_id:string;writes:true;paths:string[]}>(`${experimentDocumentsPath(projectPath,experimentId)}/refresh`,"POST",{confirmation:`REFRESH EXPERIMENT DOCUMENTS ${experimentId}`});
}

export async function listProjects(): Promise<Project[]> {
  return request<Project[]>("/api/projects");
}

export async function loadPaperBundle(projectPath: string, citekey: string): Promise<PaperBundle> {
  return request<PaperBundle>(`/api/p/${encodeURIComponent(projectPath)}/paper/${encodeURIComponent(citekey)}`);
}

export async function updateV2Paper(
  projectPath: string,
  citekey: string,
  expectedHash: string,
  fields: { seven?: PaperBundle["seven"]; annotations?: PaperBundle["annotations"]; state?: Record<string, unknown> },
): Promise<{ paper: PaperBundle; authority: string; indexed: boolean }> {
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/papers/${encodeURIComponent(citekey)}`, "PUT", {
    confirmation: "UPDATE V2 PAPER", expected_hash: expectedHash, ...fields,
  });
}

export type SevenImportPreview = {
  answers: Record<string, string>;
  meta: Record<string, string>;
  parsed_count: number;
  missing: string[];
  warnings: string[];
};

export async function previewSevenQuestionImport(projectPath: string, citekey: string, text: string): Promise<SevenImportPreview> {
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/papers/${encodeURIComponent(citekey)}/seven/import-preview`, "POST", { text });
}

export async function loadQuestions(projectPath: string): Promise<Question[]> {
  return request<Question[]>(`/api/p/${encodeURIComponent(projectPath)}/questions`);
}

export type QuestionRelationMutation={question:Question;relation?:V2Relation;removed_relation?:V2Relation;authority:"question_frontmatter"|"v2_navigation_index";canonical_question_modified:boolean;indexed:boolean};
export async function addV2QuestionRelation(projectPath:string,question:Question,targetId:string):Promise<QuestionRelationMutation>{return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/questions/${encodeURIComponent(question.id)}/relations`,"POST",{confirmation:"ADD V2 QUESTION RELATION",expected_hash:question._canonical_rev||"",target_id:targetId})}
export async function removeV2QuestionRelation(projectPath:string,question:Question,relationId:string):Promise<QuestionRelationMutation>{return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/questions/${encodeURIComponent(question.id)}/relations/${encodeURIComponent(relationId)}`,"DELETE",{confirmation:"REMOVE V2 QUESTION RELATION",expected_hash:question._canonical_rev||""})}

export async function loadIdeas(projectPath: string): Promise<Idea[]> {
  return request<Idea[]>(`/api/p/${encodeURIComponent(projectPath)}/ideas`);
}

export async function loadIntake(projectPath: string): Promise<Intake> {
  return request<Intake>(`/api/p/${encodeURIComponent(projectPath)}/intake`);
}

export async function updateV2Intake(projectPath: string, expectedHash: string, data: Omit<Intake, "_canonical_rev" | "_exists">): Promise<{ intake: Intake; authority: string }> {
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/intake`, "PUT", { confirmation: "UPDATE V2 INTAKE", expected_hash: expectedHash, data });
}

export async function materializeV2Intake(projectPath: string, expectedHash: string): Promise<{ materialize: { returncode?: number; stdout?: string; stderr?: string; [key: string]: unknown }; state: unknown; authority: string }> {
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/intake/materialize`, "POST", { confirmation: "MATERIALIZE V2 INTAKE", expected_hash: expectedHash });
}

type ExperimentMutation = { experiment: Experiment; dashboard: ExperimentDashboard };
type RunMutation = { run: Run; dashboard: ExperimentDashboard };

export async function createV2Experiment(projectPath: string, experiment: Partial<Experiment>): Promise<ExperimentMutation> {
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/experiments`, "POST", { confirmation: "CREATE V2 EXPERIMENT", experiment });
}
export async function confirmExperimentHandoff(projectPath:string, experiment:Experiment, proposal:Record<string,string>, answers:Record<string,string>):Promise<ExperimentMutation>{
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/experiments/${experiment.id}/handoff/confirm`,"POST",{confirmation:"CONFIRM EXPERIMENT HANDOFF",expected_updated:experiment.updated||"",expected_handoff:experiment.agent_handoff,proposal,answers});
}
export async function updateV2Experiment(projectPath: string, experimentId: string, expectedUpdated: string, fields: Partial<Experiment>): Promise<ExperimentMutation> {
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/experiments/${encodeURIComponent(experimentId)}`, "PUT", { confirmation: "UPDATE V2 EXPERIMENT", expected_updated: expectedUpdated, fields });
}
export async function archiveV2Experiment(projectPath:string,experiment:Experiment,reason:string,restore=false):Promise<ExperimentMutation&{archived:boolean;authority:string}>{
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/experiments/${encodeURIComponent(experiment.id)}/archive`,"POST",{confirmation:`${restore?"RESTORE":"ARCHIVE"} V2 EXPERIMENT ${experiment.id}`,expected_updated:experiment.updated||"",reason,restore});
}
export async function createV2Run(projectPath: string, experimentId: string, run: Partial<Run>): Promise<RunMutation> {
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/experiments/${encodeURIComponent(experimentId)}/runs`, "POST", { confirmation: "CREATE V2 RUN", run });
}
export async function updateV2Run(projectPath: string, runId: string, expectedUpdated: string, fields: Partial<Run>): Promise<RunMutation> {
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/runs/${encodeURIComponent(runId)}`, "PUT", { confirmation: "UPDATE V2 RUN", expected_updated: expectedUpdated, fields });
}
export async function archiveV2Run(projectPath:string,run:Run,reason:string,restore=false):Promise<RunMutation&{archived:boolean;authority:string}>{
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/runs/${encodeURIComponent(run.id)}/archive`,"POST",{confirmation:`${restore?"RESTORE":"ARCHIVE"} V2 RUN ${run.id}`,expected_updated:run.updated||"",reason,restore});
}
export async function setV2RunEvidenceLabel(projectPath:string,run:Run,label:"solid"|"",note=""):Promise<RunMutation&{evidence_label:string;authority:string;claim_verdict_changed:false}>{
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/runs/${encodeURIComponent(run.id)}/evidence-label`,"POST",{confirmation:`SET V2 RUN EVIDENCE LABEL ${run.id}`,expected_updated:run.updated||"",label,note});
}
export type RunTrialPreparation = {request:string;planning_mode:"matrix"|"ai_planned";axes?:Array<{name:string;values:Array<string|number|boolean>}>;trial_budget?:number;concurrency:number;max_retries:number};
export async function prepareV2RunTrials(projectPath:string,run:Run,input:RunTrialPreparation):Promise<RunMutation&{trial_plan:NonNullable<Run["trial_plan"]>;handoff_command:string;trial_plan_fingerprint:string;trial_planning_mode:string;trial_budget:number;execution_started:false;herdr_invoked:false}> {
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/runs/${encodeURIComponent(run.id)}/trials/prepare-steward`,"POST",{confirmation:"PREPARE V2 RUN TRIALS",expected_updated:run.updated||"",...input});
}
export type RunReviewAction = "submit" | "request_changes" | "approve" | "authorize_execution";
const reviewConfirmations: Record<RunReviewAction,string> = { submit:"SUBMIT V2 RUN REVIEW",request_changes:"REQUEST V2 RUN CHANGES",approve:"APPROVE V2 RUN",authorize_execution:"AUTHORIZE V2 RUN EXECUTION" };
export async function reviewV2Run(projectPath: string, run: Run, action: RunReviewAction, details: { requirements?: string; questions?: string; authorization_note?: string } = {}): Promise<RunMutation> {
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/runs/${encodeURIComponent(run.id)}/review`, "POST", { action,confirmation:reviewConfirmations[action],expected_updated:run.updated || "",...details });
}
export type RunWorkflowAction = "confirm-design" | "implementation-ready" | "reopen-design" | "begin-analysis" | "finalize-results" | "mark-failed";
const workflowConfirmations: Record<RunWorkflowAction,string> = {"confirm-design":"CONFIRM V2 RUN DESIGN","implementation-ready":"MARK V2 RUN IMPLEMENTATION READY","reopen-design":"REOPEN V2 RUN DESIGN","begin-analysis":"BEGIN V2 RUN ANALYSIS","finalize-results":"FINALIZE V2 RUN RESULTS","mark-failed":"MARK V2 RUN FAILED"};
export async function transitionV2RunWorkflow(projectPath: string, run: Run, action: RunWorkflowAction, resultFields: Partial<Run> = {}): Promise<RunMutation> {
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/runs/${encodeURIComponent(run.id)}/workflow`, "POST", {action,confirmation:workflowConfirmations[action],expected_updated:run.updated || "",result_fields:resultFields});
}
export async function loadV2RunSteward(projectPath:string,runId:string):Promise<import("./types").StewardStatus>{
  return request(`/api/v2/p/${encodeURIComponent(projectPath)}/runs/${encodeURIComponent(runId)}/steward`);
}
export async function loadV2Stewards(projectPath:string):Promise<import("./types").StewardStatusList>{
  return request(`/api/v2/p/${encodeURIComponent(projectPath)}/stewards`);
}
export async function loadV2StewardConsole(projectPath:string,runId:string):Promise<import("./types").StewardConsole>{
  return request(`/api/v2/p/${encodeURIComponent(projectPath)}/runs/${encodeURIComponent(runId)}/steward/console`);
}
export async function startV2RunSteward(projectPath:string,run:Run):Promise<import("./types").StewardStatus&{handoff_command:string;execution_started:false;herdr_invoked:false;dashboard:ExperimentDashboard}>{
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/runs/${encodeURIComponent(run.id)}/steward/start`,"POST",{confirmation:"PREPARE V2 RUN STEWARD",expected_updated:run.updated||""});
}
export async function restartV2FailedRunSteward(projectPath:string,run:Run,executionMode:"single"|"preserve"="single"):Promise<{run:Run;handoff_command:string;execution_started:false;herdr_invoked:false;dashboard:ExperimentDashboard;execution_mode:"single"|"preserve";cancelled_campaign_id?:string}>{
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/runs/${encodeURIComponent(run.id)}/steward/restart`,"POST",{confirmation:"RESTART V2 FAILED RUN",expected_updated:run.updated||"",execution_mode:executionMode});
}
export async function forceRestartV2RunSteward(projectPath:string,run:Run):Promise<{handoff_command:string;execution_started:false;execution_restarted:false;herdr_invoked:false;dashboard:ExperimentDashboard}>{
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/runs/${encodeURIComponent(run.id)}/steward/force-restart`,"POST",{confirmation:"FORCE RESTART V2 RUN STEWARD",expected_updated:run.updated||""});
}
export async function markV2StewardAttemptFailed(projectPath:string,run:Run,reason:string):Promise<RunMutation&{dispatch:import("./types").Dispatch;execution_stopped:false;remote_process_changed:false}>{
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/runs/${encodeURIComponent(run.id)}/steward/mark-failed`,"POST",{confirmation:"MARK V2 STEWARD ATTEMPT FAILED",expected_updated:run.updated||"",reason});
}
export async function correctV2FailedRunStatus(projectPath:string,run:Run,targetStage:"running"|"analysis_pending",reason:string,evidence:string):Promise<RunMutation&{dispatch:import("./types").Dispatch;execution_started:false;execution_stopped:false;remote_process_changed:false;requires_reattach:boolean}>{
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/runs/${encodeURIComponent(run.id)}/steward/correct-failed`,"POST",{confirmation:"CORRECT V2 FAILED RUN STATUS",expected_updated:run.updated||"",target_stage:targetStage,reason,evidence});
}
export async function updateV2RunGrouping(projectPath: string, experiment: Experiment, groups: NonNullable<Experiment["run_groups"]>, assignments: Record<string,string>): Promise<ExperimentMutation> {
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/experiments/${encodeURIComponent(experiment.id)}/run-grouping`, "PUT", { confirmation:"UPDATE V2 RUN GROUPING",expected_updated:experiment.updated || "",groups,assignments });
}
export type AiRunGroupingResult={experiment:Experiment;dashboard:ExperimentDashboard;grouping_result:{applied:Array<{run_id:string;from:string;to:string}>;skipped:Array<{run_id:string;reason:string;detail:string}>;unchanged:Array<{run_id:string;group_id:string}>;groups_added:NonNullable<Experiment["run_groups"]>;totals:Record<string,number>}};
export async function previewAiRunGroupingPrompt(projectPath:string,experimentId:string):Promise<{prompt:string;contract:string;read_only:true;bridge:{live_bound:boolean;isStreaming:boolean}}>{return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/experiments/${encodeURIComponent(experimentId)}/run-grouping/ai-prompt-preview`,"POST",{})}
export async function applyAiRunGrouping(projectPath:string,experiment:Experiment,groups:NonNullable<Experiment["run_groups"]>,assignments:Record<string,string>):Promise<AiRunGroupingResult>{return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/experiments/${encodeURIComponent(experiment.id)}/run-grouping/ai-apply`,"PUT",{confirmation:"APPLY V2 AI RUN GROUPING",expected_updated:experiment.updated||"",groups,assignments})}
export async function loadEnvironmentBindings(projectPath:string):Promise<EnvironmentBindings>{return request(`/api/v2/p/${encodeURIComponent(projectPath)}/environment-bindings`)}
export async function loadAgentRouting(projectPath:string):Promise<AgentRoutingConfig>{return request(`/api/v2/p/${encodeURIComponent(projectPath)}/agent-routing`)}
export async function updateV2AgentRouting(projectPath:string,routing:AgentRouting):Promise<AgentRoutingConfig>{return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/agent-routing`,"PUT",{confirmation:"UPDATE V2 AGENT ROUTING",routing})}
export async function updateV2Server(projectPath:string,id:string,expectedHash:string,fields:Partial<ExperimentServer>):Promise<EnvironmentBindings&{server:ExperimentServer}>{return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/servers/${encodeURIComponent(id)}`,"PUT",{confirmation:"UPDATE V2 SERVER",expected_hash:expectedHash,fields})}
export async function updateV2WorkspaceBinding(projectPath:string,id:string,expectedHash:string,fields:Partial<ExperimentWorkspaceBinding>):Promise<EnvironmentBindings&{workspace:ExperimentWorkspaceBinding}>{return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/workspaces/${encodeURIComponent(id)}`,"PUT",{confirmation:"UPDATE V2 WORKSPACE",expected_hash:expectedHash,fields})}
export async function previewWorkspaceRuleDraft(projectPath:string,preset:import("./types").WorkspaceRulePreset,requestText:string,draft:Partial<ExperimentWorkspaceBinding>):Promise<import("./types").RuleDraftPreview>{return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/rule-drafts/preview`,"POST",{scope:"workspace",preset,request:requestText,draft,organizer:"ai_auto"})}
export async function workspaceExternalRulePrompt(projectPath:string,requestText:string,draft:Partial<ExperimentWorkspaceBinding>):Promise<{prompt:string;read_only:true;contract:string}>{return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/rule-drafts/external-prompt`,"POST",{request:requestText,draft})}
export async function previewExternalWorkspaceRules(projectPath:string,preset:import("./types").WorkspaceRulePreset,requestText:string,draft:Partial<ExperimentWorkspaceBinding>,response:string):Promise<import("./types").RuleDraftPreview>{return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/rule-drafts/external-preview`,"POST",{preset,request:requestText,draft,response})}
export async function loadZoteroCollections(projectPath:string):Promise<{ok:boolean;collections:ZoteroCollection[];error?:string}>{return request(`/api/v2/p/${encodeURIComponent(projectPath)}/zotero/collections`)}
export async function loadZoteroItems(projectPath:string,collectionId:number):Promise<{ok:boolean;items:ZoteroItem[];error?:string}>{return request(`/api/v2/p/${encodeURIComponent(projectPath)}/zotero/collections/${collectionId}/items`)}
export async function stageZoteroCandidate(projectPath:string,id:number):Promise<{candidate:StoredPaperCandidate;preview:ZoteroItem;canonical_write:false;local_path_exposed:false}>{return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/zotero/items/${id}/stage`,"POST",{confirmation:"STAGE ZOTERO PAPER CANDIDATE"})}

export type PublishState = { githubUrl?: string; commitSha?: string; publishedAt?: string; name?: string };
export type DiscussionMode = "terminal_pi" | "external_gpt";
export type DiscussionTargetType = "experiment" | "run" | "question" | "paper" | "paper_candidate";
export type DiscussionTask = "question" | "review" | "counter" | "compare" | "rewrite" | "experiment" | "code_edit" | "run_implementation";
export type DiscussionFocus = "whole" | "seven" | "method" | "evidence" | "limitations" | "relevance" | "question" | "original" | "judgement" | "investigation" | "relations";
export type DiscussionPreview = { prompt: string; instruction?: string; publish?: PublishState; repository?: string; commitSha?: string; context_mode?:"code_repository_only"; code_repository?:{workspace_id:string;url:string;ref:string}; bridge?: { live_bound?: boolean; persisted_bound?: boolean; isStreaming?: boolean }; read_only: boolean };
export async function loadV2Publish(projectPath:string):Promise<PublishState>{return request(`/api/v2/p/${encodeURIComponent(projectPath)}/publish`)}
export async function syncV2Publish(projectPath:string,setup?:{repo_name?:string;visibility?:"private"|"public";include_pdfs?:boolean;include_mineru?:boolean;include_tool_state?:boolean}):Promise<{publish:PublishState;ok?:boolean;error?:string}>{return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/publish/sync`,"POST",{confirmation:"SYNC V2 PROJECT TO GITHUB",setup:setup||{}})}
export async function previewV2Discussion(projectPath:string,targetType:DiscussionTargetType,targetId:string,mode:DiscussionMode,task:DiscussionTask,requestText:string,focus:DiscussionFocus="whole",referenceIds:string[]=[],discussionSummary="",codeRepositoryId=""):Promise<DiscussionPreview>{return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/ai/discussion-prompt-preview`,"POST",discussionPreviewPayload(targetType,targetId,mode,task,requestText,focus,referenceIds,discussionSummary,codeRepositoryId))}
export async function createV2Idea(projectPath: string, idea: Partial<Idea>): Promise<{ idea: Idea; authority: string; indexed: boolean }> {
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/ideas`, "POST", { confirmation: "CREATE V2 IDEA", idea });
}

export async function updateV2Idea(projectPath: string, ideaId: string, expectedHash: string, fields: Partial<Idea>): Promise<{ idea: Idea; authority: string; indexed: boolean }> {
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/ideas/${encodeURIComponent(ideaId)}`, "PUT", { confirmation: "UPDATE V2 IDEA", expected_hash: expectedHash, fields });
}

export async function loadComparisons(projectPath: string): Promise<Comparison[]> {
  return request<Comparison[]>(`/api/p/${encodeURIComponent(projectPath)}/compares`);
}

type ComparisonResult = { comparison: Comparison; authority: string; indexed: boolean };
type FindingResult = { finding: ComparisonFinding; comparison_id?: string; authority: string; indexed: boolean };

export async function createV2Comparison(projectPath: string, comparison: Partial<Comparison>): Promise<ComparisonResult> {
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/comparisons`, "POST", { confirmation: "CREATE V2 COMPARISON", comparison });
}

export async function updateV2Comparison(projectPath: string, comparisonId: string, expectedHash: string, fields: Partial<Comparison>): Promise<ComparisonResult> {
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/comparisons/${encodeURIComponent(comparisonId)}`, "PUT", { confirmation: "UPDATE V2 COMPARISON", expected_hash: expectedHash, fields });
}

export async function createV2Finding(projectPath: string, comparisonId: string, finding: { text: string; source?: string }): Promise<FindingResult> {
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/comparisons/${encodeURIComponent(comparisonId)}/findings`, "POST", { confirmation: "CREATE V2 FINDING", finding });
}

export async function updateV2Finding(projectPath: string, findingId: string, expectedHash: string, fields: { text?: string; source?: string }): Promise<FindingResult> {
  return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/findings/${encodeURIComponent(findingId)}`, "PUT", { confirmation: "UPDATE V2 FINDING", expected_hash: expectedHash, fields });
}

export async function createV2Question(projectPath: string, question: Partial<Question>): Promise<{ question: Question; authority: string; indexed: boolean }> {
  const response = await fetch(`/api/v2/p/${encodeURIComponent(projectPath)}/questions`, {
    method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ confirmation: "CREATE V2 QUESTION", question }),
  });
  const payload = await response.json() as { error?: string };
  if (!response.ok) throw new Error(payload.error);
  return payload as { question: Question; authority: string; indexed: boolean };
}

export async function updateV2Question(projectPath: string, questionId: string, expectedHash: string, fields: Partial<Question>): Promise<{ question: Question; authority: string; indexed: boolean }> {
  const response = await fetch(`/api/v2/p/${encodeURIComponent(projectPath)}/questions/${encodeURIComponent(questionId)}`, {
    method: "PUT", headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ confirmation: "UPDATE V2 QUESTION", expected_hash: expectedHash, fields }),
  });
  const payload = await response.json() as { error?: string };
  if (!response.ok) throw new Error(payload.error);
  return payload as { question: Question; authority: string; indexed: boolean };
}

export async function searchPapers(projectPath: string, query: string): Promise<PaperSearchResult> {
  return request<PaperSearchResult>(`/api/p/${encodeURIComponent(projectPath)}/papers/web-search?q=${encodeURIComponent(query)}`);
}
export async function searchArxivPapers(projectPath:string,query:string):Promise<PaperSearchResult>{return request(`/api/v2/p/${encodeURIComponent(projectPath)}/papers/arxiv-search?q=${encodeURIComponent(query)}`)}

export async function initializeV2Store(projectPath: string): Promise<{ initialized: boolean; schema_version: number }> {
  const response = await fetch(`/api/v2/p/${encodeURIComponent(projectPath)}/initialize`, {
    method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ confirmation: "INITIALIZE SURVEY TOOL 2.0" }),
  });
  if (!response.ok) throw new Error(((await response.json()) as { error?: string }).error || "初始化失败");
  return response.json();
}

export interface StoredPaperCandidate { id:string;type?:"paper_candidate";project_id?:string;citekey?:string;title?:string;authors?:string[];year?:string;doi?:string;source_url?:string;oa_url?:string;source?:string;recommendation_reason?:string;revision:number;lifecycle_status:string;verification_status?:string;acquisition_job_id?:string;canonical_paper_path?:string;content_hash?:string;ingested_at?:string|null;created_at?:string;updated_at?:string; }
export interface StoredJob { id: string; kind: string; status: string; revision: number; target_object_id?: string; depends_on_job_id?: string; error_class?: string; error_message?: string; progress?: number; attempt?: number; created_at?: string; started_at?: string; finished_at?: string; timeout_seconds?: number; lease_owner?: string; lease_expires_at?: string; last_heartbeat_at?: string; result?: Record<string, unknown>; }

export interface AgentSessionIndex { id: string; provider: string; status: string; object_id: string; task_type: string; identity_fingerprint: string; agent?: string; model?: string; created_at: string; last_seen_at?: string; revision: number; }
export interface CurrentPiSummary { available: boolean; status: string; session_name: string; last_verified_at: string; identity_fingerprint: string; messages_exposed: boolean; prompt_exposed: boolean; session_path_exposed: boolean; }
export interface AgentSessionRegistry { initialized: boolean; sessions: AgentSessionIndex[]; current_pi: CurrentPiSummary; }
export interface ArchiveImpact { id: string; type: string; title: string; lifecycle_status: string; revision: number; jobs: Record<string, number>; relations: number; agent_sessions: number; blockers: string[]; hard_delete: boolean; canonical_files_deleted: boolean; staging_deleted: boolean; }
export interface ArchivableObject { id: string; type: string; title: string; lifecycle_status: string; revision: number; impact: ArchiveImpact; }
export interface StoredEvent { id: string; kind: string; summary: string; occurred_at: string; from_revision?: number; to_revision?: number; }
export interface StoredAutomation { id: string; title?: string; revision: number; lifecycle_status: string; automation_type: string; phase: string; budget: Record<string, unknown>; approval: Record<string, unknown>; started_at?: string; deadline_at?: string; stopped_at?: string; events?: StoredEvent[]; }
export type HerdrTaskType = "discussion" | "research" | "implementation" | "run_implementation" | "monitoring" | "analysis";
export type HerdrReasoningEffort = "low" | "medium" | "high" | "xhigh";
export type HerdrTopology = "new_tab" | "split";
export interface HerdrLaunchRequest { id: string; lifecycle_status: "draft" | "awaiting_approval" | "approved" | "cancelled"; revision: number; target_object_id: string; agent_kind: "pi" | "codex"; task_type: HerdrTaskType; task_summary: string; safe_config: { reasoning_effort: HerdrReasoningEffort; max_turns: number; topology?: HerdrTopology; reference_ids?:string[] }; approved_at?: string | null; created_at: string; updated_at: string; events?: StoredEvent[]; }
export interface HerdrLaunchRequestDraft { target_object_id: string; agent_kind: "pi" | "codex"; task_type: HerdrTaskType; task_summary: string; safe_config: { reasoning_effort: HerdrReasoningEffort; max_turns: number; topology?: HerdrTopology; reference_ids?:string[] }; }
export interface HerdrExecution { id:string;state:string;revision:number;target_object_id:string;launch_request_id:string;approved_request_revision:number;not_after:string;attempt:number;safe_runtime?:Record<string,unknown>;authorized_at?:string;created_at?:string;updated_at?:string;events?:StoredEvent[]; }

async function postV2<T>(path: string, body: Record<string, unknown>): Promise<T> {
  const response = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(body) });
  const payload = await response.json() as { error?: string };
  if (!response.ok) throw new Error(payload.error || "操作失败");
  return payload as T;
}

export async function loadArchivableObjects(projectPath: string): Promise<{ initialized: boolean; objects: ArchivableObject[]; hard_delete_available?: boolean }> {
  return request(`/api/v2/p/${encodeURIComponent(projectPath)}/objects/archive`);
}

export async function setObjectsArchived(projectPath: string, objects: ArchivableObject[], reason: string, restore = false): Promise<{ objects: Array<{ id: string; type: string; lifecycle_status: string; revision: number }>; hard_delete: boolean; canonical_files_deleted: boolean }> {
  return postV2(`/api/v2/p/${encodeURIComponent(projectPath)}/objects/archive`, { confirmation: restore ? "RESTORE V2 OBJECTS" : "ARCHIVE V2 OBJECTS", items: objects.map((item) => ({ id: item.id, expected_revision: item.revision })), reason, restore });
}

export async function loadAgentSessions(projectPath: string): Promise<AgentSessionRegistry> {
  return request(`/api/v2/p/${encodeURIComponent(projectPath)}/agent-sessions`);
}

export async function bindCurrentPiSession(projectPath: string, objectId: string, taskType: string): Promise<{ session: AgentSessionIndex; target: { id: string; type: string; authority: string; reference_identity_only: boolean }; messages_copied: boolean; prompt_copied: boolean; session_path_copied: boolean }> {
  return postV2(`/api/v2/p/${encodeURIComponent(projectPath)}/agent-sessions/bind-current-pi`, { confirmation: "BIND CURRENT PI SESSION", object_id: objectId, task_type: taskType });
}

export async function loadAutomations(projectPath: string): Promise<{ initialized: boolean; automations: StoredAutomation[] }> {
  return request(`/api/v2/p/${encodeURIComponent(projectPath)}/automations`);
}

export async function createAutomationDraft(projectPath: string, automation: Record<string, unknown>): Promise<{ automation: StoredAutomation; started: boolean }> {
  return postV2(`/api/v2/p/${encodeURIComponent(projectPath)}/automations`, { confirmation: "CREATE AUTOMATION DRAFT", automation });
}

export async function transitionAutomation(projectPath: string, automation: StoredAutomation, status: string, phase?: string, approveExperimentPhase = false): Promise<{ automation: StoredAutomation; execution_started: boolean }> {
  const confirmations: Record<string, string> = { awaiting_approval: "SUBMIT AUTOMATION FOR APPROVAL", active: "APPROVE AUTOMATION", checkpoint: "CHECKPOINT AUTOMATION", paused: "PAUSE AUTOMATION", completed: "COMPLETE AUTOMATION", completed_with_warnings: "COMPLETE AUTOMATION WITH WARNINGS", failed: "FAIL AUTOMATION", cancelled: "CANCEL AUTOMATION" };
  return postV2(`/api/v2/p/${encodeURIComponent(projectPath)}/automations/${encodeURIComponent(automation.id)}/transition`, { confirmation: confirmations[status], expected_revision: automation.revision, status, phase, approve_experiment_phase: approveExperimentPhase });
}

export async function loadHerdrLaunchRequests(projectPath: string): Promise<{ initialized: boolean; launch_requests: HerdrLaunchRequest[]; execution_available?: boolean }> {
  return request(`/api/v2/p/${encodeURIComponent(projectPath)}/herdr-launch-requests`);
}

export async function createHerdrLaunchRequestDraft(projectPath: string, launchRequest: HerdrLaunchRequestDraft): Promise<{ launch_request: HerdrLaunchRequest; execution_started: false; prompt_stored: false; command_stored: false }> {
  return postV2(`/api/v2/p/${encodeURIComponent(projectPath)}/herdr-launch-requests`, { confirmation: "CREATE HERDR LAUNCH REQUEST DRAFT", launch_request: launchRequest });
}

export async function transitionHerdrLaunchRequest(projectPath: string, launchRequest: HerdrLaunchRequest, status: "awaiting_approval" | "approved" | "cancelled"): Promise<{ launch_request: HerdrLaunchRequest; execution_started: false; herdr_invoked: false }> {
  const confirmations = { awaiting_approval: "SUBMIT HERDR LAUNCH REQUEST FOR APPROVAL", approved: "APPROVE HERDR LAUNCH REQUEST", cancelled: "CANCEL HERDR LAUNCH REQUEST" } as const;
  return postV2(`/api/v2/p/${encodeURIComponent(projectPath)}/herdr-launch-requests/${encodeURIComponent(launchRequest.id)}/transition`, { confirmation: confirmations[status], expected_revision: launchRequest.revision, status });
}

export async function authorizeHerdrLaunchRequest(projectPath:string,launchRequest:HerdrLaunchRequest,ttlSeconds=300):Promise<{execution:HerdrExecution;execution_started:false;herdr_invoked:false}>{
  return postV2(`/api/v2/p/${encodeURIComponent(projectPath)}/herdr-launch-requests/${encodeURIComponent(launchRequest.id)}/authorize`,{confirmation:`AUTHORIZE HERDR EXECUTION ${launchRequest.id}`,expected_request_revision:launchRequest.revision,ttl_seconds:ttlSeconds});
}

export interface IdentityIndexPlan { will_write: boolean; blocked: boolean; summary: { questions: number; experiments: number; relations: number; warnings: number }; warnings: Array<{ kind: string; path: string; message: string }>; authority: { question: string; experiment: string; sqlite: string }; }
export interface IdentityIndexCheckpoint { checkpoint_hash: string; status: string; applied_at: string; details: { created?: number; existing?: number; relations_created?: number; authority_changed?: boolean; record_error?: string }; }
export interface ContentIndexPlan { will_write: boolean; blocked: boolean; summary: { papers: number; comparisons: number; findings: number; claims: number; relations: number; warnings: number }; warnings: Array<{ kind: string; path: string; message: string }>; authority: { paper: string; comparison: string; finding: string; claim: string; sqlite: string }; }
export interface ContentIndexCheckpoint { checkpoint_hash: string; status: string; applied_at: string; details: { created?: number; existing?: number; relations_created?: number; authority_changed?: boolean; record_error?: string }; }
export interface MigrationInventory { will_write: boolean; summary: { source_groups: number; existing_groups: number; source_files: number; paper_pdfs: number; warnings: number }; warnings: Array<{ kind: string; path: string; message: string }>; excluded: string[]; v2_store: { initialized: boolean; schema_version: number }; identity_index_plan: IdentityIndexPlan; identity_index_history: IdentityIndexCheckpoint[]; content_index_plan: ContentIndexPlan; content_index_history: ContentIndexCheckpoint[]; }

export async function loadMigrationDryRun(projectPath: string): Promise<MigrationInventory> {
  return request(`/api/v2/p/${encodeURIComponent(projectPath)}/migration/dry-run`);
}

export async function applyIdentityIndexMigration(projectPath: string): Promise<{ status: string; created: number; existing: number; relations_created: number; authority_changed: boolean; prose_copied: boolean; canonical_files_modified: boolean; checkpoint_hash: string }> {
  return postV2(`/api/v2/p/${encodeURIComponent(projectPath)}/migration/identity-index/apply`, { confirmation: "APPLY IDENTITY INDEX MIGRATION" });
}

export async function applyContentIndexMigration(projectPath: string): Promise<{ status: string; created: number; existing: number; relations_created: number; authority_changed: boolean; prose_copied: boolean; canonical_files_modified: boolean; checkpoint_hash: string }> {
  return postV2(`/api/v2/p/${encodeURIComponent(projectPath)}/migration/content-index/apply`, { confirmation: "APPLY CONTENT INDEX MIGRATION" });
}

export async function loadCandidateRegistry(projectPath: string): Promise<{ initialized: boolean; candidates: StoredPaperCandidate[] }> {
  return request(`/api/v2/p/${encodeURIComponent(projectPath)}/paper-candidates`);
}

export async function loadV2Jobs(projectPath: string): Promise<{ initialized: boolean; jobs: StoredJob[] }> {
  return request(`/api/v2/p/${encodeURIComponent(projectPath)}/jobs`);
}
export async function runLocalPaperWorker(projectPath:string,targetObjectId="",maxJobs=2):Promise<{worker_started:boolean;already_running:boolean;worker_id:string}>{return mutation(`/api/v2/p/${encodeURIComponent(projectPath)}/jobs/run-local`,"POST",{confirmation:"RUN LOCAL PAPER WORKER",target_object_id:targetObjectId,max_jobs:maxJobs})}

export type V2Object = { id: string; type: string; title: string; lifecycle_status: string; canonical_path: string; revision: number; created_at: string; updated_at: string };
export type V2Relation = { id: string; from_object_id: string; relation_type: string; to_object_id: string; metadata: Record<string, unknown> };
export type V2ObjectIndex = { initialized: boolean; objects: V2Object[]; relations: V2Relation[]; summary: Record<string, number> };

export async function loadV2Objects(projectPath: string): Promise<V2ObjectIndex> {
  return request(`/api/v2/p/${encodeURIComponent(projectPath)}/objects`);
}

export async function retryV2Job(projectPath: string, job: StoredJob, reason: string): Promise<{ jobs: StoredJob[]; worker_started: boolean }> {
  return postV2(`/api/v2/p/${encodeURIComponent(projectPath)}/jobs/${encodeURIComponent(job.id)}/retry`, { confirmation: "RETRY FAILED JOB", expected_revision: job.revision, reason });
}

export async function cancelV2Job(projectPath: string, job: StoredJob, reason: string): Promise<{ jobs: StoredJob[]; running_process_stopped: boolean }> {
  return postV2(`/api/v2/p/${encodeURIComponent(projectPath)}/jobs/${encodeURIComponent(job.id)}/cancel`, { confirmation: "CANCEL QUEUED JOB", expected_revision: job.revision, reason });
}

export async function savePaperCandidate(projectPath: string, candidate: PaperCandidate, recommendationReason = ""): Promise<{ candidate: StoredPaperCandidate }> {
  const response = await fetch(`/api/v2/p/${encodeURIComponent(projectPath)}/paper-candidates`, {
    method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ candidate, recommendation_reason: recommendationReason }),
  });
  const payload = await response.json() as { error?: string };
  if (!response.ok) throw new Error(payload.error || "候选登记失败");
  return payload as { candidate: StoredPaperCandidate };
}

export async function stagePaperAcquisition(projectPath: string, candidate: StoredPaperCandidate): Promise<Record<string, unknown>> {
  const response = await fetch(`/api/v2/p/${encodeURIComponent(projectPath)}/paper-candidates/${encodeURIComponent(candidate.id)}/acquisition`, {
    method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ confirmation: "STAGE PAPER ACQUISITION", expected_revision: candidate.revision }),
  });
  const payload = await response.json() as { error?: string };
  if (!response.ok) throw new Error(payload.error || "任务提交失败");
  return payload;
}

export async function ingestPaperCandidate(projectPath: string, candidate: StoredPaperCandidate, confirmation: string): Promise<{ candidate: StoredPaperCandidate }> {
  const response = await fetch(`/api/v2/p/${encodeURIComponent(projectPath)}/paper-candidates/${encodeURIComponent(candidate.id)}/ingest`, {
    method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ confirmation, expected_revision: candidate.revision }),
  });
  const payload = await response.json() as { error?: string };
  if (!response.ok) throw new Error(payload.error || "正式纳入失败");
  return payload as { candidate: StoredPaperCandidate };
}

export async function loadWorkspace(project: Project): Promise<WorkspaceData> {
  const projectKey = encodeURIComponent(project.path);
  const [papers, questions, ideas, intake, comparisons, explorations, dashboard, capabilities] = await Promise.all([
    request<Paper[]>(`/api/p/${projectKey}/papers`),
    request<Question[]>(`/api/p/${projectKey}/questions`),
    loadIdeas(project.path),
    loadIntake(project.path),
    request<Comparison[]>(`/api/p/${projectKey}/compares`),
    request<ExplorationRegistry>(`/api/p/${projectKey}/explorations`),
    request<ExperimentDashboard>(`/api/p/${projectKey}/experiments`),
    request<Capabilities>(`/api/v2/p/${projectKey}/capabilities`),
  ]);
  return { project, papers, questions, ideas, intake, comparisons, explorations: explorations.explorations || [], dashboard, capabilities };
}
