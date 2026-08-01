# Phase 4 Round C — Candidate Split Independent Adversarial Review (Iteration 25)

## Verdict

**PASS — the accepted.2 split candidate passes independent implementation and
adversarial-contract review.**

This review did not modify the workspace candidate.  It rebuilt into an
independent temporary directory and verified there.

## Independent reproduction

```text
/private/tmp/condrxnbench-core-v0_2-py311/bin/python \
  scripts/build_benchmark_v0_1_splits.py \
  --out-dir /private/tmp/condrxnbench-phase4-roundc-N5hnAZ

/private/tmp/condrxnbench-core-v0_2-py311/bin/python \
  tests/verify_benchmark_v0_1_splits.py \
  --out-dir /private/tmp/condrxnbench-phase4-roundc-N5hnAZ
```

The verifier passed.  SHA-256 values of the independently rebuilt
`manifest.json`, `record_splits.csv`, `pair_splits.csv`,
`pair_exclusion_ledger.csv`, `record_exclusion_ledger.csv`, and
`split_summary.csv` exactly equal the workspace candidate.  Sandbox-only
PyArrow `sysctlbyname` warnings occurred but did not affect either command’s
success.

## Adversarial checks

| Check | Result | Evidence |
| --- | --- | --- |
| Frozen config/input/seed/provenance | PASS | Candidate records accepted.2 config SHA-256 `c0763c55…e56f76b`, seed `20260731`, and current Core/Benchmark manifest SHA-256 values.  Independent build reproduces those values byte-for-byte for the reviewed artifacts. |
| Matrix status gate | PASS | Feasibility matrix v3 contains 84 leaves: 64 `supported`, 20 `not_supported`; its config and two input hashes match the candidate. |
| S2 group OOD | PASS | Independent verifier checks pairwise disjoint train/val/test `strict_reaction_group_id` sets for each source; no group leakage is accepted. |
| S3 component OOD | PASS | Selected source-specific held-out component entities have zero train overlap for both val and test. |
| S4 tuple OOD and marginals | PASS | Held-out canonical tuples are absent from train, while every held-out role marginal occurs in train. |
| S5 double OOD / diagonal selection | PASS | Only group×tuple diagonal cells are retained; record exclusions use `S5_cross_partition_group_tuple_cell`; retained group and tuple sets are pairwise disjoint across train/val/test. |
| Record and pair ledger coverage | PASS | For every source×S0–S5, records are either assigned or recorded in the record ledger, and every strict pair is either same-partition or in the pair exclusion ledger.  Pair/ledger sets are disjoint and exhaustive. |
| Pair endpoint containment | PASS | Every included pair has equal endpoint partitions equal to its pair partition.  Cross-partition/unassigned endpoints are excluded with one of the two declared reasons. |
| Partition non-emptiness | PASS | All 12 source×split summaries have positive train, val, and test record counts. |
| Test-first selection | PASS | Code inspection finds selection decisions depend on source, reaction/group IDs, `condition_component_refs`, canonical tuples, fixed seed, and the allowed `yield_observed` eligibility flag only.  No branch or selection key accesses numeric yield, `delta_yield`, cliff labels, direction labels, or model output.  Pair membership is assigned only after record partitions are fixed. |
| No premature benchmark/model output | PASS | Candidate manifest remains `candidate_not_promoted` and explicitly lists `model_predictions`, `metric_results`, and `benchmark_promotion` as unimplemented. |

## Review decision

Round C passes for the **split candidate only**.  This evidence supports the
Phase 4 split implementation gate, subject to the root execution record and
any required maintenance updates.  It does not itself promote Benchmark v0.1,
publish model metrics, or authorize baseline training beyond the next
goal-defined gate.
