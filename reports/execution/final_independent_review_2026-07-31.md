# CondRxnBench Benchmark v0.1 — Final Independent Review

Date: 2026-07-31  
Review mode: read-only

## Final verdict

**PASS — `CondRxnBench-Benchmark v0.1` is a hash-bound local release with no remaining P0 release blocker.**

The release boundary is `releases/condrxnbench-benchmark-v0_1/manifest.json`.
Its `promoted_local_release` status does not erase the explicitly retained
candidate provenance of the underlying Core/baseline artifacts.

## Release integrity

All declared input paths exist and all four independently recomputed SHA-256
values exactly match the release manifest:

| Input | SHA-256 |
| --- | --- |
| Core v0.2 manifest | `101e9d5b1c29718d37f65e4b3a8dad77aa0edc415421b40bbe3b3e45ac1f05e2` |
| Strict pair/graph benchmark manifest | `79066267d1b9a827565805195d907903631a64785e1afa407339395c21c78e33` |
| S0–S5 split manifest | `d2b2dae8ef5c3649667c3629cf18ac428590921ce5cf8f6937cc2bc328aaed2f` |
| Baseline candidate manifest | `d20883edff10d6b3c8ac3ec1ccc2c246c793311d0662384c337681fd3d6cde88` |

All six listed acceptance-evidence files exist. The baseline input manifest
declares the validated shard assembly, 216 formal runs, 108 controls, 239,652
test predictions, 4,140 per-seed metrics, 1,208 summaries, and winner manifest
`c02ebfe1dd06ddecd2a76737cfb6e08ecd5ef8cd079acfb5f838ae5c6da9d8fb`.

## Independent verification

Each command used the specified direct `chem` interpreter,
`/Users/juliusloon/miniforge3/envs/chem/bin/python`, and exited successfully:

| Command | Result |
| --- | --- |
| `tests/verify_core_v0_2.py` | PASS — Core v0.2 records, controls, and side tables verified. |
| `tests/verify_benchmark_v0_1.py` | PASS — strict pair universe, reconciliation, and graph bijection verified. |
| `tests/verify_benchmark_v0_1_splits.py` | PASS — deterministic manifests, OOD separation, and pair-exclusion ledger verified. |
| `tests/verify_metrics_v0_1_toy.py` | PASS — metric toy, boundary, and negative checks verified. |
| `scripts/verify_benchmark_v0_1_baselines.py` | PASS — 216 formal runs, 108 controls, and the frozen winner manifest verified. |

The harmless Arrow `sysctlbyname` cache-probe messages observed in this sandbox
did not affect any verifier exit status or result.

## Documentation and limitation audit

`STATUS.md`, `PROGRESS.md`, `ROADMAP.md`, both README files, and the changelog
all consistently describe this as a **local** Benchmark v0.1 release and place
future work in a new goal/version. `CHANGELOG.md` keeps the local promotion in
`Unreleased`, which is consistent with the absence of an externally tagged
semantic-version package release.

`final_execution_summary.md` accurately identifies the baseline as candidate
evidence beneath the hash-bound local release and retains the material limits:

- absolute yield is source/yield-type stratified, with no cross-source absolute leaderboard;
- reaction-only Ridge and descriptor RF are explicit source-backed `not_supported` entries;
- Task 5 and Task 6 are explicit N/A outside S1.

## Residual P0

**None.** The above limitations are declared scope boundaries, not untracked
release defects. Any new source, reaction representation, feature family,
split, or test re-run requires a new goal, freeze/version, and release review.
