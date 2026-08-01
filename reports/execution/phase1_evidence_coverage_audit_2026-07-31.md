# Phase 1 evidence coverage audit — 2026-07-31

Role: `evidence_auditor`.  This is a read-only audit of the current
`CondRxnBench-Core-v0.1` candidate and the two vendored source snapshots.  It
does **not** modify raw data, build a mapping, assign a structure, or approve
the Phase 1 implementation.

## Verdict

**Phase 1 evidence contract: FAIL — Core v0.2 promotion is blocked.**

The current Core v0.1 is an internally consistent, source-aware regression
baseline, but it intentionally lacks the raw/normalized structure and unit
layers, mapping-level evidence/reviewer status, structure QC/disposition, and
an explicit `NA` state required by the Phase 1 hard acceptance.  It must not
be relabelled as Core v0.2 on the basis of the existing v0.1 verification.

Two safety boundaries are confirmed:

1. Ahneman's vendored `smiles/*.csv` files are source evidence for the
   **aryl-halide, additive, base, and ligand-component** structures.  They
   support a future evidence-backed mapping, not a claim that a ligand SMILES
   is the structure of a pre-formed `catalyst_system`, and not an inferred
   product or atom mapping.
2. Perera's vendored workbook has names/short-hands and no machine-readable
   structure column; its PDF supplies general experimental context but no
   complete row-level substrate/product mapping.  Its currently
   `not_reported` substrate/product SMILES must remain so.  Do not draw from
   names, figures, or reaction intuition to fill them.

## Inputs and commands

Audit inputs:

- `data/processed/core_v0_1/reaction_records.csv` (9,900 records)
- `data/processed/core_v0_1/condition_registry.csv`
- Ahneman source snapshot: `SOURCE.md`, two layout files, twelve LC/UV
  exports, and four `smiles/*-list.csv` files
- Perera source snapshot: `SOURCE.md`, `aap9112_Data_File_S1.xlsx`, and
  `aap9112_perera_sm.pdf`
- source cards and source-evidence notes named below

Commands executed:

```bash
python3 tests/verify_core_v0_1.py
python3 - <<'PY'
# profile source-specific available/not_reported/blank counts in reaction_records.csv
PY
python3 - <<'PY'
# read Data File S1 and profile its 16 columns, literal None levels, and outcome values
PY
```

The verifier passed: 9,900 unique records and 116,156 strict pairs.  This is
support for the v0.1 baseline only; it does not test the v0.2 requirements
listed in the verdict.

## Record identity and provenance coverage

| Source | Records | `source_dataset` + `source_record_id` | provenance | Result |
| --- | ---: | --- | --- | --- |
| Ahneman–Doyle | 4,140 | 4,140 / 4,140 | 4,132 raw LC/UV paths; 8 have the explicit `<reaction_id>:missing_analysis_export` source-ID sentinel and `provenance_path=not_reported` | PASS for the stated Phase 1 provenance alternative; no provenance was fabricated |
| Perera | 5,760 | 5,760 / 5,760 | 5,760 point to `aap9112_Data_File_S1.xlsx:Sheet1` and retain `Reaction_No` as `source_record_id` | PASS |

## Structure evidence coverage

`available` below means a non-sentinel Core cell, not successful RDKit
parsing.  No RDKit parse/sanitize claim is made in this audit.

| Source | `substrate_1_smiles` | `substrate_2_smiles` | `product_smiles` | Evidence and interpretation |
| --- | ---: | ---: | ---: | --- |
| Ahneman–Doyle | 4,140 available (15 unique) | 4,140 `not_reported` | 4,140 `not_reported` | The aryl-halide values exactly originate from vendored `smiles/aryl_halide-list.csv`.  The raw snapshot has no row-level machine-readable p-toluidine/product table, product SMILES, atom mapping, canonical reaction, or bond-change evidence. |
| Perera | 5,760 `not_reported` | 5,760 `not_reported` | 5,760 `not_reported` | Data File S1's 16 columns contain names and short-hands, but no SMILES.  The vendored PDF does not provide a complete importable row-level structure mapping. |

The current registry stores `structure_smiles=not_reported` for every entity,
including all 23 Ahneman additives, 3 bases, and 4 ligand components for which
the raw snapshot does have SMILES.  This is a recoverable v0.2 evidence gap,
not permission to set `catalyst_system` equal to a free-ligand structure.

The following required v0.2 structure controls are absent and therefore
**FAIL**: raw/normalized separate fields; canonical SMILES/InChIKey; parse and
sanitize result/status; error class/raw value/source/disposition for every
failure; and `available/not_supported/failed` status for Murcko, ECFP4/6,
DRFP, and reaction-center features.  Accordingly the ≥99% parse/sanitize gate
has not been evaluated and cannot be inferred from the apparent coverage.

## Condition roles, explicit-null state, and units

| Source | Available discrete roles in every record | `not_reported` roles | Explicit-null evidence | Unit/continuous coverage in Core |
| --- | --- | --- | --- | --- |
| Ahneman–Doyle | `catalyst_system`, `ligand`, `base`, `additive` (4/4/3/23 levels) | `catalyst`, both solvents, atmosphere, vessel and every continuous field | none in the main matrix | all `temperature_c`, `time_h`, `concentration_m`, loading/equivalence etc. are `not_reported` |
| Perera | `catalyst`, `ligand`, `base`, `solvent_1`, `solvent_2`, atmosphere; fixed temperature/residence time/pressure/scale and declared equivalents | `catalyst_system`, additive, vessel, time and concentration | raw literal `None` is preserved as `NULL_COMPONENT`: 480 ligand records and 720 base records | column suffixes express target units, but Core has no per-field `raw_value`, `raw_unit`, conversion record, mapping evidence, or reviewer status; 480 null-ligand records have blank `ligand_equiv`, not an explicit `NA` state |

Perera Data File S1 directly supports 5,760 unique `Reaction_No`, 12 ligand
settings including the 480 literal `None` cells, 8 base settings including 720
literal `None` cells, and six original carrier-solvent labels.  The current
processing preserves the original solvent labels outside Core and reduces
`MeOH/H2O_V2 9:1` and `THF_V2` to four standardized `solvent_1` labels.
The evidence note identifies the mapping, but the Core registry records only
generic `evidence=core_v0_1_processed_record`, no source locator or reviewer
status.  That fails the Phase 1 requirement that every non-identity
name/role/unit mapping have evidence and reviewer status.

`NULL_COMPONENT`, `not_reported`, and a true numeric-field `NA` are not yet a
three-state data contract.  The first two have distinct values in Core; the
third is represented as a blank CSV cell (notably `ligand_equiv` for the
explicit no-ligand experiments).  A v0.2 automatic test for
`NULL_COMPONENT != not_reported != NA` therefore cannot pass from the current
schema alone.  The 480 blank `ligand_equiv` values must not be silently
converted to zero.

## Outcome semantic coverage

| Source | Observed | missing | observed zero | Raw measurement/semantic protection | Result |
| --- | ---: | ---: | ---: | --- | --- |
| Ahneman–Doyle | 4,132 | 8 | 273 | `yield_observed`, `zero_yield`, `yield_type=lc_uv_product_scaled_percent`, `measurement_method=per_well_LC_UV_internal_standard_corrected`, and raw `product` signal are retained for observed rows | PASS for 0 vs missing; the 8 missing raw values are blank and identified by the boolean/sentinel, not reclassified as zero |
| Perera | 5,760 | 0 | 275 | `yield_type=lc_ms_uv_area_percent_reported`, `measurement_method=UPLC-MS/DAD; UV area percent`, and raw `Product_Yield_PCT_Area_UV` are retained | PASS for observed/zero semantics; this is not isolated yield |

Neither source provides a current `not_detected` outcome category.  Its absence
must be represented as unsupported/not present in the evidence, not as a
synonym for either zero or missing.  The present fields distinguish observed
zero and missing, but v0.2 still needs a specified raw/normalized outcome
schema, range-exception audit, eligibility distinct from quality grade, and a
test suite covering all four relevant states (`0`, missing/`NA`,
`not_reported`, and `not_detected` where applicable).

## Evidence recoverable from vendored sources but not yet in Core v0.1

These are an evidence inventory only.  No mapping is implemented or approved
by this report.

1. **Ahneman condition-component SMILES.**  The four vendored lists provide
   15 aryl-halide, 23 additive, 3 base, and 4 ligand-component SMILES.  Core
   carries only the aryl-halide structure; the registry carries none.  A
   future mapping must preserve raw string, source file/component key, and
   review status, and keep the pre-formed Pd--ligand `catalyst_system` atomic
   unless separate complex evidence is supplied.
2. **Ahneman analytical raw fields.**  The LC/UV export reconstruction keeps
   `product`, `internal_standard`, and `corr_factor`; Core carries only the
   raw product signal as `measurement_value_raw`.  The two other fields can
   be preserved as source-measurement evidence, not promoted to yield labels.
3. **Perera raw-label dual fields.**  Data File S1 supplies raw reactant
   short-hands, raw ligand/base `None` strings, original six solvent labels,
   and all 16 original columns.  The derived source table already records
   several raw/normalized pairs, but Core drops them.  A v0.2 raw/normalized
   layer can retain them with source locators.
4. **Perera ancillary instrument signal.**
   `Product_Yield_Mass_Ion_Count` is present for every Data File S1 record and
   exists in the source-derived table, but is not Core.  It may be preserved
   as an ancillary raw measurement; it is explicitly not a second yield
   label.
5. **Perera shared operating metadata.**  The vendored SI documents 1 mL/min
   flow, 1 uL-per-component injection, approximately 45 s segments, and the
   source-derived table has these fields.  They are absent from Core.  They
   must be recorded as shared/source-page-backed metadata rather than invented
   row-specific logs.

The Ahneman project notes refer to fixed p-toluidine and general reaction
conditions, but the immutable Ahneman raw snapshot presently contains no
vendored paper/SI PDF or page-addressable machine-readable table for those
facts.  Do not add a second substrate, product, solvent, time, temperature,
scale, or loading from the notes alone.  First restore/pin the underlying
source artefact and cite its exact evidence location; product and atom mapping
still require explicit row-level evidence rather than chemical inference.

## Requirement-by-requirement decision

| Phase 1 hard requirement | Evidence status | Decision |
| --- | --- | --- |
| Preserve all 9,900 main-matrix records and source identity/provenance | counts and source IDs verified; Ahneman has 8 permitted missing-export sentinels | PASS (baseline) |
| Preserve observed/missing/zero yield counts and source-aware measurement semantics | counts and boolean/measurement fields verified | PASS (baseline) |
| 100% discrete-condition state coverage; valid/explicit-null conditions >99% | all populated design-role cells are covered; Perera null levels are explicit | PASS for current role availability, not v0.2 registry evidence |
| `NULL_COMPONENT != not_reported != NA` automatic tests | no explicit `NA` representation/schema or test | FAIL |
| ≥99% parse/sanitize among declared parseable structures; all failures dispositioned | no v0.2 normalized structures, parse run, or failure ledger | FAIL / not evaluated |
| All non-identity role/name/unit mappings have source evidence and reviewer status | registry has only generic processed-record evidence and no reviewer field | FAIL |
| raw/normalized fields, unit conversion preservation, and source-located unit evidence | absent from Core; raw values/units are not systematically retained | FAIL |
| 100% structural-failure/error-class disposition; feature availability states | absent | FAIL |
| source-backed exclusions rather than deleting records | v0.1 retains all records and explicit sentinels | PASS (baseline) |
| schema/dictionary/card/ADR synchronized with v0.2 implementation | current documents describe v0.1 only | FAIL pending implementation |

## Handoff: allowed next hypothesis

Before implementation, freeze a v0.2 schema/ADR that (a) makes raw,
normalized, `not_reported`, explicit-null, and numeric `NA` states distinct;
(b) specifies evidence locator and reviewer-status fields for every mapping;
and (c) classifies Ahneman component-list SMILES as condition-component
evidence without decomposing `catalyst_system`.  The maker can then implement
only that contract and must submit it to an independent mapping audit before
promotion.
