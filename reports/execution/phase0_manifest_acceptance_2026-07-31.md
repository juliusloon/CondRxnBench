# Phase 0 raw-input manifest acceptance — 2026-07-31

## Decision

The following immutable input manifests are accepted as the Phase 0 recovery
baseline after independent content review:

- `metadata/raw_input_manifests/ahneman_doyle_rxnpredict_v0_2_candidate.json`
- `metadata/raw_input_manifests/perera_suzuki_miyaura_v0_2_candidate.json`

The acceptance is intentionally a **new** record. It does not rewrite the
historical `candidate_pending_independent_review` state captured by
`reports/execution/phase0_candidate_manifest_review_2026-07-31.md`.

## Evidence and scope

- The independent evidence auditor recomputed all 20 file hashes and checked
  that the 18 Ahneman entries exactly equal the builder's 12 per-well exports,
  2 layout tables, and 4 component lists; the 2 Perera entries exactly equal
  the builder's workbook and supporting PDF.
- The current Perera values agree with the deleted legacy manifest at
  `HEAD:data/raw_metadata/perera_raw_input_manifest.json`, but this acceptance
  uses the new repository-relative manifest and does not restore or overwrite
  that existing user deletion.
- The manifests cover reconstruction inputs only. Licence and source narrative
  files remain under `data/raw/*/` and are not reclassified as tabular inputs.

## Review chain

1. Content audit: `reports/execution/phase0_candidate_manifest_review_2026-07-31.md` — PASS.
2. Integration acceptance: this record; both JSON manifests now declare
   `accepted_after_independent_review_2026-07-31` and link to the content
   audit.
3. Full Phase 0 promotion remains pending the revised clean-environment
   rerun and the follow-up independent review. It is not inferred merely from
   this manifest acceptance.
