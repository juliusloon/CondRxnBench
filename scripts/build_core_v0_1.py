#!/usr/bin/env python3
"""Build the auditable two-source CondRxnBench-Core v0.1 release.

This release standardizes *access*, provenance and field semantics.  It does
not collapse the two measurement types into one label, assign benchmark
splits, or label condition cliffs.  Those are later, separately versioned
benchmark decisions.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
VERSION = "CondRxnBench-Core-v0.1"
OUT = ROOT / "data" / "processed" / "core_v0_1"
NOT_REPORTED = "not_reported"
NOT_ASSIGNED = "not_assigned"

RECORD_COLUMNS = [
    "schema_version", "source_dataset", "source_record_id", "reaction_id",
    "reaction_group_id", "record_class", "is_control", "provenance_path",
    "source_file", "plate_id", "batch_id", "well_id", "reaction_class",
    "substrate_1_name", "substrate_1_smiles", "substrate_2_name",
    "substrate_2_smiles", "product_name", "product_smiles", "atom_mapped_rxn",
    "canonical_rxn", "bond_changes", "catalyst_system", "catalyst", "ligand",
    "base", "additive", "solvent_1", "solvent_2", "atmosphere", "vessel",
    "temperature_c", "time_h", "residence_time_min", "concentration_m",
    "pressure_bar", "scale_mmol", "catalyst_equiv", "ligand_equiv",
    "base_equiv", "substrate_1_equiv", "substrate_2_equiv", "yield_percent",
    "yield_observed", "zero_yield", "yield_type", "measurement_method",
    "measurement_value_raw", "success_label", "quality_grade", "qc_flags",
    "manual_review_status",
]

PAIR_COLUMNS = [
    "schema_version", "source_dataset", "pair_id", "reaction_group_id",
    "reaction_id_a", "reaction_id_b", "changed_factor", "n_changed_factors",
    "condition_a", "condition_b", "yield_a", "yield_b", "delta_yield",
    "abs_delta_yield", "pair_definition", "condition_distance", "cliff_label",
    "confidence_grade",
]


def stable_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def scalar(value: Any) -> Any:
    """Use explicit text for unreported categorical fields, preserving numbers."""
    return NOT_REPORTED if pd.isna(value) else value


def ahneman_records() -> pd.DataFrame:
    source = pd.read_csv(ROOT / "data/processed/ahneman_buchwald_hartwig_main_matrix.csv")
    if len(source) != 4140 or source["reaction_id"].nunique() != 4140:
        raise ValueError("Unexpected Ahneman main-matrix shape or identifiers")

    source_filename = source["source_file"].map(
        lambda value: Path(value).name if pd.notna(value) else NOT_REPORTED)
    source_well = source["source_well"].fillna(NOT_REPORTED).astype(str)
    source_record_id = source_filename + ":" + source_well
    source_record_id = source_record_id.where(
        source_filename.ne(NOT_REPORTED),
        source["reaction_id"] + ":missing_analysis_export",
    )
    provenance_path = source_filename.map(
        lambda name: f"data/raw/ahneman_doyle_rxnpredict/yield_data/{name}"
        if name != NOT_REPORTED else NOT_REPORTED)

    records = pd.DataFrame({
        "schema_version": VERSION,
        "source_dataset": "ahneman_doyle_buchwald_hartwig_2018",
        # A well is the source-level record; reaction_id remains the derived stable ID.
        "source_record_id": source_record_id,
        "reaction_id": source["reaction_id"],
        "reaction_group_id": source["reaction_group_id"],
        "record_class": source["record_class"],
        "is_control": source["is_control"],
        "provenance_path": provenance_path,
        "source_file": source_filename,
        "plate_id": "plate_" + source["plate"].astype(int).astype(str),
        "batch_id": "not_reported",
        "well_id": source_well,
        "reaction_class": "Buchwald_Hartwig_C_N_cross_coupling",
        "substrate_1_name": source["aryl_halide"],
        "substrate_1_smiles": source["aryl_halide_smiles"],
        "substrate_2_name": NOT_REPORTED,
        "substrate_2_smiles": NOT_REPORTED,
        "product_name": NOT_REPORTED,
        "product_smiles": NOT_REPORTED,
        "atom_mapped_rxn": NOT_REPORTED,
        "canonical_rxn": NOT_REPORTED,
        "bond_changes": NOT_REPORTED,
        # The raw design supplies a pre-formed Pd--ligand system.  It is not
        # decomposed into a separate catalyst field without source evidence.
        "catalyst_system": source["catalyst_system"],
        "catalyst": NOT_REPORTED,
        "ligand": source["ligand"],
        "base": source["base"],
        "additive": source["additive"],
        "solvent_1": NOT_REPORTED,
        "solvent_2": NOT_REPORTED,
        "atmosphere": NOT_REPORTED,
        "vessel": NOT_REPORTED,
        "temperature_c": NOT_REPORTED,
        "time_h": NOT_REPORTED,
        "residence_time_min": NOT_REPORTED,
        "concentration_m": NOT_REPORTED,
        "pressure_bar": NOT_REPORTED,
        "scale_mmol": NOT_REPORTED,
        "catalyst_equiv": NOT_REPORTED,
        "ligand_equiv": NOT_REPORTED,
        "base_equiv": NOT_REPORTED,
        "substrate_1_equiv": NOT_REPORTED,
        "substrate_2_equiv": NOT_REPORTED,
        "yield_percent": source["yield_percent"],
        "yield_observed": source["yield_observed"],
        "zero_yield": source["zero_yield"],
        "yield_type": "lc_uv_product_scaled_percent",
        "measurement_method": "per_well_LC_UV_internal_standard_corrected",
        "measurement_value_raw": source["product"],
        "success_label": NOT_ASSIGNED,
        "quality_grade": "B",
        "qc_flags": source.apply(
            lambda row: json.dumps([
                "main_matrix",
                "yield_missing" if not row["yield_observed"] else "yield_observed",
                "observed_zero_yield" if row["zero_yield"] else "not_observed_zero",
            ]), axis=1),
        "manual_review_status": "source_reconstruction_qc_complete",
    })
    return records[RECORD_COLUMNS]


def perera_records() -> pd.DataFrame:
    source = pd.read_csv(ROOT / "data/processed/perera_suzuki_miyaura_main_matrix.csv")
    if len(source) != 5760 or source["reaction_id"].nunique() != 5760:
        raise ValueError("Unexpected Perera main-matrix shape or identifiers")

    records = pd.DataFrame({
        "schema_version": VERSION,
        "source_dataset": source["source_dataset"],
        "source_record_id": source["source_record_id"].astype(str),
        "reaction_id": source["reaction_id"],
        "reaction_group_id": source["reaction_group_id"],
        "record_class": source["record_class"],
        "is_control": source["is_control"],
        "provenance_path": "data/raw/perera_suzuki_miyaura/aap9112_Data_File_S1.xlsx:Sheet1",
        "source_file": "aap9112_Data_File_S1.xlsx",
        "plate_id": NOT_REPORTED,
        "batch_id": NOT_REPORTED,
        "well_id": NOT_REPORTED,
        "reaction_class": "Suzuki_Miyaura_C_C_cross_coupling",
        "substrate_1_name": source["Reactant_1_Name"],
        "substrate_1_smiles": source["substrate_smiles"],
        "substrate_2_name": source["Reactant_2_Name"],
        "substrate_2_smiles": NOT_REPORTED,
        "product_name": NOT_REPORTED,
        "product_smiles": source["product_smiles"],
        "atom_mapped_rxn": NOT_REPORTED,
        "canonical_rxn": NOT_REPORTED,
        "bond_changes": NOT_REPORTED,
        "catalyst_system": NOT_REPORTED,
        "catalyst": source["catalyst"],
        "ligand": source["ligand"],
        "base": source["base"],
        "additive": NOT_REPORTED,
        "solvent_1": source["solvent_1"],
        "solvent_2": source["aqueous_cosolvent"],
        "atmosphere": "glovebox; O2 <20 ppm; H2O <20 ppm",
        "vessel": NOT_REPORTED,
        "temperature_c": source["temperature_c"],
        "time_h": NOT_REPORTED,
        "residence_time_min": source["residence_time_min"],
        "concentration_m": NOT_REPORTED,
        "pressure_bar": source["pressure_bar"],
        "scale_mmol": source["reactant_1_mmol"],
        "catalyst_equiv": source["catalyst_equiv"],
        "ligand_equiv": source["ligand_equiv_reported"],
        "base_equiv": source["base_equiv_reported"],
        "substrate_1_equiv": source["reactant_1_equiv"],
        "substrate_2_equiv": source["reactant_2_equiv"],
        "yield_percent": source["yield_percent"],
        "yield_observed": source["yield_observed"],
        "zero_yield": source["zero_yield"],
        "yield_type": source["yield_type"],
        "measurement_method": source["measurement_method"],
        "measurement_value_raw": source["Product_Yield_PCT_Area_UV"],
        "success_label": NOT_ASSIGNED,
        "quality_grade": "B",
        "qc_flags": source.apply(
            lambda row: json.dumps([
                "main_matrix", "yield_observed",
                "observed_zero_yield" if row["zero_yield"] else "not_observed_zero",
                "blank_ligand" if row["ligand_is_blank"] else "nonblank_ligand",
                "blank_base" if row["base_is_blank"] else "nonblank_base",
            ]), axis=1),
        "manual_review_status": "source_reconstruction_qc_complete",
    })
    return records[RECORD_COLUMNS]


def standardize_pairs(path: Path, source_dataset: str) -> pd.DataFrame:
    source = pd.read_csv(path)
    if not source["pair_id"].is_unique or not (source["n_changed_factors"] == 1).all():
        raise ValueError(f"Invalid strict-pair input: {path}")
    pairs = source.copy()
    pairs.insert(0, "schema_version", VERSION)
    pairs.insert(1, "source_dataset", source_dataset)
    pairs["pair_definition"] = "same_strict_reaction_group__one_discrete_factor_changed__both_yields_observed"
    pairs["condition_distance"] = 1.0
    pairs["cliff_label"] = NOT_ASSIGNED
    pairs["confidence_grade"] = "B"
    return pairs[PAIR_COLUMNS]


def condition_registry(records: pd.DataFrame) -> pd.DataFrame:
    roles = ["catalyst_system", "catalyst", "ligand", "base", "additive", "solvent_1", "solvent_2"]
    rows: list[dict[str, str]] = []
    for role in roles:
        for source_dataset, group in records.groupby("source_dataset", sort=True):
            values = sorted({str(value) for value in group[role] if str(value) != NOT_REPORTED})
            for value in values:
                normalized = "NULL_COMPONENT" if value == "NULL_COMPONENT" else value
                # A shared spelling is not evidence of a cross-source entity
                # equivalence.  Source-scope the ID until a reviewed registry
                # mapping explicitly establishes that relationship.
                key = hashlib.sha256(
                    f"{source_dataset}|{role}|{normalized}".encode()
                ).hexdigest()[:12].upper()
                rows.append({
                    "component_id": f"CRB_{role.upper()}_{key}",
                    "role": role,
                    "normalized_name": normalized,
                    "source_dataset": source_dataset,
                    "raw_value": value,
                    "normalization_status": "explicit_null_component" if normalized == "NULL_COMPONENT" else "identity_from_source_reconstruction",
                    "structure_smiles": NOT_REPORTED,
                    "evidence": "core_v0_1_processed_record",
                })
    return pd.DataFrame(rows).sort_values(["role", "normalized_name", "source_dataset"])


def validate(records: pd.DataFrame, pairs: pd.DataFrame) -> None:
    if records.columns.tolist() != RECORD_COLUMNS or pairs.columns.tolist() != PAIR_COLUMNS:
        raise ValueError("Output columns do not match the v0.1 schema")
    if len(records) != 9900 or records["reaction_id"].nunique() != 9900:
        raise ValueError("Core must contain exactly 9,900 unique main-matrix records")
    counts = records.groupby("source_dataset").size().to_dict()
    expected = {"ahneman_doyle_buchwald_hartwig_2018": 4140, "perera_suzuki_miyaura_2018": 5760}
    if counts != expected:
        raise ValueError(f"Unexpected source counts: {counts}")
    if records.loc[records["yield_observed"], "yield_percent"].isna().any():
        raise ValueError("Observed yield cannot be null")
    if not records.loc[records["yield_observed"], "yield_percent"].between(0, 100).all():
        raise ValueError("Observed yields must be within 0--100")
    if not (records["zero_yield"] == (records["yield_observed"] & records["yield_percent"].eq(0))).all():
        raise ValueError("zero_yield must represent observed zeros only")
    endpoints = set(pairs["reaction_id_a"]).union(pairs["reaction_id_b"])
    if not endpoints.issubset(set(records["reaction_id"])):
        raise ValueError("Pair endpoint is absent from reaction records")
    if len(pairs) != 116156 or not (pairs["n_changed_factors"] == 1).all():
        raise ValueError("Unexpected strict pair count or non-single-factor pair")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records = pd.concat([ahneman_records(), perera_records()], ignore_index=True)
    pairs = pd.concat([
        standardize_pairs(ROOT / "data/processed/ahneman_buchwald_hartwig_single_factor_pairs.csv", "ahneman_doyle_buchwald_hartwig_2018"),
        standardize_pairs(ROOT / "data/processed/perera_suzuki_miyaura_single_factor_pairs.csv", "perera_suzuki_miyaura_2018"),
    ], ignore_index=True)
    validate(records, pairs)
    registry = condition_registry(records)

    records_path = OUT / "reaction_records.csv"
    pairs_path = OUT / "condition_pairs.csv"
    registry_path = OUT / "condition_registry.csv"
    records.to_csv(records_path, index=False)
    pairs.to_csv(pairs_path, index=False)
    registry.to_csv(registry_path, index=False)
    manifest = {
        "release": VERSION,
        "scope": "two-source HTE Core; no benchmark splits or cliff labels assigned",
        "record_count": int(len(records)),
        "pair_count": int(len(pairs)),
        "source_record_counts": {key: int(value) for key, value in records.groupby("source_dataset").size().items()},
        "source_pair_counts": {key: int(value) for key, value in pairs.groupby("source_dataset").size().items()},
        "observed_zero_yields": {key: int(value) for key, value in records.groupby("source_dataset")["zero_yield"].sum().items()},
        "files": {path.name: stable_sha256(path) for path in (records_path, pairs_path, registry_path)},
        "format_note": "CSV is the auditable interim deliverable; export equivalent Parquet only after pyarrow is installed in the pinned Python 3.10--3.12 environment.",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
