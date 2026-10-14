"""Source-only migration checks. Does not import project code or run launchers/tests."""
import ast
import json
from pathlib import Path
import re
import subprocess

ROOT = Path.cwd() / "code-repositories/03/iploc-szy"
BASE = "3c7ed5cdcde16c096b65021935002074f8080e51"
OUT = Path(__file__).resolve().parent

def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])

def original(path):
    return git("show", BASE + ":" + path).decode()

def tree(source):
    return ast.parse(source, feature_version=(3, 9))

def shape(source):
    return ast.dump(tree(source), include_attributes=False)

def executable(source):
    lines = source.splitlines(keepends=True)
    return "".join(line for line in lines if not line.lstrip().startswith("#"))

moves = [
    ("run_branch.sh", "tasks/run_branch.sh"),
    ("run_focus_tasks.sh", "tasks/run_focus_tasks.sh"),
    ("run_reference_query_alignment.sh", "train/run_reference_query_alignment.sh"),
    ("run_dynamic_reference_query_alignment.sh", "train/run_dynamic_reference_query_alignment.sh"),
    ("run_head_stability_suite.sh", "analysis/run_head_stability_suite.sh"),
]
for name in ("e014_step800_eval1766_8gpu.sh", "e014_multi_v2_step200_eval1766_8gpu.sh", "e014_cover_min_cap5_step150_eval1766_8gpu.sh"):
    moves.append(("analysis/e014/" + name, "eval/e014/" + name))
for old, new in moves:
    old, new = "tools/run/" + old, "tools/run/" + new
    body = executable((ROOT / new).read_text())
    body = body.replace('/../_common.sh"', '/_common.sh"').replace("configs/tasks/", "configs/sft/")
    assert body == executable(original(old)), (old, new)
    wrapper = (ROOT / old).read_text()
    assert "exec bash" in wrapper and wrapper.rstrip().endswith('"$@"'), old
    suffix = re.search(r'exec bash "\$\(cd -- "\$\(dirname -- "\$\{BASH_SOURCE\[0\]\}"\)" && pwd\)(/[^"\n]+)" "\$@"', wrapper)
    assert suffix, old
    assert ((ROOT / old).parent / suffix[1].lstrip("/")).resolve() == (ROOT / new).resolve(), old
    assert (ROOT / old).stat().st_mode & 0o111 == (ROOT / new).stat().st_mode & 0o111

config_names = ["qwen3vl_8b_focus_branch", "qwen3vl_8b_focus_tasks", "qwen3vl_8b_grounding_tasks"]
for name in config_names:
    old = "configs/sft/" + name + ".py"
    new = "configs/tasks/" + name + ".py"
    previous = original(old)
    parents = [node.value.value for node in ast.walk(tree(previous))
               if isinstance(node, ast.keyword) and node.arg == "parent_config"]
    assert len(parents) == 1
    normalized = (ROOT / new).read_text().replace('parent_config="../sft/' + parents[0] + '"', 'parent_config="' + parents[0] + '"')
    assert shape(normalized) == shape(previous), name
    assert ((ROOT / new).parent / "../sft" / parents[0]).resolve() == (ROOT / old).parent / parents[0]
    aliases = [node for node in tree((ROOT / old).read_text()).body if isinstance(node, ast.Assign)]
    assert len(aliases) == 1 and aliases[0].targets[0].id == "config_alias"
    assert ((ROOT / old).parent / ast.literal_eval(aliases[0].value)).resolve() == (ROOT / new).resolve()

for name in ("e012_head_circuit_path_patching.sh", "e012_head_circuit_zero_attention.sh"):
    path = "tools/run/analysis/e012/" + name
    source = executable((ROOT / path).read_text())
    assert source.replace('/../../../.." && pwd)', '/../.." && pwd)') == executable(original(path))
    assert ((ROOT / path).parent / "../../../..").resolve() == ROOT.resolve()

source = (ROOT / "iploc_szy/branching.py").read_text()
added = '''    try:
        parent_path = _parent_path(composition_path, branch.get("parent_config"))
    except FileNotFoundError:
        # A moved recipe's defaults still resolve from its canonical source.
        # Preserve an explicit legacy CLI override that named a sibling of the
        # invocation file, but do not change any already-resolvable precedence.
        explicit_parent = any(o.split("=", 1)[0] == "branch.parent_config" for o in options)
        if composition_path == config_path or not explicit_parent:
            raise
        parent_path = _parent_path(config_path, branch.get("parent_config"))
'''
assert added in source
assert shape(source.replace(added, '    parent_path = _parent_path(composition_path, branch.get("parent_config"))\n')) == shape(original("iploc_szy/branching.py"))
package_files = git("ls-files", "iploc_szy").decode().splitlines()
for path in package_files:
    if path != "iploc_szy/branching.py":
        assert (ROOT / path).read_bytes() == git("show", BASE + ":" + path), path

python_files = sorted((ROOT / "configs").rglob("*.py")) + [ROOT / p for p in ("iploc_szy/branching.py", "tools/audit_entrypoints.py", "tests/test_config_migration.py", "tests/test_e009_distillation_suite.py")]
for path in python_files:
    tree(path.read_text())
shells = sorted((ROOT / "tools").rglob("*.sh"))
for path in shells:
    subprocess.run(["bash", "-n", str(path)], check=True, capture_output=True)

links = 0
for relative in ("configs/ENTRYPOINT_INDEX.md", "docs/LAUNCH_CATALOG.md", "tools/run/README.md", "configs/README.md"):
    page = ROOT / relative
    for target in re.findall(r"\]\(([^)]+)\)", page.read_text()):
        if re.match(r"[a-z]+://", target) or target.startswith("#"):
            continue
        target = target.split("#", 1)[0]
        resolved = (page.parent / target).resolve()
        assert resolved.is_relative_to(ROOT.resolve()) and resolved.exists(), (relative, target)
        links += 1
subprocess.run(["git", "-C", str(ROOT), "diff", BASE, "--check"], check=True)
subprocess.run(["git", "-C", str(ROOT), "diff", "--cached", "--check"], check=True)
result = dict(base_revision=BASE, canonical_shell_moves=len(moves), task_config_moves=len(config_names),
              package_files_unchanged=len(package_files)-1, python39_ast_files=len(python_files),
              bash_n_shells=len(shells), valid_local_markdown_links=links,
              root_fixes=2, note="static evidence only; no tests, imports of project code, models, builds or remote execution")
(OUT / "static_check_results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(result, ensure_ascii=False, indent=2))
