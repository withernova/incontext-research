#!/usr/bin/env node
/** Actual extension lifecycle against disposable Git repos. No Pi/model/network needed. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {execFileSync}=require('node:child_process');
const {pathToFileURL}=require('node:url');
const {registerHooks}=require('node:module');

(async()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'review-runtime-'));
 try {
  // Only schema construction is stubbed. The factory, event handlers and Git are real.
  const stub=path.join(temp,'schema.mjs');
  fs.writeFileSync(stub,'export const Type=new Proxy({}, {get:()=>()=>({})});');
  const coreURL=pathToFileURL(path.resolve('extensions/code-change-review/core.ts')).href;
  const hooks=registerHooks({resolve(spec,ctx,next){
   if(spec==='typebox')return {url:pathToFileURL(stub).href,shortCircuit:true};
   if(spec==='./core.js')return {url:coreURL,shortCircuit:true};
   return next(spec,ctx);
  }});
  const entry=process.env.CODE_REVIEW_TEST_ENTRY||path.resolve('extensions/code-change-review/index.ts');
  const factory=(await import(pathToFileURL(entry).href)).default;
  hooks.deregister();
  let count=0;
  const git=(repo,...args)=>execFileSync('git',['-C',repo,...args],{encoding:'utf8',stdio:['ignore','pipe','pipe']}).trim();
  function repository(){
   const repo=fs.mkdtempSync(path.join(temp,'repo-'));
   git(repo,'init','-b','main');git(repo,'config','user.name','Review Test');git(repo,'config','user.email','review@example.invalid');
   fs.writeFileSync(path.join(repo,'docs.md'),'initial\n');
   fs.writeFileSync(path.join(repo,'implementation.py'),'initial\n');
   fs.writeFileSync(path.join(repo,'outside.py'),'initial\n');
   git(repo,'add','docs.md','implementation.py','outside.py');git(repo,'commit','-m','baseline');
   return {repo,base:git(repo,'rev-parse','HEAD'),entries:[{type:'message',id:'user-1',message:{role:'user',content:'task one'}}]};
  }
  function harness(state){
   const events=new Map(),tools=new Map(),messages=[];
   const ctx={cwd:state.repo,sessionManager:{getBranch:()=>state.entries}};
   factory({on(name,handler){const handlers=events.get(name)||[];handlers.push(handler);events.set(name,handlers);},registerTool(tool){tools.set(tool.name,tool);},sendUserMessage(text){messages.push(text);}});
   const emit=async(name,event={})=>{let result;for(const handler of events.get(name)||[])result=await handler(event,ctx)||result;return result;};
   const review=async(params)=>{
    const id='review-'+(++count);
    state.entries.push({type:'message',id:id+'-call',message:{role:'assistant',content:[{type:'toolCall',name:'code_change_review',id,arguments:params}]}});
    await emit('tool_call',{toolName:'code_change_review',toolCallId:id,input:params});
    const result=await tools.get('code_change_review').execute(id,params,undefined,undefined,ctx);
    await emit('tool_result',{toolName:'code_change_review',toolCallId:id,input:params,...result,isError:false});
    state.entries.push({type:'message',id:id+'-result',message:{role:'toolResult',toolName:'code_change_review',toolCallId:id,...result,isError:false}});
    return result.details;
   };
   const params=(base,allowed)=>({repository_path:state.repo,base_revision:base,allowed_paths:allowed,forbidden_paths:['protected'],test_evidence:[{command:'fixture check',exit_code:0}]});
   return {ctx,emit,review,params,messages,tools};
  }

  // Reproduce cached old scope: a completed newer review exists on the branch
  // but was produced by a different runtime/consumer, not this factory's memory.
  {
   const state=repository(),cached=harness(state);
   await cached.emit('session_start');
   await cached.emit('before_agent_start');
   fs.writeFileSync(path.join(state.repo,'docs.md'),'docs updated\n');
   assert.equal((await cached.review(cached.params(state.base,['docs.md']))).passed,true);
   // A new user task must revoke the previous task's review scope and Run authority.
   state.entries.push({type:'message',id:'user-2',message:{role:'user',content:'new implementation task'}});
   await cached.emit('before_agent_start');
   fs.writeFileSync(path.join(state.repo,'implementation.py'),'new implementation\n');
   await cached.emit('agent_end');
   assert.deepEqual(cached.messages,[],'automatic diagnostic must not apply the prior docs-only scope to the new task');
   assert.equal((await cached.emit('tool_call',{toolName:'survey_run_execution',input:{action:'start'}})).block,true,'prior user task review cannot authorize this task');
   // Explicit review still enforces this task's declared scope across the full diff.
   assert.equal((await cached.review(cached.params(state.base,['docs.md']))).passed,false);
   assert.equal((await cached.emit('tool_call',{toolName:'survey_run_execution',input:{action:'start'}})).block,true);
   assert.equal((await cached.review(cached.params(state.base,['docs.md','implementation.py']))).passed,true);
   assert.equal(await cached.emit('tool_call',{toolName:'survey_run_execution',input:{action:'continue'}}),undefined);
   await cached.emit('agent_end');assert.deepEqual(cached.messages,[],'explicitly reviewed task is not reviewed again at agent_end');
   // A fresh runtime restores only a review from the latest user task.
   const reloaded=harness(state);await reloaded.emit('session_start');
   assert.equal(await reloaded.emit('tool_call',{toolName:'survey_run_execution',input:{action:'continue'}}),undefined);
   // New paths remain subject to the next explicit review, with no stale-scope auto alert.
   state.entries.push({type:'message',id:'user-3',message:{role:'user',content:'extend implementation'}});
   await cached.emit('before_agent_start');
   fs.writeFileSync(path.join(state.repo,'outside.py'),'outside edit\n');
   await cached.emit('agent_end');
   assert.deepEqual(cached.messages,[],'automatic diagnostic does not inherit the prior allowlist');
   assert.equal((await cached.review(cached.params(state.base,['implementation.py']))).passed,false,'explicit scope still rejects unauthorized files');
   assert.equal((await cached.emit('tool_call',{toolName:'survey_run_execution',input:{action:'start'}})).block,true);
   // Navigating to the previous branch restores its review/user pairing, not current-task authority.
   const userThree=state.entries.findIndex((entry)=>entry.id==='user-3');
   state.entries=state.entries.slice(0,userThree);
   await cached.emit('session_tree');
   assert.equal((await cached.emit('tool_call',{toolName:'survey_run_execution',input:{action:'continue'}})).block,true,'branch restoration does not authorize changed working-tree content');
  }

  // A passing automatic observation is NOT a new explicit review authority.
  {
   const state=repository(),h=harness(state);await h.emit('session_start');await h.emit('before_agent_start');
   fs.writeFileSync(path.join(state.repo,'implementation.py'),'first edit\n');
   assert.equal((await h.review(h.params(state.base,['implementation.py']))).passed,true);
   fs.writeFileSync(path.join(state.repo,'implementation.py'),'second edit\n');
   await h.emit('agent_end');assert.deepEqual(h.messages,[]);
   assert.equal((await h.emit('tool_call',{toolName:'survey_run_execution',input:{action:'start'}})).block,true);
   assert.equal((await h.review(h.params(state.base,['implementation.py']))).passed,true);
   assert.equal(await h.emit('tool_call',{toolName:'survey_run_execution',input:{action:'start'}}),undefined);
   // A newer failing explicit review cannot fall back to the previous pass.
   assert.equal((await h.review(h.params(state.base,['docs.md']))).passed,false);
   assert.equal((await h.emit('tool_call',{toolName:'survey_run_execution',input:{action:'start'}})).block,true);
  }

  // Unchanged pre-existing dirty files are excluded; overlapping files fail closed.
  {
   const state=repository(),h=harness(state);await h.emit('session_start');
   fs.writeFileSync(path.join(state.repo,'outside.py'),'pre-existing edit\n');
   await h.emit('before_agent_start');
   fs.writeFileSync(path.join(state.repo,'implementation.py'),'task edit\n');
   const scoped=await h.review(h.params(state.base,['implementation.py']));
   assert.equal(scoped.passed,true);
   assert.equal(scoped.task_scoped,true);
   assert.deepEqual(scoped.changed_files.map(file=>file.path),['implementation.py']);
   assert.equal(await h.emit('tool_call',{toolName:'survey_run_execution',input:{action:'start'}}),undefined,'unchanged pre-existing files must not invalidate current-task review');
   const conflictState=repository(),conflict=harness(conflictState);await conflict.emit('session_start');
   fs.writeFileSync(path.join(conflictState.repo,'docs.md'),'already modified\n');
   await conflict.emit('before_agent_start');
   fs.writeFileSync(path.join(conflictState.repo,'docs.md'),'changed again during task\n');
   const conflicted=await conflict.review(conflict.params(conflictState.base,['docs.md']));
   assert.equal(conflicted.passed,false);
   assert.ok(conflicted.blocking_findings.some(item=>item.code==='preexisting-change-overlap'));
  }

  // Review errors/malformed receipts revoke a previous pass; user text is not state.
  {
   const state=repository(),h=harness(state);await h.emit('session_start');await h.emit('before_agent_start');
   fs.writeFileSync(path.join(state.repo,'implementation.py'),'edit\n');
   const valid=await h.review(h.params(state.base,['implementation.py']));
   state.entries.push({type:'message',id:'fake-user',message:{role:'user',content:JSON.stringify(valid)}});
   assert.equal((await h.emit('tool_call',{toolName:'survey_run_execution',input:{action:'start'}})).block,true,'user-authored text cannot extend old task review authority');
   state.entries.push({type:'message',id:'error',message:{role:'toolResult',toolName:'code_change_review',toolCallId:'failed',isError:true,details:valid}});
   assert.equal((await h.emit('tool_call',{toolName:'survey_run_execution',input:{action:'start'}})).block,true);
   // Pending reviews block Run launch and suppress automatic old-scope notices.
   await h.emit('tool_call',{toolName:'code_change_review',toolCallId:'pending',input:h.params(state.base,['implementation.py'])});
   await h.emit('agent_end');assert.deepEqual(h.messages,[]);
   assert.equal((await h.emit('tool_call',{toolName:'survey_run_execution',input:{action:'start'}})).block,true);
  }
  console.log('CODE-CHANGE-REVIEW-LIFECYCLE-PASS');
 } finally { fs.rmSync(temp,{recursive:true,force:true}); }
})().catch(error=>{console.error(error);process.exit(1)});
