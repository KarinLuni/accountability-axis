# Supplementary boundary cases

`N-vectors.json` contains nineteen supplementary cases for normative conditions that are deliberately kept outside the accepted 95-case base corpus. They do not change the base corpus, its ordering, or its SHA-256 digest.

The cases make selected boundaries of the procedure executable. Each vector identifies `oracle_basis: spec` and the SPEC clause that determines its expectation.

## What the cases exercise

| Cases | Rule boundary |
|---|---|
| N-01, N-02 | A party type that is absent or not recognised is not established. |
| N-03…N-08 | A workflow must be established outside agent control before its first untrusted read; recorded timestamps must establish that ordering. |
| N-09 | A step outside an established workflow requires external re-establishment and a new approval before it can proceed. |
| N-10…N-12 | Multiple accountable-party records are aggregated: a FAIL governs; otherwise a PASS governs; otherwise the result is UNESTABLISHED. |
| N-13…N-19 | Each case isolates one accountable-party evidence condition: resolvable identity, acknowledgement, capacity, action binding, single-use nonce, performer, or stated basis. |

These cases are supplementary documentation and test material. They do not amend the normative procedure in `SPEC.md`.

## Run

```sh
python3 verifier/alpha_verify.py --vectors vectors-supplementary selftest
```
