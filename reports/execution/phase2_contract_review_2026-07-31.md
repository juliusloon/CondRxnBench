# Phase 2 Round A contract review

Date: 2026-07-31  
Role: `independent_reviewer`  
Scope: ADR 0005 and `configs/benchmark_v0_1_group_pair_graph_contract.json` only. No benchmark artifact was built or modified.

## Verdict

**FAIL — do not implement Benchmark v0.1 pairs or graphs yet.**

The source-design grouping boundary is sound: `design_group_id` and `strict_reaction_group_id` are not claimed to be structure verified; Perera scaffold/template groups are correctly `not_supported`; Ahneman treats ligand as linked metadata rather than a second factor of a `catalyst_system` perturbation. Primary cliff bins are also complete: invariant `<=10`, moderate `>10 && <30`, strong `>=30`.

## Blocker 1 — factor-view regression cannot be proven

The contract freezes only the total 116,156 v0.1 pair count. It must freeze the source-by-factor baseline and require a reconciliation ledger:

| Source | factor | v0.1 count |
| --- | --- | ---: |
| Ahneman | catalyst_system | 6,187 |
| Ahneman | base | 4,124 |
| Ahneman | additive | 45,365 |
| Perera | ligand | 31,680 |
| Perera | base | 20,160 |
| Perera | solvent_1 | 8,640 |

Core v0.2 retains Perera raw solvent labels while v0.1 pairs use its four-level normalized `solvent_1`. The config says only `solvent_1`; it never freezes raw versus v0.1-compatible normalized value view. A builder can change pair identity/counts while retaining the aggregate total. Require a factor-value view per source/role, source-factor baselines, current counts, pair-ID differences, reason code, and hard failure for unexplained differences.

## Blocker 2 — cliff ordering and sensitivity boundaries are incomplete

The config has no machine invariant that full eligible pair-universe enumeration precedes delta/cliff labeling, no universe/config hash, and no negative case for labeling a filtered or high-delta-selected subset.

Sensitivity thresholds 20 and 40 also lack explicit `>=`/`>` semantics, required boolean/nesting behavior, and boundary cases. Define `strong_20 = abs_delta_yield >= 20` and `strong_40 = abs_delta_yield >= 40` if that is intended, then add tests at 10, 20, 30, and 40 pp. Primary labels themselves have no overlap/gap, but that does not close the sensitivity gap.

## Blocker 3 — graph format cannot demonstrate edge/pair bijection

`group_json` is named without required JSON keys or a graph schema. No required node/edge Parquet columns are specified. In particular, an edge is not required to carry `pair_id`, both endpoint IDs, group/version IDs, changed factor, or a canonical undirected key. A graph can therefore appear to match endpoints while dropping pair identity or duplicate-edge evidence.

Freeze node and edge table schemas and canonical group JSON: each graph needs group/version IDs and exact ordered node reaction IDs; each edge needs `pair_id`, two endpoints, strict-group ID, changed factor, and canonical undirected key. Add negative cases for duplicate pair/endpoint identity and missing node/edge bijection.

## Minimal revision and boundary

Revise only ADR/config/validation-contract work for the three items above, then repeat Round A. No pair/graph output, cliff labels, split, or model result is authorized by this FAIL.
