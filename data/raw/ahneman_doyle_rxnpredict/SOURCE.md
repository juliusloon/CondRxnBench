# Source snapshot: Ahneman--Doyle Buchwald--Hartwig HTE

This directory is the minimal, versioned input subset required to reconstruct
the Ahneman--Doyle HTE dataset in this repository.

- Upstream repository: <https://github.com/doylelab/rxnpredict>
- Upstream commit copied: `57e15fdb7f7483c6bf3a601df69f6ac9e5af6965`
- Retrieved from local upstream checkout: 2026-07-29
- License: copied verbatim as `LICENSE.txt` (MIT license in the upstream
  repository).

Included inputs:

- `yield_data/plate*.csv`: raw, per-well LC/UV analytical exports.
- `layout/Table_S1.csv`, `layout/Table_S2.csv`: SI plate layouts.
- `smiles/*-list.csv`: component identifiers and structures required to map
  wells to the factorial experimental design.

Intentionally excluded: `data_table.csv`, `Response/Scaled_dataset.csv`,
`Response/Unscaled_dataset.csv`, and descriptor/model outputs. Those are
derived data products, not reconstruction inputs.
