# Anti-Hallucination Rules (extended)

## 1. Citation Integrity (primary defense)
Source: HKUSTDial/Supervisor-Skills Code of Conduct.
- NEVER generate, fabricate, or guess a reference entry.
- Every cited paper must be a real, retrievable source that YOU fetched during this project (or a seed paper the human provided).
- If you only have a title you saw mentioned but cannot fetch/verify -> mark `[UNVERIFIED-CITATION]`. Such a citation CANNOT support a claim's promotion.
- Reference fields (authors, year, venue, DOI) must come from the fetched metadata (CrossRef/OpenAlex/arXiv), not from memory.
- If the human asks "does paper X say Y?", and X is not ingested -> fetch X first, then answer from the PDF. Never answer from parametric memory of a paper.

## 2. Content Hashing (provenance proof)
Source: mariklolik/vibe SHA-256 result signing.
- `ingest.py` computes SHA-256 of every fetched PDF and stores it in `kernel/citations.md` (`content_hash: sha256:...`).
- `check_hash.py` recomputes and compares. Mismatch -> provenance broken, flag to human.
- The human can run `check_hash.py --citekey <key>` anytime to verify you actually retrieved that file and haven't swapped it.

## 3. No Silent Zero
Source: VRE safety model.
- Zotero workspace unavailable -> state `degraded: zotero`, continue with APIs, report at review.
- API call fails -> log `FAIL` in search_log with error, do not pretend "0 hits".
- A claim with no evidence after N searches -> `blocker`, escalate. Do NOT mark it `supported` to look productive.

## 4. Search Log (auditability)
- Every search appends: timestamp, source (arxiv|openalex|s2|zotero|web), query, hit count, hit citekeys.
- Purpose: prove searches happened, prevent duplicates, let the human audit breadth.
- Never retroactively edit a search_log entry (append-only).

## 5. Grounded Corpus Q&A (PaperQA2 substitute)
- The local PDF corpus lives in `shell/03_evidence/papers/`.
- When answering about paper content: read the ingested PDF (pdf-converter or read tool), extract the relevant passage into the per-paper `.md` note, and cite `[[citekey]] §section`.
- If the corpus doesn't cover the question: say "not in ingested corpus", then go fetch. Do not answer from memory.
- This is the mechanism that keeps synthesis grounded in real text, not in the model's prior.

## 6. Two-Gate Promotion
- Gate A (R2 adversarial): `r2_review.py` produces a verdict; only PASS allows promotion candidacy.
- Gate B (human): `human_verdict=approved` required.
- Mechanical check: `promote_claim.py` verifies (a) r2_verdict=PASS, (b) human_verdict=approved, (c) ≥1 source citekey exists in citations.md with a content_hash. All three -> status=validated. Else refuse with reason.
- `validated` is the only status that may appear in synthesis as established fact.

## 7. Claim Status Lifecycle
```
draft -> supported -> (R2 PASS + human approved) -> validated
draft -> contradicted / contradicted_by_prior   (terminal-ish, can revive via REVISE)
draft -> partial                                  (mixed evidence)
draft -> inference_only                           (no source path, never validated)
```
`inference_only` claims may appear in synthesis ONLY as explicitly labeled speculation, never as fact.

## 8. Append-Only Surfaces
- `kernel/review_log.md`: append-only. Never delete or rewrite a verdict.
- `shell/02_search/search_log.md`: append-only.
- `kernel/citations.md`: entries may be enriched (add DOI, fix metadata) but a content_hash, once set, is immutable.
- `kernel/claims.md`: status fields are updated (not append-only) but every status change should have a corresponding review_log entry for traceability.

## 9. What "I searched and found nothing" must mean
Before asserting "no prior work found" in NOVELTY_CHECK, you must have:
- run ≥3 query classes across ≥2 sources, all logged in search_log.md,
- and explicitly list the closest hit even if not a match.
Otherwise the assertion is a hallucination.