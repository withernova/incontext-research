binding = {'run_id': 'e014-20261015T172455Z-tier065-oracle005-selected015-score015-g8-kl0-sft659-400step-seed11451', 'run_dir': '/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-20261015T172455Z-tier065-oracle005-selected015-score015-g8-kl0-sft659-400step-seed11451', 'parent_run': 'e014-discovery-priority-score04-beta0-sft659-200step-seed11451', 'git_commit': 'e64c8742dec0ee88f08fed15712b989e55e9bc53', 'config': 'configs/experiments/E-014/training/e014_behavior_tier_g8_400step_grpo.py'}
import sys,json
from pathlib import Path
repo=Path('/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/iploc-szy')
sys.path.insert(0,str(repo))
from tools.run_symmetric_grpo import config_settings, source_preflight
s=config_settings(repo/binding['config'],['output.run_name='+binding['run_id']])
t=s['trainer']
assert t['group_size']==8 and t['max_steps']==400 and t['beta']==0
assert t['reward_scheme']=='candidate_behavior_tier_v1' and t['prompt_variant']=='boxes_then_scores_v1'
assert t['counterfactual']['weight']==0 and t['save_every_steps']==50
assert not Path(binding['run_dir']).exists()
facts=source_preflight(s);assert facts['git_commit']==binding['git_commit']
print(json.dumps(dict(preflight='passed',git_commit=facts['git_commit'],group_size=t['group_size'],max_steps=t['max_steps'],beta=t['beta'],reward_scheme=t['reward_scheme'],reward=t['reward'],seed=t['seed'],save_every_steps=t['save_every_steps'],max_new_tokens=t['max_new_tokens'],inputs=facts)))
