#!/usr/bin/env python3
"""Build the strict-only Benchmark v0.1 candidate from Core v0.2.

The build is intentionally limited to source-design groups, strict pair
universe, and graph diagnostics.  It does not create splits or model outputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from itertools import combinations
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "data" / "processed" / "core_v0_2"
V01 = ROOT / "data" / "processed" / "core_v0_1"
VERSION = "CondRxnBench-Benchmark-v0.1-proposed.1"
AHN = "ahneman_doyle_buchwald_hartwig_2018"
PER = "perera_suzuki_miyaura_2018"
FACTORS = {AHN: ["catalyst_system", "base", "additive"], PER: ["ligand", "base", "solvent_1"]}
BASELINE = {AHN: {"catalyst_system": 6187, "base": 4124, "additive": 45365}, PER: {"ligand": 31680, "base": 20160, "solvent_1": 8640}}


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def read_core() -> pd.DataFrame:
    manifest = json.loads((CORE / "manifest.json").read_text())
    if manifest["status"] != "candidate_not_promoted":
        raise ValueError("unexpected Core v0.2 input status")
    records = pd.read_csv(CORE / "reaction_records.csv", keep_default_na=False, na_filter=False, low_memory=False)
    registry = pd.read_csv(CORE / "condition_registry.csv", keep_default_na=False, na_filter=False).set_index("component_id")
    records = records.loc[records.record_class == "main_matrix"].copy()
    records["design_group_id"] = records.source_dataset + "::" + records.reaction_group_id
    records["strict_reaction_group_id"] = records["design_group_id"]
    for source, factors in FACTORS.items():
        idx = records.source_dataset.eq(source)
        for factor in factors:
            if source == PER:
                records.loc[idx, f"_factor_{factor}"] = records.loc[idx, "condition_component_refs"].map(
                    lambda value, role=factor: registry.at[json.loads(value)[role], "raw_value"]
                )
            else:
                records.loc[idx, f"_factor_{factor}"] = records.loc[idx, factor]
    return records


def cliff(abs_delta: float) -> tuple[str, bool, bool]:
    if abs_delta <= 10:
        label = "invariant"
    elif abs_delta < 30:
        label = "moderate"
    else:
        label = "strong"
    return label, abs_delta >= 20, abs_delta >= 40


def build_pairs(records: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for source, factors in FACTORS.items():
        source_records = records.loc[records.source_dataset.eq(source) & records.yield_observed.astype(bool)]
        for factor in factors:
            others = [f"_factor_{item}" for item in factors if item != factor]
            grouping = ["strict_reaction_group_id", *others]
            for _, frame in source_records.groupby(grouping, sort=True, dropna=False):
                # Equal factor levels do not form strict one-factor comparisons.
                ordered = frame.sort_values("reaction_id").to_dict("records")
                for left, right in combinations(ordered, 2):
                    lv, rv = left[f"_factor_{factor}"], right[f"_factor_{factor}"]
                    if lv == rv:
                        continue
                    left_id, right_id = left["reaction_id"], right["reaction_id"]
                    vector = {factor: {"a": lv, "b": rv}}
                    delta = float(right["yield_percent"]) - float(left["yield_percent"])
                    label, strong20, strong40 = cliff(abs(delta))
                    token = f"{source}|{left['strict_reaction_group_id']}|{factor}|{left_id}|{right_id}"
                    rows.append({
                        "pair_id": "BPAIR-" + digest(token)[:20], "source_dataset": source,
                        "design_group_id": left["design_group_id"], "strict_reaction_group_id": left["strict_reaction_group_id"],
                        "reaction_id_a": left_id, "reaction_id_b": right_id, "changed_factor": factor,
                        "changed_factor_vector": canonical(vector), "n_changed_factors": 1,
                        "yield_a": float(left["yield_percent"]), "yield_b": float(right["yield_percent"]),
                        "delta_yield": delta, "abs_delta_yield": abs(delta),
                        "pair_definition_version": "benchmark_v0_1_strict_discrete_v1",
                        "group_definition_version": "benchmark_v0_1_source_design_group_v1",
                        "cliff_label_primary": label, "cliff_strong_20pp": strong20, "cliff_strong_40pp": strong40,
                    })
    pairs = pd.DataFrame(rows).sort_values(["source_dataset", "strict_reaction_group_id", "changed_factor", "reaction_id_a", "reaction_id_b"]).reset_index(drop=True)
    if not pairs.pair_id.is_unique:
        raise ValueError("pair ID collision")
    return pairs


def reconciliation(pairs: pd.DataFrame) -> pd.DataFrame:
    old = pd.read_csv(V01 / "condition_pairs.csv", keep_default_na=False, na_filter=False)
    rows = []
    for source, factors in BASELINE.items():
        for factor, baseline in factors.items():
            current = pairs.loc[(pairs.source_dataset == source) & (pairs.changed_factor == factor)]
            legacy = old.loc[(old.source_dataset == source) & (old.changed_factor == factor)]
            current_keys = set(zip(current.reaction_id_a, current.reaction_id_b))
            legacy_keys = set(zip(legacy.reaction_id_a, legacy.reaction_id_b))
            same = current_keys == legacy_keys
            reason = "identical_pair_universe" if same else "perera_raw_solvent_identity_preserved" if source == PER and factor == "solvent_1" else "accepted_bug_fix_adr"
            rows.append({"source_dataset": source, "changed_factor": factor, "v0_1_baseline_count": baseline,
                         "current_count": len(current), "endpoint_intersection_count": len(current_keys & legacy_keys),
                         "v0_1_only_count": len(legacy_keys - current_keys), "current_only_count": len(current_keys - legacy_keys),
                         "reason_code": reason, "evidence_path": "data/processed/core_v0_1/condition_pairs.csv"})
    ledger = pd.DataFrame(rows)
    if (ledger.v0_1_baseline_count != ledger.current_count).any():
        raise ValueError("unexplained strict-pair count reconciliation")
    return ledger


def build_graphs(records: pd.DataFrame, pairs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[dict[str, object]]]:
    nodes, edges, summaries, graphs = [], [], [], []
    for (source, group), group_records in records.groupby(["source_dataset", "strict_reaction_group_id"], sort=True):
        graph_id = "BGRAPH-" + digest(f"{source}|{group}")[:20]
        reaction_ids = sorted(group_records.reaction_id.tolist())
        for reaction_id in reaction_ids:
            nodes.append({"graph_id": graph_id, "source_dataset": source, "strict_reaction_group_id": group,
                          "group_definition_version": "benchmark_v0_1_source_design_group_v1", "reaction_id": reaction_id})
        group_pairs = pairs.loc[(pairs.source_dataset == source) & (pairs.strict_reaction_group_id == group)]
        edge_payload = []
        degree = {reaction_id: 0 for reaction_id in reaction_ids}
        for row in group_pairs.to_dict("records"):
            key = f"{row['reaction_id_a']}::{row['reaction_id_b']}"
            edge = {"graph_id": graph_id, "pair_id": row["pair_id"], "reaction_id_a": row["reaction_id_a"], "reaction_id_b": row["reaction_id_b"],
                    "source_dataset": source, "strict_reaction_group_id": group, "group_definition_version": "benchmark_v0_1_source_design_group_v1",
                    "changed_factor": row["changed_factor"], "canonical_undirected_key": key}
            edges.append(edge); edge_payload.append({k: edge[k] for k in ("pair_id", "reaction_id_a", "reaction_id_b", "changed_factor", "canonical_undirected_key")})
            degree[row["reaction_id_a"]] += 1; degree[row["reaction_id_b"]] += 1
        # Union-find is sufficient for the component diagnostic without adding a graph dependency.
        parent = {node: node for node in reaction_ids}
        def find(node: str) -> str:
            while parent[node] != node:
                parent[node] = parent[parent[node]]; node = parent[node]
            return node
        for edge in edge_payload:
            a, b = find(edge["reaction_id_a"]), find(edge["reaction_id_b"])
            if a != b: parent[a] = b
        summaries.append({"graph_id": graph_id, "source_dataset": source, "strict_reaction_group_id": group, "node_count": len(reaction_ids), "edge_count": len(edge_payload), "connected_components": len({find(n) for n in reaction_ids}), "isolated_node_count": sum(value == 0 for value in degree.values()), "degree_min": min(degree.values()), "degree_max": max(degree.values()), "edge_count_by_changed_factor": canonical(group_pairs.changed_factor.value_counts().sort_index().to_dict())})
        graphs.append({"graph_id": graph_id, "source_dataset": source, "strict_reaction_group_id": group, "group_definition_version": "benchmark_v0_1_source_design_group_v1", "graph_version": "benchmark_v0_1_strict_group_json_v1", "nodes": [{"reaction_id": value} for value in reaction_ids], "edges": edge_payload})
    return pd.DataFrame(nodes), pd.DataFrame(edges), pd.DataFrame(summaries), graphs


def write(frame: pd.DataFrame, name: str, out: Path) -> dict[str, object]:
    csv = out / f"{name}.csv"; parquet = out / f"{name}.parquet"
    frame.to_csv(csv, index=False, lineterminator="\n")
    pq.write_table(pa.Table.from_pandas(frame, preserve_index=False), parquet, compression="zstd")
    return {"rows": len(frame), "csv_sha256": digest(csv.read_bytes().hex()), "parquet_sha256": digest(parquet.read_bytes().hex()), "columns": frame.columns.tolist()}


def build(out: Path) -> dict[str, object]:
    records = read_core(); pairs = build_pairs(records); ledger = reconciliation(pairs); nodes, edges, summary, graphs = build_graphs(records, pairs)
    group_columns = ["reaction_id", "source_dataset", "design_group_id", "strict_reaction_group_id"]
    groups = records[group_columns].copy(); groups["group_definition_version"] = "benchmark_v0_1_source_design_group_v1"; groups["group_confidence"] = "source_design_defined_not_structure_verified"; groups["scaffold_group_id"] = "not_supported"; groups["scaffold_group_reason"] = "incomplete_source_structure_coverage"; groups["template_group_id"] = "not_supported"; groups["template_group_reason"] = "no_complete_verified_reaction_representation"
    tables = {"record_groups": groups, "strict_pairs": pairs, "pair_reconciliation": ledger, "graph_nodes": nodes, "graph_edges": edges, "graph_summary": summary}
    if out.exists(): shutil.rmtree(out)
    (out / "group_json").mkdir(parents=True)
    manifest_tables = {name: write(frame, name, out) for name, frame in tables.items()}
    for graph in graphs:
        (out / "group_json" / f"{graph['graph_id']}.json").write_text(json.dumps(graph, sort_keys=True, separators=(",", ":")) + "\n")
    universe = pairs[["source_dataset", "strict_reaction_group_id", "reaction_id_a", "reaction_id_b", "changed_factor"]].to_dict("records")
    return {"release": VERSION, "status": "candidate_not_promoted", "input_core_manifest_sha256": digest((CORE / "manifest.json").read_text()), "strict_pair_universe_sha256": digest(canonical(universe)), "strict_pair_count": len(pairs), "pair_baseline_count": 116156, "graph_count": len(graphs), "tables": manifest_tables, "unimplemented_by_design": ["extended_pairs", "extended_graphs", "splits", "model_results"]}


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--out-dir", type=Path, default=ROOT / "data" / "processed" / "benchmark_v0_1")
    args = parser.parse_args(); manifest = build(args.out_dir.resolve()); (args.out_dir.resolve() / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n"); print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
