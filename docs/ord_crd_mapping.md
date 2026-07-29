# ORD/CRD mapping: Ahneman--Doyle Buchwald--Hartwig HTE

## Interpretation boundary

This source is a controlled HTE screen, not an ORD export. We preserve its
plate/well and LC/UV provenance in an internal **CRD** (CondRxnBench reaction
data) record now; an ORD record can be emitted only after all quantities,
solvents, vessel/setup, and outcome metadata have been recovered from the
original SI. Fields absent from the present raw analytical exports are marked
`not_reported`, rather than guessed.

## CRD fields emitted in this phase

| CRD field | Ahneman source / handling |
|---|---|
| `reaction_id` | deterministic plate-row-column key |
| `reaction_group_id` | fixed aryl halide + fixed p-toluidine coupling family |
| `electrophile` | SI compound list; source name and SMILES |
| `nucleophile` | fixed *p*-toluidine; add as constant in the next schema migration |
| `catalyst_system` | the pre-formed Pd(II)-ligand system; atomic categorical level |
| `base`, `additive` | SI compound list; source name and SMILES |
| `yield_value` | `product_scaled` from the raw LC/UV well export, 0--100 scale |
| `yield_observed` | analytical presence flag; distinct from zero yield |
| `provenance_path` | source plate/block CSV + original well location |
| `plate_id`, `batch_id` | plate and block retained |
| `is_control` | separated from the 4,140-cell factorial matrix |

## ORD mapping plan

| ORD concept | Mapping / status |
|---|---|
| `ReactionInput` | electrophile, p-toluidine, base, additive, and pre-catalyst need amount/equivalent records from SI; structures available for all varying small molecules |
| `ReactionSetup` | temperature, time, concentration, atmosphere, vessel: **not_reported in current machine-readable inputs**; recover only from original SI text |
| `ReactionOutcome` | product yield maps to outcome product measurement with `analysis_key = LC/UV product_scaled`; exact calibration semantics need SI verification |
| provenance | DOI, SI file/page/table, source repository commit/checksum, plate/well |

## Non-negotiable modelling rules

1. A zero `product_scaled` value is an observed failed outcome; `NA` is an
   unobserved/failed analytical measurement.
2. The four Pd--ligand precatalysts are represented as `catalyst_system`, not
   as independently variable Pd and ligand columns.
3. An additive is a controlled fragment perturbation, not a reaction substrate.
4. A condition pair fixes `reaction_group_id` and changes exactly one of
   `catalyst_system`, `base`, or `additive`.

