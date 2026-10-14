/**
 * Experiment Steward — Autonomous Remote ML Experiment Monitor for Pi
 *
 * Monitors long-running ML experiments on remote servers via SSH + tmux.
 * Supports BOTH manual checking AND fully autonomous AFK monitoring.
 *
 * ## Autonomous Mode
 *
 *   /steward start [minutes]   — start autonomous monitoring (default: 30 min)
 *   /steward stop              — stop autonomous monitoring
 *   /steward status            — show monitoring state
 *
 * In autonomous mode, Experiment Steward performs structured checks.
 * If the experiment is healthy, it reports briefly. If errors are found,
 * pi attempts to diagnose and fix the issue automatically.
 *
 * ## Manual Tools (also available)
 *
 *   experiment_status           — Full health check
 *   experiment_log              — View recent output
 *   experiment_scan_errors      — Scan for error patterns
 *   experiment_steward_config  — Show config
 */

import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { blockingIncidentCount, decideInterval, decideObservationPhase, shouldNotifyIncident, defaultConfig, evaluateCompletion, inventoryWindow, isStaleManagedLeaseError, managedPathAllowed, manifestHash, normalizeConfig, parseEta, redact, redactManagedResult, restartAllowed, runWritebackDecision, stableArchiveId, surveyctlPathFromExtension, type StewardConfig, type StewardPhase } from "./core.js";

// ─── Types ───────────────────────────────────────────────────────────────────

type StewardRuntimeConfig = StewardConfig;

interface MonitorState {
  active: boolean;
  intervalMinutes: number;
  checkCount: number;
  lastCheckTime: number | null;
  lastCheckResult: "ok" | "error" | "crash" | "unknown";
  consecutiveErrors: number;
  sessionStartTime: number;
  phase: StewardPhase;
  healthyStreak: number;
  nextCheck: string | null;
  currentInterval: number;
  latestEtaSeconds: number | null;
  latestEtaSourceLine: string;
  latestProgressLine: string;
  completionStableCount: number;
  restartCount: number;
  archiveId: string;
  lastReason: string;
  pausedAfterRestart?: boolean;
  lastCompletionArtifacts?:Array<{path:string;size:number;mtime:string}>;
  verifyingFingerprintId?:string;
  observationFailureNotified?:boolean;
  notifiedIncidentSignature?:string;
}

type ErrorFingerprintStatus = "open" | "remediation_applied" | "resolved";
interface LogCursor {
  logIdentity: string;
  byteOffset: number;
  since: string;
  pendingLine?: string;
}
interface ErrorFingerprintRecord {
  id: string;
  exceptionType: string;
  normalizedStackRoot: string;
  command: string;
  runId: string;
  firstSeen: string;
  lastSeen: string;
  occurrences: number;
  remediation?: string;
  remediationAppliedAt?: string;
  resolvedAt?: string;
  status: ErrorFingerprintStatus;
  lastContext: string;
  lastAppliedOccurrence?:number;
  lastAppliedPlaybookId?:string;
  lastAttemptId?:string;
}
interface ObservationRecord {
  cursor?: LogCursor;
  fingerprints: Record<string, ErrorFingerprintRecord>;
}
interface ObservationStore {
  version: 1;
  records: Record<string, ObservationRecord>;
}

type QueueTaskStatus = "pending" | "running" | "completed" | "failed" | "blocked" | "skipped";
type QueueCapability = "inspect" | "implement" | "execute_approved";
type FailureClass = "transient" | "environment" | "invalid_spec" | "scientific" | "authorization" | "external_dependency";
interface RetryBasis {
  changedInput?: string;
  changedConfig?: string;
  changedEnvironment?: string;
  newEvidence?: string;
}

interface QueueTask {
  id: string;
  instruction: string;
  acceptance: string[];
  dependsOn: string[];
  capability: QueueCapability;
  maxAttempts: number;
  attempts: number;
  onFailure: "pause" | "continue";
  status: QueueTaskStatus;
  result?: string;
  failureClass?: FailureClass;
  retryBasis?: RetryBasis;
  startedAt?: string;
  finishedAt?: string;
}

interface TaskQueueState {
  version: 1;
  active: boolean;
  intervalMinutes: number;
  currentTaskId: string | null;
  tasks: QueueTask[];
  createdAt: string;
  updatedAt: string;
}

const STATE_ENTRY_TYPE = "x-experiment-steward-state";
const LEGACY_STATE_ENTRY_TYPE = "x-watchdog-state";

function defaultState(): MonitorState {
  return {
    active: false,
    intervalMinutes: 15,
    checkCount: 0,
    lastCheckTime: null,
    lastCheckResult: "unknown",
    consecutiveErrors: 0,
    sessionStartTime: Date.now(),
    phase:"idle",healthyStreak:0,nextCheck:null,currentInterval:15,latestEtaSeconds:null,latestEtaSourceLine:"",latestProgressLine:"",completionStableCount:0,restartCount:0,archiveId:"",lastReason:"",pausedAfterRestart:false,
  };
}

// ─── SSH Helpers ─────────────────────────────────────────────────────────────

function sshExec(
  host: string,
  command: string,
  timeout?: number,
): Promise<{ stdout: string; stderr: string; exitCode: number }> {
  return new Promise((resolve, reject) => {
    const child = spawn("ssh", [
      "-o", "ConnectTimeout=10",
      "-o", "StrictHostKeyChecking=accept-new",
      host, command,
    ], { stdio: ["ignore", "pipe", "pipe"] });

    const outChunks: Buffer[] = [];
    const errChunks: Buffer[] = [];
    child.stdout.on("data", (d) => outChunks.push(d));
    child.stderr.on("data", (d) => errChunks.push(d));

    const timer = timeout
      ? setTimeout(() => { child.kill(); reject(new Error(`SSH timeout ${timeout}s`)); }, timeout * 1000)
      : undefined;

    child.on("error", (e) => { if (timer) clearTimeout(timer); reject(e); });
    child.on("close", (code) => {
      if (timer) clearTimeout(timer);
      resolve({
        stdout: Buffer.concat(outChunks).toString("utf-8"),
        stderr: Buffer.concat(errChunks).toString("utf-8"),
        exitCode: code ?? -1,
      });
    });
  });
}

async function sshExecSafe(host: string, command: string, timeout?: number) {
  try { return await sshExec(host, command, timeout); }
  catch (e: any) { return { stdout: "", stderr: `SSH failed: ${e.message}`, exitCode: -1 }; }
}
function localExec(command:string,args:string[]):Promise<{stdout:string;stderr:string;exitCode:number}>{return new Promise(resolve=>{const child=spawn(command,args,{stdio:["ignore","pipe","pipe"]}),out:Buffer[]=[],err:Buffer[]=[];child.stdout.on("data",d=>out.push(d));child.stderr.on("data",d=>err.push(d));child.on("error",e=>resolve({stdout:"",stderr:e.message,exitCode:-1}));child.on("close",code=>resolve({stdout:Buffer.concat(out).toString(),stderr:Buffer.concat(err).toString(),exitCode:code??-1}))})}

// ─── Config Loading ──────────────────────────────────────────────────────────

function loadConfig(cwd: string): StewardRuntimeConfig | null {
  const paths = [
    path.join(cwd, ".pi", "experiment-steward.json"),
    path.join(cwd, "experiment-steward.json"),
    path.join(os.homedir(), ".pi", "experiment-steward.json"),
    path.join(cwd, ".pi", "experiment-watchdog.json"),
    path.join(cwd, "experiment-watchdog.json"),
    path.join(os.homedir(), ".pi", "experiment-watchdog.json"),
  ];
  for (const p of paths) {
    try {
      const cfg = normalizeConfig(JSON.parse(fs.readFileSync(p, "utf-8")));
      if (cfg.remote?.host && cfg.remote?.projectDir) return cfg;
    } catch { /* continue */ }
  }
  return null;
}

function loadRunConfig(cwd:string,runId:string):StewardRuntimeConfig|null{
  if(!/^[A-Za-z0-9][A-Za-z0-9._-]{0,159}$/.test(runId))return null;
  try{
    const cfg=normalizeConfig(JSON.parse(fs.readFileSync(path.join(cwd,".pi","stewards",`${runId}.json`),"utf-8")));
    if(cfg.identity.runId===runId&&cfg.remote.host&&cfg.remote.projectDir)return cfg;
  }catch{/* fall through to legacy compatibility config */}
  const legacy=loadConfig(cwd);
  return legacy?.identity.runId===runId?legacy:null;
}

// ─── Config Write / Merge ───────────────────────────────────────────────────

const DEFAULT_ERROR_PATTERNS = [
  "FileNotFoundError", "CUDA out of memory", "RuntimeError",
  "KeyboardInterrupt", "Traceback", "AssertionError",
];
const DEFAULT_PROGRESS_PATTERNS = ["iteration:", "epoch:", "loss:", "ETA:"];

interface SetParams {
  host?: string;
  project_dir?: string;
  tmux_session?: string;
  log_file?: string;
  description?: string;
  error_patterns?: string[];
  progress_patterns?: string[];
  gpu_warning_percent?: number;
}

/** Merge set-params into an existing config (or build a fresh one from defaults). */
function mergeConfig(existing: StewardRuntimeConfig | null, p: SetParams): StewardRuntimeConfig {
  const base: StewardRuntimeConfig = existing ?? defaultConfig();
  if (p.host !== undefined) base.remote.host = p.host;
  if (p.project_dir !== undefined) base.remote.projectDir = p.project_dir;
  if (p.tmux_session !== undefined) base.experiment.tmuxSession = p.tmux_session;
  if (p.log_file !== undefined) base.experiment.logFile = p.log_file;
  if (p.description !== undefined) base.experiment.description = p.description;
  if (p.error_patterns !== undefined) base.monitoring.errorPatterns = p.error_patterns;
  if (p.progress_patterns !== undefined) base.monitoring.progressPatterns = p.progress_patterns;
  if (p.gpu_warning_percent !== undefined) base.monitoring.gpuWarningPercent = p.gpu_warning_percent;
  return base;
}

function configWritePath(cwd: string, scope: string): string {
  if (scope === "global") return path.join(os.homedir(), ".pi", "experiment-steward.json");
  return path.join(cwd, ".pi", "experiment-steward.json");
}

function writeConfig(cfg: StewardRuntimeConfig, filePath: string): void {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  const tmp=`${filePath}.tmp-${process.pid}`; fs.writeFileSync(tmp, JSON.stringify(normalizeConfig(cfg), null, 2)+"\n", "utf-8"); fs.renameSync(tmp,filePath);
}

function renderConfig(cfg: StewardRuntimeConfig, st: MonitorState): string {
  return `## Experiment Steward Config\n` +
    `**Remote:** ${cfg.remote.host}:${cfg.remote.projectDir}\n` +
    `**Experiment:** ${cfg.experiment.description || cfg.experiment.tmuxSession}\n` +
    `**tmux:** ${cfg.experiment.tmuxSession}\n` +
    `**Log:** ${cfg.experiment.logFile}\n` +
    `**Errors:** ${cfg.monitoring.errorPatterns.join(", ")}\n` +
    `**Progress:** ${cfg.monitoring.progressPatterns.join(", ")}\n` +
    `**GPU warn:** ${cfg.monitoring.gpuWarningPercent}%\n` +
    `**Monitoring:** ${st.active ? `ACTIVE (${st.intervalMinutes}m)` : "inactive"}`;
}

// ─── Experiment Status Checkers ──────────────────────────────────────────────

async function checkTmuxSession(cfg: StewardRuntimeConfig): Promise<{ alive: boolean; text: string }> {
  const r = await sshExecSafe(cfg.remote.host,
    `tmux has-session -t ${shellQuote(cfg.experiment.tmuxSession)} >/dev/null 2>&1`);
  const alive = r.exitCode===0;
  if (alive) {
    const info = await sshExecSafe(cfg.remote.host,
      `tmux list-windows -t ${shellQuote(cfg.experiment.tmuxSession)} -F '#{window_name} #{pane_current_path}' 2>/dev/null`);
    return { alive: true, text: `✅ tmux "${cfg.experiment.tmuxSession}" alive` };
  }
  return { alive: false, text: `❌ tmux "${cfg.experiment.tmuxSession}" DEAD` };
}

async function checkTrainingProcess(cfg: StewardRuntimeConfig): Promise<{ running: boolean; verified:boolean; text: string }> {
  const pattern=cfg.experiment.processPattern;if(!pattern)return{running:false,verified:false,text:"⚠️ processPattern 未配置，无法验证 process"};
  const r = await sshExecSafe(cfg.remote.host,
    `pane_pid=$(tmux display-message -p -t ${shellQuote(cfg.experiment.tmuxSession)} '#{pane_pid}' 2>/dev/null || true); candidates=$({ test -n "$pane_pid" && { ps -o pid=,ppid=,args= -p "$pane_pid"; pgrep -a -P "$pane_pid"; }; pgrep -af -- ${shellQuote(pattern)} | grep -F -- ${shellQuote(cfg.remote.projectDir)}; } 2>/dev/null); filtered=$(printf '%s\n' "$candidates" | grep -E -- ${shellQuote(pattern)}); rc=$?; test "$rc" -eq 0 && printf '%s\n' "$filtered" | sort -u; if test "$rc" -eq 1; then echo NO_PROCESS; elif test "$rc" -ne 0; then exit "$rc"; fi`);
  if(r.exitCode!==0)return{running:false,verified:false,text:`⚠️ process check failed (exit=${r.exitCode})`};const running = !r.stdout.includes("NO_PROCESS")&&r.stdout.trim()!=="";
  if (running) {
    const lines = r.stdout.trim().split("\n").filter(Boolean);
    return { running: true, verified:true, text: `✅ ${lines.length} training process(es)` };
  }
  return { running: false, verified:true, text: "❌ No training process found" };
}

async function checkGPU(cfg: StewardRuntimeConfig): Promise<string> {
  const r = await sshExecSafe(cfg.remote.host,
    "nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits 2>&1");
  if (r.exitCode !== 0 || !r.stdout.trim()) return `⚠️ nvidia-smi unavailable`;
  const results: string[] = [];
  for (const line of r.stdout.trim().split("\n").filter(Boolean)) {
    const [idx, name, util, memUsed, memTotal, temp] = line.split(",").map(s => s.trim());
    if (!memUsed || !memTotal) continue;
    const memPct = (Number.parseFloat(memUsed) / Number.parseFloat(memTotal)) * 100;
    const icon = Number.parseFloat(util) > 0 ? "🟢" : "⚫";
    const warn = memPct > cfg.monitoring.gpuWarningPercent ? " ⚠️" : "";
    results.push(`GPU${idx} [${name}]: ${icon} ${util}% ${memUsed}/${memTotal}MiB (${memPct.toFixed(0)}%)${warn} ${temp}°C`);
  }
  return results.join("\n");
}

async function checkDisk(cfg: StewardRuntimeConfig): Promise<string> {
  const r = await sshExecSafe(cfg.remote.host, `df -h -- ${shellQuote(cfg.remote.projectDir)} | tail -1`);
  if (!r.stdout.trim()) return "⚠️ disk query failed";
  const parts = r.stdout.trim().split(/\s+/);
  const [fs, size, used, avail, usePct] = parts;
  const pct = Number.parseInt(usePct);
  return `${pct > 90 ? "🔴" : pct > 75 ? "🟡" : "🟢"} ${used}/${size} (${usePct})`;
}

async function getRecentOutput(cfg: StewardRuntimeConfig, lines = 30): Promise<string> {
  lines=Math.max(1,Math.min(1000,Math.trunc(lines)));
  const r = await sshExecSafe(cfg.remote.host,
    `tmux capture-pane -t ${shellQuote(cfg.experiment.tmuxSession)} -p -S -${lines} 2>/dev/null`);
  if (r.stdout.trim()) return r.stdout;
  const logPath = path.posix.isAbsolute(cfg.experiment.logFile)?cfg.experiment.logFile:path.posix.join(cfg.remote.projectDir, cfg.experiment.logFile);
  const r2 = await sshExecSafe(cfg.remote.host, `tail -${lines} -- ${shellQuote(logPath)} 2>/dev/null`);
  return r2.stdout || "[no output]";
}

function shellQuote(value: string): string {
  return `'${value.replace(/'/g, `'"'"'`)}'`;
}
function remotePath(cfg:StewardRuntimeConfig,value:string){return path.posix.isAbsolute(value)?value:path.posix.join(cfg.remote.projectDir,value)}

function observationFile(cwd: string): string { return path.join(cwd, ".pi", "steward-observations.json"); }
function legacyObservationFile(cwd: string): string { return path.join(cwd, ".pi", "watchdog-observations.json"); }
function observationEventsFile(cwd: string): string { return path.join(cwd, ".pi", "steward-error-events.jsonl"); }
function observationKey(cfg: StewardRuntimeConfig): string {
  return [cfg.remote.host, cfg.remote.projectDir, cfg.experiment.logFile, cfg.experiment.tmuxSession].join("|");
}
function emptyObservationStore(): ObservationStore { return { version: 1, records: {} }; }
function loadObservations(cwd: string): ObservationStore {
  try {
    const selected=fs.existsSync(observationFile(cwd))?observationFile(cwd):legacyObservationFile(cwd);
    const parsed = JSON.parse(fs.readFileSync(selected, "utf-8")) as ObservationStore;
    if (parsed.version === 1 && parsed.records) return parsed;
  } catch { /* initialize below */ }
  return emptyObservationStore();
}
function saveObservations(cwd: string, store: ObservationStore, event?: Record<string, unknown>) {
  fs.mkdirSync(path.dirname(observationFile(cwd)), { recursive: true });
  const tmp = observationFile(cwd) + `.tmp-${process.pid}`;
  fs.writeFileSync(tmp, JSON.stringify(store, null, 2) + "\n", "utf-8");
  fs.renameSync(tmp, observationFile(cwd));
  if (event) fs.appendFileSync(observationEventsFile(cwd), JSON.stringify({ time: new Date().toISOString(), ...event }) + "\n", "utf-8");
}
function normalizeStackRoot(lines: string[], index: number): string {
  const nearby = lines.slice(Math.max(0, index - 12), index + 15);
  const frame = [...nearby].reverse().find(line => /^\s*File\s+".*",\s+line\s+\d+(?:,\s+in\s+.+)?/.test(line));
  if (frame) return frame.trim().replace(/line\s+\d+/g, "line <N>").replace(/File\s+"[^"]+"/, "File <PATH>");
  return lines[index].trim().replace(/\b\d+\b/g, "<N>").slice(0, 240);
}
function exceptionTypeFor(lines: string[], index: number, matchedPattern: string): string {
  if (matchedPattern !== "Traceback") return matchedPattern;
  for (const line of lines.slice(index + 1, index + 30).reverse()) {
    const m = line.match(/^\s*([A-Za-z_][\w.]*(?:Error|Exception))\s*:/);
    if (m) return m[1];
    if (/CUDA out of memory/i.test(line)) return "CUDA out of memory";
  }
  return "Traceback";
}
function fingerprintId(exceptionType: string, stackRoot: string, command: string, runId: string): string {
  const digest = createHash("sha256").update([exceptionType, stackRoot, command, runId].join("\n")).digest("hex").slice(0, 12);
  return `ERR-${digest}`;
}

interface ErrorScanResult { count: number; openCount: number; text: string; fingerprints: string[]; baseline?: boolean; }

async function scanErrors(cfg: StewardRuntimeConfig, cwd: string): Promise<ErrorScanResult> {
  const logPath = path.posix.isAbsolute(cfg.experiment.logFile)
    ? cfg.experiment.logFile : path.posix.join(cfg.remote.projectDir, cfg.experiment.logFile);
  const quoted = shellQuote(logPath);
  const stat = await sshExecSafe(cfg.remote.host, `stat -c '%d:%i:%s' -- ${quoted} 2>/dev/null`);
  const statText = stat.stdout.trim();
  if (!statText) return { count: 0, openCount: 0, fingerprints: [], text: "ℹ️ No log file" };
  const match = statText.match(/^(\d+):(\d+):(\d+)$/);
  if (!match) return { count: 0, openCount: 0, fingerprints: [], text: "⚠️ Unable to identify log cursor" };
  const [, device, inode, sizeText] = match;
  const size = Number(sizeText);
  const identity = `${device}:${inode}`;
  const store = loadObservations(cwd);
  const key = observationKey(cfg);
  const record = store.records[key] ?? { fingerprints: {} };
  store.records[key] = record;
  const now = new Date().toISOString();

  // First observation establishes an EOF baseline. Historical tail content is not
  // actionable evidence and must not trigger a fresh remediation loop.
  if (!record.cursor) {
    record.cursor = { logIdentity: identity, byteOffset: size, since: now };
    saveObservations(cwd, store, { event: "cursor_initialized", key, logIdentity: identity, byteOffset: size });
    const blocking=Object.values(record.fingerprints).filter(fp=>fp.status==="open"||fp.status==="remediation_applied").length;
    return { count: 0, openCount:blocking, fingerprints: [], baseline: true, text: `ℹ️ Error cursor initialized at byte ${size}; historical log entries were not treated as new errors.${blocking?` ${blocking} existing incident(s) still block completion.`:""}` };
  }

  let rotated = false;
  if (record.cursor.logIdentity !== identity || size < record.cursor.byteOffset) {
    rotated = true;
    record.cursor = { logIdentity: identity, byteOffset: 0, since: now };
    saveObservations(cwd, store, { event: "log_rotated", key, logIdentity: identity, size });
  }

  const start = record.cursor.byteOffset;
  if (size === start) {
    const openCount = Object.values(record.fingerprints).filter(fp => fp.status === "open" || fp.status === "remediation_applied").length;
    const awaitingEvidence = Object.values(record.fingerprints).filter(fp => fp.status === "remediation_applied").length;
    return { count: 0, openCount, fingerprints: [], text:
      `✅ No new error occurrences.${openCount ? ` ${openCount} unresolved fingerprint(s) remain; no retry is authorized without a new occurrence.` : ""}` +
      `${awaitingEvidence ? ` ${awaitingEvidence} remediation(s) await newly appended clean log evidence before resolution.` : ""}` };
  }

  // Read only bytes appended since the prior cursor. Cap each observation to 1 MiB;
  // the cursor advances by the bytes actually consumed, so backlog is not skipped.
  const limit = Math.min(size - start, 1024 * 1024);
  const chunk = await sshExecSafe(cfg.remote.host, `dd if=${quoted} bs=1 skip=${start} count=${limit} status=none 2>/dev/null`, 30);
  if (chunk.exitCode !== 0 && !chunk.stdout) {
    return { count: 0, openCount: Object.values(record.fingerprints).filter(fp => fp.status === "open" || fp.status === "remediation_applied").length, fingerprints: [], text: "⚠️ Failed to read incremental log bytes; cursor was not advanced." };
  }
  const raw = (record.cursor.pendingLine || "") + chunk.stdout;
  const endsWithNewline = raw.endsWith("\n");
  const lines = raw.split("\n");
  record.cursor.pendingLine = endsWithNewline ? "" : (lines.pop() || "");
  // dd was asked for an exact byte count. Advancing by the requested count avoids
  // UTF-8 replacement characters changing Buffer.byteLength when a chunk boundary
  // splits a multibyte character.
  record.cursor.byteOffset = start + limit;
  record.cursor.since = now;

  const seenThisScan = new Set<string>();
  const contexts: string[] = [];
  for (let i = 0; i < lines.length; i++) {
    const pattern = cfg.monitoring.errorPatterns.find(p => lines[i].includes(p));
    if (!pattern) continue;
    const exceptionType = exceptionTypeFor(lines, i, pattern);
    const stackRoot = normalizeStackRoot(lines, i);
    const command = cfg.experiment.tmuxSession;
    const runId = cfg.experiment.description || cfg.experiment.tmuxSession;
    const id = fingerprintId(exceptionType, stackRoot, command, runId);
    if (seenThisScan.has(id)) continue; // one traceback may match Traceback + RuntimeError
    seenThisScan.add(id);
    const context = lines.slice(Math.max(0, i - 2), Math.min(lines.length, i + 5)).join("\n");
    const existing = record.fingerprints[id];
    const reopened = existing?.status === "remediation_applied" || existing?.status === "resolved";
    if (existing) {
      existing.lastSeen = now; existing.occurrences += 1; existing.lastContext = context;
      if (reopened) { existing.status = "open"; existing.resolvedAt = undefined; }
    } else {
      record.fingerprints[id] = { id, exceptionType, normalizedStackRoot: stackRoot, command, runId,
        firstSeen: now, lastSeen: now, occurrences: 1, status: "open", lastContext: context };
    }
    saveObservations(cwd, store, { event: reopened ? "fingerprint_reopened" : existing ? "fingerprint_reoccurred" : "fingerprint_opened", key, fingerprintId: id, exceptionType });
    contexts.push(`${reopened ? "♻️ REOPENED" : "❌ NEW"} ${id} (${exceptionType})\n${context}`);
  }

  // remediation_applied is not resolved by absence alone. The autonomous
  // verifier additionally requires tmux/process recovery and new clean progress.
  saveObservations(cwd, store);
  const openCount = Object.values(record.fingerprints).filter(fp => fp.status === "open" || fp.status === "remediation_applied").length;
  const prefix = rotated ? "Log rotation detected; cursor restarted safely. " : "";
  if (!seenThisScan.size) return { count: 0, openCount, fingerprints: [], text: `✅ ${prefix}No new error occurrences in ${limit} appended byte(s).${openCount ? ` ${openCount} earlier unresolved fingerprint(s) remain, but did not recur.` : ""}` };
  return { count: seenThisScan.size, openCount, fingerprints: [...seenThisScan], text: `${prefix}❌ ${seenThisScan.size} new error fingerprint occurrence(s):\n\n${contexts.slice(0, 10).join("\n\n---\n\n")}` };
}

async function getProgress(cfg: StewardRuntimeConfig): Promise<string> {
  const grep = cfg.monitoring.progressPatterns.map(p => p.replace(/[|]/g, "\\|")).join("|");
  const r = await sshExecSafe(cfg.remote.host,
    `tmux capture-pane -t ${cfg.experiment.tmuxSession} -p -S -100 2>/dev/null | grep -iE "${grep}" | tail -5 || echo "[none]"`);
  if (!r.stdout.trim() || r.stdout.includes("[none]")) return "ℹ️ No progress lines";
  return r.stdout.split("\n").filter(Boolean).slice(-6).map(l => `  ${l.trim()}`).join("\n");
}

// ─── Full Status Check (for tool output) ─────────────────────────────────────

async function fullStatus(config: StewardRuntimeConfig, cwd: string): Promise<string> {
  const parts: string[] = [];
  const add = (label: string, s: string) => parts.push(`## ${label}\n${s}`);
  try { const r = await checkTmuxSession(config); add("Tmux", r.text); } catch (e: any) { add("Tmux", `Err: ${e.message}`); }
  try { const r = await checkTrainingProcess(config); add("Process", r.text); } catch (e: any) { add("Process", `Err: ${e.message}`); }
  try { add("GPU", await checkGPU(config)); } catch (e: any) { add("GPU", `Err: ${e.message}`); }
  try { add("Disk", await checkDisk(config)); } catch (e: any) { add("Disk", `Err: ${e.message}`); }
  try { add("Progress", await getProgress(config)); } catch (e: any) { add("Progress", `Err: ${e.message}`); }
  try { const r = await scanErrors(config, cwd); add("Errors", r.text); } catch (e: any) { add("Errors", `Err: ${e.message}`); }
  return parts.join("\n\n");
}

// ─── Quick Health Check (for autonomous loop — returns structured result) ────

interface QuickCheck {
  healthy: boolean;
  tmuxAlive: boolean;
  processRunning: boolean;
  processVerified:boolean;
  errorCount: number;
  blockingCount:number;
  newErrorFingerprints:string[];
  summary: string;
}

async function quickCheck(config: StewardRuntimeConfig, cwd: string): Promise<QuickCheck> {
  let tmuxAlive = false;
  let processRunning = false;
  let processVerified = false;
  let errorCount = 0;
  let blockingCount = 0;
  let newErrorFingerprints:string[]=[];
  const notes: string[] = [];

  try {
    const r = await checkTmuxSession(config);
    tmuxAlive = r.alive;
    if (!r.alive) notes.push("tmux dead");
  } catch { notes.push("tmux check failed"); }

  try {
    const r = await checkTrainingProcess(config);
    processRunning = r.running;processVerified=r.verified;
    if (!r.running) notes.push("no training process");
  } catch { notes.push("process check failed"); }

  try {
    const r = await scanErrors(config, cwd);
    errorCount = r.count;
    blockingCount=r.openCount;
    newErrorFingerprints=(r.fingerprints||[]).map(String).filter(Boolean);
    if (r.count > 0) notes.push(`${r.count} new error occurrence(s)`);
    else if (r.openCount > 0) notes.push(`${r.openCount} unresolved fingerprint(s), no new occurrence`);
  } catch { notes.push("error scan failed"); }

  const healthy = processVerified && tmuxAlive && processRunning && errorCount === 0;
  return {
    healthy,
    tmuxAlive,
    processRunning,
    processVerified,
    errorCount,
    blockingCount,
    newErrorFingerprints,
    summary: healthy ? "all OK" : notes.join("; "),
  };
}

const COMPLETION_BLOCKED_PHASES=new Set<StewardPhase>(["incident_open","remediation_pending","restarting","verifying_recovery","needs_attention"]);
async function completionCheck(config:StewardRuntimeConfig,cwd:string,processRunning:boolean,processVerified:boolean,phase:StewardPhase,previousStableCount:number,previousArtifacts:any[]=[]){
  const required=[...config.completion.requiredArtifacts,...(config.completion.metricsFile?[config.completion.metricsFile]:[]),...(config.completion.exitCodeFile?[config.completion.exitCodeFile]:[])],artifacts=[] as any[];
  for(const p of required){const r=await sshExecSafe(config.remote.host,`stat -c '%s|%Y' -- ${shellQuote(remotePath(config,p))} 2>/dev/null`),[size,mtime]=r.stdout.trim().split("|");artifacts.push({path:p,exists:r.exitCode===0,size:Number(size||0),mtime:mtime||""})}
  const output=await getRecentOutput(config,500),markersFound=config.completion.completionMarkers.filter(m=>output.includes(m)),store=loadObservations(cwd),record=store.records[observationKey(config)];const openIncidents=record?blockingIncidentCount(Object.values(record.fingerprints)):0;
  let exitCode:number|null=null,exitCodeVerified=false;if(config.completion.exitCodeFile&&!processRunning){const r=await sshExecSafe(config.remote.host,`head -c 64 -- ${shellQuote(remotePath(config,config.completion.exitCodeFile))} 2>/dev/null`),raw=r.stdout.trim();if(r.exitCode===0&&/^-?\d+$/.test(raw)){exitCode=Number(raw);exitCodeVerified=Number.isSafeInteger(exitCode)}}
  const result=evaluateCompletion(config,{markersFound,artifacts,previousArtifacts,processRunning,processVerified,exitCode,exitCodeVerified,openIncidents,blockedPhase:COMPLETION_BLOCKED_PHASES.has(phase)},previousStableCount);return{...result,artifacts,output,exitCode,exitCodeVerified,openIncidents};
}

// ─── Autonomous Check Message Crafting ───────────────────────────────────────

function craftCheckMessage(state: MonitorState): string {
  const n = state.checkCount + 1;
  const base = `[AUTOCHECK #${n}] `;

  if (state.consecutiveErrors >= 3) {
    return base + `There have been ${state.consecutiveErrors} consecutive checks with NEW error occurrences. Run experiment_status and experiment_scan_errors. Do not retry merely by changing wording or strategy: remediation requires a concrete changed input/config/environment or new evidence. If none exists, stop and request human intervention.`;
  }

  if (state.lastCheckResult === "error" || state.lastCheckResult === "crash") {
    return base + `The previous check observed a NEW error occurrence. Run experiment_status and experiment_scan_errors. Diagnose only fingerprints reported NEW/REOPENED. Historical or resolved fingerprints do not authorize another fix. After a concrete remediation, mark that fingerprint remediation_applied; reopen it only if a new post-remediation occurrence is observed.`;
  }

  // Healthy or unknown — light check. Error scanning is cursor-based, so old log
  // entries cannot turn this into an implicit remediation request.
  return base + `Brief health check — run experiment_status. Only NEW/REOPENED error fingerprints are actionable. Historical, unresolved-without-recurrence, or resolved errors must not trigger a new fix. If no new occurrence exists, just report current health concisely.`;
}

// ─── Extension Entry Point ───────────────────────────────────────────────────

export default function (pi: ExtensionAPI) {
  let config: StewardRuntimeConfig | null = null;
  let state: MonitorState = defaultState();
  let checkTimer: ReturnType<typeof setTimeout> | null = null;
  let runtimeCwd = process.cwd();
  let queue: TaskQueueState = emptyTaskQueue();
  let archiveExecutor:((action:"prepare"|"finalize")=>Promise<any>)|null=null;
  let managedLease:{dispatchId:string;token:string;consumer:string;runId:string}|null=null;
  let trialDraft:{runId:string;manifest:any}|null=null;
  const extensionEntry=fileURLToPath(import.meta.url);
  let realExtensionEntry=extensionEntry;
  try{realExtensionEntry=fs.realpathSync(extensionEntry)}catch{/* execute reports an incomplete installation */}
  const surveyctlPath=surveyctlPathFromExtension(extensionEntry,realExtensionEntry);
  function trustedSurveyProject(cwd:string, activeConfig:StewardRuntimeConfig|null):string{
    // A freshly-owned Herdr Pi can call a tool before session_start has
    // replaced the extension host cwd. Prefer the call cwd, then the explicit
    // configured project root; each candidate must prove it is this project.
    for(const candidate of [cwd,activeConfig?.identity.projectRoot||""]){
      if(!candidate)continue;
      const root=path.resolve(candidate);
      if(fs.existsSync(path.join(root,"state.md"))&&fs.existsSync(path.join(root,".survey-tool","runs.json")))return root;
    }
    throw new Error("trusted Survey Tool project cwd is required; launch Herdr with --cwd at the project containing state.md");
  }

  async function surveyctlJson(args:string[]){
    const result=await localExec(process.env.PYTHON||"python3",[surveyctlPath,"--project",runtimeCwd,...args]);
    if(result.exitCode!==0)throw new Error((result.stderr||result.stdout||"surveyctl failed").slice(-2000));
    try{return JSON.parse(result.stdout)}catch{throw new Error("surveyctl returned invalid JSON")}
  }

  function emptyTaskQueue(): TaskQueueState {
    const now = new Date().toISOString();
    return { version: 1, active: false, intervalMinutes: 15, currentTaskId: null, tasks: [], createdAt: now, updatedAt: now };
  }

  function queueFile(): string { return path.join(runtimeCwd, ".pi", "steward-task-queue.json"); }
  function legacyQueueFile(): string { return path.join(runtimeCwd, ".pi", "watchdog-task-queue.json"); }
  function queueEventsFile(): string { return path.join(runtimeCwd, ".pi", "steward-task-events.jsonl"); }

  function loadQueue(): TaskQueueState {
    try {
      const selected=fs.existsSync(queueFile())?queueFile():legacyQueueFile();
      const parsed = JSON.parse(fs.readFileSync(selected, "utf-8")) as TaskQueueState;
      if (parsed.version === 1 && Array.isArray(parsed.tasks)) {
        // Never resume autonomous execution merely because pi restarted.
        return { ...parsed, active: false, currentTaskId: parsed.currentTaskId ?? null };
      }
    } catch { /* start empty */ }
    return emptyTaskQueue();
  }

  function saveQueue(event?: string, details: Record<string, unknown> = {}) {
    queue.updatedAt = new Date().toISOString();
    fs.mkdirSync(path.dirname(queueFile()), { recursive: true });
    const tmp=queueFile()+`.tmp-${process.pid}`; fs.writeFileSync(tmp, JSON.stringify(queue, null, 2) + "\n", "utf-8"); fs.renameSync(tmp,queueFile());
    if (event) {
      fs.appendFileSync(queueEventsFile(), JSON.stringify({ time: queue.updatedAt, event, ...details }) + "\n", "utf-8");
    }
  }

  function normalizeTask(raw: any, index: number): QueueTask {
    const id = String(raw?.id || `T-${String(index + 1).padStart(3, "0")}`);
    const instruction = String(raw?.instruction || "").trim();
    if (!instruction) throw new Error(`Task ${id} is missing instruction`);
    const capability = (["inspect", "implement", "execute_approved"].includes(raw?.capability)
      ? raw.capability : "inspect") as QueueCapability;
    return {
      id, instruction,
      acceptance: Array.isArray(raw?.acceptance) ? raw.acceptance.map(String).filter(Boolean) : [],
      dependsOn: Array.isArray(raw?.depends_on ?? raw?.dependsOn) ? (raw.depends_on ?? raw.dependsOn).map(String) : [],
      capability,
      maxAttempts: Math.max(1, Math.min(5, Number(raw?.max_attempts ?? raw?.maxAttempts ?? 2))),
      attempts: 0,
      onFailure: raw?.on_failure === "continue" || raw?.onFailure === "continue" ? "continue" : "pause",
      status: "pending",
      failureClass: undefined,
      retryBasis: undefined,
    };
  }

  function validateQueueTasks(tasks: QueueTask[]) {
    const ids = new Set<string>();
    for (const task of tasks) {
      if (ids.has(task.id)) throw new Error(`Duplicate task id: ${task.id}`);
      ids.add(task.id);
    }
    for (const task of tasks) {
      for (const dep of task.dependsOn) if (!ids.has(dep)) throw new Error(`${task.id} depends on unknown task ${dep}`);
      if (task.dependsOn.includes(task.id)) throw new Error(`${task.id} cannot depend on itself`);
    }
  }

  function currentQueueTask(): QueueTask | undefined {
    return queue.tasks.find(t => t.id === queue.currentTaskId);
  }

  function nextReadyTask(): QueueTask | undefined {
    return queue.tasks.find(task => task.status === "pending" && task.dependsOn.every(dep => queue.tasks.find(t => t.id === dep)?.status === "completed"));
  }

  function queueSummary(): string {
    const counts = (status: QueueTaskStatus) => queue.tasks.filter(t => t.status === status).length;
    const lines = [
      `## Experiment Steward Task Queue: ${queue.active ? "▶ ACTIVE" : "⏸ PAUSED"}`,
      `**File:** ${queueFile()}`,
      `**Tasks:** ${queue.tasks.length} | pending ${counts("pending")} | running ${counts("running")} | completed ${counts("completed")} | failed ${counts("failed")} | blocked ${counts("blocked")}`,
      `**Current:** ${queue.currentTaskId || "none"}`,
      "",
      ...queue.tasks.map(t => `- [${t.status}] ${t.id} (${t.capability}, attempt ${t.attempts}/${t.maxAttempts}) — ${t.instruction}`),
    ];
    return lines.join("\n");
  }

  function queueTaskMessage(task: QueueTask, continuation = false): string {
    const acceptance = task.acceptance.length ? task.acceptance.map((x, i) => `${i + 1}. ${x}`).join("\n") : "（未提供额外判据；仍需用可检查证据说明完成）";
    return `[EXPERIMENT STEWARD TASK ${task.id}${continuation ? " CONTINUE" : ""}]\n` +
      `用户批准的任务队列正在执行。只处理当前任务，不得自行新增、拆出或提前执行后续任务。\n\n` +
      `任务：${task.instruction}\n能力边界：${task.capability}\n尝试：${task.attempts}/${task.maxAttempts}\n` +
      `验收条件：\n${acceptance}\n\n` +
      `推进规则：\n` +
      `1. 优先完成当前任务要求的实际算法与数据流实现。先复用仍匹配当前代码、配置、数据和环境的已有结果、events、Runs、日志和产物；针对公式、梯度、mask/索引和指标验证具体风险。仅相关入口/依赖/环境变化且缺少证据，或复现具体故障时补最小 smoke，不单独创建凑流程的 smoke Run。检查通过后继续任务。\n` +
      `2. inspect 不得修改或执行；implement 可修改并做与改动成比例的验证，但不得启动正式科学 Run；execute_approved 只授权当前任务文字明确描述的执行，不扩展范围。\n` +
      `3. 长任务放入可观察的 tmux/日志后可结束本轮，Experiment Steward 会继续监控。不要用“仍在运行”冒充完成。\n` +
      `4. 完成全部验收后调用 steward_task_queue action=complete 并附 evidence；无法完成时调用 action=fail，并选择 failure_class。\n` +
      `5. retry 不是换一种说法重做。只有 transient，或 remediation 后的 environment，且 retry_basis 至少包含 changed_input/changed_config/changed_environment/new_evidence 之一时才允许 retry。invalid_spec 退回 Run review；scientific 记录为证据；authorization 等用户；external_dependency 等依赖变化。\n` +
      `6. 涉及 Experiment/Run 时通过 surveyctl.py 写回 canonical 记录；不得直接编辑 .survey-tool JSON。不得执行破坏性动作、泄露密钥、伪造结果或自动更改 Claim verdict。`;
  }

  function dispatchNextTask() {
    if (!queue.active) return;
    let task = currentQueueTask();
    if (task?.status === "running") {
      pi.sendUserMessage(queueTaskMessage(task, true), { deliverAs: "followUp" });
      return;
    }
    task = nextReadyTask();
    if (!task) {
      const unresolved = queue.tasks.filter(t => t.status === "pending");
      if (unresolved.length) {
        unresolved.forEach(t => t.status = "blocked");
        queue.active = false; queue.currentTaskId = null;
        saveQueue("queue_blocked", { tasks: unresolved.map(t => t.id) });
        pi.sendMessage({ customType: "steward-queue", content: `Queue blocked by unmet dependencies: ${unresolved.map(t => t.id).join(", ")}`, display: true });
      } else {
        queue.active = false; queue.currentTaskId = null;
        saveQueue("queue_completed");
        pi.sendMessage({ customType: "steward-queue", content: "✅ Experiment Steward task queue completed.", display: true });
      }
      return;
    }
    task.status = "running"; task.attempts += 1; task.startedAt = new Date().toISOString();
    queue.currentTaskId = task.id;
    saveQueue("task_started", { taskId: task.id, attempt: task.attempts });
    pi.sendUserMessage(queueTaskMessage(task), { deliverAs: "followUp" });
  }

  function scheduleQueueCheck() {
    if (!queue.active) return;
    if (checkTimer) clearTimeout(checkTimer);
    checkTimer = setTimeout(() => dispatchNextTask(), queue.intervalMinutes * 60 * 1000);
  }

  // ── State persistence ──

  function activeRunKey(){const value=String(config?.identity.runId||"");return /^[A-Za-z0-9][A-Za-z0-9._-]{0,159}$/.test(value)?value:""}
  function stateFile(){const key=activeRunKey();return key?path.join(runtimeCwd,".pi","stewards",`${key}.state.json`):path.join(runtimeCwd,".pi","steward-state.json")}
  function stateEventsFile(){const key=activeRunKey();return key?path.join(runtimeCwd,".pi","stewards",`${key}.events.jsonl`):path.join(runtimeCwd,".pi","steward-events.jsonl")}
  function persistState(event?:string,from?:StewardPhase){
    fs.mkdirSync(path.dirname(stateFile()),{recursive:true});const tmp=stateFile()+`.tmp-${process.pid}`;fs.writeFileSync(tmp,JSON.stringify({schema:"survey-tool.experiment-steward-state/v1",version:1,...state},null,2)+"\n");fs.renameSync(tmp,stateFile());
    if(event)fs.appendFileSync(stateEventsFile(),JSON.stringify({time:new Date().toISOString(),event,from,to:state.phase,reason:state.lastReason})+"\n");
  }
  function transition(phase:StewardPhase,reason:string){const from=state.phase;state.phase=phase;state.lastReason=reason;persistState("phase_transition",from)}

  function saveState() {
    pi.appendEntry(STATE_ENTRY_TYPE, { ...state });
    persistState();
  }

  function loadPreviousState(entries: any[]) {
    let loaded=false;try {const disk=JSON.parse(fs.readFileSync(stateFile(),"utf8"));state={...defaultState(),...disk};loaded=true}catch{}
    if(!loaded){for(const entry of [...entries].reverse()){if(entry.type==="custom"&&[STATE_ENTRY_TYPE,LEGACY_STATE_ENTRY_TYPE].includes(entry.customType)&&entry.data){state={...defaultState(),...entry.data};loaded=true;break}}}
    if(loaded){const alreadyPaused=state.pausedAfterRestart===true&&!state.active&&state.phase==="stopped";state.active=false;state.phase="stopped";state.pausedAfterRestart=true;state.lastReason="pi restarted; explicit /steward start required";if(!alreadyPaused)persistState("paused_after_restart")}
  }

  // ── Autonomous loop ──

  function stopMonitoring(reason: string) {
    if (checkTimer) { clearTimeout(checkTimer); checkTimer = null; }
    state.active = false;
    transition("stopped",reason);
    saveState();
  }

  function scheduleNextCheck(initialDelayMs?:number) {
    if (!state.active) return;
    if (checkTimer) clearTimeout(checkTimer);

    const ms = initialDelayMs===undefined ? state.currentInterval * 60 * 1000 : Math.max(250,initialDelayMs); state.nextCheck=new Date(Date.now()+ms).toISOString(); saveState();
    checkTimer = setTimeout(async () => {
      if (!state.active || !config) return;
      try{state.checkCount++;state.lastCheckTime=Date.now();
      const observation=await quickCheck(config,runtimeCwd);state.lastCheckResult=observation.healthy?"ok":observation.errorCount?"error":"crash"; state.healthyStreak=observation.healthy?state.healthyStreak+1:0;
      const progressText=await getProgress(config),previousProgress=state.latestProgressLine;const lines=progressText.split("\n").map(x=>x.trim()).filter(x=>x&&!x.includes("No progress"));state.latestProgressLine=lines[lines.length-1]||"";for(let i=lines.length-1;i>=0;i--){const eta=parseEta(lines[i],config.monitoring.etaRegex);if(eta!=null){state.latestEtaSeconds=eta;state.latestEtaSourceLine=lines[i].trim();break}}
      if(state.phase==="verifying_recovery"&&state.verifyingFingerprintId&&observation.processVerified&&observation.tmuxAlive&&observation.processRunning&&state.latestProgressLine&&state.latestProgressLine!==previousProgress&&observation.errorCount===0){const store=loadObservations(runtimeCwd),record=store.records[observationKey(config)],fp=record?.fingerprints[state.verifyingFingerprintId];const noOccurrenceAfterApply=!!fp?.remediationAppliedAt&&Date.parse(fp.lastSeen||"")<=Date.parse(fp.remediationAppliedAt);if(fp?.status==="remediation_applied"&&noOccurrenceAfterApply){fp.status="resolved";fp.resolvedAt=new Date().toISOString();saveObservations(runtimeCwd,store,{event:"fingerprint_resolved_verified_recovery",fingerprintId:fp.id,progress:state.latestProgressLine.slice(0,500)});state.verifyingFingerprintId=undefined;const remaining=blockingIncidentCount(Object.values(record.fingerprints));transition(remaining?"incident_open":"monitoring",remaining?`${remaining} other blocking incident(s) remain`:"verified current fingerprint recovery with new clean progress")}}
      const completion=await completionCheck(config,runtimeCwd,observation.processRunning,observation.processVerified,state.phase,state.completionStableCount,state.lastCompletionArtifacts||[]);state.completionStableCount=completion.stableCount;state.lastCompletionArtifacts=completion.artifacts.map(x=>({path:x.path,size:x.size,mtime:x.mtime}));
      const decision=decideObservationPhase({currentPhase:state.phase,tmuxAlive:observation.tmuxAlive,processRunning:observation.processRunning,processVerified:observation.processVerified,newErrorFingerprints:observation.newErrorFingerprints,completionContractOk:completion.contractOk,completionComplete:completion.complete});
      transition(decision.phase,decision.reason);
      if(shouldNotifyIncident(state.notifiedIncidentSignature,decision)){state.notifiedIncidentSignature=decision.incidentSignature;const recovery=managedLease?`\n当前 Pi 仍持有 ${managedLease.runId} 的 managed lease。先读取最新日志并诊断；代码、launcher、依赖导入等实现层错误必须先调用 ${trialDraft?.runId===managedLease.runId?"survey_run_trials":"survey_run_execution"} action=repair（附具体错误和 changed evidence）。工具会保留同一批准、dispatch、Campaign 与 Trial manifest，释放 bash guard；修复并聚焦测试后按 run_id 自动重启。修复预算未耗尽时不得 fail，不要绕过 managed executor，也不要向用户索要 dispatch ID 或重新批准。`:"";pi.sendUserMessage(craftCheckMessage(state)+recovery,{deliverAs:"followUp"});}
      if(decision.phase!=="incident_open"&&decision.phase!=="needs_attention")state.notifiedIncidentSignature=undefined;
      if(decision.phase==="completion_candidate"&&completion.complete&&managedLease&&config.identity.runId===managedLease.runId){
        try{
          const completed=await surveyctlJson(["managed-run","complete",managedLease.dispatchId,"--lease-token",managedLease.token,"--consumer",managedLease.consumer]);
          managedLease=null;pi.sendUserMessage(`Managed Run 已按稳定 completion contract 完成并进入 analysis_pending：${JSON.stringify(redactManagedResult(completed))}`,{deliverAs:"followUp"});
        }catch(e:any){
          const message=String(e.message||e);
          if(message.includes("not yet stable"))pi.sendUserMessage("Managed Run 后端正在进行第二次稳定性观察；下次 Steward 检查将继续，不会自动重跑任务。",{deliverAs:"followUp"});
          else{transition("needs_attention",`managed completion failed: ${message.slice(0,500)}`);pi.sendUserMessage(`Managed Run 完成校验失败，需要人工处理：${message.slice(0,1000)}`,{deliverAs:"followUp"});}
        }
      }
      if(decision.archiveEligible){if(config.archive.enabled&&config.archive.autoArchive&&archiveExecutor){try{await archiveExecutor("prepare");await archiveExecutor("finalize")}catch(e:any){transition("needs_attention",`auto archive failed: ${e.message}`);pi.sendUserMessage(`Experiment Steward 自动归档失败，需要人工处理：${e.message}`,{deliverAs:"followUp"})}}}
      state.observationFailureNotified=false;
      }catch(e:any){state.completionStableCount=0;state.currentInterval=config.scheduling.minIntervalMinutes;transition("needs_attention",`structured observation failed: ${e.message}`);if(!state.observationFailureNotified){state.observationFailureNotified=true;pi.sendUserMessage(`Experiment Steward 结构化检查失败，已转 needs_attention 并按安全间隔重试：${String(e.message).slice(0,1000)}`,{deliverAs:"followUp"})}}finally{if(state.active&&config){const decision=decideInterval(config,{phase:state.phase,etaSeconds:state.latestEtaSeconds,healthyStreak:state.healthyStreak});state.currentInterval=Math.max(config.scheduling.minIntervalMinutes,decision.minutes);state.intervalMinutes=state.currentInterval;state.lastReason=`${state.lastReason}; schedule=${decision.reason}`;saveState();scheduleNextCheck()}}
    }, ms);
  }

  function startMonitoring(intervalMinutes: number, immediate=false) {
    if(!config?.experiment.processPattern)throw new Error("启动自动监控前必须配置非空 experiment.processPattern，以限定当前项目/tmux process")
    if (checkTimer) clearTimeout(checkTimer);
    if (queue.active) {
      queue.active = false;
      saveQueue("queue_paused", { reason: "single-experiment monitoring started" });
    }

    state.active = true;
    state.intervalMinutes = intervalMinutes; state.currentInterval=Math.max(config?.scheduling.minIntervalMinutes||2,Math.min(config?.scheduling.maxIntervalMinutes||60,intervalMinutes)); state.phase="monitoring"; state.pausedAfterRestart=false;
    state.checkCount = 0;
    state.lastCheckTime = null;
    state.lastCheckResult = "unknown";
    state.consecutiveErrors = 0;
    saveState();

    // Establish the observation cursor at activation time, not at the first
    // delayed check. Thus errors appended during the monitoring interval are
    // visible, while pre-existing historical errors are a non-actionable baseline.
    if (config) void scanErrors(config, runtimeCwd).catch(() => { /* status check will report read failures */ });

    // Managed launches often fail in their first seconds. Observe those once
    // almost immediately; manual monitoring keeps its configured first delay.
    scheduleNextCheck(immediate?1000:undefined);
  }

  // ── Agent end handler — update state based on check results ──

  pi.on("agent_end", async () => {
    // A queue task that launched a long-running process may end its agent turn
    // without marking completion. Revisit it later instead of falsely advancing.
    if (queue.active && currentQueueTask()?.status === "running") scheduleQueueCheck();
  });

  // ── Commands ──

  const stewardCommand={
    description: "Control Experiment Steward: start [minutes], stop, status, archive",
    async handler(args, ctx) {
      if (!config) {
        ctx.ui.notify("⚠️ No steward config — create .pi/experiment-steward.json", "warn");
        return;
      }

      const parts = (args || "").trim().split(/\s+/);
      const sub = parts[0]?.toLowerCase();

      if (sub === "start") {
        const mins = Number.parseInt(parts[1]) || state.intervalMinutes;
        if (mins < 1) {
          ctx.ui.notify("Interval must be at least 1 minute", "error");
          return;
        }
        startMonitoring(mins);
        const eta = new Date(Date.now() + mins * 60 * 1000).toLocaleTimeString();
        ctx.ui.notify(`🔍 Autonomous monitoring: every ${mins} min (first check ~${eta})`, "info");
        ctx.ui.setStatus("steward",
          `🔍 auto/${mins}m on ${config.remote.host}:${config.experiment.tmuxSession}`);

      } else if (sub === "stop") {
        stopMonitoring("user requested");
        ctx.ui.notify("⏸️ Monitoring stopped", "info");
        ctx.ui.setStatus("steward",
          `${config.remote.host}:${config.experiment.tmuxSession}`);

      } else if (sub === "status" || !sub) {
        const now = Date.now();
        if (state.active) {
          const elapsed = Math.floor((now - state.sessionStartTime) / 60000);
          const sinceLast = state.lastCheckTime
            ? `${Math.floor((now - state.lastCheckTime) / 60000)}m ago`
            : "pending";
          const nextCheck = checkTimer
            ? `~${state.intervalMinutes - Math.floor((now - (state.lastCheckTime || state.sessionStartTime)) / 60000)}m`
            : "n/a";
          ctx.ui.notify(
            `🔍 Active: every ${state.intervalMinutes}m | Checks: ${state.checkCount} | Last: ${sinceLast} | Next: ${nextCheck} | Result: ${state.lastCheckResult}${state.consecutiveErrors > 0 ? ` (${state.consecutiveErrors}x errors)` : ""}`,
            "info",
          );
        } else {
          ctx.ui.notify(
            `⏸️ Inactive | Config: ${config.remote.host}:${config.experiment.tmuxSession}`,
            "info",
          );
        }

      } else if(sub==="archive") {
        ctx.ui.notify("归档必须通过 experiment_steward_archive inspect/prepare/finalize，并满足完整 completion contract。", "info");
      } else {
        ctx.ui.notify("Usage: /steward start [minutes] | stop | status | archive", "warn");
      }
    },
  };
  pi.registerCommand("steward",stewardCommand);
  pi.registerCommand("watchdog",{description:"DEPRECATED alias: use /steward",async handler(args,ctx){ctx.ui.notify("/watchdog 已弃用；请迁移到 /steward（本次仍兼容执行）。","warn");return stewardCommand.handler(args,ctx)}});

  // ── Tool: watchdog_control (LLM-accessible version of commands) ──

  const stewardControlTool={
    name: "experiment_steward_control",
    label: "Experiment Steward Control",
    description:
      "Start or stop autonomous Experiment Steward monitoring for a configured experiment.",
    promptSnippet: "Control autonomous experiment monitoring (start/stop/status)",
    promptGuidelines: [
      "Use experiment_steward_control to start autonomous monitoring when the user says they'll be AFK.",
      "Default interval is 30 minutes unless the user specifies otherwise.",
      "Use experiment_steward_control to stop monitoring when the user returns.",
    ],
    parameters: Type.Object({
      action: Type.String({ description: "Action: 'start', 'stop', or 'status'" }),
      interval_minutes: Type.Optional(
        Type.Number({ description: "Check interval in minutes (only for 'start', default: 30)" }),
      ),
    }),
    async execute(_id, params, _signal, _onUpdate, ctx) {
      if (!config) {
        return {
          content: [{ type: "text", text: "⚠️ No Experiment Steward config found. Create .pi/experiment-steward.json first." }],
          details: {},
        };
      }

      const action = params.action?.toLowerCase();

      if (action === "start") {
        const mins = params.interval_minutes || 30;
        startMonitoring(mins);
        const eta = new Date(Date.now() + mins * 60 * 1000).toLocaleTimeString();
        return {
          content: [{
            type: "text",
            text: `🔍 Autonomous monitoring started: every ${mins} minutes.\n` +
              `   First check: ~${eta}\n` +
              `   Experiment: ${config.remote.host}:${config.experiment.tmuxSession}\n` +
              `   Run /steward stop to disable.`,
          }],
          details: { active: true, interval: mins },
        };
      }

      if (action === "stop") {
        stopMonitoring("user requested via tool");
        return {
          content: [{ type: "text", text: "⏸️ Autonomous monitoring stopped." }],
          details: { active: false },
        };
      }

      // status
      const now = Date.now();
      const lines: string[] = [];
      lines.push(`## Experiment Steward Status: ${state.active ? "🔍 ACTIVE" : "⏸️ INACTIVE"}`);
      lines.push(`**Remote:** ${config.remote.host}:${config.remote.projectDir}`);
      lines.push(`**Experiment:** ${config.experiment.description || config.experiment.tmuxSession}`);
      lines.push(`**tmux:** ${config.experiment.tmuxSession}`);
      if (state.active) {
        lines.push(`**Interval:** ${state.intervalMinutes} minutes`);
        lines.push(`**Checks:** ${state.checkCount}`);
        lines.push(`**Last result:** ${state.lastCheckResult}${state.consecutiveErrors > 0 ? ` (${state.consecutiveErrors} consecutive errors)` : ""}`);
        if (state.lastCheckTime) {
          lines.push(`**Last check:** ${new Date(state.lastCheckTime).toLocaleString()}`);
        }
      }
      return {
        content: [{ type: "text", text: lines.join("\n") }],
        details: { ...state, configured: true },
      };
    },
  };
  pi.registerTool(stewardControlTool);
  pi.registerTool({...stewardControlTool,name:"watchdog_control",label:"DEPRECATED: Steward Control",description:"DEPRECATED alias; migrate to experiment_steward_control. Functionality is temporarily preserved.",async execute(...args:any[]){const r=await (stewardControlTool.execute as any)(...args);r.content=[{type:"text",text:"⚠️ watchdog_control 已弃用，请迁移到 experiment_steward_control。\n\n"+r.content.map((x:any)=>x.text||"").join("\n")}];return r}} as any);

  // ── Tool: bounded multi-task queue ──

  const stewardQueueTool={
    name: "steward_task_queue",
    label: "Steward Task Queue",
    description:
      "Manage a persistent, user-approved task queue that Experiment Steward can execute sequentially. " +
      "Tasks have explicit instructions, acceptance criteria, dependencies, capability bounds, and retry limits.",
    promptSnippet: "Create, start, pause, inspect, and advance a bounded Experiment Steward task queue",
    promptGuidelines: [
      "Use steward_task_queue when the user asks Experiment Steward to complete several tasks continuously, not merely monitor one experiment.",
      "Never invent queue tasks or broaden their scope. The user must provide or approve the ordered tasks.",
      "For a running queue task, call steward_task_queue complete only with concrete evidence satisfying its acceptance criteria; call fail for a real blocker.",
      "A task queue does not override formal experiment authorization, destructive-action prohibitions, secret protection, or human Claim verdict gates.",
    ],
    parameters: Type.Object({
      action: Type.String({ description: "set, add, start, pause, resume, status, complete, fail, or skip" }),
      tasks: Type.Optional(Type.Array(Type.Object({
        id: Type.Optional(Type.String()),
        instruction: Type.String(),
        acceptance: Type.Optional(Type.Array(Type.String())),
        depends_on: Type.Optional(Type.Array(Type.String())),
        capability: Type.Optional(Type.String({ description: "inspect, implement, or execute_approved" })),
        max_attempts: Type.Optional(Type.Number()),
        on_failure: Type.Optional(Type.String({ description: "pause or continue" })),
      }))),
      task_id: Type.Optional(Type.String()),
      evidence: Type.Optional(Type.String()),
      reason: Type.Optional(Type.String()),
      failure_class: Type.Optional(Type.String({ description: "transient, environment, invalid_spec, scientific, authorization, or external_dependency (required for fail)" })),
      retry_basis: Type.Optional(Type.Object({
        changed_input: Type.Optional(Type.String()),
        changed_config: Type.Optional(Type.String()),
        changed_environment: Type.Optional(Type.String()),
        new_evidence: Type.Optional(Type.String()),
      })),
      interval_minutes: Type.Optional(Type.Number({ description: "Long-task revisit interval; default 15 minutes" })),
    }),
    async execute(_id, params, _signal, _onUpdate, ctx) {
      const action = String(params.action || "status").toLowerCase();

      if (action === "set" || action === "add") {
        if (!params.tasks?.length) throw new Error(`${action} requires a non-empty tasks array`);
        const base = action === "add" ? [...queue.tasks] : [];
        const incoming = params.tasks.map((task, i) => normalizeTask(task, base.length + i));
        const combined = [...base, ...incoming];
        validateQueueTasks(combined);
        if (action === "set") {
          queue = emptyTaskQueue();
          queue.tasks = incoming;
        } else queue.tasks = combined;
        queue.active = false; queue.currentTaskId = null;
        saveQueue(action === "set" ? "queue_set" : "queue_added", { tasks: incoming.map(t => t.id) });
        return { content: [{ type: "text", text: queueSummary() }], details: { queue } };
      }

      if (action === "start" || action === "resume") {
        if (!queue.tasks.length) throw new Error("Task queue is empty; set tasks first");
        const executable = queue.tasks.filter(t => t.status === "pending" && t.capability === "execute_approved");
        if (executable.length) {
          if (!ctx.hasUI) throw new Error("Queue contains execute_approved tasks and requires interactive human confirmation before start");
          const approved = await ctx.ui.confirm(
            "确认连续任务的执行授权",
            `以下任务可启动其文字明确描述的正式执行：${executable.map(t => t.id).join(", ")}。授权不扩展到队列外任务，是否启动？`,
          );
          if (!approved) throw new Error("User did not authorize execute_approved queue tasks");
        }
        if (params.interval_minutes !== undefined) queue.intervalMinutes = Math.max(1, Number(params.interval_minutes));
        // Monitoring and queue execution share one scheduler; make the active mode explicit.
        if (state.active) stopMonitoring("task queue started");
        queue.active = true;
        saveQueue(action === "start" ? "queue_started" : "queue_resumed");
        setTimeout(() => dispatchNextTask(), 0);
        return { content: [{ type: "text", text: `▶ Queue ${action}ed.\n\n${queueSummary()}` }], details: { queue } };
      }

      if (action === "pause") {
        queue.active = false;
        if (checkTimer) { clearTimeout(checkTimer); checkTimer = null; }
        saveQueue("queue_paused", { reason: params.reason || "user requested" });
        return { content: [{ type: "text", text: `⏸ Queue paused. Current task state is preserved.\n\n${queueSummary()}` }], details: { queue } };
      }

      if (action === "complete") {
        const task = currentQueueTask();
        if (!task || task.status !== "running") throw new Error("No running queue task to complete");
        if (params.task_id && params.task_id !== task.id) throw new Error(`Current task is ${task.id}, not ${params.task_id}`);
        const evidence = String(params.evidence || "").trim();
        if (!evidence) throw new Error("Completion requires concrete evidence for the acceptance criteria");
        task.status = "completed"; task.result = evidence; task.finishedAt = new Date().toISOString();
        queue.currentTaskId = null;
        saveQueue("task_completed", { taskId: task.id, evidence });
        setTimeout(() => dispatchNextTask(), 0);
        return { content: [{ type: "text", text: `✅ ${task.id} completed with recorded evidence. Advancing to the next ready task.` }], details: { queue } };
      }

      if (action === "fail") {
        const task = currentQueueTask();
        if (!task || task.status !== "running") throw new Error("No running queue task to fail");
        if (params.task_id && params.task_id !== task.id) throw new Error(`Current task is ${task.id}, not ${params.task_id}`);
        const reason = String(params.reason || "").trim();
        if (!reason) throw new Error("Failure requires the real blocker or error");
        const allowedClasses: FailureClass[] = ["transient", "environment", "invalid_spec", "scientific", "authorization", "external_dependency"];
        const failureClass = String(params.failure_class || "") as FailureClass;
        if (!allowedClasses.includes(failureClass)) throw new Error(`Failure requires failure_class: ${allowedClasses.join(", ")}`);
        const rawBasis = params.retry_basis || {};
        const retryBasis: RetryBasis = {
          changedInput: String(rawBasis.changed_input || "").trim() || undefined,
          changedConfig: String(rawBasis.changed_config || "").trim() || undefined,
          changedEnvironment: String(rawBasis.changed_environment || "").trim() || undefined,
          newEvidence: String(rawBasis.new_evidence || "").trim() || undefined,
        };
        const hasChangedEvidence = Object.values(retryBasis).some(Boolean);
        task.result = reason; task.failureClass = failureClass; task.retryBasis = retryBasis; task.finishedAt = new Date().toISOString();
        queue.currentTaskId = null;

        const classAllowsRetry = failureClass === "transient" || failureClass === "environment";
        if (task.attempts < task.maxAttempts && classAllowsRetry && hasChangedEvidence) {
          task.status = "pending";
          saveQueue("task_retry_scheduled", { taskId: task.id, attempt: task.attempts, reason, failureClass, retryBasis });
          setTimeout(() => dispatchNextTask(), 0);
          return { content: [{ type: "text", text: `↻ ${task.id} retry scheduled because ${failureClass} failure has recorded changed evidence: ${Object.entries(retryBasis).filter(([, v]) => v).map(([k]) => k).join(", ")}.` }], details: { queue } };
        }

        task.status = failureClass === "authorization" || failureClass === "external_dependency" || failureClass === "invalid_spec" ? "blocked" : "failed";
        // These classes require a human/spec/dependency transition, never an automatic retry.
        // A scientific failure is retained as evidence but is not marked completed: doing so
        // would falsely satisfy dependent tasks.
        if (failureClass === "invalid_spec" || failureClass === "authorization" || failureClass === "external_dependency") queue.active = false;
        else if (task.onFailure === "pause" && task.status === "failed") queue.active = false;
        const noRetryReason = !classAllowsRetry
          ? `${failureClass} failures are not automatically retryable`
          : !hasChangedEvidence
            ? "retry_basis contains no changed input/config/environment or new evidence"
            : `maxAttempts ${task.maxAttempts} reached`;
        saveQueue("task_retry_denied", { taskId: task.id, reason, failureClass, retryBasis, noRetryReason, status: task.status });
        if (queue.active) setTimeout(() => dispatchNextTask(), 0);
        return { content: [{ type: "text", text: `❌ ${task.id}: ${noRetryReason}. Status=${task.status}; failure evidence is retained; queue ${queue.active ? "will continue" : "is paused"}.` }], details: { queue } };
      }

      if (action === "skip") {
        const id = params.task_id || queue.currentTaskId;
        const task = queue.tasks.find(t => t.id === id);
        if (!task) throw new Error("Unknown task to skip");
        task.status = "skipped"; task.result = String(params.reason || "explicitly skipped"); task.finishedAt = new Date().toISOString();
        if (queue.currentTaskId === task.id) queue.currentTaskId = null;
        saveQueue("task_skipped", { taskId: task.id, reason: task.result });
        if (queue.active) setTimeout(() => dispatchNextTask(), 0);
        return { content: [{ type: "text", text: `⏭ ${task.id} skipped.\n\n${queueSummary()}` }], details: { queue } };
      }

      return { content: [{ type: "text", text: queueSummary() }], details: { queue } };
    },
  };
  pi.registerTool(stewardQueueTool);
  pi.registerTool({...stewardQueueTool,name:"watchdog_task_queue",label:"DEPRECATED: Steward Task Queue",description:"DEPRECATED alias; migrate to steward_task_queue. Functionality is temporarily preserved.",async execute(...args:any[]){const r=await (stewardQueueTool.execute as any)(...args);r.content=[{type:"text",text:"⚠️ watchdog_task_queue 已弃用，请迁移到 steward_task_queue。\n\n"+r.content.map((x:any)=>x.text||"").join("\n")}];return r}} as any);

  // ── Existing Tools ──

  const experimentStatusTool={
    name: "experiment_status",
    label: "Experiment Status",
    description:
      "Comprehensive health check of a remote ML experiment. Checks tmux session, training process, GPU usage, disk space, recent output, and scans for errors.",
    promptSnippet: "Check remote ML experiment health (tmux, GPU, process, errors)",
    promptGuidelines: [
      "Use experiment_status when the user asks about experiment status, during autonomous checks, or after a fix to verify recovery.",
      "Look for ❌ indicators and warnings. Analyze errors and suggest fixes.",
      "If errors found, use experiment_scan_errors for detailed error analysis.",
    ],
    parameters: Type.Object({}),
    async execute() {
      if (!config) {
        return {
          content: [{ type: "text", text: "⚠️ No Experiment Steward config found. Create .pi/experiment-steward.json in your project. Use experiment_steward_config to see the expected format." }],
          details: { configured: false },
        };
      }
      return {
        content: [{ type: "text", text: await fullStatus(config, runtimeCwd) }],
        details: { configured: true, host: config.remote.host },
      };
    },
  };
  pi.registerTool(experimentStatusTool);

  pi.registerTool({
    name: "experiment_log",
    label: "Experiment Log",
    description: "View recent experiment output from tmux or log file.",
    promptSnippet: "View recent experiment output (last N lines)",
    parameters: Type.Object({
      lines: Type.Optional(Type.Number({ description: "Lines to retrieve (default: 50)" })),
    }),
    async execute(_id, params) {
      if (!config) {
        return { content: [{ type: "text", text: "⚠️ No Experiment Steward config found." }], details: {} };
      }
      const output = await getRecentOutput(config, params.lines ?? 50);
      return { content: [{ type: "text", text: output || "[no output]" }], details: { lines: params.lines ?? 50 } };
    },
  });

  pi.registerTool({
    name: "experiment_scan_errors",
    label: "Scan Experiment Errors",
    description: "Incrementally scan only newly appended log bytes, fingerprint errors, or record remediation/resolution lifecycle changes.",
    promptSnippet: "Scan remote experiment logs for error patterns",
    promptGuidelines: [
      "Use experiment_scan_errors after experiment_status reports a NEW/REOPENED fingerprint or when the user suspects a new issue.",
      "Historical or resolved fingerprints do not authorize remediation. After applying a concrete fix, call action=mark_remediation with fingerprint and remediation. A fingerprint reopens only on a new post-remediation occurrence.",
    ],
    parameters: Type.Object({
      action: Type.Optional(Type.String({ description: "scan (default), mark_remediation, resolve, or reset_cursor" })),
      fingerprint: Type.Optional(Type.String({ description: "ERR-... for lifecycle updates" })),
      remediation: Type.Optional(Type.String({ description: "Concrete remediation applied; required for mark_remediation" })),
    }),
    async execute(_id, params) {
      if (!config) return { content: [{ type: "text", text: "⚠️ No config." }], details: {} };
      const action = String(params.action || "scan").toLowerCase();
      const store = loadObservations(runtimeCwd);
      const key = observationKey(config);
      const record = store.records[key] ?? { fingerprints: {} };
      store.records[key] = record;
      if (action === "reset_cursor") {
        record.cursor = undefined;
        saveObservations(runtimeCwd, store, { event: "cursor_reset", key });
        return { content: [{ type: "text", text: "Cursor reset. The next scan will establish a new EOF baseline; historical errors will not be actionable." }], details: { reset: true } };
      }
      if (action === "mark_remediation" || action === "resolve") {
        const id = String(params.fingerprint || "");
        const fp = record.fingerprints[id];
        if (!fp) throw new Error(`Unknown fingerprint ${id}`);
        const now = new Date().toISOString();
        if (action === "mark_remediation") {
          const remediation = String(params.remediation || "").trim();
          if (!remediation) throw new Error("mark_remediation requires a concrete remediation");
          fp.remediation = remediation; fp.remediationAppliedAt = now; fp.status = "remediation_applied";state.verifyingFingerprintId=id;transition("verifying_recovery","external remediation recorded; awaiting verified recovery");
          saveObservations(runtimeCwd, store, { event: "remediation_applied", key, fingerprintId: id, remediation });
          return { content: [{ type: "text", text: `${id} marked remediation_applied. It will reopen only if the same fingerprint occurs in newly appended post-remediation log bytes.` }], details: { fingerprint: fp } };
        }
        fp.status = "resolved"; fp.resolvedAt = now;if(state.verifyingFingerprintId===id){state.verifyingFingerprintId=undefined;transition("monitoring","fingerprint resolved by explicit human/external verification")}
        saveObservations(runtimeCwd, store, { event: "fingerprint_resolved_human_external_verification", key, fingerprintId: id });
        return { content: [{ type: "text", text: `${id} marked resolved. Historical occurrences will not trigger a fix.` }], details: { fingerprint: fp } };
      }
      const result = await scanErrors(config, runtimeCwd);
      return { content: [{ type: "text", text: result.text }], details: { errorCount: result.count, openCount: result.openCount, fingerprints: result.fingerprints, baseline: result.baseline || false } };
    },
  });

  pi.registerTool({
    name:"experiment_steward_remediation",label:"Experiment Steward Remediation",
    description:"列出或应用人类预设 playbook；不接受任意命令。requiresCodeEdit 只生成 experiment_code_edit 协调要求。",
    parameters:Type.Object({action:Type.String({description:"list, apply, record_code_fix"}),fingerprint:Type.Optional(Type.String()),playbook_id:Type.Optional(Type.String()),evidence:Type.Optional(Type.String())}),
    async execute(_id,params){
      if(!config)throw new Error("No steward config");const action=String(params.action||"list");const store=loadObservations(runtimeCwd),record=store.records[observationKey(config)]??{fingerprints:{}};
      if(action==="list")return{content:[{type:"text",text:JSON.stringify({enabled:config.remediation.enabled,restartCount:state.restartCount,maxRestarts:config.remediation.maxRestarts,playbooks:config.remediation.playbooks.map(p=>({id:p.id,requiresCodeEdit:p.requiresCodeEdit,fingerprints:p.fingerprints,errorPatterns:p.errorPatterns,commands:p.commands}))},null,2)}],details:{policy:redact(config.remediation)}};
      const fp=record.fingerprints[String(params.fingerprint||"")];if(!fp||fp.status!=="open")throw new Error("必须指定 NEW/REOPENED 且仍 open 的 fingerprint");const pb=config.remediation.playbooks.find(p=>p.id===params.playbook_id);if(!config.remediation.enabled||!pb)throw new Error("remediation 未启用或 playbook 未配置");
      if(!pb.fingerprints.includes(fp.id)&&!pb.errorPatterns.some(p=>fp.exceptionType.includes(p)||fp.lastContext.includes(p)))throw new Error("fingerprint 与 playbook 不匹配");
      if(action==="record_code_fix") {const evidence=String(params.evidence||"").trim();if(!pb.requiresCodeEdit||!evidence)throw new Error("record_code_fix 只接受 requiresCodeEdit playbook 的外部 changed evidence");const attemptId=`attempt-${createHash("sha256").update(`${fp.id}|${pb.id}|${fp.occurrences}|${Date.now()}`).digest("hex").slice(0,16)}`;fp.remediation=evidence;fp.remediationAppliedAt=new Date().toISOString();fp.status="remediation_applied";fp.lastAppliedOccurrence=fp.occurrences;fp.lastAppliedPlaybookId=pb.id;fp.lastAttemptId=attemptId;state.verifyingFingerprintId=fp.id;saveObservations(runtimeCwd,store,{event:"external_code_fix_recorded",attemptId,fingerprintId:fp.id,playbookId:pb.id,evidence:evidence.slice(0,2000)});transition("verifying_recovery","external code fix recorded; awaiting clean progress");return{content:[{type:"text",text:"已记录外部修复证据；未声称插件执行了代码修改。至少一次 tmux/process 恢复且有新增 clean progress 后才能 resolved。"}],details:{recorded:true,attemptId}}}
      if(action!=="apply")throw new Error("unknown remediation action");if(fp.lastAppliedOccurrence===fp.occurrences&&fp.lastAppliedPlaybookId===pb.id)throw new Error("同一 occurrence/playbook 已 apply；必须等待新 occurrence 或提供外部 changed evidence");const attemptId=`attempt-${createHash("sha256").update(`${fp.id}|${pb.id}|${fp.occurrences}|${Date.now()}`).digest("hex").slice(0,16)}`;fp.lastAppliedOccurrence=fp.occurrences;fp.lastAppliedPlaybookId=pb.id;fp.lastAttemptId=attemptId;saveObservations(runtimeCwd,store,{event:"remediation_apply_attempt",attemptId,fingerprintId:fp.id,playbookId:pb.id,occurrence:fp.occurrences});if(pb.requiresCodeEdit){transition("remediation_pending","requires experiment_code_edit delegation");return{content:[{type:"text",text:"此 playbook 需要代码修改，插件不会执行。请协调 pi 查询项目有效 experiment_code_edit 路由并委派，完成后用 record_code_fix 提交 changed evidence。不得硬编码 Agent/model。"}],details:{requiresCodeEdit:true,playbookId:pb.id,fingerprint:fp.id,attemptId}}}
      if(!restartAllowed(!!pb.restartCommand,state.restartCount,config.remediation.maxRestarts)) {transition("needs_attention","restart budget exhausted");throw new Error("restart budget exhausted")}
      transition("remediation_pending",`playbook ${pb.id} gated`);const results=[] as any[];for(const command of pb.commands){const r=await sshExecSafe(config.remote.host,command,120);results.push({command,exitCode:r.exitCode,stdout:r.stdout.slice(-4000),stderr:r.stderr.slice(-4000)});if(r.exitCode!==0){saveObservations(runtimeCwd,store,{event:"remediation_apply_failed",attemptId,fingerprintId:fp.id,playbookId:pb.id,exitCode:r.exitCode});transition("needs_attention",`playbook ${pb.id} command failed`);return{content:[{type:"text",text:"playbook 命令失败；已停止，不会继续重启。"}],details:{attemptId,results:redact(results)}}}}
      if(pb.restartCommand){state.restartCount++;transition("restarting",`playbook ${pb.id} restart`);saveObservations(runtimeCwd,store,{event:"restart_attempt",attemptId,fingerprintId:fp.id,playbookId:pb.id,restartCount:state.restartCount});const rr=await sshExecSafe(config.remote.host,pb.restartCommand,120);results.push({command:pb.restartCommand,exitCode:rr.exitCode,stdout:rr.stdout.slice(-4000),stderr:rr.stderr.slice(-4000)});saveObservations(runtimeCwd,store,{event:rr.exitCode===0?"restart_sent":"restart_failed",attemptId,fingerprintId:fp.id,playbookId:pb.id,restartCount:state.restartCount,exitCode:rr.exitCode});if(rr.exitCode!==0){transition("needs_attention","restart failed");return{content:[{type:"text",text:"restart 失败，已转人工处理。"}],details:{attemptId,results:redact(results)}}}}
      fp.remediation=`playbook:${pb.id}`;fp.remediationAppliedAt=new Date().toISOString();fp.status="remediation_applied";fp.lastAppliedOccurrence=fp.occurrences;fp.lastAppliedPlaybookId=pb.id;fp.lastAttemptId=attemptId;state.verifyingFingerprintId=fp.id;saveObservations(runtimeCwd,store,{event:"remediation_applied",attemptId,fingerprintId:fp.id,playbookId:pb.id,results:redact(results)});transition("verifying_recovery","awaiting tmux/process and new clean progress");return{content:[{type:"text",text:"playbook 已执行；现在处于 verifying_recovery，尚未宣称恢复。"}],details:{attemptId,results:redact(results),phase:state.phase}};
    }
  });

  function archiveRoot(cfg:StewardRuntimeConfig){const project=path.resolve(cfg.identity.projectRoot||runtimeCwd),local=path.resolve(project,cfg.archive.localDir);if(local!==project&&!local.startsWith(project+path.sep))throw new Error("archive.localDir 必须位于 identity.projectRoot 内");return local}
  function atomicText(file:string,value:string){fs.mkdirSync(path.dirname(file),{recursive:true});const tmp=`${file}.tmp-${process.pid}`;fs.writeFileSync(tmp,value,"utf8");fs.renameSync(tmp,file)}
  function sanitizeEvidence(value:string){return value.split("\n").map(line=>/^\s*(?:\$|python\d*|bash|sh|ssh|tmux|sudo)\b/.test(line)||/\bprompt\b/i.test(line)?"[REDACTED_COMMAND_OR_PROMPT_LINE]":line).join("\n")}
  async function boundedRemoteContent(file:string|undefined,limit=65536){if(!file)return{status:"unavailable",content:"",sha256:"",truncated:false,size:0};const stat=await sshExecSafe(config!.remote.host,`stat -c '%s' -- ${shellQuote(file)} 2>/dev/null`);if(stat.exitCode!==0||!/^\d+$/.test(stat.stdout.trim()))return{status:"unavailable",content:"",sha256:"",truncated:false,size:0};const size=Number(stat.stdout.trim()),r=await sshExecSafe(config!.remote.host,`head -c ${limit} -- ${shellQuote(file)} 2>/dev/null`),h=await sshExecSafe(config!.remote.host,`sha256sum -- ${shellQuote(file)} 2>/dev/null | cut -d' ' -f1`);return{status:"available",content:redact(sanitizeEvidence(r.stdout.slice(0,limit))),sha256:h.stdout.trim(),truncated:size>limit,size}}
  async function collectArchiveObservation(){
    if(!config)throw new Error("No steward config");const proc=await checkTrainingProcess(config),completion=await completionCheck(config,runtimeCwd,proc.running,proc.verified,state.phase,state.completionStableCount,state.lastCompletionArtifacts||[]),rawRows:any[]=[];
    const inventoryRoots=[...new Set([...config.archive.includePaths,...config.completion.requiredArtifacts,...(config.completion.metricsFile?[config.completion.metricsFile]:[]),...(config.completion.exitCodeFile?[config.completion.exitCodeFile]:[])])];for(const include of inventoryRoots){const q=shellQuote(remotePath(config,include)),r=await sshExecSafe(config.remote.host,`if test -d ${q}; then find ${q} -type f -printf '%p|file|%s|%T@\n' | sort | head -n ${config.archive.maxFiles+1}; elif test -e ${q}; then stat -c '%n|%F|%s|%Y' -- ${q}; else printf '%s|missing|0|\n' ${q}; fi`);for(const line of r.stdout.trim().split("\n").filter(Boolean)){const[p,type,size,mtime]=line.split("|");rawRows.push({path:p,type,size:Number(size||0),mtime,exists:type!=="missing"})}}
    const window=inventoryWindow(rawRows,config.archive.maxFiles,config.archive.maxTotalBytes),inventory=[] as any[];for(const row of window.items){const h=row.exists&&row.type==="file"?await sshExecSafe(config.remote.host,`sha256sum -- ${shellQuote(row.path)} 2>/dev/null | cut -d' ' -f1`):null;inventory.push({...row,sha256:h?.stdout.trim()||""})}
    const store=loadObservations(runtimeCwd),record=store.records[observationKey(config)],errorLifecycle=Object.values(record?.fingerprints||{}).slice(0,500).map(fp=>({id:fp.id,type:fp.exceptionType,status:fp.status,occurrences:fp.occurrences,firstSeen:fp.firstSeen,lastSeen:fp.lastSeen,remediationAppliedAt:fp.remediationAppliedAt,resolvedAt:fp.resolvedAt,remediation:fp.remediation?{recorded:true,sha256:createHash("sha256").update(String(fp.remediation)).digest("hex")}: {recorded:false},attemptId:fp.lastAttemptId}));
    const eventsPath=observationEventsFile(runtimeCwd),remediationEvents=fs.existsSync(eventsPath)?fs.readFileSync(eventsPath,"utf8").trim().split("\n").slice(-100).map(x=>{try{const e=JSON.parse(x);return redact({time:e.time,event:e.event,attemptId:e.attemptId,fingerprintId:e.fingerprintId,playbookId:e.playbookId,exitCode:e.exitCode})}catch{return null}}).filter(Boolean):[];
    const {output:_completionOutput,...completionSafe}=completion;return{completion:completionSafe,inventory,truncated:window.truncated,totalBytes:window.totalBytes,inventoryIdentity:manifestHash(inventory),errorLifecycle,remediationEvents,logTail:await boundedRemoteContent(remotePath(config,config.experiment.logFile)),metrics:await boundedRemoteContent(config.completion.metricsFile?remotePath(config,config.completion.metricsFile):"")}
  }
  function archiveStatus(){return{phase:state.phase,archiveId:state.archiveId||null,enabled:config?.archive.enabled||false,mode:config?.archive.mode}}
  const stewardArchiveTool={name:"experiment_steward_archive",label:"Experiment Steward Archive",description:"检查、准备、终结严格 completion contract 的 manifest_reference 归档。",parameters:Type.Object({action:Type.String({description:"inspect, prepare, finalize, status"}),force:Type.Optional(Type.Boolean())}),async execute(_id,params){
    if(!config)throw new Error("No steward config");const action=String(params.action||"status");if(action==="status")return{content:[{type:"text",text:JSON.stringify(archiveStatus(),null,2)}],details:archiveStatus()};const collected=await collectArchiveObservation();
    if(action==="inspect")return{content:[{type:"text",text:JSON.stringify({completion:collected.completion,inventory:collected.inventory,truncated:collected.truncated,totalBytes:collected.totalBytes,phase:state.phase},null,2).slice(0,65536)}],details:redact(collected)};
    if(!config.archive.enabled||!collected.completion.complete||COMPLETION_BLOCKED_PHASES.has(state.phase))throw new Error("严格 completion contract 尚未连续满足或仍处于修复/人工处理 phase；force 不能绕过");const archiveId=stableArchiveId(config.identity,collected.inventoryIdentity),dir=path.join(archiveRoot(config),config.identity.runId||"unknown-run",archiveId),manifestPath=path.join(dir,"manifest.json"),summaryPath=path.join(dir,"summary.md");fs.mkdirSync(dir,{recursive:true});
    if(action==="prepare"){transition("archiving","preparing strict manifest archive");const cfgSummary={identity:config.identity,remote:{host:config.remote.host,projectDir:config.remote.projectDir},experiment:{tmuxSession:config.experiment.tmuxSession,logFile:config.experiment.logFile,processPatternConfigured:!!config.experiment.processPattern},monitoring:{errorPatterns:config.monitoring.errorPatterns,progressPatterns:config.monitoring.progressPatterns,gpuWarningPercent:config.monitoring.gpuWarningPercent},scheduling:config.scheduling,completion:config.completion,archive:{...config.archive},remediation:{enabled:config.remediation.enabled,maxRestarts:config.remediation.maxRestarts,playbooks:config.remediation.playbooks.map(p=>({id:p.id,requiresCodeEdit:p.requiresCodeEdit,fingerprintCount:p.fingerprints.length,errorPatternCount:p.errorPatterns.length}))}};const manifest:any=redact({schema:"survey-tool.experiment-steward-archive/v1",version:1,archiveId,runId:config.identity.runId||"",experimentId:config.identity.experimentId||"",prepared_at:new Date().toISOString(),inventoryIdentity:collected.inventoryIdentity,completion:collected.completion,health:{checkCount:state.checkCount,healthyStreak:state.healthyStreak,latestEtaSeconds:state.latestEtaSeconds,latestEtaSourceLine:state.latestEtaSourceLine},configSnapshot:cfgSummary,remoteArtifacts:collected.inventory,truncated:collected.truncated,totalBytes:collected.totalBytes,errorLifecycle:collected.errorLifecycle,remediationEvents:collected.remediationEvents,logTail:collected.logTail,metrics:collected.metrics,provenance:{generator:"experiment-steward",mode:"manifest_reference"},outboxCompletion:"pending until lease holder completes with evidence"});manifest.draft_manifest_sha256=manifestHash(manifest);atomicText(manifestPath,JSON.stringify(manifest,null,2)+"\n");atomicText(summaryPath,`# Experiment Steward Archive\n\n- Run: ${config.identity.runId||"unknown"}\n- Experiment: ${config.identity.experimentId||"unknown"}\n- 状态：draft；自动归档，待科研解释。\n- Execution Outbox：等待持有 lease 的 consumer 用 manifest 证据 complete。\n`);state.archiveId=archiveId;saveState();return{content:[{type:"text",text:`归档 draft 已生成：${manifestPath}`}],details:{archiveId,manifestPath,draft:true}}}
    if(action!=="finalize")throw new Error("unknown archive action");if(!fs.existsSync(manifestPath))throw new Error("先 prepare");const manifest=JSON.parse(fs.readFileSync(manifestPath,"utf8"));if(manifest.finalized_at&&manifest.manifest_sha256===manifestHash(manifest))return{content:[{type:"text",text:`归档已幂等完成：${manifestPath}`}],details:{archiveId,manifestPath,idempotent:true}};const draft={...manifest};delete draft.draft_manifest_sha256;if(manifest.draft_manifest_sha256!==manifestHash(draft))throw new Error("draft manifest hash 校验失败");if(collected.inventoryIdentity!==manifest.inventoryIdentity||!collected.completion.complete||COMPLETION_BLOCKED_PHASES.has(state.phase))throw new Error("finalize 复验失败：严格合同、phase 或 inventory 已变化");manifest.finalized_at=new Date().toISOString();manifest.manifest_sha256=manifestHash(manifest);atomicText(manifestPath,JSON.stringify(manifest,null,2)+"\n");transition("archived","manifest finalized");let runWriteback="not_configured",outboxPending=false;if(config.identity.projectRoot&&config.identity.runId){let statuses:string[]=[];try{const box=JSON.parse(fs.readFileSync(path.join(config.identity.projectRoot,".survey-tool","execution-outbox.json"),"utf8"));statuses=(box.items||[]).filter((x:any)=>x.run_id===config!.identity.runId).map((x:any)=>String(x.status))}catch{}const decision=runWritebackDecision(statuses);outboxPending=decision.outboxPending;const args=[surveyctlPath,"--project",config.identity.projectRoot,"run","update",config.identity.runId,...(decision.writeCompleted?["--status","completed"]:[]),"--result-summary","自动归档，待科研解释；Experiment Steward manifest_reference 已完成。","--artifacts",manifestPath,"--audit-paths",manifestPath,"--notes",decision.outboxPending?"归档完成；Execution Outbox completion pending，等待 lease holder 写入完成证据。":"归档完成；未发现 active Execution Outbox dispatch。","--message","Experiment Steward 自动归档写回"],wr=await localExec(process.env.PYTHON||"python3",args);runWriteback=wr.exitCode===0?"completed":`failed: ${wr.stderr.slice(-1000)}`;if(wr.exitCode!==0)transition("needs_attention","archive finalized but surveyctl Run writeback failed")}return{content:[{type:"text",text:`归档 finalized：${manifestPath}。Run 回写：${runWriteback}${outboxPending?"；Outbox pending，未写 operational completed":""}。`}],details:{archiveId,manifestPath,manifest_sha256:manifest.manifest_sha256,runWriteback,outboxPending}}
  }};
  archiveExecutor=async action=>(stewardArchiveTool.execute as any)("auto-archive",{action},undefined,undefined,{});
  pi.registerTool(stewardArchiveTool);

  const stewardConfigTool={
    name: "experiment_steward_config",
    label: "Experiment Steward Config",
    description:
      "Show, create, or switch the Experiment Steward configuration. With no params, shows current config. " +
      "Provide set_* params (host, project_dir, tmux_session, ...) to create/update a task's config " +
      "— written to <cwd>/.pi/experiment-steward.json by default (scope='global' -> ~/.pi/). " +
      "Lets different projects monitor different experiments without restarting pi.",
    promptSnippet: "Show or set Experiment Steward config (per-project tasks)",
    promptGuidelines: [
      "With no parameters, shows the current config.",
      "Provide host + project_dir + tmux_session (optionally log_file, description, error_patterns, progress_patterns, gpu_warning_percent) to create or switch to a new experiment task. This updates the active config immediately — no restart needed.",
      "By default persists to project-local <cwd>/.pi/experiment-steward.json so each project has its own Steward task. Use scope='global' to write to ~/.pi/ instead.",
      "After setting a config, start monitoring with experiment_steward_control action='start'.",
    ],
    parameters: Type.Object({
      host: Type.Optional(Type.String({ description: "Remote SSH host" })),
      project_dir: Type.Optional(Type.String({ description: "Remote project directory" })),
      tmux_session: Type.Optional(Type.String({ description: "tmux session name" })),
      log_file: Type.Optional(Type.String({ description: "Log file path (relative to remote project dir or absolute)" })),
      description: Type.Optional(Type.String({ description: "Human-readable experiment description" })),
      error_patterns: Type.Optional(Type.Array(Type.String(), { description: "Error patterns to scan for" })),
      progress_patterns: Type.Optional(Type.Array(Type.String(), { description: "Progress indicator patterns" })),
      gpu_warning_percent: Type.Optional(Type.Number({ description: "GPU memory warning threshold %" })),
      scope: Type.Optional(Type.String({ description: "Where to persist: 'project' (default, <cwd>/.pi/) or 'global' (~/.pi/)" })),
      clear: Type.Optional(Type.Boolean({ description: "If true, reset to no active config" })),
      config_json: Type.Optional(Type.String({ description: "完整 v2 JSON；remediation/playbook/autoArchive 只能由带 UI 的人类确认保存" })),
    }),
    async execute(_id, params, _signal, _onUpdate, ctx) {
      const cwd = (ctx as any)?.cwd ?? process.cwd();

      if(params.config_json!==undefined){
        const candidate=normalizeConfig(JSON.parse(String(params.config_json)));
        const expandsRemediation=candidate.remediation.enabled||candidate.remediation.playbooks.length>(config?.remediation.playbooks.length||0);
        const enablesAutoArchive=candidate.archive.autoArchive;
        if((expandsRemediation||enablesAutoArchive)&&!(ctx as any)?.hasUI)throw new Error("新增/放宽 remediation 或 autoArchive 必须通过交互 UI 由人类确认");
        if(expandsRemediation||enablesAutoArchive){const ok=await (ctx as any).ui.confirm("确认实验管家权限",`remediation=${candidate.remediation.enabled}，playbooks=${candidate.remediation.playbooks.length}，autoArchive=${candidate.archive.autoArchive}。命令只允许配置原文，代码修改仍必须交给 experiment_code_edit。确认保存？`);if(!ok)throw new Error("用户未确认 Steward 权限")}
        config=candidate;const filePath=configWritePath(cwd,"project");writeConfig(candidate,filePath);return{content:[{type:"text",text:`✅ v2 Steward config 已由人类确认并保存：${filePath}`}],details:{configured:true,savedTo:filePath,config:redact(candidate)}};
      }

      // Clear mode
      if (params.clear) {
        config = null;
        if ((ctx as any)?.hasUI) (ctx as any).ui.setStatus("steward", "no config");
        return {
          content: [{ type: "text", text: "🧹 Experiment Steward config cleared (no active task)." }],
          details: { configured: false },
        };
      }

      const hasSetFields =
        params.host !== undefined || params.project_dir !== undefined ||
        params.tmux_session !== undefined || params.log_file !== undefined ||
        params.description !== undefined || params.error_patterns !== undefined ||
        params.progress_patterns !== undefined || params.gpu_warning_percent !== undefined;

      // Set / update mode
      if (hasSetFields) {
        const merged = mergeConfig(config, {
          host: params.host, project_dir: params.project_dir, tmux_session: params.tmux_session,
          log_file: params.log_file, description: params.description,
          error_patterns: params.error_patterns, progress_patterns: params.progress_patterns,
          gpu_warning_percent: params.gpu_warning_percent,
        });
        if (!merged.remote.host || !merged.remote.projectDir) {
          return {
            content: [{ type: "text", text: "⚠️ Need at least host and project_dir to set a config." }],
            details: { configured: false },
          };
        }
        const wasNew = config === null;
        config = merged;
        const scope = params.scope === "global" ? "global" : "project";
        const filePath = configWritePath(cwd, scope);
        writeConfig(merged, filePath);
        if ((ctx as any)?.hasUI) {
          (ctx as any).ui.setStatus("steward",
            state.active
              ? `🔍 auto/${state.intervalMinutes}m on ${merged.remote.host}:${merged.experiment.tmuxSession}`
              : `${merged.remote.host}:${merged.experiment.tmuxSession}`);
        }
        return {
          content: [{
            type: "text",
            text: `✅ Experiment Steward config ${wasNew ? "created" : "updated"} and saved to ${filePath}.\n\n` +
              renderConfig(merged, state),
          }],
          details: { configured: true, savedTo: filePath, scope },
        };
      }

      // Read mode (no set fields)
      if (config) {
        return {
          content: [{ type: "text", text: renderConfig(config, state) }],
          details: { configured: true, monitoring: state.active },
        };
      }
      const example = {
        remote: { host: "your-ssh-host", projectDir: "/path/to/remote/project" },
        experiment: { tmuxSession: "sar", logFile: "results/experiment.log", description: "My Experiment" },
        monitoring: {
          errorPatterns: ["FileNotFoundError", "CUDA out of memory", "RuntimeError", "KeyboardInterrupt"],
          progressPatterns: ["iteration:", "epoch:", "loss:", "ETA:"],
          gpuWarningPercent: 95,
        },
      };
      return {
        content: [{
          type: "text",
          text: `## No Config Found\nCall this tool with host + project_dir + tmux_session to create a task in-place,\nor create \`.pi/experiment-steward.json\` manually:\n\`\`\`json\n${JSON.stringify(example, null, 2)}\n\`\`\`\n` +
            `Tip: setting config persists to <cwd>/.pi/experiment-steward.json (project-local) by default.`,
        }],
        details: { configured: false },
      };
    },
  };
  pi.registerTool(stewardConfigTool);
  pi.registerTool({...stewardConfigTool,name:"experiment_watchdog_config",label:"DEPRECATED: Steward Config",description:"DEPRECATED alias; migrate to experiment_steward_config. Writes v2 steward config.",async execute(...args:any[]){const r=await (stewardConfigTool.execute as any)(...args);r.content=[{type:"text",text:"⚠️ experiment_watchdog_config 已弃用，请迁移到 experiment_steward_config。\n\n"+r.content.map((x:any)=>x.text||"").join("\n")}];return r}} as any);

  pi.registerTool({
    name:"survey_run_trials",label:"Survey Run Trials",description:"Plan and execute the exact bounded Trial set attached to one Run. The Python backend validates count, IDs, matrix coverage, managed start, and complete result coverage.",
    parameters:Type.Object({
      action:Type.String({description:"inspect, create, plan, start, reattach, status, repair, complete, or fail"}),
      run_id:Type.String({description:"Exact Run ID"}),
      request:Type.Optional(Type.String({description:"For create: the user's concise parameter-campaign request"})),
      concurrency:Type.Optional(Type.Number()),max_retries:Type.Optional(Type.Number()),
      trials:Type.Optional(Type.Array(Type.Object({
        id:Type.String({description:"Consecutive Trial ID such as T-001"}),
        parameters:Type.Record(Type.String(),Type.Union([Type.String(),Type.Number(),Type.Boolean()])),
        rationale:Type.Optional(Type.String()),
      }))),
      runtime_command:Type.Optional(Type.String({description:"Concrete batch launcher command that executes the planned Trials and writes the Trial metrics contract"})),
      failure_class:Type.Optional(Type.String()),reason:Type.Optional(Type.String()),retryable:Type.Optional(Type.Boolean()),
    }),
    async execute(_id,params,_signal,_onUpdate,ctx){
      const toolCwd=String((ctx as any)?.cwd||runtimeCwd);
      if(!fs.existsSync(surveyctlPath))throw new Error("Survey Tool installation is incomplete: surveyctl.py is unavailable");
      runtimeCwd=trustedSurveyProject(toolCwd,config);
      const action=String(params.action||"").toLowerCase(),runId=String(params.run_id||"");
      if(!/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(runId))throw new Error("exact Trial Run ID is required");
      config=loadRunConfig(runtimeCwd,runId)??config;
      if(config?.identity.projectRoot&&path.resolve(config.identity.projectRoot)!==runtimeCwd)throw new Error("configured project identity does not match trusted project cwd");
      let result:any;
      if(action==="inspect"){
        result=await surveyctlJson(["managed-run","trial-plan",runId]);
      }else if(action==="create"){
        if(managedLease)throw new Error("cannot create a Trial Campaign while this Pi holds a managed lease");
        const request=String(params.request||"").trim();if(!request)throw new Error("create requires the user's concrete parameter-campaign request");
        if(!Array.isArray(params.trials)||!params.trials.length)throw new Error("create requires the complete structured Trial list");
        const manifest={contract:"survey-tool.run-trial-manifest/v1",trials:params.trials},consumer=`pi-steward:${process.pid}`;
        result=await surveyctlJson(["managed-run","trial-campaign",runId,"--request",request,"--trial-manifest-json",JSON.stringify(manifest),"--concurrency",String(params.concurrency||1),"--max-retries",String(params.max_retries??1),"--consumer",consumer]);
        trialDraft={runId,manifest:result.trial_manifest};
      }else if(action==="plan"){
        if(managedLease)throw new Error("cannot replace a Trial plan while this Pi holds a managed lease");
        if(!Array.isArray(params.trials)||!params.trials.length)throw new Error("plan requires the complete structured Trial list");
        const manifest={contract:"survey-tool.run-trial-manifest/v1",trials:params.trials};
        result=await surveyctlJson(["managed-run","trial-plan",runId,"--trial-manifest-json",JSON.stringify(manifest)]);
        if(!result.ready_to_prepare||Number(result.planned_trials)!==Number(result.expected_trials))throw new Error("backend did not accept the exact Trial set");
        trialDraft={runId,manifest:result.manifest};
      }else if(action==="start"){
        if(managedLease)throw new Error("this Pi process already holds a managed lease");
        if(!trialDraft||trialDraft.runId!==runId){
          const saved=await surveyctlJson(["managed-run","trial-plan",runId]);
          if(!saved?.ready_to_prepare||!saved?.manifest)throw new Error("this Run has no saved exact Trial manifest; plan it before start");
          trialDraft={runId,manifest:saved.manifest};
        }
        const runtimeCommand=String(params.runtime_command||"").trim();if(!runtimeCommand)throw new Error("start requires one concrete batch runtime_command");
        const consumer=`pi-steward:${process.pid}`;
        const prepared=await surveyctlJson(["managed-run","prepare",runId,"--consumer",consumer,"--runtime-command",runtimeCommand,"--trial-manifest-json",JSON.stringify(trialDraft.manifest)]);
        const claim=await surveyctlJson(["outbox","claim-next","--consumer",consumer,"--run-id",runId]);
        const token=String(claim.lease_token||""),dispatch=claim.task?.dispatch||claim.dispatch||claim;
        if(!token||!dispatch.dispatch_id||String(dispatch.run_id||"")!==runId)throw new Error("no claimable dispatch for this exact Trial Run");
        const requestedAgent=String(dispatch.requested_agent||""),requestedModel=String(dispatch.requested_model||"");
        if(!requestedAgent)throw new Error("dispatch has no requested route");
        await surveyctlJson(["outbox","ack",String(dispatch.dispatch_id),"--lease-token",token,"--consumer",consumer,"--actual-agent",requestedAgent,"--actual-model",requestedModel]);
        managedLease={dispatchId:String(dispatch.dispatch_id),token,consumer,runId};
        const started=await surveyctlJson(["managed-run","start",managedLease.dispatchId,"--lease-token",token,"--consumer",consumer]);
        config=loadRunConfig(runtimeCwd,runId);
        if(!config?.identity.managedExecution||path.resolve(config.identity.projectRoot||"")!==path.resolve(runtimeCwd)){state.phase="needs_attention";throw new Error("Trial start succeeded but trusted managed Steward config could not be loaded")}
        let monitoringStarted=false;
        try{startMonitoring(config.scheduling.minIntervalMinutes,true);monitoringStarted=true}catch(error:any){transition("needs_attention",`managed Trial monitoring failed to start: ${String(error.message||error).slice(0,500)}`);pi.sendUserMessage(`Trial 已启动，但自动观察未能启动：${String(error.message||error).slice(0,1000)}。请立即调用 survey_run_trials status。`,{deliverAs:"followUp"})}
        result={ok:true,planned_trials:trialDraft.manifest.trials.length,prepared,started,monitoring_started:monitoringStarted,first_check_seconds:monitoringStarted?1:null};
      }else if(action==="reattach"){
        if(managedLease){
          if(managedLease.runId!==runId)throw new Error("this Pi process already holds a managed lease for another Run");
          try{result=await surveyctlJson(["managed-run","status",managedLease.dispatchId,"--lease-token",managedLease.token,"--consumer",managedLease.consumer,"--heartbeat"])}
          catch(error){if(!isStaleManagedLeaseError(error))throw error;managedLease=null;stopMonitoring("Discarded stale in-memory managed lease before reattach")}
        }
        if(result){const safe=redactManagedResult(result);return {content:[{type:"text",text:JSON.stringify(safe,null,2)}],details:safe}}
        const box=await surveyctlJson(["outbox","list"]),items=Array.isArray(box?.items)?box.items:[];
        const candidates=items.filter((row:any)=>String(row.run_id||"")===runId&&String(row.status||"")==="running").sort((a:any,b:any)=>String(b.updated_at||"").localeCompare(String(a.updated_at||"")));
        if(!candidates.length)throw new Error("this Run has no running dispatch to reattach; inspect returns the Trial contract without a lease");
        const dispatchId=String(candidates[0].dispatch_id||""),consumer=`pi-steward:${process.pid}`;
        const attached=await surveyctlJson(["managed-run","reattach",dispatchId,"--consumer",consumer]),token=String(attached.lease_token||""),dispatch=attached.dispatch||{};
        if(!token||dispatch.dispatch_id!==dispatchId||String(dispatch.run_id||"")!==runId)throw new Error("reattach did not return the exact Trial Run lease");
        managedLease={dispatchId,token,consumer,runId};config=loadRunConfig(runtimeCwd,runId);
        result=await surveyctlJson(["managed-run","status",dispatchId,"--lease-token",token,"--consumer",consumer,"--heartbeat"]);
        if(config?.identity.managedExecution)startMonitoring(config.scheduling.minIntervalMinutes,true);
      }else if(action==="repair"){
        if(!managedLease||managedLease.runId!==runId)throw new Error("this Pi process does not hold the requested Trial Run lease");
        const reason=String(params.reason||"").trim();if(!reason)throw new Error("repair requires the concrete observed error and intended changed evidence");
        const repair=await surveyctlJson(["managed-run","repair",managedLease.dispatchId,"--lease-token",managedLease.token,"--consumer",managedLease.consumer,"--failure-class",String(params.failure_class||"implementation"),"--reason",reason]);
        managedLease=null;stopMonitoring("Pi entered bounded Trial repair mode");
        result={...repair,ok:true,repair_mode:true,bash_guard_active:false,dispatch_resolved_internally:true,next:"repair and focused-test the bound repository, then call survey_run_trials start by run_id with the retained exact plan; do not ask the user for approval or a dispatch ID"};
      }else if(action==="status"&&!managedLease){
        const box=await surveyctlJson(["outbox","list"]),items=Array.isArray(box?.items)?box.items:[];
        const candidates=items.filter((row:any)=>String(row.run_id||"")===runId&&String(row.status||"")==="running").sort((a:any,b:any)=>String(b.updated_at||"").localeCompare(String(a.updated_at||"")));
        if(candidates.length!==1)throw new Error("status requires exactly one running Trial dispatch when the in-memory lease is absent");
        const dispatchId=String(candidates[0].dispatch_id||""),consumer=`pi-steward:${process.pid}`,attached=await surveyctlJson(["managed-run","reattach",dispatchId,"--consumer",consumer]),token=String(attached.lease_token||""),dispatch=attached.dispatch||{};
        if(!token||dispatch.dispatch_id!==dispatchId||String(dispatch.run_id||"")!==runId)throw new Error("automatic status reattach did not return the exact Trial Run lease");
        managedLease={dispatchId,token,consumer,runId};config=loadRunConfig(runtimeCwd,runId)??config;result=await surveyctlJson(["managed-run","status",dispatchId,"--lease-token",token,"--consumer",consumer,"--heartbeat"]);
        if(config?.identity.managedExecution)startMonitoring(config.scheduling.minIntervalMinutes,true);
      }else{
        if(!managedLease||managedLease.runId!==runId)throw new Error("this Pi process does not hold the requested Trial Run lease");
        const base=["managed-run",action,managedLease.dispatchId,"--lease-token",managedLease.token,"--consumer",managedLease.consumer];
        if(action==="status")base.push("--heartbeat");
        else if(action==="fail")base.push("--failure-class",String(params.failure_class||"environment"),"--reason",String(params.reason||"Trial execution failed"),...(params.retryable?["--retryable"]:[]));
        else if(action!=="complete")throw new Error("unknown survey_run_trials action");
        try{result=await surveyctlJson(base)}catch(error){
          if(action!=="status"||!isStaleManagedLeaseError(error))throw error;
          const dispatchId=managedLease.dispatchId,consumer=`pi-steward:${process.pid}`;managedLease=null;stopMonitoring("Discarded stale in-memory Trial lease before automatic reattach");
          const attached=await surveyctlJson(["managed-run","reattach",dispatchId,"--consumer",consumer]),token=String(attached.lease_token||""),dispatch=attached.dispatch||{};
          if(!token||dispatch.dispatch_id!==dispatchId||String(dispatch.run_id||"")!==runId)throw new Error("automatic reattach did not return the exact Trial Run lease");
          managedLease={dispatchId,token,consumer,runId};result=await surveyctlJson(["managed-run","status",dispatchId,"--lease-token",token,"--consumer",consumer,"--heartbeat"]);
          config=loadRunConfig(runtimeCwd,runId)??config;if(config?.identity.managedExecution)startMonitoring(config.scheduling.minIntervalMinutes,true);
        }
        if(action==="complete"||action==="fail"){managedLease=null;trialDraft=null}
      }
      const safe=redactManagedResult(result);
      return {content:[{type:"text",text:JSON.stringify(safe,null,2)}],details:safe};
    },
  } as any);

  pi.registerTool({
    name:"survey_run_execution",label:"Survey Run Execution",description:"Continue one approved managed Run by run_id. The tool resolves the current dispatch internally; lease credentials and dispatch IDs are not user inputs.",
    parameters:Type.Object({action:Type.String({description:"continue (preferred: atomically prepare/claim/ack/start by run_id), prepare, claim, reattach, start, status, repair, complete, fail, or retry"}),dispatch_id:Type.Optional(Type.String({description:"Internal recovery identity only; never ask the user for it"})),experiment_id:Type.Optional(Type.String()),run_id:Type.Optional(Type.String()),runtime_command:Type.Optional(Type.String()),trial_manifest_json:Type.Optional(Type.String({description:"For a Trial Run, exact survey-tool.run-trial-manifest/v1 JSON with all planned Trial parameters"})),failure_class:Type.Optional(Type.String()),reason:Type.Optional(Type.String()),retryable:Type.Optional(Type.Boolean())}),
    async execute(_id,params,_signal,_onUpdate,ctx){
      // Tool calls can arrive before/without the extension's session_start
      // callback in a newly-owned Herdr Pi. Bind to the *calling session* cwd
      // here rather than retaining the extension host's original cwd.
      const toolCwd=String((ctx as any)?.cwd||runtimeCwd);
      if(!fs.existsSync(surveyctlPath))throw new Error("Survey Tool installation is incomplete: surveyctl.py is unavailable");
      runtimeCwd=trustedSurveyProject(toolCwd,config);
      const requestedRun=String(params.run_id||managedLease?.runId||"");
      if(requestedRun)config=loadRunConfig(runtimeCwd,requestedRun)??config;
      if(config?.identity.projectRoot&&path.resolve(config.identity.projectRoot)!==runtimeCwd)throw new Error("configured project identity does not match trusted project cwd");
      const action=String(params.action||"").toLowerCase();let result:any;
      if(action==="continue"){
        if(managedLease)throw new Error("this Pi process already controls a managed attempt; use status/start instead of continue");
        const runId=String(params.run_id||"");const runtimeCommand=String(params.runtime_command||"").trim();
        if(!/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(runId))throw new Error("continue requires the exact run_id; never ask the user for a dispatch ID");
        if(!runtimeCommand)throw new Error("continue requires the concrete runtime_command already present in the approved Run context");
        const consumer=`pi-steward:${process.pid}`;
        const prepared=await surveyctlJson(["managed-run","prepare",runId,"--consumer",consumer,"--runtime-command",runtimeCommand,...(params.trial_manifest_json?["--trial-manifest-json",String(params.trial_manifest_json)]:[])]);
        const claim=await surveyctlJson(["outbox","claim-next","--consumer",consumer,"--run-id",runId]);
        const token=String(claim.lease_token||"");const dispatch=claim.task?.dispatch||claim.dispatch||claim;
        if(!token||!dispatch.dispatch_id||String(dispatch.run_id||"")!==runId)throw new Error("the current approved Run has no claimable dispatch; refresh the Run state, never retry a historical dispatch ID");
        const requestedAgent=String(dispatch.requested_agent||"");const requestedModel=String(dispatch.requested_model||"");
        if(!requestedAgent)throw new Error("current Run dispatch has no requested route");
        await surveyctlJson(["outbox","ack",String(dispatch.dispatch_id),"--lease-token",token,"--consumer",consumer,"--actual-agent",requestedAgent,"--actual-model",requestedModel]);
        managedLease={dispatchId:String(dispatch.dispatch_id),token,consumer,runId};
        const started=await surveyctlJson(["managed-run","start",managedLease.dispatchId,"--lease-token",managedLease.token,"--consumer",managedLease.consumer]);
        config=loadRunConfig(runtimeCwd,runId);
        if(!config?.identity.managedExecution||path.resolve(config.identity.projectRoot||"")!==path.resolve(runtimeCwd)){state.phase="needs_attention";throw new Error("managed continue started but trusted Run config could not be loaded")}
        try{startMonitoring(config.scheduling.minIntervalMinutes,true)}catch(error:any){transition("needs_attention",`managed monitoring failed to start: ${String(error.message||error).slice(0,500)}`)}
        result={ok:true,state:"running",run_id:runId,prepared:redactManagedResult(prepared),started:redactManagedResult(started),dispatch_resolved_internally:true,next:"call status by run_id; do not retain or ask the user for a dispatch ID"};
      }else if(action==="prepare"){
        if(managedLease)throw new Error("runtime command must be prepared before claiming the managed lease");
        const runId=String(params.run_id||"");const runtimeCommand=String(params.runtime_command||"");
        if(!/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(runId))throw new Error("prepare requires the exact Steward run_id");
        if(!runtimeCommand.trim())throw new Error("prepare requires the concrete runtime_command resolved from the approved Workspace");
        const consumer=`pi-steward:${process.pid}`;
        result=await surveyctlJson(["managed-run","prepare",runId,"--consumer",consumer,"--runtime-command",runtimeCommand,...(params.trial_manifest_json?["--trial-manifest-json",String(params.trial_manifest_json)]:[])]);
      }else if(action==="claim"){
        if(managedLease)throw new Error("this Pi process already holds a managed lease");
        const consumer=`pi-steward:${process.pid}`;
        // claim-next atomically expires claimed/acknowledged stale leases before
        // selecting a dispatch. Reclaiming that unchanged approved dispatch is
        // operational recovery, not a new Run approval or authorization.
        const runId=String(params.run_id||"");if(!/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(runId))throw new Error("claim requires the exact Steward run_id");
        const claim=await surveyctlJson(["outbox","claim-next","--consumer",consumer,...(params.experiment_id?["--experiment-id",String(params.experiment_id)]:[]),"--run-id",runId]);
        const token=String(claim.lease_token||"");const dispatch=claim.task?.dispatch||claim.dispatch||claim;
        if(!token||!dispatch.dispatch_id||String(dispatch.run_id||"")!==runId)throw new Error("no claimable approved dispatch for this exact Run; inspect the current Outbox state");
        const requestedAgent=String(dispatch.requested_agent||"");const requestedModel=String(dispatch.requested_model||"");
        if(!requestedAgent)throw new Error("dispatch has no requested route");
        await surveyctlJson(["outbox","ack",String(dispatch.dispatch_id),"--lease-token",token,"--consumer",consumer,"--actual-agent",requestedAgent,"--actual-model",requestedModel]);
        managedLease={dispatchId:String(dispatch.dispatch_id),token,consumer,runId:String(dispatch.run_id||"")};
        result={ok:true,state:"acknowledged",dispatch_id:managedLease.dispatchId,run_id:managedLease.runId};
      }else if(action==="retry"){
        if(managedLease)throw new Error("release or fail the current managed lease before retrying");
        const dispatchId=String(params.dispatch_id||"");const reason=String(params.reason||"");
        if(!/^dispatch-[a-f0-9]{24}$/.test(dispatchId)||!reason.trim())throw new Error("retry requires dispatch_id and concrete changed evidence/reason");
        // Retry atomically requeues the same retryable dispatch and restores
        // only the Run's operational ready_to_run projection. If the human has
        // reopened the spec, Python returns state=revision_open without
        // mutation; that is permission to continue the requested revision,
        // never a reason to retry the stale dispatch or report a blocker.
        result=await surveyctlJson(["outbox","retry",dispatchId,"--reason",reason,"--evidence",reason]);
      }else if(action==="reattach"){
        const dispatchId=String(params.dispatch_id||"");if(!/^dispatch-[a-f0-9]{24}$/.test(dispatchId))throw new Error("strict dispatch_id is required");
        if(managedLease){
          if(managedLease.dispatchId!==dispatchId)throw new Error("this Pi process already holds a managed lease for another dispatch");
          try{result=await surveyctlJson(["managed-run","status",dispatchId,"--lease-token",managedLease.token,"--consumer",managedLease.consumer,"--heartbeat"])}
          catch(error){if(!isStaleManagedLeaseError(error))throw error;managedLease=null;stopMonitoring("Discarded stale in-memory managed lease before reattach")}
        }
        if(result){const safe=redactManagedResult(result);return {content:[{type:"text",text:JSON.stringify(safe,null,2)}],details:safe}}
        const consumer=`pi-steward:${process.pid}`;const attached=await surveyctlJson(["managed-run","reattach",dispatchId,"--consumer",consumer]);const token=String(attached.lease_token||"");const dispatch=attached.dispatch||{};
        if(!token||dispatch.dispatch_id!==dispatchId)throw new Error("reattach did not return the requested lease");
        managedLease={dispatchId,token,consumer,runId:String(dispatch.run_id||"")};
        config=loadRunConfig(runtimeCwd,managedLease.runId)??config;
        try{result=await surveyctlJson(["managed-run","status",dispatchId,"--lease-token",token,"--consumer",consumer,"--heartbeat"])}catch(error){state.phase="needs_attention";throw error}
      }else if(action==="repair"){
        if(!managedLease)throw new Error("no in-memory managed lease to repair");
        const reason=String(params.reason||"").trim();if(!reason)throw new Error("repair requires the concrete observed error and intended changed evidence");
        const repair=await surveyctlJson(["managed-run","repair",managedLease.dispatchId,"--lease-token",managedLease.token,"--consumer",managedLease.consumer,"--failure-class",String(params.failure_class||"implementation"),"--reason",reason]);
        managedLease=null;stopMonitoring("Pi entered bounded Run repair mode");
        result={...repair,ok:true,repair_mode:true,bash_guard_active:false,dispatch_resolved_internally:true,next:"repair and focused-test the bound repository, then call survey_run_execution continue by run_id; reuse the approved command and never ask the user for approval or a dispatch ID"};
      }else if(action==="status"&&!managedLease){
        let dispatchId=String(params.dispatch_id||"");
        if(!dispatchId){
          const runId=String(params.run_id||"");if(!/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(runId))throw new Error("status requires run_id or dispatch_id when the in-memory lease is absent");
          const box=await surveyctlJson(["outbox","list"]),items=Array.isArray(box?.items)?box.items:[];
          const candidates=items.filter((row:any)=>String(row.run_id||"")===runId&&String(row.status||"")==="running").sort((a:any,b:any)=>String(b.updated_at||"").localeCompare(String(a.updated_at||"")));
          if(candidates.length!==1)throw new Error("status requires exactly one running dispatch when the in-memory lease is absent");dispatchId=String(candidates[0].dispatch_id||"");
        }
        if(!/^dispatch-[a-f0-9]{24}$/.test(dispatchId))throw new Error("strict dispatch_id is required");
        const consumer=`pi-steward:${process.pid}`,attached=await surveyctlJson(["managed-run","reattach",dispatchId,"--consumer",consumer]),token=String(attached.lease_token||""),dispatch=attached.dispatch||{};
        if(!token||dispatch.dispatch_id!==dispatchId)throw new Error("automatic status reattach did not return the requested lease");
        managedLease={dispatchId,token,consumer,runId:String(dispatch.run_id||"")};config=loadRunConfig(runtimeCwd,managedLease.runId)??config;result=await surveyctlJson(["managed-run","status",dispatchId,"--lease-token",token,"--consumer",consumer,"--heartbeat"]);
        if(config?.identity.managedExecution)startMonitoring(config.scheduling.minIntervalMinutes,true);
      }else{
        if(!managedLease)throw new Error("no in-memory managed lease; claim is required in this Pi process");
        const base=["managed-run",action,managedLease.dispatchId,"--lease-token",managedLease.token,"--consumer",managedLease.consumer];
        if(action==="status")base.push("--heartbeat");
        else if(action==="fail")base.push("--failure-class",String(params.failure_class||"environment"),"--reason",String(params.reason||"managed execution failed"),...(params.retryable?["--retryable"]:[]));
        else if(!["start","complete"].includes(action))throw new Error("unknown managed execution action");
        try{result=await surveyctlJson(base)}catch(error){
          if(action!=="status"||!isStaleManagedLeaseError(error))throw error;
          const stale=managedLease,dispatchId=stale.dispatchId,consumer=`pi-steward:${process.pid}`;managedLease=null;stopMonitoring("Discarded stale in-memory managed lease before automatic reattach");
          const attached=await surveyctlJson(["managed-run","reattach",dispatchId,"--consumer",consumer]),token=String(attached.lease_token||""),dispatch=attached.dispatch||{};
          if(!token||dispatch.dispatch_id!==dispatchId)throw new Error("automatic reattach did not return the requested lease");
          managedLease={dispatchId,token,consumer,runId:String(dispatch.run_id||stale.runId)};config=loadRunConfig(runtimeCwd,managedLease.runId)??config;
          result=await surveyctlJson(["managed-run","status",dispatchId,"--lease-token",token,"--consumer",consumer,"--heartbeat"]);
          if(config?.identity.managedExecution)startMonitoring(config.scheduling.minIntervalMinutes,true);
        }
        if(action==="start"){
          config=loadRunConfig(runtimeCwd,managedLease.runId);
          if(!config?.identity.managedExecution||path.resolve(config.identity.projectRoot||"")!==path.resolve(runtimeCwd)){state.phase="needs_attention";throw new Error("managed start succeeded but trusted managed Steward config could not be loaded")}
          try{startMonitoring(config.scheduling.minIntervalMinutes,true)}catch(error:any){transition("needs_attention",`managed monitoring failed to start: ${String(error.message||error).slice(0,500)}`);pi.sendUserMessage(`Run 已启动，但自动观察未能启动：${String(error.message||error).slice(0,1000)}。请立即调用 survey_run_execution status。`,{deliverAs:"followUp"})}
        }
        if(action==="complete"||action==="fail")managedLease=null;
      }
      const safe=redactManagedResult(result);
      return {content:[{type:"text",text:JSON.stringify(safe,null,2)}],details:safe};
    },
  } as any);

  pi.on("tool_call",(event:any)=>{
    if(!managedLease)return;
    const name=String(event.toolName||event.name||"");const input=event.input||event.params||{};
    if(name==="bash")return {block:true,reason:"Managed Run lease 期间禁止全部内置 bash；普通 Run 使用 survey_run_execution，参数实验使用 survey_run_trials。"};
    if(["write","edit"].includes(name)){
      const target=String(input.path||input.file_path||"");
      if(!config?.identity.projectRoot||!managedPathAllowed(config.identity.projectRoot,target))return {block:true,reason:"Managed Run 写入越过项目边界或受保护治理路径。"};
    }
    if(name==="read"){
      const target=String(input.path||input.file_path||"");
      if(/(?:^|\/)(?:\.ssh|\.aws|\.gnupg)(?:\/|$)/.test(target))return {block:true,reason:"Managed Run 不读取凭据目录。"};
    }
  });

  // ── Lifecycle ──

  pi.on("session_start", async (_event, ctx) => {
    runtimeCwd = ctx.cwd;
    config = loadConfig(ctx.cwd);
    queue = loadQueue();
    loadPreviousState(ctx.sessionManager.getEntries());

    if (ctx.hasUI) {
      const label = queue.tasks.length
        ? `queue ${queue.tasks.filter(t => t.status === "completed").length}/${queue.tasks.length} paused`
        : config
          ? `${config.remote.host}:${config.experiment.tmuxSession}`
          : "no config";
      ctx.ui.setStatus("steward", label);
    }
  });

  // Clean up on shutdown
  pi.on("session_shutdown", () => {
    if (checkTimer) clearTimeout(checkTimer);
    managedLease=null;
  });
}
