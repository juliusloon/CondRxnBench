# Phase 4 Round A — Proposed.3 Independent Contract Review (Iteration 15)

## Verdict

**FAIL — do not materialize S0–S5 splits.**  Proposed.3 repairs several
previous ambiguities, and the feasibility artifact has 84 syntactically
complete leaves, but contradictory feasibility states and incomplete
metric/evidence binding still make the protocol non-deterministic at the
contract level.

This review was read-only.  The contract parses as JSON; the feasibility matrix
contains 84 leaves with all six required leaf fields; and its recorded Core and
Benchmark manifest hashes equal the current manifest SHA-256 values.  No split
or model artifact was written by this review.

## Checks against the prior blockers

| Check | Verdict | Evidence |
| --- | --- | --- |
| 84 source × task × split leaves exist | PASS | `metadata/benchmark_v0_1_task_split_feasibility_matrix.json` has exactly 84 leaves (`2 × 7 × 6`).  Every leaf has `status`, `reason`, `evidence_path`, `minimum_eligible_records_or_pairs`, `nonempty_expectation`, and `materialization_disposition`. |
| Input-manifest hashes are current | PASS | Matrix `core_manifest=101e9…f05e2` and `benchmark_manifest=790662…8e33` match the current two manifest files. |
| Leaf-specific feasibility/evidence is sufficient | FAIL | Every leaf uses the same two broad CSV paths, global observed-record count, global strict-pair count, and a generic reason.  The builder merely hard-codes task/split status from task name and split (`scripts/build_task_split_feasibility_matrix.py:24–35`), without measuring task eligibility, S1 candidate-set size, S2/S3/S4/S5 predicates, class balance, or the future same-partition pair count.  In particular, supported Task 5/6 S1 leaves specify `minimum_eligible_records_or_pairs=1` although their contract eligibility requires a candidate set of at least 2. |
| Contract and leaf feasibility agree | FAIL | `task_split_feasibility` remains source-free and conflicts with the new leaves: both sources mark Task 2/3/4 S2 as `limited` in the contract but `supported` in the matrix; Task 5/6 non-S1 cells are `limited` in the contract but `not_supported` in the matrix.  Two competing truth sources cannot guide materialization. |
| S0–S5 selection, role, NULL, val/test isolation | MOSTLY PASS | Contract line 28 now fixes hash ordering, S0 allocation, S1/S2 partition rules, deterministic S3 role selection, literal NULL eligibility, S4 tuple logic, and disjoint val/test component/tuple/group sets.  Before a PASS, tuple/component identifiers must explicitly be extracted from the source-scoped `condition_component_refs` / raw factor view used by the strict-pair contract, so Perera cannot silently fall back to an unaccepted normalized solvent mapping. |
| Task 2/4/5/6 semantics | PARTIALLY PASS | Contract line 27 now fixes direct Task 2 Δ prediction, Task 4’s `cliff_label_primary == strong`, Task 5 ranks and ties, and Task 6 optimum ties/regret.  However the Task 2 metric list still includes `within_group_variance_ratio`, whose formula needs `predicted_yield`; a direct pair-Δ prediction supplies no such value.  It must either move to a stated endpoint-yield adapter/Task 1 view or declare its prediction construction and eligibility. |
| Sensitivity/regret formulas and fixtures | FAIL | Sensitivity and regret formulas were added (contract line 32), but fixture coverage is not yet “every metric” and no verifier consumes it. `tests/fixtures/metrics_v0_1_toy_cases.json` lacks numeric expected results for MAE/RMSE/correlations, direction accuracy/macro-F1, AUPRC/AUROC/F1, NDCG/top-k, factor-wise sensitivity, variance ratio, and regret.  A fixture declaration without executable tests cannot satisfy the goal’s toy/boundary/negative-test requirement. |
| Cross-partition pair-training semantics | PASS | Contract line 31 correctly narrows the invariant to `cross_partition_pairs_used_for_training: 0` and permits same-partition Task 2–4 training. |

## Blocking corrections

1. **Use one canonical feasibility matrix.**  Remove or mark the old
   `task_split_feasibility` object as deprecated/non-authoritative, then make
   the 84-leaf file the only materialization input.  Fix all current conflicts
   before release.  The builder must read the proposed contract rather than
   independently hard-code task/split status.

2. **Make each leaf evidence-bearing, not a global-count template.**  Record
   per leaf the exact eligible record/pair/candidate-set count, class support
   when applicable, source/group/factor evidence query or reproducible command,
   and the evaluated predicate.  Set Task 5/6 S1 minimum eligibility to at
   least two observed candidates.  Do not label a selection-dependent cell
   `supported` until its stated feasibility predicate has actually been
   evaluated; otherwise retain `limited` with a clear no-score disposition.

3. **Bind matrix provenance to the contract.**  Add `config_sha256` (and
   preferably builder SHA/version) to the matrix and validate it in the
   builder/verifier.  The two input manifest hashes are correct, but a changed
   proposed contract currently leaves a stale matrix indistinguishable from a
   current one.

4. **Resolve Task 2 variance-ratio incompatibility.**  Either define it for
   an endpoint-yield prediction adapter (including endpoint grouping and
   predictions), or remove it from direct-pair Task 2 and assign it to the
   appropriate endpoint-yield task.  Make its fixture test the chosen formula.

5. **Add executable metric and selection-contract tests.**  Implement a
   verifier consuming the versioned fixture file and asserting expected
   numerical/`not_supported` outputs for every required metric.  Add negative
   split fixtures for S0–S5, including Perera raw-source tuple identity,
   NULL_COMPONENT, val/test entity overlap, cross-partition pair use, config
   hash mismatch, and the 84-leaf completeness/consistency invariant.

## Positive findings

- The proposed.3 task objects now name concrete Core/Benchmark artifacts and
  make Task 2 direct prediction vs. endpoint adapter explicit.
- Direction is exclusive, cliff positive is frozen, and recommendation hit is
  explicitly a group-optimum hit rather than an invented success threshold.
- S0/S1 allocation and S3/S4/S5 val/test separation are much more precise than
  in proposed.2.
- Current matrix input hashes were independently recomputed and matched.

## Review decision

Revise only ADR/config/feasibility-builder/fixture-verifier contract work for
the five blockers above, bump the proposed version, and repeat Round A.  No
formal split, metric result, prediction, baseline, or benchmark promotion is
authorized by this FAIL.
