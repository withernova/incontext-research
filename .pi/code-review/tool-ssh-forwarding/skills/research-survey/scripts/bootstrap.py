#!/usr/bin/env python
"""Initialize a research-survey project: create the skeleton from templates/ and drop
an INTAKE.md form for the user to fill. Sets state.md to AWAIT_INTAKE.

Usage:
  python bootstrap.py --project <new-project-dir> [--name "Pretty Name"]

After this, the human fills <project>/INTAKE.md and says "intake done";
the agent then runs materialize.py to populate context.md/idea.md/AGENTS.md and advance.
"""
import sys as _sys, pathlib as _pl, shutil, re
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
import argparse
from _common import now_iso

TPL = _pl.Path(__file__).resolve().parent.parent / "templates"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, help="path of the new project dir (created if missing)")
    ap.add_argument("--name", default="", help="human-readable project name (optional)")
    args = ap.parse_args()
    proj = _pl.Path(args.project).resolve()
    if proj.exists() and any(proj.iterdir()):
        sys.exit(f"[err] project dir not empty: {proj} (pick a fresh path or clear it first)")
    proj.mkdir(parents=True, exist_ok=True)

    # copy skeleton
    for sub in ["kernel", "shell"]:
        src = TPL / sub
        if src.exists():
            shutil.copytree(src, proj / sub, dirs_exist_ok=True)
    shutil.copy(TPL / "state.md", proj / "state.md")
    shutil.copy(TPL / "INTAKE.md", proj / "INTAKE.md")

    # make sure papers dir + repo dir exist
    (proj / "shell" / "03_evidence" / "papers").mkdir(parents=True, exist_ok=True)
    (proj / "shell" / "01_repo").mkdir(parents=True, exist_ok=True)

    # seed a minimal AGENTS.md placeholder (materialize.py will overwrite with real content)
    ag = proj / "AGENTS.md"
    ag.write_text(f"""# AGENTS.md — {args.name or proj.name}

> 遵循 **research-survey** skill（~/.pi/agent/skills/research-survey）。
> 项目当前为 AWAIT_INTAKE：请填写 INTAKE.md，然后告诉 agent “intake done / 填好了”。
> 项目约定：中文模板（C1）、MinerU 产物优先读取（C2）。
""", encoding="utf-8")

    # set state to AWAIT_INTAKE
    st = proj / "state.md"
    st.write_text(f"""# state.md

state: AWAIT_INTAKE
iteration: 0
budget:
  max_iterations: 3
  max_wall_seconds: 600
blockers: []
next_actions:
  - 用户填写 INTAKE.md
  - agent 运行 materialize.py --project {proj}
  - 随后 REPO_INGEST -> DECOMPOSE -> ...
last_updated: {now_iso()}

## 阶段历史（append-only）
- {now_iso()} | AWAIT_INTAKE | 创建项目骨架 + INTAKE.md
""", encoding="utf-8")

    print(f"""[ok] 项目已初始化：{proj}
[next] 填写 {proj / 'INTAKE.md'}（所有 <...> 必须替换）
[next] 然后告诉 agent：“intake done”
[then] agent 运行：materialize.py --project {proj}""")

if __name__ == "__main__":
    main()