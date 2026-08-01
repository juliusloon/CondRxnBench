# Phase 5 Round B/C — Shard-assembled Candidate Final Independent Review (Iteration 32)

## Verdict

**PASS — the restored shard-assembled Phase 5 candidate is complete, contract-consistent, and verifiable.**

This was a read-only final review.  No training, metric materialization, shard,
or candidate artifact was rewritten.

## Checks

| Check | Result | Evidence |
| --- | --- | --- |
| Specified chem verifier | PASS | Executed `/Users/juliusloon/miniforge3/envs/chem/bin/python scripts/verify_benchmark_v0_1_baselines.py`. It returned `baseline_candidate_verification: passed`, 216 formal runs, 108 controls, and winner manifest `c02ebfe1dd06ddecd2a76737cfb6e08ecd5ef8cd079acfb5f838ae5c6da9d8fb`. Arrow `sysctlbyname` messages are sandbox cache-probe warnings only. |
| Final manifest | PASS | `manifest.json` is `candidate_not_promoted`, declares `assembly: validated_source_split_shards`, and records 239,652 predictions, 324 runs, 108 controls, 4,140 metric rows, 1,208 summary rows, and the contract row-hash manifest `c02ebfe1…a9d8fb`. |
| Shard assembly | PASS | `scripts/assemble_benchmark_v0_1_baseline_shards.py` enumerates the prescribed 2 sources × 6 splits × 3 seeds. All 36 expected seed-shard manifests exist. Each has 9 runs (six formal and three controls), three control rows, six frozen winners, and two source-scoped structural N/A rows. The final prediction, run, and control ledgers are exact unions of the 36 shards; the four final structural N/A rows result from deduplication across seed/split shards. |
| Task 5 and 6 coverage | PASS | S1 Task 5 completed rows contain `spearman`, `ndcg`, `top_1_recall`, `top_3_recall`, and `top_5_recall`. S1 Task 6 contains regret plus top-1/3/5 observed-optimum-hit metrics. All 360 Task 5/6 non-S1 rows are explicit null-valued `not_applicable` / `not_supported`, not omitted or zero-filled. |
| Source stratification | PASS | The 1,208-row summary retains only the two source labels; no leaderboard run×task group mixes sources. |

## Review decision

Phase 5 Round B/C baseline materialization evidence passes final independent
review.  The candidate remains unpromoted; any benchmark promotion still
requires the separate Phase 6 release decision under ADR 0007.
