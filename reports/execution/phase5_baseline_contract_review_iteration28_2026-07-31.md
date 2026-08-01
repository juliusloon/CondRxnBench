# Phase 5 Round A — Proposed.3 Baseline Experiment Contract Independent Review (Iteration 28)

## Verdict

**PASS — the proposed.3 Phase 5 baseline experiment contract passes Round A.**

This was a read-only review.  No model training, prediction, metric result,
leaderboard, or baseline promotion was created.  The PASS permits the parent
workflow to accept ADR 0007 and the corresponding contract before any Round B
implementation work.

## Resolution of Iteration 27 P0 findings

| Prior finding | Result | Independent evidence |
| --- | --- | --- |
| Structural fallback and Perera evidence boundary | PASS | Both sources now have a closed eight-family eligibility matrix: six supported non-structural families and explicit `not_supported` reaction-only/descriptor leaves.  All four structural N/A leaves link to the Phase 1 evidence-coverage audit and Core v0.2 source data version.  ADR 0007 decision 6 supplies the six-family (≥5) fallback; its Proposed state is appropriate until this review passes. |
| Winner freeze and negative-control coverage | PASS | Run identity includes contract, split, feature config, source/split/seed/family/candidate/control values.  Winner-row hash explicitly excludes `freeze_sha256`; JSONL order and canonical manifest-hash semantics are fixed.  Constant, shuffled-y-train-only, and shuffled-condition-train-only are required for every source × supported split × seed, with ledger entries even on failure. |
| Feature semantics/code binding | PASS | Feature config SHA-256 `42bbd4e8…9f225c`, implementation SHA-256 `16dca1a4…b9bef`, requirements SHA-256 `cf9291fb…d11ba0`, and feasibility SHA-256 `d17b1e3…21f5aa` independently match the contract.  The feature config fixes source-scoped condition refs, ordered role tuples, train-only one-hot fitting/unknown behavior, S2 unseen groups, lookup fallback, identity target transform, and forbidden structure/proxy fields. |

## Contract completeness checks

| Requirement | Result |
| --- | --- |
| Eight-family inventory and ≥5 valid-family fallback | PASS — eight families are named; evidence-backed six-family fallback is frozen per source. |
| Three seeds and local resource bound | PASS — three pre-registered seeds, CPU-only/no paid-service, and six-candidate maximum. |
| Train/val-only tuning and one frozen test evaluation | PASS — candidate grid, val metric/tie-break, winner-freeze precondition, and test restriction are explicit. |
| Predictions/failures/controls/leaderboard | PASS — versioned schemas include run/source/split/seed/family/candidate/control/status/hash/log fields; failed/N/A results cannot be zero-filled. |
| Task and adapter boundary | PASS — frozen endpoint-delta/direction/cliff adapters, S1-only ranking/recommendation, no Task 7 head, supported-leaves-only policy, and source/yield-type primary absolute rows. |
| Perera no fabricated structure | PASS — feature config permits source-scoped categorical condition/group data only and declares structure features unavailable; contract explicitly forbids synthetic Perera reaction features. |
| Static/provenance validation | PASS — all referenced paths exist, all declared hashes match, every source has exactly six supported family leaves, all four structural evidence files exist, JSON parses, and no baseline outputs are present. |

## Review decision

Phase 5 Round A is accepted for proposed.3.  The next permitted action is to
mark ADR 0007/contract Accepted and enter **Round B implementation validation**
under this frozen contract.  This PASS does not authorize a claim of completed
baselines, benchmark promotion, or any uncontracted structure feature.
