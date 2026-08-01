# Phase 1 Round A contract review — Core v0.2 proposed.1

Date: 2026-07-31  
Role: `independent_reviewer`  
Scope: read-only contract review of ADR 0004 and
`configs/core_v0_2_contract.json` against the goal's Phase 1 requirements.
No maker code, raw data, mapping, Core v0.2 table, pair, graph, split, label,
or model result was changed by this review.

## Verdict

**FAIL — do not freeze this contract or begin Phase 1 data implementation.**

ADR 0004 establishes the right safety intent: additive v0.2 delivery,
source-aware outcomes, source-scoped entities, no automatic Perera structure
recovery, explicit-null protection, mixtures/units, and quality-versus-
eligibility separation.  However, the JSON contract does not fully encode
those rules and is inconsistent with the ADR on an allowed Ahneman structure
role.  A maker could therefore make consequential structure, mapping, unit,
or state decisions without a frozen machine-checkable rule or validator.
This is a Round A gate failure, not a failure of the v0.1 baseline.

## Requirements that are adequately stated in ADR 0004

| Goal boundary | Contract evidence | Review |
| --- | --- | --- |
| Additive raw/normalized direction; never overwrite raw/v0.1 | ADR decisions 1–2 | PASS in ADR prose |
| No fabricated Perera substrate/product/reaction structures; Ahneman catalyst system stays atomic | ADR decision 3 | PASS in ADR prose |
| Source-scoped entities; no automatic cross-source equivalence | ADR decision 4 | PASS in ADR prose |
| `NULL_COMPONENT`, `not_reported`, `NA`, observed zero distinct | ADR decision 5 | PASS in ADR prose |
| Raw value/unit plus normalized value/unit; no cross-source yield calibration; mixture preservation | ADR decision 6 | PASS in ADR prose |
| Quality grade distinct from training eligibility | ADR decision 7 | PASS in ADR prose |
| New Parquet authority plus CSV mirror; 9,900 and outcome conservation gates | ADR consequences and contract `storage`/`conservation` | Partly stated; see failures below |

## Blocking contract gaps

### 1. Ahneman `substrate_1` structure permission is contradictory

ADR 0004 decision 3 explicitly permits source-backed Ahneman `substrate_1`
assertions.  Yet `source_boundaries.ahneman_supported_component_structure_roles`
in `core_v0_2_contract.json` permits only `ligand`, `base`, and `additive`.
It omits `substrate_1`.  The machine contract therefore either forbids a
legitimate source-backed structure or invites an unfrozen exception.  This
fails the required “Ahneman allows evidence-backed structures; Perera is not
filled in” boundary.

### 2. The required structure assertion schema cannot prove the structure gate

The JSON `record_structure_assertions.required` list includes raw value,
locator, parse status, disposition, and review status, but omits required
fields for normalized SMILES, canonical SMILES, InChIKey, normalization-rule
version, `error_class`, assertion version, and per-feature status/reason
columns.  It lists possible feature-state values without requiring a Murcko,
ECFP4, ECFP6, DRFP, and reaction-centre status field on each assertion.

Thus the contract cannot automatically establish the goal's requirements that
every declared-parseable structure has a parse/sanitize result, every failure
has raw value/source/error class/disposition, and unavailable reaction
structures never create pseudo-fingerprints.  ADR prose mentions these
concepts, but the purported machine contract does not require their storage.

### 3. Identity-changing chemistry policy is not frozen/config-driven

Neither ADR 0004 nor the JSON config freezes a referenced standardization
policy for salt/parent selection, metal and ion-pair handling, R-group
markers, canonicalization software/rule version, or a conservative default
when evidence is insufficient.  Goal Phase 1 requires these operations to be
config-driven and conservative.  Leaving them to implementation allows silent
identity changes or inconsistent parseability claims.

### 4. Mapping model cannot fully audit cross-source equivalence or attributes

`condition_mappings.required_for_non_identity` lacks a required target
representation/component, mapping version, `non_identity` flag, evidence ID,
and reviewer/disposition identity.  `source_component_id` alone cannot show
what was mapped, whether a mapping claims cross-source equivalence, or whether
an accepted status applies to the exact target.

The config also has no registry attribute contract requiring an attribute to
be marked `evidence_backed` versus `derived` (e.g. ligand family, base type,
solvent polarity).  Consequently a derived category could be presented as
source fact.  The ADR's general mapping rule does not cure the missing fields
and invariants.

### 5. Units and mixture composition are only partially specified

The `record_extensions` list has no general raw-value/raw-unit/normalized-
value/normalized-unit/conversion-rule/evidence structure for every continuous
field.  `measurement_value_raw_unit` is too narrow.  Similarly,
`condition_compositions` stores raw ratios but omits a required composition
mapping/version, target component scope and explicit rule for the documented
Perera 9:1 mixture.  Without those, unit conversion or mixture expansion can
be improvised and cannot be consistently reviewed.

### 6. Missingness and outcome states lack closed, testable domains

The config defines the lexical meanings of `NA`, `not_reported`,
`NULL_COMPONENT`, and zero, but provides no closed allowed values for
`outcome_observation_status`, no explicit `not_detected` state, and no generic
value-state field binding Arrow null / CSV `NA` to a semantic state.  It also
does not specify the negative invariants required to prevent a numeric null,
literal token, explicit-null condition, observed zero, and `not_detected`
from collapsing during a build or CSV read.

### 7. Conservation and storage checks are under-specified in the config

The config records total/source record counts, Ahneman missing yields, and
zero counts, but omits explicit observed/missing counts for both sources
(Ahneman 4,132/8; Perera 5,760/0).  It therefore cannot independently enforce
the full observed/missing/zero conservation rule.

It declares Parquet authoritative and CSV an inspection mirror, but does not
freeze logical types, primary keys, Arrow-schema fingerprint, side-table
schema/row rules, canonical map/list encoding, or the complete cross-format
equality checks.  ADR 0004 discusses these requirements, but the config is
not sufficient as a pre-implementation validation target.

## Adversarial failure modes left open

- Treat `ligand=XPhos` across sources as the same target mapping because the
  mapping table lacks an explicit target scope and cross-source flag.
- Add an Ahneman `substrate_1` structure through an undocumented exception, or
  reject it despite direct source evidence, because ADR and JSON disagree.
- Strip a counterion, select a parent fragment, or canonicalize an R-group
  without a frozen rule/version, then report a parse rate that cannot be
  independently reproduced.
- Serialize a blank numeric cell as `NA`, then let a CSV reader convert it to
  null without a semantic state; subsequent code can conflate it with missing
  yield or an explicit no-ligand condition.
- Mark an inferred solvent polarity or ligand family as a registry fact with
  no indication that it is derived.
- Store a raw 9:1 solvent string yet silently apply a composition/unit
  conversion whose evidence and mapping version are not required.

## Required contract revision before implementation

Only the following contract/ADR/config/test-design revision work is allowed
next; do **not** build Core v0.2 data or create mappings until it passes a
new Round A review.

1. Reconcile `source_boundaries` with ADR 0004: explicitly allow Ahneman
   `substrate_1` source-backed assertions and explicitly enumerate every
   allowed/unsupported role by source.
2. Define complete versioned schemas for assertions, registry entities,
   mappings, compositions, and continuous-unit observations, including all
   raw/normalized/canonical/error/evidence/review/target/scope fields above.
3. Add a frozen conservative structure-standardization policy/config for
   salts, metals, ion pairs, R-groups, canonicalization, feature software and
   failure dispositions.
4. Define closed domains and negative-test cases for all outcome/value states,
   component states, feature states and accepted/pending/rejected mapping use.
5. Encode full per-source yield conservation (observed, missing, zero),
   9,900-row identity/provenance rules, source-scoped foreign-key checks, and
   Parquet/CSV logical-schema/equivalence/manifest checks.
6. Specify attribute provenance as `evidence_backed` or `derived`, and forbid
   automatic cross-source equivalence absent a reviewed mapping to an explicit
   target.

After those revisions, resubmit ADR 0004 plus the JSON contract for a clean
Round A review.  No Phase 1 implementation, pair regeneration, graph/split,
cliff-label, or model work is authorized by this FAIL verdict.
