# Implementation-run index

This file indexes published runs of `alpha-axis/0.1` against implementations. The released specification, vectors, reference verifier, and decision-record fixture are not themselves implementation runs and are not listed as one here.

## How to read a run entry

Each entry identifies the implementation, version or commit, suite release, report location, report filename, SHA-256 digest, run origin, self-reported status, and re-runnability. These fields identify the published report without turning the index into a claim about the implementation.

A report should state its per-case outcomes as `N PASS / F FAIL / U UNESTABLISHED of M`, rather than as a percentage alone.

## Runs

No implementation runs recorded yet.

| Implementation | Version / commit | Suite release | Date | Result | Self-reported | Re-runnable | Run origin | Report file | SHA-256 |
|---|---|---|---|---|---|---|---|---|---|
| _(none yet)_ | | `alpha-axis/0.1` | | | | | | | |

## Adding a run

1. Pin the report to the exact `SPEC.md` revision and vectors hash used for the run.
2. Publish the report at a stable URL or release asset and state the filename whose bytes are hashed.
3. Record the per-case outcomes, implementation version, run origin, self-reported status, and re-runnability.
4. Add a row with the report URL and SHA-256 digest.
