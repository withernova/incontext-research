const assert = require('node:assert/strict');
(async () => {
  const {codeBlocks, recentCodeBlocks, bashSingleLine, shellWarnings} = await import('../extensions/copy-code/core.ts');
  const raw = 'bash tools/run/eval/run_e011_inter.sh \\\n  branch.source=e011_gt_mask \\\n  parent_checkpoint=/defaultShare/checkpoints/samples_00126264_step_001973 \\\n  \'attention_intervention.heads=["L26H25","L24H13"]\' \\\n  evaluation.limit=20\n';
  assert.equal(codeBlocks('```bash\n' + raw + '```')[0].text, raw);
  assert.equal(bashSingleLine(raw), raw.replaceAll('\\\n', '').replace(/\n$/, ''));
  assert.equal(bashSingleLine('echo verylong\\\npath\n'), 'echo verylongpath');
  assert.equal(codeBlocks('~~~python\nx = "```"\n~~~')[0].text, 'x = "```"\n');
  assert.deepEqual(codeBlocks('```bash\nunclosed'), []);
  assert.deepEqual(recentCodeBlocks([
    {type:'message',message:{role:'assistant',content:[{type:'thinking',thinking:'```sh\nsecret\n```'},{type:'text',text:'```sh\necho old\n```'}]}},
    {type:'message',message:{role:'toolResult',content:[{type:'text',text:'```sh\nunwanted\n```'}]}},
    {type:'message',message:{role:'assistant',content:[{type:'text',text:'```sh\necho new\n```'}]}},
  ]).map(block=>block.text), ['echo new\n','echo old\n']);
  for (const broken of ['echo a \\\n\n b\n','echo path=/long/174853785\n 543Z/checkpoint \\\n x=1\n','echo a \\ \n b\n',"echo 'hello\nworld'\n",'cat <<EOF\nhello\nEOF\n','echo a # comment \\\n b\n','echo a\necho b\n','echo a \\\n']) assert.throws(()=>bashSingleLine(broken),undefined,broken);
  assert.ok(shellWarnings('bash x \\\n\n arg=1').length);
  assert.ok(shellWarnings('path=/long/174853785\n 543Z/file').length);
  const fs = require('node:fs'), path = require('node:path');
  let copied = null; globalThis.copyCodeTestClipboard = async text => {copied = text;};
  const source = require('node:module').stripTypeScriptTypes(fs.readFileSync('extensions/copy-code/index.ts','utf8'))
    .replace(/import \{[^}]+\} from "@earendil-works\/pi-coding-agent";/, 'const copyToClipboard = globalThis.copyCodeTestClipboard;')
    .replace('"./core.js"', JSON.stringify(require('node:url').pathToFileURL(path.resolve('extensions/copy-code/core.ts')).href));
  const extension = (await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'))).default;
  let command; extension({registerCommand:(name,value)=>{assert.equal(name,'copy-code');command=value;}});
  const notifications=[];
  const ctx={hasUI:true,sessionManager:{getBranch:()=>[{type:'message',message:{role:'assistant',content:[{type:'text',text:'```bash\n'+raw+'```'}]}}]},ui:{select:async (_title,options)=>options.find(option=>option.startsWith('Bash')),notify:(text)=>notifications.push(text),confirm:async()=>false}};
  await command.handler('1',ctx);
  assert.equal(copied,bashSingleLine(raw));
  copied=null;ctx.ui.select=async()=>undefined;
  await command.handler('1',ctx);assert.equal(copied,null);
  await command.handler('999',ctx);assert.equal(copied,null);
  assert.ok(notifications.some(text=>text.includes('序号超出范围')));
  console.log('COPY-CODE-PASS');
})().catch(error=>{console.error(error);process.exit(1)});
