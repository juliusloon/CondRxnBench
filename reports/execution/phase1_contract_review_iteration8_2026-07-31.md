# Phase 1 Round A final contract review — Core v0.2 proposed.3

Date: 2026-07-31  
Role: `independent_reviewer`  
Scope: read-only final re-review of ADR 0004 and
`configs/core_v0_2_contract.json`.  No data, code, mapping, or candidate
release artifact was changed by this review.

## Verdict

**PASS — freeze `CondRxnBench-Core-v0.2-proposed.3` as the Phase 1 Round A
implementation contract.**

The JSON is valid and identifies itself as `CondRxnBench-Core-v0.2-proposed.3`.
ADR 0004 decision 11 and the JSON encode the four previously blocking rules
consistently, and each is now named in `validation_negative_cases`.

| Prior blocker | Frozen rule | Negative validation contract | Result |
| --- | --- | --- | --- |
| Perera structure fabrication | Empty `perera_allowed_structure_roles` plus default-deny unlisted-role policy | `perera_unlisted_condition_structure_role_is_default_denied` | PASS |
| Cross-source/cross-role record component reference | Each reference resolves to exactly one registry entity with identical source and role | `record_component_ref_cross_source_or_cross_role_is_rejected` | PASS |
| Unconstrained continuous state | `continuous_value_state` closed domain and table binding | `continuous_value_state_outside_closed_domain_is_rejected` | PASS |
| Unfrozen discrete condition coverage | Explicit source roles, 100% state coverage, and >=99% valid-or-explicit-null completeness | Two below-threshold negative cases | PASS |

The broader contract also retains the previously accepted controls: raw/v0.1
immutability; raw/normalized/canonical structure assertions; conservative
salt/metal/ion/R-group policy; accepted evidence/review for non-identity
mappings; derived-versus-evidence-backed attributes; separate
`NULL_COMPONENT`/`not_reported`/`NA`/zero/not-detected states; unit and 9:1
mixture evidence; source-aware outcome conservation; and Parquet/CSV schema
and equivalence requirements.

## Minimum implementation scope now authorized

Implementation may now create a **candidate** Core v0.2 standardization path
only, within the frozen contract:

1. Add a v0.2 builder and validators that read accepted raw inputs/Core v0.1
   and write only `data/processed/core_v0_2/` plus versioned reports/tests;
   never rewrite `data/raw/` or Core v0.1.
2. Preserve all 9,900 records and the frozen per-source
observed/missing/zero counts; add the specified record extensions, provenance
states, source-scoped registry references, continuous observations, and
Perera solvent-composition records.
3. Create structure assertions only for the allowed Ahneman roles
(`substrate_1`, `ligand`, `base`, `additive`) using source-backed inputs and
the conservative RDKit policy.  Perera receives no structure assertion based
on condition names; unsupported roles/statuses must be emitted explicitly.
4. Implement source-scoped registry/foreign-key validation, sentinel and
outcome-state negative tests, mapping-review gating, coverage gates, exact
conservation checks, and Parquet/CSV round-trip/equivalence checks.

The following remain outside this authorization: unreviewed curated mappings
or cross-source equivalence; catalyst-system splitting; salt/parent/metal/
ion/R-group transformations; product/atom-mapped/reaction-centre fabrication;
Core v0.2 promotion; pair/graph regeneration; splits, cliff/success labels,
or any baseline model result.  Those require the appropriate later
implementation validation and independent review gates.
