binding = {'run_id': 'e014-20261016T014300Z-discovery-score05-g8-kl0-sft659-400step-seed11451', 'run_dir': '/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-20261016T014300Z-discovery-score05-g8-kl0-sft659-400step-seed11451', 'parent_run': 'e014-discovery-priority-score04-beta0-sft659-200step-seed11451', 'git_commit': 'e64c8742dec0ee88f08fed15712b989e55e9bc53', 'config': 'configs/experiments/E-014/training/e014_discovery_priority_score04_grpo.py', 'overrides': ['output.run_name=e014-20261016T014300Z-discovery-score05-g8-kl0-sft659-400step-seed11451', 'settings.trainer.reward.score_weight=0.5', 'settings.trainer.group_size=8', 'settings.trainer.max_steps=400', 'settings.trainer.beta=0.0']}
from pathlib import Path
import json
r=Path(binding['run_dir']);p=r/'payload'
out={'run':binding['run_id'],'payload_exists':p.exists()}
for name in ['plan.json','trainer_config.json','status.json','failure.json']:
 f=p/name
 if f.exists():
  x=json.loads(f.read_text())
  if name=='plan.json':out['plan']={k:x.get(k) for k in ['total_steps','start_step','original_rows','symmetry_rows','nproc_per_node']}
  elif name=='trainer_config.json':out['trainer']={k:x.get(k) for k in ['group_size','max_steps','beta','reward_scheme','prompt_variant','seed','save_every_steps','reward']}
  else:out[name]=x
log=r/'managed_console.log'
if log.exists():
 text=log.read_text(errors='replace')[-16000:]
 out['console_bytes']=log.stat().st_size
 out['traceback_seen']='Traceback (most recent call last)' in text
print(json.dumps(out))
