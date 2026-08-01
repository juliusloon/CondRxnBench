# Phase 4 Round A — Accepted.2 S5 Clarification Independent Review (Iteration 24)

## Verdict

**PASS — accepted.2 is a valid minimal clarification of the accepted Phase 4
Round A contract.**

This was a read-only review.  No record/pair split candidate was edited,
rebuilt, promoted, or otherwise generated.

## Scope reviewed

The only contract clarification under review is explicit `S5.tuple_roles`.
Accepted.2 now gives S5 the same source-specific tuple roles as S4:

| Source | S4 / S5 canonical tuple roles |
| --- | --- |
| Ahneman–Doyle | `catalyst_system`, `base`, `additive` |
| Perera | `ligand`, `base`, `solvent_1` |

This removes implicit implementation inheritance while preserving the accepted
S5 selection key (`strict_reaction_group_id plus canonical factor tuple`) and
double-OOD predicate.

## Evidence

| Check | Result | Evidence |
| --- | --- | --- |
| Minimal S5 clarification | PASS | `split_policy.S5.tuple_roles == split_policy.S4.tuple_roles`; both sources and role orders match exactly. |
| Accepted status and no protocol widening | PASS | Contract is `CondRxnBench-Benchmark-v0.1-task-split-metrics-accepted.2` with `accepted_for_split_materialization_2026-07-31`.  Seed remains `20260731`; direction/cliff thresholds, task metrics, fixture set, and S0–S5 predicates are unchanged in scope. |
| Matrix provenance | PASS | Matrix config SHA-256 `c0763c55…e56f76b`, Core manifest `101e9d5b…c1f05e2`, and Benchmark manifest `79066267…1c78e33` match independently recomputed current hashes.  Matrix still has all 84 leaves and the required leaf fields. |
| Fixture/metric regression | PASS | Required fixture keys equal actual fixture keys; `tests/verify_metrics_v0_1_toy.py` passes. |
| Input regression | PASS | `tests/verify_phase0_inputs.py` passes (20 raw inputs). |
| Candidate split status | PASS | Existing files under `data/processed/benchmark_v0_1_splits_candidate/` were only inventoried.  They remain unaccepted drafts and are outside this review’s authority. |

## Review decision

The accepted.2 clarification closes the S5 tuple-role ambiguity without
changing the frozen evaluation protocol.  Phase 4 Round B must rebuild split
candidates against accepted.2 before validation; prior split candidates remain
draft evidence only.  This PASS does not promote Benchmark v0.1 or authorize
model training/results.
