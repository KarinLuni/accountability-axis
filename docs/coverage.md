# Coverage guide

The accepted base corpus is the unchanged 95-case set in `vectors/`. N-01…N-19 are supplementary cases in `vectors-supplementary/`; they do not contribute to the base-corpus hash or its default selftest.

The tables below identify the normative conditions directly exercised by these cases. A count identifies direct cases for that condition; it is not a measure of overall assurance.

## §6.3 — accountable-party check

| Condition | Result | Base cases | Supplementary cases |
|---|---|---:|---|
| No record for the action | UNESTABLISHED | 16 | — |
| Record under agent control or unplaced | UNESTABLISHED | 1 | — |
| Listed non-human party type | FAIL | 5 | — |
| Party type absent or not recognised | UNESTABLISHED | — | N-01, N-02 |
| `basis: approval` | FAIL | 1 | — |
| `bound_to_action: false` | FAIL | 1 | — |
| `nonce_single_use: false` | FAIL | 1 | — |
| Agent performer | FAIL | 1 | — |
| Required evidence not established | UNESTABLISHED | 4 | N-13…N-19 |
| All required evidence established | PASS | 39 | — |

### Aggregation of several records

| Combination | Base cases | Supplementary cases |
|---|---|---|
| UNESTABLISHED + FAIL | P7-obligation-record/13 | — |
| PASS + UNESTABLISHED | — | N-10 |
| PASS + FAIL | — | N-11 |
| UNESTABLISHED + UNESTABLISHED | — | N-12 |

## §5.1 E5 — workflow establishment

| Condition | Result | Base cases | Supplementary cases |
|---|---|---:|---|
| No establishment record | UNESTABLISHED | — | N-03 |
| Establisher under agent control | FAIL | 2 | — |
| Establisher unplaced | UNESTABLISHED | 2 | — |
| Empty extent | UNESTABLISHED | 1 | — |
| Establishment time absent or not offset-aware | UNESTABLISHED | 1 (absent) | N-07 (not offset-aware) |
| First-read marker absent | UNESTABLISHED | 1 | — |
| First-read marker explicitly null | PASS | 1 | — |
| First-read marker not offset-aware | UNESTABLISHED | — | N-04 |
| Establishment after first read | FAIL | 1 | — |
| Same instant | UNESTABLISHED | — | N-05, N-06 |
| Established before the first read | PASS | 9 | N-08 |

## §5.4 X2 — workflow extension

| Condition | Base cases | Supplementary cases |
|---|---:|---|
| External re-establisher and `new_approval_obtained: true` | 2 | — |
| External re-establisher and `new_approval_obtained: false` | 1 | — |
| External re-establisher and `new_approval_obtained` absent | — | N-09 |
