# Phase 4 Round A — Proposed.11 Independent Contract Review (Iteration 22)

## Verdict

**FAIL — fixture closure and matrix provenance pass, but Task 5’s metric
contract has been corrupted by two fixture IDs. Do not build formal splits.**

This was a read-only Round A review.  JSON parsing passed; the toy verifier
passed in the pinned environment; `tests/verify_phase0_inputs.py` passed; and
no formal split manifest exists in `data/processed/benchmark_v0_1`.

## Passing checks

| Requirement | Result | Evidence |
| --- | --- | --- |
| Required fixture set is exact | PASS | `metrics.fixtures.required` and `metrics_v0_1_toy_cases.json` each contain exactly 21 keys, with no set difference. |
| Matrix provenance is current | PASS | Proposed.11 config SHA-256 `1792e581…ad7ac9`, Core manifest `101e9d5b…c1f05e2`, and Benchmark manifest `79066267…1c78e33` equal the matrix provenance; it contains exactly 84 leaves. |
| S0–S5 and pair partition contract | PASS | Fixed seed, deterministic selection rules, source-specific roles, explicit null policy, val/test OOD disjointness, no cross-partition pair use, exclusion ledger, freeze/version policy, and no structure-OOD claim remain present. |
| Labels and source semantics | PASS | Direction is exclusive; cliff is frozen to `strong`; success remains unsupported; source yield types remain separated and absolute cross-source aggregation is forbidden. |
| Fixture execution / edge coverage | PASS | Toy verifier exercises input rejection, correlation guards and discrimination, label/cliff boundaries, class absence, ranking, top-k, regret, sensitivity denominator, multi-group variance, and factor-wise sensitivity. |

## Blocking finding — Task 5 names fixture IDs as metrics

In `tasks.Task5_ranking.metrics`, proposed.11 lists:

```json
["spearman", "ndcg", "top_k_recall", "sensitivity_positive", "pearson_constant_prediction"]
```

The final two names are fixture case IDs, not metrics.  They do not occur in
the top-level ranking metric contract and do not express a Task 5 evaluation
quantity.  This violates the Task 1–7 requirement to freeze task-specific
inputs, labels, eligibility, split, and **metrics**, and would let a later
evaluator attempt unsupported pseudo-metrics.

**Minimal repair:** restore `Task5_ranking.metrics` exactly to:

```json
["spearman", "ndcg", "top_k_recall"]
```

Keep `sensitivity_positive` and `pearson_constant_prediction` only in
`metrics.fixtures.required`.  Recompute the feasibility matrix’s config hash,
then repeat this independent review.  No other P0 issue was found in this
review.

## Review decision

Apply only the minimal task-metric cleanup and rebuild the provenance hash.
No split, prediction, metric result, baseline, benchmark promotion, or release
is authorized by this FAIL.
