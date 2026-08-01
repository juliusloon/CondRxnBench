# Phase 5 Round A — Proposed.2 Baseline Experiment Contract Independent Review (Iteration 27)

## Verdict

**FAIL — substantial P0 progress, but the contract still does not authorize
baseline training or predictions.**

The JSON is valid and no model/prediction/leaderboard artifact exists.  Proposed.2
closes much of Iteration 26, but three remaining contract ambiguities can still
change experimental evidence after test manifests are known.

## Resolution of Iteration 26 findings

| Prior finding | Result | Evidence |
| --- | --- | --- |
| P0-1 source × family eligibility | PARTIAL PASS | Closed `family_eligibility` now covers both sources and all eight families; both structural families are explicitly not supported, and Perera has no reaction/descriptor proxy.  However ADR 0007 remains **Proposed**, while the goal requires an **Accepted ADR** for the six-family fallback.  Eligibility evidence is prose, not a versioned evidence path/feature-source reference. |
| P0-2 winner freeze/test-first | PARTIAL PASS | Seeds, candidate grids, val metric/tie-break, run ID template, and winner-freeze fields are now present; group lookup fallback is fixed.  `freeze_sha256` is required but its canonical bytes/scope are not defined, making a self-referential field impossible to reproduce unambiguously. |
| P0-3 result/failure/control schemas | PARTIAL PASS | Prediction, run, failure, negative-control and leaderboard schemas, plus Task 2–6 adapters, are substantially better.  The contract never requires the three negative controls for each formal source×split (and declares no seed/family coverage policy), so a later runner can omit a control without violating a machine rule. |
| P0-4 feasibility/source/environment binding | PARTIAL PASS | Feasibility v3 SHA-256, 64/20 expected statuses, requirements SHA-256, source-only absolute aggregation, and clean reproduction requirement are now bound.  Features are only labels such as `source_specific_condition_components`; no encoder/category/unknown handling, target transformation, feature-config path/hash, or implementation code hash is frozen. `feature_code_version` is not a content hash. |

## Blocking corrections

### P0-1 — accept and evidence-bind the structural fallback

ADR 0007 decision 6 supplies the correct six-family rationale, but its state
is `Proposed` (line 5).  The goal’s Phase 5 hard acceptance calls specifically
for an Accepted ADR when structure evidence makes families ineligible.  Add
the accepted status only after this Round A gate, and bind each structural
`not_supported` leaf to a repository evidence path (for example the applicable
Phase 1 evidence audit/structure assertion coverage) and source data version.

### P0-2 — make winner freezing and control coverage executable

Define `freeze_sha256` as the SHA-256 of a canonical winner payload **excluding
the hash field itself**, name its JSONL ordering, and require the manifest of
all winner rows to be hashed before test access.  Add a closed
`negative_control_coverage` rule requiring constant, shuffled-y-train-only,
and shuffled-condition-train-only for every source×supported split×seed (or
explicitly fix and justify a smaller independent coverage unit); require a
ledger entry for every required cell.

### P0-3 — freeze concrete feature semantics, not feature labels

Add versioned feature-config artifacts with SHA-256 and explicit:

- source-specific component extraction from raw/source-scoped
  `condition_component_refs`, ordered role views, categorical encoder and
  unseen-category behavior;
- group/condition lookup keys and train-only fallback recording;
- full-categorical group encoding and S2 unseen-group behavior;
- target scale/unit and any transform/inverse-transform rule; and
- feature implementation file/package hash.

Bind that feature-config hash to run ID, winner freeze, prediction rows, and
the clean-reproduction validator.  This is necessary to prevent an after-test
feature implementation change, and to ensure Perera cannot be given synthetic
structure columns through an unstated encoder.

## Positive regression checks

- `benchmark_v0_1_baseline_experiment_contract.json` parses.
- Contract pins feasibility matrix SHA-256 `d17b1e32…21f5aa` and requirements
  SHA-256 `cf9291fb…d11ba0`, both independently matched.
- Matrix v3 is 84 leaves with 64 `supported` and 20 `not_supported`.
- `git diff --check` is clean; no baseline prediction, model, leaderboard, or
  result file was found in the reviewed output paths.

## Review decision

Revise ADR/config only for the three P0 corrections, then repeat Phase 5 Round
A.  No training, prediction, metric computation, leaderboard, or baseline
promotion is authorized by this FAIL.
