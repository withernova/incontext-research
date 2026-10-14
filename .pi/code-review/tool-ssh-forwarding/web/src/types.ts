export type Project = {
  name: string;
  label: string;
  path: string;
  state: string;
  iteration: number;
  blockers: string[];
  next_actions: string[];
};

export type Paper = {
  citekey: string;
  title: string;
  date?: string;
  venue?: string;
  file?: string;
  has_pdf?: boolean;
  has_mineru?: boolean;
  has_images?: boolean;
  images_count?: number;
};

export type PaperBundle = {
  citekey: string;
  note_exists: boolean;
  note_path: string;
  seven: Record<string, string | boolean>;
  annotations: PaperAnnotation[];
  state?: Record<string, unknown>;
  _canonical_rev: string;
  claims: Array<{ id?: string; text?: string; status?: string }>;
  images: Array<{ name?: string; path?: string } | string>;
  citation: Record<string, unknown>;
  mineru_md: string;
  pdf_path: string;
};

export type PaperAnnotation = {
  citekey: string;
  fig?: string;
  src?: string;
  note?: string;
  boxes?: unknown[];
  raw?: string;
};

export type PaperCandidate = {
  citekey: string;
  title: string;
  authors: string[];
  year: string;
  doi?: string;
  url: string;
  is_oa: boolean;
  oa_url?: string | null;
  cited_by_count?: number;
  source?: string;
  arxiv_id?: string;
};

export type PaperSearchResult = {
  source: string;
  query: string;
  hits: PaperCandidate[];
  error?: string;
  warning?: string;
};

export type ComparisonFinding = {
  id?: string;
  text?: string;
  source?: string;
  status?: string;
  _canonical_rev?: string;
};

export type Comparison = {
  id: string;
  name: string;
  mode?: string;
  papers: string[];
  axes?: string[];
  customAxes?: string[];
  analysis?: string;
  piAnalysis?: string;
  findings?: ComparisonFinding[];
  obsidian_notes?: string;
  _canonical_rev?: string;
};

export type Question = {
  id: string;
  title: string;
  status: string;
  created?: string;
  updated?: string;
  papers?: string[];
  comparisons?: string[];
  findings?: string[];
  experiments?: string[];
  question?: string;
  current_judgement?: string;
  investigation?: string;
  path?: string;
  _canonical_rev?: string;
};

export type Idea = {
  id: string;
  title: string;
  hypothesis?: string;
  motivation?: string;
  method?: string;
  key_experiments?: string;
  risks?: string;
  related_diff?: string;
  falsification?: string;
  status?: string;
  novelty?: string;
  novelty_note?: string;
  support_claims?: string;
  contra_claims?: string;
  sources?: string;
  created?: string;
  updated?: string;
  _canonical_rev: string;
};

export type Intake = {
  repo_path: string;
  project_slug: string;
  project_name: string;
  idea: string;
  domain: string;
  target_venue: string;
  polite_email: string;
  seed_papers: string[];
  constraints: string[];
  notes: string;
  _exists?: boolean;
  _canonical_rev: string;
};

export type Experiment = {
  agent_handoff?: {contract:string;experiment_id:string;verified_facts?:Array<{label:string;value:string;evidence?:string}>;proposal?:{objective?:string;implementation_scope?:string;evaluation?:string};questions?:Array<{key:string;label:string;why?:string;suggested?:string}>;risks?:string[]};
  user_answers?: Record<string,string>;
  implementation_scope?:string;
  evaluation?:string;
  id: string;
  title: string;
  status: string;
  objective?: string;
  workspace_id?: string;
  code_repository_workspace_id?: string;
  updated?: string;
  workflow_stage?: string;
  constraints?: string;
  evidence_refs?: string[] | string;
  hypothesis?: string;
  success_criteria?: string;
  failure_criteria?: string;
  schedule?: string;
  variables?: string;
  minimum_test?: string;
  baseline?: string;
  treatments?: string;
  metrics?: string;
  confounders?: string;
  risks?: string;
  open_questions?: string;
  budget?: string | Record<string, unknown>;
  source_ref?: string;
  run_groups?: Array<{ id: string; name: string; description?: string; color?: string }>;
  metric_definitions?: Array<Record<string, unknown>>;
  archived_at?: string;
  archived_by?: string;
  archive_reason?: string;
  archive_history?: Array<{time:string;action:"archive"|"restore";actor:string;reason:string}>;
};

export type Run = {
  id: string;
  experiment_id: string;
  status?: string;
  review_status?: string;
  workflow_version?: number;
  workflow_stage?: string;
  workflow_status?: string;
  variant?: string;
  purpose?: string;
  necessity?: string;
  evidence_basis?: string;
  implementation_summary?: string;
  implementation_details?: string;
  research_question?: string;
  hypothesis?: string;
  metric_plan?: string;
  architecture_plan?: string;
  implementation_ref?: unknown;
  data_definition?: string;
  data_scale?: string;
  model_config?: string;
  variables_controls?: string;
  metric_definition?: string;
  integrity_gates?: string;
  expected_outcome?: string;
  acceptance_criteria?: string;
  dependencies?: string;
  result_analysis?: string;
  key_results?: unknown;
  metric_observations?: unknown;
  auxiliary_metric_observations?: unknown;
  metrics?: string;
  artifacts?: string;
  notes?: string;
  result_summary?: string;
  limitations?: string;
  conclusion_scope?: string;
  claim_boundary?: string;
  audit_paths?: string;
  workspace_id?: string;
  group_id?: string;
  command?: string;
  git_commit?: string;
  artifact_dir?: string;
  log_path?: string;
  output_dir?: string;
  metrics_path?: string;
  execution_authorized_at?: string;
  execution_authorization_note?: string;
  review_requirements?: string;
  review_questions?: string;
  execution_authorization_consumed_at?: string;
  execution_dispatch_id?: string;
  created?: string;
  updated?: string;
  automation_policy?: {mode:"off"|"careful"|"active";allowed_code_roots:string[];test_commands:string[];max_repairs:number;time_budget_minutes:number;auto_rerun:boolean;install_declared_dependencies:boolean;dependency_files:string[];prohibited_actions?:string[]};
  trial_plan?: RunTrialPlan;
  trial_campaigns?: RunTrialCampaign[];
  active_trial_campaign_id?: string;
  archived_at?: string;
  archived_by?: string;
  archive_reason?: string;
  archive_history?: Array<{time:string;action:"archive"|"restore";actor:string;reason:string}>;
  evidence_label?: "solid";
  evidence_label_note?: string;
  evidence_labeled_at?: string;
  evidence_labeled_by?: string;
  evidence_label_history?: Array<{time:string;action:"set"|"clear";label:string;actor:string;note:string}>;
};

export type RunTrialValue=string|number|boolean;
export type RunTrialPlan={contract:"survey-tool.run-trial-plan/v1";campaign_id?:string;planning_mode?:"matrix"|"ai_planned";request:string;trial_budget?:number;axes:Array<{name:string;values:RunTrialValue[]}>;trials:Array<{id:string;parameters:Record<string,RunTrialValue>;status:string;attempts:number}>;planning_status?:"planned"|"awaiting_ai";concurrency:number;max_retries:number;created_at?:string;updated_at?:string};
export type RunTrialCampaign={id:string;contract:"survey-tool.run-trial-campaign/v1";request:string;status:string;created_at:string;updated_at?:string;previous_workflow_stage?:string;plan:RunTrialPlan;manifest?:{contract:"survey-tool.run-trial-manifest/v1";trials:Array<{id:string;parameters:Record<string,RunTrialValue>;rationale?:string}>};previous_result?:Record<string,unknown>;result?:Record<string,unknown>;failure?:{failure_class?:string;reason?:string;retryable?:boolean}};

export type Dispatch = {
  dispatch_id?: string;
  run_id?: string;
  status?: string;
  requested_agent?: string;
  actual_agent?: string;
  last_error?: string;
  updated_at?: string;
  managed_execution?: { isolation_mode?:string; started_evidence?:string; status_observation?:{tmux_alive?:boolean;observed_at?:string;completion_candidate?:boolean;exit_code?:string|null;marker_found?:boolean;files?:Record<string,{exists?:boolean;size?:number;mtime?:number}>} };
};

export type StewardStatus = {
  run_id:string;
  experiment_id:string;
  run_label:string;
  workflow_stage:string;
  revision_open?:boolean;
  state_conflict?:boolean;
  canonical_stage_stale?:boolean;
  supervisor:{run_id?:string;phase?:string;runtime_kind?:"herdr_pi";agent_status?:string;started_at?:string;updated_at?:string;finished_at?:string;error_class?:string;message?:string;dispatch_id?:string};
  supervisor_active:boolean;
  remote_execution_active:boolean;
  remote_tmux_observed?:boolean;
  remote_observed_at?:string;
  needs_attention:boolean;
  dispatch?:Dispatch;
  can_start:boolean;
  can_resume:boolean;
  can_restart?:boolean;
  resume_waiting?:boolean;
  resume_available_at?:string;
  can_recover?:boolean;
  execution_started:boolean;
  lease_exposed:false;
  prompt_used:false;
};
export type StewardStatusList={items:StewardStatus[];summary:{total:number;active:number;attention:number;phases:Record<string,number>};remote_probe_performed:false;lease_exposed:false};
export type StewardConsole={run_id:string;available:boolean;connected:boolean;output:string;reason:string;captured_at:string;truncated:boolean;source?:"owned_tmux_stdout"|"herdr_pi";agent_status?:string};

export type Reconciliation = {
  actions?: Array<{ action: string; run_id: string; authorization_timestamp?: string }>;
  anomalies?: Array<{ run_id: string; type: string; detail?: string }>;
  totals?: { actions?: number; anomalies?: number; unchanged?: number };
};

export type ExperimentDashboard = {
  experiments: Experiment[];
  runs: Run[];
  execution_outbox?: {
    items?: Dispatch[];
    summary?: Record<string, number>;
  };
  reconciliation?: Reconciliation;
  governance_tasks?: { tasks?: Array<{ status?: string }> } | Array<{ status?: string }>;
  servers?: ExperimentServer[];
  machines?: ExperimentServer[];
  workspaces?: ExperimentWorkspaceBinding[];
  events?: Array<Record<string, unknown>>;
};

export type ExperimentServer={id:string;label?:string;ssh_host?:string;project_root?:string;gpu_type?:string;gpu_count?:number|string;launcher?:string;notes?:string};
export type EnvironmentPolicy={allowed_write_roots?:string[];read_only_roots?:string[];forbidden_paths?:string[];forbidden_operations?:string[];temp_policy?:string;notes?:string;policy_preset?:string;dangerous_exceptions?:string[];default_deny_write?:true};
export type ExecutionIsolation={mode:"none"|"bubblewrap";required:true;network:"host"|"none";deny_read_roots:string[];notes:string};
export type DatasetBinding={id:string;label:string;source_path:string;target_path:string;mode:"bind_ro"|"symlink_ro";required:boolean;notes:string};
export type WorkspaceRuleInput={contract:"survey-tool.workspace-rule-input/v1";original_request:string;preset:WorkspaceRulePreset;updated_at:string};
export type RuleOrganizer={requested:"ai_auto"|"basic"|"external";used:"ai"|"basic_fallback"|"basic";reason:string};
export type WorkspaceRuleProfile={contract:"survey-tool.workspace-rule-profile/v1";original_request:string;preset:WorkspaceRulePreset;rules:Array<{id:string;label:string;detail:string;source:"preset"|"request"}>;warnings:string[];questions:string[];updated_at:string;organizer?:RuleOrganizer};
export type CodeDevelopment={mode:"auto"|"remote"|"local-git";repository_url?:string;branch?:string;storage?:"project"|"external";transport?:"https"|"ssh"};
export type ExperimentWorkspaceBinding={code_development?:CodeDevelopment;local_code_repo?:string;id:string;label?:string;server_id?:string;remote_repo?:string;external_code_url?:string;external_code_ref?:string;remote_data_root?:string;remote_worktree_root?:string;remote_experiment_root?:string;environment_activation?:string;launcher?:string;environment_policy?:EnvironmentPolicy;execution_isolation?:ExecutionIsolation;dataset_bindings?:DatasetBinding[];rule_input?:WorkspaceRuleInput;rule_profile?:WorkspaceRuleProfile;pending_rule_draft?:RuleDraftPreview&{generated_at?:string;trigger?:"execution_claim"}};
export type EnvironmentBindings={project_code_root?:string;servers:ExperimentServer[];workspaces:ExperimentWorkspaceBinding[];servers_hash:string;workspaces_hash:string;managed_execution?:Record<string,{ready:boolean;reason:string;isolation:ExecutionIsolation;remote_probe_performed:false}>;authority:string;intake_repo_path?:string;publish?:{githubUrl?:string;commitSha?:string;publishedAt?:string};binding_note?:string};
export type AgentKind="codex"|"pi";
export type AgentRoute={enabled:boolean;agent_kind:AgentKind;model:string;fallback_agent_kind:AgentKind;fallback_model:string;inherited_from?:"local_tool_edit"};
export type AgentRouting={version:1;routes:{local_tool_edit:AgentRoute;experiment_code_edit:AgentRoute;lightweight_governance:AgentRoute}};
export type AgentRoutingConfig={routing:AgentRouting;authority:"project_tool_state";known_codex_models:string[];applies_to:"future_dispatches_only"};
export type WorkspaceRulePreset="research_safe"|"read_only_analysis"|"custom";
export type RuleDraftPreview={contract:"survey-tool.rule-draft/v1";scope:"workspace";original_request:string;preset:{id:WorkspaceRulePreset;label:string;description:string};rules:Array<{id:string;label:string;detail:string;source:"preset"|"request"}>;structured_preview:{environment_policy:EnvironmentPolicy;execution_isolation:ExecutionIsolation;dataset_bindings:DatasetBinding[]};warnings:string[];questions:string[];read_only:true;organizer:RuleOrganizer;external_intent?:{remote_repo:string;remote_data_root:string;remote_worktree_root:string;remote_experiment_root:string;environment_activation:string}};
export type ZoteroCollection={id:number;name:string;parent?:number|null;count:number};
export type ZoteroItem={id:number;title:string;authors:string[];date?:string;venue?:string;doi?:string;has_pdf:boolean;already_in:boolean};

export type Capabilities = {
  api_version: number;
  storage_schema_version: number;
  features: Record<string, string>;
  project_store?: {
    initialized: boolean;
    schema_version: number;
    relative_path: string;
  };
  herdr?: {
    managed: boolean;
    cli_available: boolean;
    codex_supported: boolean;
    probe_status: "available" | "unavailable";
    access: "discovery_only";
  };
};

export type Exploration = {
  id?: string;
  exploration_id?: string;
  target_type?: string;
  target_id?: string;
  status?: string;
  budget?: Record<string, unknown>;
  round_count?: number;
  canonical_path?: string;
  updated_at?: string;
};

export type ExplorationRegistry = {
  explorations: Exploration[];
};

export type WorkspaceData = {
  project: Project;
  papers: Paper[];
  questions: Question[];
  ideas: Idea[];
  intake: Intake;
  comparisons: Comparison[];
  explorations: Exploration[];
  dashboard: ExperimentDashboard;
  capabilities: Capabilities;
};
