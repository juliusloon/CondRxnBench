# Phase 4 Round A — Proposed.5 Independent Contract Review (Iteration 18)

## Verdict

**FAIL — metric verifier coverage is substantially improved but still not a
complete executable check of the frozen negative/boundary contract.  Do not
generate splits yet.**

This was a read-only re-review focused on the sole Iteration 17 blocker.  I
ran the strengthened toy verifier successfully in the pinned temporary Python
environment.  The success output is necessary evidence, but source inspection
shows several required behaviors can still change without making that command
fail.

## What is now closed

| Check | Result | Evidence |
| --- | --- | --- |
| Matrix freshness | PASS | Current contract SHA-256 `ac629ef8…30b111`, Core manifest SHA-256 `101e9d5b…c1f05e2`, and Benchmark manifest SHA-256 `79066267…1c78e33` equal the hashes recorded in the 84-leaf matrix. |
| Absolute, Δ error, R2, variance, factor-MAE, direction, cliff, NDCG and regret positive cases | PASS | The fixture now supplies numeric expected values for these families, and the verifier evaluates most of them against those values. |
| Direct Δ/variance task binding | PASS | No change from Iteration 17: Task 2 and top-level pair metrics exclude `within_group_variance_ratio`; Task 1 owns it. |
| Basic label/cliff boundaries | PASS | The 10/20/30/40 cliff boundaries, direction `[-10,0,10]`, and 20/40 nesting are executable checks. |

## Remaining blocking gaps

### P0-1 — several contract behaviors are still static assertions, not executed metrics

The following statements merely inspect a fixture literal or perform ad-hoc
arithmetic instead of invoking a guarded metric/ranking function:

- Empty and missing-prediction cases (lines 44–45) only compare strings/null
  presence.  No input-validation function returns the contractual
  `not_supported_with_reason` or `reject_input` result.
- Zero-denominator sensitivity (line 71) only reads the expected sentinel;
  the ratio is never attempted through a denominator guard.
- `top_k_recall` at line 65 is the tautology
  `rank_case["top_k_recall"] == 1.0`; no top-k IDs are derived from scores and
  relevance.  It therefore does not test the frozen top-k semantics.
- Multiple-optimum recommendation at line 66 only reads `"hit"` and evaluates
  `5 - 5`; it does not rank candidate IDs, apply deterministic score ties, or
  test that any observed-max ID is a hit.

### P0-2 — correlation and class-imbalance edge semantics remain unproven

- `corr()` still implements Spearman only.  Pearson is called directly rather
  than via a contract metric function, and the single fixture has two points
  with Pearson = Spearman = -1.  It cannot catch a Pearson/Spearman swap or
  incorrect Pearson constant-vector handling.
- The direction macro-F1 fixture has all true classes represented.  It does
  not test the `absent_class: not_supported_with_reason` clause, nor does the
  verifier implement that disposition before calling scikit-learn.
- Cliff single-class status is tested, but its fixture field
  `expected_auprc` is not consumed; no fixture asserts the full three-metric
  status object (`AUPRC`, `AUROC`, F1) mandated by the contract.

These omissions violate the Phase 4 hard acceptance requirement that every
metric has executable toy, boundary, **and negative** cases.  The verifier can
currently pass if the later evaluator handles empty input, missing predictions,
zero denominators, top-k, multiple optima, Pearson, or absent direction classes
differently from the written contract.

## Minimal repair

1. Add contract metric functions for input validation, Pearson and Spearman,
   sensitivity ratio, top-k recall, and recommendation hit/regret; invoke them
   from fixtures rather than inspecting constants.
2. Add a non-monotonic fixture where Pearson and Spearman differ, plus
   constant-prediction tests for both correlations.
3. Add negative fixtures and exact result objects for empty/missing input,
   zero denominator, absent true direction class, single-class cliff all three
   metrics, top-k ID selection, and tied multiple optima.  Validate every
   field, including `expected_auprc`.
4. Add the new case IDs to `metrics.fixtures.required` (or an equivalent
   exhaustive mapping from `tasks.*.metrics`) so removal of a case becomes a
   contract violation.

## Review decision

Proposed.5 remains close, but these executable negative/boundary gaps are
still a Round A blocker.  Apply only the fixture/verifier changes above, then
repeat the review.  No split, prediction, metric result, baseline, or
benchmark promotion is authorized by this FAIL.
