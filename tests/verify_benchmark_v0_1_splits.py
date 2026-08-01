#!/usr/bin/env python3
"""Adversarial contract checks for frozen Benchmark v0.1 split manifests."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "data" / "processed" / "core_v0_2"
BENCH = ROOT / "data" / "processed" / "benchmark_v0_1"
CONTRACT = ROOT / "configs" / "benchmark_v0_1_task_split_metrics_contract.json"
SOURCES = ("ahneman_doyle_buchwald_hartwig_2018", "perera_suzuki_miyaura_2018")
SPLITS = ("S0", "S1", "S2", "S3", "S4", "S5")
PARTITIONS = {"train", "val", "test"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(out: Path, name: str, meta: dict[str, object]) -> pd.DataFrame:
    csv = pd.read_csv(out / f"{name}.csv", keep_default_na=False, na_filter=False, low_memory=False)
    parquet = pq.read_table(out / f"{name}.parquet").to_pandas()
    assert len(csv) == len(parquet) == meta["rows"], name
    assert list(csv.columns) == list(parquet.columns) == meta["columns"], name
    assert sha(out / f"{name}.csv") == meta["csv_sha256"] and sha(out / f"{name}.parquet") == meta["parquet_sha256"], name
    return parquet


def refs(value: object) -> dict[str, str]:
    if isinstance(value, str):
        value = json.loads(value)
    return {str(key): str(component) for key, component in value}


def tuple_for(row: pd.Series, roles: list[str]) -> str:
    return json.dumps([[role, refs(row.condition_component_refs)[role]] for role in roles], sort_keys=True, separators=(",", ":"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=ROOT / "data" / "processed" / "benchmark_v0_1_splits_candidate")
    args = parser.parse_args(); out = args.out_dir.resolve()
    contract = json.loads(CONTRACT.read_text()); manifest = json.loads((out / "manifest.json").read_text())
    assert contract["status"] == "accepted_for_split_materialization_2026-07-31"
    assert manifest["status"] == "candidate_not_promoted"
    assert manifest["config_sha256"] == sha(CONTRACT)
    assert manifest["input_hashes"] == {"core_manifest_sha256": sha(CORE / "manifest.json"), "benchmark_manifest_sha256": sha(BENCH / "manifest.json")}
    assert manifest["unimplemented_by_design"] == ["model_predictions", "metric_results", "benchmark_promotion"]
    records, pair_splits, pair_ledger, record_ledger, summary = (table(out, name, manifest["tables"][name]) for name in ("record_splits", "pair_splits", "pair_exclusion_ledger", "record_exclusion_ledger", "split_summary"))
    core = pd.read_parquet(CORE / "reaction_records.parquet")
    core = core.loc[core.record_class.eq("main_matrix")].copy()
    core["strict_reaction_group_id"] = core.source_dataset.astype(str) + "::" + core.reaction_group_id.astype(str)
    eligible = core.loc[core.yield_observed.astype(bool)].copy().set_index("reaction_id", drop=False)
    pairs = pd.read_parquet(BENCH / "strict_pairs.parquet").set_index("pair_id", drop=False)
    assert not records.duplicated(["source_dataset", "split", "reaction_id"]).any()
    assert not pair_splits.duplicated(["source_dataset", "split", "pair_id"]).any()
    assert not pair_ledger.duplicated(["source_dataset", "split", "pair_id"]).any()
    for source in SOURCES:
        source_eligible = eligible.loc[eligible.source_dataset.eq(source)].copy()
        expected_ids = set(source_eligible.reaction_id)
        source_pairs = set(pairs.loc[pairs.source_dataset.eq(source), "pair_id"])
        for split in SPLITS:
            rs = records.loc[(records.source_dataset.eq(source)) & (records.split.eq(split))]
            excluded_records = record_ledger.loc[(record_ledger.source_dataset.eq(source)) & (record_ledger.split.eq(split))]
            assert set(rs.partition) == PARTITIONS, (source, split)
            assert set(rs.reaction_id).isdisjoint(set(excluded_records.reaction_id))
            assert set(rs.reaction_id) | set(excluded_records.reaction_id) == expected_ids
            if split != "S5":
                assert set(rs.reaction_id) == expected_ids and excluded_records.empty
            ps = pair_splits.loc[(pair_splits.source_dataset.eq(source)) & (pair_splits.split.eq(split))]
            pl = pair_ledger.loc[(pair_ledger.source_dataset.eq(source)) & (pair_ledger.split.eq(split))]
            assert set(ps.pair_id).isdisjoint(set(pl.pair_id))
            assert set(ps.pair_id) | set(pl.pair_id) == source_pairs
            partition_by_id = rs.set_index("reaction_id").partition.to_dict()
            for pair in ps.itertuples(index=False):
                assert pair.endpoint_partition_a == pair.endpoint_partition_b == pair.partition
                assert partition_by_id[pairs.at[pair.pair_id, "reaction_id_a"]] == pair.partition
                assert partition_by_id[pairs.at[pair.pair_id, "reaction_id_b"]] == pair.partition
            assert (pl.exclusion_reason.isin(["cross_partition_endpoint", "endpoint_unassigned_by_split"])).all()
        # S2 is exactly group-disjoint across all record partitions.
        s2 = records.loc[(records.source_dataset.eq(source)) & (records.split.eq("S2"))].merge(source_eligible[["reaction_id", "strict_reaction_group_id"]].reset_index(drop=True), on="reaction_id", validate="one_to_one")
        group_sets = {part: set(s2.loc[s2.partition.eq(part), "strict_reaction_group_id"]) for part in PARTITIONS}
        assert not (group_sets["train"] & group_sets["val"] or group_sets["train"] & group_sets["test"] or group_sets["val"] & group_sets["test"])
        # S3 component OOD: selected held-out entity never appears in train.
        s3 = records.loc[(records.source_dataset.eq(source)) & (records.split.eq("S3"))]
        role = summary.loc[(summary.source_dataset.eq(source)) & (summary.split.eq("S3")), "selection_roles"].item()
        role = json.loads(role)[0]
        component_lookup = source_eligible.condition_component_refs.map(refs).map(lambda value: value[role])
        component_by_id = s3.reaction_id.map(component_lookup)
        train_components = set(component_by_id.loc[s3.partition.eq("train")])
        assert not (train_components & set(component_by_id.loc[s3.partition.eq("val")]))
        assert not (train_components & set(component_by_id.loc[s3.partition.eq("test")]))
        # S4: full tuple OOD, with every held-out component marginal seen in train.
        s4 = records.loc[(records.source_dataset.eq(source)) & (records.split.eq("S4"))]
        roles = json.loads(summary.loc[(summary.source_dataset.eq(source)) & (summary.split.eq("S4")), "selection_roles"].item())
        tuple_lookup = source_eligible.apply(lambda row: tuple_for(row, roles), axis=1)
        s4_tuples = s4.reaction_id.map(tuple_lookup)
        train_tuples = set(s4_tuples.loc[s4.partition.eq("train")])
        assert not (train_tuples & set(s4_tuples.loc[s4.partition.eq("val")]))
        assert not (train_tuples & set(s4_tuples.loc[s4.partition.eq("test")]))
        marginals = {role: set() for role in roles}
        for key in train_tuples:
            for role_name, value in json.loads(key): marginals[role_name].add(value)
        for key in set(s4_tuples.loc[~s4.partition.eq("train")]):
            assert all(value in marginals[role_name] for role_name, value in json.loads(key))
        # S5 retains only diagonal group×tuple cells, so group and tuple are both disjoint.
        s5 = records.loc[(records.source_dataset.eq(source)) & (records.split.eq("S5"))]
        roles = json.loads(summary.loc[(summary.source_dataset.eq(source)) & (summary.split.eq("S5")), "selection_roles"].item())
        s5_groups = s5.reaction_id.map(source_eligible.strict_reaction_group_id)
        s5_tuple_lookup = source_eligible.apply(lambda row: tuple_for(row, roles), axis=1)
        s5_tuples = s5.reaction_id.map(s5_tuple_lookup)
        for values in (s5_groups, s5_tuples):
            parts = {part: set(values.loc[s5.partition.eq(part)]) for part in PARTITIONS}
            assert not (parts["train"] & parts["val"] or parts["train"] & parts["test"] or parts["val"] & parts["test"])
    assert len(summary) == 12 and (summary[["record_train", "record_val", "record_test"]] > 0).all().all()
    print("Benchmark v0.1 split candidate verification passed: deterministic manifests, OOD separation, and pair exclusion ledger.")


if __name__ == "__main__":
    main()
