# Phase 1 Round A contract re-review — Core v0.2 proposed.2

Date: 2026-07-31  
Role: `independent_reviewer`  
Scope: read-only re-review of ADR 0004 and
`configs/core_v0_2_contract.json` (`proposed.2`) against the seven blocking
findings in the prior Round A review and the Phase 1 hard acceptance.  No
data, maker code, mapping, or Core v0.2 release artifact was changed.

## Verdict

**FAIL — keep the contract Proposed; do not begin Phase 1 implementation.**

The revision substantively closes most of the prior findings, but four
remaining machine-contract gaps still permit fabricated Perera condition
structures, cross-source registry references, or collapsible typed missingness.
They must be resolved before a data builder or mapping is allowed to interpret
the contract.

## Regression matrix for the prior seven blockers

| Prior blocker | proposed.2 evidence | Result |
| --- | --- | --- |
| 1. Ahneman `substrate_1` contradicted by the JSON role list | `source_boundaries.ahneman_allowed_structure_roles` now explicitly includes `substrate_1`; unsupported Ahneman roles are enumerated | PASS |
| 2. Structure assertions lacked canonical/error/feature fields | `tables.record_structure_assertions.required` now includes assertion version, normalized/canonical SMILES, InChIKey, normalization rule, error/disposition, and five feature status/reason pairs | PASS |
| 3. Salt/metal/ion/R-group policy unfrozen | `structure_standardization_policy` fixes a conservative no-identity-change default, RDKit 2024.03.6, and no feature generation after failure | PASS |
| 4. Non-identity mapping target/scope and attribute provenance absent | `condition_mappings` adds target/scope/version/evidence/reviewer/disposition; `condition_attributes` adds the closed provenance domain and mapping rules prohibit unaccepted use | PASS for mapping rows; see remaining record-reference gap below |
| 5. Units and mixture composition incomplete | `continuous_observations` and `condition_compositions` now require raw/normalized values/units, rule/version, source evidence and review; 9:1 Perera mixture is recorded | PASS, subject to the remaining `value_state` domain gap |
| 6. Missingness/outcome domains not closed or negative-tested | component/outcome/parse/feature/review domains and nine negative cases were added | PARTIAL FAIL — generic numeric `value_state` remains undefined |
| 7. Yield conservation and storage/equivalence under-specified | per-source record/observed/missing/zero counts, Arrow types/fingerprint and equivalence checks are now explicit | PARTIAL FAIL — discrete-condition coverage threshold and same-source FK validation are still absent |

## Remaining blocking gaps

### 1. Perera condition structures remain open to fabrication

The requested boundary is “Ahneman allows source-backed structures; Perera
does not fabricate structures.”  `source_boundaries` now provides
`ahneman_allowed_structure_roles`, but it provides neither
`perera_allowed_structure_roles: []` nor a default-deny rule.  Its
`perera_not_supported_structure_roles` lists only substrate/product/reaction
roles and omits `catalyst`, `ligand`, `base`, `solvent_1`, `solvent_2`,
`catalyst_system`, and `additive`.

Consequently an implementer can take Perera ligand/base/catalyst strings from
the workbook, resolve them with an external database, and emit source-looking
SMILES without violating any explicit JSON rule.  ADR 0004 decision 3 also
only states Perera substrate/product/reaction exclusions, so it does not close
this hole for Perera condition entities.

Required contract change: state a default-deny source-boundary rule and either
set `perera_allowed_structure_roles` to an empty list or enumerate every
currently unsupported Perera role.  A later source-backed exception must be a
new reviewed contract/mapping, not an implementation choice.

### 2. Record-to-registry same-source/role foreign keys are not required

`reaction_records.condition_component_refs` is required, and registry rows
carry `source_dataset`/`role`, but no machine rule says each referenced
`component_id` must resolve to exactly one registry entity having the same
record `source_dataset` and represented role.  `mapping_rules.target_scope_required`
only controls mapping rows, not record foreign keys.

This permits an Ahneman record to reference a Perera component ID (or an ID
with a mismatched role) while all current fields remain syntactically valid.
That is exactly the unreviewed cross-source merge/leakage failure Phase 1 must
prevent.

Required contract change: add explicit source-scoped/role-scoped foreign-key
invariants for every `condition_component_refs` entry and a negative case for
cross-source or role-mismatched references.

### 3. `continuous_observations.value_state` has no closed semantic domain

The table requires `value_state`, but `closed_domains` defines only
`component_value_state`, not a numeric/continuous value-state domain.  The
storage contract says Arrow null must be paired with explicit state, yet it
does not define permitted states for raw/normalized numeric absence (for
example, `observed`, `NA`, `not_reported`, `not_assessed`) or state-to-null
rules.  The present negative case `raw_numeric_null_never_implies_zero` is
necessary but cannot reject an arbitrary or contradictory state string.

This leaves the concrete Phase 1 risk identified in the evidence audit:
blank `ligand_equiv` values in explicit no-ligand Perera records could be
serialized/decoded inconsistently, then collapsed with zero or source
non-reporting.

Required contract change: define a closed `continuous_value_state` domain,
bind `continuous_observations.value_state` to it, and add Arrow-null/CSV-token
truth-table negative cases for each state.

### 4. Discrete condition coverage gate is not frozen

Phase 1 requires 100% state coverage for discrete core conditions and >99%
completeness for valid/explicit-null levels.  No `conservation` or validation
rule states the discrete roles, denominator, sentinel treatment, coverage
calculation, or thresholds.  A builder can omit component references for a
role/record and still satisfy the current 9,900/outcome/registry checks.

Required contract change: freeze the included discrete roles per source,
define coverage numerator/denominator and explicit-null treatment, require
100% state coverage and >99% valid-or-explicit-null completeness, and include
a failing missing-reference test.

## What is now correctly protected

Once the four items above are repaired, the revised ADR/config already provide
strong controls for raw-vs-normalized preservation, Ahneman source-backed
structure roles, atom/product/reaction non-fabrication, source-scoped mapping
targets, conservative standardization, mixture/unit evidence, derived versus
evidence-backed attributes, explicit zero/not-detected semantics, 9,900-row
outcome conservation, and Parquet/CSV equivalence.

## Permitted next work

Because this Round A result is **FAIL**, the only permitted work is a further
ADR/config/validator-test-contract revision addressing the four precise gaps
above.  Do not generate `core_v0_2` tables, registry mappings, structure
assertions, Parquet outputs, pairs, graphs, splits, labels, or model results
until a new independent Round A review passes.
