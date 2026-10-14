#!/usr/bin/env node
const assert=require('node:assert/strict'),fs=require('node:fs');
(async()=>{
  const c=await import('../extensions/research-explorer/core.ts');
  const b=c.validateBudget({durationMinutes:30,now:0});
  assert.equal(b.hardMaxRounds,20);assert.equal(b.intervalMinutes,1);
  assert.ok(c.budgetDecision({deadline:new Date(0).toISOString(),hardMaxRounds:20,completedRounds:0},1).stop);
  assert.ok(c.budgetDecision({deadline:'',maxRounds:2,hardMaxRounds:20,completedRounds:2}).stop);
  assert.ok(c.retryAllowed('transient',['new_evidence'],0));assert.ok(!c.retryAllowed('transient',[],0));
  assert.equal(c.remainingLeaseMs(new Date(5000).toISOString(),1000),4000);
  assert.match(c.corruptStatePath('/p/state.json',0),/state\.json\.corrupt-/);
  assert.deepEqual(c.parseCommandArgs('start --project-root "/a path/project" --target-type idea --target-id I-001 --max-rounds 2'),{action:'start',project_root:'/a path/project',target_type:'idea',target_id:'I-001',max_rounds:2});
  assert.throws(()=>c.parseCommandArgs('start --wat x'),/未知参数/);assert.throws(()=>c.parseCommandArgs('start --max-rounds nope'),/整数/);
  const src=fs.readFileSync('extensions/research-explorer/index.ts','utf8');
  for(const x of['research_explorer_control','research_explorer_round','research_explorer_finalize','registerCommand("explore"','deliverAs: "followUp"','research-explorer-state.json','StringEnum','record_failed','restoreRoundTimer','corruptStatePath'])assert.ok(src.includes(x),x);
  console.log('RESEARCH-EXPLORER-PASS');
})().catch(e=>{console.error(e);process.exit(1)});
