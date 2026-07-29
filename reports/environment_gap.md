# Environment / software gap

The data reconstruction and QC scripts run with the currently available Python
runtime (`pandas`, `numpy`). The requested molecular-fingerprint and random
forest baselines deliberately do **not** fall back to non-chemical proxies.

Install later, in a dedicated environment:

- Python 3.10--3.12 (the currently visible Miniforge Python is 3.13 and its
  `conda` command crashes in this desktop context).
- `rdkit` for validated molecular parsing and ECFP4 fingerprints.
- `scikit-learn` for Ridge, random forest, metrics, and split helpers.
- `pyarrow` to emit the planned Parquet deliverables (CSV is used for the
  present auditable interim output).
- `ord-schema` and `ord-interface` before ORD/CRD ingestion; no ORD data has
  been parsed in this first literature-specific phase.
- `git` is available; GitHub CLI/authentication or the GitHub connector is not
  available, so a remote GitHub repository cannot yet be created/pushed from
  this workspace.

Suggested creation command once the environment issue is resolved:

```bash
conda create -n condrxnbench -c conda-forge python=3.11 rdkit scikit-learn pandas numpy pyarrow ord-schema ord-interface
```

