#!/usr/bin/env python3
"""Independent release checks for CondRxnBench-Core v0.1."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed" / "core_v0_1"


def main() -> None:
    records = pd.read_csv(OUT / "reaction_records.csv")
    pairs = pd.read_csv(OUT / "condition_pairs.csv")
    manifest = json.loads((OUT / "manifest.json").read_text())

    assert len(records) == 9900 and records.reaction_id.is_unique
    assert records.groupby("source_dataset").size().to_dict() == {
        "ahneman_doyle_buchwald_hartwig_2018": 4140,
        "perera_suzuki_miyaura_2018": 5760,
    }
    observed = records.loc[records.yield_observed]
    assert observed.yield_percent.between(0, 100).all()
    assert (records.zero_yield == (records.yield_observed & records.yield_percent.eq(0))).all()
    assert set(records.success_label) == {"not_assigned"}

    assert len(pairs) == 116156 and pairs.pair_id.is_unique
    assert (pairs.n_changed_factors == 1).all()
    assert set(pairs.cliff_label) == {"not_assigned"}
    endpoint = records.set_index("reaction_id")[["reaction_group_id", "source_dataset", "yield_observed"]]
    group_a = pairs.reaction_id_a.map(endpoint.reaction_group_id)
    group_b = pairs.reaction_id_b.map(endpoint.reaction_group_id)
    source_a = pairs.reaction_id_a.map(endpoint.source_dataset)
    source_b = pairs.reaction_id_b.map(endpoint.source_dataset)
    observed_a = pairs.reaction_id_a.map(endpoint.yield_observed)
    observed_b = pairs.reaction_id_b.map(endpoint.yield_observed)
    assert (pairs.reaction_group_id == group_a).all() and (group_a == group_b).all()
    assert (pairs.source_dataset == source_a).all() and (source_a == source_b).all()
    assert observed_a.all() and observed_b.all()
    assert manifest["record_count"] == len(records) and manifest["pair_count"] == len(pairs)
    print("Core v0.1 verification passed: 9,900 records; 116,156 strict pairs.")


if __name__ == "__main__":
    main()
