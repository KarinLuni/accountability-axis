# The Accountability Axis (α) for Agent Actions — verifiable form

**Author:** K. Lunina · ORCID [0009-0000-5586-738X](https://orcid.org/0009-0000-5586-738X)  
**Identifier:** `alpha-axis/0.1` · **Status:** public draft for review · **Licence:** Apache-2.0

This repository contains the specification, the 95-case base vector corpus, a dependency-free reference verifier, reference decision records, execution records, and supplementary native-format vectors for previously unexercised table rows and isolated record defects. The accountability class has two values: `delegable` and `human_only`.

The browser companion is maintained separately: [Alpha-Gate Lab](https://github.com/KarinLuni/alpha-gate-lab).

## Relation to the public κ reference model

This is an independent companion specification for the accountability axis (α). It uses the public κ vocabulary and reference ladder of Mayur Agnihotri’s [aisvs-c9-action-class-conformance](https://github.com/Mayur021/aisvs-c9-action-class-conformance) (v1.2.0) to keep the vector inputs self-contained. It does not alter that model’s κ classification; it specifies the independent question of whether an agent may be the accountable subject of an action.

## Acknowledgements

This work benefited from the public technical discussion with Mayur Agnihotri in [OWASP/AISVS#1154](https://github.com/OWASP/AISVS/issues/1154) and from his recommendation to publish a verifiable independent procedure before proposing a later AISVS change. His public κ reference model is cited here under its Apache-2.0 licence. This acknowledgement does not imply endorsement.

## Layout

| Path | Contents |
|---|---|
| `SPEC.md` | The specification. Sections 3–10 are normative. |
| `vectors/` | The unchanged 95-case base corpus in six JSON files. |
| `verifier/alpha_verify.py` | Dependency-free Python reference verifier and audit runner. |
| `examples/reference-records.json` | Decision records produced by the reference verifier for all 95 base cases. It is a concrete §7 record fixture and the parity fixture for the separate browser companion. |
| `RESULTS.md` | Reproducible execution record for the base corpus and the supplementary-vector run. It records artefact behaviour, not a deployed product. |
| `vectors-supplementary/N-vectors.json` | N-01…N-19, outside `vectors/` so the base-corpus hash and default 95-case selftest remain unchanged. |
| `vectors-supplementary/spec-table-derivation.md` | The cited SPEC-table reading for N-01…N-19. |
| `vectors-supplementary/lab-comparison.md` | Recorded comparison of the supplementary vectors against the separate browser companion’s engine. |
| `vectors-supplementary/lab-engine-run.json` | Machine-readable record of that comparison. |
| `docs/ambiguities.md` | Open readings in the specification and a documented verifier-versus-SPEC difference. |
| `docs/coverage.md` | Coverage of SPEC table rows by the base and supplementary vector sets. |
| `CHANGELOG.md` | Publication-archive change entry. |
| `CITATION.cff`, `LICENSE`, `NOTICE` | Citation and Apache-2.0 publication files. |
| `MANIFEST.sha256` | SHA-256 digests for every payload file in this repository. |

## Run

Python 3.8 or later and the standard library are sufficient.

```sh
python3 verifier/alpha_verify.py selftest
# selftest: PASS 95 / FAIL 0 / UNESTABLISHED 0 of 95 cases

python3 verifier/alpha_verify.py records -o generated-reference-records.json
# compare generated-reference-records.json with examples/reference-records.json

python3 verifier/alpha_verify.py --vectors vectors-supplementary selftest
# selftest: PASS 19 / FAIL 0 / UNESTABLISHED 0 of 19 cases

sha256sum -c MANIFEST.sha256
```

The supplementary command reads the native N-vector file; the accompanying JSON comparison record has no `vectors` array and contributes no cases.

## Three results, two gate outcomes

The named checks use `PASS`, `FAIL`, and `UNESTABLISHED`. At the gate, only PASS proceeds; FAIL and UNESTABLISHED block. See `SPEC.md` §§3.3 and 8.

## Licence

Apache-2.0. See `LICENSE` and `NOTICE`.
