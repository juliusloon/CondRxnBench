# Phase 1 Round B independent reproduction review — Iteration 9

Date: 2026-07-31  
Role: `independent_reviewer`  
Scope: independent reproduction of the proposed.3 Core v0.2 candidate builder
and verifier, plus adversarial checks of source boundaries, semantic states,
foreign keys, output scope, and promotion claims.  This review did not modify
workspace raw data, Core v0.1, or workspace candidate output.

## Verdict

**PASS — Phase 1 candidate implementation clears the Round B gate.**

The build was executed from a fresh copied worktree at
`/private/tmp/condrxnbench-phase1-review9.XrkpHW/repo`, with output directed
outside that copy to `/private/tmp/condrxnbench-phase1-review9.XrkpHW/candidate`.
It used the pre-existing Phase 0-reviewed CPython 3.11.15 environment with
pandas 2.2.3, PyArrow 17.0.0, and RDKit 2024.03.6.

## Reproduction commands

```bash
/private/tmp/condrxnbench-phase0-review3-py311/bin/python \
  scripts/build_core_v0_2.py \
  --out-dir /private/tmp/condrxnbench-phase1-review9.XrkpHW/candidate

/private/tmp/condrxnbench-phase0-review3-py311/bin/python \
  tests/verify_core_v0_2.py \
  --out-dir /private/tmp/condrxnbench-phase1-review9.XrkpHW/candidate
```

Both commands exited zero.  The verifier printed:

```text
Core v0.2 candidate verification passed: records/controls/side tables; no pairs or benchmark artifacts.
```

PyArrow emitted sandbox-only CPU-feature `sysctlbyname ... Operation not
permitted` warnings; these did not change exit status or validation results.

## Immutable baseline and scope checks

| Check | Result | Evidence |
| --- | --- | --- |
| Raw inputs unchanged | PASS | SHA-256 comparison before/after over all 18 Ahneman and 2 Perera accepted inputs was identical. |
| Core v0.1 unchanged | PASS | `reaction_records.csv`, `condition_pairs.csv`, `condition_registry.csv`, and `manifest.json` hashes were identical before/after. |
| Core cardinality/outcomes | PASS | 9,900 records: Ahneman 4,140 / 4,132 observed / 273 zero; Perera 5,760 / 5,760 observed / 275 zero. |
| Historical pairs preserved but not regenerated | PASS | Manifest records the 116,156-pair v0.1 hash as a baseline and `included_as_output=false`; candidate directory has no pair file. |
| No graphs/splits/labels/models | PASS | Candidate contains records, controls, and six side-table CSV/Parquet pairs only; filename scan found no forbidden artifact. |
| Candidate promotion status | PASS | Manifest is `candidate_not_promoted`; scope and `unimplemented_by_design` explicitly exclude v0.2 pairs, graphs, splits, labels, and model results. |

## Standardization-boundary checks

| Boundary | Result | Independent observed evidence |
| --- | --- | --- |
| Ahneman structure allowance | PASS | Exactly 16,560 `source_reported` assertions (`4 × 4,140`), with roles only `substrate_1`, `ligand`, `base`, and `additive`; all parse/sanitize successfully and retain normalized/canonical SMILES and InChIKey. |
| Perera no fabricated structure | PASS | All 63,360 Perera assertions are `parse_sanitize_status=not_supported`; their normalized/canonical/InChIKey fields contain zero non-null values. |
| Unsupported feature behavior | PASS | `not_supported` assertions also record ECFP4 and reaction-centre feature status as `not_supported`; no pseudo-feature is produced from absent structures. |
| Source/role-scoped record FKs | PASS | The verifier resolves every `condition_component_refs` entry to exactly one registry row with matching `source_dataset` and role. Its negative tests reject a Perera ligand in an Ahneman reference and an Ahneman ligand as a base reference. |
| Explicit condition/null semantics | PASS | Registry has only `explicit_component` or `explicit_null_component` states; it contains the two expected Perera `NULL_COMPONENT` entities (ligand and base), and no `not_reported` entity. |
| Continuous typed state | PASS | 108,900 rows (`9,900 × 11`): 51,360 `observed_numeric`, 480 `NA`, and 57,060 `not_reported`. Non-observed numeric values are Arrow null; an `NA` row exists and cannot be interpreted as zero. |
| Observed-zero semantics | PASS | All records satisfy `zero_yield == yield_observed && yield_percent == 0`; zero totals are Ahneman 273 and Perera 275. |
| Mixture/mapping guard | PASS | 11,520 composition rows retain the Perera 9:1 organic/water ratio (two rows per record). The two legacy non-identity solvent mappings are explicitly `pending`, have evidence fields, and are not used by the raw-source record references. |

## Contract and storage checks

The builder and verifier are consistent with ADR 0004 and
`configs/core_v0_2_contract.json` proposed.3: v0.1/raw remain immutable,
Perera has no allowed condition structure role, source/role FK resolution is
enforced, continuous `value_state` is closed, and discrete role references are
complete.  The verifier checks each candidate CSV/Parquet pair against its
manifest schema fingerprint, column ordering, primary-key order/uniqueness,
row count, null/state representation, literal tokens, canonical JSON values,
and measurement semantics.

## Promotion boundary

This PASS supports only the **Phase 1 Round B candidate implementation**.
Core v0.2 itself remains `candidate_not_promoted`.  Phase 1 promotion still
requires the prescribed mapping/role sampling and independent Round C review;
it does not authorize pair/graph rebuilds, benchmark splits, labels, or model
work.
