# Phase 4 Round A — Task / Split / Metric Contract Independent Review

## Verdict

**FAIL — do not materialize split manifests, metrics, or model results from this
contract.**

This is a read-only Round A review of
`adr/0006-benchmark-v0_1-task-split-metrics-protocol.md` and
`configs/benchmark_v0_1_task_split_metrics_contract.json` against Phase 4 of
the active goal.  JSON syntax is valid.  No split or model artifact was
generated or changed by this review.

## Evidence inspected

| Evidence | Observation |
| --- | --- |
| Goal lines 294–308 | Requires an accepted protocol before results, explicit Task 1–7 input/label/eligibility/split/metric contracts, and a **source × task × split** feasibility matrix with evidence. |
| Goal lines 310–328 | Requires precise S0–S5 held-out semantics; separate/versioned record and pair manifests; source/yield-type stratification; sensitivity ratio, within-group variance ratio, and factor-wise sensitivity; and explicit metric edge behavior. |
| Goal lines 332–338 | Requires deterministic manifests/hashes, zero leakage by split type, nonempty partitions or explicit `not_supported`, toy/boundary/negative metric tests, independent reviews, and immutable frozen tests. |
| ADR 0006 lines 13–17 | Correctly fixes the seed, source-aware absolute-yield rule, record-to-pair endpoint rule, no fabricated structure OOD claim, and success-label non-support. |
| Contract lines 8–16 | Correctly identifies partitions, intended split units, source-specific condition roles, S4 marginal condition, S5 limited status, and same-partition pair inclusion. |
| Contract lines 17 and 27–28 | Supplies provisional labels, basic metrics, and several relevant negative cases, but not enough detail to be an executable metric contract. |
| `data/processed/benchmark_v0_1/manifest.json` | Still declares `splits` and `model_results` unimplemented by design; therefore this review did not conflate the no-split candidate with evidence that a Phase 4 implementation passed. |

## What is already sound

| Requirement | Result | Basis |
| --- | --- | --- |
| Fixed seed and historical-only S0 intent | PASS | ADR 0006 decision 1; contract lines 5 and 9. |
| No cross-source absolute-yield pooling | PASS | ADR 0006 decisions 1/3; contract line 6 preserves the two source yield types and forbids aggregation. |
| Structure-evidence boundary | PASS | ADR 0006 decision 4 explicitly calls S2 a source-design-group OOD split, not structure/scaffold/template OOD. |
| Record/pair separation rule | PASS in principle | ADR 0006 decision 2 and contract line 16 require a distinct pair manifest and exclude cross-partition endpoints.  The later implementation must additionally emit the required exclusion ledger. |
| Success threshold is not invented | PASS | ADR 0006 decision 3 and contract line 17 set success classification to `not_supported`. |
| Task 7 is not a prediction head | PASS | ADR 0006 decision 3 and contract line 25 name it an OOD framework. |

## Blocking findings and minimal repairs

### P0-1 — feasibility matrix has neither source dimension nor evidence

The goal requires `source × task × split` values with evidence (goal lines
306–308).  Contract lines 18–25 only contain `task × split` strings.  They do
not distinguish Ahneman (4,132 observed and 8 missing main records) from
Perera (5,760 observed records), or explain why a source/task/split is
supported, limited, or not supported.  A generic `limited` also cannot satisfy
the hard acceptance rule that an infeasible case must be explicitly
`not_supported`, rather than silently yield an empty score.

**Minimal repair:** replace `task_split_feasibility` with a closed
`task_split_feasibility_matrix[source][task][split]` object.  Each leaf must
contain `status` (`supported|limited|not_supported`), `reason`,
`evidence_path`, `minimum_eligible_records_or_pairs`, and the required
nonempty/coverage expectation.  Include both sources and all Task 1–7 × S0–S5
cells.  A `limited` cell must specify the feasibility check and its prescribed
outcome (`materialize` or `not_supported`) when the check fails.

### P0-2 — S0–S5 units are named but selection is not reproducibly defined

Contract lines 9–14 give a unit and selected roles, not the held-out selection
algorithm demanded by goal line 301.  In particular, it leaves unspecified:

- deterministic candidate ordering/tie breaking and how the fixed seed maps to
  source-specific train/val/test selections;
- whether held-out selections for val and test are disjoint, and how target
  fractions/nonempty partitions are enforced or honestly marked infeasible;
- S1's rule that every source-design group has records in the required
  partitions;
- S2's exact train/val/test group-disjointness (and the group identifier);
- S3 component identity (`condition_id`/raw entity), treatment of
  `NULL_COMPONENT`, frequency thresholds, and all held-out-component checks;
- S4 canonical ordered tuple identity, treatment of explicit null components,
  and disjointness from train **and** val as applicable;
- S5's simultaneous group and condition/tuple OOD predicates.  Marking S5
  `limited` does not define double OOD or its failure disposition.

**Minimal repair:** add per-S0–S5 `selection_algorithm`,
`selection_key`, `candidate_eligibility`, `partition_predicates`,
`val_test_disjointness`, `deterministic_tie_break`, and `infeasible_policy`.
For S3/S4/S5, define the identifiers from the source-scoped registry / ordered
role tuple and explicitly state the `NULL_COMPONENT` policy.  S5 must require
both source-design-group absence and tuple/component OOD in train, rather than
only name a combined unit.

### P0-3 — Task contracts are not explicit enough to implement or test

ADR 0006 decision 3 enumerates task names, but the config contains no
per-task declaration of input tables/keys, target construction, eligibility,
allowed split layers, prediction interface, source reporting rule, and metric
binding.  Thus, for example, it is unresolved whether Task 2 consumes direct
pair predictions or differences of endpoint yield predictions, and whether
Task 5/6 candidate sets use `strict_reaction_group_id` with a fixed minimum
cardinality.  Those choices can change a result after test manifests are
known.

**Minimal repair:** add a closed `tasks` object for Task 1–7.  For each task
state `input_artifacts`, `primary_key`, `target`, `eligibility`,
`allowed_splits`, `prediction_contract`, `source_stratification`,
`candidate_set_definition` (Tasks 5/6), `metrics`, and
`not_supported_behavior`.  Bind Task 7 to strata/reporting only and prohibit a
prediction field.  Require all non-absolute metrics to report per source too,
with any aggregate explicitly disallowed or precisely defined.

### P0-4 — direction labels overlap, while recommendation uses ambiguous “success”

Contract line 17 defines `decrease: delta<0`, `invariant: abs(delta)<=10`, and
`increase: delta>0`.  Every nonzero delta in `[-10, 10]` belongs both to
`invariant` and a sign class, so Task 3's label cardinality and macro-F1 are
undefined.  This conflicts with the requested explicit direction/invariant
policy.  The same contract says thresholded success is not supported but line
27 then requests `top_k_success`; its meaning (top-k hit containing the
observed group optimum vs. an unlicensed binary success threshold) is not
frozen.

**Minimal repair:** either define an exclusive ternary direction target
(`delta < -10`, `abs(delta) <= 10`, `delta > 10`) or make sign and invariance
two separately named tasks/labels with separate metrics.  Rename and define
recommendation hit rate as e.g. `top_k_contains_group_optimum` (including the
tie policy) so it cannot be interpreted as a success-threshold label.  Retain
thresholded success classification as `not_supported`.

### P0-5 — mandatory metrics and their edge behavior are incomplete

Goal lines 323–328 require sensitivity ratio, within-group variance ratio, and
factor-wise sensitivity, none of which appears in ADR 0006 or contract line
27.  “Constant” is a single blanket `not_supported` value even though MAE/RMSE
remain defined for constant labels/predictions.  The contract also does not
specify: R2/Pearson/Spearman minimum n and constant-target behavior; metric
direction/averaging and absent-class policy for macro-F1; AUPRC/AUROC/F1
positive label and zero-division behavior; NDCG gain/discount and `k`; top-k
values; group weighting; or exact tie policy (average ranks and deterministic
tie-breaking are different operations).  `single_class_cliff` is insufficient
to cover direction class imbalance and recommendation/ranking degeneracy.

**Minimal repair:** enumerate the missing required metric families and provide
per-metric `formula_or_library_semantics`, `eligibility`, `minimum_n`,
`constant_truth`, `constant_prediction`, `missing_prediction`,
`ties`, `class_imbalance`, `group_aggregation`, and `not_supported_reason`
rules.  Fix a finite `k` list and a deterministic key for ranking/top-k ties.
Specify that cliff AUPRC is the primary class-imbalance metric and retain
AUROC/F1 only with their valid-domain rules.

### P1-1 — test-first/freeze and pair-exclusion artifacts are prose only

ADR 0006 decision 2 correctly forbids use of held-out labels for selection and
requires an exclusion ledger, but the JSON has no required manifest schema for
config/data hashes, record primary keys, pair primary keys, exclusion reasons,
freeze version, rerun hash, or evaluation-only-anchor status.  The goal’s hard
acceptance lines 332, 334, and 338 cannot be verified from the future outputs
without these requirements.  The config’s negative-case strings do not define
test-first validation inputs or required toy/boundary/negative tests.

**Minimal repair:** add `manifest_contract`, `pair_exclusion_ledger_contract`,
and `test_first_policy` sections.  Require seed/config/input hashes, canonical
sorted IDs, per-partition counts, source coverage, deterministic rerun hash,
cross-partition exclusion counts/reasons, `pairs_used_for_training=0`, an
explicit anchor policy (`not_used` unless a new ADR permits it), plus a
version-bump-only test-manifest change rule.  Add required toy/boundary/negative
test case identifiers for every metric and each S0–S5 leakage predicate.

## Review decision

The reviewed ADR/config are a useful protocol outline, but they do not yet
meet the Phase 4 Round A contract gate.  Apply only the contract/ADR edits
above, increment the proposed contract version, validate JSON, and repeat an
independent Round A review before writing any split, metric, prediction, or
model artifact.
