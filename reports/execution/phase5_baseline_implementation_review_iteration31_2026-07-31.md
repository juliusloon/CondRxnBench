# Phase 5 Round B/C — Baseline Candidate Independent Re-review (Iteration 31)

## Verdict

**PASS — the current Phase 5 candidate satisfies the accepted baseline experiment contract and ADR 0007 materialization requirements.**

The reviewer only rewrote `leaderboard.parquet`, `leaderboard_summary.parquet`,
and `task_split_coverage_ledger.parquet` through the user-authorized,
evaluation-only metrics materializer.  No training, frozen prediction, split,
or raw-data artifact was changed.

## Independent checks

| Contract check | Result | Independent evidence |
| --- | --- | --- |
| Winner freeze and manifest | PASS | `winner_freeze.jsonl` has 216 rows, is in the required lexicographic order, and is byte-for-byte identical to `metadata/benchmark_v0_1_pretest_winner_freeze.jsonl` (both raw SHA-256 `6be2a066…877c26e`). All 216 canonical row hashes recompute correctly. The required ordered-row-hash manifest is `c02ebfe1…a9d8fb`, equal to `manifest.json`. |
| No test-set selection | PASS | The runner evaluates candidates on train→val only, constructs and verifies the frozen winner before the train+val fit/test prediction, and every formal prediction has the matching frozen row hash. There are zero non-test formal prediction rows. |
| Formal, controls, and structural N/A ledgers | PASS | `run_ledger.parquet` records 216 formal and 108 negative-control runs (324 total); `negative_control_ledger.parquet` has 36 rows for each required control. `unsupported_family_ledger.parquet` has exactly four source×structural-family `not_supported` entries. |
| Feasibility and Task 5/6 N/A handling | PASS | `task_split_coverage_ledger.parquet` has 84 source×task×split leaves: 64 `supported`, 20 `not_supported`. Every Task 5/6 non-S1 leaderboard cell is explicit `not_applicable`/`not_supported` with null score. |
| Metric contract and source stratification | PASS | Latest `leaderboard.parquet` has 4,140 rows and contains S1 Task 5 `spearman`, `ndcg`, and `top_1/top_3/top_5_recall`; Task 6 has regret plus top-1/3/5 optimum-hit metrics. `leaderboard_summary.parquet` has 1,208 rows, retains a source field for every row, and no run×task group combines sources. |
| Clean Python 3.11 rerun | PASS | Using `/private/tmp/condrxnbench-core-v0_2-py311/bin/python`, the latest authorized metrics materialization completed from frozen predictions, then `scripts/verify_benchmark_v0_1_baselines.py` passed with 216 formal runs, 108 controls, and manifest hash `c02ebfe1…a9d8fb`. The observed Arrow `sysctlbyname` cache-probe warnings are sandbox-environment warnings only; both commands exited successfully. |

## Review decision

Phase 5 Round B/C baseline candidate evidence is internally consistent and
contract-bound.  This passes baseline materialization review only; per ADR
0007 it does **not** itself authorize benchmark promotion, which remains a
Phase 6 release-gate decision.
