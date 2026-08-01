# Phase 5 Round A — Baseline Experiment Contract Independent Review (Iteration 26)

## Verdict

**FAIL — do not train, generate predictions, or compute metrics from the
proposed baseline contract.**

ADR 0007 and `benchmark_v0_1_baseline_experiment_contract.json` establish a
useful outline, but leave several post-test-decidable choices and evidence
gaps.  They are not yet sufficient to make later baseline execution
independently reproducible or to prevent unsupported Perera structure use.

This was a read-only review.  The baseline-contract JSON parses; no baseline
prediction, metric, model, or leaderboard artifact was generated.

## What is already sound

| Requirement | Result | Evidence |
| --- | --- | --- |
| Three fixed seeds | PASS | Contract line 8 fixes `20260731`, `20260801`, `20260802`. |
| Source-aware absolute-yield separation | PASS in principle | ADR 0007 decision 1 and contract line 9 forbid cross-source absolute aggregation. |
| Test-first intent | PASS in principle | ADR 0007 decision 2 and contract line 10 state train/val-only selection and one test evaluation after winner freeze. |
| Eight named baseline families | PASS as an inventory | Contract lines 14–21 lists source/group means, condition Ridge/RF, reaction Ridge, full categorical Ridge/RF, and descriptor RF. |
| Basic resource ceiling | PASS in principle | Local CPU-only, no unapproved GPU/paid service, and at most six hyperparameter candidates per family are stated. |
| Negative-control intent | PASS in principle | ADR 0007 decision 4 and contract line 23 list constant, shuffled-y, and shuffled-condition. |
| Task 7 / Perera no-fabrication intent | PASS in principle | ADR 0007 decision 5 makes Task 7 strata-only; contract line 25 forbids synthetic Perera reaction features. |

## Blocking findings

### P0-1 — no source × family structure-eligibility matrix or accepted fallback

`reaction_only_ridge` and `descriptor_random_forest` have only generic
eligibility strings (contract lines 18 and 21).  They do not state, by source,
which source-backed structure/descriptors exist, their evidence path, parse
criteria, feature version, or explicit `not_supported` reason.  Thus an
implementation can decide after seeing results whether to run a structural
family, or fabricate a Perera proxy despite the broad forbidden string.

The Phase 5 hard acceptance additionally requires an **Accepted ADR** with at
least five independent valid families if structure evidence rules families out
(goal line 370).  ADR 0007 is Proposed and contains no source-by-family
fallback/coverage decision.

**Minimal repair:** add a closed `family_eligibility[source][family]` matrix
with `supported|not_supported`, evidence path/structure fields, feature
version, and required N/A reason.  Explicitly set all Perera reaction-only,
descriptor, and DRFP/reaction-representation families to `not_supported`
unless evidence proves otherwise.  Either preserve eight viable families per
supported leaf, or add an Accepted scope ADR defining the evidence-backed
minimum-five-family fallback before training.

### P0-2 — train/val winner freeze is policy prose, not an auditable artifact

Contract line 10 says a val winner precedes one test run, but specifies no
candidate/run identity, hyperparameter grid serialization, val metric used for
selection, deterministic tie-break, winner-freeze record, or test-access
guard.  `reaction_only_ridge` also has no fixed `alpha` grid, unlike the other
Ridge families.  `group_condition_mean` does not define unseen lookup fallback
or its train-only provenance.

**Minimal repair:** add `run_id` construction and `tuning_contract` fields:
canonical feature/config hash, exact candidate grid (including reaction Ridge),
primary val metric/tie-break, train/val record IDs/config hashes, frozen-winner
manifest, and a verifier rule rejecting test predictions without a prior
winner-freeze hash.  Define train-only lookup fallback for group/condition
mean and record it per prediction.

### P0-3 — prediction, failure, negative-control, and leaderboard schemas are under-specified

`prediction_schema.record_required` has only a minimal point-prediction row.
It omits input/split/feature hashes, hyperparameter/candidate ID, control type,
prediction status, error/log pointer, and result/metric linkage.  Pair/ranking/
recommendation output derivations are described only by prose.  The
`store_failure_logs` boolean does not require a failure table schema; similarly
the negative-control list does not require every source×split×seed/family
coverage.  This cannot prove the goal’s no-unexplained-leaderboard-blank,
failed-with-log, or saved-prediction requirements.

**Minimal repair:** specify versioned schemas for `prediction_records`,
`run_ledger`, `failure_ledger`, `negative_control_ledger`, and `leaderboard`.
Require keys including run/source/split/seed/family/candidate/control/partition,
input/config/feature hashes, status (`completed|failed|not_supported`), N/A or
failure reason/log path, and task metric/result references.  Fix explicit
record-to-pair/ranking/recommendation adapters and prohibit filling failed/N/A
values with zero.

### P0-4 — supported-leaf, source-stratification, and environment binding are not executable

`supported_leaves_only: true` does not identify the v3 feasibility artifact
hash, the 64 supported / 20 not-supported leaves, or task-specific applicable
metrics.  `aggregate: source_stratified_macro_with_seed_mean_and_std` is
ambiguous about whether it creates an impermissible cross-source absolute-yield
score.  Finally, the contract does not bind an environment/requirements hash,
library versions, feature implementation version, command template, or a clean
reproduction validator.

**Minimal repair:** pin feasibility v3 SHA-256 and enumerate/derive the 64
supported source×task×split leaves; require source/yield-type rows as primary
absolute results and label/forbid any cross-source macro accordingly.  Link the
Phase 0 Python requirements/environment record, exact feature code hashes and
versioned command/config, plus a verifier for clean rerun/hash consistency.

## Review decision

Revise ADR/config only for P0-1 through P0-4, increment the proposed baseline
contract, validate JSON, and repeat Phase 5 Round A.  No training, prediction,
metric, leaderboard, or baseline promotion is authorized by this FAIL.
