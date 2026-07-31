# CondRxnBench

English | [中文](README_CN.md)

Reproducible construction and evaluation code for **CondRxnBench**, currently
covering the Ahneman–Doyle Buchwald–Hartwig and Perera Suzuki–Miyaura HTE screens.

## Current data policy

The derived dataset is rebuilt from the versioned original per-well analytical
exports (`data/raw/ahneman_doyle_rxnpredict/yield_data/plate*.csv`) and SI
plate-layout tables. These inputs were copied from the `doylelab/rxnpredict`
checkout at commit `57e15fdb7f7483c6bf3a601df69f6ac9e5af6965`; see the raw
source README and bundled license.
`data_table.csv` and the response CSVs are intentionally not read by the build
pipeline. The input manifest records exact source paths and SHA-256 checksums.

The 15 × 4 × 3 × 23 design contains 4,140 theoretical main-matrix cells.
Controls are preserved separately rather than being silently discarded.

## Reproduce

```bash
python3 scripts/Buchwald-Hartwig-HTE/build_dataset.py
python3 scripts/Buchwald-Hartwig-HTE/qc_and_pairs.py
python3 scripts/Buchwald-Hartwig-HTE/run_baselines.py
python3 scripts/Suzuki-Miyaura-HTE/build_dataset.py
python3 scripts/Suzuki-Miyaura-HTE/qc_and_pairs.py
```

`run_baselines.py` requires the packages in `requirements.txt`. See
`reports/environment_gap.md` when those packages are not available.

The Perera workflow reads the vendored `Data File S1` workbook and supporting
materials PDF only. It retains explicit blank ligand/base settings and observed
zero outcomes, then enumerates all `n_changed_factors = 1` condition pairs
before any cliff threshold is chosen.
