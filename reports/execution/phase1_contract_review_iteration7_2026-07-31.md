# Phase 1 Round A contract re-review — claimed proposed.3

Date: 2026-07-31  
Role: `independent_reviewer`  
Scope: read-only check that the four Iteration 6 blockers are closed in ADR
0004 and `configs/core_v0_2_contract.json`.  No code, data, mapping, or Core
v0.2 artifact was modified.

## Verdict

**FAIL — the policy text closes the four semantic gaps, but the frozen
machine-validation contract and revision identity are still incomplete.**

## Four blocker regression check

| Iteration 6 blocker | Current contract evidence | Semantic rule | Executable negative-case contract | Result |
| --- | --- | --- | --- | --- |
| Perera could receive fabricated condition structures | `perera_allowed_structure_roles: []`; full Perera condition-role deny list; `unlisted_structure_role_policy=default_deny` | Closed | No explicit negative case that attempts a Perera ligand/base/catalyst structure assertion | PARTIAL FAIL |
| Record refs could point across source or role | `mapping_rules.record_component_reference_rule` requires exactly one registry entity with identical `source_dataset` and role | Closed | No cross-source or role-mismatched record-reference negative case | PARTIAL FAIL |
| `continuous_observations.value_state` had no closed domain | `closed_domains.continuous_value_state` plus table binding | Closed | No invalid-state / Arrow-null-versus-CSV-token truth-table cases for continuous observations | PARTIAL FAIL |
| Discrete condition coverage threshold absent | `condition_coverage_gate` defines source roles, 1.0 state coverage, 0.99 valid-or-explicit-null completeness, and source-only `not_reported` exception | Closed | No missing-reference / below-99%-completeness negative case | PARTIAL FAIL |

ADR 0004 decision 11 states the same four rules, so ADR and JSON are now
semantically consistent.  The remaining issue is that `validation_negative_cases`
does not name any of the four required adversarial cases.  A later validator
could pass its existing listed cases while entirely omitting the new guard:
for example, `cross_source_same_spelling_not_equivalent` can exercise mapping
rows without checking that `reaction_records.condition_component_refs` obey
the same-source/same-role foreign key.

## Revision-identity defect

The requested review target is “proposed.3”, while the only machine contract
identifies itself as:

```json
"contract_version": "CondRxnBench-Core-v0.2-proposed.2"
```

The ADR has no matching proposed-revision identifier.  Therefore a future
builder/manifest cannot unambiguously declare whether it implements the
previously rejected proposed.2 or this revised text.  Version identity is
part of the required frozen rule/config provenance and must be corrected
before acceptance.

## Minimal required revision

Only contract/test-design editing is allowed next.  It must:

1. Bump the JSON contract identifier to the agreed proposed.3 value and add
   the same explicit contract-version reference to ADR 0004.
2. Add these named negative cases to `validation_negative_cases` (or an
   unambiguously referenced validation-test contract):
   - `perera_unallowed_condition_structure_rejected`;
   - `record_component_ref_cross_source_or_role_mismatch_rejected`;
   - `continuous_value_state_and_arrow_null_csv_token_truth_table`;
   - `condition_coverage_missing_reference_or_below_threshold_rejected`.

No Core v0.2 data implementation, mapping, feature generation, Parquet
delivery, pair regeneration, graph/split, label, or model work is authorized
until the versioned machine contract names and tests these rules and another
Round A review passes.
