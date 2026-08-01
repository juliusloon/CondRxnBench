#!/usr/bin/env python3
"""Evidence audit for Phase 3 bias, confounding, and leakage gates."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "data" / "processed" / "core_v0_2"
BENCH = ROOT / "data" / "processed" / "benchmark_v0_1"
OUT = ROOT / "reports" / "execution" / "phase3_bias_leakage_audit_2026-07-31.json"


def main() -> None:
    records = pd.read_csv(CORE / "reaction_records.csv", keep_default_na=False, na_filter=False, low_memory=False)
    controls = pd.read_csv(CORE / "control_records.csv", keep_default_na=False, na_filter=False, low_memory=False)
    pairs = pd.read_csv(BENCH / "strict_pairs.csv", keep_default_na=False, na_filter=False, low_memory=False)
    nodes = pd.read_csv(BENCH / "graph_nodes.csv", keep_default_na=False, na_filter=False)
    edges = pd.read_csv(BENCH / "graph_edges.csv", keep_default_na=False, na_filter=False)
    main_records = records.loc[records.record_class.eq("main_matrix")].copy()
    main_records["yield_percent"] = pd.to_numeric(main_records["yield_percent"], errors="coerce")
    observed = main_records.loc[main_records.yield_observed.astype(bool)].copy()
    index = main_records.set_index("reaction_id")
    degree = pd.concat([pairs.reaction_id_a, pairs.reaction_id_b]).value_counts()
    # A positive control mutates a valid pair into cross-source leakage; a negative
    # control retains an actual edge. Both use the same predicate as the audit.
    def pair_valid(row: pd.Series) -> bool:
        a, b = index.loc[row.reaction_id_a], index.loc[row.reaction_id_b]
        return bool(a.yield_observed) and bool(b.yield_observed) and a.source_dataset == b.source_dataset == row.source_dataset and a.reaction_group_id == b.reaction_group_id and row.reaction_id_a != row.reaction_id_b
    positive = pairs.iloc[0].copy(); positive["source_dataset"] = "synthetic_cross_source"
    report = {
        "scope": "strict candidate only; no pretraining, split, or model result",
        "checks": {
            "identity_group_pair_leakage": {"status": "tested", "invalid_pairs": int(sum(not pair_valid(row) for _, row in pairs.iterrows())), "duplicate_pair_ids": int(pairs.pair_id.duplicated().sum()), "duplicate_graph_edge_keys": int(edges.canonical_undirected_key.duplicated().sum()), "cross_partition_leakage": "not_applicable_no_splits"},
            "audit_tool_controls": {"status": "tested", "positive_cross_source_detected": not pair_valid(positive), "negative_valid_pair_accepted": pair_valid(pairs.iloc[0])},
            "measurement_separation": {"status": "tested", "source_yield_type_counts": {f"{source}::{yield_type}": int(count) for (source, yield_type), count in observed.groupby(["source_dataset", "yield_type"]).size().items()}, "control_main_overlap": int(set(controls.reaction_id) & set(main_records.reaction_id) != set())},
            "missingness_and_zero_pattern": {"status": "tested", "by_source": main_records.groupby("source_dataset").agg(records=("reaction_id", "size"), observed=("yield_observed", "sum"), zero=("zero_yield", "sum")).to_dict("index")},
            "design_position_effects": {"status": "tested", "ahneman_plate_means": observed.loc[observed.source_dataset.str.contains("ahneman")].groupby("plate_id").yield_percent.agg(["count", "mean"]).to_dict("index"), "perera_batch_levels": sorted(observed.loc[observed.source_dataset.str.contains("perera"), "batch_id"].astype(str).unique().tolist())},
            "condition_frequency_and_covariation": {"status": "tested", "ahneman_catalyst_ligand_pairs": int(observed.loc[observed.source_dataset.str.contains("ahneman"), ["catalyst_system", "ligand"]].drop_duplicates().shape[0]), "perera_solvent_labels": sorted(observed.loc[observed.source_dataset.str.contains("perera"), "solvent_1"].astype(str).unique().tolist()), "interpretation": "condition-only shortcut assessment is descriptive only; no split/model score exists"},
            "structure_scaffold_coverage": {"status": "not_testable", "reason": "Benchmark v0.1 scaffold/template groups are contractually not_supported because complete verified reaction structures are absent"},
            "pair_degree_imbalance": {"status": "tested", "degree_min": int(degree.min()), "degree_median": float(degree.median()), "degree_max": int(degree.max()), "isolated_main_records": int(len(main_records) - len(degree))},
            "controls_isolation": {"status": "tested", "controls": int(len(controls)), "main_records": int(len(main_records)), "overlap_reaction_ids": int(len(set(controls.reaction_id) & set(main_records.reaction_id))), "pairs_reference_controls": int(len((set(pairs.reaction_id_a) | set(pairs.reaction_id_b)) & set(controls.reaction_id)))},
            "pretraining_contamination": {"status": "not_applicable", "reason": "no pretrained model is used or evaluated in this phase"}
        }
    }
    dispositions = {
        "identity_group_pair_leakage": ("identity leakage invalidates pair evaluation", "builder/verifier reject cross-source, cross-group, self-loop and duplicate edges; split leakage is deferred until split manifests exist"),
        "audit_tool_controls": ("an audit without known controls may be vacuous", "synthetic cross-source mutation must fail while an unmodified strict pair must pass"),
        "measurement_separation": ("mixing source yield types invalidates absolute comparisons", "all future metrics and splits are source/yield-type stratified"),
        "missingness_and_zero_pattern": ("missing analysis and observed zero can bias eligibility", "retain all records and use yield_observed/zero_yield flags; pairs require observed endpoints"),
        "design_position_effects": ("plate effects can shortcut within-source prediction", "record plate/batch availability and audit their association before any split/model claim"),
        "condition_frequency_and_covariation": ("condition-only correlation can overstate reaction generalization", "treat this as shortcut diagnostic; held-out component/combination protocol is required before modeling"),
        "structure_scaffold_coverage": ("unsupported structures cannot justify scaffold leakage claims", "declare scaffold/template tasks not_supported rather than deriving proxies"),
        "pair_degree_imbalance": ("high-degree nodes can dominate pair metrics", "report degree distribution and require group-aware pair reporting in the later protocol"),
        "controls_isolation": ("controls mixed into the main matrix would contaminate outcomes", "controls retain a separate table and pair endpoints are checked against main records"),
        "pretraining_contamination": ("public-data overlap can invalidate a clean-pretraining claim", "no pretrained model is used; any later model must declare contamination risk"),
    }
    for name, item in report["checks"].items():
        item["impact"], item["control"] = dispositions[name]
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
