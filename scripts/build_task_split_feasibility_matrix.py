#!/usr/bin/env python3
"""Materialize the source × task × split feasibility contract (84 leaves)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "data" / "processed" / "core_v0_2"
BENCH = ROOT / "data" / "processed" / "benchmark_v0_1"
SPLIT_OUT = ROOT / "data" / "processed" / "benchmark_v0_1_splits_candidate"
OUT = ROOT / "metadata" / "benchmark_v0_1_task_split_feasibility_matrix.json"
CONTRACT = ROOT / "configs" / "benchmark_v0_1_task_split_metrics_contract.json"
SOURCES = ["ahneman_doyle_buchwald_hartwig_2018", "perera_suzuki_miyaura_2018"]
TASKS = ["Task1_absolute_yield", "Task2_delta_yield", "Task3_direction", "Task4_cliff", "Task5_ranking", "Task6_recommendation", "Task7_OOD_framework"]
SPLITS = ["S0", "S1", "S2", "S3", "S4", "S5"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def leaf(source: str, task: str, split: str, eligible: int, evidence: str, *, record_splits: pd.DataFrame | None = None, pair_splits: pd.DataFrame | None = None, observed: pd.DataFrame | None = None) -> dict[str, object]:
    minimum = 2 if task in {"Task2_delta_yield", "Task3_direction", "Task4_cliff", "Task5_ranking", "Task6_recommendation"} else 1
    status, reason, action = "limited", "selection-dependent eligibility must be evaluated by the frozen split predicate", "materialize_only_if_predicate_and_nonempty_check_pass"
    if task in {"Task5_ranking", "Task6_recommendation"} and split != "S1":
        status, reason, action = "not_supported", "ranking/recommendation v0.1 is restricted to within-group interpolation", "do_not_materialize_score"
    elif split == "S5":
        status, reason, action = "limited", "double-OOD must first demonstrate nonempty disjoint group+tuple partitions", "materialize_only_if_selection_predicate_and_nonempty_check_pass"
    if record_splits is not None and pair_splits is not None and observed is not None and not (task in {"Task5_ranking", "Task6_recommendation"} and split != "S1"):
        selected_records = record_splits.loc[(record_splits.source_dataset == source) & (record_splits.split == split)]
        selected_pairs = pair_splits.loc[(pair_splits.source_dataset == source) & (pair_splits.split == split)]
        if task in {"Task2_delta_yield", "Task3_direction", "Task4_cliff"}:
            sufficient = set(selected_pairs.partition) == {"train", "val", "test"} and (selected_pairs.groupby("partition").size() >= minimum).all()
        elif task in {"Task5_ranking", "Task6_recommendation"}:
            groups = selected_records.merge(observed[["reaction_id", "reaction_group_id"]], on="reaction_id", validate="one_to_one").groupby(["partition", "reaction_group_id"]).size()
            sufficient = {part: int((groups.loc[part] >= 2).sum()) if part in groups.index.get_level_values("partition") else 0 for part in ("train", "val", "test")}
            sufficient = all(value >= 1 for value in sufficient.values())
        else:
            sufficient = set(selected_records.partition) == {"train", "val", "test"} and (selected_records.groupby("partition").size() >= minimum).all()
        status = "supported" if sufficient else "not_supported"
        reason = "accepted split manifest has nonempty task-eligible train/val/test partitions" if sufficient else "accepted split manifest lacks a nonempty task-eligible partition"
        action = "materialized_and_eligible" if sufficient else "do_not_emit_empty_score"
        evidence = "data/processed/benchmark_v0_1_splits_candidate/record_splits.parquet + pair_splits.parquet"
    return {"source_dataset": source, "task": task, "split": split, "status": status, "reason": reason,
            "evidence_path": evidence, "eligible_count_before_split": eligible, "minimum_eligible_records_or_pairs": minimum,
            "nonempty_expectation": "required_if_materialized", "materialization_disposition": action}


def main() -> None:
    records = pd.read_csv(CORE / "reaction_records.csv", keep_default_na=False, na_filter=False, low_memory=False)
    pairs = pd.read_csv(BENCH / "strict_pairs.csv", keep_default_na=False, na_filter=False, low_memory=False)
    observed = records.loc[(records.record_class == "main_matrix") & records.yield_observed.astype(bool)].copy()
    record_counts = observed.groupby("source_dataset").size().to_dict()
    pair_counts = pairs.groupby("source_dataset").size().to_dict()
    rank_counts = observed.groupby(["source_dataset", "reaction_group_id"]).filter(lambda f: len(f) >= 2).groupby("source_dataset").size().to_dict()
    record_splits = pair_splits = None
    if SPLIT_OUT.exists() and (SPLIT_OUT / "manifest.json").exists():
        split_manifest = json.loads((SPLIT_OUT / "manifest.json").read_text())
        if split_manifest.get("config_sha256") == sha(CONTRACT):
            record_splits = pd.read_parquet(SPLIT_OUT / "record_splits.parquet")
            pair_splits = pd.read_parquet(SPLIT_OUT / "pair_splits.parquet")
    def eligibility(source: str, task: str) -> tuple[int, str]:
        if task in {"Task2_delta_yield", "Task3_direction", "Task4_cliff"}:
            return int(pair_counts[source]), "data/processed/benchmark_v0_1/strict_pairs.csv (same-source strict pairs)"
        if task in {"Task5_ranking", "Task6_recommendation"}:
            return int(rank_counts.get(source, 0)), "data/processed/core_v0_2/reaction_records.csv (observed records in groups with >=2 candidates)"
        return int(record_counts[source]), "data/processed/core_v0_2/reaction_records.csv (observed main_matrix records)"
    leaves = [leaf(source, task, split, *eligibility(source, task), record_splits=record_splits, pair_splits=pair_splits, observed=observed) for source in SOURCES for task in TASKS for split in SPLITS]
    assert len(leaves) == 84 and {row["source_dataset"] for row in leaves} == set(SOURCES)
    payload = {"matrix_version": "benchmark_v0_1_task_split_feasibility_v3", "contract": "configs/benchmark_v0_1_task_split_metrics_contract.json", "config_sha256": sha(CONTRACT), "input_hashes": {"core_manifest": sha(CORE / "manifest.json"), "benchmark_manifest": sha(BENCH / "manifest.json")}, "materialization_evidence": "data/processed/benchmark_v0_1_splits_candidate/manifest.json" if record_splits is not None else "not_materialized", "leaves": leaves}
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
