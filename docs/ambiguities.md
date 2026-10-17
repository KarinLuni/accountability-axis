# Open readings and verifier-versus-SPEC notes

This document records readings that the current text does not select. The specification text governs where it differs from the reference verifier (SPEC.md §0).

## AMB-001 — Canonical parameters

**Clause.** SPEC.md §6.2 requires an obligation record to be bound to the action’s “canonical parameters”; §6.3 row 6 makes an explicit `bound_to_action: false` a FAIL.

**Readings.**

1. An implementation may choose a deterministic canonical form and report the Lab field `bound_to_action`.
2. The predicate is not demonstrable until the specification defines the canonical representation and equality relation over transmitted bytes, parsed values, and executed values.

**Status.** Open.

## AMB-002 — `recorded_at`

**Clause.** SPEC.md §6.2 lists `recorded_at` as required content, then states that it is evidenced by the auditor in step 6 of §9.2 and not by the vectors.

**Status.** Closed. It is not a vector input requirement.

## AMB-003 — E4 completeness on re-establishment

**Clause.** SPEC.md §5.4 X2 makes re-establishment subject to E1 and E3–E4. E4 requires, among other things, a chain identifier, establishment time, first-untrusted-read marker, extent detail, and a digest.

**Readings.**

1. Every E4 field is required for a re-establishment result of PASS.
2. X2’s explicit extension conditions are sufficient for a re-establishment result when the attempted step and new approval are present.

**Status.** Open. It affects P5-09 and P5-11: their re-establishment records carry no digest.

## AMB-004 — Capacity authorisation

**Clause.** SPEC.md §6.2 requires a stated `capacity`; §6.3 row 9 makes a missing capacity UNESTABLISHED.

**Readings.**

1. The specified gate check is limited to whether a capacity is stated.
2. The phrase “the relation in which that person is answerable” requires independent evidence that the person holds that capacity.

**Status.** Open. The current vectors test whether capacity is present, not an external authority check.

## AMB-005 — Chain-level aggregation of accountable-party results

**Clause.** SPEC.md §5.3 F4 requires a PASS accountable-party check before each `human_only` step executes. SPEC.md §6.3 defines aggregation only where several records exist for one action.

**Readings.**

1. A chain-level reported result is the worst of its `human_only` steps: FAIL, then UNESTABLISHED, then PASS.
2. The §6.3 several-records rule is applied across `human_only` steps: any FAIL gives FAIL; otherwise any PASS gives PASS; otherwise UNESTABLISHED.

**Status.** Open. F4 makes the gate decision the same under both readings because every `human_only` step needs its own PASS; only the reported chain-level result differs.

## AMB-006 — Offset-aware timestamp predicate

**Clause.** SPEC.md §5.1 E5 uses “offset-aware ISO 8601 timestamp” but does not define a grammar.

**Readings.**

1. Any offset-aware ISO 8601 form accepted by the implementation is sufficient.
2. A platform-independent grammar is required before a timestamp form can establish ordering.

**Status.** Open. The reference verifier uses Python `datetime.fromisoformat`; accepted forms can depend on the Python version.

## AMB-007 — Trust as a gate condition

**Clause.** SPEC.md §3.3 defines trust as a check; §8 T1 names checks as three-valued; §8 T2 says the gate proceeds only when every applicable check is PASS. α-P3 describes a closed gate in the absence of an obligation record.

**Readings.**

1. T1/T2 apply literally: any non-PASS trust check blocks.
2. For a `human_only` action, a PASS accountable-party record opens the gate even where declaration trust is not PASS, following the α-P3 framing.

**Status.** Open. No base vector separates these readings.

## AMB-008 — Empty-extent α fold

**Clause.** SPEC.md §5.1 E3 forbids an empty extent and E5 row 4 blocks it. SPEC.md §5.3 F1 states that `fold_α(C)` is `human_only` if any step in C is `human_only`, otherwise `delegable`.

**Readings.**

1. Read literally over an empty set, F1 yields `delegable`.
2. The empty extent is fail-closed for the fold and yields `human_only`.

**Status.** Open. E3 and E5 row 4 make the gate outcome `block` under either reading; only `fold.alpha` differs.

# Verifier vs SPEC

The verifier treats `party.type: team` and `party.type: organization` as non-human types and returns FAIL. SPEC.md §6.3 row 3 lists `agent`, `service`, `role`, `group`, and `organisation`; other party-type values proceed to row 4 and return UNESTABLISHED. No base vector supplies either `team` or `organization`. By SPEC.md §0, the specification text prevails. No verifier code is changed in this release.
