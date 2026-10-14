#!/usr/bin/env node
// Exercise the real extension against an isolated Git repository.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFile, execFileSync } = require('node:child_process');
const { stripTypeScriptTypes } = require('node:module');
const { pathToFileURL } = require('node:url');

(async () => {
  let source = fs.readFileSync('extensions/code-change-review/index.ts', 'utf8');
  // Simulate SSH's remote shell interpretation without contacting a server.
  globalThis.reviewTestExecFile = (command, args, options, callback) => {
    if (command === 'ssh') {
      assert.equal(args.at(-2), 'fixture-host');
      return execFile('sh', ['-c', args.at(-1)], options, callback);
    }
    return execFile(command, args, options, callback);
  };
  globalThis.reviewTestExecFile[require('node:util').promisify.custom] = (command, args, options) => new Promise((resolve, reject) => {
    globalThis.reviewTestExecFile(command, args, options, (error, stdout, stderr) => {
      if (error) { error.stdout = stdout; error.stderr = stderr; reject(error); }
      else resolve({stdout, stderr});
    });
  });
  source = stripTypeScriptTypes(source)
    .replace('import { execFile } from "node:child_process";', 'const execFile = globalThis.reviewTestExecFile;')
    .replace('import { Type } from "typebox";', 'const Type = new Proxy({}, {get: () => () => ({})});')
    .replace('"./core.js"', JSON.stringify(pathToFileURL(path.resolve('extensions/code-change-review/core.ts')).href));
  const extension = (await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'))).default;
  const repo = fs.mkdtempSync(path.join(os.tmpdir(), 'review-checkpoint-'));
  const git = (...args) => execFileSync('git', ['-C', repo, ...args], {encoding:'utf8'}).trim();
  const write = (file, text) => fs.writeFileSync(path.join(repo, file), text);
  git('init', '-q'); git('config', 'user.name', 'Review Test'); git('config', 'user.email', 'review@example.invalid');
  write('code.py', 'value = 1\n'); write('other.txt', 'baseline\n');
  git('add', '--', 'code.py', 'other.txt'); git('commit', '-qm', 'baseline');
  const baseline = git('rev-parse', 'HEAD');
  const events = {}; const registered = {}; const entries=[{type:'message',id:'user-task',message:{role:'user',content:'implement code'}}]; let sequence=0;
  const context={cwd:repo,sessionManager:{getBranch:()=>entries}};
  extension({on: (name, fn) => events[name] = fn, registerTool: tool => registered[tool.name] = tool, sendUserMessage: () => {}});
  await events.session_start({}, context);
  const review = async args => {
    const id='review-'+(++sequence);
    entries.push({type:'message',id:id+'-call',message:{role:'assistant',content:[{type:'toolCall',id,name:'code_change_review',arguments:args}]}});
    await events.tool_call({toolName:'code_change_review',toolCallId:id,input:args},context);
    try {
      const result=await registered.code_change_review.execute(id,args);
      await events.tool_result({toolName:'code_change_review',toolCallId:id,input:args,...result,isError:false},context);
      entries.push({type:'message',id:id+'-result',message:{role:'toolResult',toolName:'code_change_review',toolCallId:id,...result,isError:false}});
      return result.details;
    } catch(error) {
      await events.tool_result({toolName:'code_change_review',toolCallId:id,input:args,isError:true},context);
      entries.push({type:'message',id:id+'-result',message:{role:'toolResult',toolName:'code_change_review',toolCallId:id,isError:true}});
      throw error;
    }
  };
  const gate = () => events.tool_call({toolName:'survey_run_execution', input:{action:'start'}},context);
  write('code.py', 'value = 2\n'); write('new.py', 'new_value = 3\n');
  write('other.txt', 'preexisting user edit\n'); git('add', '--', 'other.txt');
  const result = await review({repository_path:repo, commit_paths:['code.py','new.py'], commit_message:'Implement checkpoint', test_evidence:[{command:'fixture check',exit_code:0}]});
  assert.equal(result.passed, true); assert.equal(result.review_current, true);
  assert.equal(result.base_revision, baseline); assert.equal(result.commit.sha, git('rev-parse','HEAD'));
  assert.deepEqual(git('show','--pretty=format:','--name-only','HEAD').split('\n').sort(), ['code.py','new.py']);
  assert.equal(git('diff','--cached','--name-only'), 'other.txt', 'preserves unrelated staging');
  assert.equal(await gate(), undefined, 'commit does not stale a passing review');
  write('code.py','value = 4\n');
  assert.equal((await gate()).block, true, 'later content edits invalidate review');
  const checked = await review({repository_path:repo, base_revision:baseline});
  assert.ok(checked.changed_files.some(file => file.path === 'new.py'), 'fixed-base review includes committed files');
  git('add','--','code.py');
  assert.equal(await gate(), undefined, 'staging alone does not invalidate review');
  await assert.rejects(review({repository_path:repo,commit_paths:['.'],commit_message:'bad'}), /精确/);
  const before = git('rev-parse','HEAD');
  write('code.py','<<<<<<< conflict\n');
  const blocked = await review({repository_path:repo,commit_paths:['code.py'],commit_message:'must not commit'});
  assert.equal(blocked.passed, false); assert.equal(blocked.commit, undefined);
  assert.equal(git('rev-parse','HEAD'), before, 'blocking review never commits');
  write('code.py','value = 5\n');
  const message = "remote checkpoint 'quoted' $HOME; printf SURPRISE";
  const remote = await review({repository_path:repo,ssh_host:'fixture-host',commit_paths:['code.py'],commit_message:message});
  assert.equal(remote.review_current,true);
  assert.equal(git('log','-1','--format=%B'),message, 'remote commit message is literal shell-safe data');
  assert.equal(await gate(),undefined);
  console.log('CODE-CHANGE-REVIEW-RUNTIME-PASS');
})().catch(error => {console.error(String(error.stack || error).replace(/data:text\/javascript;base64,[A-Za-z0-9+/=]+/g, '<extension>'));process.exit(1)});
