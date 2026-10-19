import json,pathlib,subprocess,sys
R=pathlib.Path('/defaultShare/archive/songzhengyue/projects/IPLoc')
repo=R/'mechanism/iploc-szy';sys.path.insert(0,str(repo))
from iploc_szy.branching import load_experiment_config
from iploc_szy.rl.task import validate_reward_config
from iploc_szy.prompting.variable_candidates import variable_prompt
from hashlib import sha256
cfg=load_experiment_config(repo/'configs/experiments/E-014/training/e014_boxes_then_scores_grpo.py')
t=cfg['settings']['trainer'];validate_reward_config(t)
assert t['beta']==0 and t['reward']['exploration_penalty']==0 and t['reward']['multibox_bonus_weight']==0
assert t['prompt_variant']=='boxes_then_scores_v1'
E=R/'experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766'
log=(E/'managed_console.log').read_text(errors='replace')
out=dict(training_config=dict(beta=t['beta'],reward=t['reward'],prompt_variant=t['prompt_variant'],reward_scheme=t['reward_scheme'],adapter_path=t['adapter_path']),prompt_sha256=sha256(variable_prompt(t['prompt_variant']).encode()).hexdigest(),evaluation=dict(traceback_count=log.count('Traceback (most recent call last)'),progress_lines=[x for x in log.splitlines() if 'EVAL_PROGRESS' in x][-2:],payload_exists=(E/'payload').exists(),metrics_exists=(E/'payload/evaluation/metrics.json').exists()))
with (E/'startup_configuration_audit.json').open('x') as f:json.dump(out,f,indent=2)
print(json.dumps(out))
