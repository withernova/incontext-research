// Invoke the installed code_change_review implementation with explicit scope.
// Only module import locations are adapted; review/commit logic is unchanged.
import fs from 'node:fs';
import path from 'node:path';
import { stripTypeScriptTypes, createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
const folder=path.resolve('.pi/code-review/e014-boxes-then-scores');
const audit=JSON.parse(fs.readFileSync(path.join(folder,'source_audit.json'),'utf8'));
const repo=path.resolve('code-repositories/03/iploc-szy');
const toolDir='/home/zhengyuesong/Tools/survey-tool/extensions/code-change-review';
const piMain=fs.realpathSync('/home/zhengyuesong/.nvm/versions/node/v24.19.0/bin/pi');
const typebox=createRequire(piMain).resolve('typebox');
let source=stripTypeScriptTypes(fs.readFileSync(path.join(toolDir,'index.ts'),'utf8'))
 .replace('"typebox"',JSON.stringify(pathToFileURL(typebox).href))
 .replace('"./core.js"',JSON.stringify(pathToFileURL(path.join(toolDir,'core.ts')).href));
const extension=(await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'))).default;
let tool;
extension({registerCommand(){},on(){},registerTool(value){if(value.name==='code_change_review')tool=value;}});
if(!tool)throw new Error('code_change_review not registered');
const params={repository_path:repo,base_revision:audit.baseline,
 task_id:'E-014-boxes-then-scores-v1',
 intent:'Implement all-boxes-then-all-scores protocol and explicit three-main-reward GRPO with both multi-box incentives zero; preserve old protocols and raw-token replay; add step0 recipe and EOS-aware evaluation.',
 allowed_paths:audit.changed_files,
 forbidden_paths:['.git','work_dirs','experiments','data','checkpoints'],
 test_evidence:[
  {command:'python3 .pi/code-review/e014-boxes-then-scores/source_audit.py',exit_code:0,summary:'Static AST 3.9 and source/hash comparison only; no imports, tests or execution of configs.'},
  {command:'python3 tools/audit_entrypoints.py --source-only --check-navigation',exit_code:0,summary:'Source navigation only; not runtime validation.'},
  {command:'git diff --check',exit_code:0,summary:'Whitespace/conflict-marker check only.'}],
 commit_paths:audit.changed_files,
 commit_message:'Add boxes-then-scores protocol with three-main-reward GRPO'};
const result=await tool.execute('explicit-code-review',params);
fs.writeFileSync(path.join(folder,'code_change_review.json'),JSON.stringify(result.details,null,2)+'\n',{flag:'wx'});
const r=result.details;
console.log(JSON.stringify({review_id:r.review_id,passed:r.passed,review_current:r.review_current,commit:r.commit?.sha,changed_files:r.changed_files?.length,blocking_findings:r.blocking_findings,warnings:r.warnings,tests_executed:false},null,2));
if(!r.passed||!r.review_current||!r.commit?.sha)process.exitCode=1;
