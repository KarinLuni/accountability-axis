# Coverage of normative table rows

The base corpus is the unchanged 95-case set in `vectors/`. N-01…N-19 are supplementary vectors in `vectors-supplementary/` and are not part of the base-corpus hash or its default selftest.

## §6.3 — accountable-party check

| Row | Result | Reached by base 95 | Reached by supplementary vectors |
|---:|---|---:|---|
| 1 — no record for this action | UNESTABLISHED | 16 | — |
| 2 — record under agent control or unplaced | UNESTABLISHED | 1 | — |
| 3 — listed non-human party type | FAIL | 5 | — |
| 4 — party type missing or unknown | UNESTABLISHED | 0 | N-01, N-02 |
| 5 — `basis: approval` | FAIL | 1 | — |
| 6 — `bound_to_action: false` | FAIL | 1 | — |
| 7 — `nonce_single_use: false` | FAIL | 1 | — |
| 8 — agent performer | FAIL | 1 | — |
| 9 — required evidence not established | UNESTABLISHED | 4 | N-13…N-19 |
| 10 — otherwise | PASS | 39 | — |

The base corpus’s four row-9 cases include an absent performer. N-13, N-14 and N-15 isolate identity resolution, acknowledgement, and capacity by restoring the performer; N-16…N-19 isolate the remaining row-9 evidence conditions.

### §6.3 aggregation after the table

| Combination | Reached by base 95 | Reached by supplementary vectors |
|---|---|---|
| UNESTABLISHED + FAIL | P7-obligation-record/13 | — |
| PASS + UNESTABLISHED | — | N-10 |
| PASS + FAIL | — | N-11 |
| UNESTABLISHED + UNESTABLISHED | — | N-12 |

## §5.1 E5 — establishment check

| Row | Result | Reached by base 95 | Reached by supplementary vectors |
|---:|---|---:|---|
| 1 — no establishment record | UNESTABLISHED | 0 | N-03 |
| 2 — establisher under agent control | FAIL | 2 | — |
| 3 — establisher unplaced | UNESTABLISHED | 2 | — |
| 4 — empty extent | UNESTABLISHED | 1 | — |
| 5 — establishment time absent or not offset-aware | UNESTABLISHED | 1 (absent) | N-07 (not offset-aware) |
| 6 — first-read marker absent | UNESTABLISHED | 1 | — |
| 7 — first-read marker explicit null | PASS | 1 | — |
| 8 — first-read marker not offset-aware | UNESTABLISHED | 0 | N-04 |
| 9 — established after first read | FAIL | 1 | — |
| 10 — same instant | UNESTABLISHED | 0 | N-05, N-06 |
| 11 — otherwise | PASS | 9 | N-08 |

## §5.4 X2 — re-establishment

| Condition | Reached by base 95 | Reached by supplementary vectors |
|---|---:|---|
| External establisher and `new_approval_obtained: true` | 2 | — |
| External establisher and `new_approval_obtained: false` | 1 | — |
| External establisher and `new_approval_obtained` absent | 0 | N-09 |

## Remaining gaps

- No chain contains two `human_only` steps with differing accountable-party results; the readings in AMB-005 are not separated.
- No vector separates the trust-in-the-gate readings in AMB-007.
- N-02 supplies one party type outside the five row-3 types (`contractor`). The requested statement that no party type outside the five listed is present conflicts with N-02; no additional unlisted party-type category is covered.
- No input carries `recorded_at`; AMB-002 records why this is not a vector-input requirement.
