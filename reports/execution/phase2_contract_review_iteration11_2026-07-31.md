# Phase 2 Contract Review — Iteration 11 (Independent)

Date: 2026-07-31  
Reviewer role: independent Phase 2 contract reviewer  
Scope: ADR 0005 and `configs/benchmark_v0_1_group_pair_graph_contract.json` only. This review authorizes no implementation and does not promote Core v0.2.

## Result

**PASS — the three Round A blockers are precisely closed.**

The reviewed contract remains deliberately limited to the strict, discrete Benchmark v0.1 layer. It continues to forbid extended pairs/graphs, splits, and model results.

## Blocker closure checks

| Prior blocker | Independent evidence | Result |
| --- | --- | --- |
| Source-by-factor v0.1 baseline; Perera raw solvent view and reconciliation ledger | ADR 0005 decisions 3 and 6 specify Perera `solvent_1` from `condition_component_refs` through the same-source registry raw entity/value, explicitly reject a pending non-identity mapping, and require endpoint differences from the v0.1 normalized solvent view in the ledger. The config fixes the three Ahneman and three Perera source-factor baseline counts, requires current/intersection/only-on-one-side counts, reason code, and evidence path; unexplained differences hard-fail. | PASS |
| Full universe and hash before delta/cliff; exact threshold semantics and nesting | ADR 0005 decision 4 and `pair_policy.universe_build_order` require eligible manifest → full strict universe → universe hash → delta → labels, with a canonical pre-label hash and an explicit rejection of delta/label filtering. The config encodes primary boundaries (`<=10`, `10<d<30`, `>=30`), `>=20` and `>=40` sensitivity labels, the 10/20/30/40 boundary tests, and `strong_40 ⇒ strong_20`. | PASS |
| Node/edge Parquet and canonical group JSON with pair-to-edge bijection | ADR 0005 decision 5 requires per-group node/edge Parquet and a fixed-schema group JSON. The config fixes node and edge columns, including `pair_id`, ordered endpoints, source/group/version, changed factor, and `canonical_undirected_key`; it defines the canonical key, the JSON keys/schemas, strict pair-edge bijection, and negative tests for duplicate keys, duplicate pair IDs, missing JSON keys, and failed bijection. | PASS |

## Additional contract checks

- Source-design group semantics remain explicit: `reaction_group_id`-derived groups are `source_design_defined`, while scaffold/template inference stays `not_supported` without complete evidence.
- Pair eligibility is still same source, same strict group, observed main-matrix outcomes, no self loops, exactly one changed factor; the Ahneman ligand/catalyst linkage remains metadata rather than a second factor.
- The contract JSON parses successfully with `python3 -m json.tool`.

## Authorization boundary

Phase 2 implementation may now build and validate only the stated Benchmark v0.1 candidate artifacts: eligible-record manifest, complete strict pair universe and pre-label universe hash, reconciliation ledger, strict group node/edge Parquet, and canonical group JSON. It must preserve raw inputs and Core v0.1, keep Core v0.2 candidate status unchanged, and leave extended layers, splits, and models out of scope.
