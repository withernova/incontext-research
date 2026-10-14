#!/usr/bin/env node
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../extensions/pi-session-export/index.ts'),'utf8');
for(const marker of ['registerCommand("export-copyable"','getSessionFile()','pi_session_export.py','copy-friendly HTML','path.basename(session,".jsonl")','raw Markdown copy','shell:false'])assert.ok(source.includes(marker),marker);
assert.ok(!source.includes('exec('));
console.log('PI-SESSION-EXPORT-EXTENSION-PASS');
