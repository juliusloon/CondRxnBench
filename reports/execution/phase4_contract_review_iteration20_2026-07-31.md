# Phase 4 Round A — Proposed.8 Independent Contract Review (Iteration 20)

## Verdict

**FAIL — Iteration 19 is only partially fixed. Do not generate splits.**

The matrix is fresh and several previously missing paths now execute, but the
required-fixture closure claim is false and the generic empty/missing/Pearson
negative behaviors remain outside contract functions.

## Verified repairs

| Item | Result | Evidence |
| --- | --- | --- |
| Matrix freshness | PASS | Current config SHA-256 `1e43fe4a…fb8084`, Core manifest `101e9d5b…c1f05e2`, and Benchmark manifest `79066267…1c78e33` match matrix fields; leaf count remains 84. |
| Pearson/Spearman positive discriminator | PASS | `pearson_spearman_distinct` now has Pearson `0.7745966692…` and Spearman `0.7378647873…`; the passing verifier evaluates the two distinct values. |
| Single-class cliff full result | PASS | Fixture now contains expected AUPRC, AUROC, and F1 sentinels; verifier compares the full three-key object. |
| Fixture-driven positive sensitivity and multiple optimum hit | PASS | The verifier consumes `sensitivity_positive` and `recommendation_multiple_optima` inputs/results through `sensitivity_ratio` and `top_k_recall`. |

## Remaining blockers

### P0-1 — the required fixture set is not closed

The contract’s `metrics.fixtures.required` has 19 IDs, while the fixture has
20 keys.  The fixture-only key is `sensitivity_positive`.  Thus a required
positive sensitivity case can be silently removed from the contract’s declared
fixture set without a contract-level completeness failure.  This directly
contradicts the requested required-ID/fixture closure.

**Minimal repair:** add `sensitivity_positive` to
`metrics.fixtures.required` (or remove it and use an already-required
appropriately named case), then enforce exact key-set equality in the verifier.

### P0-2 — input and Pearson negative paths are still not contract functions

- Lines 58–59 still implement empty/missing behavior only as a call to
  `top_k_recall(set(), [], 1)` and a static `None` membership check.  There is
  no generic `reject_input` validator consuming the missing-prediction fixture.
- `corr()` remains Spearman-only.  Although the positive Pearson direct call is
  now discriminating, there is no `pearson_contract()` wrapper or
  `pearson_constant_prediction` fixture.  The contract specifies correlation
  `constant_prediction: ... correlation_not_supported`; this path is not
  executed.

**Minimal repair:** add a common validation function that returns the frozen
empty/reject state and invoke it from the fixtures. Add `pearson_contract()`
with minimum-n/constant truth/constant prediction guards, a required constant
prediction fixture, and direct assertions for Pearson and Spearman guards.

## Review decision

No S0–S5, task, direct-Δ/variance, or matrix provenance conflict was found.
Repair only the required-key closure and the two negative contract functions,
then repeat Round A. No split, prediction, metric result, baseline, or
promotion is authorized by this FAIL.
