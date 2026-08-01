# Phase 4 Round A — Proposed.5 Independent Contract Review (Iteration 17)

## Verdict

**FAIL — the two Iteration 16 themes are only partially repaired.  Do not
generate a split manifest yet.**

The proposed.5 matrix is current and the direct-delta/variance registry
conflict is fixed.  However the passed toy command still is not a complete,
fixture-driven verifier of the metric contract, so it cannot establish the
goal’s “every metric has analytical toy, boundary, and negative cases” hard
acceptance criterion.

## Independent checks performed

- `tests/verify_metrics_v0_1_toy.py` was run in the pinned temporary Python
  environment and printed its success message.
- Current SHA-256 values were recomputed.  Matrix
  `config_sha256=ac629ef8…30b111`, Core manifest
  `101e9d5b…c1f05e2`, and Benchmark manifest
  `79066267…1c78e33` match the current files.
- The matrix still has exactly 84 leaves (64 `limited`, 20 `not_supported`) and
  no competing source-free feasibility object appears in proposed.5.

## Iteration 16 blocker resolution

| Iteration 16 finding | Verdict | Evidence |
| --- | --- | --- |
| Matrix provenance after contract change | PASS | The matrix was rebuilt against the proposed.5 config hash, and retains matching Core/Benchmark input hashes. |
| `within_group_variance_ratio` incompatible with direct Task 2 Δ prediction | PASS | Task 2 lists only direct-delta-compatible metrics; the top-level `metrics.pair` list no longer contains `within_group_variance_ratio`; Task 1/`metrics.absolute` owns that endpoint-yield metric. |
| Toy/boundary/negative verifier faithfully validates the frozen metric contract | FAIL | The R2 constant-truth guard was corrected, and a Pearson calculation was added, but most required metric behavior remains unimplemented or asserted only through inline/hard-coded values rather than fixture-defined expected results. |

## Remaining blocker — metric fixture/verifier coverage is incomplete

The verifier exit code is green, but inspection of
`tests/verify_metrics_v0_1_toy.py` and its fixture shows the following gaps:

1. `corr()` (lines 25–28) still implements only Spearman.  Line 51 invokes
   `pearsonr` directly on a two-point inline case, rather than a contract
   metric function with a fixture expectation.  No fixture can distinguish a
   Pearson result from Spearman.
2. The fixture contains no expected numeric cases for MAE/RMSE, Pearson,
   Spearman, direction accuracy/macro-F1, AUPRC/AUROC/F1, NDCG, top-k recall,
   factor-wise sensitivity, group-mean variance ratio, or regret.  Their
   current assertions are inline constants or simple arithmetic.
3. Direction testing establishes the label threshold, but never evaluates
   Task 3 `direction_accuracy` or `direction_macro_f1`, including the
   contract’s absent-class disposition.
4. Recommendation testing only reads the literal `"hit"` and evaluates
   `5 - 5`; it does not compute a deterministic ranked top-k list, multiple
   optimum hits, or the specified regret from fixture inputs.
5. The zero-denominator sensitivity fixture is only compared with a literal;
   it is not passed through a guarded sensitivity-ratio implementation.
   Factor-wise sensitivity has neither source/factor fixture identifiers nor a
   macro aggregation check.  The variance test uses a single inline group, not
   the required mean-over-groups calculation.
6. Empty/missing-prediction checks similarly assert sentinel text and null
   presence, not a common input-validation path returning the declared
   `not_supported_with_reason` or `reject_input` result.

These are not merely coverage niceties: they leave a metric implementation
free to differ from the frozen contract while this verifier still passes.

## Minimal final repair

Replace the ad-hoc inline checks with fixture-driven metric functions.  Expand
`metrics_v0_1_toy_cases.json` to supply inputs and exact expected
numbers/reason codes for every metric in `tasks.*.metrics`, including at least
one non-collinear Pearson-vs-Spearman case, ternary macro-F1 with an absent
class, source/factor-labelled macro sensitivity, multi-group variance ratio,
top-k/multiple-optimum ranking, and non-zero regret.  Make the verifier load
those expectations and test its functions—not library defaults or static
fixture strings.  Retain the existing R2 and all S0–S5/matrix tests.

## Contract completeness check

No new undefined Task, S0–S5 split predicate, or direct-Δ/variance conflict
was found in proposed.5.  The feasibility matrix remains intentionally
`limited` wherever actual split selection has not yet been run, which is
correct at Round A.  The sole remaining blocker is the required executable
metric/fixture gate above.

## Review decision

Apply only the fixture/verifier repair, increment the proposed contract
version if the metric semantics or required fixture list changes, and repeat
Round A.  No split, prediction, metric result, baseline, or promotion is
authorized by this FAIL.
