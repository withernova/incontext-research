import { createHash } from "node:crypto";
import * as nodePath from "node:path";

export const STEWARD_CONFIG_VERSION = 2;
export const DEFAULT_ETA_REGEX = String.raw`ETA:\s*(?:(\d+):)?(\d{1,2}):(\d{2}):(\d{2})|ETA:\s*(\d+(?:\.\d+)?)\s*([mh])`;
export type StewardPhase = "idle"|"monitoring"|"incident_open"|"remediation_pending"|"restarting"|"verifying_recovery"|"completion_candidate"|"archiving"|"archived"|"needs_attention"|"stopped";

export interface StewardConfig {
  version: 2;
  identity: { projectRoot?: string; runId?: string; experimentId?: string; managedExecution?: boolean };
  remote: { host: string; projectDir: string };
  experiment: { tmuxSession: string; logFile: string; description?: string; processPattern?: string };
  monitoring: { errorPatterns: string[]; progressPatterns: string[]; gpuWarningPercent: number; etaRegex: string };
  scheduling: { minIntervalMinutes:number; normalIntervalMinutes:number; maxIntervalMinutes:number; etaFraction:number; nearCompletionMinutes:number; stableBackoffAfterChecks:number };
  completion: { enabled:boolean; completionMarkers:string[]; requiredArtifacts:string[]; metricsFile?:string; exitCodeFile?:string; stableChecks:number; requireProcessExit:boolean; allowNonzeroExit:boolean };
  remediation: { enabled:boolean; maxRestarts:number; playbooks:Array<{id:string; fingerprints:string[]; errorPatterns:string[]; commands:string[]; restartCommand?:string; requiresCodeEdit:boolean}> };
  archive: { enabled:boolean; mode:"manifest_reference"; localDir:string; includePaths:string[]; checksumAlgorithm:"sha256"; autoArchive:boolean; maxFiles:number; maxTotalBytes:number };
}

const errors=["FileNotFoundError","CUDA out of memory","RuntimeError","KeyboardInterrupt","Traceback","AssertionError"];
const progress=["iteration:","epoch:","loss:","ETA:"];
export function defaultConfig():StewardConfig { return {
  version:2,identity:{},remote:{host:"",projectDir:""},experiment:{tmuxSession:"exp",logFile:"results/experiment.log",description:"",processPattern:""},
  monitoring:{errorPatterns:[...errors],progressPatterns:[...progress],gpuWarningPercent:95,etaRegex:DEFAULT_ETA_REGEX},
  scheduling:{minIntervalMinutes:2,normalIntervalMinutes:15,maxIntervalMinutes:60,etaFraction:.1,nearCompletionMinutes:30,stableBackoffAfterChecks:3},
  completion:{enabled:false,completionMarkers:[],requiredArtifacts:[],metricsFile:"",exitCodeFile:"",stableChecks:2,requireProcessExit:true,allowNonzeroExit:false},
  remediation:{enabled:false,maxRestarts:1,playbooks:[]},
  archive:{enabled:false,mode:"manifest_reference",localDir:".survey-tool/experiment-archives",includePaths:[],checksumAlgorithm:"sha256",autoArchive:false,maxFiles:2000,maxTotalBytes:2_000_000_000},
}; }

function obj(v:any):Record<string,any>{return v&&typeof v==="object"&&!Array.isArray(v)?v:{}}
function strings(v:any,key:string):string[]{if(v===undefined)return[];if(!Array.isArray(v)||v.some(x=>typeof x!=="string"))throw new Error(`${key} 必须为字符串数组`);if(v.some(x=>/[\0\r\n]/.test(x)))throw new Error(`${key} 含非法控制字符`);return v.map(x=>x.trim()).filter(Boolean)}
function text(v:any,key:string,fallback=""):string{if(v===undefined||v===null)return fallback;if(typeof v!=="string")throw new Error(`${key} 必须为字符串`);if(/[\0\r\n]/.test(v))throw new Error(`${key} 含非法控制字符`);return v.trim()}
function bool(v:any,key:string,fallback:boolean):boolean{if(v===undefined)return fallback;if(typeof v!=="boolean")throw new Error(`${key} 必须为 boolean`);return v}
function num(v:any,key:string,fallback:number):number{if(v===undefined)return fallback;if(typeof v!=="number"||!Number.isFinite(v))throw new Error(`${key} 必须为有限数字`);return v}
export function normalizeConfig(input:any):StewardConfig {
  const raw=obj(input), out=defaultConfig();
  // Legacy flat activate_run contract and nested WatchdogConfig are both accepted.
  const remote=obj(raw.remote), exp=obj(raw.experiment), mon=obj(raw.monitoring), sched=obj(raw.scheduling), completion=obj(raw.completion), remediation=obj(raw.remediation), archive=obj(raw.archive), identity=obj(raw.identity);
  out.identity={projectRoot:text(identity.projectRoot??raw.projectRoot,"identity.projectRoot"),runId:text(identity.runId??raw.runId,"identity.runId"),experimentId:text(identity.experimentId??raw.experimentId,"identity.experimentId"),managedExecution:bool(identity.managedExecution,"identity.managedExecution",false)};
  out.remote={host:text(remote.host??raw.host,"remote.host"),projectDir:text(remote.projectDir??raw.project_dir,"remote.projectDir")};
  out.experiment={tmuxSession:text(exp.tmuxSession??raw.tmux_session,"experiment.tmuxSession","exp"),logFile:text(exp.logFile??raw.log_file,"experiment.logFile","results/experiment.log"),description:text(exp.description??raw.description,"experiment.description"),processPattern:text(exp.processPattern??raw.process_pattern,"experiment.processPattern")};
  const ep=strings(mon.errorPatterns,"monitoring.errorPatterns"),pp=strings(mon.progressPatterns,"monitoring.progressPatterns");
  out.monitoring={errorPatterns:ep.length?ep:[...errors],progressPatterns:pp.length?pp:[...progress],gpuWarningPercent:num(mon.gpuWarningPercent,"monitoring.gpuWarningPercent",95),etaRegex:text(mon.etaRegex,"monitoring.etaRegex",DEFAULT_ETA_REGEX)};
  out.scheduling={minIntervalMinutes:num(sched.minIntervalMinutes,"scheduling.minIntervalMinutes",2),normalIntervalMinutes:num(sched.normalIntervalMinutes,"scheduling.normalIntervalMinutes",15),maxIntervalMinutes:num(sched.maxIntervalMinutes,"scheduling.maxIntervalMinutes",60),etaFraction:num(sched.etaFraction,"scheduling.etaFraction",.1),nearCompletionMinutes:num(sched.nearCompletionMinutes,"scheduling.nearCompletionMinutes",30),stableBackoffAfterChecks:num(sched.stableBackoffAfterChecks,"scheduling.stableBackoffAfterChecks",3)};
  out.completion={enabled:bool(completion.enabled,"completion.enabled",false),completionMarkers:strings(completion.completionMarkers,"completion.completionMarkers"),requiredArtifacts:strings(completion.requiredArtifacts,"completion.requiredArtifacts"),metricsFile:text(completion.metricsFile,"completion.metricsFile"),exitCodeFile:text(completion.exitCodeFile,"completion.exitCodeFile"),stableChecks:num(completion.stableChecks,"completion.stableChecks",2),requireProcessExit:bool(completion.requireProcessExit,"completion.requireProcessExit",true),allowNonzeroExit:bool(completion.allowNonzeroExit,"completion.allowNonzeroExit",false)};
  out.archive={enabled:bool(archive.enabled,"archive.enabled",false),mode:text(archive.mode,"archive.mode","manifest_reference") as "manifest_reference",localDir:text(archive.localDir,"archive.localDir",".survey-tool/experiment-archives"),includePaths:strings(archive.includePaths,"archive.includePaths"),checksumAlgorithm:text(archive.checksumAlgorithm,"archive.checksumAlgorithm","sha256") as "sha256",autoArchive:bool(archive.autoArchive,"archive.autoArchive",false),maxFiles:num(archive.maxFiles,"archive.maxFiles",2000),maxTotalBytes:num(archive.maxTotalBytes,"archive.maxTotalBytes",2_000_000_000)};
  if(remediation.playbooks!==undefined&&!Array.isArray(remediation.playbooks))throw new Error("remediation.playbooks 必须为数组");
  out.remediation.enabled=bool(remediation.enabled,"remediation.enabled",false); out.remediation.maxRestarts=num(remediation.maxRestarts,"remediation.maxRestarts",1); out.remediation.playbooks=(remediation.playbooks||[]).map((p:any)=>{p=obj(p);return{id:text(p.id,"playbook.id"),fingerprints:strings(p.fingerprints,"playbook.fingerprints"),errorPatterns:strings(p.errorPatterns,"playbook.errorPatterns"),commands:strings(p.commands,"playbook.commands"),restartCommand:p.restartCommand===undefined?undefined:text(p.restartCommand,"playbook.restartCommand"),requiresCodeEdit:bool(p.requiresCodeEdit,"playbook.requiresCodeEdit",false)}});
  validateConfig(out); return out;
}

export function validateConfig(c:StewardConfig):void {
  if(c.version!==2) throw new Error("Steward config version 必须为 2");
  const s=c.scheduling;
  if(!(s.minIntervalMinutes>=1&&s.minIntervalMinutes<=s.normalIntervalMinutes&&s.normalIntervalMinutes<=s.maxIntervalMinutes&&s.maxIntervalMinutes<=1440)) throw new Error("scheduling interval 必须满足 1 <= min <= normal <= max <= 1440");
  if(!(s.etaFraction>0&&s.etaFraction<=1)||!(s.nearCompletionMinutes>=1)||!Number.isInteger(s.stableBackoffAfterChecks)||s.stableBackoffAfterChecks<1) throw new Error("scheduling 参数越界");
  if(!Number.isInteger(c.completion.stableChecks)||c.completion.stableChecks<1||c.completion.stableChecks>100) throw new Error("completion.stableChecks 越界");
  if(!(c.monitoring.gpuWarningPercent>0&&c.monitoring.gpuWarningPercent<=100))throw new Error("monitoring.gpuWarningPercent 越界");
  for(const [key,value] of Object.entries({"completion.enabled":c.completion.enabled,"completion.requireProcessExit":c.completion.requireProcessExit,"completion.allowNonzeroExit":c.completion.allowNonzeroExit,"remediation.enabled":c.remediation.enabled,"archive.enabled":c.archive.enabled,"archive.autoArchive":c.archive.autoArchive}))if(typeof value!=="boolean")throw new Error(`${key} 必须为 boolean`);
  if(!Number.isInteger(c.archive.maxFiles)||c.archive.maxFiles<1||c.archive.maxFiles>100000||!Number.isFinite(c.archive.maxTotalBytes)||c.archive.maxTotalBytes<1||c.archive.maxTotalBytes>1_000_000_000_000)throw new Error("archive 扫描上限越界");
  if(c.archive.mode!=="manifest_reference"||c.archive.checksumAlgorithm!=="sha256") throw new Error("archive 第一版只支持 manifest_reference/sha256");
  if(c.archive.autoArchive&&!c.archive.enabled)throw new Error("archive.autoArchive 需要 archive.enabled=true");
  if(!Number.isInteger(c.remediation.maxRestarts)||c.remediation.maxRestarts<0||c.remediation.maxRestarts>10) throw new Error("remediation.maxRestarts 越界");
  const ids=new Set<string>(); for(const p of c.remediation.playbooks){if(!p.id||ids.has(p.id))throw new Error("playbook id 必须安全且唯一");ids.add(p.id);if(!/^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$/.test(p.id)||(!p.fingerprints.length&&!p.errorPatterns.length)||(!p.requiresCodeEdit&&!p.commands.length))throw new Error(`playbook ${p.id} 不完整`)}
  try{new RegExp(c.monitoring.etaRegex,"gi")}catch(e:any){throw new Error(`monitoring.etaRegex 无效：${e.message}`)}
  if(c.experiment.processPattern){try{new RegExp(c.experiment.processPattern)}catch(e:any){throw new Error(`experiment.processPattern 无效：${e.message}`)}}
  for(const [key,value] of Object.entries({"remote.projectDir":c.remote.projectDir,"experiment.logFile":c.experiment.logFile,"completion.metricsFile":c.completion.metricsFile||"","completion.exitCodeFile":c.completion.exitCodeFile||"","archive.localDir":c.archive.localDir}))if(value.includes("\0"))throw new Error(`${key} 路径无效`);
  if((c.completion.enabled||c.archive.autoArchive)&&!c.experiment.processPattern)throw new Error("completion/auto monitor 需要非空 experiment.processPattern");
  if(c.completion.enabled&&c.completion.requireProcessExit&&!c.completion.allowNonzeroExit&&!c.completion.exitCodeFile)throw new Error("严格进程退出合同需要 completion.exitCodeFile");
}

export function parseEta(line:string, regex=DEFAULT_ETA_REGEX):number|null {
  let found:RegExpExecArray|null=null,re:RegExp;try{re=new RegExp(regex,"gi")}catch(e:any){throw new Error(`ETA regex 无效：${e.message}`)}for(let m;(m=re.exec(line));){found=m;if(m[0]==="")re.lastIndex++}
  if(!found)return null; if(found[5])return Number(found[5])*(found[6].toLowerCase()==="h"?3600:60);
  if(!found[2]||!found[3]||!found[4])return null;const values=[found[1]||"0",found[2],found[3],found[4]].map(Number);if(values.some(x=>!Number.isFinite(x)))return null;const[days,hours,mins,seconds]=values;return days*86400+hours*3600+mins*60+seconds;
}
export function decideInterval(c:StewardConfig,input:{phase:StewardPhase;etaSeconds?:number|null;healthyStreak:number}):{minutes:number;reason:string}{
  const s=c.scheduling;if(["incident_open","remediation_pending","restarting","verifying_recovery","completion_candidate","needs_attention"].includes(input.phase))return{minutes:s.minIntervalMinutes,reason:`phase=${input.phase}`};
  if(input.etaSeconds!=null){if(input.etaSeconds<=s.nearCompletionMinutes*60)return{minutes:s.minIntervalMinutes,reason:"ETA near completion"};return{minutes:Math.max(s.minIntervalMinutes,Math.min(s.maxIntervalMinutes,input.etaSeconds/60*s.etaFraction)),reason:"ETA fraction"}}
  if(input.healthyStreak>=s.stableBackoffAfterChecks){const steps=input.healthyStreak-s.stableBackoffAfterChecks+1;return{minutes:Math.min(s.maxIntervalMinutes,s.normalIntervalMinutes*Math.pow(2,steps)),reason:"stable backoff"}}
  return{minutes:s.normalIntervalMinutes,reason:"normal interval"};
}

export interface CompletionObservation{markersFound:string[];artifacts:Array<{path:string;exists:boolean;size:number;mtime:string}>;processRunning:boolean;processVerified?:boolean;exitCode?:number|null;exitCodeVerified?:boolean;openIncidents:number;blockedPhase?:boolean;previousArtifacts?:Array<{path:string;size:number;mtime:string}>}
export function evaluateCompletion(c:StewardConfig,o:CompletionObservation,previousStableCount=0){
  const required=[...c.completion.requiredArtifacts,...(c.completion.metricsFile?[c.completion.metricsFile]:[]),...(c.completion.exitCodeFile?[c.completion.exitCodeFile]:[])], byPath=new Map(o.artifacts.map(x=>[x.path,x]));
  const markersOk=c.completion.completionMarkers.every(x=>o.markersFound.includes(x)); const artifactsOk=required.every(p=>{const x=byPath.get(p);return !!x?.exists&&x.size>0});
  const exitOk=!c.completion.requireProcessExit||(o.processVerified===true&&!o.processRunning&&(c.completion.allowNonzeroExit||(o.exitCodeVerified===true&&o.exitCode===0))); const incidentsOk=o.openIncidents===0&&!o.blockedPhase;
  const prev=new Map((o.previousArtifacts||[]).map(x=>[x.path,x])); const stable=required.every(p=>{const a=byPath.get(p),b=prev.get(p);return !!a&&!!b&&a.size===b.size&&a.mtime===b.mtime});
  const contractOk=c.completion.enabled&&markersOk&&artifactsOk&&exitOk&&incidentsOk; const stableCount=contractOk&&stable?previousStableCount+1:0;
  return{contractOk,complete:contractOk&&stableCount>=c.completion.stableChecks,stableCount,checks:{enabled:c.completion.enabled,markersOk,artifactsOk,exitOk,incidentsOk,stable},reason:!c.completion.enabled?"completion disabled":!markersOk?"missing markers":!artifactsOk?"missing/nonempty artifacts":!exitOk?"process/exit contract":!incidentsOk?"open incident":!stable?"files not yet stable":"stable completion contract"};
}

export function redact(value:any):any {if(Array.isArray(value))return value.map(redact);if(value&&typeof value==="object")return Object.fromEntries(Object.entries(value).filter(([k])=>!/token|secret|password|prompt|message|private.?key|commands?|restartCommand/i.test(k)).map(([k,v])=>[k,redact(v)]));if(typeof value==="string"&&(/-----BEGIN .*PRIVATE KEY-----/.test(value)||/(?:password|token|secret)\s*[=:]\s*\S+/i.test(value)))return"[REDACTED]";return value}
export function managedPathAllowed(projectRoot:string,value:string):boolean {
  if(!nodePath.isAbsolute(projectRoot)||!nodePath.isAbsolute(value)||/[\0\r\n]/.test(projectRoot+value)||value.split(nodePath.sep).includes(".."))return false;
  const root=nodePath.resolve(projectRoot),resolved=nodePath.resolve(value),relative=nodePath.relative(root,resolved);
  if(relative==="" )return true;
  if(relative.startsWith(".."+nodePath.sep)||nodePath.isAbsolute(relative))return false;
  return !/^(?:\.git|\.pi(?:\/|$)|\.survey-tool(?:\/|$)|kernel\/claims\.md$)/.test(relative.split(nodePath.sep).join("/"));
}
export function managedBashAllowed(command:string,surveyctlPath:string,projectRoot:string):boolean {
  const prefix=`python3 ${surveyctlPath} --project ${projectRoot} `;
  if(!command.startsWith(prefix)||/[\n\r\0;&|`$<>]/.test(command))return false;
  const tail=command.slice(prefix.length);
  return /^(?:outbox (?:list|status)(?: |$)|managed-run (?:preflight|start|status|complete|fail)(?: |$))/.test(tail);
}
export function surveyctlPathFromExtension(extensionEntry:string,realExtensionEntry=extensionEntry):string {
  if(!nodePath.isAbsolute(extensionEntry)||!nodePath.isAbsolute(realExtensionEntry)||/[\0\r\n]/.test(extensionEntry+realExtensionEntry))throw new Error("extension entry path must be absolute");
  return nodePath.resolve(nodePath.dirname(realExtensionEntry),"..","..","surveyctl.py");
}
export function redactManagedResult(value:any):any {
  return redact(value);
}
export function isStaleManagedLeaseError(value:unknown):boolean {
  const text=String((value as any)?.message||value||"");
  return /lease (?:token(?:\/consumer)?|consumer).*(?:invalid|无效|mismatch)|lease (?:已)?过期|lease expired/i.test(text);
}
export function stableArchiveId(identity:{projectRoot?:string;experimentId?:string;runId?:string},completionIdentity:string):string{return "archive-"+createHash("sha256").update(JSON.stringify([identity.projectRoot||"",identity.experimentId||"",identity.runId||"",completionIdentity])).digest("hex").slice(0,24)}
export function canonicalStringify(value:any):string{if(Array.isArray(value))return`[${value.map(canonicalStringify).join(",")}]`;if(value&&typeof value==="object")return`{${Object.keys(value).filter(k=>value[k]!==undefined).sort().map(k=>`${JSON.stringify(k)}:${canonicalStringify(value[k])}`).join(",")}}`;return JSON.stringify(value)}
export function manifestHash(value:any):string{const copy=JSON.parse(JSON.stringify(redact(value)));if(copy&&typeof copy==="object")delete copy.manifest_sha256;return createHash("sha256").update(canonicalStringify(copy)).digest("hex")}
export function inventoryWindow<T extends {size:number}>(rows:T[],maxFiles:number,maxTotalBytes:number){const sorted=[...rows].sort((a:any,b:any)=>String(a.path||"").localeCompare(String(b.path||""))),items:T[]=[];let totalBytes=0,truncated=sorted.length>maxFiles;for(const row of sorted.slice(0,maxFiles)){if(totalBytes+row.size>maxTotalBytes){truncated=true;break}items.push(row);totalBytes+=row.size}return{items,totalBytes,truncated}}
export function restartAllowed(hasRestartCommand:boolean,restartCount:number,maxRestarts:number){return!hasRestartCommand||restartCount<maxRestarts}
export function runWritebackDecision(statuses:string[]){const active=new Set(["queued","delivered","claimed","acknowledged","running"]);return{writeCompleted:!statuses.some(s=>active.has(s)),outboxPending:statuses.some(s=>active.has(s))}}
export function blockingIncidentCount(rows:Array<{status:string}>){return rows.filter(x=>x.status==="open"||x.status==="remediation_applied").length}

export const REMEDIATION_BLOCKED_PHASES=new Set<StewardPhase>(["incident_open","remediation_pending","restarting","verifying_recovery","needs_attention"]);
export interface ObservationPhaseInput {currentPhase:StewardPhase;tmuxAlive:boolean;processRunning:boolean;processVerified:boolean;newErrorFingerprints?:string[];completionContractOk:boolean;completionComplete:boolean}
export function decideObservationPhase(i:ObservationPhaseInput):{phase:StewardPhase;reason:string;incidentSignature:string;archiveEligible:boolean}{
  const ids=[...(i.newErrorFingerprints||[])].sort();
  if(ids.length)return{phase:"incident_open",reason:"new error occurrence",incidentSignature:`errors:${ids.join(",")}`,archiveEligible:false};
  if(!i.processVerified)return{phase:"needs_attention",reason:"process check unverified",incidentSignature:"process:unverified",archiveEligible:false};
  if(REMEDIATION_BLOCKED_PHASES.has(i.currentPhase))return{phase:i.currentPhase,reason:"remediation/attention phase remains blocking",incidentSignature:"",archiveEligible:false};
  if(i.completionComplete)return{phase:"completion_candidate",reason:"completion contract stable; archive is eligible",incidentSignature:"",archiveEligible:true};
  if(i.completionContractOk)return{phase:"completion_candidate",reason:"completion contract first stable check",incidentSignature:"",archiveEligible:false};
  if(!i.tmuxAlive)return{phase:"incident_open",reason:"tmux stopped before completion",incidentSignature:"tmux:dead",archiveEligible:false};
  if(!i.processRunning)return{phase:"incident_open",reason:"process verified stopped before completion",incidentSignature:"process:stopped",archiveEligible:false};
  return{phase:"monitoring",reason:"structured observation healthy",incidentSignature:"",archiveEligible:false};
}
export function shouldNotifyIncident(previousSignature:string|undefined,decision:{phase:StewardPhase;incidentSignature:string}):boolean{return(decision.phase==="incident_open"||decision.phase==="needs_attention")&&!!decision.incidentSignature&&decision.incidentSignature!==previousSignature}
