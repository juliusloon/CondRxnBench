#!/usr/bin/env python3
"""Independent candidate checks for the frozen Core v0.2 machine contract."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


ROOT = Path.cwd()
OUT_DEFAULT = ROOT / "data" / "processed" / "core_v0_2"
AHNEMAN = "ahneman_doyle_buchwald_hartwig_2018"
PERERA = "perera_suzuki_miyaura_2018"
NA = "NA"
NOT_REPORTED = "not_reported"
NULL_COMPONENT = "NULL_COMPONENT"
PRIMARY_KEYS = {
    "reaction_records": "reaction_id", "control_records": "reaction_id",
    "record_structure_assertions": "structure_assertion_id", "condition_registry": "component_id",
    "condition_mappings": "mapping_id", "condition_attributes": "attribute_id",
    "condition_compositions": "composition_id", "continuous_observations": "continuous_observation_id",
}
MAP_COLUMNS = {"reaction_records": ("condition_component_refs", "condition_raw_values"), "control_records": ("condition_component_refs", "condition_raw_values")}
LIST_COLUMNS = {"reaction_records": ("eligibility_reason_codes",), "control_records": ("eligibility_reason_codes",)}
DISCRETE = {AHNEMAN: ("catalyst_system", "ligand", "base", "additive"), PERERA: ("catalyst", "ligand", "base", "solvent_1", "solvent_2", "atmosphere")}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def schema_fingerprint(schema: pa.Schema) -> str:
    return hashlib.sha256(schema.serialize().to_pybytes()).hexdigest()


def map_value(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return {str(k): str(v) for k, v in value.items()}
    return {str(k): str(v) for k, v in value}


def csv_value(value: Any) -> str:
    if value is None:
        return NA
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (dict, list, tuple)):
        if isinstance(value, list) and value and isinstance(value[0], tuple):
            value = map_value(value)
        return canonical_json(value)
    return str(value)


def assert_csv_parquet_equivalent(out: Path, name: str, manifest_table: dict[str, Any]) -> pa.Table:
    arrow = pq.read_table(out / f"{name}.parquet")
    assert schema_fingerprint(arrow.schema) == manifest_table["arrow_schema_fingerprint"], name
    assert arrow.schema.names == manifest_table["columns"], name
    csv = pd.read_csv(out / f"{name}.csv", dtype=str, keep_default_na=False, na_filter=False)
    assert csv.columns.tolist() == arrow.schema.names, name
    assert len(csv) == arrow.num_rows == manifest_table["rows"], name
    got = csv.astype(str).values.tolist()
    # Arrow table rows are dictionaries; normalize in schema order rather
    # than iterating their keys (which would compare CSV values to headers).
    expected = [[csv_value(row[column]) for column in arrow.schema.names] for row in arrow.to_pylist()]
    assert got == expected, f"CSV/Parquet semantic mismatch: {name}"
    key = manifest_table["primary_key"]
    key_values = arrow.column(key).to_pylist()
    assert len(key_values) == len(set(key_values)), (name, key)
    return arrow


def reject_bad_reference(registry: dict[str, dict[str, Any]], source: str, role: str, component: str | None) -> bool:
    return component is not None and component in registry and registry[component]["source_dataset"] == source and registry[component]["role"] == role


def reject_bad_continuous(state: str, raw: Any, normalized: Any) -> bool:
    return state in {"observed_numeric", "NA", "not_reported"} and ((state == "observed_numeric") == (raw is not None and normalized is not None))


def reject_bad_outcome(observed: bool, zero: bool, value: Any, status: str) -> bool:
    return status == "observed_numeric" and observed and value == 0.0 and zero


def run_negative_contract_cases(registry: dict[str, dict[str, Any]], ahn_component: str, perera_component: str) -> None:
    # These adversarial variants must all fail their relevant contract predicate.
    assert not reject_bad_reference(registry, AHNEMAN, "ligand", None)                 # NA is not a component
    assert not reject_bad_reference(registry, AHNEMAN, "ligand", perera_component)     # cross-source rejected
    assert not reject_bad_reference(registry, AHNEMAN, "base", ahn_component)          # cross-role rejected
    assert not reject_bad_continuous("outside_domain", None, None)
    assert not reject_bad_continuous("observed_numeric", None, None)                   # raw numeric null never zero
    assert not reject_bad_outcome(False, False, None, "observed_numeric")               # NA is not observed zero
    assert not reject_bad_outcome(True, False, 0.0, "not_detected")                     # zero is not direct-evidence not-detected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DEFAULT)
    args = parser.parse_args()
    out = args.out_dir.resolve()
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["release"] == "CondRxnBench-Core-v0.2-proposed.3"
    assert manifest["status"] == "candidate_not_promoted"
    assert manifest["pair_baseline"]["count"] == 116156 and not manifest["pair_baseline"]["included_as_output"]
    assert not (out / "condition_pairs.csv").exists() and not (out / "condition_pairs.parquet").exists()

    tables = {name: assert_csv_parquet_equivalent(out, name, meta) for name, meta in manifest["tables"].items()}
    records = tables["reaction_records"].to_pandas()
    registry_rows = tables["condition_registry"].to_pylist()
    registry = {row["component_id"]: row for row in registry_rows}
    assertions = tables["record_structure_assertions"].to_pandas()
    continuous = tables["continuous_observations"].to_pandas()
    compositions = tables["condition_compositions"].to_pandas()
    mappings = tables["condition_mappings"].to_pandas()

    assert len(records) == 9900 and records.reaction_id.is_unique
    assert records.groupby("source_dataset").size().to_dict() == {AHNEMAN: 4140, PERERA: 5760}
    assert records.groupby("source_dataset").yield_observed.sum().to_dict() == {AHNEMAN: 4132, PERERA: 5760}
    assert records.groupby("source_dataset").zero_yield.sum().to_dict() == {AHNEMAN: 273, PERERA: 275}
    assert (records.zero_yield == (records.yield_observed & records.yield_percent.eq(0))).all()
    assert records.outcome_observation_status.eq("observed_numeric").eq(records.yield_observed).all()
    assert records.eligibility_status.eq("not_assessed").all()
    assert set(records.provenance_status) == {"direct_source_record", "missing_analysis_export"}

    assert len(registry) == len(registry_rows)
    assert all(row["raw_value"] != NOT_REPORTED and row["normalized_name"] != NOT_REPORTED for row in registry_rows)
    assert all(row["component_value_state"] in {"explicit_component", "explicit_null_component"} for row in registry_rows)
    assert any(row["component_value_state"] == "explicit_null_component" and row["normalized_name"] == NULL_COMPONENT for row in registry_rows)
    assert all(row["structure_status"] == "not_supported" for row in registry_rows if row["source_dataset"] == PERERA)
    assert all(row["structure_status"] == "not_supported" for row in registry_rows if row["source_dataset"] == AHNEMAN and row["role"] == "catalyst_system")

    record_maps = tables["reaction_records"].to_pylist()
    for row in record_maps:
        refs, raw = map_value(row["condition_component_refs"]), map_value(row["condition_raw_values"])
        assert set(refs) == set(raw)
        for role, cid in refs.items():
            assert reject_bad_reference(registry, row["source_dataset"], role, cid)
            assert registry[cid]["normalized_name"] != NOT_REPORTED
        assert "not_reported" not in refs.values()
    for source, roles in DISCRETE.items():
        source_rows = [row for row in record_maps if row["source_dataset"] == source]
        for role in roles:
            states = [registry[map_value(row["condition_component_refs"])[role]]["component_value_state"] for row in source_rows]
            assert len(states) == len(source_rows) and set(states) <= {"explicit_component", "explicit_null_component"}

    source_reported = assertions.loc[assertions.structure_evidence_status.eq("source_reported")]
    assert len(source_reported) == 4 * 4140
    assert set(source_reported.structure_role) == {"substrate_1", "ligand", "base", "additive"}
    assert source_reported.parse_sanitize_status.eq("success").all()
    assert source_reported[["normalized_smiles", "canonical_smiles", "inchikey"]].notna().all().all()
    perera_assertions = assertions.loc[assertions.source_dataset.eq(PERERA)]
    assert perera_assertions.parse_sanitize_status.eq("not_supported").all()
    assert perera_assertions[["normalized_smiles", "canonical_smiles", "inchikey"]].isna().all().all()
    assert assertions.loc[assertions.parse_sanitize_status.eq("not_supported"), "ecfp4_status"].eq("not_supported").all()
    assert assertions.loc[assertions.parse_sanitize_status.eq("not_supported"), "reaction_center_fp_status"].eq("not_supported").all()

    assert len(continuous) == 9900 * 11 and continuous.continuous_observation_id.is_unique
    assert set(continuous.value_state) <= {"observed_numeric", "NA", "not_reported"}
    observed = continuous.value_state.eq("observed_numeric")
    assert continuous.loc[observed, ["raw_value", "normalized_value"]].notna().all().all()
    assert continuous.loc[~observed, ["raw_value", "normalized_value"]].isna().all().all()
    assert (continuous.value_state.eq("NA") & continuous.raw_value.isna()).any()

    assert len(compositions) == 11520 and compositions.composition_id.is_unique
    assert compositions.ratio_raw_value.eq("9:1").all()
    assert compositions.groupby("reaction_id").size().eq(2).all()
    assert set(compositions.component_label) == {"organic_carrier", "H2O"}
    assert all(reject_bad_reference(registry, PERERA, registry[cid]["role"], cid) for cid in compositions.component_component_id)

    assert len(mappings) == 2 and mappings.non_identity.all()
    assert mappings.review_status.eq("pending").all()
    assert mappings.reviewer_id.isna().all()
    assert mappings.target_scope.eq("core_v0_1_compatibility_only").all()
    assert mappings[["evidence_id", "source_locator", "rule_id", "rule_version"]].notna().all().all()
    assert records.condition_mapping_version.eq("core_v0_2_source_raw_identity_v1").all()

    ahn_ligand = next(k for k, v in registry.items() if v["source_dataset"] == AHNEMAN and v["role"] == "ligand")
    perera_ligand = next(k for k, v in registry.items() if v["source_dataset"] == PERERA and v["role"] == "ligand")
    run_negative_contract_cases(registry, ahn_ligand, perera_ligand)
    print("Core v0.2 candidate verification passed: records/controls/side tables; no pairs or benchmark artifacts.")


if __name__ == "__main__":
    main()
