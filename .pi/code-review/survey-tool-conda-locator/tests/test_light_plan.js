#!/usr/bin/env node
const assert=require('node:assert/strict'),fs=require('node:fs');
(async()=>{
  const p=await import('../extensions/light-plan/core.ts');
  const plan=p.makePlan([{step:'inspect',status:'completed'},{step:'implement',status:'in_progress'},{step:'test',status:'pending'}],'reason','now');
  assert.equal(plan.updatedAt,'now'); assert.match(p.renderPlan(plan),/◉ 2\. implement/); assert.equal(p.isComplete(plan),false);
  assert.throws(()=>p.makePlan([{step:'a',status:'in_progress'},{step:'b',status:'in_progress'}]),/最多一个/);
  assert.throws(()=>p.makePlan([{step:'a',status:'pending'},{step:'b',status:'completed'}]),/不能跳过/);
  assert.ok(p.isComplete(p.makePlan([{step:'done',status:'completed'}])));
  const src=fs.readFileSync('extensions/light-plan/index.ts','utf8');
  for(const marker of ['name: "update_plan"','registerCommand("plan"','promptGuidelines','plan.json','session_start']) assert.ok(src.includes(marker),marker);
  console.log('LIGHT-PLAN-PASS');
})().catch(error=>{console.error(error);process.exit(1)});
