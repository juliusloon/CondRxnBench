# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CondRxnBench is a benchmark for reproducible construction and evaluation of conditional reaction datasets from high-throughput experimentation (HTE). The current phase focuses on reconstructing the Ahneman–Doyle Buchwald–Hartwig HTE screen from raw SI layout tables and per-well LC/UV analytical exports — never from the derived `data_table.csv`.

The 15 × 4 × 3 × 23 factorial design yields 4,140 main-matrix cells. Controls (additive-free, aryl-halide-free, blank) are preserved separately, not discarded.

## Commands

### Environment setup

```bash
conda create -n condrxnbench -c conda-forge python=3.11 rdkit scikit-learn pandas numpy pyarrow
conda activate condrxnbench
```

### Rebuild the derived dataset from raw sources

```bash
python scripts/build_ahneman_dataset.py
```

Outputs:
- `data/processed/ahneman_buchwald_hartwig_main_matrix.csv`
- `data/processed/ahneman_buchwald_hartwig_controls.csv`
- `data/raw_metadata/ahneman_raw_input_manifest.json` (SHA-256 checksums of every input file)

### Run QC and build single-factor pairs

```bash
python scripts/qc_and_pairs.py
```

Outputs:
- `reports/ahneman_qc_report.md` and `reports/ahneman_qc_summary.json`
- `data/processed/ahneman_buchwald_hartwig_single_factor_pairs.csv`

### Run yield baselines

```bash
python scripts/run_baselines.py
```

Requires all packages in `requirements.txt`. Models: condition-only Ridge, substrate ECFP4 + condition Ridge, substrate ECFP4 + condition Random Forest. Two splits: random 80/20 and additive-component OOD.

## Architecture

### Data pipeline (scripts/)

`build_ahneman_dataset.py` → `qc_and_pairs.py` → `run_baselines.py`. Each script reads from `data/processed/` or `data/raw/` and writes to `data/processed/`, `reports/`, or `results/`. No script mutates another script's inputs.

**`build_ahneman_dataset.py`** — Reads SI layout tables (`layout/Table_S1.csv`, `Table_S2.csv`), compound SMILES lists (`smiles/*.csv`), and raw per-plate quadrant exports (`yield_data/plate{1,2,3}.{1..4}.csv`). Joins by physical well location (row/col, plate/block). Outputs main-matrix and controls CSVs plus a checksum manifest.

**`qc_and_pairs.py`** — Reads the main-matrix CSV. Builds exhaustive single-factor perturbation pairs (fix `reaction_group_id`, fix 2 of {catalyst_system, base, additive}, vary exactly 1). Produces QC markdown report and pair table.

**`run_baselines.py`** — Reads the main-matrix CSV. Computes ECFP4 fingerprints (RDKit Morgan radius=2, 2048 bits) from `aryl_halide_smiles`. One-hot encodes conditions (`catalyst_system`, `base`, `additive`). Evaluates Ridge and Random Forest regressors on random and additive-component OOD splits.

### Data layout (data/)

- `data/raw/ahneman_doyle_rxnpredict/` — versioned copy of the `doylelab/rxnpredict` subset (commit `57e15fdb`). Contains `layout/`, `smiles/`, `yield_data/` subdirectories.
- `data/processed/` — derived CSVs produced by the scripts.
- `data/raw_metadata/` — input manifest with checksums.
- `data/interim/` — scratch space.

### Key domain rules

1. Zero `product_scaled` is an observed failed outcome; `NA` is an unobserved analytical measurement. Never conflate the two.
2. The four Pd–ligand precatalysts are represented as `catalyst_system`, not as independent Pd and ligand columns.
3. A condition pair fixes `reaction_group_id` (aryl halide identity) and changes exactly one of `catalyst_system`, `base`, or `additive`. Substrate perturbation is a separate task.
4. OOD test components are sampled once with a recorded seed (`SEED = 20260729`), never chosen by outcome.

### Report conventions

- QC reports go to `reports/` as markdown + JSON summary.
- Baseline results go to `results/` as CSV + protocol JSON.
- `docs/ord_crd_mapping.md` documents the CRD (CondRxnBench reaction data) field mapping and the gap to a full ORD export.
