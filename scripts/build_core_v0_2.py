#!/usr/bin/env python3
"""Build a conservative, evidence-preserving Core v0.2 *candidate*.

This builder deliberately does not write pairs, graphs, splits or labels.  It
keeps the Core v0.1 compatibility columns and puts standardization facts in
side tables so no unreviewed mapping is promoted to a new chemical identity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from rdkit import Chem
from rdkit.Chem import inchi


_SCRIPT_ROOT = Path(__file__).resolve().parents[1]
ROOT = _SCRIPT_ROOT if (_SCRIPT_ROOT / "data").exists() else Path.cwd()
V01 = ROOT / "data" / "processed" / "core_v0_1"
VERSION = "CondRxnBench-Core-v0.2-proposed.3"
REGISTRY_VERSION = "core_v0_2_registry_source_scoped_v1"
ASSERTION_VERSION = "core_v0_2_source_assertion_v1"
MAPPING_VERSION = "core_v0_2_source_raw_identity_v1"
QC_VERSION = "core_v0_2_candidate_qc_v1"
NOT_REPORTED = "not_reported"
NULL_COMPONENT = "NULL_COMPONENT"
NA = "NA"
AHNEMAN = "ahneman_doyle_buchwald_hartwig_2018"
PERERA = "perera_suzuki_miyaura_2018"
ARTIFACTS = {
    AHNEMAN: "ahneman_doyle_rxnpredict_v0_2_candidate",
    PERERA: "perera_suzuki_miyaura_v0_2_candidate",
}
DISCRETE_ROLES = {
    AHNEMAN: ("catalyst_system", "ligand", "base", "additive"),
    PERERA: ("catalyst", "ligand", "base", "solvent_1", "solvent_2", "atmosphere"),
}
ALLOWED_STRUCTURE_ROLES = {AHNEMAN: {"substrate_1", "ligand", "base", "additive"}, PERERA: set()}
UNSUPPORTED_ASSERTION_ROLES = {
    AHNEMAN: ("catalyst_system", "catalyst", "substrate_2", "product", "atom_mapped_rxn", "canonical_rxn", "bond_changes"),
    PERERA: ("substrate_1", "substrate_2", "product", "catalyst", "ligand", "base", "solvent_1", "solvent_2", "atom_mapped_rxn", "canonical_rxn", "bond_changes"),
}
CONTINUOUS_FIELDS = (
    "temperature_c", "time_h", "residence_time_min", "concentration_m", "pressure_bar", "scale_mmol",
    "catalyst_equiv", "ligand_equiv", "base_equiv", "substrate_1_equiv", "substrate_2_equiv",
)
FIELD_UNITS = {
    "temperature_c": "degC", "time_h": "h", "residence_time_min": "min", "concentration_m": "mol/L",
    "pressure_bar": "bar", "scale_mmol": "mmol", "catalyst_equiv": "equiv", "ligand_equiv": "equiv",
    "base_equiv": "equiv", "substrate_1_equiv": "equiv", "substrate_2_equiv": "equiv",
}

RECORD_EXTENSIONS = [
    "standardization_version", "source_artifact_id", "provenance_status", "condition_component_refs",
    "condition_raw_values", "condition_mapping_version", "outcome_observation_status", "record_qc_status",
    "qc_rule_version", "eligibility_status", "eligibility_policy_version", "eligibility_reason_codes",
    "quality_grade_basis", "quality_grade_version",
]
ASSERTION_COLUMNS = [
    "structure_assertion_id", "reaction_id", "source_dataset", "structure_role", "assertion_version",
    "structure_raw_value", "structure_raw_format", "source_artifact_id", "source_locator", "evidence_id",
    "structure_evidence_status", "normalized_smiles", "canonical_smiles", "inchikey", "normalization_rule_version",
    "parse_sanitize_status", "error_class", "curation_disposition", "review_status", "murcko_status", "murcko_reason",
    "ecfp4_status", "ecfp4_reason", "ecfp6_status", "ecfp6_reason", "drfp_status", "drfp_reason",
    "reaction_center_fp_status", "reaction_center_fp_reason",
]
REGISTRY_COLUMNS = [
    "component_id", "registry_version", "entity_scope", "source_dataset", "role", "raw_value", "normalized_name",
    "component_value_state", "structure_raw_value", "normalized_smiles", "canonical_smiles", "inchikey",
    "structure_status", "structure_error_class", "evidence_id", "source_artifact_id", "source_locator", "review_status",
]
MAPPING_COLUMNS = [
    "mapping_id", "mapping_version", "source_component_id", "source_scope", "target_representation", "target_scope",
    "mapping_kind", "non_identity", "source_raw_value", "normalized_value", "rule_id", "rule_version", "evidence_id",
    "source_artifact_id", "source_locator", "review_status", "reviewer_id", "review_disposition",
]
ATTRIBUTE_COLUMNS = [
    "attribute_id", "component_id", "attribute_name", "attribute_value", "attribute_provenance", "evidence_id",
    "source_artifact_id", "source_locator", "review_status",
]
COMPOSITION_COLUMNS = [
    "composition_id", "reaction_id", "role", "raw_label", "component_component_id", "component_scope", "component_label",
    "ratio_raw_value", "ratio_raw_unit", "ratio_normalized_value", "ratio_normalized_unit", "composition_rule_id",
    "composition_rule_version", "evidence_id", "source_artifact_id", "source_locator", "review_status",
]
CONTINUOUS_COLUMNS = [
    "continuous_observation_id", "reaction_id", "source_dataset", "field_name", "raw_value", "raw_unit", "normalized_value",
    "normalized_unit", "conversion_rule_id", "conversion_rule_version", "evidence_id", "source_artifact_id", "source_locator",
    "value_state", "review_status",
]

MAP_COLUMNS = {"reaction_records": ("condition_component_refs", "condition_raw_values"), "control_records": ("condition_component_refs", "condition_raw_values")}
LIST_COLUMNS = {"reaction_records": ("eligibility_reason_codes",), "control_records": ("eligibility_reason_codes",)}
BOOL_COLUMNS = {
    "reaction_records": {"is_control", "yield_observed", "zero_yield"},
    "control_records": {"is_control", "yield_observed", "zero_yield"},
    "condition_mappings": {"non_identity"},
}
FLOAT_COLUMNS = {
    "reaction_records": {"yield_percent", "measurement_value_raw"},
    "control_records": {"yield_percent", "product", "internal_standard", "corr_factor"},
    "condition_compositions": {"ratio_normalized_value"},
    "continuous_observations": {"raw_value", "normalized_value"},
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def stable_id(prefix: str, *values: object) -> str:
    digest = hashlib.sha256("|".join(str(v) for v in values).encode()).hexdigest()[:16].upper()
    return f"{prefix}_{digest}"


def text(value: Any) -> str:
    return NOT_REPORTED if value is None or pd.isna(value) else str(value)


def source_locator(source: str, role: str, value: str) -> str:
    if source == AHNEMAN:
        if role == "substrate_1":
            return f"data/raw/ahneman_doyle_rxnpredict/smiles/aryl_halide-list.csv:component={value}"
        if role in {"ligand", "base", "additive"}:
            filename = {"ligand": "ligand-list.csv", "base": "base-list.csv", "additive": "additive-list.csv"}[role]
            key = "name" if role in {"ligand", "base"} else "component"
            return f"data/raw/ahneman_doyle_rxnpredict/smiles/{filename}:{key}={value}"
        return f"data/raw/ahneman_doyle_rxnpredict/layout/Table_S1.csv:role={role};value={value}"
    return f"data/raw/perera_suzuki_miyaura/aap9112_Data_File_S1.xlsx:Sheet1:role={role};value={value}"


def rdkit_structure(raw: str) -> dict[str, Any]:
    if raw in {NOT_REPORTED, NA, ""}:
        raise ValueError("missing_source_smiles")
    molecule = Chem.MolFromSmiles(raw, sanitize=True)
    if molecule is None:
        raise ValueError("rdkit_mol_from_smiles_returned_none")
    canonical = Chem.MolToSmiles(molecule, canonical=True, isomericSmiles=True)
    return {"normalized_smiles": canonical, "canonical_smiles": canonical, "inchikey": inchi.MolToInchiKey(molecule)}


def registry_structure(source: str, role: str, raw_name: str, smiles: str | None) -> dict[str, Any]:
    if role not in ALLOWED_STRUCTURE_ROLES[source] or smiles is None:
        return {
            "structure_raw_value": NOT_REPORTED, "normalized_smiles": None, "canonical_smiles": None, "inchikey": None,
            "structure_status": "not_supported", "structure_error_class": "role_not_supported_by_source_boundary",
        }
    try:
        parsed = rdkit_structure(smiles)
    except Exception as exc:
        return {
            "structure_raw_value": smiles, "normalized_smiles": None, "canonical_smiles": None, "inchikey": None,
            "structure_status": "failed", "structure_error_class": type(exc).__name__ + ":" + str(exc),
        }
    return {"structure_raw_value": smiles, "structure_status": "success", "structure_error_class": "none", **parsed}


def read_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Core v0.1 has no literal `NA` token.  Let pandas restore its genuinely
    # blank numeric outcome cells so conservation checks keep numeric zero
    # distinct from missing analysis.
    records = pd.read_csv(V01 / "reaction_records.csv")
    ahneman = pd.read_csv(ROOT / "data" / "processed" / "ahneman_buchwald_hartwig_main_matrix.csv", keep_default_na=False)
    perera = pd.read_csv(ROOT / "data" / "processed" / "perera_suzuki_miyaura_main_matrix.csv", keep_default_na=False)
    controls = pd.read_csv(ROOT / "data" / "processed" / "ahneman_buchwald_hartwig_controls.csv", keep_default_na=False)
    if len(records) != 9900 or set(records.source_dataset) != {AHNEMAN, PERERA}:
        raise ValueError("unexpected Core v0.1 input")
    if len(ahneman) != 4140 or len(perera) != 5760 or len(controls) != 468:
        raise ValueError("unexpected source input cardinality")
    return records, ahneman.set_index("reaction_id"), perera.set_index("reaction_id"), controls


def raw_conditions(row: pd.Series, source_row: pd.Series, source: str) -> dict[str, str]:
    if source == AHNEMAN:
        return {role: text(row[role]) for role in DISCRETE_ROLES[source]}
    return {
        "catalyst": text(source_row["Catalyst_1_Short_Hand"]),
        "ligand": text(source_row["Ligand_Short_Hand"]),
        "base": text(source_row["Reagent_1_Short_Hand"]),
        "solvent_1": text(source_row["Solvent_1_Short_Hand"]),
        "solvent_2": "H2O",
        "atmosphere": text(row["atmosphere"]),
    }


def component_value_state(raw: str) -> tuple[str, str]:
    if raw == "None":
        return NULL_COMPONENT, "explicit_null_component"
    if raw in {NOT_REPORTED, NA, ""}:
        raise ValueError(f"not a valid registry component: {raw!r}")
    return raw, "explicit_component"


def component_id(source: str, role: str, raw: str) -> str:
    normalized, _ = component_value_state(raw)
    return stable_id("CRB_V02", source, role, normalized)


def build_registry(records: pd.DataFrame, ahneman: pd.DataFrame, perera: pd.DataFrame) -> tuple[pd.DataFrame, dict[tuple[str, str, str], str]]:
    entities: dict[tuple[str, str, str], dict[str, Any]] = {}
    for _, row in records.iterrows():
        source = row["source_dataset"]
        source_row = ahneman.loc[row.reaction_id] if source == AHNEMAN else perera.loc[row.reaction_id]
        for role, raw in raw_conditions(row, source_row, source).items():
            normalized, state = component_value_state(raw)
            key = (source, role, raw)
            if key in entities:
                continue
            smiles: str | None = None
            if source == AHNEMAN:
                field = {"ligand": "ligand_smiles", "base": "base_smiles", "additive": "additive_smiles"}.get(role)
                if field:
                    smiles = text(source_row[field])
            structure = registry_structure(source, role, raw, smiles)
            entities[key] = {
                "component_id": component_id(source, role, raw), "registry_version": REGISTRY_VERSION,
                "entity_scope": source, "source_dataset": source, "role": role, "raw_value": raw,
                "normalized_name": normalized, "component_value_state": state, **structure,
                "evidence_id": f"{source}:source_condition:{role}", "source_artifact_id": ARTIFACTS[source],
                "source_locator": source_locator(source, role, raw), "review_status": "not_required",
            }
    frame = pd.DataFrame(entities.values(), columns=REGISTRY_COLUMNS).sort_values(["source_dataset", "role", "raw_value"], kind="stable").reset_index(drop=True)
    lookup = {key: value["component_id"] for key, value in entities.items()}
    return frame, lookup


def record_extensions(records: pd.DataFrame, ahneman: pd.DataFrame, perera: pd.DataFrame, lookup: dict[tuple[str, str, str], str]) -> pd.DataFrame:
    out = records.copy()
    refs, raws, artifact_ids, statuses = [], [], [], []
    for _, row in records.iterrows():
        source = row.source_dataset
        source_row = ahneman.loc[row.reaction_id] if source == AHNEMAN else perera.loc[row.reaction_id]
        raw = raw_conditions(row, source_row, source)
        refs.append({role: lookup[(source, role, value)] for role, value in raw.items()})
        raws.append(raw)
        artifact_ids.append(ARTIFACTS[source])
        statuses.append("missing_analysis_export" if source == AHNEMAN and row.provenance_path == NOT_REPORTED else "direct_source_record")
    out.insert(len(out.columns), "standardization_version", VERSION)
    out["source_artifact_id"] = artifact_ids
    out["provenance_status"] = statuses
    out["condition_component_refs"] = refs
    out["condition_raw_values"] = raws
    out["condition_mapping_version"] = MAPPING_VERSION
    out["outcome_observation_status"] = out["yield_observed"].map({True: "observed_numeric", False: "missing_analysis"})
    out["record_qc_status"] = "pass"
    out["qc_rule_version"] = QC_VERSION
    out["eligibility_status"] = "not_assessed"
    out["eligibility_policy_version"] = "not_assessed_v1"
    out["eligibility_reason_codes"] = [[] for _ in range(len(out))]
    out["quality_grade_basis"] = "source_reconstruction_coverage_and_measurement_semantics"
    out["quality_grade_version"] = "core_v0_1_inherited_grade_v1"
    return out


def assertion_row(reaction_id: str, source: str, role: str, raw: str, locator: str, supported: bool) -> dict[str, Any]:
    base = {
        "structure_assertion_id": stable_id("CRB_SA", reaction_id, role, ASSERTION_VERSION), "reaction_id": reaction_id,
        "source_dataset": source, "structure_role": role, "assertion_version": ASSERTION_VERSION,
        "source_artifact_id": ARTIFACTS[source], "source_locator": locator,
        "evidence_id": f"{source}:structure:{role}", "normalization_rule_version": "core_v0_2_proposed_2",
        "review_status": "not_required",
    }
    if not supported:
        reason = "role_not_supported_by_source_boundary"
        return {**base, "structure_raw_value": NOT_REPORTED, "structure_raw_format": "not_reported", "structure_evidence_status": "not_reported",
                "normalized_smiles": None, "canonical_smiles": None, "inchikey": None, "parse_sanitize_status": "not_supported",
                "error_class": reason, "curation_disposition": "no_structure_asserted", "murcko_status": "not_supported", "murcko_reason": reason,
                "ecfp4_status": "not_supported", "ecfp4_reason": reason, "ecfp6_status": "not_supported", "ecfp6_reason": reason,
                "drfp_status": "not_supported", "drfp_reason": reason, "reaction_center_fp_status": "not_supported", "reaction_center_fp_reason": reason}
    try:
        parsed = rdkit_structure(raw)
    except Exception as exc:
        reason = type(exc).__name__ + ":" + str(exc)
        return {**base, "structure_raw_value": raw, "structure_raw_format": "smiles", "structure_evidence_status": "source_reported",
                "normalized_smiles": None, "canonical_smiles": None, "inchikey": None, "parse_sanitize_status": "failed", "error_class": reason,
                "curation_disposition": "retain_raw_no_feature_generation", "murcko_status": "failed", "murcko_reason": reason,
                "ecfp4_status": "failed", "ecfp4_reason": reason, "ecfp6_status": "failed", "ecfp6_reason": reason,
                "drfp_status": "not_supported", "drfp_reason": "reaction_representation_not_supported",
                "reaction_center_fp_status": "not_supported", "reaction_center_fp_reason": "reaction_representation_not_supported"}
    return {**base, "structure_raw_value": raw, "structure_raw_format": "smiles", "structure_evidence_status": "source_reported", **parsed,
            "parse_sanitize_status": "success", "error_class": "none", "curation_disposition": "canonicalized_conservative_no_identity_change",
            "murcko_status": "available", "murcko_reason": "sanitized_source_backed_smiles", "ecfp4_status": "available", "ecfp4_reason": "sanitized_source_backed_smiles",
            "ecfp6_status": "available", "ecfp6_reason": "sanitized_source_backed_smiles", "drfp_status": "not_supported", "drfp_reason": "reaction_representation_not_supported",
            "reaction_center_fp_status": "not_supported", "reaction_center_fp_reason": "reaction_representation_not_supported"}


def build_assertions(records: pd.DataFrame, ahneman: pd.DataFrame, perera: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, record in records.iterrows():
        source, rid = record.source_dataset, record.reaction_id
        source_row = ahneman.loc[rid] if source == AHNEMAN else perera.loc[rid]
        if source == AHNEMAN:
            structure_fields = {"substrate_1": "aryl_halide_smiles", "ligand": "ligand_smiles", "base": "base_smiles", "additive": "additive_smiles"}
            names = {"substrate_1": "aryl_halide", "ligand": "ligand", "base": "base", "additive": "additive"}
            for role, field in structure_fields.items():
                raw = text(source_row[field])
                rows.append(assertion_row(rid, source, role, raw, source_locator(source, role, text(source_row[names[role]])), True))
        for role in UNSUPPORTED_ASSERTION_ROLES[source]:
            rows.append(assertion_row(rid, source, role, NOT_REPORTED, f"{ARTIFACTS[source]}:source_boundary:{role}", False))
    return pd.DataFrame(rows, columns=ASSERTION_COLUMNS)


def continuous_value(source: str, source_row: pd.Series, field: str) -> tuple[float | None, str, str, str, str]:
    if source == AHNEMAN:
        return None, NOT_REPORTED, NOT_REPORTED, "no_source_evidence_no_conversion", "not_reported"
    source_column = {
        "temperature_c": "temperature_c", "residence_time_min": "residence_time_min", "pressure_bar": "pressure_bar",
        "scale_mmol": "reactant_1_mmol", "catalyst_equiv": "catalyst_equiv", "ligand_equiv": "ligand_equiv_reported",
        "base_equiv": "base_equiv_reported", "substrate_1_equiv": "reactant_1_equiv", "substrate_2_equiv": "reactant_2_equiv",
    }.get(field)
    if source_column is None:
        return None, NOT_REPORTED, NOT_REPORTED, "no_source_evidence_no_conversion", "not_reported"
    raw = source_row[source_column]
    if raw == "" or pd.isna(raw):
        return None, FIELD_UNITS[field], FIELD_UNITS[field], "source_blank_typed_missing_v1", "NA"
    return float(raw), FIELD_UNITS[field], FIELD_UNITS[field], "identity_source_reported_v1", "observed_numeric"


def build_continuous(records: pd.DataFrame, ahneman: pd.DataFrame, perera: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, record in records.iterrows():
        source, rid = record.source_dataset, record.reaction_id
        source_row = ahneman.loc[rid] if source == AHNEMAN else perera.loc[rid]
        for field in CONTINUOUS_FIELDS:
            raw, raw_unit, normalized_unit, rule, state = continuous_value(source, source_row, field)
            rows.append({"continuous_observation_id": stable_id("CRB_CO", rid, field), "reaction_id": rid, "source_dataset": source,
                         "field_name": field, "raw_value": raw, "raw_unit": raw_unit, "normalized_value": raw,
                         "normalized_unit": normalized_unit, "conversion_rule_id": rule, "conversion_rule_version": "v1",
                         "evidence_id": f"{source}:continuous:{field}", "source_artifact_id": ARTIFACTS[source],
                         "source_locator": source_locator(source, field, rid) if state == "observed_numeric" else NOT_REPORTED,
                         "value_state": state, "review_status": "not_required"})
    return pd.DataFrame(rows, columns=CONTINUOUS_COLUMNS)


def build_compositions(records: pd.DataFrame, perera: pd.DataFrame, lookup: dict[tuple[str, str, str], str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    perera_records = records.loc[records.source_dataset.eq(PERERA)]
    for _, record in perera_records.iterrows():
        raw_label = text(perera.loc[record.reaction_id, "Solvent_1_Short_Hand"])
        parts = (("organic_carrier", lookup[(PERERA, "solvent_1", raw_label)], 9.0), ("H2O", lookup[(PERERA, "solvent_2", "H2O")], 1.0))
        for label, cid, ratio in parts:
            rows.append({"composition_id": stable_id("CRB_COMP", record.reaction_id, label), "reaction_id": record.reaction_id, "role": "solvent",
                         "raw_label": raw_label, "component_component_id": cid, "component_scope": PERERA, "component_label": label,
                         "ratio_raw_value": "9:1", "ratio_raw_unit": "volume_ratio", "ratio_normalized_value": ratio,
                         "ratio_normalized_unit": "volume_parts", "composition_rule_id": "perera_documented_organic_water_ratio_v1",
                         "composition_rule_version": "v1", "evidence_id": "PERERA_SI_S24_SOLVENT_9_TO_1",
                         "source_artifact_id": ARTIFACTS[PERERA], "source_locator": "data/raw/perera_suzuki_miyaura/aap9112_perera_sm.pdf:S24",
                         "review_status": "not_required"})
    return pd.DataFrame(rows, columns=COMPOSITION_COLUMNS)


def build_mappings(lookup: dict[tuple[str, str, str], str]) -> pd.DataFrame:
    """Record historical non-identity labels without promoting them to entities.

    Core v0.1 retained a normalized carrier-solvent convenience column.  The
    two transformations below have source evidence but no independent mapping
    acceptance in this candidate.  They are therefore explicitly pending and
    records reference their source-raw registry entities instead.
    """
    rows = []
    for raw, target in (("MeOH/H2O_V2 9:1", "MeOH"), ("THF_V2", "THF")):
        rows.append({"mapping_id": stable_id("CRB_MAP", PERERA, "solvent_1", raw, target), "mapping_version": "perera_legacy_solvent_mapping_pending_v1",
                     "source_component_id": lookup[(PERERA, "solvent_1", raw)], "source_scope": PERERA,
                     "target_representation": target, "target_scope": "core_v0_1_compatibility_only", "mapping_kind": "condition_name_normalization",
                     "non_identity": True, "source_raw_value": raw, "normalized_value": target, "rule_id": "perera_v0_1_solvent_normalization_v1",
                     "rule_version": "v1", "evidence_id": "PERERA_WORKBOOK_SOLVENT_1_SHORT_HAND", "source_artifact_id": ARTIFACTS[PERERA],
                     "source_locator": "data/raw/perera_suzuki_miyaura/aap9112_Data_File_S1.xlsx:Sheet1:Solvent_1_Short_Hand",
                     "review_status": "pending", "reviewer_id": None, "review_disposition": "not_usable_until_independent_acceptance"})
    return pd.DataFrame(rows, columns=MAPPING_COLUMNS)


def build_controls(controls: pd.DataFrame, lookup: dict[tuple[str, str, str], str]) -> pd.DataFrame:
    out = controls.copy()
    refs, raws = [], []
    for _, row in out.iterrows():
        payload: dict[str, str] = {}
        for role in DISCRETE_ROLES[AHNEMAN]:
            raw = text(row[role])
            if raw != NOT_REPORTED:
                payload[role] = raw
        refs.append({role: lookup[(AHNEMAN, role, raw)] for role, raw in payload.items() if (AHNEMAN, role, raw) in lookup})
        raws.append(payload)
    out["standardization_version"] = VERSION
    out["source_artifact_id"] = ARTIFACTS[AHNEMAN]
    out["provenance_status"] = "direct_source_record"
    out["condition_component_refs"] = refs
    out["condition_raw_values"] = raws
    out["condition_mapping_version"] = MAPPING_VERSION
    out["outcome_observation_status"] = out["yield_observed"].map({True: "observed_numeric", False: "missing_analysis"})
    out["record_qc_status"] = "pass"
    out["qc_rule_version"] = QC_VERSION
    out["eligibility_status"] = "not_assessed"
    out["eligibility_policy_version"] = "not_assessed_v1"
    out["eligibility_reason_codes"] = [[] for _ in range(len(out))]
    out["quality_grade_basis"] = "source_reconstructed_control"
    out["quality_grade_version"] = "core_v0_1_inherited_grade_v1"
    return out


def ensure_columns(frame: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    frame = frame.copy()
    for column in columns:
        if column not in frame:
            frame[column] = None
    return frame[list(columns)]


def arrow_table(frame: pd.DataFrame, table: str) -> pa.Table:
    arrays: list[pa.Array] = []
    fields: list[pa.Field] = []
    map_columns = set(MAP_COLUMNS.get(table, ()))
    list_columns = set(LIST_COLUMNS.get(table, ()))
    for column in frame.columns:
        values = frame[column].tolist()
        if column in map_columns:
            typ = pa.map_(pa.string(), pa.string())
            arrays.append(pa.array(values, type=typ)); fields.append(pa.field(column, typ, nullable=False))
        elif column in list_columns:
            typ = pa.list_(pa.string())
            arrays.append(pa.array(values, type=typ)); fields.append(pa.field(column, typ, nullable=False))
        elif column in BOOL_COLUMNS.get(table, set()):
            typ = pa.bool_(); arrays.append(pa.array(values, type=typ)); fields.append(pa.field(column, typ, nullable=False))
        elif column in FLOAT_COLUMNS.get(table, set()):
            typ = pa.float64()
            numeric = pd.to_numeric(pd.Series(values), errors="coerce")
            arrays.append(pa.array([None if pd.isna(v) else float(v) for v in numeric], type=typ)); fields.append(pa.field(column, typ, nullable=True))
        else:
            typ = pa.string(); arrays.append(pa.array([None if pd.isna(v) else str(v) for v in values], type=typ)); fields.append(pa.field(column, typ, nullable=True))
    return pa.Table.from_arrays(arrays, schema=pa.schema(fields))


def csv_frame(frame: pd.DataFrame, table: str) -> pd.DataFrame:
    out = frame.copy()
    for column in MAP_COLUMNS.get(table, ()):
        out[column] = out[column].map(canonical_json)
    for column in LIST_COLUMNS.get(table, ()):
        out[column] = out[column].map(canonical_json)
    # Keep nullable numeric CSV cells in the same typed representation used
    # by Parquet.  In particular, an empty source string is an Arrow null,
    # not an empty numeric observation.
    for column in FLOAT_COLUMNS.get(table, set()):
        out[column] = pd.to_numeric(out[column], errors="coerce")
    return out


def schema_fingerprint(schema: pa.Schema) -> str:
    return hashlib.sha256(schema.serialize().to_pybytes()).hexdigest()


def write_table(frame: pd.DataFrame, table: str, out: Path) -> dict[str, Any]:
    csv_path, parquet_path = out / f"{table}.csv", out / f"{table}.parquet"
    stored_csv = csv_frame(frame, table)
    stored_csv.to_csv(csv_path, index=False, na_rep=NA, lineterminator="\n")
    arrow = arrow_table(frame, table)
    pq.write_table(arrow, parquet_path, compression="zstd")
    persisted_schema = pq.read_schema(parquet_path)
    return {"rows": len(frame), "primary_key": {"reaction_records": "reaction_id", "control_records": "reaction_id", "record_structure_assertions": "structure_assertion_id", "condition_registry": "component_id", "condition_mappings": "mapping_id", "condition_attributes": "attribute_id", "condition_compositions": "composition_id", "continuous_observations": "continuous_observation_id"}[table], "csv_sha256": sha256(csv_path), "parquet_sha256": sha256(parquet_path), "arrow_schema_fingerprint": schema_fingerprint(persisted_schema), "columns": list(frame.columns)}


def validate_frames(tables: dict[str, pd.DataFrame]) -> None:
    records, registry, assertions = tables["reaction_records"], tables["condition_registry"], tables["record_structure_assertions"]
    if len(records) != 9900 or not records.reaction_id.is_unique:
        raise ValueError("record cardinality failure")
    expected = {AHNEMAN: 4140, PERERA: 5760}
    if records.groupby("source_dataset").size().to_dict() != expected:
        raise ValueError("source record count failure")
    outcomes = records.groupby("source_dataset").agg(observed=("yield_observed", "sum"), zero=("zero_yield", "sum"))
    if outcomes.loc[AHNEMAN].to_dict() != {"observed": 4132, "zero": 273} or outcomes.loc[PERERA].to_dict() != {"observed": 5760, "zero": 275}:
        raise ValueError("outcome conservation failure")
    if not (records.zero_yield == (records.yield_observed & records.yield_percent.eq(0))).all():
        raise ValueError("zero sentinel failure")
    if registry.component_id.duplicated().any() or registry.raw_value.eq(NOT_REPORTED).any() or registry.normalized_name.eq(NOT_REPORTED).any():
        raise ValueError("registry sentinel/id failure")
    registry_index = registry.set_index("component_id")
    for _, row in records.iterrows():
        refs, raw = row.condition_component_refs, row.condition_raw_values
        if set(refs) != set(raw): raise ValueError("condition maps differ")
        for role, cid in refs.items():
            entity = registry_index.loc[cid]
            if entity.source_dataset != row.source_dataset or entity.role != role:
                raise ValueError("record component reference scope failure")
            if entity.component_value_state not in {"explicit_component", "explicit_null_component"}:
                raise ValueError("invalid component value state")
    for source, roles in DISCRETE_ROLES.items():
        subset = records.loc[records.source_dataset.eq(source)]
        for role in roles:
            states = [registry_index.loc[r[role], "component_value_state"] for r in subset.condition_component_refs]
            if len(states) != len(subset) or not set(states) <= {"explicit_component", "explicit_null_component"}:
                raise ValueError("condition coverage failure")
    allowed = assertions.loc[assertions.structure_evidence_status.eq("source_reported")]
    if len(allowed) != 4 * 4140 or not allowed.parse_sanitize_status.eq("success").all():
        raise ValueError("allowed structure parse coverage failure")
    if assertions.loc[assertions.source_dataset.eq(PERERA), "parse_sanitize_status"].ne("not_supported").any():
        raise ValueError("Perera default deny failure")
    if assertions.loc[assertions.source_dataset.eq(PERERA), ["normalized_smiles", "canonical_smiles", "inchikey"]].notna().any().any():
        raise ValueError("Perera structure fabrication failure")
    continuous = tables["continuous_observations"]
    if not set(continuous.value_state) <= {"observed_numeric", "NA", "not_reported"}:
        raise ValueError("continuous state domain failure")
    if continuous.loc[continuous.value_state.eq("observed_numeric"), ["raw_value", "normalized_value"]].isna().any().any():
        raise ValueError("observed continuous missing")
    if continuous.loc[continuous.value_state.ne("observed_numeric"), ["raw_value", "normalized_value"]].notna().any().any():
        raise ValueError("missing continuous became numeric")
    compositions = tables["condition_compositions"]
    if len(compositions) != 2 * 5760 or not compositions.ratio_raw_value.eq("9:1").all():
        raise ValueError("composition conservation failure")
    mapping = tables["condition_mappings"]
    if not mapping.empty:
        required = mapping.loc[mapping.non_identity]
        if required[["evidence_id", "source_locator", "rule_id", "rule_version"]].isna().any().any():
            raise ValueError("nonidentity mapping lacks evidence")
        if not required.review_status.isin({"accepted", "pending", "rejected"}).all():
            raise ValueError("mapping review state failure")
        # The candidate has no accepted non-identity mapping.  Its raw source
        # references must remain usable independently of the pending rows.
        if required.review_status.eq("accepted").any() or not records.condition_mapping_version.eq(MAPPING_VERSION).all():
            raise ValueError("unaccepted nonidentity mapping became usable")


def build(out: Path) -> dict[str, Any]:
    records, ahneman, perera, controls = read_inputs()
    registry, lookup = build_registry(records, ahneman, perera)
    tables: dict[str, pd.DataFrame] = {
        "reaction_records": record_extensions(records, ahneman, perera, lookup),
        "control_records": build_controls(controls, lookup),
        "record_structure_assertions": build_assertions(records, ahneman, perera),
        "condition_registry": registry,
        "condition_mappings": build_mappings(lookup),
        "condition_attributes": ensure_columns(pd.DataFrame(), ATTRIBUTE_COLUMNS),
        "condition_compositions": build_compositions(records, perera, lookup),
        "continuous_observations": build_continuous(records, ahneman, perera),
    }
    validate_frames(tables)
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    manifest_tables = {table: write_table(frame, table, out) for table, frame in tables.items()}
    manifest = {
        "release": VERSION, "status": "candidate_not_promoted", "contract": "configs/core_v0_2_contract.json",
        "scope": "standardized main records, separate controls, registry and side tables only; no v0.2 pairs, graphs, splits, labels or model results",
        "source_record_counts": {k: int(v) for k, v in records.groupby("source_dataset").size().items()},
        "source_outcomes": {source: {"records": int(len(group)), "observed": int(group.yield_observed.sum()), "missing": int((~group.yield_observed).sum()), "zero": int(group.zero_yield.sum())} for source, group in records.groupby("source_dataset")},
        "control_count": int(len(tables["control_records"])),
        "pair_baseline": {"count": 116156, "v0_1_csv_sha256": sha256(V01 / "condition_pairs.csv"), "included_as_output": False},
        "v0_1_input_hashes": {name: sha256(V01 / name) for name in ("reaction_records.csv", "condition_registry.csv", "condition_pairs.csv", "manifest.json")},
        "input_manifests": {path.name: sha256(path) for path in (ROOT / "metadata" / "raw_input_manifests").glob("*_v0_2_candidate.json")},
        "runtime": {"python": platform.python_version(), "pandas": pd.__version__, "pyarrow": pa.__version__, "rdkit": Chem.rdBase.rdkitVersion},
        "tables": manifest_tables,
        "sentinel_contract": {"NULL_COMPONENT": "literal explicit component", "not_reported": "literal source/evidence absence", "NA": "Arrow null and CSV token only for typed nullable values"},
        "unimplemented_by_design": ["nonidentity_or_cross_source_mappings", "condition_attributes", "v0_2_pairs", "graphs", "splits", "success_or_cliff_labels", "model_results"],
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=ROOT / "data" / "processed" / "core_v0_2")
    args = parser.parse_args()
    print(json.dumps(build(args.out_dir.resolve()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
