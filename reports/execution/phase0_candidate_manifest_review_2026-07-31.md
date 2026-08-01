# Phase 0 candidate raw-input manifest — independent review

Date: 2026-07-31  
Role: `evidence_auditor`  
Review scope: read-only review of the two v0.2 candidate manifests and
`tests/verify_phase0_inputs.py`.  No raw file, candidate manifest, source
builder, or processed dataset was modified by this review.

## Verdict

**Candidate content: PASS.** All 20 declared relative paths exist, every
SHA-256 matches its current raw file, both candidate source pins agree with
the project source evidence, and their file sets exactly cover the respective
source builders' raw inputs.  The direct verifier passes.

**Raw-manifest evidence gap: remediated in content, but not yet formally
closed.** The blocker can be lifted *after* the integrator records this
independent PASS as an acceptance/promotion, changes the manifests out of
`candidate_pending_independent_review` according to the chosen versioning
policy, and version-controls the new manifests and verifier.  At this audit
snapshot those artifacts are untracked, and the former Perera manifest remains
deleted, so it would be premature to state that the repository currently has
an accepted immutable baseline.  No raw-byte discrepancy remains.

## Checks and evidence

| Check | Result | Evidence |
| --- | --- | --- |
| Candidate verifier | PASS | `python3 tests/verify_phase0_inputs.py` printed `Phase 0 candidate input-manifest verification passed: 20 raw inputs.` |
| Path and hash hygiene | PASS | 20 entries, 20 unique paths, all relative with no `..` segment, all hashes match lowercase `[0-9a-f]{64}`. |
| Ahneman candidate count and coverage | PASS | 18 entries exactly equal the 12 `yield_data/plate{1..3}.{1..4}.csv`, 2 `layout/Table_S*.csv`, and 4 `smiles/*-list.csv` paths read by `scripts/Buchwald-Hartwig-HTE/build_dataset.py`. No missing or extra file. |
| Perera candidate count and coverage | PASS | 2 entries exactly equal `aap9112_Data_File_S1.xlsx` and `aap9112_perera_sm.pdf`, which `scripts/Suzuki-Miyaura-HTE/build_dataset.py` resolves from `--source-root`. No missing or extra file. |
| Ahneman source pin | PASS | Candidate pin `57e15fdb7f7483c6bf3a601df69f6ac9e5af6965` equals `data/raw/ahneman_doyle_rxnpredict/SOURCE.md` (`Upstream commit copied`). |
| Perera source pin and historical evidence | PASS | Candidate pin `d9e6b87ce1b881978490d68bfc00021e3b48127a` equals `data/raw/perera_suzuki_miyaura/SOURCE.md`. Its two hashes equal both that source document and `HEAD:data/raw_metadata/perera_raw_input_manifest.json`. Candidate expects 5,760 rows and 16 columns; direct workbook read reproduced 5,760 x 16 with 5,760 unique `Reaction_No`. |
| Raw immutability during review | PASS | `git diff --quiet -- data/raw` passed. |
| Current version-control/acceptance state | NOT YET ACCEPTED | Both candidates and `tests/verify_phase0_inputs.py` are untracked; both JSON files state `candidate_pending_independent_review`. The old tracked Perera manifest is still `D data/raw_metadata/perera_raw_input_manifest.json`. |

## Exact verified hashes

### Perera (2 inputs)

| Path | SHA-256 |
| --- | --- |
| `data/raw/perera_suzuki_miyaura/aap9112_Data_File_S1.xlsx` | `a869e020ba31bd5676c67a4791c3b7384711b5216de6af444b8cd0a24c284640` |
| `data/raw/perera_suzuki_miyaura/aap9112_perera_sm.pdf` | `54e505db0b1e7200552dae79dfff5398d1d2cbae08fcbfe472239aaa86c81b30` |

### Ahneman (18 inputs)

The candidate's 18 entries all match their raw-file hashes; the verified path
set is precisely:

```text
data/raw/ahneman_doyle_rxnpredict/yield_data/plate1.1.csv
data/raw/ahneman_doyle_rxnpredict/yield_data/plate1.2.csv
data/raw/ahneman_doyle_rxnpredict/yield_data/plate1.3.csv
data/raw/ahneman_doyle_rxnpredict/yield_data/plate1.4.csv
data/raw/ahneman_doyle_rxnpredict/yield_data/plate2.1.csv
data/raw/ahneman_doyle_rxnpredict/yield_data/plate2.2.csv
data/raw/ahneman_doyle_rxnpredict/yield_data/plate2.3.csv
data/raw/ahneman_doyle_rxnpredict/yield_data/plate2.4.csv
data/raw/ahneman_doyle_rxnpredict/yield_data/plate3.1.csv
data/raw/ahneman_doyle_rxnpredict/yield_data/plate3.2.csv
data/raw/ahneman_doyle_rxnpredict/yield_data/plate3.3.csv
data/raw/ahneman_doyle_rxnpredict/yield_data/plate3.4.csv
data/raw/ahneman_doyle_rxnpredict/layout/Table_S1.csv
data/raw/ahneman_doyle_rxnpredict/layout/Table_S2.csv
data/raw/ahneman_doyle_rxnpredict/smiles/additive-list.csv
data/raw/ahneman_doyle_rxnpredict/smiles/aryl_halide-list.csv
data/raw/ahneman_doyle_rxnpredict/smiles/base-list.csv
data/raw/ahneman_doyle_rxnpredict/smiles/ligand-list.csv
```

The candidate JSON is the authoritative exact 18-hash listing; the direct
verifier independently recomputed each value rather than relying on that
listing alone.

## Verifier review

`tests/verify_phase0_inputs.py` is correct for these two reviewed candidates:
it loads both explicit manifests, requires schema `1.0` and the candidate
status, confirms each listed path is a file, recomputes every SHA-256, and
asserts the total is 20.

Its scope is intentionally narrower than this review: it does **not** assert
per-manifest entry counts, uniqueness, no path traversal, exact builder-file
sets, source commits, Perera workbook dimensions, or historical-manifest
agreement.  Those gaps did not cause a failure here because the independent
checks above established each of them, but they should not be inferred from a
green verifier alone.

The Perera candidate changes only wording from historical input-policy
`sole tabular input` to `only tabular input`; it retains the same source,
hashes, sheet, and 5,760 x 16 constraints.  This is semantically consistent,
not a raw-evidence change.

## Reproduction commands

Run from the repository root:

```bash
python3 tests/verify_phase0_inputs.py
git diff --quiet -- data/raw
git show HEAD:data/raw_metadata/perera_raw_input_manifest.json
git status --short metadata/raw_input_manifests tests/verify_phase0_inputs.py \
  data/raw data/raw_metadata
```

For an independent all-path comparison, use the candidate manifests together
with the builders' explicit file declarations.  The important code anchors are
`scripts/Buchwald-Hartwig-HTE/build_dataset.py` (`read_wells`,
`read_compounds`, `build_layout`) and
`scripts/Suzuki-Miyaura-HTE/build_dataset.py` (`source_root`, `xlsx`, `pdf`).

## Promotion recommendation

The integrator may accept these candidates as the new raw input baseline;
there is no evidence-based reason to keep the *content* blocker open.  Before
declaring Phase 0 raw-manifest hard acceptance, record the acceptance decision
in the state/maintenance artifacts, make the candidate status immutable under
the selected policy, and ensure the manifests/verifier are version-controlled.
Do not restore, overwrite, or otherwise modify `data/raw/` as part of that
promotion.
