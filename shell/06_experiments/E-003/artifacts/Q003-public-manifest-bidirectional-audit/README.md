# Q-003 public-manifest bidirectional-reference audit

Date: 2026-07-21

Scope: all public IPLoc-ID `data/*T2*.json` manifests available in the audited repository. This is a manifest-structure audit, not a visual audit of every source frame.

Questions:
1. Is an identical query path paired with distinct reference identities?
2. Do manifests explicitly form same-query `ref A/B × candidate A/B` cells?
3. Are sequence-level negative edges reciprocal, and if so are they still cross-image?

Findings:
- LaSOT and VastTrack: zero identical-query reuse under distinct reference sets.
- PDM: repeated paths exist but reference sets do not change.
- GOT-10K: three reused query paths per shot setting; each is own-sequence positive under one reference and unrelated out-class negative under another. These are class-level/query-presence cells, not same-image same-class candidate binding.
- LaSOT train: 28 reciprocal sequence-level negative identity pairs, but the queries are different images/sequences; no fixed `query(A,B)` and no two candidate boxes.

Boundary: establishes absence of an explicitly scored bidirectional same-query candidate-binding cell in these manifests. It does not prove source frames contain no additional instances and does not prove model failure.
