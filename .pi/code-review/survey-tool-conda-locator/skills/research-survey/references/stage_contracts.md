# Stage Output Contracts & Failure Modes

Each stage produces a fixed artifact and documents how it breaks. Loaded on demand.

## INIT_PROJECT
**Output:** project dir with skeleton (kernel/, shell/, state.md=AWAIT_INTAKE, AGENTS.md placeholder, INTAKE.md form). Created by `bootstrap.py`.
**Failure modes:**
- Project dir exists and is non-empty -> refuse, ask for a fresh path (don't clobber).
- Template missing -> reinstall skill.
**Handoff:** state -> AWAIT_INTAKE; STOP, ask human to fill INTAKE.md.

## AWAIT_INTAKE
**Output:** none (blocked on human). The human fills `INTAKE.md` and says "intake done".
**Failure modes:**
- Human says "done" but INTAKE.md still has `<...>` -> materialize.py will refuse; tell them which fields.
**Handoff:** on "intake done" -> MATERIALIZE.

## MATERIALIZE
**Output:** `shell/00_idea/context.md` + `shell/00_idea/idea.md` + `AGENTS.md` populated from INTAKE.md; `state.md` -> BOOTSTRAP. Validated required fields: repo_path, project_slug, seed_papers, idea, domain, polite_email.
**Failure modes:**
- Placeholder remains -> refuse (or `--force` with gaps flagged in AGENTS.md + state blockers).
- polite_email is example.com -> warn (Unpaywall will 422); still proceed but flag.
**Handoff:** state -> BOOTSTRAP.

## BOOTSTRAP
**Output:** project skeleton from `templates/`; seed papers copied to `shell/03_evidence/papers/`, hashed, written to `kernel/citations.md`; per-paper `.md` note skeletons; `state.md` = BOOTSTRAP->REPO_INGEST.
**Failure modes:**
- Seed paper not fetchable (dead link, paywalled, no DOI) -> mark `[UNVERIFIED-SEED]` in citations.md with whatever metadata you have; do NOT invent the rest. Add to blockers.
- Duplicate seed (same DOI) -> dedupe by DOI/content_hash.
**Handoff:** `state.md` -> REPO_INGEST.

## REPO_INGEST
**Output:** `shell/01_repo/repo_map.md` containing:
- Architecture overview (entry points, module map, data flow)
- Datasets / dataloaders, losses, metrics, configs
- Implemented vs stubbed vs TODO/FIXME (grep the repo)
- Gaps & assumptions
- **Paper<->module cross-link table**: which seed paper grounds which module/loss/trick
- "Grounding anchor": 3-5 facts about the repo that constrain the idea
**Failure modes:**
- Repo unreadable / wrong path -> mark `degraded` in state.md, say so, ask human.
- Idea contradicts repo (e.g. idea assumes a module that doesn't exist) -> flag explicitly, this is the highest-value finding of this stage.
**Handoff:** `state.md` -> DECOMPOSE.

## DECOMPOSE
**Output:** `kernel/claims.md` with claims C01..Cnn. Each claim:
- atomic, falsifiable, single sentence
- status=`draft`, confidence unset, sources=[], contradicting_evidence=[], r2_verdict=pending, human_verdict=pending
**Failure modes:**
- Claim not falsifiable ("X is good") -> reword to a testable form or split.
- Claim too broad -> split into 2-3.
- Claim is an opinion -> demote to `inference_only` immediately, no promotion path.
**Handoff:** `state.md` -> NOVELTY_CHECK.

## NOVELTY_CHECK
**Output:** for each claim, append to its claims.md entry:
- `prior_work: [{citekey, what_they_did, overlap}]`
- `verdict: novel | partially_overlapping | already_done`
- `pivot_suggestion` (if not novel)
Update status: `already_done` -> `contradicted_by_prior`; `partially_overlapping` -> keep but note overlap.
**Search policy:** ≥3 query classes per claim: method-name, task-name, dataset-name. Use arXiv + OpenAlex + S2.
**Failure modes:**
- Query too narrow -> missed already_done. Fix: 3 query classes, MUST list ≥1 "most similar prior work" even for novel claims.
- Conflating "similar task" with "same method" -> be precise about what overlaps.
**Handoff:** `state.md` -> GATHER (only for non-contradicted claims).

## GATHER
**Output:** per non-contradicted claim:
- searches logged in `shell/02_search/search_log.md`
- relevant PDFs fetched + ingested (hash in citations.md) + per-paper notes
- evidence extracted into the claim's `sources` (citekey + section/table)
- status updated: `supported` (≥1 supporting source) / `contradicted` / `partial` / `inference_only`
- `contradicting_evidence` field populated (MANDATORY even for supported claims)
**Bounded:** max_iterations, max_wall_seconds from state.md. N=3 failed searches -> blocker -> escalate.
**Failure modes:**
- 只报喜 (only supportive) -> MUST populate contradicting_evidence; if none found, state "no contradicting evidence found (searched: ...)".
- Citation without fetch -> forbidden; must fetch first.
- Ingesting a paper but not reading it -> must extract at least the relevant passage into the per-paper note before citing.
**Handoff:** `state.md` -> R2_REVIEW (for supported claims).

## R2_REVIEW
**Output:** for each `supported` claim, append to `kernel/review_log.md`:
```
## <timestamp> | <claim_id> | R2 adversarial
- stance: try to KILL this claim
- weakest_link: ...
- counterexample_search: [queries] -> [results / no hits]
- confounds_ignored: ...
- verdict: PASS | REJECT | NEEDS_MORE_EVIDENCE
- reasoning: ...
- next: (if REJECT/NEEDS_MORE) what to do
```
Set claim's `r2_verdict` field. REJECT -> status back to draft/contradicted; NEEDS_MORE -> back to GATHER.
**Failure modes:**
- Rubber-stamp PASS -> re-run with explicit adversarial stance; if you can't articulate a weakest_link, you didn't review.
- Skipping contradicting evidence already found -> re-incorporate.
**Handoff:** `state.md` -> AWAIT_REVIEW (claims with R2 PASS).

## AWAIT_REVIEW
**Output:** `shell/04_review/iteration_N.md` with the §5 review queue format. STOP and wait for human.
**Failure modes:**
- Wall of text -> must use the structured queue.
- Asking too many questions -> max 5 questions per iteration, prioritize.
**Handoff:** on human response -> REVISE or next stage.

## REVISE
**Output:** updated `kernel/claims.md` (split/merge/drop/reword), updated `shell/00_idea/idea.md` if idea changed, `state.md` -> GATHER.
**Failure modes:**
- Silently changing claims without logging -> log changes in review_log.md.
**Handoff:** loop.

## SYNTHESIS
**Output:** `shell/05_synthesis/report.md` (+ gap_analysis.md, risk_register.md). Every factual sentence cites a `validated` claim id. Non-validated -> inline `[PENDING-HUMAN]` or `[UNVERIFIED]`.
**Failure modes:**
- Citing non-validated claim -> forbidden; the promote_claim gate blocks the claim, and you must not bypass it by paraphrasing.
- Missing gap analysis -> required.
**Handoff:** `state.md` -> GO_NOGO.

## GO_NOGO
**Output:** verdict (go / go-with-caveats / no-go / pivot), rationale, remaining-evidence checklist, and (if go) handoff plan to experiment execution (experiment_* / autoresearch) or paper writing.
**Handoff:** `state.md` -> DONE.