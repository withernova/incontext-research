#!/usr/bin/env node
const assert=require('node:assert/strict');

(async()=>{
  const core=await import('../extensions/experiment-steward/core.ts');
  const flat=core.normalizeConfig({host:'gpu',project_dir:'/repo',tmux_session:'run',log_file:'/logs/a.log',description:'legacy'});
  assert.equal(flat.version,2);assert.equal(flat.remote.host,'gpu');assert.equal(flat.experiment.tmuxSession,'run');assert.equal(flat.completion.enabled,false);assert.equal(flat.archive.enabled,false);assert.equal(flat.remediation.enabled,false);
  const nested=core.normalizeConfig({remote:{host:'h',projectDir:'/p'},experiment:{tmuxSession:'t',logFile:'x'},monitoring:{errorPatterns:['E'],progressPatterns:['ETA:'],gpuWarningPercent:90}});
  assert.equal(nested.remote.projectDir,'/p');assert.deepEqual(nested.monitoring.errorPatterns,['E']);

  assert.equal(core.parseEta('step 2 ETA: 01:02:03'),3723);
  assert.equal(core.parseEta('ETA: 02:01:02:03'),2*86400+3723);
  assert.equal(core.parseEta('ETA: 90m'),5400);assert.equal(core.parseEta('ETA: 1.5h'),5400);assert.equal(core.parseEta('no estimate'),null);

  const cfg=core.defaultConfig();cfg.scheduling={minIntervalMinutes:2,normalIntervalMinutes:15,maxIntervalMinutes:60,etaFraction:.1,nearCompletionMinutes:30,stableBackoffAfterChecks:3};
  assert.equal(core.decideInterval(cfg,{phase:'incident_open',healthyStreak:0}).minutes,2);
  assert.equal(core.decideInterval(cfg,{phase:'monitoring',etaSeconds:1200,healthyStreak:0}).minutes,2);
  assert.equal(core.decideInterval(cfg,{phase:'monitoring',etaSeconds:72000,healthyStreak:0}).minutes,60);
  assert.equal(core.decideInterval(cfg,{phase:'monitoring',healthyStreak:5}).minutes,60);

  cfg.experiment.processPattern='python.*train';cfg.completion={enabled:true,completionMarkers:['DONE','SAVED'],requiredArtifacts:['/a'],metricsFile:'/m',exitCodeFile:'/exit-code',stableChecks:2,requireProcessExit:true,allowNonzeroExit:false};
  const artifacts=[{path:'/a',exists:true,size:2,mtime:'1'},{path:'/m',exists:true,size:3,mtime:'1'},{path:'/exit-code',exists:true,size:2,mtime:'1'}];
  const completeObs={markersFound:['DONE','SAVED'],artifacts,previousArtifacts:artifacts,processRunning:false,processVerified:true,exitCode:0,exitCodeVerified:true,openIncidents:0};
  let result=core.evaluateCompletion(cfg,{...completeObs,markersFound:['DONE']},0);assert.equal(result.contractOk,false);assert.equal(result.complete,false);
  result=core.evaluateCompletion(cfg,{...completeObs,exitCode:null,exitCodeVerified:false},0);assert.equal(result.contractOk,false);
  result=core.evaluateCompletion(cfg,{...completeObs,exitCode:1},0);assert.equal(result.contractOk,false);
  result=core.evaluateCompletion(cfg,completeObs,0);assert.equal(result.contractOk,true);assert.equal(result.stableCount,1);assert.equal(result.complete,false);
  result=core.evaluateCompletion(cfg,completeObs,1);assert.equal(result.complete,true);
  result=core.evaluateCompletion(cfg,{...completeObs,openIncidents:1},1);assert.equal(result.complete,false); // includes remediation_applied in caller
  result=core.evaluateCompletion(cfg,{...completeObs,blockedPhase:true},1);assert.equal(result.complete,false);
  cfg.completion.allowNonzeroExit=true;result=core.evaluateCompletion(cfg,{...completeObs,exitCode:9,exitCodeVerified:false},1);assert.equal(result.complete,true);cfg.completion.allowNonzeroExit=false;

  const clean=core.redact({lease_token:'x',nested:{approved_spec_hash:'h',password:'p',safe:'yes'},prompt:'secret'});assert.deepEqual(clean,{nested:{approved_spec_hash:'h',safe:'yes'}});
  assert.equal(core.managedPathAllowed('/project','/project/results/a.json'),true);
  for(const blocked of ['/project/.git/config','/project/.pi/steward.json','/project/.survey-tool/execution-outbox.json','/project/kernel/claims.md','/other/file'])assert.equal(core.managedPathAllowed('/project',blocked),false,blocked);
  assert.equal(core.managedPathAllowed('/project','/project/ok/../../other'),false);
  assert.equal(core.managedBashAllowed('python3 /tool/surveyctl.py --project /project managed-run status D-1 --heartbeat','/tool/surveyctl.py','/project'),true);
  assert.equal(core.managedBashAllowed('python3 /tool/surveyctl.py --project /project managed-run status D-1; id','/tool/surveyctl.py','/project'),false);
  assert.equal(core.surveyctlPathFromExtension('/home/u/.pi/agent/extensions/experiment-steward/index.ts','/opt/survey-tool/extensions/experiment-steward/index.ts'),'/opt/survey-tool/surveyctl.py');
  assert.throws(()=>core.surveyctlPathFromExtension('relative/index.ts'),/absolute/);
  assert.deepEqual(core.redactManagedResult({lease_token:'raw',dispatch_id:'D-1'}),{dispatch_id:'D-1'});
  for(const message of ['lease token invalid','lease token/consumer 无效','lease consumer mismatch','lease 已过期','lease expired'])assert.equal(core.isStaleManagedLeaseError(new Error(message)),true,message);
  assert.equal(core.isStaleManagedLeaseError(new Error('managed status observation failed')),false);
  const id1=core.stableArchiveId({projectRoot:'/p',experimentId:'E',runId:'R'},'files:1');const id2=core.stableArchiveId({projectRoot:'/p',experimentId:'E',runId:'R'},'files:1');assert.equal(id1,id2);assert.notEqual(id1,core.stableArchiveId({projectRoot:'/p',experimentId:'E',runId:'R'},'files:2'));
  const manifest={z:1,a:{y:2,x:3},finalized_at:'now'};manifest.manifest_sha256=core.manifestHash(manifest);const diskRoundTrip=JSON.parse(JSON.stringify(manifest)),storedHash=diskRoundTrip.manifest_sha256;delete diskRoundTrip.manifest_sha256;assert.equal(storedHash,core.manifestHash(diskRoundTrip));assert.equal(core.canonicalStringify({b:1,a:2}),'{"a":2,"b":1}');
  const window=core.inventoryWindow([{path:'/b',size:2},{path:'/a',size:2},{path:'/c',size:2}],2,10);assert.deepEqual(window.items.map(x=>x.path),['/a','/b']);assert.equal(window.truncated,true);assert.equal(core.inventoryWindow([{path:'/a',size:6},{path:'/b',size:6}],5,10).truncated,true);
  assert.equal(core.restartAllowed(false,99,0),true);assert.equal(core.restartAllowed(true,1,1),false);assert.equal(core.restartAllowed(true,0,1),true);
  assert.equal(core.blockingIncidentCount([{status:'resolved'},{status:'remediation_applied'},{status:'open'}]),2);
  assert.deepEqual(core.runWritebackDecision(['running']),{writeCompleted:false,outboxPending:true});assert.deepEqual(core.runWritebackDecision(['completed']),{writeCompleted:true,outboxPending:false});
  const phase=(overrides={})=>core.decideObservationPhase({currentPhase:'monitoring',tmuxAlive:true,processRunning:true,processVerified:true,newErrorFingerprints:[],completionContractOk:false,completionComplete:false,...overrides});
  assert.equal(phase({newErrorFingerprints:['fp-1']}).phase,'incident_open');assert.equal(phase({tmuxAlive:false}).phase,'incident_open');assert.equal(phase({processVerified:false}).phase,'needs_attention');
  assert.equal(phase({tmuxAlive:true,processRunning:false,processVerified:true}).phase,'incident_open');assert.equal(phase({completionContractOk:true}).phase,'completion_candidate');assert.equal(phase({completionContractOk:true,completionComplete:true}).archiveEligible,true);
  assert.equal(phase({currentPhase:'verifying_recovery'}).phase,'verifying_recovery');const incident=phase({processRunning:false});assert.equal(core.shouldNotifyIncident(undefined,incident),true);assert.equal(core.shouldNotifyIncident(incident.incidentSignature,incident),false);
  assert.throws(()=>core.normalizeConfig({scheduling:{minIntervalMinutes:'2'}}),/有限数字/);assert.throws(()=>core.normalizeConfig({scheduling:{minIntervalMinutes:NaN}}),/有限数字/);assert.throws(()=>core.normalizeConfig({monitoring:{etaRegex:'['}}),/etaRegex/);assert.equal(core.parseEta('ETA soon','ETA'),null);
  assert.throws(()=>core.normalizeConfig({experiment:{processPattern:'x'},completion:{enabled:true,requireProcessExit:true,allowNonzeroExit:false}}),/exitCodeFile/);

  const source=require('node:fs').readFileSync(require('node:path').join(__dirname,'../extensions/experiment-steward/index.ts'),'utf8');
  for(const marker of ['experiment_steward_control','experiment_steward_config','experiment_steward_archive','experiment_steward_remediation','steward_task_queue','survey_run_execution','survey_run_trials','watchdog_control','experiment_watchdog_config','watchdog_task_queue','x-experiment-steward-state','pausedAfterRestart'])assert.ok(source.includes(marker),marker);
  assert.ok(source.includes('let managedLease'));assert.ok(source.includes('managedLease=null'));assert.ok(!source.includes('writeFileSync(managedLease'));
  assert.ok(source.includes('action==="prepare"'));assert.ok(source.includes('runtime_command'));assert.ok(source.includes('trial_manifest_json'));assert.ok(source.includes('--trial-manifest-json'));assert.ok(source.includes('action==="reattach"'));assert.ok(source.includes('Managed Run lease 期间禁止全部内置 bash'));assert.ok(!source.includes('managedBashAllowed(command'));
  assert.ok(source.includes('action==="continue"'));assert.ok(source.includes('dispatch_resolved_internally:true'));assert.ok(source.includes('never ask the user for a dispatch ID'));
  assert.ok(source.includes('managed-run","trial-plan'));assert.ok(source.includes('action==="plan"'));assert.ok(source.includes('planned_trials'));assert.ok(source.includes('trialDraft=null'));
  assert.ok(source.includes('action==="create"'));assert.ok(source.includes('managed-run","trial-campaign'));assert.ok(source.includes('create requires the user'));
  assert.ok(source.includes('startMonitoring(config.scheduling.minIntervalMinutes,true)'));assert.ok(source.includes('first_check_seconds:monitoringStarted?1:null'));
  assert.ok(source.includes('action==="repair"'));assert.ok(source.includes('managed-run","repair'));assert.ok(source.includes('repair_mode:true'));assert.ok(source.includes('bash_guard_active:false'));assert.ok(source.includes('Pi entered bounded Trial repair mode'));assert.ok(source.includes('do not ask the user for approval or a dispatch ID'));
  assert.ok(source.includes('当前 Pi 仍持有'));assert.ok(source.includes('deliverAs:"followUp"'));
  assert.ok(source.includes('function loadRunConfig'));assert.ok(source.includes('.pi","stewards"'));assert.ok(source.includes('loadRunConfig(runtimeCwd,runId)'));
  assert.ok(source.includes('action==="reattach"'));assert.ok(source.includes('this Run has no running dispatch to reattach'));
  assert.ok(source.includes('Discarded stale in-memory managed lease before automatic reattach'));
  assert.ok(source.includes('automatic status reattach did not return the requested lease'));
  assert.ok(source.includes('`${key}.state.json`'));assert.ok(source.includes('`${key}.events.jsonl`'));
  const agentEnd=source.slice(source.indexOf('pi.on("agent_end"'),source.indexOf('// ── Commands'));
  assert.ok(agentEnd.includes('scheduleQueueCheck'));assert.ok(!agentEnd.includes('scheduleNextCheck'));assert.ok(!agentEnd.includes('event.messages'));
  assert.ok(source.includes('customType: "steward-queue"'));assert.ok(source.includes('setStatus("steward"'));assert.ok(source.includes('steward_task_queue action=complete'));
  console.log('EXPERIMENT-STEWARD-PASS');
})().catch(e=>{console.error(e);process.exit(1)});
