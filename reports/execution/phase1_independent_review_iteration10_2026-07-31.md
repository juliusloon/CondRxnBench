# Phase 1 Round C independent adversarial review — Iteration 10

Date: 2026-07-31  
Role: `independent_reviewer`  
Scope: adversarial sampling of the independently reproduced candidate at
`/private/tmp/condrxnbench-phase1-review9.XrkpHW/candidate`.  No implementation,
raw input, Core v0.1 file, or workspace candidate output was modified.

## Verdict

**PASS — Phase 1 Round C independent adversarial review passes.**

Every sampled source/role reference resolves to a same-source/same-role
registry entity; source structure boundaries, mapping-pending boundaries,
explicit-null/missing/zero semantics, composition, and direct negative cases
behaved as the frozen proposed.3 contract requires.  This supports Phase 1
promotion from candidate implementation to the goal's next phase gate; it
does not authorize Phase 2 pairs/graphs or any benchmark/model artifact.

## Source × role registry/FK samples

One main-matrix record was sampled for every discrete role in both sources.
For `AHNEMAN_BH_P1_R02_C01`, the sampled references were
`catalyst_system=XPhos`, `ligand=XPhos`, `base=P2Et`, and
`additive=5-phenylisoxazole`; each resolved to a distinct Ahneman
source-scoped entity of the same role.  In particular, same spelling does not
cause the catalyst-system and free-ligand entities to merge.

For `PERERA_SM_0001`, sampled `catalyst=Pd(OAc)2`, `ligand=P(tBu)3`,
`base=NaOH`, `solvent_1=MeCN`, `solvent_2=H2O`, and the glovebox atmosphere
each resolved to a Perera entity of the same role.  The full verifier's FK
scan confirmed this for all 9,900 record maps.

## Structure boundary and parse audit

| Check | Result | Evidence |
| --- | --- | --- |
| Source-reported assertions | PASS | Exactly 16,560 (`4 × 4,140`), all Ahneman and only roles `substrate_1`, `ligand`, `base`, `additive`. |
| Source samples parse/canonicalize | PASS | First-record samples parse/sanitize and match RDKit canonical SMILES/InChIKey: substrate `QULYNCCPRWKEMF-UHFFFAOYSA-N`, ligand `UGOMMVLRQDMAQQ-UHFFFAOYSA-N`, base `CFUKEHPEQCSIOM-UHFFFAOYSA-N`, additive `BXQDLEHCXQQSCH-UHFFFAOYSA-N`; source locators point to the corresponding vendored list CSVs. |
| Perera structure denial | PASS | All 63,360 Perera assertions are `not_supported`; normalized/canonical SMILES and InChIKey have zero non-null values. |
| Artificial Perera structure attempt | PASS | Calling the builder's registry-structure path with a Perera ligand name and synthetic `CC` SMILES returned `structure_status=not_supported` and no normalized SMILES. |

## Mapping, null, outcome, and composition audit

- **Pending non-identity mappings:** exactly two Perera solvent rows:
  `MeOH/H2O_V2 9:1 → MeOH` and `THF_V2 → THF`.  Both identify the workbook
  solvent column as source locator/evidence, have `review_status=pending`,
  `reviewer_id=null`, target scope `core_v0_1_compatibility_only`, and
  `not_usable_until_independent_acceptance`.  Their source component IDs remain
  the values referenced by records; neither mapping is used to normalize a
  v0.2 record reference.
- **Explicit null:** sampled `PERERA_SM_0012` ligand and `PERERA_SM_0085` base
  retain raw literal `None`, each resolving to a separate Perera
  `NULL_COMPONENT` registry entity with `explicit_null_component` state.
  No registry row has raw `not_reported`.
- **Typed NA versus not reported:** `PERERA_SM_0012:ligand_equiv` is Arrow-null
  with `value_state=NA`; `AHNEMAN_BH_P1_R02_C01:temperature_c` is Arrow-null
  with `value_state=not_reported`.  The candidate therefore does not collapse
  typed missingness with absent source evidence.
- **Ahneman missing and zero outcomes:** all eight yield-null records have
  `yield_observed=false`, `zero_yield=false`,
  `outcome_observation_status=missing_analysis`, and
  `provenance_status=missing_analysis_export`.  Sample
  `AHNEMAN_BH_P1_R03_C04` is an observed numeric zero
  (`yield_percent=0`, `yield_observed=true`, `zero_yield=true`).
- **Mixture composition:** every Perera record has exactly two composition rows
  with raw ratio `9:1`.  Sample `PERERA_SM_0001` retains raw carrier `MeCN`
  and components `organic_carrier=9.0` and `H2O=1.0` volume parts.

## Direct adversarial negative calls

The verifier/build helper predicates were called with artificial invalid
values against the isolated candidate.  All invalid inputs were rejected:

| Negative case | Result |
| --- | --- |
| Use a Perera ligand component ID for an Ahneman ligand reference | rejected (`false`) |
| Use an Ahneman ligand component ID for an Ahneman base reference | rejected (`false`) |
| Use continuous `value_state=outside_domain` | rejected (`false`) |
| Supply a synthetic Perera ligand SMILES | denied as `not_supported`, no normalized structure |

The previously run full candidate verifier also passed, including its
CSV/Parquet, sentinel, conservation, FK, and no-pair/benchmark-output checks.

## Promotion boundary

This is an independent **Round C PASS** for Phase 1.  It verifies the
standardization candidate and its declared constraints; it does not change
the manifest's `candidate_not_promoted` status itself.  The integrator may
record the Phase 1 promotion decision and then begin only the Phase 2
protocol-first contract work.  No pair/graph/split/label/model artifact may be
generated merely from this review.
