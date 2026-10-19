import hashlib,json,pathlib,subprocess,copy
R=pathlib.Path('/defaultShare/archive/songzhengyue/projects/IPLoc')
repo=R/'mechanism/iploc-szy'
assert subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()=='41698665d15742276bf22d1376e8d53a367c07db'
assert not subprocess.check_output(['git','-C',str(repo),'status','--porcelain'],text=True).strip()
apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=used_memory','--format=csv,noheader'],text=True).strip()
assert not apps,'GPU compute applications are still active'
run=R/'experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766'
assert not run.exists(),'fresh Run directory required'
source=R/'experiments/E-009/E009-real-focus-data/manifests/test_combined_lasot600_gotval_taoval_1shot_focus.json'
cp=R/'experiments/E-013/focus-confidence-sft/checkpoints/samples_00042136_step_000659'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
 return h.hexdigest()
assert sha(source)=='48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b'
rows=json.loads(source.read_text());assert len(rows)==1766
aliases=sorted([(p.resolve(),p) for p in (R/'mechanism/dataset').iterdir() if p.is_dir()],key=lambda x:len(str(x[0])),reverse=True)
for row in rows:
 before=copy.deepcopy(row);paths=[]
 for v in row['image_path']:
  p=pathlib.Path(v[0] if isinstance(v,list) else v)
  for physical,alias in aliases:
   try:q=alias/p.relative_to(physical)
   except ValueError:continue
   assert q.is_file();paths.append([str(q)] if isinstance(v,list) else str(q));break
  else:raise ValueError('image outside registered alias')
 row['image_path']=paths
 assert {k:v for k,v in row.items() if k!='image_path'}=={k:v for k,v in before.items() if k!='image_path'}
sources={str(p):sha(p) for p in (source,cp/'adapter/adapter_config.json',cp/'adapter/adapter_model.safetensors')}
(run/'inputs').mkdir(parents=True)
manifest=run/'inputs/manifest.json'
with manifest.open('x') as f:json.dump(rows,f,ensure_ascii=False)
inputs=dict(checkpoint=str(cp),step=0,source_sft_step=659,expected_samples=1766,prompt_variant='boxes_then_scores_v1',source_sha256=sources,derived_manifest_sha256=sha(manifest),code_sha='41698665d15742276bf22d1376e8d53a367c07db')
with (run/'inputs/inputs.json').open('x') as f:json.dump(inputs,f,indent=2)
print(json.dumps({'prepared':True,'samples':len(rows),'source_sha256_verified':True,'gpu_idle':True,'payload_absent':not (run/'payload').exists()}))
