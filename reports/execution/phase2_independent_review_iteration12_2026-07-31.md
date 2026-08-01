# Phase 2 Independent Review — Iteration 12 (Round B/C)

Date: 2026-07-31  
Reviewer role: independent reviewer  
Result: **PASS**

## Isolation and reproducibility

- Reviewed workspace was copied to `/private/tmp/condrxnbench-phase2-review12.wqGUTp/repo` with any existing `data/processed/benchmark_v0_1` excluded.
- A new candidate was built only at `/private/tmp/condrxnbench-phase2-review12.wqGUTp/candidate`; no workspace Benchmark output was created or changed.
- Runtime: Python 3.11.15, pandas 2.2.3, pyarrow 17.0.0.
- From the copied workspace, the reviewer ran:

  ```bash
  /private/tmp/condrxnbench-phase0-review3-py311/bin/python scripts/build_benchmark_v0_1.py --out-dir /private/tmp/condrxnbench-phase2-review12.wqGUTp/candidate
  /private/tmp/condrxnbench-phase0-review3-py311/bin/python tests/verify_benchmark_v0_1.py --out-dir /private/tmp/condrxnbench-phase2-review12.wqGUTp/candidate
  ```

  The build completed with strict-pair universe hash `b10dae2adfa3e366a229f09016ce43e76217b6c80cd9d4c23b195487da7c2fe7`; the verifier printed its success message.

## Input immutability

File-level SHA-256 snapshots were taken before and after the isolated build, both for the copied inputs and for the original workspace inputs. Every comparison was byte-identical.

| Immutable input | Files | Combined post-check snapshot SHA-256 |
| --- | ---: | --- |
| `data/raw` | 25 | `b5809076de73336be86d78ba1dbb71962b2ff5f14cfdb6b2d6ddc378acafc5c8` |
| `data/processed/core_v0_1` | 4 | `d61c7fd1c30225f1485d4e07aa6f2d6a9bafdfd537ee9f7fffda91ad62ee679d` |
| `data/processed/core_v0_2` | 17 | `600985db611fbbae133370ff1fb4002fac0dca82808229751f6b7683eea7039c` |

## Full-candidate checks

- Strict pair count: **116,156**; all `pair_id` values unique; all endpoints ordered; no self-loop.
- Source×factor counts exactly match the frozen baseline:

  | Source | Changed factor | Pairs |
  | --- | --- | ---: |
  | Ahneman | `catalyst_system` | 6,187 |
  | Ahneman | `base` | 4,124 |
  | Ahneman | `additive` | 45,365 |
  | Perera | `ligand` | 31,680 |
  | Perera | `base` | 20,160 |
  | Perera | `solvent_1` | 8,640 |

- The six reconciliation-ledger rows were independently recomputed from candidate and Core v0.1 endpoint sets. All baseline/current/intersection/current-only/v0.1-only counts match the emitted ledger. The Perera `solvent_1` row is correctly labeled `perera_raw_solvent_identity_preserved`: 8,640 current, 4,032 intersections, 4,608 Core-v0.1-only, and 4,608 current-only endpoint pairs.
- For **all 8,640** Perera `solvent_1` candidate pairs, the two values in `changed_factor_vector` exactly equal the endpoints' `condition_component_refs.solvent_1` registry `raw_value`. No normalized solvent substitute was used.
- Graph materialization is complete: **9,900** unique nodes, equal to all Core v0.2 main-matrix records (4,140 Ahneman + 5,760 Perera); **116,156** unique graph edges; exact `pair_id` edge/pair bijection; no self loop, cross-group endpoint, or duplicate canonical undirected key.
- All 30 group JSON files were parsed. Each includes the fixed graph keys, exact node set, exact edge `pair_id` set, and for every edge the required `pair_id`, ordered endpoints, changed factor, and canonical undirected key matching the Parquet edge row.

## Deterministic stratified pair audit

Sampling rule: within each source×factor stratum, rank pairs by SHA-256 of `phase2-round-bc-iteration12|pair_id`, then inspect the first 40. This selects **240** distinct pairs.

| Stratum | Audited pairs | Identity/group/observed-yield/factor-view checks passed |
| --- | ---: | ---: |
| Ahneman `catalyst_system` | 40 | 40 |
| Ahneman `base` | 40 | 40 |
| Ahneman `additive` | 40 | 40 |
| Perera `ligand` | 40 | 40 |
| Perera `base` | 40 | 40 |
| Perera `solvent_1` | 40 | 40 |
| **Total** | **240** | **240** |

For every sampled pair, the review verified endpoint source and strict group, both observed outcomes, exact Core v0.2 yields and signed delta, exactly one changed source-specific factor, equality of all other factor views, the serialized factor vector, endpoint ordering, and deterministic `pair_id` derivation.

- Pair-level audit accuracy: **100.0% (240/240)**.
- Critical reaction-identity errors: **0**.

## Round B/C decision

The strict Benchmark v0.1 candidate builder and verifier pass independent clean-copy execution and the expanded reconciliation, graph, JSON, and source-aware factor-view audit. The candidate remains unpromoted and intentionally excludes extended layers, splits, and model results.
