# Phase 0 Round C independent review — Iteration 3 revision

Date: 2026-07-31  
Role: `independent_reviewer`  
Scope: re-review of the Iteration 3 fixes for the Python 3.11 runtime,
raw-input-manifest acceptance chain, selectively staged Phase 0 delivery, and
the complete two-source reconstruction/QC → Core → verifier sequence.  The
reviewer did not change maker code, raw data, or staged deliverables.  All
execution occurred in a fresh copied worktree,
`/private/tmp/condrxnbench-phase0-review3.ZwmURe/repo`, with a newly created
`/private/tmp/condrxnbench-phase0-review3-py311` virtual environment.

## Verdict

**PASS — Iteration 3 clears the Phase 0 Round C promotion gate.**

The prior reproducibility blocker is resolved: the declared CPython 3.11
requirements install cleanly and support the entire two-source build/QC
sequence.  Core count, pair, registry, raw-input, and CSV-to-Parquet
invariants all hold in the new isolation run.  The staged delivery contains
the Phase 0 contracts, generated Core artifact/manifest, evidence records,
and minimal QC path repair; it does not stage a raw-data modification.

## Clean-environment installation

Installed exactly from `environment/core_v0_2_py311_requirements.txt` into a
new CPython 3.11.15 environment on macOS arm64.  The direct packages resolved
to the following actual versions:

| Package | Version |
| --- | ---: |
| numpy | 1.26.4 |
| pandas | 2.2.3 |
| pyarrow | 17.0.0 |
| scikit-learn | 1.5.2 |
| rdkit | 2024.03.6 |
| pandera | 0.20.4 |
| pytest | 8.3.3 |
| networkx | 3.3 |
| openpyxl | 3.1.5 |
| tabulate | 0.10.0 |

This independently confirms the two direct runtime dependencies that failed
the prior review (`openpyxl` for `read_excel`; `tabulate` for `to_markdown`)
are now declared and installed.

## Full independent rerun

All commands below were run sequentially from the clean copied repository
using that new environment and exited zero:

```bash
python scripts/Buchwald-Hartwig-HTE/build_dataset.py
python scripts/Buchwald-Hartwig-HTE/qc_and_pairs.py
python scripts/Suzuki-Miyaura-HTE/build_dataset.py
python scripts/Suzuki-Miyaura-HTE/qc_and_pairs.py
python scripts/build_core_v0_1.py
python tests/verify_core_v0_1.py
python tests/verify_phase0_inputs.py
python tests/verify_parquet_roundtrip.py
```

The Core verifier printed `Core v0.1 verification passed: 9,900 records;
116,156 strict pairs.`  The input verifier recomputed all 20 declared raw
inputs and passed.  The Parquet verifier passed for all three Core tables.
PyArrow emitted sandbox-only `sysctlbyname ... Operation not permitted`
warnings while probing CPU features; it exited zero and did not affect the
round-trip result.

Fresh source reconstruction/QC outputs had the required counts:

| Artifact | Result |
| --- | ---: |
| Ahneman main matrix | 4,140 records |
| Ahneman controls | 468 records |
| Ahneman strict pairs | 55,676 |
| Perera main matrix | 5,760 records |
| Perera strict pairs | 60,480 |

The Ahneman QC root correction is therefore validated end-to-end from its
documented repository root.  Its freshly emitted source-intermediate CSVs
hold absolute `source_file` paths and consequently differ bytewise in an
isolation directory.  After normalizing that field to its basename, both the
4,140-row main matrix and 468-row controls were exactly equal to their
historical tracked contents.  These generated intermediates are not in the
selectively staged Phase 0 delivery, and Core normalizes the source filename;
there is no effect on the certified Core hashes below.

## Required invariant checks

| Check | Result |
| --- | --- |
| Ahneman 18 + Perera 2 raw SHA-256 values | PASS — unchanged before/after all builds/QC |
| `reaction_records.csv` | PASS — 9,900 rows, 9,900 unique IDs, historical SHA-256 `71ae9d62b48aa088ffd00238b83cbce7acd94b4c741d8192231e1d38ca3a9449` unchanged |
| `condition_pairs.csv` | PASS — 116,156 rows, 116,156 unique IDs, historical SHA-256 `c026562beb4c8af7be5e3f74fd61c076b6ade73e442a4f44f2c96e1701daf52b` unchanged |
| `condition_registry.csv` | PASS — 60 rows and 60 unique `component_id` values; SHA-256 `d757048413965999a22405c4485486082f0622c3463070097a4a4d9e1e115b40` |
| Registry identity change | PASS — source-scoped IDs separate the Ahneman and Perera `ligand=XPhos` entries, without changing records/pairs/raw evidence |
| CSV → Parquet → DataFrame | PASS — primary keys, row counts, booleans, numeric values, and `not_reported`/`NULL_COMPONENT`/`not_assigned` sentinel counts all preserved |

## Staging and acceptance-chain audit

`git diff --cached --name-status` shows a selective Phase 0 scope: ADR 0003,
the fixed requirements, source-scoped Core builder and Core CSV/manifest,
registry/docs/state/notes, candidate manifests, the three Phase 0 evidence
records, acceptance record, and the two verifiers.  The minimal Ahneman QC
root-path correction is the only modified existing script.  The rebuilt Core
worktree object IDs match their staged index object IDs for all three CSV
tables and `manifest.json`.

`git diff --cached --quiet -- data/raw` exited zero: no raw-content change is
staged.  The pre-existing deletion of
`data/raw_metadata/perera_raw_input_manifest.json` remains outside the staged
set and has not been restored or overwritten by this work.

The acceptance chain is now coherent:

1. `phase0_candidate_manifest_review_2026-07-31.md` is the historical
   independent content review and accurately records its then-pending state.
2. `phase0_manifest_acceptance_2026-07-31.md` is a later explicit integration
   decision; it names both relative-path manifests, preserves the historical
   record rather than rewriting it, and states that full promotion awaited
   this re-review.
3. Both staged candidate JSON manifests declare
   `accepted_after_independent_review_2026-07-31`; the direct verifier confirms
   their 20 file hashes.

This resolves the contradiction identified in the prior review without
changing raw evidence or retroactively falsifying the original audit.

## Promotion decision

**Promotion recommended for Phase 0, Iteration 3.**  This recommendation is
limited to the Phase 0 preflight/environment/immutable-baseline gate.  ADR
0003 remains Proposed and no Core v0.2 standardized release, benchmark split,
cliff label, baseline-model result, external push, or publication is approved
by this review.
