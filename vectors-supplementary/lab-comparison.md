prompt_version: 1610_17_12
spec_commit: sha256:847573b5b9b38e1a34ba19cdce8aabd3ca381512026ff4509f6cfcd25d1aa31e
corpus_version: alpha-axis/0.1; base_vectors_sha256:51c32a3a08071a0c939a561288b45fdf19c39d7ad1d77b69212ff10fb99a6232; base_cases:95; additions:N-01…N-19
generated: 1610_17_20
---
# Phase 4 — Lab comparison against SPEC-table expectations

## Run identity

- Engine: `Alpha-Gate Lab engine` `0.1.0` from `lab/src/engine.js`.
- Invocation: one `A.selftest` call over `N-vectors.json` only.
- Input file SHA-256 as calculated by the Lab engine: `5c9dcdc9623741d02af9ead7a85f0d0fd148f779d78057bd97b57f93a8dd13e6`.
- Summary: `PASS 19 / FAIL 0 / UNESTABLISHED 0 of 19 cases`.

## Result

The run returned no divergence from the nineteen vector expectations. The results are listed in execution order below; this is agreement with the narrow, cited table-row expectations, not a general claim about the Lab or the specification.

| Priority | IDs | Lab result against vector expectation |
|---|---|---|
| C | N-13, N-14, N-15, N-16, N-17, N-18, N-19 | PASS for each comparison |
| A | N-01, N-02, N-03, N-04, N-05, N-06 | PASS for each comparison |
| B | N-07, N-08, N-09, N-10, N-11, N-12 | PASS for each comparison |

No Phase 5 category is assigned here. In particular, this result does not resolve the previously recorded E4 completeness question; N-09 is limited to the explicit absent-`new_approval_obtained` condition in X2.
