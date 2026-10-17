prompt_version: 1610_17_12
spec_commit: sha256:847573b5b9b38e1a34ba19cdce8aabd3ca381512026ff4509f6cfcd25d1aa31e
corpus_version: alpha-axis/0.1; base_vectors_sha256:51c32a3a08071a0c939a561288b45fdf19c39d7ad1d77b69212ff10fb99a6232; base_cases:95; additions:N-01…N-19
generated: 1610_17_18
---
# Phase 4 — SPEC-table derivation before Lab execution

## Method

Each proposed expectation was read from the first applicable row of the normative table named in its vector-level `citation`. The derivation below was completed before the Lab engine was run.

## C — isolated §6.3 row 9 defects (priority first)

| ID | Only changed field from the complete proper record | SPEC result | Deciding text |
|---|---|---|---|
| N-13 | `party.resolvable: false` | UNESTABLISHED | §6.3 row 9: identity not resolvable. |
| N-14 | `acknowledged: false` | UNESTABLISHED | §6.3 row 9: not acknowledged. |
| N-15 | `capacity` absent | UNESTABLISHED | §6.3 row 9: capacity missing. |
| N-16 | `bound_to_action` absent | UNESTABLISHED | §6.3 row 9: binding not evidenced. It is not row 6, which requires explicit `false`. |
| N-17 | `nonce_single_use` absent | UNESTABLISHED | §6.3 row 9: nonce not evidenced. It is not row 7, which requires explicit `false`. |
| N-18 | `performer` absent | UNESTABLISHED | §6.3 row 9: performer not evidenced. |
| N-19 | `basis: implied` | UNESTABLISHED | §6.3 row 9: basis is not `acknowledged_as_party`. It is not row 5, which requires `basis: approval`. |

These readings isolate the target conditions in P7-07, P7-08 and P7-14 by restoring their missing `performer`; no second §6.3 defect is introduced.

## A — previously unexecuted rows (priority second)

| ID | First applicable SPEC row | Result |
|---|---|---|
| N-01 | §6.3 row 4 — `party.type` missing | UNESTABLISHED |
| N-02 | §6.3 row 4 — `party.type` is not `natural_person` and not one of row 3’s listed non-human types | UNESTABLISHED |
| N-03 | §5.1 E5 row 1 — no establishment record | UNESTABLISHED |
| N-04 | §5.1 E5 row 8 — first-read marker present but not offset-aware | UNESTABLISHED |
| N-05 | §5.1 E5 row 10 — equal timestamps do not evidence ordering | UNESTABLISHED |
| N-06 | §5.1 E5 row 10 — the two offset-aware strings identify the same instant | UNESTABLISHED |

## B — partial rows and aggregation (priority third)

| ID | First applicable SPEC rule | Result |
|---|---|---|
| N-07 | §5.1 E5 row 5 — establishment time not offset-aware | UNESTABLISHED |
| N-08 | §5.1 E5 row 11 — 10:00+03:00 is 07:00Z, before 08:00Z | PASS |
| N-09 | §5.4 X2 — external re-establisher but `new_approval_obtained` absent | UNESTABLISHED |
| N-10 | §6.3 aggregation — no FAIL and one PASS | PASS |
| N-11 | §6.3 aggregation — any FAIL governs | FAIL |
| N-12 | §6.3 aggregation — no PASS and no FAIL | UNESTABLISHED |

## No new ambiguity entered

For the targeted predicates, the cited row or aggregation sentence decides the expectation. N-09 does not claim that the sparse re-establishment object settles the separate E4-completeness issue recorded previously as AMB-003; it tests only X2’s explicit missing-approval condition.
