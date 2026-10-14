"""Read-only CPU audit of the existing GRPO code; all inputs are synthetic."""
import ast
import json
import math
from pathlib import Path
import sys
import tempfile

REPO = Path('/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/code-repositories/03/iploc-szy')
sys.path.insert(0, str(REPO))
import torchvision
import torch
from iploc_szy.rl.objective import group_advantages, grpo_loss
from iploc_szy.rl.multi_candidate import multi_reward
from iploc_szy.rl.sampling import completion_logp, reset_positions
from transformers import GenerationConfig

results = {}
ratios = [1.5, 0.7, 1.1, 0.95]
deltas = [0.4, -0.3, 0.1, -0.2]
for advantage in [-1.3, 0.0, 0.7]:
    current = torch.tensor([-1., -2., -3., -4.], dtype=torch.float64, requires_grad=True)
    old = current.detach() - torch.tensor(ratios, dtype=torch.float64).log()
    ref = current.detach() + torch.tensor(deltas, dtype=torch.float64)
    beta = 0.04
    actual = grpo_loss(current, old, ref, advantage, beta=beta)
    actual.backward()
    expected_loss = 0.0
    expected_grad = []
    for ratio, delta in zip(ratios, deltas):
        clipped = (advantage > 0 and ratio > 1.2) or (advantage < 0 and ratio < 0.8)
        effective = max(0.8, min(1.2, ratio)) if clipped else ratio
        expected_loss += (-effective * advantage + beta * (math.exp(delta) - delta - 1)) / 4
        expected_grad.append(((0 if clipped else -ratio * advantage) + beta * (1 - math.exp(delta))) / 4)
    # Advantage is converted to float32 by the public API for Python scalars.
    assert math.isclose(actual.item(), expected_loss, rel_tol=1e-6, abs_tol=1e-8)
    assert torch.allclose(current.grad, torch.tensor(expected_grad, dtype=torch.float64), atol=1e-7)
results['scalar_loss_and_gradient_oracle'] = '3 advantage signs, both clip boundaries: passed'

reward_group = torch.tensor([0., 1., 2., 3.])
ours = group_advantages(reward_group)
upstream = (reward_group - reward_group.mean()) / (reward_group.std() + 1e-4)
results['advantage_scale_relative_to_trl_0_15_2'] = float(ours[0] / upstream[0])

boxes = [[0,0,100,100], [0,0,60,100], [200,200,300,300]]
def reward(scores):
    text = '\n'.join(f'<answer>{json.dumps(box)}</answer><score>{score:.2f}</score>' for box, score in zip(boxes, scores))
    return multi_reward(text, target_present=True, gt_box=boxes[0])
calibrated, ranked = reward([1,1,0]), reward([1,.9,0])
assert calibrated['brier'] == 0 and ranked['brier'] > 0
assert calibrated['selected_index'] == ranked['selected_index'] == 0
assert ranked['total'] > calibrated['total']
results['ranking_calibration_counterexample'] = {
    'ious': calibrated['candidate_ious'],
    'scores_1_1_0': {'reward': calibrated['total'], 'brier': calibrated['brier']},
    'scores_1_09_0': {'reward': ranked['total'], 'brier': ranked['brier']},
}

# Reuse the existing random tiny two-image Qwen fixture, stopping before its checks.
tree = ast.parse((REPO/'tests/test_e013_grpo_tiny.py').read_text())
fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef))
setup = []
for node in fn.body:
    if isinstance(node, ast.With):
        break
    setup.append(node)
imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
with tempfile.TemporaryDirectory(prefix='grpo-probe-', dir='/tmp') as directory:
    scope = {'tmp_path': Path(directory)}
    exec(compile(ast.Module(body=imports+setup, type_ignores=[]), '<existing-tiny-fixture>', 'exec'), scope)
    model, batch = scope['model'], scope['batch']
    errors = []
    for seed in [11, 22, 33]:
        torch.manual_seed(seed)
        reset_positions(model)
        cfg = GenerationConfig(do_sample=True, temperature=1., top_k=0, top_p=1.,
            max_new_tokens=8, eos_token_id=63, pad_token_id=0, use_cache=True,
            return_dict_in_generate=True, output_scores=True)
        with torch.no_grad():
            generated = model.generate(**batch, generation_config=cfg, use_model_defaults=False)
            replay = completion_logp(model, batch, generated.sequences)
        tokens = generated.sequences[0, batch['input_ids'].shape[1]:]
        sampling = torch.stack([torch.log_softmax(scores[0].float(), -1)[token] for scores, token in zip(generated.scores, tokens)])
        error = float((sampling-replay).abs().max())
        assert torch.allclose(sampling, replay, atol=2e-5, rtol=1e-6), (seed,error)
        errors.append({'seed':seed, 'tokens':len(tokens), 'max_abs_logp_error':error})
    results['cached_sampling_vs_uncached_replay'] = errors

Path('/tmp/e013-grpo-audit-20261010/probe_results.json').write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
