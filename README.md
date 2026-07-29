# CondRxnBench

Reproducible construction and evaluation code for **CondRxnBench**, starting
with the Ahneman–Doyle Buchwald–Hartwig HTE screen.

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
python scripts/build_ahneman_dataset.py
python scripts/run_baselines.py
```

`run_baselines.py` requires the packages in `requirements.txt`. See
`reports/environment_gap.md` when those packages are not available.
