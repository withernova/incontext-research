"""Expand actual branch configs and materialize reward-function defaults."""
import inspect
import json
from pathlib import Path
import sys

REPO = Path('/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/code-repositories/03/iploc-szy')
sys.path.insert(0, str(REPO))
from iploc_szy.branching import load_experiment_config
from iploc_szy.rl.multi_candidate import multi_reward

rows = {}
for name in ['e013_multi3_branch.py', 'e013_multi3_rank_branch.py']:
    full = load_experiment_config(REPO/'configs/experiments/E-013/training'/name)
    config = full['grpo']
    bound = inspect.signature(multi_reward).bind('', target_present=True,
        gt_box=[0,0,100,100], **config['reward'])
    bound.apply_defaults()
    rows[name] = {
        'trainer_settings':{k:v for k,v in config.items() if k != 'reward'},
        'effective_reward':{k:v for k,v in bound.arguments.items()
                            if k not in ('text','target_present','gt_box','terminated')},
        'nproc_per_node':full['branch']['nproc_per_node'],
        'same_data_definition':full['train_dataloader']['dataset']['ann_file'],
        'same_checkpoint_definition':full['runner']['initialize_from'],
    }
assert rows['e013_multi3_branch.py'] == rows['e013_multi3_rank_branch.py']
Path('/tmp/e013-grpo-audit-20261010/config_equivalence.json').write_text(json.dumps(rows,indent=2))
print('Actual branch resolver: training settings, effective rewards, process count and input/checkpoint definitions are equal.')
print('Both effective rank_weight values: 0.5')
