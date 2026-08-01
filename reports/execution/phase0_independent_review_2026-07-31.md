# Phase 0 Round C independent review — Iterations 1–2

Date: 2026-07-31  
Role: `independent_reviewer`  
Scope: adversarial review of the Ahneman QC root-path correction, source-scoped
condition-registry IDs, candidate raw-input manifests and acceptance status,
the Python 3.11 runtime specification, the Parquet verifier, and ADR 0003.
The reviewer did not modify source code, raw data, or release data.  All
commands below were run in a fresh copy at
`/private/tmp/condrxnbench-phase0-review.f8a2nc/repo`; its Python environment
was `/private/tmp/condrxnbench-phase0-review-py311`.

## Verdict

**FAIL — Phase 0 must not be promoted.**

The root-path correction and source-scoped registry implementation are valid
when Core is rebuilt in the isolated copy.  The raw hash verifier, Core
verifier, and Parquet round-trip verifier also pass.  However, the claimed
versioned Python 3.11 environment cannot reproduce the required two-source
build/QC chain: the requirements omit `openpyxl` (Perera Excel build) and
`tabulate` (both Markdown QC reports).  In addition, the candidate raw-input
manifests/ADR/runtime files are untracked, and their asserted accepted status
conflicts with the linked prior review report, which still records them as
pending acceptance.  These are Phase 0 hard-gate failures.

No raw bytes changed in the isolated copy.  The principal Core records/pairs
hashes were invariant after rebuilding.  The registry artifact changed only
as expected to give the cross-source XPhos entries separate IDs.

## Environment actually tested

`environment/core_v0_2_py311_requirements.txt` was installed as written into a
new CPython 3.11.15 environment (macOS arm64).  Direct pinned packages
resolved to: numpy 1.26.4; pandas 2.2.3; pyarrow 17.0.0; scikit-learn 1.5.2;
rdkit 2024.3.6; pandera 0.20.4; pytest 8.3.3; networkx 3.3.  The install itself
passed, establishing that the failures below are missing runtime declarations,
not a failed resolver.

## Required reproduction results

| Required command / check | Result | Independent evidence |
| --- | --- | --- |
| `python scripts/Buchwald-Hartwig-HTE/build_dataset.py` | PASS | Completed in the isolated copy. |
| `python scripts/Buchwald-Hartwig-HTE/qc_and_pairs.py` | FAIL | Fails at `qc_and_pairs.py:187`, `DataFrame.to_markdown`, with `ImportError: Missing optional dependency 'tabulate'.`  The corrected `ROOT = Path(__file__).resolve().parents[2]` did resolve repository-level `data/processed/`, so the prior root-path defect is fixed. |
| `python scripts/Suzuki-Miyaura-HTE/build_dataset.py` | FAIL | Fails at `build_dataset.py:46`, `pd.read_excel`, with `ImportError: Missing optional dependency 'openpyxl'.` |
| `python scripts/Suzuki-Miyaura-HTE/qc_and_pairs.py` | FAIL | Fails at `qc_and_pairs.py:94`, again `DataFrame.to_markdown`, with the same missing `tabulate` error. |
| `python scripts/build_core_v0_1.py` | PASS, limited | Completed using the copied source outputs; cannot certify a fresh Perera source rebuild because the Perera builder above failed. |
| `python tests/verify_core_v0_1.py` | PASS | Printed `Core v0.1 verification passed: 9,900 records; 116,156 strict pairs.` |
| `python tests/verify_phase0_inputs.py` | PASS | Printed `Phase 0 candidate input-manifest verification passed: 20 raw inputs.` |
| `python tests/verify_parquet_roundtrip.py` | PASS | Printed `Parquet round-trip verification passed for all Core v0.1 tables.`  PyArrow emitted sandbox-only `sysctlbyname ... Operation not permitted` warnings but exited 0. |

Minimal environment failure reproductions, after installing exactly the
versioned requirements, are:

```bash
/private/tmp/condrxnbench-phase0-review-py311/bin/python \
  scripts/Suzuki-Miyaura-HTE/build_dataset.py
# ImportError: Missing optional dependency 'openpyxl'.

/private/tmp/condrxnbench-phase0-review-py311/bin/python \
  scripts/Buchwald-Hartwig-HTE/qc_and_pairs.py
# ImportError: Missing optional dependency 'tabulate'.
```

The second reproduction also applies to `scripts/Suzuki-Miyaura-HTE/qc_and_pairs.py`.
No workaround package was added for this review.

## Data invariants and negative checks

| Invariant | Before isolated rebuild | After isolated rebuild | Result |
| --- | ---: | ---: | --- |
| `reaction_records.csv` rows / unique `reaction_id` | 9,900 / 9,900 | 9,900 / 9,900 | PASS |
| `condition_pairs.csv` rows / unique `pair_id` | 116,156 / 116,156 | 116,156 / 116,156 | PASS |
| records SHA-256 | `71ae9d62b48aa088ffd00238b83cbce7acd94b4c741d8192231e1d38ca3a9449` | same | PASS |
| pairs SHA-256 | `c026562beb4c8af7be5e3f74fd61c076b6ade73e442a4f44f2c96e1701daf52b` | same | PASS |
| registry rows / unique `component_id` | 60 / 59 | 60 / 60 | PASS after rebuild |
| registry SHA-256 | `e5a80b4913be4cb57cf3cec61c0d76c9bae1168068acb25f350ee9b742c22b8d` | `d757048413965999a22405c4485486082f0622c3463070097a4a4d9e1e115b40` | expected identity-only change |
| 18 Ahneman + 2 Perera raw-input SHA-256 values | fixed snapshot | identical post-run | PASS |

The only original registry collision was the `ligand=XPhos` ID shared by the
Ahneman and Perera sources.  Rebuilt IDs include `source_dataset` in their
hash input, yielding 60 unique IDs without changing the source labels,
records, pairs, observed-zero counts, or input hashes.  This is consistent
with `metadata/condition_registry/condition_ontology.md` and `docs/api.md`.

## Raw input manifests and acceptance state

The direct verifier recomputed and matched all 20 declared file hashes.  The
candidate manifests have relocated Perera paths to repository-relative paths,
and both currently state
`accepted_after_independent_review_2026-07-31`.

This is not sufficient to pass the Phase 0 raw-manifest promotion gate:

1. `metadata/raw_input_manifests/`, `tests/verify_phase0_inputs.py`, ADR 0003,
   and the runtime requirements are still untracked, so they are not yet a
   version-controlled recovery contract.
2. The linked
   `reports/execution/phase0_candidate_manifest_review_2026-07-31.md` says the
   candidates were `candidate_pending_independent_review`, says their current
   acceptance state is `NOT YET ACCEPTED`, and conditions acceptance on a later
   integrator decision.  The manifest status therefore contradicts its own
   cited evidence.
3. The legacy `data/raw_metadata/perera_raw_input_manifest.json` remains a
   deletion in the candidate worktree.  The replacement content can be
   accepted, but that acceptance must be documented consistently and staged
   without silently restoring or overwriting the user deletion.

## ADR and documentation consistency

ADR 0003 is correctly **Proposed** and its preservation/Parquet assertions are
compatible with the implementation: the verifier checks CSV column order,
row count, primary-key ordering, sentinel counts, boolean columns, and exact
frame values after a temporary PyArrow round-trip.  The source-scoped registry
rule also matches the rebuilt result.

The runtime contract is incomplete: both `read_excel` and `to_markdown` are
called by in-scope commands, but neither `openpyxl` nor `tabulate` is in the
versioned requirements.  Consequently the statement in ADR 0003 that an
independent reviewer can recreate the required environment is not satisfied.
The report `phase0_environment_2026-07-31.md` lists only the eight direct
packages and does not expose this failed full-pipeline check.  Existing README
and status pages appropriately still call Parquet pending for the official
v0.1 release, but must not be used as evidence that this new candidate gate
has passed.

## Promotion decision and required re-review scope

**Do not promote Iteration 1 or 2 / do not mark Phase 0 complete.**  A revision
must make the build and both QC commands reproducible from the declared Python
3.11 contract, reconcile candidate-manifest status with the review record,
and version-control the agreed artifacts.  Then rerun the complete source
build → QC → Core build → `verify_core_v0_1` → `verify_phase0_inputs` →
`verify_parquet_roundtrip` sequence in a new isolated copy, preserving the
same raw, records, and pairs hash checks.  The registry release artifact and
manifest must be rebuilt together so the official output, not only the
builder source, has 60 unique `component_id` values.
