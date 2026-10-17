# Reference execution record

This file records reproducible executions of the released reference artefacts. It is not a product assessment, certification, or general results index. Each row identifies the corpus, implementation artefact, hashes and reported outcome so that a reader can reproduce the specific run.

## Base corpus — 95 cases

| Date | Artefact | Version / source | Corpus | Vectors SHA-256 (first 16) | Records SHA-256 (first 16) | Reported outcome |
|---|---|---|---:|---|---|---|
| 2026-10-14 | Reference verifier | `verifier/alpha_verify.py` 0.1.0 | 95 | `51c32a3a08071a0c` | `7334cc77970713bd` | PASS 95 / FAIL 0 / UNESTABLISHED 0 of 95 cases |
| 2026-10-15 | Alpha-Gate Lab browser engine | separate browser companion, engine 0.1.0 | 95 | `51c32a3a08071a0c` | `7334cc77970713bd` | PASS 95 / FAIL 0 / UNESTABLISHED 0 of 95 cases |

`examples/reference-records.json` is the 95-case reference-verifier record fixture identified by the first row. The browser companion is built to generate the same record document from the embedded base vectors; its published page performs that comparison in the browser.

## Supplementary vectors — N-01…N-19

| Date | Artefact | Corpus | Vector SHA-256 | Reported outcome | Record |
|---|---|---:|---|---|---|
| 2026-10-16 | Reference verifier | 19 | `5c9dcdc9623741d02af9ead7a85f0d0fd148f779d78057bd97b57f93a8dd13e6` | PASS 19 / FAIL 0 / UNESTABLISHED 0 of 19 cases | `vectors-supplementary/N-vectors.json` |
| 2026-10-16 | Alpha-Gate Lab browser engine | 19 | `5c9dcdc9623741d02af9ead7a85f0d0fd148f779d78057bd97b57f93a8dd13e6` | PASS 19 / FAIL 0 / UNESTABLISHED 0 of 19 cases | `vectors-supplementary/lab-engine-run.json` |

The N-vector expectations are tied to the cited table rows in `vectors-supplementary/spec-table-derivation.md`. The run record is limited to those expectations; it does not settle the open readings in `docs/ambiguities.md`.

## Reproduction

```sh
python3 verifier/alpha_verify.py selftest
python3 verifier/alpha_verify.py records -o generated-reference-records.json
sha256sum generated-reference-records.json examples/reference-records.json

python3 verifier/alpha_verify.py --vectors vectors-supplementary selftest
```

The base reference-record file and the supplementary browser-engine record are released so that the decision-record shape and the recorded runs remain inspectable.
