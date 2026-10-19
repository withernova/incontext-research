import pathlib,json,hashlib,subprocess,torch,re,collections
root=pathlib.Path('/defaultShare/archive/songzhengyue/projects/IPLoc');er=root/'experiments/E-014'
train=er/'e014-boxes-then-scores-beta0-sft659-seed11451';cp=train/'payload/grpo/checkpoints/step_000150';run=er/'e014-boxes-then-scores-beta0-step150-eval1766'
assert not run.exists()
assert subprocess.check_output(['git','-C',str(root/'mechanism/iploc-szy'),'rev-parse','HEAD'],text=True).strip()=='41698665d15742276bf22d1376e8d53a367c07db'
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=used_memory','--format=csv,noheader'],text=True).strip()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8388608),b''):h.update(b)
 return h.hexdigest()
files=[cp/'adapter/policy/adapter_config.json',cp/'adapter/policy/adapter_model.safetensors',cp/'optimizer.pt']
before=[(p.stat().st_size,p.stat().st_mtime_ns) for p in files];assert all(s>0 for s,_ in before)
assert torch.load(cp/'optimizer.pt',map_location='cpu',weights_only=True)['steps']==150
cfg=json.loads((train/'payload/trainer_config.json').read_text());assert cfg['beta']==0 and cfg['prompt_variant']=='boxes_then_scores_v1';assert cfg['reward']['exploration_penalty']==cfg['reward']['multibox_bonus_weight']==0
baseline=er/'e014-boxes-then-scores-sft659-step0-eval1766/inputs'
old=json.loads((baseline/'inputs.json').read_text());manifest=baseline/'manifest.json';assert sha(manifest)==old['derived_manifest_sha256'];assert len(json.loads(manifest.read_text()))==1766
for src,digest in old['source_sha256'].items():
 if 'manifests/' in src:assert sha(pathlib.Path(src))==digest
hashes={str(p):sha(p) for p in files};assert before==[(p.stat().st_size,p.stat().st_mtime_ns) for p in files]
(run/'inputs').mkdir(parents=True)
(run/'inputs/manifest.json').write_bytes(manifest.read_bytes())
inputs=dict(checkpoint=str(cp),step=150,source_sft_step=659,expected_samples=1766,prompt_variant='boxes_then_scores_v1',derived_manifest_sha256=sha(run/'inputs/manifest.json'),source_sha256=hashes,source_manifest_sha256=old['source_sha256'],code_sha='41698665d15742276bf22d1376e8d53a367c07db')
(run/'inputs/inputs.json').write_text(json.dumps(inputs,indent=2))
steps=collections.defaultdict(int)
for m in re.finditer(r'\{"rank":\s*(\d+),\s*"step":\s*(\d+),\s*"gradient_norm"',(train/'managed_console.log').read_text(errors='replace')):steps[m[1]]=max(steps[m[1]],int(m[2]))
print(json.dumps({'prepared':True,'checkpoint_step':150,'weights_sha256':hashes[str(files[1])],'last_train_steps':dict(steps),'samples':1766,'beta':cfg['beta']}))
