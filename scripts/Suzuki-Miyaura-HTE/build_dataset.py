#!/usr/bin/env python3
"""Build a provenance-preserving Perera Suzuki--Miyaura HTE dataset.

The only tabular input is the vendored Data File S1 workbook. Constant
experimental fields are added only where they are stated in the vendored
supporting-material PDF (Experiment 2 / Table S1).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


SOURCE_DATASET = "perera_suzuki_miyaura_2018"
NULL_COMPONENT = "NULL_COMPONENT"
SOLVENT_NORMALIZATION = {"MeOH/H2O_V2 9:1": "MeOH", "THF_V2": "THF"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def component_or_null(value: object) -> str:
    """Represent literal ``None`` as an explicit condition level."""
    return NULL_COMPONENT if value == "None" else str(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=Path("data/raw/perera_suzuki_miyaura"))
    parser.add_argument("--out-root", type=Path, default=Path("."))
    args = parser.parse_args()
    source_root, out_root = args.source_root.resolve(), args.out_root.resolve()
    xlsx = source_root / "aap9112_Data_File_S1.xlsx"
    pdf = source_root / "aap9112_perera_sm.pdf"

    # Keep literal "None" strings: they encode blank ligand/base experiments.
    raw = pd.read_excel(xlsx, dtype=object, keep_default_na=False)
    expected_raw_columns = [
        "Reaction_No", "Reactant_1_Name", "Reactant_1_Short_Hand", "Reactant_1_eq",
        "Reactant_1_mmol", "Reactant_2_Name", "Reactant_2_eq", "Catalyst_1_Short_Hand",
        "Catalyst_1_eq", "Ligand_Short_Hand", "Ligand_eq", "Reagent_1_Short_Hand",
        "Reagent_1_eq", "Solvent_1_Short_Hand", "Product_Yield_PCT_Area_UV",
        "Product_Yield_Mass_Ion_Count",
    ]
    assert raw.columns.tolist() == expected_raw_columns, raw.columns.tolist()
    assert len(raw) == 5760
    assert raw["Reaction_No"].is_unique and raw["Reaction_No"].notna().all()

    data = raw.copy()
    data["source_dataset"] = SOURCE_DATASET
    data["source_record_id"] = data["Reaction_No"].astype(int).astype(str)
    data["reaction_id"] = "PERERA_SM_" + data["Reaction_No"].astype(int).astype(str).str.zfill(4)
    data["reaction_group_id"] = (
        "PERERA_SM_" + data["Reactant_1_Short_Hand"].str.split(",").str[0]
        + "_" + data["Reactant_2_Name"].str.split(",").str[0]
    )
    data["record_class"] = "main_matrix"
    data["is_control"] = False

    data["ligand_raw"] = data["Ligand_Short_Hand"]
    data["ligand"] = data["Ligand_Short_Hand"].map(component_or_null)
    data["ligand_is_blank"] = data["Ligand_Short_Hand"].eq("None")
    data["base_raw"] = data["Reagent_1_Short_Hand"]
    data["base"] = data["Reagent_1_Short_Hand"].map(component_or_null)
    data["base_is_blank"] = data["Reagent_1_Short_Hand"].eq("None")
    data["solvent_1_raw"] = data["Solvent_1_Short_Hand"]
    data["solvent_1"] = data["Solvent_1_Short_Hand"].replace(SOLVENT_NORMALIZATION)
    data["solvent_normalization_note"] = data["Solvent_1_Short_Hand"].map(
        lambda value: "normalized_from_original_variant" if value in SOLVENT_NORMALIZATION else "original_label"
    )
    data["aqueous_cosolvent"] = "H2O"
    data["organic_to_water_volume_ratio"] = "9:1"
    data["catalyst"] = data["Catalyst_1_Short_Hand"]
    data["catalyst_equiv"] = pd.to_numeric(data["Catalyst_1_eq"])
    data["ligand_equiv_reported"] = pd.to_numeric(data["Ligand_eq"], errors="coerce")
    data["base_equiv_reported"] = pd.to_numeric(data["Reagent_1_eq"])
    data["reactant_1_equiv"] = pd.to_numeric(data["Reactant_1_eq"])
    data["reactant_1_mmol"] = pd.to_numeric(data["Reactant_1_mmol"])
    data["reactant_2_equiv"] = pd.to_numeric(data["Reactant_2_eq"])

    # Supporting material, Table S1 (S11) and Experiment 2 (S23--S24).
    data["temperature_c"] = 100.0
    data["residence_time_min"] = 1.0
    data["pressure_bar"] = 100.0
    data["flow_rate_ml_min"] = 1.0
    data["injection_volume_per_component_ul"] = 1.0
    data["reaction_segment_interval_s"] = 45.0
    data["reaction_environment"] = "glovebox; O2 <20 ppm; H2O <20 ppm"
    data["yield_percent"] = pd.to_numeric(data["Product_Yield_PCT_Area_UV"], errors="coerce")
    data["yield_observed"] = data["yield_percent"].notna()
    data["zero_yield"] = data["yield_observed"] & data["yield_percent"].eq(0)
    data["yield_type"] = "lc_ms_uv_area_percent_reported"
    data["measurement_method"] = "UPLC-MS/DAD; UV area percent"
    data["product_mass_ion_count"] = pd.to_numeric(data["Product_Yield_Mass_Ion_Count"], errors="coerce")
    data["substrate_smiles"] = "not_reported"
    data["product_smiles"] = "not_reported"

    assert data["reaction_group_id"].nunique() == 15
    assert (data.groupby("reaction_group_id").size() == 384).all()
    factors = ["reaction_group_id", "ligand", "base", "solvent_1"]
    assert not data.duplicated(factors).any()
    assert data["yield_observed"].all() and data["yield_percent"].between(0, 100).all()

    processed = out_root / "data" / "processed"
    metadata = out_root / "data" / "raw_metadata"
    processed.mkdir(parents=True, exist_ok=True)
    metadata.mkdir(parents=True, exist_ok=True)
    output = processed / "perera_suzuki_miyaura_main_matrix.csv"
    data.to_csv(output, index=False)
    manifest = {
        "source_dataset": SOURCE_DATASET,
        "input_policy": "Data File S1 is the sole tabular input; the supporting PDF supplies only cited constant experimental metadata.",
        "files": [{"path": str(xlsx), "sha256": sha256(xlsx)}, {"path": str(pdf), "sha256": sha256(pdf)}],
        "source_sheet": "Sheet1", "source_rows": int(len(raw)), "source_columns": int(len(raw.columns)),
        "reaction_groups": 15,
        "factorial_design": "15 substrate pairs x 12 ligand settings (including blank) x 8 base settings (including blank) x 4 carrier solvents",
        "solvent_normalization": SOLVENT_NORMALIZATION,
        "pdf_evidence": {"table_s1": "S11", "experiment_2": "S23-S24"}, "output": str(output),
    }
    (metadata / "perera_raw_input_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
