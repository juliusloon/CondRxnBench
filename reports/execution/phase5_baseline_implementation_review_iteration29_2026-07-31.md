# Phase 5 Round B — Baseline Candidate Implementation Independent Review (Iteration 29)

## Verdict

**FAIL — do not accept the baseline candidate, compute a leaderboard, or promote any result.**

This was a read-only review. No model was rerun and no result artifact was changed. The candidate has the expected scale and several strong safeguards, but three P0 provenance/audit defects violate the accepted experiment contract.

## Independent observations that pass

| Check | Result | Evidence |
| --- | --- | --- |
| Contract/hash binding | PASS | Candidate contract SHA-256 is `12700b5f…416fca`; feature-config SHA-256 matches; split manifest SHA-256 and environment/feature artifacts are recorded. |
| Formal/control run counts | PASS | `run_ledger.parquet` has 324 rows: **216** formal (`2 sources × 6 splits × 3 seeds × 6 supported families`) and **108** actual controls (`2 × 6 × 3 × 3`). The negative-control ledger has 108 unique source×split×seed×control entries. |
| Six-family structural boundary | PASS in training behavior | Both structural families are absent from formal runs; each source has 18 runs for exactly six non-structural families. No Perera structural/descriptor model was materialized. |
| Prediction schema and test partition | PASS | 239,652 prediction rows have every required prediction-schema column; all are `partition=test`; 159,768 are formal and 79,884 are control predictions. |
| Train/val selection code path | PASS in local logic | Candidate grids are scored on `val`; winner selection uses `(val MAE, candidate ID)`; a test prediction is computed only after an in-memory winner row is constructed. Numeric test yields do not enter the selection branch. |
| No premature result promotion | PASS | Manifest status is `candidate_not_promoted`; it lists no leaderboard/metric output. |

## P0-1 — winner manifest hash violates the frozen contract

The contract defines `winner_freeze.manifest_hash` as SHA-256 of canonical newline-joined **row-hash values** in JSONL order. Independently recomputing that value from all 216 correctly ordered `freeze_sha256` values produces:

```text
c02ebfe1dd06ddecd2a76737cfb6e08ecd5ef8cd079acfb5f838ae5c6da9d8fb
```

The candidate manifest instead records:

```text
6be2a06628b5174845a0a62eaf76c502d227efd73f4e498adcd695580877c26e
```

which is the SHA-256 of raw `winner_freeze.jsonl` bytes. The two definitions are not interchangeable. This is a direct provenance mismatch, even though each individual row hash correctly excludes its own `freeze_sha256` field.

**Required repair:** compute and store the contract-defined newline-joined row-hash manifest value, and add a verifier that rejects byte-hash substitution.

## P0-2 — winner rows are not persisted/frozen before test access

The runner appends a winner to an in-memory list (line 89), immediately trains on train+val and predicts test (lines 90–94), and writes `winner_freeze.jsonl` only after all source/split/seed/family runs finish (lines 112–113). There is no runtime test-access check against a persisted winner-freeze manifest, despite the contract’s `test_prediction_requires_matching_freeze_sha256` condition.

**Required repair:** materialize and hash the ordered winner-freeze manifest before any test prediction step, load/validate the matching row hash for each test run, and make the verifier prove that sequence. A later failure/restart must not allow test predictions to exist without a prior frozen winner artifact.

## P0-3 — contract-required N/A/failure audit artifacts are absent

The runner silently `continue`s over structural `not_supported` families (line 75). It emits no `not_supported` run/leaderboard ledger rows with the source-specific evidence reason, contrary to the contract’s `unsupported: emit_reason_not_score` rule and the goal’s requirement that each leaderboard cell carry a result, N/A reason, or failed-with-log. It also emits neither an empty versioned `failure_ledger` nor any verifier-visible failure schema. The candidate contains only prediction, run, control, winner, and manifest files.

**Required repair:** write an explicit N/A ledger/result row for all four source×structural-family leaves, reference their frozen evidence paths/reasons, and always materialize `failure_ledger` (empty when no failures) with its declared schema. If leaderboard calculation is deferred, write a versioned pending/result-status ledger rather than silently omitting cells.

## P1 — run ID implementation should be verified against the contract

Formal/control IDs are generated from ad-hoc dictionaries rather than a shared implementation of the specified canonical run-ID payload. Control IDs omit contract/split/feature/family/candidate hash fields. Add a shared run-ID function and verifier for formal and control rows to prevent future provenance drift.

## Review decision

Repair the three P0 defects (and preferably P1) without changing the frozen experiment semantics, then rebuild the candidate and repeat Round B/Round C verification. No leaderboard, baseline promotion, or Phase 5 completion is authorized by this FAIL.
