# Phase 1 schema gap analysis — Core v0.1 → v0.2

**Role:** `standardization_maker` (read-only contract analysis)  
**Date:** 2026-07-31  
**Decision:** proposed contract only. This report neither changes raw inputs nor
creates Core v0.2 records, registry mappings, pairs, graphs, splits, labels, or
model results.

## Scope and evidence inspected

The analysis compares the current Core v0.1 implementation with the
requirements in proposal sections 5–6:

- `docs/Proposal/详细研究计划书.md` §§5.1–5.4 and §§6.1–6.4;
- `configs/core_v0_1_schema.json`, `metadata/unified_schema.md`,
  `metadata/data_dictionary.md`, and
  `metadata/condition_registry/condition_ontology.md`;
- `data/processed/core_v0_1/{reaction_records,condition_pairs,condition_registry}.csv`
  and `manifest.json`;
- `scripts/build_core_v0_1.py`, `tests/verify_core_v0_1.py`,
  `tests/verify_parquet_roundtrip.py`, and proposed
  `adr/0003-core-v0_2-storage-and-runtime-compatibility.md`.

The current release is a sound compatibility baseline, not yet a v0.2
standardization contract:

| Checked item | Current evidence | Consequence for v0.2 |
|---|---|---|
| Core cardinality | 9,900 records: Ahneman 4,140 and Perera 5,760 | Preserve all rows and stable `reaction_id`; do not drop records for training convenience. |
| Outcome states | Ahneman: 4,132 observed / 8 missing / 273 observed zeros. Perera: 5,760 observed / 275 observed zeros. | These counts are conservation gates, not quality filters. |
| Structure evidence in Core records | `substrate_1_smiles` is populated for Ahneman only (4,140 rows, 15 unique strings); `substrate_2_smiles`, `product_smiles`, `atom_mapped_rxn`, `canonical_rxn`, and `bond_changes` are all `not_reported`. | There is no basis to claim a cross-source reaction representation, strict structural group, product structure, atom mapping, or reaction-centre feature. |
| Condition registry | 60 source-scoped rows: 58 `identity_from_source_reconstruction`, 2 `explicit_null_component`; all `structure_smiles=not_reported`; all evidence is only `core_v0_1_processed_record`. | Existing IDs are useful source-scoped anchors, but do not yet document structure, non-identity mapping, precise source locator, or review. |
| Record-to-registry relation | Records retain condition strings, but do not carry component-ID foreign keys or an immutable raw-condition payload. | A future mapping cannot be reproduced/audited only from the records table. |
| Outcome/quality provenance | `yield_type`, `measurement_method`, observed/zero flags and grade B exist; all 9,900 records have the same `manual_review_status`. | Source-aware measurement semantics are preserved, but record-level grade basis, eligibility and review status are not separable. |
| Storage | v0.1 is CSV; the tested temporary round trip proves a candidate path, while ADR 0003 is still Proposed. | Parquet cannot be declared a release contract before the ADR and an explicit Arrow schema are reviewed. |

The two source-scoped registry rows named `XPhos` are **not** treated as the
same entity here. Identical spelling, a recovered structure, or a chemical
name is not by itself authorization to establish cross-source equivalence.

## Minimal additive v0.2 data model

### 1. Preserve the v0.1 table; add only versioned extensions

Publish a new directory, for example `data/processed/core_v0_2/`, rather than
rewriting v0.1 or `data/raw/`. Keep every v0.1 column and value, and add the
following record-level fields:

| Field | Type / allowed state | Why it is minimally required |
|---|---|---|
| `standardization_version` | non-null string | Identifies the frozen rules/config used for this record. |
| `source_artifact_id` | non-null string | Foreign key to a versioned manifest/evidence entry; avoids treating a path string as immutable evidence. |
| `provenance_status` | `direct_source_record`, `missing_analysis_export`, `curated_source_recovery`, `not_assessed` | Makes the eight Ahneman missing-analysis cases explicit without inventing a raw pointer. |
| `condition_component_refs` | Arrow `map<string,string>`; canonical JSON object in CSV | Role → source-scoped `component_id`. It is a foreign-key snapshot, not a cross-source equivalence claim. |
| `condition_raw_values` | Arrow `map<string,string>`; canonical JSON object in CSV | Preserves the literal source/reconstruction value for every represented role, including `None` before its explicit-null mapping. |
| `condition_mapping_version` | non-null string | Binds the two maps to the registry/mapping rule version. |
| `record_qc_status` | `pass`, `warning`, `fail`, `not_assessed` | Separates rule execution from a scientific quality grade. |
| `qc_rule_version` | non-null string | Makes warnings/flags reproducible. |
| `eligibility_status` | `eligible`, `ineligible`, `not_assessed` | Keeps later task-specific filtering out of `quality_grade`; no record is deleted. |
| `eligibility_policy_version` and `eligibility_reason_codes` | string and Arrow `list<string>` / canonical JSON list | States which policy made an eligibility judgment and why. |
| `quality_grade_basis` and `quality_grade_version` | string | Replaces an unauditable blanket grade with its evidence basis; it does not change grade solely because a model cannot consume a record. |
| `duplicate_group_id`, `replicate_id`, `replicate_status` | nullable strings plus `not_assessed` status | Allows replicated/noise evidence only when source evidence supports it. No fabricated replicate identifiers. |

`condition_component_refs` must omit roles that are absent from the source
record rather than manufacture components. `not_reported` is not a registry
entity and must therefore never be a referenced `component_id`.

### 2. Add `record_structure_assertions` instead of widening every role

One row per `(reaction_id, structure_role, assertion_version)` is the smallest
way to retain raw and normalized structure evidence without adding a separate
wide-field family for every current and future role. Suggested primary key is
`structure_assertion_id`; `(reaction_id, structure_role, assertion_version)`
must be unique.

| Field group | Required fields |
|---|---|
| Identity | `structure_assertion_id`, `reaction_id`, `structure_role`, `assertion_version` |
| Raw evidence | `structure_raw_value`, `structure_raw_format`, `source_artifact_id`, `source_locator`, `evidence_id` |
| Normalized representation | `normalized_smiles`, `canonical_smiles`, `inchikey`, `normalization_rule_version` |
| State and audit | `structure_evidence_status`, `parse_sanitize_status`, `error_class`, `curation_disposition`, `review_status`, `reviewer_id`, `reviewed_at`, `review_note` |
| Feature availability | `murcko_status`, `ecfp4_status`, `ecfp6_status`, `drfp_status`, `reaction_center_fp_status`, and one reason/error field per failed status |

`structure_evidence_status` records whether the input is source-reported,
evidence-backed curated, `not_reported`, or rejected. It must not be inferred
from an empty SMILES cell. Feature status is independently limited to
`available`, `not_supported`, or `failed` as required by the goal; the reason
field explains, for example, that a product/mapped reaction is not available.
Canonicalization never overwrites `structure_raw_value`.

Atom-mapped reaction, canonical reaction and bond changes may be emitted only
when their rows carry direct evidence and a reviewed disposition. In this
snapshot they remain unsupported for both sources. Ahneman substrate parsing
may be evaluated separately; it does not validate the unreported Ahneman
product/nucleophile or any Perera structure.

### 3. Evolve the condition registry as entities plus reviewed mappings

Retain current source-scoped `component_id`s. Add the following fields to
`condition_registry`, and place potentially many-to-one operations in a
separate mapping table rather than overwriting a row.

| Registry entity additions | Reviewed mapping additions |
|---|---|
| `registry_version`, `entity_scope` (must include source), `role`, `raw_value`, `normalized_name`, `entity_status` | `mapping_id`, `mapping_version`, `source_component_id`, `target_representation`, `mapping_kind`, `mapping_status` |
| `structure_raw_value`, `normalized_smiles`, `canonical_smiles`, `inchikey`, `structure_status`, `structure_error_class` | `source_raw_value`, `normalized_value`, `rule_id`, `rule_version`, `non_identity` |
| `attribute_name`, `attribute_value`, `attribute_provenance` only for evidence-backed or explicitly marked derived attributes | `evidence_id`, `evidence_source_type`, `source_artifact_id`, `source_locator` (page/table/row when applicable) |
| `created_at`, `supersedes_component_id` only for within-scope versioning | `review_status`, `reviewer_id`, `reviewed_at`, `review_note`, `review_disposition` |

Use `condition_mappings` for all non-identity name, role, unit, structure and
attribute mappings. `mapping_kind=identity` can be recorded compactly by rule
version, but every `non_identity=true` row must have an evidence ID and a
non-pending reviewer status before promotion. A source-scoped mapping must not
become an unscoped entity merely because two strings match. Any proposed
cross-source equivalence needs an explicit mapping row, evidence, and review;
absence of this row means *not equivalent*, not “unknown but usable”.

For mixture solvents, add a one-to-many `condition_compositions` table rather
than compressing components/ratios into a normalized name:
`composition_id`, `reaction_id` or `component_id`, `role`,
`component_component_id`, `raw_label`, `ratio_raw_value`, `ratio_raw_unit`,
`ratio_normalized_value`, `evidence_id`, `mapping_version`, and review fields.
This can retain the Perera organic/water evidence without asserting composition
details for Ahneman's unreported solvent.

### 4. Outcome, missingness and quality extension

Keep the current `yield_percent`, `yield_observed`, `zero_yield`, `yield_type`,
`measurement_method`, and `measurement_value_raw` as the source-aware
compatibility interface. Add:

| Field | Constraint |
|---|---|
| `outcome_observation_status` | `observed_numeric`, `missing_analysis`, `not_detected`, `not_reported`, `not_assessed`; current zeroes remain `observed_numeric` unless the source explicitly says “not detected”. |
| `measurement_value_raw_unit`, `measurement_value_standardized`, `measurement_standardization_status`, `measurement_evidence_id` | Preserve original units/value; a standardized value is only a within-measurement representation, never a cross-source calibration. |
| `measurement_limit_raw`, `measurement_limit_unit`, `censoring_status` | Nullable/`not_reported` unless source evidence exists. Do not infer a detection limit from a zero. |
| `conversion_value`, `selectivity_value`, `product_ratio_value` plus individual observation-status fields | Optional source evidence only; no default zero or copied yield. |
| `outcome_range_audit_status`, `outcome_range_audit_reason` | Out-of-range values are flagged and audited before any correction/exclusion. |
| `uncertainty_value`, `uncertainty_unit`, `uncertainty_type`, `uncertainty_status` | Present only with direct replicate/measurement evidence; missing uncertainty does not turn B into a failed record. |

`quality_grade` describes evidence quality, while `eligibility_status` is a
versioned task/split policy decision. They must be independently testable:
grade B does not imply train eligibility, and ineligibility does not downgrade
or delete provenance.

## Sentinel and null contract (release blocker)

The current documentation states `not_reported` and `NULL_COMPONENT`, but it
does not define the storage-level meaning of `NA`. Therefore no v0.1 value may
be converted to `NA` under this analysis. The following candidate contract
requires an ADR decision before implementation:

| State | Meaning | Storage rule |
|---|---|---|
| `NULL_COMPONENT` | A source reports an explicit no-ligand/no-base (or another explicit empty condition) experimental level. | Literal categorical value plus a registry entity with `entity_status=explicit_null_component`; never Arrow null and never `not_reported`. |
| `not_reported` | The relevant source/evidence does not report the field. It says nothing about chemical absence. | Literal value in applicable textual compatibility columns; never a registry component and never silently replaced with `NA`. |
| `NA` | **Undecided in current Core documentation.** Candidate meaning: typed missing/not-applicable serialization only, never a chemistry entity or reported condition. | In Parquet use a typed Arrow null plus an explicit state column; in the CSV mirror serialize this only as the reserved token `NA`, with quoting/escaping rules that prevent a real raw string from being mistaken for it. |
| Observed zero | A numeric result was observed and equals exactly 0. | `yield_observed=true`, `zero_yield=true`, numeric `yield_percent=0`, and `outcome_observation_status=observed_numeric`; never null, `NA`, `not_reported`, or `not_detected` without direct source evidence. |

The proposed `value_state`/observation-status fields, rather than parser
defaults, are the authority for semantic missingness. CSV readers must disable
automatic conversion of the literal tokens `NA`, `not_reported`, and
`NULL_COMPONENT` before applying this contract.

## Parquet and CSV delivery contract

1. **Formal deliverable:** Parquet files with a versioned Arrow schema for
   `reaction_records`, `record_structure_assertions`, `condition_registry`,
   `condition_mappings`, `condition_compositions` (when populated), and the
   inherited pair table. CSV files are inspection mirrors, not an alternate
   authority.
2. **Typed schema:** IDs and semantic sentinels are UTF-8 strings; flags are
   non-null Arrow booleans; observed numeric outcomes are `float64` (or an
   ADR-approved decimal type); nullable numeric evidence is Arrow null, not a
   string sentinel. Lists/maps remain Arrow list/map in Parquet and canonical
   sorted JSON in CSV. Timestamp fields are UTC ISO-8601.
3. **Manifest:** publish `schema_version`, exact Arrow-schema fingerprint,
   producer/runtime versions, input-manifest hashes, table row counts, primary
   keys, semantic-sentinel counts, and SHA-256 for every delivered file.
4. **Round trip:** read both representations with the release reader, compare
   primary keys/order, row count, columns, booleans, numeric values, null
   states, literal sentinel counts, maps/lists after canonical decoding, and
   source-aware measurement fields. Any difference blocks release.
5. **Compatibility:** v0.1 hashes stay unchanged. The v0.2 manifest must
   state whether each inherited v0.1 field is copied, deprecated-but-copied, or
   represented by an additive side table; no silent replacement of a raw field
   is allowed.

## Required validation invariants for implementation

### Record/outcome preservation

- Exactly 9,900 unique `reaction_id`s; source counts remain 4,140 and 5,760.
- Every record has `source_dataset`, `source_record_id`, and either a direct
  `provenance_path`/`source_artifact_id` or the explicit
  `missing_analysis_export` provenance status.
- Yield conservation must reproduce exactly: Ahneman 4,132 observed, 8
  missing, 273 observed zero; Perera 5,760 observed, 0 missing, 275 observed
  zero. No correction is permitted absent an Accepted bug-fix ADR.
- `zero_yield == (yield_observed and yield_percent == 0)`; observed outcomes
  have a numeric value in [0, 100]. Range flags do not mutate a value.
- `yield_type` and `measurement_method` never become null and are retained in
  all record and outcome views. No validator may pool absolute yields from the
  two source/yield-type strata.

### Sentinel, structure, and registry integrity

- All four sentinel cases in the preceding table have negative tests: a
  `NULL_COMPONENT` is not null/not-reported/`NA`; `not_reported` is not a
  component; `NA` is not a component or observed zero; observed zero is not a
  missing/censored value.
- Every record-to-component reference resolves to exactly one registry row of
  the same `source_dataset` and role. The registry contains no
  `not_reported` entity.
- Every non-identity condition/unit/role/name/structure mapping has an
  evidence locator, a rule/version, and reviewer status. Pending, rejected or
  missing-evidence mappings cannot be treated as accepted normalized facts.
- No cross-source component equivalence may exist without its own reviewed
  mapping. In particular, current same-spelling names must remain separately
  source-scoped by default.
- Every structure assertion with `structure_evidence_status` claiming a
  parseable structure is RDKit parsed/sanitized; success is at least 99% over
  that declared subset. Structure coverage is reported separately by source
  and role. Every failure has raw value, source/evidence, error class and
  disposition.
- Atom-mapped reaction, product, bond-change and reaction-centre features are
  absent/`not_supported` unless their own asserted evidence rows exist; no
  missing structure may yield a pseudo-fingerprint.

### Quality, storage, and change control

- `quality_grade`, `quality_grade_basis`, `record_qc_status`, and
  `eligibility_status` satisfy separate rule sets; eligibility is never
  inferred solely from grade.
- A `replicate_id`, duplicate group, uncertainty, or “not detected” status
  requires direct evidence. Its absence is represented as not assessed/reported
  under the accepted sentinel contract, not a fabricated zero.
- Parquet/CSV mirror equivalence satisfies the delivery contract above for all
  tables, including raw values and semantic states.
- Raw-input hashes and Core v0.1 hashes remain unchanged. v0.2 build output is
  release-blocked until an independent reviewer reruns the builder and the
  validators from a clean environment.

## Decisions requiring Proposed ADR and independent review

The following are deliberate non-decisions in this report; implementation
must not choose them implicitly.

| Topic | Required before promotion | Why independent review is necessary |
|---|---|---|
| `NA`/Arrow-null/CSV lexical contract | **Proposed ADR**, then automated negative tests | Current v0.1 defines neither `NA` semantics nor CSV parsing rules. A wrong choice can silently collapse missingness and experimental levels. |
| v0.2 additive schema and Arrow logical types | **Proposed ADR** superseding/augmenting ADR 0003 | ADR 0003 is Proposed and does not specify field-level types, side tables, or schema fingerprinting. |
| Structure standardization policy | **Proposed ADR/config** for salt handling, metal/ion pairs, R-groups, canonicalization and feature software versions | These rules can change identity/features. Reviewer must audit source evidence, failure classes, and a stratified sample. |
| Curated structure recovery | Evidence ledger plus independent source/page/table review for every curated mapping | No recovery may be inferred from reaction names, similar papers, or a public-database hit alone. |
| Registry non-identity and cross-source mappings | Frozen mapping config, evidence ledger, reviewer approval per mapping class | String identity is insufficient; reviewer must explicitly test source scope and critical roles. |
| Composite catalyst-system splitting | Source evidence plus independent review; otherwise keep `catalyst_system` atomic | Ahneman's pre-formed Pd–ligand system cannot be silently decomposed. |
| Mixture ratios/unit conversions and `measurement_value_standardized` | Proposed unit-conversion config and review | A numeric conversion can create false comparability or erase the raw label. |
| Quality-grade rubric and eligibility policy | Separate Proposed ADR/configs and reviewer audit | The proposal's A–E rubric does not authorize a blanket regrade or training exclusion. |

## Handoff

**Recommendation:** accept this as the Phase 1 contract-review input only;
first implement the frozen schema/ADR and validators, then create a candidate
v0.2 build. Do not regenerate pairs, graphs, splits, cliffs, or baselines until
the standardization contract receives the required independent review.

**Commands used for this read-only analysis:**

```text
rg --files / rg -n over the schema, proposal, metadata, scripts, tests and reports
python3 (stdlib csv) aggregate check of current Core v0.1 records/registry
git status --short
```

