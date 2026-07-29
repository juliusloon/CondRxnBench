#!/usr/bin/env python3
"""Rebuild Ahneman--Doyle HTE records from SI layout and raw per-well exports.

No derived rxnpredict table is used as an input.  The source repository stores
the SI layout tables and one LC/UV export per plate quadrant; joining those by
their physical well locations is the provenance-preserving reconstruction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def location_to_row_col(location: str, block: int, plate: int) -> tuple[int, int]:
    # This orientation is specified by the SI plate exports and independently
    # documented in the original rxnpredict reconstruction utility.
    first, second = location.split(":")
    if plate == 3:
        row_letter, col = first, int(second)
    else:
        col, row_letter = int(first), second
    row = ord(row_letter) - ord("A") + 1
    if block == 2:
        col += 24
    elif block == 3:
        row += 16
    elif block == 4:
        row += 16
        col += 24
    return row, col


def read_wells(root: Path) -> tuple[pd.DataFrame, list[Path]]:
    frames, files = [], []
    for plate in (1, 2, 3):
        for block in (1, 2, 3, 4):
            path = root / "yield_data" / f"plate{plate}.{block}.csv"
            raw = pd.read_csv(path)
            raw = raw.loc[raw["Location"].notna()].copy()
            raw[["row", "col"]] = raw["Location"].map(
                lambda x: location_to_row_col(x, block, plate)
            ).apply(pd.Series)
            raw["plate"] = plate
            raw["block"] = block
            raw["source_file"] = str(path)
            raw["source_well"] = raw["Location"]
            frames.append(raw[["plate", "block", "row", "col", "source_file", "source_well",
                               "Sample Name", "Data File", "product", "internal_standard",
                               "corr_factor", "product_scaled"]])
            files.append(path)
    return pd.concat(frames, ignore_index=True), files


def read_compounds(root: Path) -> dict[str, pd.DataFrame]:
    names = {
        "additive": ("additive-list.csv", "component", "Additive_SMILES"),
        "aryl_halide": ("aryl_halide-list.csv", "component", "Aryl_halide_SMILES"),
        "base": ("base-list.csv", "name", "Base_SMILES"),
        "ligand": ("ligand-list.csv", "name", "Ligand_SMILES"),
    }
    out = {}
    for role, (filename, key, smiles) in names.items():
        df = pd.read_csv(root / "smiles" / filename)
        # For base/ligand the physical layout stores the component name itself,
        # so that name becomes the index and must not also be selected as a
        # column. Additive/aryl-halide layouts instead store a numeric ID.
        columns = [smiles] if key == "name" else ["name", smiles]
        out[role] = df.set_index(key)[columns].rename(columns={smiles: f"{role}_smiles"})
    return out


def build_layout(root: Path) -> tuple[pd.DataFrame, list[Path]]:
    rows_path, cols_path = root / "layout" / "Table_S1.csv", root / "layout" / "Table_S2.csv"
    rows, cols, compounds = pd.read_csv(rows_path), pd.read_csv(cols_path), read_compounds(root)
    records = []
    for plate in (1, 2, 3):
        additive_column = f"Additive (Plate {plate})"
        for _, r in rows.iterrows():
            for _, c in cols.iterrows():
                record = {"plate": plate, "row": int(r.Row), "col": int(c.Column),
                          "ligand": r.Ligand, "base": c.Base,
                          "additive_number": r[additive_column], "aryl_halide_number": c["Aryl Halide"]}
                records.append(record)
    layout = pd.DataFrame(records)
    for role, number_col in (("additive", "additive_number"), ("aryl_halide", "aryl_halide_number")):
        lookup = compounds[role].copy()
        lookup.index = pd.to_numeric(lookup.index)
        layout = layout.join(lookup, on=number_col)
        layout = layout.rename(columns={"name": role})
    for role in ("base", "ligand"):
        layout = layout.join(compounds[role], on=role)
    return layout, [rows_path, cols_path, root / "smiles" / "additive-list.csv", root / "smiles" / "aryl_halide-list.csv", root / "smiles" / "base-list.csv", root / "smiles" / "ligand-list.csv"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path,
                        default=Path("data/raw/ahneman_doyle_rxnpredict"),
                        help="versioned raw rxnpredict subset (default: %(default)s)")
    parser.add_argument("--out-root", type=Path, default=Path("."))
    args = parser.parse_args()
    root, out = args.source_root.resolve(), args.out_root.resolve()
    wells, well_files = read_wells(root)
    layout, layout_files = build_layout(root)
    merged = layout.merge(wells, how="left", on=["plate", "row", "col"], validate="one_to_one")
    merged["is_control"] = merged[["additive", "aryl_halide"]].isna().any(axis=1)
    merged["record_class"] = merged["is_control"].map({False: "main_matrix", True: "control"})
    merged["control_type"] = pd.NA
    merged.loc[merged["additive"].isna() & merged["aryl_halide"].notna(), "control_type"] = "additive_free_control"
    merged.loc[merged["additive"].notna() & merged["aryl_halide"].isna(), "control_type"] = "aryl_halide_free_control"
    merged.loc[merged["additive"].isna() & merged["aryl_halide"].isna(), "control_type"] = "blank_control"
    merged["yield_percent"] = pd.to_numeric(merged["product_scaled"], errors="coerce")
    merged["yield_observed"] = merged["yield_percent"].notna()
    merged["zero_yield"] = merged["yield_percent"].eq(0) & merged["yield_observed"]
    merged["reaction_group_id"] = merged["aryl_halide_number"].map(
        lambda x: f"AHNEMAN_BH_ARYL_{int(x):02d}" if pd.notna(x) else pd.NA
    )
    merged["reaction_id"] = merged.apply(
        lambda x: f"AHNEMAN_BH_P{x.plate}_R{x.row:02d}_C{x.col:02d}", axis=1
    )
    # The four levels are pre-formed Pd(II)--ligand precatalysts in this HTE,
    # not independently combinable free ligand/Pd variables.
    merged["catalyst_system"] = merged["ligand"]
    main_cols = ["aryl_halide", "ligand", "base", "additive"]
    main = merged.loc[~merged.is_control].copy()
    controls = merged.loc[merged.is_control].copy()
    # Expected full factorial cells are defined by named factors, not by any
    # analytical outcome. This retains failed/NA measurements as missing data.
    expected = 15 * 4 * 3 * 23
    assert len(main) == expected, (len(main), expected)
    assert not main[main_cols].isna().any().any()
    processed = out / "data" / "processed"
    meta = out / "data" / "raw_metadata"
    processed.mkdir(parents=True, exist_ok=True); meta.mkdir(parents=True, exist_ok=True)
    keep = ["reaction_id", "reaction_group_id", "record_class", "is_control", "control_type", "plate", "block", "row", "col",
            "source_file", "source_well", "Sample Name", "Data File", "aryl_halide_number", "aryl_halide",
            "aryl_halide_smiles", "catalyst_system", "ligand", "ligand_smiles", "base", "base_smiles", "additive_number", "additive",
            "additive_smiles", "yield_percent", "yield_observed", "zero_yield", "product", "internal_standard", "corr_factor"]
    main[keep].to_csv(processed / "ahneman_buchwald_hartwig_main_matrix.csv", index=False)
    controls[keep].to_csv(processed / "ahneman_buchwald_hartwig_controls.csv", index=False)
    manifest = {"source_repository": str(root), "input_policy": "SI layout + raw per-well LC/UV exports only; derived CSVs excluded",
                "files": [{"path": str(p), "sha256": sha256(p)} for p in sorted(well_files + layout_files)],
                "expected_main_cells": expected, "reconstructed_main_cells": int(len(main)), "controls": int(len(controls))}
    (meta / "ahneman_raw_input_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
