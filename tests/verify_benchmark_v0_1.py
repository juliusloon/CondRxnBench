#!/usr/bin/env python3
"""Contract checks for strict-only Benchmark v0.1 candidate artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "data" / "processed" / "core_v0_2"
V01 = ROOT / "data" / "processed" / "core_v0_1"
AHN = "ahneman_doyle_buchwald_hartwig_2018"
PER = "perera_suzuki_miyaura_2018"
BASELINE = {AHN: {"catalyst_system": 6187, "base": 4124, "additive": 45365}, PER: {"ligand": 31680, "base": 20160, "solvent_1": 8640}}


def sha_text(path: Path) -> str:
    return hashlib.sha256(path.read_text().encode()).hexdigest()


def csv_parquet(out: Path, name: str, meta: dict[str, object]) -> pd.DataFrame:
    csv = pd.read_csv(out / f"{name}.csv", keep_default_na=False, na_filter=False)
    parquet = pq.read_table(out / f"{name}.parquet").to_pandas()
    assert list(csv.columns) == list(parquet.columns) == meta["columns"], name
    assert len(csv) == len(parquet) == meta["rows"], name
    return parquet


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--out-dir", type=Path, default=ROOT / "data" / "processed" / "benchmark_v0_1")
    out = parser.parse_args().out_dir.resolve(); manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["status"] == "candidate_not_promoted" and manifest["strict_pair_count"] == 116156
    assert manifest["input_core_manifest_sha256"] == sha_text(CORE / "manifest.json")
    assert not any((out / name).exists() for name in ("extended_pairs.csv", "splits.csv", "model_results.csv"))
    tables = {name: csv_parquet(out, name, meta) for name, meta in manifest["tables"].items()}
    groups, pairs = tables["record_groups"], tables["strict_pairs"]
    nodes, edges, ledger, summary = tables["graph_nodes"], tables["graph_edges"], tables["pair_reconciliation"], tables["graph_summary"]
    records = pd.read_csv(CORE / "reaction_records.csv", keep_default_na=False, na_filter=False, low_memory=False)
    records = records.loc[records.record_class.eq("main_matrix")].copy().set_index("reaction_id")
    assert len(groups) == len(records) == 9900 and groups.reaction_id.is_unique
    assert groups.groupby("source_dataset").size().to_dict() == {AHN: 4140, PER: 5760}
    assert groups.group_confidence.eq("source_design_defined_not_structure_verified").all()
    assert groups.scaffold_group_id.eq("not_supported").all() and groups.template_group_id.eq("not_supported").all()
    assert len(pairs) == 116156 and pairs.pair_id.is_unique
    assert pairs.groupby(["source_dataset", "changed_factor"]).size().to_dict() == {(source, factor): count for source, values in BASELINE.items() for factor, count in values.items()}
    assert pairs.n_changed_factors.eq(1).all() and (pairs.reaction_id_a < pairs.reaction_id_b).all()
    assert not (pairs.reaction_id_a == pairs.reaction_id_b).any()
    for row in pairs.itertuples(index=False):
        a, b = records.loc[row.reaction_id_a], records.loc[row.reaction_id_b]
        assert a.source_dataset == b.source_dataset == row.source_dataset
        assert f"{a.source_dataset}::{a.reaction_group_id}" == row.strict_reaction_group_id == f"{b.source_dataset}::{b.reaction_group_id}"
        assert bool(a.yield_observed) and bool(b.yield_observed)
        vector = json.loads(row.changed_factor_vector)
        assert list(vector) == [row.changed_factor] and row.abs_delta_yield == abs(row.delta_yield)
        assert row.cliff_label_primary == ("invariant" if row.abs_delta_yield <= 10 else "moderate" if row.abs_delta_yield < 30 else "strong")
        assert bool(row.cliff_strong_40pp) <= bool(row.cliff_strong_20pp)
    assert set(ledger.columns) >= {"source_dataset", "changed_factor", "v0_1_baseline_count", "current_count", "endpoint_intersection_count", "v0_1_only_count", "current_only_count", "reason_code", "evidence_path"}
    assert (ledger.v0_1_baseline_count == ledger.current_count).all() and set(ledger.reason_code) <= {"identical_pair_universe", "perera_raw_solvent_identity_preserved", "accepted_bug_fix_adr"}
    assert len(nodes) == 9900 and nodes.reaction_id.is_unique and len(edges) == len(pairs) and edges.pair_id.is_unique
    assert set(edges.pair_id) == set(pairs.pair_id) and not edges.canonical_undirected_key.duplicated().any()
    assert len(summary) == 30 and (summary.node_count > 0).all() and (summary.edge_count >= 0).all()
    for item in summary.itertuples(index=False):
        graph_nodes = set(nodes.loc[nodes.graph_id.eq(item.graph_id), "reaction_id"])
        expected = set(records.loc[(records.source_dataset.eq(item.source_dataset)) & ((records.source_dataset + "::" + records.reaction_group_id).eq(item.strict_reaction_group_id))].index)
        assert graph_nodes == expected
        graph_edges = edges.loc[edges.graph_id.eq(item.graph_id)]
        assert len(graph_edges) == item.edge_count
        graph_file = out / "group_json" / f"{item.graph_id}.json"; graph = json.loads(graph_file.read_text())
        assert {"graph_id", "source_dataset", "strict_reaction_group_id", "group_definition_version", "graph_version", "nodes", "edges"} <= set(graph)
        assert {node["reaction_id"] for node in graph["nodes"]} == graph_nodes
        assert {edge["pair_id"] for edge in graph["edges"]} == set(graph_edges.pair_id)
    print("Benchmark v0.1 strict candidate verification passed: full pair universe, reconciliation, and graph bijection.")


if __name__ == "__main__":
    main()
