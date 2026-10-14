"""Real two-process Gloo audit using random tiny Qwen weights and synthetic tensors."""
import ast
import copy
import datetime
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace

REPO = Path('/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/code-repositories/03/iploc-szy')
sys.path.insert(0, str(REPO))
import torchvision
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel as DDP
from iploc_szy.rl import trainer as t


def fixture(directory):
    tree = ast.parse((REPO/'tests/test_e013_grpo_tiny.py').read_text())
    fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef))
    setup = []
    for node in fn.body:
        if isinstance(node, ast.With):
            break
        setup.append(node)
    imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
    scope = {'tmp_path': Path(directory)}
    exec(compile(ast.Module(body=imports+setup, type_ignores=[]), '<tiny-fixture>', 'exec'), scope)
    model = scope['model']
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
    return model, scope['batch']


def accumulate(runtime, batch, data_rank, config):
    for condition in range(2):
        runtime.unwrapped_model.eval()
        inputs = dict(batch, pixel_values=batch['pixel_values'] + data_rank * .15 + condition * .2)
        prompt = t.PromptBatch(row={'id':'synthetic', 'target_present':True}, batch=inputs, target_box=None)
        records = []
        for index in range(2):
            ids = torch.cat([inputs['input_ids'], torch.tensor([[4+index, 8+data_rank, 6]])], dim=1)
            positive_ids = ids.clone(); positive_ids[0,-2] = 10+data_rank
            with torch.no_grad():
                old = t.completion_logp(runtime.unwrapped_model, inputs, ids).detach()
            cf = {'ids':positive_ids, 'positive_mask':torch.tensor([False,True,False]),
                  'negative_mask':torch.tensor([False,True,False]), 'reward_gain':0.1}
            records.append(t.RolloutRecord(ids, 'synthetic', True, {'total':float(index)}, old, cf, 'applied'))
        refs = t._replay_anchor(runtime, prompt, records)
        group = t.RolloutGroup(prompt, records, refs, torch.tensor([-1.,1.]))
        t._backward_and_log(config, runtime, group, row_index=condition, pair_size=2, step=0, log=io.StringIO())


def worker(rank, root):
    torch.set_num_threads(1)
    dist.init_process_group('gloo', init_method='file://'+str(Path(root)/'rendezvous'),
                            rank=rank, world_size=2, timeout=datetime.timedelta(seconds=60))
    model, batch = fixture(Path(root)/f'fixture{rank}')
    serial = copy.deepcopy(model)
    policy_names = [n for n,p in model.named_parameters() if p.requires_grad]
    frozen = {n:p.detach().clone() for n,p in model.named_parameters() if '.anchor.' in n}
    ddp = DDP(model, find_unused_parameters=False, broadcast_buffers=False)
    runtime = SimpleNamespace(model=ddp, unwrapped_model=model, world_size=2)
    serial_runtime = SimpleNamespace(model=serial, unwrapped_model=serial, world_size=1)
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=1e-4)
    serial_optimizer = torch.optim.AdamW([p for p in serial.parameters() if p.requires_grad], lr=1e-4)
    config = {'group_size':2, 'beta':.04, 'counterfactual':{'weight':.1,'beta':.1}}
    max_grad_error = 0.
    for step in range(2):
        optimizer.zero_grad(set_to_none=True)
        serial_optimizer.zero_grad(set_to_none=True)
        accumulate(runtime, batch, rank, config)
        for data_rank in range(2):
            accumulate(serial_runtime, batch, data_rank, config)
        parameters = dict(model.named_parameters()); serial_parameters = dict(serial.named_parameters())
        for name in policy_names:
            actual, expected = parameters[name].grad, serial_parameters[name].grad
            assert actual is not None and expected is not None
            expected.div_(2)
            max_grad_error = max(max_grad_error, float((actual-expected).abs().max()))
            torch.testing.assert_close(actual, expected, atol=2e-6, rtol=2e-4)
        optimizer.step(); serial_optimizer.step()
        for name in policy_names:
            torch.testing.assert_close(parameters[name],serial_parameters[name],atol=2e-6,rtol=2e-4)
        assert all(torch.equal(parameters[name], value) for name,value in frozen.items())
    if rank == 0:
        result = {'two_rank_gloo_vs_serial_global_batch':'passed', 'optimizer_steps':2,
            'anchor_unchanged':True, 'counterfactual_two_forwards':True,
            'gradient_checkpointing':True, 'max_abs_gradient_error':max_grad_error}
        Path('/tmp/e013-grpo-audit-20261010/ddp_results.json').write_text(json.dumps(result,indent=2))
        print(json.dumps(result))
    dist.destroy_process_group()


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='grpo-ddp-audit-', dir='/tmp') as directory:
        mp.spawn(worker, args=(directory,), nprocs=2, join=True)
