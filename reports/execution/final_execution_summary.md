# CondRxnBench Core v0.2 → Benchmark/Baseline v0.1 execution summary

Date: 2026-07-31. Scope: the Ahneman--Doyle Buchwald--Hartwig and Perera Suzuki--Miyaura HTE sources only.

## Accepted gates

- Core v0.2 standardization, strict pair/graph, bias/leakage, and task/split/metric protocol gates passed their recorded independent reviews.
- Baseline Round C passed in `phase5_baseline_implementation_review_iteration32_2026-07-31.md`.
- The baseline candidate contains 216 frozen formal runs, 108 actual negative-control runs, 239,652 source-stratified test predictions, four evidence-backed structural-family N/A entries, and 4,140 per-seed metric rows (1,208 summaries).
- The winner freeze is byte-identical to the pre-test freeze and has contract hash `c02ebfe1dd06ddecd2a76737cfb6e08ecd5ef8cd079acfb5f838ae5c6da9d8fb`.

## Reproduction and recovery

Full baseline materialization is executed as 36 source×split×seed shards using the frozen Python 3.11 environment and then assembled atomically:

```bash
/private/tmp/condrxnbench-core-v0_2-py311/bin/python scripts/assemble_benchmark_v0_1_baseline_shards.py
/private/tmp/condrxnbench-core-v0_2-py311/bin/python scripts/verify_benchmark_v0_1_baselines.py
/Users/juliusloon/miniforge3/envs/chem/bin/python scripts/materialize_benchmark_v0_1_baseline_metrics.py
```

The `chem` environment is the default environment for repository validation. It includes scikit-learn 1.8.0 and pytest 8.4.2; its newer numerical stack is intentionally not used to regenerate the pre-test winner freeze, because that changes RF validation tie outcomes and is rejected before test access.

## Preserved limitations

- Absolute yields remain source/yield-type stratified; no cross-source absolute leaderboard is claimed.
- `reaction_only_ridge` and `descriptor_random_forest` are N/A for both sources because complete source-backed reaction representations are unavailable.
- Task 5/6 are N/A outside S1 by the accepted feasibility contract; all such cells are explicit in the leaderboard.

## Final independent acceptance

`reports/execution/final_independent_review_2026-07-31.md` independently verified all release-input hashes, the maintenance entry points, and the final Core/Benchmark/split/metric/baseline verifier matrix. Verdict: PASS; unresolved P0 scientific risks: 0.
