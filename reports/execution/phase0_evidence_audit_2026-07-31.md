# Phase 0 independent evidence audit — 2026-07-31

Role: `evidence_auditor` (independent, read-only for data and code).  This
report records only the audit evidence; it does not rebuild, normalize, or
modify raw/processed datasets.

Audit snapshot:

- Repository `HEAD`: `80ee279e1bfaeb0750807d2d09a15b1f4d1e2dd4`.
- The worktree is dirty.  In particular, the tracked
  `data/raw_metadata/perera_raw_input_manifest.json` is deleted; Core v0.1,
  its builder, verifier, metadata, and goal files are currently untracked.
- `git diff --quiet -- data/raw` passed: no tracked file below `data/raw/` has
  been modified relative to `HEAD`.

## Verdict

**Phase 0 raw/input-manifest hard acceptance: FAIL / promotion blocked.**

The currently present raw bytes and Core v0.1 outputs pass the checks below,
but an *available, accepted* input-hash manifest is a hard prerequisite:

1. Perera's only tracked raw-input manifest is absent from the worktree
   (`D data/raw_metadata/perera_raw_input_manifest.json`).  Its historical
   `HEAD` content agrees with the current raw hashes, but a `git show` result
   is not an available workspace manifest for a reproducible restoration.
2. There is no workspace or `HEAD` copy of
   `data/raw_metadata/ahneman_raw_input_manifest.json`.  The Ahneman builder
   can generate it, but that would create a new derived artifact rather than
   verify an accepted manifest.  Therefore the 18 required Ahneman build
   inputs have presence and immutability evidence, but no accepted-hash
   comparison evidence.

Do not promote beyond Phase 0 until the owner resolves the deletion and
accepts/version-controls the Ahneman input manifest (or records an explicit
ADR replacing that requirement).  This is an evidence/provenance blocker,
not evidence that either raw data file has changed.

## Evidence table

| Gate | Status | Independent evidence |
| --- | --- | --- |
| Ahneman raw inputs needed by its builder are present | PASS (presence) | `scripts/Buchwald-Hartwig-HTE/build_dataset.py` reads 12 `yield_data/plate{1..3}.{1..4}.csv`, `layout/Table_S1.csv`, `layout/Table_S2.csv`, and 4 `smiles/*-list.csv`. All 18 files are present and tracked under `data/raw/ahneman_doyle_rxnpredict/`; `SOURCE.md` pins upstream `doylelab/rxnpredict` commit `57e15fdb7f7483c6bf3a601df69f6ac9e5af6965`. |
| Ahneman raw hashes compare to an accepted manifest | FAIL | No `data/raw_metadata/ahneman_raw_input_manifest.json` exists in either the worktree or `HEAD`. The builder emits one, but no prior accepted expected hashes are available to compare. |
| Perera raw input files and historical-manifest hashes | PASS (bytes), FAIL (available manifest) | `shasum -a 256` gives workbook `a869e020ba31bd5676c67a4791c3b7384711b5216de6af444b8cd0a24c284640` and PDF `54e505db0b1e7200552dae79dfff5398d1d2cbae08fcbfe472239aaa86c81b30`; both equal the historical tracked manifest at `HEAD:data/raw_metadata/perera_raw_input_manifest.json` and `data/raw/perera_suzuki_miyaura/SOURCE.md`. The manifest itself is deleted from the workspace. |
| Perera tabular source shape/identity/zero semantics | PASS | Direct workbook read: 5,760 x 16, 5,760 unique `Reaction_No`, 275 `Product_Yield_PCT_Area_UV == 0`, 480 literal blank-ligand (`None`) levels, 720 literal blank-base levels. This agrees with the historical manifest and source card. |
| Ahneman reconstruction baseline | PASS (derived-output consistency) | `reports/Buchwald-Hartwig-HTE/ahneman_qc_summary.json` reports 4,140 reconstructed main cells, 4,132 observed outcomes, 8 missing outcomes, 273 observed zero yields, and 55,676 observed-only strict pairs. `data/processed/ahneman_buchwald_hartwig_controls.csv` independently has 468 controls (467 observed, 1 missing, 289 observed zero). |
| Perera reconstruction baseline | PASS (derived-output consistency) | `reports/Suzuki-Miyaura-HTE/perera_qc_summary.json` reports 5,760 records, 15 reaction groups, 5,760 observed yields, 275 zero yields, and 60,480 strict pairs. |
| Core v0.1 manifest count support | PASS | `data/processed/core_v0_1/manifest.json` declares 9,900 records, 116,156 pairs; sources are 4,140/5,760 records and 55,676/60,480 pairs; observed zeros are 273/275. Independent CSV inspection reproduced every one of these values. |
| Core v0.1 semantic / endpoint invariants | PASS | `python3 tests/verify_core_v0_1.py` passed. It verifies record/pair unique keys; source counts; observed yields in [0,100]; `zero_yield == yield_observed AND yield_percent == 0`; all pairs single-factor, same source/group, with observed endpoints; and `success_label` / `cliff_label` are `not_assigned`. |
| Core v0.1 file-hash integrity | PASS | Recomputed SHA-256 equals manifest: `reaction_records.csv` `71ae9d62b48aa088ffd00238b83cbce7acd94b4c741d8192231e1d38ca3a9449`; `condition_pairs.csv` `c026562beb4c8af7be5e3f74fd61c076b6ade73e442a4f44f2c96e1701daf52b`; `condition_registry.csv` `e5a80b4913be4cb57cf3cec61c0d76c9bae1168068acb25f350ee9b742c22b8d`. |

## Reproduced Core v0.1 statistics

| Quantity | Ahneman–Doyle | Perera Suzuki–Miyaura | Total |
| --- | ---: | ---: | ---: |
| Core main-matrix records | 4,140 | 5,760 | 9,900 |
| Observed outcomes | 4,132 | 5,760 | 9,892 |
| Missing outcomes | 8 | 0 | 8 |
| Observed zero yields | 273 | 275 | 548 |
| Strict single-factor pairs | 55,676 | 60,480 | 116,156 |

The corresponding checks found 9,900 unique `reaction_id`, 116,156 unique
`pair_id`, all `n_changed_factors == 1`, `success_label == not_assigned`, and
`cliff_label == not_assigned`.

## Commands rerun for this audit

All commands below are read-only except for the test process's normal in-memory
work.  They can be rerun from the repository root.

```bash
git rev-parse HEAD
git status --short
git diff --quiet -- data/raw
git diff -- data/raw_metadata/perera_raw_input_manifest.json

shasum -a 256 \
  data/raw/perera_suzuki_miyaura/aap9112_Data_File_S1.xlsx \
  data/raw/perera_suzuki_miyaura/aap9112_perera_sm.pdf \
  data/raw/perera_suzuki_miyaura/UPSTREAM_REPO_LICENSE.txt
git show HEAD:data/raw_metadata/perera_raw_input_manifest.json

find data/raw/ahneman_doyle_rxnpredict/yield_data \
     data/raw/ahneman_doyle_rxnpredict/layout \
     data/raw/ahneman_doyle_rxnpredict/smiles \
     -type f -print0 | sort -z | xargs -0 shasum -a 256

python3 tests/verify_core_v0_1.py
shasum -a 256 data/processed/core_v0_1/reaction_records.csv \
  data/processed/core_v0_1/condition_pairs.csv \
  data/processed/core_v0_1/condition_registry.csv
```

For a write-isolated source rebuild after manifest remediation, use a fresh
temporary directory and compare its generated manifests and derived hashes;
do **not** point either builder at the repository root:

```bash
audit_tmp="$(mktemp -d)"
python3 scripts/Buchwald-Hartwig-HTE/build_dataset.py --out-root "$audit_tmp"
python3 scripts/Suzuki-Miyaura-HTE/build_dataset.py --out-root "$audit_tmp"
```

The pair-QC scripts currently write fixed repository paths, so do not use them
for a supposedly isolated verification until they gain an output-root option.

## Required owner decision / next evidence

1. Preserve or intentionally restore the deleted Perera manifest without
   altering `data/raw/`; verify its hashes again after restoration.
2. Produce and review an Ahneman input manifest that covers all 18 actual
   builder inputs (12 per-well CSVs, 2 layout CSVs, and 4 SMILES lists), then
   version/accept it.  The current builder's `well_files + layout_files`
   manifest construction does include the four SMILES lists; the missing
   evidence is an accepted persisted instance, not an apparent omission from
   that construction.
3. Re-run this audit's raw-hash comparison before signing the Phase 0 hard
   acceptance.  Until then, Core v0.1 may be used as an internally consistent
   regression baseline, but not promoted as a fully reproducible Phase 0
   baseline.
