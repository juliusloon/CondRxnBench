# Phase 4 Round A — Proposed.2 Independent Contract Review (Iteration 14)

## Verdict

**FAIL — proposed.2 is a substantial improvement, but does not yet authorize
split materialization, metric computation, predictions, or model results.**

This is a read-only re-review of ADR 0006 and
`configs/benchmark_v0_1_task_split_metrics_contract.json` at contract version
`CondRxnBench-Benchmark-v0.1-task-split-metrics-proposed.2`.  The JSON parses
with `python3 -m json.tool`.  No split artifact was generated, and the current
Benchmark candidate still lists `splits` and `model_results` as unimplemented.

## Resolution of the prior review findings

| Prior finding | Verdict | Evidence and residual issue |
| --- | --- | --- |
| **P0-1** source × task × split feasibility leaves with evidence | **Not closed** | Contract line 29 defines a *schema* requiring the dimensions and leaf fields, and supplies only two source-wide prose evidence strings.  The actual `task_split_feasibility` at lines 18–25 remains a source-free `task × S0–S5` matrix of bare strings.  No 2-source × 7-task × 6-split leaf contains status, reason, evidence path, minimum eligibility, nonempty expectation, and materialization disposition. |
| **P0-2** reproducible S0–S5 selection, NULL, S5 | **Partially closed** | Line 28 now fixes a hash order, S1/S2 predicates, literal `NULL_COMPONENT`, canonical tuple selection keys, and the train-side S5 double-OOD predicate.  It still does not require held-out S3 components, S4 tuples, or S5 groups/tuples to be disjoint **between val and test**; global `val_test_disjoint: true` only prevents record identity overlap.  It also does not define a source/role allocation rule when S3 says “one frozen role”, nor an explicit S0 allocation/fraction rounding rule. |
| **P0-3** Task 1–7 input/label/eligibility/split/metric contract | **Partially closed** | Line 27 adds all seven task objects and correctly makes Task 7 prediction-forbidden.  However its `input` values (`record_manifest`, `pair_manifest`) are logical names rather than versioned table paths/column mappings, and the source reporting/aggregation rule is not bound per task.  `Task4.target=cliff_strong` is not an existing strict-pair column and has no construction rule from `cliff_label_primary == strong`.  Task 2 does not state whether a pair score is directly learned or an endpoint-prediction difference; Task 5/6 do not define rank relevance, optimum-tie handling, or regret formula. |
| **P0-4** exclusive direction and unambiguous top-k | **Closed** | Contract line 17 defines an exclusive `delta<-10 / abs(delta)<=10 / delta>10` ternary target and explicitly identifies recommendation hit as top-k containing the observed group optimum rather than a binary success label.  This preserves `success: not_supported_no_threshold`. |
| **P0-5** required metric families and edge cases | **Partially closed** | Line 32 adds sensitivity ratio, within-group variance ratio, factor-wise sensitivity, fixed k values, primary AUPRC, classification handling, and several degeneracy rules.  The three added metric families have no formula/denominator/aggregation definition beyond `denominator_zero`; `regret` also has no formula.  `all.group_aggregation=macro source-stratified` is ambiguous about whether it permits pooled cross-source reporting despite ADR 0006 decision 1 requiring every source to be reported separately.  The actual toy/boundary/negative test cases and expected outputs are not enumerated. |
| **P1-1** manifest/freeze/exclusion-ledger/test-first schema | **Mostly closed, one ambiguity** | Lines 30–31 now prescribe record/pair fields, canonical hash freeze, no anchor, held-out-label prohibition, and a cross-partition exclusion ledger.  `pairs_used_for_training: 0` is ambiguous: it should explicitly mean **cross-partition excluded pairs** used for training equals zero, rather than prohibit all legitimate same-partition pair training permitted by future Task 2 methods.  The negative-cases list and boolean test requirement do not yet name required test fixtures/expected results. |

## Blocking corrections required before a PASS

1. **Materialize the matrix in the contract, not just its type.**  Replace the
   source-free lines 18–25 with a closed
   `task_split_feasibility_matrix[source][task][split]` object.  All 84 leaves
   need the six required line-29 fields and a concrete repository
   `evidence_path`; use `not_supported` (not a bare `limited`) whenever the
   stated materialization check fails.

2. **Make OOD selection independent of both training and validation exposure.**
   Require different val/test held-out component identities for S3, tuple
   identities for S4, and group-plus-tuple identities for S5; state those
   pairwise predicates explicitly.  Define S3's deterministic role-selection
   and allocation procedure, and fix the S0 70/15/15 rounding/tie rule.  This
   makes the seed sufficient to reproduce the actual selection rather than
   merely its sort order.

3. **Finish task object semantics.**  Bind inputs to exact candidate table
   names, versions and source columns; define Task 4 as
   `cliff_label_primary == "strong"`; select either direct pair prediction or
   endpoint-difference construction for Task 2; define ranking relevance,
   group-optimum ties, and same-source regret.  Require a per-source primary
   report for every task; any aggregate must be explicitly prohibited or
   labelled secondary and not a mixed-yield score.

4. **Specify the missing metric formulas and verifiable fixtures.**  Define
   sensitivity ratio, within-group variance ratio, factor-wise sensitivity and
   regret mathematically, including group/source aggregation and all zero/one
   denominator cases.  Add versioned toy inputs with expected output values
   for every metric, cliff and direction boundaries, ranking/optimum ties,
   missing predictions, absent classes, and every S0–S5 leakage rejection.

5. **Scope the training-use invariant.**  Rename the ledger invariant to
   `cross_partition_pairs_used_for_training: 0` (and likewise for pair
   metrics), preserving same-partition Task 2 training as a possible future
   model choice.  Name the fixture that proves the invariant.

## Positive controls retained

- Fixed seed, source-specific yield semantics, no cross-source absolute-yield
  aggregation, and no fabricated structure OOD remain sound (ADR 0006 lines
  13–16; contract lines 5–6).
- Pair records remain separate, require same-partition endpoints, and receive a
  cross-partition exclusion ledger (ADR 0006 line 14; contract lines 16 and
  30–31).
- S5 now states the intended simultaneous train-side group and tuple absence,
  rather than just naming double OOD (ADR 0006 line 18; contract line 28).
- The contract correctly prevents a success threshold being silently inferred
  (ADR 0006 lines 15 and 19; contract line 17).

## Review decision

Revise ADR/config only for the five corrections above, increment the proposed
contract version, validate JSON, and re-run Round A.  The prior P0-4 issue is
closed; all other findings are either only partially closed or remain blocking.
No split, metric, prediction, baseline, or benchmark promotion is authorized
by this FAIL.
