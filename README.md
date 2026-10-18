# The Accountability Axis (α) for Agent Actions

**Author:** K. Lunina · ORCID [0009-0000-5586-738X](https://orcid.org/0009-0000-5586-738X)  
**Identifier:** `alpha-axis/0.1` · **Status:** public draft for review · **Licence:** Apache-2.0

This repository is a self-contained, checkable form of the accountability axis for agent actions. It contains the specification, its unchanged 95-case base corpus, a dependency-free reference verifier, a concrete decision-record fixture, and supplementary boundary cases. The accountability class has two values: `delegable` and `human_only`.

**Interactive browser companion:** [Open Alpha-Gate Lab](https://karinluni.github.io/alpha-gate-lab/) · [repository](https://github.com/KarinLuni/alpha-gate-lab).

## The question this artefact makes checkable

Consequence and reversibility answer how much autonomy an action may receive. Accountability answers a different question: whether an agent may be the accountable subject of the action at all. A `human_only` action requires an identified natural person on record as the party to the obligation; an approval is not that record.

## Relationship to the AISVS C9 action-class suite

The accountability gap was set out by K. Lunina in [OWASP/AISVS#1154](https://github.com/OWASP/AISVS/issues/1154). This repository uses the public κ vocabulary and reference ladder of Mayur Agnihotri’s [aisvs-c9-action-class-conformance](https://github.com/Mayur021/aisvs-c9-action-class-conformance) (v1.2.0). The κ model grades reversibility and consequence; this repository specifies the independent α class. The α specification, corpus, and conclusions are K. Lunina’s work.

### Acknowledgement

The author thanks Mayur Agnihotri for private technical correspondence that clarified how an AISVS gap becomes assessable: publish a separate, independently checkable reference procedure first, so that a later requirement has a concrete artefact to cite. His review helped sharpen the treatment of the trust boundary, externally established chain extent, the distinct `UNESTABLISHED` outcome, and re-approval for extensions. The α axis, specification, corpus, and conclusions are K. Lunina’s independent work.

## Contents

| Path | Purpose |
|---|---|
| `SPEC.md` | The normative procedure. Sections 3–10 are normative. |
| `vectors/` | The unchanged 95-case base corpus in six JSON files. |
| `verifier/alpha_verify.py` | Dependency-free Python reference verifier and audit runner. |
| `examples/reference-records.json` | The 95 decision records produced by the reference verifier. It is a concrete §7 fixture and parity fixture for the browser companion. |
| `vectors-supplementary/N-vectors.json` | N-01…N-19: supplementary boundary cases. They do not change the base corpus or its hash. |
| `vectors-supplementary/README.md` | The purpose and SPEC basis of the supplementary cases. |
| `docs/coverage.md` | A guide to the normative table conditions directly exercised by the base and supplementary cases. |
| `RESULTS.md` | A provenance-aware index for published runs against implementations. It is empty until an implementation run is recorded. |
| `CITATION.cff`, `LICENSE`, `NOTICE` | Citation and Apache-2.0 publication files. |
| `MANIFEST.sha256` | SHA-256 digests for every payload file in this repository. |

## Run

The reference verifier is dependency-free. The published self-tests have been run with the standard library on CPython 3.8–3.13; see **Timestamp-parsing scope** below before treating those runs as a cross-version interoperability claim.

```sh
python3 verifier/alpha_verify.py selftest
# selftest: PASS 95 / FAIL 0 / UNESTABLISHED 0 of 95 cases

python3 verifier/alpha_verify.py records -o generated-reference-records.json
# compare generated-reference-records.json with examples/reference-records.json

python3 verifier/alpha_verify.py --vectors vectors-supplementary selftest
# selftest: PASS 19 / FAIL 0 / UNESTABLISHED 0 of 19 cases

sha256sum -c MANIFEST.sha256
```

## Reading results

Each applicable check records `PASS`, `FAIL`, or `UNESTABLISHED`. Only PASS opens the binary gate; FAIL and UNESTABLISHED both block. See `SPEC.md` §§3.3 and 8.

## Timestamp-parsing scope

The published 95 base cases and 19 supplementary cases pass on CPython 3.8–3.13. That result does not establish identical treatment of timestamp strings outside those corpora. In cross-implementation testing of 51 timestamp forms, the Python verifier and Alpha-Gate Lab returned different verdicts for 9 forms. For example, the Python verifier accepts `20261014T090000Z` and `2026-10-14t09:00:00Z`, while the Lab returns `UNESTABLISHED`. On non-corpus records, the verifier also returned different verdicts between CPython 3.8–3.10 and CPython 3.11–3.13.

Until the timestamp lexical profile is specified and both implementations are aligned, record the interpreter version or Lab version with any run and do not treat an unvectored timestamp result as evidence of Python–Lab parity. See `SPEC.md` §12.7.

## Licence

Apache-2.0. See `LICENSE` and `NOTICE`.
