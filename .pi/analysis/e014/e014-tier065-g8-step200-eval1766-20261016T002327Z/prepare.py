binding = {'run_id': 'e014-tier065-g8-step200-eval1766-20261016T002327Z', 'run_dir': '/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-tier065-g8-step200-eval1766-20261016T002327Z', 'checkpoint': '/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-20261015T172455Z-tier065-oracle005-selected015-score015-g8-kl0-sft659-400step-seed11451/payload/grpo/checkpoints/step_000200', 'source_training_run_id': 'e014-20261015T172455Z-tier065-oracle005-selected015-score015-g8-kl0-sft659-400step-seed11451', 'source_training_git_commit': 'e64c8742dec0ee88f08fed15712b989e55e9bc53', 'evaluation_git_commit': 'e64c8742dec0ee88f08fed15712b989e55e9bc53'}
import pathlib,json,hashlib,subprocess,torch
root=pathlib.Path('/defaultShare/archive/songzhengyue/projects/IPLoc');er=root/'experiments/E-014'
run=pathlib.Path(binding['run_dir']);cp=pathlib.Path(binding['checkpoint']);train=cp.parents[3]
assert not run.exists()
assert subprocess.check_output(['git','-C',str(root/'mechanism/iploc-szy'),'rev-parse','HEAD'],text=True).strip()==binding['evaluation_git_commit']
# GPU availability must be checked immediately before managed launch.
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8388608),b''):h.update(block)
 return h.hexdigest()
files=[cp/'adapter/policy/adapter_config.json',cp/'adapter/policy/adapter_model.safetensors',cp/'optimizer.pt']
before=[(p.stat().st_size,p.stat().st_mtime_ns) for p in files];assert all(s>0 for s,_ in before)
assert torch.load(cp/'optimizer.pt',map_location='cpu',weights_only=True)['steps']==200
cfg=json.loads((train/'payload/trainer_config.json').read_text())
assert cfg['beta']==0 and cfg['reward_scheme']=='candidate_behavior_tier_v1'
assert cfg['reward']['score_weight']==.15 and cfg['max_steps']==400 and cfg['group_size']==8 and cfg['prompt_variant']=='boxes_then_scores_v1'
baseline=er/'e014-boxes-then-scores-sft659-step0-eval1766/inputs';old=json.loads((baseline/'inputs.json').read_text());manifest=baseline/'manifest.json'
assert sha(manifest)==old['derived_manifest_sha256'];assert len(json.loads(manifest.read_text()))==1766
for src,digest in old['source_sha256'].items():
 if 'manifests/' in src:assert sha(pathlib.Path(src))==digest
hashes={str(p):sha(p) for p in files};assert before==[(p.stat().st_size,p.stat().st_mtime_ns) for p in files]
(run/'inputs').mkdir(parents=True)
(run/'inputs/manifest.json').write_bytes(manifest.read_bytes())
inputs=dict(checkpoint=str(cp),step=200,source_sft_step=659,expected_samples=1766,prompt_variant='boxes_then_scores_v1',derived_manifest_sha256=sha(run/'inputs/manifest.json'),source_sha256=hashes,source_manifest_sha256=old['source_sha256'],source_training_run_id=binding['source_training_run_id'],source_training_git_commit=binding['source_training_git_commit'],code_sha=binding['evaluation_git_commit'])
(run/'inputs/inputs.json').write_text(json.dumps(inputs,indent=2))
print(json.dumps({'prepared':True,'checkpoint_step':200,'weights_sha256':hashes[str(files[1])],'samples':1766,'payload_absent':not (run/'payload').exists()}))
