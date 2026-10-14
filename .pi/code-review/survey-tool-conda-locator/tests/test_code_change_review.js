#!/usr/bin/env node
const assert=require('node:assert/strict'),fs=require('node:fs');
(async()=>{
  const core=await import('../extensions/code-change-review/core.ts');
  assert.deepEqual(core.parsePorcelainZ(' M src/a.ts\0?? new.txt\0'),[
    {path:'src/a.ts',status:' M',untracked:false},{path:'new.txt',status:'??',untracked:true},
  ]);
  assert.deepEqual(core.parsePorcelainZ('R  src/new.ts\0src/old.ts\0'),[{path:'src/new.ts',status:'R ',untracked:false}]);
  const diff='diff --git a/src/a.ts b/src/a.ts\n--- a/src/a.ts\n+++ b/src/a.ts\n@@ -1 +1,2 @@\n old\n+const token = "abcdefghijklmnop";\n';
  assert.deepEqual(core.parseAddedLines(diff),[{path:'src/a.ts',line:2,text:'const token = "abcdefghijklmnop";'}]);
  let result=core.reviewChanges({files:[{path:'src/a.ts',status:' M'}],diff,allowedPaths:['src'],testEvidence:[{command:'npm test',exit_code:0}]});
  assert.equal(result.passed,false); assert.equal(result.blocking_findings[0].code,'generic-secret');
  result=core.reviewChanges({files:[{path:'docs/a.md',status:' M'}],diff:'',allowedPaths:['src'],testEvidence:[]});
  assert.equal(result.passed,false); assert.ok(result.blocking_findings.some(x=>x.code==='outside-allowed-path')); assert.ok(result.warnings.some(x=>x.code==='test-evidence-missing'));
  assert.equal(core.reviewFingerprint('s','d',{b:'2',a:'1'}),core.reviewFingerprint('s','d',{a:'1',b:'2'}));
  const params={allowed_paths:['docs.md','implementation.py'],forbidden_paths:['protected']};
  const receipt={contract:'pi.code-change-review/v1',diff_fingerprint:'a'.repeat(64),base_revision:'b'.repeat(40),passed:true,review_current:true,repository:{path:'/project'}};
  const call={type:'message',id:'call',message:{role:'assistant',content:[{type:'toolCall',name:'code_change_review',id:'review',arguments:params}]}};
  const completed={type:'message',id:'result',message:{role:'toolResult',toolName:'code_change_review',toolCallId:'review',details:receipt,isError:false}};
  assert.deepEqual(core.latestBranchReview([call,completed]),{id:'result',userEntryId:null,currentUserEntryId:null,params,result:receipt});
  const textOnly={...completed,message:{...completed.message,details:undefined,content:[{type:'text',text:JSON.stringify(receipt)}]}};
  assert.equal(core.latestBranchReview([call,textOnly]).result.passed,true);
  const failed={...completed,id:'failed',message:{...completed.message,isError:true}};
  assert.equal(core.latestBranchReview([call,completed,failed]).result,null);
  const malformed={...completed,id:'malformed',message:{...completed.message,details:{...receipt,diff_fingerprint:'not-a-hash'}}};
  assert.equal(core.latestBranchReview([call,completed,malformed]).result,null);
  assert.equal(core.latestBranchReview([completed]).result,null,'unpaired historical result must fail closed');
  const nested={...completed,message:{...completed.message,details:{...receipt,review_scope:params}}};
  assert.deepEqual(core.latestBranchReview([nested]).params,params,'persisted scope supports nested reviews without a transcript call');
  assert.equal(core.latestBranchReview([{type:'message',message:{role:'user',content:JSON.stringify(receipt)}}]),null);
  assert.equal(core.latestBranchReview([call,completed]).id,'result');
  const newTask={type:'message',id:'next-user',message:{role:'user',content:'different task'}};
  const taskReceipt=core.latestBranchReview([newTask,call,completed]);
  assert.equal(taskReceipt.userEntryId,'next-user');
  assert.equal(core.latestBranchReview([newTask,call,completed,{type:'message',id:'later-user',message:newTask.message}]).currentUserEntryId,'later-user');
  assert.equal(core.latestBranchReview([call]),null,'unfinished call must not be treated as a passed review');
  const badScope={...call,message:{...call.message,content:[{...call.message.content[0],arguments:{allowed_paths:[123]}}]}};
  assert.equal(core.latestBranchReview([badScope,completed]).result,null);
  const source=fs.readFileSync('extensions/code-change-review/index.ts','utf8');
  for(const marker of ['name: "code_change_review"','promptGuidelines','pi.on("tool_call"','pi.on("agent_end"','diff_fingerprint','survey_run_execution','reviewedFingerprint','repository_path','ssh_host','BatchMode=yes']) assert.ok(source.includes(marker),marker);
  for(const marker of ['latestBranchReview','sessionManager.getBranch()','executionMode: "sequential"','pi.on("tool_result"','pi.on("session_tree"','if (!automatic) adoptReview','epoch !== reviewEpoch']) assert.ok(source.includes(marker),marker);
  assert.ok(source.includes('execFile')); assert.ok(!source.includes('exec('));
  assert.ok(source.includes('if (!reviewedPassed || current.fingerprint !== reviewedFingerprint)'));
  const installer=fs.readFileSync('scripts/install-pi-components.sh','utf8'); assert.ok(installer.includes('code-change-review'));
  console.log('CODE-CHANGE-REVIEW-PASS');
})().catch(error=>{console.error(error);process.exit(1)});
