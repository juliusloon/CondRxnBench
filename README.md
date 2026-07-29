# CondRxnBench

Reproducible construction and evaluation code for **CondRxnBench**, starting
with the Ahneman–Doyle Buchwald–Hartwig HTE screen.

## Current data policy

The derived dataset is rebuilt from the original per-well analytical exports
(`yield_data/plate*.csv`) and the SI plate-layout tables (`layout/Table_S1.csv`,
`layout/Table_S2.csv`) in the locally supplied `doylelab/rxnpredict` checkout.
`data_table.csv` and the response CSVs are intentionally not read by the build
pipeline. The input manifest records exact source paths and SHA-256 checksums.

The 15 × 4 × 3 × 23 design contains 4,140 theoretical main-matrix cells.
Controls are preserved separately rather than being silently discarded.

## Reproduce

```bash
python scripts/build_ahneman_dataset.py --source-root /Volumes/Jupetit/rxnpredict
python scripts/run_baselines.py
```

`run_baselines.py` requires the packages in `requirements.txt`. See
`reports/environment_gap.md` when those packages are not available.

