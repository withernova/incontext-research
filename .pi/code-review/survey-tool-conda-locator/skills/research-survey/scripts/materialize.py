#!/usr/bin/env python
"""Read a filled INTAKE.md, validate required fields, then write/overwrite:
  - shell/00_idea/context.md
  - shell/00_idea/idea.md
  - AGENTS.md
and set state.md to BOOTSTRAP (ready for REPO_INGEST).

Refuses (exit 1) if any required field still contains a `<...>` placeholder.

Usage:  python materialize.py --project <dir>
"""
import sys as _sys, pathlib as _pl, re
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
import argparse
from _common import now_iso

REQUIRED = ["repo_path", "project_slug", "seed_papers", "idea", "domain", "polite_email"]
LIST_FIELDS = {"seed_papers", "constraints"}

def parse_intake(text):
    """Parse the simple key:value + '- ' bullet-continuation format."""
    data = {}
    cur = None
    for ln in text.splitlines():
        s = ln.rstrip()
        m = re.match(r"^([a-z_]+):\s*(.*)$", s)
        if m and m.group(1) in LIST_FIELDS:
            cur = m.group(1)
            data[cur] = []
            rest = m.group(2).strip()
            if rest and rest.startswith("- "):
                data[cur].append(rest[2:].strip())
            elif rest and rest != "":
                data[cur].append(rest)
            continue
        if m:
            cur = m.group(1)
            data[cur] = m.group(2).strip()
            continue
        if cur in LIST_FIELDS and s.lstrip().startswith("- "):
            data[cur].append(s.lstrip()[2:].strip())
        elif cur in LIST_FIELDS and s.strip() == "":
            # blank line ends the list
            cur = None
        # ignore other lines (## Notes, comments)
    return data

def has_placeholder(v):
    if isinstance(v, list):
        return any("<" in x and ">" in x for x in v) or len(v) == 0
    return ("<" in str(v) and ">" in str(v)) or str(v).strip() == ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--force", action="store_true", help="materialize even with missing fields (flags them)")
    args = ap.parse_args()
    proj = _pl.Path(args.project).resolve()
    intake = proj / "INTAKE.md"
    if not intake.exists():
        _sys.exit(f"[err] no INTAKE.md at {intake}")
    data = parse_intake(intake.read_text(encoding="utf-8"))

    missing = [k for k in REQUIRED if has_placeholder(data.get(k))]
    if missing and not args.force:
        _sys.exit(f"[err] INTAKE.md still has placeholders/empty for: {missing}\n    fill them, then re-run. Or pass --force to proceed with gaps (they will be flagged).")

    slug = data.get("project_slug") or proj.name
    name = data.get("project_name") or slug
    repo = data.get("repo_path", "")
    seeds = data.get("seed_papers", [])
    idea = data.get("idea", "")
    domain = data.get("domain", "")
    venue = data.get("target_venue", "")
    email = data.get("polite_email", "")
    constraints = data.get("constraints", []) or ["none"]

    # context.md
    (proj / "shell" / "00_idea").mkdir(parents=True, exist_ok=True)
    ctx = proj / "shell" / "00_idea" / "context.md"
    seeds_block = "\n".join(f"- {s}" for s in seeds) or "- <none>"
    cons_block = "\n".join(f"- {c}" for c in constraints)
    ctx.write_text(f"""# Context（上下文）

## 仓库（Repo）
- path: {repo}
- project: {name}

## 种子论文（Seed papers）
{seeds_block}

## 领域 / 会议
- domain: {domain}
- target venue: {venue}

## API 联系邮箱
polite_email: {email}

## 约束（Constraints）
{cons_block}
""", encoding="utf-8")

    # idea.md
    idea_md = proj / "shell" / "00_idea" / "idea.md"
    idea_md.write_text(f"""# 想法（Idea） — {name}

> 活文档。随声明被支持/反驳而迭代。保持具体：写“机制”，而非“目标”。

## Pitch（来自 intake）
{idea}

## 假设 / 机制
- （将在 DECOMPOSE 阶段拆解为原子声明）

## 什么会证伪它
- 

## 假设清单（待对照代码库 + 文献核查）
- 

## 待解决问题
- 
""", encoding="utf-8")

    # AGENTS.md
    ag = proj / "AGENTS.md"
    ag.write_text(f"""# AGENTS.md — {name}

> 遵循 **research-survey** skill（全局：~/.pi/agent/skills/research-survey）。
> 行动前先阅读其 SKILL.md，遵守反幻觉硬规则与项目约定（中文模板 C1、MinerU 优先 C2）。

## 项目输入（从 INTAKE.md 物化而来）
- **代码仓库路径：** {repo}
- **种子论文：**
{chr(10).join('  - '+s for s in seeds) if seeds else '  - <none>'}
- **想法：** {idea}
- **领域：** {domain}
- **目标会议：** {venue}
- **联系邮箱：** {email}

## 约束
{chr(10).join('- '+c for c in constraints)}

## 工作流
- 始终从 state.md 恢复进度。
- 声明存于 kernel/claims.md；只有 validated 的声明才能进入综合。
- 引用格式 [[citekey]] §小节。绝不允许引用未实际抓取过的论文。
- 论文内容问答：优先读取同名目录下 MinerU 抽取的 .md（含图像与公式）；否则对 PDF 做 read/pdf-converter 抽取。
- 使用 ~/.pi/agent/skills/research-survey/scripts/ 下的脚本。

## Intake 缺口（如有）
{chr(10).join('- '+m for m in missing) if missing else '- none'}
""", encoding="utf-8")

    # state.md -> BOOTSTRAP
    st = proj / "state.md"
    st.write_text(f"""# state.md

state: BOOTSTRAP
iteration: 0
budget:
  max_iterations: 3
  max_wall_seconds: 600
blockers: {missing if missing else '[]'}
next_actions:
  - 摄取种子论文（scripts/papers/ingest.py；自动探测 MinerU .md，见 C2）
  - 运行 repo_map.py --repo {repo}
  - DECOMPOSE：把想法拆解为原子声明
last_updated: {now_iso()}

## 阶段历史（append-only）
- {now_iso()} | AWAIT_INTAKE | 创建项目骨架
- {now_iso()} | MATERIALIZE | INTAKE 解析 -> context/idea/AGENTS 已写入{" | gaps: "+str(missing) if missing else ""}
""", encoding="utf-8")

    print(f"""[ok] 已从 INTAKE.md 物化 {name}
- context:    {ctx}
- idea:       {idea_md}
- AGENTS.md:  {ag}
- state:      BOOTSTRAP{' (缺口: '+str(missing)+')' if missing else ''}
[next] 摄取种子论文，随后 REPO_INGEST ({repo})""")

if __name__ == "__main__":
    main()