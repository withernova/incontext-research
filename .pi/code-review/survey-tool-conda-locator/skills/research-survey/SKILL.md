---
name: research-survey
description: Rigorous, human-in-the-loop research idea validation pipeline. Use when the user wants to validate/refine a research idea against a code repository + foundational papers, search and download real literature, decompose the idea into testable claims, run adversarial review gates, and produce a traceable, anti-hallucination synthesis. Triggers include "调研/validate idea/research survey/继续调研/novelty check/claim review/synthesis".
---

# Research Survey — Idea Validation Pipeline

A disciplined, file-backed pipeline for validating a research idea with an AI agent.
Design borrowed from awesome-vibe-research (Vincentwei1021 five-layer framework, VRE/vibe-science truth-workflow split, vibe-science R2 adversarial gate, mariklolik result hashing, HKUSTDial citation-integrity code of conduct, jiajingyyyyyy stage output-contracts).

**You = the agent executing this skill. Follow these rules exactly. Do not improvise around the anti-hallucination rules.**

## Conventions (项目约定)

### C1. 中文优先的模板（Chinese-first templates）

所有由本 skill 生成的 Markdown 模板与脚本输出（INTAKE / AGENTS / state.md / kernel/* / shell/** 以及 `materialize.py`、`ingest.py`、`bootstrap.py` 写出的内容）**默认使用中文**撰写标题、说明性文字与字段标签。

保留为英文/原文的项：
- 机器读取的字段键（`state:`、`iteration:`、`citekey:`、`status:`、`content_hash:` 等）保持英文，以保证脚本正则解析稳定。
- 引用键 `[[citekey]]`、状态枚举（`draft|supported|validated|contradicted|partial|inference_only`、`PASS|REJECT|NEEDS_MORE_EVIDENCE`）保持英文。
- 论文标题、作者、原文引用句保持原文（不翻译）。

当项目 AGENTS.md 明确要求英文输出时，再切换为英文；否则一律中文。

### C2. MinerU 抽取产物优先读取（prefer MinerU-extracted markdown）

若一篇论文存在 **MinerU 抽取出的文件夹**，**优先读取其中的 `.md` 而非直接对 PDF 做转换**，因为 MinerU 产物保留了**图像（images/）与详细公式（LaTeX/结构化）**，质量显著优于对原 PDF 的二次抽取。

典型 MinerU 产物布局（以本仓库为例）：
```
papers/<Title>_<year>/
└── hybrid_auto/
    ├── <Title>_<year>.md          # ← 首选阅读对象（含图片引用 + 公式）
    ├── <Title>_<year>_origin.pdf
    ├── <Title>_<year>_layout.pdf
    ├── <Title>_<year>_content_list.json / _v2.json
    ├── <Title>_<year>_middle.json
    ├── <Title>_<year>_model.json
    └── images/                    # md 中引用的图片
```

规则：
1. 在 BOOTSTRAP / GATHER 摄取一篇论文时，先在 PDF 所在目录的**同级**或**同名子目录**下查找 `<stem>.md` + `images/`（MinerU 标志）。若找到，把该 `.md` 路径与 `images/` 路径记入 `shell/03_evidence/papers/<citekey>.md` 笔记骨架的「来源」区，并据此做 grounded Q&A（引用 `[[citekey]] §<md 中的小节>`）。
2. `ingest.py` 在写笔记骨架时，会自动探测 PDF 同级/同名子目录里的 MinerU `.md`，并在骨架顶部记录 `mineru_md:` / `mineru_images:` 字段（见脚本实现）。
3. 当且仅当没有 MinerU 产物时，才回退到对原 PDF 的 `read`/pdf-converter 抽取。
4. 任何情况下，**content_hash 仍以原始 PDF 计算**（保证可验证溯源），MinerU `.md` 仅作为阅读辅助，不替代哈希校验。

### C3. 实验代码：本地开发，服务器验证和执行

进入代码实现或修复任务前，先读取当前 Experiment / Run 的 Workspace，不使用 INTAKE、聊天记忆或 Publish 快照代替执行绑定。绑定是工具自动记录的仓库定位信息，不是要求用户手填的前置审批。

- Workspace `code_development.mode=local-git` 时，真实代码仓库在本机 `local_code_repo`。本机指 Survey Tool 服务所在机器。新绑定默认 `storage=project`，代码放在 `<研究项目>/code-repositories/<Workspace-ID>/<仓库名>/`，与文档分开且不进入 Publish 快照。旧外部路径不自动搬动。仓库 URL、分支和远程执行目录由 Workspace 指定；准备成功后读取该代码仓库的 AGENTS.md。
- Workspace 没有 `code_development` 或为 `mode=auto` 时，默认本地 Git 自动绑定。先执行下面的 `code prepare`：工具只读发现 `remote_repo` 的 origin 与当前分支，自动登记项目内路径，保留 SSH/HTTPS 传输方式，再准备代码。不得要求用户先手动登记 URL、分支或路径，也不得猜 main。使用返回的 `local_repo` 编辑，已有 local-git 绑定不覆盖。
- **每次本地修改任务，在第一处编辑前自动执行** `python3 <tool>/surveyctl.py --project <project> code prepare --workspace-id <W>`。它检查本机干净、活动 Run、服务器同用户进程、origin、分支和 Git 状态，先自动提交远端代码改动并 push 到绑定分支，再将本机 fast-forward 到同一已发布 commit。项目内目标目录不存在时可首次克隆绑定分支；已有目录、文件或软链接冲突则停止，禁止覆盖。
- 认证失败、外部目录缺失、项目内克隆失败、本机脏仓库、远端含数据/输出/疑似凭据、分叉或运行中任务：停止并报告 blocker。不得 stash、reset、clean、自动 checkout、更换 origin、强推，或退回 SSH patch。
- 只在绑定本机仓库内做允许的代码修改。默认不运行测试、构建、smoke、import/启动检查，也不新增测试 Run；只有用户明确要求时执行。仓库默认测试约定不算本轮授权，不得委派其他 Agent 绕过。复用实际模块，不复制实验包。对当前本地 diff 调用 code_change_review；未测试可省略 test_evidence，不为缺少测试阻断交付，并如实注明‘未测试’。审阅后用精确任务文件 checkpoint commit，保留用户改动，并立即自动执行 `python3 <tool>/surveyctl.py --project <project> code publish --workspace-id <W> --commit <完整40位SHA>`，不另行询问 push。此默认流程仅适用于绑定私人代码仓库和分支，不授权推送 Survey Tool 或其他仓库。
- push、指定 SHA 部署、服务器验证、正式 Run 是不同动作。自动发布代码不授权部署或训练；部署和 Run 仍遵守用户授权与既有科研门禁。
- 获得指定 commit 部署授权后，执行 `code deploy --workspace-id <W> --commit <完整40位SHA> --confirmation 'DEPLOY CODE <W> <完整40位SHA>'`。commit 必须已发布到绑定分支且可 fast-forward；不部署 latest。部署不会启动实验。
- 只有用户明确要求时执行服务器 Linux/CUDA 测试；已授权正式 Run 的必要 preflight 和执行命令仍按原门禁处理，不自行增加测试。将真实已部署的完整 SHA 写入 Run `git_commit`。报告 authored / deployed commit；只记录实际执行的命令与退出码，未测试标注‘未验证’，不把审阅通过当作运行验证。
- Workspace 显式选择 `mode=remote` 时，保留已有远程开发流程。用户明确要求本地整理/编辑时，直接执行 `code prepare` 自动转换并登记，不再要求手动切换表单。绑定变化不能继承旧 Run 的执行授权。只读调研阶段不运行准备或自动绑定命令。

操作说明见 Survey Tool 的 `docs/LOCAL_CODE_WORKFLOW.md`。上述流程不改变 Claim 人工 verdict，也不授予 Run 执行权限。

## 0. The Five Layers (vocabulary for where things fail)

Every project must satisfy all five. Most failures happen in layers 2–4.

1. **Architecture** — this skill + project AGENTS.md + kernel/shell split + state machine.
2. **Context Continuity** — `kernel/` (append-only truth) vs `shell/` (workflow/drafts); `state.md` for resume.
3. **Approval Gates** — claim promotion needs TWO gates: R2 adversarial auto-review + human approval.
4. **Trust** — citation-integrity hard rules + content hashing + no-silent-zero + search log.
5. **Observability** — append-only `kernel/review_log.md` + bounded loop (budget/blocker/escalation) + per-iteration digest.

## 1. Directory Layout (per project)

```
<project>/
  AGENTS.md                 #钾入 this skill + project-specific context
  state.md                  # state machine state + iteration count + next actions
  kernel/                   # TRUTH layer: append-only, gate-controlled
    claims.md               # claim registry (id, text, status, confidence, sources, verdicts)
    citations.md            # citekey -> {title, authors, year, url, doi, content_hash, fetched_at, local_pdf}
    review_log.md           # append-only: every R2 adversarial + human verdict (timestamped)
  shell/                    # WORKFLOW layer: drafts, overwritable
    00_idea/
      idea.md               # original idea + hypotheses
      context.md            # repo path, seed papers, domain, target venue
    01_repo/
      repo_map.md           # code repo analysis + paper<->module cross-links
    02_search/
      search_log.md         # every search: query, source, timestamp, hit citekeys
    03_evidence/
      papers/               # <citekey>.pdf + <citekey>.md (notes)
    04_review/
      iteration_N.md        # review queue + human annotations per round
    05_synthesis/
      report.md             # ONLY references kernel claims with status=validated
      gap_analysis.md
      risk_register.md
  autoresearch.ideas.md     # side-effect ideas (don't lose them)
```

**Hard rule:** `shell/05_synthesis/*` may ONLY cite claims whose `status=validated` in `kernel/claims.md`. Anything else must be marked `[PENDING-HUMAN]` or `[UNVERIFIED]` inline. The `promote_claim.py` script enforces the gate mechanically.

## 2. State Machine

```
INIT_PROJECT (bootstrap.py)
   -> AWAIT_INTAKE  (human fills INTAKE.md, says "intake done")
   -> MATERIALIZE (materialize.py parses INTAKE -> context/idea/AGENTS, state=BOOTSTRAP)
   -> BOOTSTRAP (ingest seed papers: copy + hash + citations.md + note skeletons)
   -> REPO_INGEST -> DECOMPOSE -> NOVELTY_CHECK -> GATHER <-> R2_REVIEW -> AWAIT_REVIEW -> REVISE -+
                ^                                                                                       |
                +-------------------------------------- (loop until claims stable) ----------------------+
                                                                                                          v
                                                                                                    SYNTHESIS -> GO_NOGO -> DONE
```

`state.md` holds: `state`, `iteration`, `budget {max_iterations, max_wall_seconds}`, `blockers[]`, `next_actions[]`. On "继续调研/continue/intake done", read `state.md` and resume from the recorded state.

The intake step is mandatory: do NOT skip to REPO_INGEST with an unfilled INTAKE.md. `materialize.py` refuses if required fields (`repo_path, project_slug, seed_papers, idea, domain, polite_email`) still contain `<...>` placeholders.

## 3. Stage Output Contracts (each stage has a fixed output + failure modes)

Full contracts in `references/stage_contracts.md`. Summary:

- **INIT_PROJECT** — run `bootstrap.py --project <dir>`: create skeleton from `templates/`, drop `INTAKE.md` form, set state=AWAIT_INTAKE. Then STOP and ask the human to fill `INTAKE.md` (repo path, seed papers, idea, domain, venue, polite email, constraints). Failure: project dir not empty -> refuse; ask for a fresh path.
- **AWAIT_INTAKE** — wait for the human to fill `INTAKE.md` and say "intake done / 填好了". Do nothing else.
- **MATERIALIZE** — run `materialize.py --project <dir>`: parse `INTAKE.md`, validate required fields (refuse on `<...>` placeholders), write `shell/00_idea/context.md`, `shell/00_idea/idea.md`, `AGENTS.md`, set state=BOOTSTRAP. Then proceed to seed-paper ingestion.
- **BOOTSTRAP** — ingest seed papers (copy PDFs to `shell/03_evidence/papers/`, hash, write `kernel/citations.md`, create note skeletons). Output: populated kernel/citations + skeleton files. Failure: seed paper not fetchable -> mark `[UNVERIFIED-SEED]`, do NOT fabricate metadata.
- **REPO_INGEST** — analyze the code repo -> `shell/01_repo/repo_map.md` (architecture, modules, entry points, datasets, losses, implemented vs stub, TODO/FIXME, gaps). Cross-link seed papers <-> repo modules. Output: repo_map.md + a "grounding anchor" section. Failure: repo unreadable -> mark `degraded`, say so (no silent zero).
- **DECOMPOSE** — split idea into atomic falsifiable claims, each with id (C01..), text, status=`draft`. Output: `kernel/claims.md` populated. Failure: claim not falsifiable -> reword or split.
- **NOVELTY_CHECK** — for each claim, actively search "has this been done?" using ≥3 query classes (method-name / task-name / dataset-name). Output per claim: `verdict: novel|partial|already_done` + `prior_work[]` + `pivot_suggestion`. Claims already_done -> status=`contradicted_by_prior`. Failure: query too narrow -> missed already_done. Fix: cross 3 query classes, MUST list ≥1 "most similar prior work".
- **GATHER** — for each non-contradicted claim, search (Zotero workspace + arXiv/OpenAlex/S2 APIs) + fetch PDFs + ingest + extract evidence into paper notes + update claim status (`supported`/`contradicted`/`partial`/`inference_only`). Bounded: max_iterations, max_wall_seconds; on N failed searches -> blocker -> escalate to AWAIT_REVIEW. Output: updated claims + paper notes + search_log entries. Failure: only supportive evidence ("只报喜") -> MUST also record contradicting_evidence field.
- **R2_REVIEW** — adversarial pass on every `supported` claim: actively hunt counterexamples, find weakest link, find ignored confounds. Output: R2 verdict `PASS|REJECT|NEEDS_MORE_EVIDENCE` + reasoning, appended to `review_log.md`. REJECT -> claim back to GATHER or dropped; NEEDS_MORE -> back to GATHER. Failure: rubber-stamp -> re-run with explicit "try to kill this claim" stance.
- **AWAIT_REVIEW** — present a structured review queue to the human (see §5). Human approves/rejects/asks. Output: `iteration_N.md` with human annotations; claims get `human_verdict`. Failure: dumping a wall of text -> always use the review queue format.
- **REVISE** — apply human feedback: split/merge/drop claims, revise idea.md. Loop back to GATHER. Output: updated claims + idea.md.
- **SYNTHESIS** — write report/gap_analysis/risk_register citing ONLY `validated` claims. Output: `shell/05_synthesis/*`. Failure: citing a non-validated claim -> the promote_claim gate / your own discipline must block it.
- **GO_NOGO** — final verdict + remaining-evidence checklist. Output: go/no-go + next steps (possibly hand off to experiment_* / autoresearch).

## 4. Anti-Hallucination Hard Rules (non-negotiable)

1. **Citation integrity (HKUSTDail code of conduct).** NEVER generate, fabricate, or guess a reference. Every citation must be a source you actually fetched. If you cannot fetch/verify -> mark `[UNVERIFIED-CITATION]` and the claim CANNOT be promoted. Real, retrievable sources only.
2. **Content hashing (mariklolik).** Every fetched PDF/web content gets SHA-256 stored in `kernel/citations.md`. The human can re-hash anytime to prove provenance. Run `ingest.py` (it hashes automatically) or `scripts/kernel/check_hash.py`.
3. **No silent zero (VRE).** If Zotero workspace is unavailable / an API fails / a search returns nothing -> say so explicitly (`degraded` / `no hits`). Never imply "searched and found nothing" when you didn't actually search.
4. **Search log mandatory.** Every search (web or Zotero) -> append to `shell/02_search/search_log.md` with query, source, timestamp, hit citekeys. Prevents fake searches and duplicate searches.
5. **Grounded corpus Q&A (PaperQA2 substitute).** When answering the human's questions about papers, answer ONLY from PDFs you have ingested into `shell/03_evidence/papers/` — **优先读取 MinerU 抽取的 `.md`（含图像与公式），见 C2**；否则对 PDF 做 `read`/pdf-converter 抽取。 Cite `[[citekey]] §section`. If the ingested PDFs don't cover it -> say "not in ingested corpus" and go fetch. Do NOT answer from parametric memory about a paper's content.
6. **Two-gate promotion.** `supported` -> `validated` requires: (a) R2 verdict = PASS in review_log, (b) human_verdict = approved, (c) ≥1 source citekey with valid content_hash in citations.md. Enforced by `promote_claim.py`.

## 5. Human-in-the-Loop Review Queue Format

At AWAIT_REVIEW, produce this exact structure (not free text):

```markdown
## Iteration N Review Queue  (date)
### Newly supported
- [Cxx] "<claim text>"
  sources: [[citekey]] §sec, [[citekey]] Table x
  confidence: med  <- contradicting: [[citekey]] Fig y
  R2 verdict: PASS / NEEDS_MORE
  ? Please confirm: <specific question>
### Contradicted
- [Cxx] "<claim>" contradicted by [[citekey]] §sec. Propose: drop / rewrite.
### No evidence (your call)
- [Cxx] "<claim>" — N searches, no hits. Likely novel gap OR search-term problem.
### Questions for you
1. ...
```

Human responds per-item: approve / reject / ask. You log to `iteration_N.md` and update `human_verdict`.

## 6. Tools & Scripts

Scripts live in this skill's `scripts/` dir. Invoke as (replace `{SKILL}` with this skill's absolute directory, which is the parent of this SKILL.md):

```bash
# Project init + intake (run these FIRST)
python "{SKILL}/scripts/bootstrap.py"    --project "<new-project-dir>" [--name "Pretty Name"]   # creates skeleton + INTAKE.md
# (human fills <project>/INTAKE.md, then says "intake done")
python "{SKILL}/scripts/materialize.py"  --project "<proj>"                                # parse INTAKE -> context/idea/AGENTS, state=BOOTSTRAP

# Paper acquisition (no API key needed; polite email from context.md)
python "{SKILL}/scripts/papers/search_arxiv.py"   --project "<proj>" "query"
python "{SKILL}/scripts/papers/search_openalex.py" --project "<proj>" "query"
python "{SKILL}/scripts/papers/search_s2.py"       --project "<proj>" "query"
python "{SKILL}/scripts/papers/fetch_pdf.py"       --project "<proj>" --id <arxiv-id|doi>
python "{SKILL}/scripts/papers/enrich_crossref.py" --project "<proj>" --doi <doi>
python "{SKILL}/scripts/papers/ingest.py"          --project "<proj>" --pdf <path> --citekey <key> [--url ..] [--doi ..]   # 会自动探测同名 MinerU .md，记入笔记骨架（见 C2）

# Repo ingestion
python "{SKILL}/scripts/repo/repo_map.py" --project "<proj>" --repo <repo-path>

# Kernel gates
python "{SKILL}/scripts/kernel/new_claim.py"     --project "<proj>" --text "..." [--sources ..]
python "{SKILL}/scripts/kernel/r2_review.py"     --project "<proj>" --claim Cxx
python "{SKILL}/scripts/kernel/promote_claim.py" --project "<proj>" --claim Cxx
python "{SKILL}/scripts/kernel/check_hash.py"    --project "<proj>" [--citekey ..]
```

All paper scripts append to `shell/02_search/search_log.md` and print JSON to stdout. `ingest.py` writes to `kernel/citations.md` and creates `shell/03_evidence/papers/<citekey>.md` note skeleton.

**Zotero local library:** use pi's workspace tools (`workspace_search` on the `zotero` workspace, `workspace_read`, `workspace_copy`). Read-only — never write to Zotero.

**Reading PDFs:** use the `pdf-converter` skill or `read` tool to extract text from ingested PDFs into the per-paper `.md` notes. This is the grounded-Q&A substitute for PaperQA2.

## 7. Bounded Loop (no runaway)

GATHER runs with `budget` from `state.md` (default `max_iterations=3, max_wall_seconds=600`). On:
- a claim failing N searches (default N=3) -> add to `blockers`, stop, escalate to AWAIT_REVIEW with "no evidence" item.
- API failure -> mark `degraded` in search_log, continue with other sources, report at AWAIT_REVIEW.
- budget exhausted -> stop at AWAIT_REVIEW regardless.

## 8. AFK Background Mode (optional)

If the human says they'll be away: run extra GATHER rounds within budget, filling `kernel` + paper notes but DO NOT promote claims and DO NOT write synthesis. On return, present one consolidated review queue. Use `watchdog_control` only if a remote experiment is involved; for pure literature work, just run bounded GATHER rounds and stop.

## 9. Per-Project AGENTS.md

Every project's `AGENTS.md` must:
- Reference this skill ("follow the `research-survey` skill").
- Pin: repo path, seed paper list (arXiv id / DOI / local path), the idea, domain, target venue, polite email for APIs.
- Note any project-specific constraints.

Template: `templates/AGENTS.md`.

## 10. Resume Protocol

On "继续调研 / continue / resume": read `<project>/state.md`, jump to the recorded `state`, execute that stage's contract, update `state.md`. Never silently skip stages. If `state == AWAIT_INTAKE`, remind the human to fill `INTAKE.md`.

## 11. What NOT to do

- Do not write synthesis claims that aren't `validated`.
- Do not cite a paper you haven't fetched (citation-integrity rule).
- Do not answer paper-content questions from memory — read the ingested PDF.
- Do not promote a claim without R2 PASS + human approval.
- Do not pretend a search happened. Log it or say you didn't do it.
- Do not delete from `kernel/review_log.md` (append-only).

See `references/stage_contracts.md` for full per-stage output contracts and failure modes, and `references/anti_hallucination.md` for the extended rules.