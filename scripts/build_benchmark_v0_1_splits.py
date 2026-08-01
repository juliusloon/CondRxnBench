#!/usr/bin/env python3
"""Materialize frozen Benchmark v0.1 record and strict-pair split manifests.

The split assignment never reads yield values or pair labels.  Eligibility is
limited to observed main-matrix records as frozen by ADR 0006; pair membership
is derived only after record partitions are fixed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "data" / "processed" / "core_v0_2"
BENCH = ROOT / "data" / "processed" / "benchmark_v0_1"
CONTRACT = ROOT / "configs" / "benchmark_v0_1_task_split_metrics_contract.json"
VERSION = "CondRxnBench-Benchmark-v0.1-splits-candidate.1"
SOURCES = ("ahneman_doyle_buchwald_hartwig_2018", "perera_suzuki_miyaura_2018")
PARTITIONS = ("train", "val", "test")
SPLITS = ("S0", "S1", "S2", "S3", "S4", "S5")


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def rank_keys(seed: int, source: str, keys: list[str]) -> list[str]:
    return sorted(keys, key=lambda key: (hashlib.sha256(f"{seed}|{source}|{key}".encode()).hexdigest(), key))


def unit_partitions(seed: int, source: str, keys: list[str], *, mode: str) -> dict[str, str]:
    """Assign units with the ADR's deterministic hash ordering."""
    ordered = rank_keys(seed, source, sorted(set(keys)))
    n = len(ordered)
    if n < 3:
        raise ValueError(f"{source} {mode} has fewer than three units")
    if mode == "S1":
        train_n, val_n = math.ceil(0.70 * n), math.ceil(0.15 * n)
    else:
        train_n, val_n = math.floor(0.70 * n), math.floor(0.15 * n)
    test_n = n - train_n - val_n
    if min(train_n, val_n, test_n) < 1:
        raise ValueError(f"{source} {mode} creates an empty partition for {n} units")
    return {key: "train" if i < train_n else "val" if i < train_n + val_n else "test" for i, key in enumerate(ordered)}


def refs(value: object) -> dict[str, str]:
    if isinstance(value, str):
        value = json.loads(value)
    return {str(key): str(component) for key, component in value}


def tuple_key(row: pd.Series, roles: list[str]) -> str:
    mapping = refs(row.condition_component_refs)
    return canonical([[role, mapping[role]] for role in roles])


@dataclass
class Selection:
    assignments: dict[str, str]
    key_by_reaction: dict[str, str]
    reason: str
    excluded: dict[str, str]
    roles: list[str]


def select_s0(frame: pd.DataFrame, seed: int, source: str) -> Selection:
    keys = frame.reaction_id.astype(str).tolist()
    alloc = unit_partitions(seed, source, keys, mode="S0")
    return Selection(alloc, {key: key for key in keys}, "S0_hash_rank_reaction_id", {}, [])


def select_s1(frame: pd.DataFrame, seed: int, source: str) -> Selection:
    assignments, key_by_reaction = {}, {}
    for group, group_frame in frame.groupby("strict_reaction_group_id", sort=True):
        keys = group_frame.reaction_id.astype(str).tolist()
        alloc = unit_partitions(seed, source, keys, mode="S1")
        for reaction_id, partition in alloc.items():
            assignments[reaction_id] = partition
            key_by_reaction[reaction_id] = f"{group}::{reaction_id}"
    return Selection(assignments, key_by_reaction, "S1_hash_rank_reaction_id_within_strict_group", {}, [])


def select_s2(frame: pd.DataFrame, seed: int, source: str) -> Selection:
    groups = frame.strict_reaction_group_id.astype(str).unique().tolist()
    alloc = unit_partitions(seed, source, groups, mode="S2")
    assignments = {str(row.reaction_id): alloc[str(row.strict_reaction_group_id)] for row in frame.itertuples(index=False)}
    keys = {str(row.reaction_id): str(row.strict_reaction_group_id) for row in frame.itertuples(index=False)}
    return Selection(assignments, keys, "S2_hash_rank_strict_reaction_group_id", {}, [])


def source_roles(contract: dict[str, object], source: str, split: str) -> list[str]:
    policy = contract["split_policy"][split]
    key = "roles" if split == "S3" else "tuple_roles"
    return list(policy[key][source])


def select_s3(frame: pd.DataFrame, seed: int, source: str, contract: dict[str, object]) -> Selection:
    declared = source_roles(contract, source, "S3")
    mappings = frame.condition_component_refs.map(refs)
    candidate_roles = []
    for role in declared:
        counts = mappings.map(lambda value: value[role]).value_counts()
        if (counts >= 2).sum() >= 3:
            candidate_roles.append(role)
    if not candidate_roles:
        raise ValueError(f"{source} S3 has no declared role with three frequency>=2 entities")
    role = sorted(candidate_roles)[0]
    entity_by_reaction = {str(row.reaction_id): mappings.loc[row.Index][role] for row in frame.itertuples()}
    alloc = unit_partitions(seed, source, list(entity_by_reaction.values()), mode="S3")
    assignments = {reaction_id: alloc[entity] for reaction_id, entity in entity_by_reaction.items()}
    return Selection(assignments, entity_by_reaction, f"S3_hash_rank_component_ref_role={role}", {}, [role])


def select_s4(frame: pd.DataFrame, seed: int, source: str, contract: dict[str, object]) -> Selection:
    roles = source_roles(contract, source, "S4")
    tuple_by_reaction = {str(row.reaction_id): tuple_key(frame.loc[row.Index], roles) for row in frame.itertuples()}
    alloc = unit_partitions(seed, source, list(tuple_by_reaction.values()), mode="S4")
    # All tuple marginals in a held-out partition must remain present in train.
    train_tuples = {key for key, partition in alloc.items() if partition == "train"}
    train_marginals = {role: set() for role in roles}
    for key in train_tuples:
        for role, value in json.loads(key):
            train_marginals[role].add(value)
    for key, partition in alloc.items():
        if partition == "train":
            continue
        if any(value not in train_marginals[role] for role, value in json.loads(key)):
            raise ValueError(f"{source} S4 held-out tuple lacks a train marginal: {key}")
    assignments = {reaction_id: alloc[key] for reaction_id, key in tuple_by_reaction.items()}
    return Selection(assignments, tuple_by_reaction, "S4_hash_rank_canonical_condition_tuple", {}, roles)


def select_s5(frame: pd.DataFrame, seed: int, source: str, contract: dict[str, object]) -> Selection:
    roles = source_roles(contract, source, "S5")
    group_by_reaction = {str(row.reaction_id): str(row.strict_reaction_group_id) for row in frame.itertuples(index=False)}
    tuple_by_reaction = {str(row.reaction_id): tuple_key(frame.loc[row.Index], roles) for row in frame.itertuples()}
    group_alloc = unit_partitions(seed, source, list(group_by_reaction.values()), mode="S5")
    tuple_alloc = unit_partitions(seed, source, list(tuple_by_reaction.values()), mode="S5")
    assignments, excluded = {}, {}
    for reaction_id, group in group_by_reaction.items():
        tuple_value = tuple_by_reaction[reaction_id]
        group_partition, tuple_partition = group_alloc[group], tuple_alloc[tuple_value]
        if group_partition == tuple_partition:
            assignments[reaction_id] = group_partition
        else:
            excluded[reaction_id] = "S5_cross_partition_group_tuple_cell"
    if set(assignments.values()) != set(PARTITIONS):
        raise ValueError(f"{source} S5 did not retain all nonempty partitions")
    keys = {reaction_id: canonical({"strict_reaction_group_id": group_by_reaction[reaction_id], "condition_tuple": tuple_by_reaction[reaction_id]}) for reaction_id in assignments}
    return Selection(assignments, keys, "S5_hash_rank_group_and_canonical_condition_tuple", excluded, roles)


def selection(split: str, frame: pd.DataFrame, seed: int, source: str, contract: dict[str, object]) -> Selection:
    return {"S0": select_s0, "S1": select_s1, "S2": select_s2}.get(split, lambda *_: None)(frame, seed, source) if split in {"S0", "S1", "S2"} else {"S3": select_s3, "S4": select_s4, "S5": select_s5}[split](frame, seed, source, contract)


def write_frame(frame: pd.DataFrame, name: str, out: Path) -> dict[str, object]:
    csv_path, parquet_path = out / f"{name}.csv", out / f"{name}.parquet"
    frame.to_csv(csv_path, index=False, lineterminator="\n")
    pq.write_table(pa.Table.from_pandas(frame, preserve_index=False), parquet_path, compression="zstd")
    return {"rows": len(frame), "columns": frame.columns.tolist(), "csv_sha256": sha_file(csv_path), "parquet_sha256": sha_file(parquet_path)}


def build(out: Path) -> dict[str, object]:
    contract_bytes = CONTRACT.read_bytes(); contract = json.loads(contract_bytes)
    if contract["status"] != "accepted_for_split_materialization_2026-07-31":
        raise ValueError("split contract is not accepted")
    seed = int(contract["seed"]); config_sha = hashlib.sha256(contract_bytes).hexdigest()
    core_manifest_sha, benchmark_manifest_sha = sha_file(CORE / "manifest.json"), sha_file(BENCH / "manifest.json")
    records = pd.read_parquet(CORE / "reaction_records.parquet")
    records = records.loc[records.record_class.eq("main_matrix")].copy()
    records["strict_reaction_group_id"] = records.source_dataset.astype(str) + "::" + records.reaction_group_id.astype(str)
    eligible = records.loc[records.yield_observed.astype(bool)].copy()
    pairs = pd.read_parquet(BENCH / "strict_pairs.parquet")
    record_rows, pair_rows, pair_exclusions, record_exclusions, summaries = [], [], [], [], []
    for source in SOURCES:
        frame = eligible.loc[eligible.source_dataset.eq(source)].copy().sort_values("reaction_id")
        all_pairs = pairs.loc[pairs.source_dataset.eq(source)].copy()
        for split in SPLITS:
            result = selection(split, frame, seed, source, contract)
            assigned = result.assignments
            for row in frame.itertuples(index=False):
                reaction_id = str(row.reaction_id)
                if reaction_id in assigned:
                    record_rows.append({"split_version": VERSION, "config_sha256": config_sha, "input_manifest_sha256": core_manifest_sha, "seed": seed, "source_dataset": source, "split": split, "reaction_id": reaction_id, "partition": assigned[reaction_id], "selection_key": result.key_by_reaction[reaction_id], "selection_reason": result.reason})
                else:
                    record_exclusions.append({"split_version": VERSION, "source_dataset": source, "split": split, "reaction_id": reaction_id, "exclusion_reason": result.excluded[reaction_id]})
            partition_by_id = assigned
            included, excluded = 0, 0
            for pair in all_pairs.itertuples(index=False):
                a, b = str(pair.reaction_id_a), str(pair.reaction_id_b)
                part_a, part_b = partition_by_id.get(a), partition_by_id.get(b)
                if part_a is not None and part_a == part_b:
                    pair_rows.append({"split_version": VERSION, "config_sha256": config_sha, "input_manifest_sha256": benchmark_manifest_sha, "source_dataset": source, "split": split, "pair_id": pair.pair_id, "partition": part_a, "endpoint_partition_a": part_a, "endpoint_partition_b": part_b})
                    included += 1
                else:
                    reason = "cross_partition_endpoint" if part_a is not None and part_b is not None else "endpoint_unassigned_by_split"
                    pair_exclusions.append({"split_version": VERSION, "source_dataset": source, "split": split, "pair_id": pair.pair_id, "partition_a": part_a or "unassigned", "partition_b": part_b or "unassigned", "exclusion_reason": reason})
                    excluded += 1
            counts = pd.Series(list(assigned.values())).value_counts().to_dict()
            if set(counts) != set(PARTITIONS):
                raise ValueError(f"{source} {split} has an empty record partition")
            summaries.append({"split_version": VERSION, "source_dataset": source, "split": split, "record_train": counts["train"], "record_val": counts["val"], "record_test": counts["test"], "record_excluded": len(result.excluded), "same_partition_pairs": included, "excluded_pairs": excluded, "selection_roles": canonical(result.roles), "selection_reason": result.reason})
    record_frame = pd.DataFrame(record_rows).sort_values(["source_dataset", "split", "partition", "reaction_id"]).reset_index(drop=True)
    pair_frame = pd.DataFrame(pair_rows).sort_values(["source_dataset", "split", "partition", "pair_id"]).reset_index(drop=True)
    pair_exclusion_frame = pd.DataFrame(pair_exclusions).sort_values(["source_dataset", "split", "pair_id"]).reset_index(drop=True)
    record_exclusion_frame = pd.DataFrame(record_exclusions).sort_values(["source_dataset", "split", "reaction_id"]).reset_index(drop=True)
    summary_frame = pd.DataFrame(summaries).sort_values(["source_dataset", "split"]).reset_index(drop=True)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    tables = {name: write_frame(frame, name, out) for name, frame in {"record_splits": record_frame, "pair_splits": pair_frame, "pair_exclusion_ledger": pair_exclusion_frame, "record_exclusion_ledger": record_exclusion_frame, "split_summary": summary_frame}.items()}
    manifest = {"release": VERSION, "status": "candidate_not_promoted", "contract_version": contract["contract_version"], "config_sha256": config_sha, "seed": seed, "input_hashes": {"core_manifest_sha256": core_manifest_sha, "benchmark_manifest_sha256": benchmark_manifest_sha}, "tables": tables, "freeze": "canonical sorted IDs + output sha256; change requires new benchmark version", "test_first": "heldout selection uses only source, identifiers, component refs, group IDs, tuple keys, fixed seed, and config; it never reads yield values or pair labels", "unimplemented_by_design": ["model_predictions", "metric_results", "benchmark_promotion"]}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=ROOT / "data" / "processed" / "benchmark_v0_1_splits_candidate")
    args = parser.parse_args()
    manifest = build(args.out_dir.resolve())
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
