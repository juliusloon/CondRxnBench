# CondRxnBench

English | [中文](README_CN.md)

Reproducible construction and evaluation code for **CondRxnBench**, currently
covering the Ahneman–Doyle Buchwald–Hartwig and Perera Suzuki–Miyaura HTE screens.

## Project status

**Current local release: CondRxnBench-Benchmark v0.1.** It binds Core v0.2,
strict pairs/graphs, S0–S5 manifests, and a source-stratified baseline
leaderboard through [the release manifest](releases/condrxnbench-benchmark-v0_1/manifest.json).
It does not compare absolute yields across sources or fabricate missing reaction structures.

Read [STATUS.md](STATUS.md) for the current hand-off snapshot,
[PROGRESS.md](PROGRESS.md) for the stage history, and [ROADMAP.md](ROADMAP.md)
for ordered next work. Design and data-interface documentation lives in
[docs/](docs/README.md); durable technical decisions live in [adr/](adr/README.md).

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
python3 scripts/build_core_v0_1.py
python3 tests/verify_core_v0_1.py
```

`run_baselines.py` requires the packages in `requirements.txt`. See
`reports/environment_gap.md` when those packages are not available.

The Perera workflow reads the vendored `Data File S1` workbook and supporting
materials PDF only. It retains explicit blank ligand/base settings and observed
zero outcomes, then enumerates all `n_changed_factors = 1` condition pairs
before any cliff threshold is chosen.

## Contributing

1. Keep raw evidence, derived tables, and reports separate; do not overwrite
   vendored raw inputs with derived values.
2. Run the applicable build/QC commands and `python3 tests/verify_core_v0_1.py`
   when changing Core v0.1 inputs, schema, or builders.
3. Update the relevant dataset card or schema document with any semantic change.
4. Update `STATUS.md`, `PROGRESS.md`, and `ROADMAP.md` when a work stage changes;
   record durable design choices as a new ADR.
5. Add a concise entry to `CHANGELOG.md` for user-visible data, API, or behavior
   changes. Do not claim a baseline or external-source result unless it ran or
   was obtained reproducibly.
