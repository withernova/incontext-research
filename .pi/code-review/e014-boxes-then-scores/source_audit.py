"""Static source inspection only: no project imports or execution of configs/tests."""
import ast,hashlib,json,pathlib,subprocess
repo=pathlib.Path('code-repositories/03/iploc-szy').resolve()
base='7bb09c762b4e6030fe870b34f9c1a119d7c81425'
def git(*args):return subprocess.check_output(['git','-C',str(repo),*args])
def previous(name):return git('show',base+':'+name)
def tree(raw):return ast.parse(raw,feature_version=(3,9))
def fn(raw,name):return next(n for n in tree(raw).body if isinstance(n,ast.FunctionDef) and n.name==name)
def same(a,b):return ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
changed=sorted(set(git('diff','--name-only',base).decode().splitlines()+git('ls-files','--others','--exclude-standard').decode().splitlines()))
python_files=[name for name in changed if name.endswith('.py')]
for name in python_files:tree((repo/name).read_bytes())
unchanged=['iploc_szy/rl/trainer.py','iploc_szy/rl/sampling.py','iploc_szy/rl/core.py','iploc_szy/rl/policy.py','iploc_szy/rl/data.py','iploc_szy/rl/symmetric_data.py','iploc_szy/prompting/messages.py','iploc_szy/prompting/confidence.py','iploc_szy/evaluation/multi_candidate.py']
unchanged_hashes={}
for name in unchanged:
    data=(repo/name).read_bytes();assert data==previous(name),name
    unchanged_hashes[name]=hashlib.sha256(data).hexdigest()
name='iploc_szy/prompting/variable_candidates.py'
a=fn(previous(name),'variable_prompt');b=fn((repo/name).read_bytes(),'variable_prompt')
assert all(same(x,y) for x,y in zip(a.body[2:],b.body[2:])) and len(a.body)==len(b.body)
a=fn(previous(name),'variable_messages');b=fn((repo/name).read_bytes(),'variable_messages')
del b.body[1]
assert same(a,b)
name='iploc_szy/rl/variable_candidates.py'
a=fn(previous(name),'conditional_exploration_reward');b=fn((repo/name).read_bytes(),'conditional_exploration_reward')
assert b.args.kwonlyargs[-1].arg=='output_layout' and ast.literal_eval(b.args.kw_defaults[-1])=='interleaved'
b.args.kwonlyargs.pop();b.args.kw_defaults.pop()
old_assignment=next(x for x in a.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='candidates' for t in x.targets))
for i,x in enumerate(b.body):
    if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='candidates' for t in x.targets):b.body[i]=old_assignment
assert same(a,b),'Reward numerical formula changed beyond parser binding'
assert not any(x.startswith('configs/') and not ('boxes_then_scores' in x or x.endswith('ENTRYPOINT_INDEX.md')) for x in changed)
for name in ['configs/experiments/E-014/training/e014_boxes_then_scores_grpo.py','configs/experiments/E-014/evaluation/e014_boxes_then_scores_sft659_step0_eval1766.py']:
    calls=[x for x in ast.walk(tree((repo/name).read_bytes())) if isinstance(x,ast.Call)]
    assert all(isinstance(x.func,ast.Name) and x.func.id=='dict' for x in calls)
checks={'baseline':base,'changed_files':changed,'python_ast_39_files':len(python_files),'old_prompt_and_suffix_branches_source_identical':True,'old_reward_formula_and_defaults_preserved_except_explicit_parser_binding':True,'old_configs_unchanged':True,'new_configs_only_dict_calls_no_artifact_io':True,'unchanged_source_sha256':unchanged_hashes,'tests_executed':False,'runtime_imports_executed':False}
out=pathlib.Path('.pi/code-review/e014-boxes-then-scores/source_audit.json')
out.write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in checks.items() if k not in {'unchanged_source_sha256','changed_files'}},ensure_ascii=False))
