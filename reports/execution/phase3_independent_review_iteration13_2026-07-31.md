# Phase 3 Independent Adversarial Audit — Iteration 13

Date: 2026-07-31  
Reviewer role: independent adversarial reviewer  
Result: **PASS — no P0 risk or unhandled critical leakage found in the stated strict-candidate scope.**

## Isolated rerun

- Created a new clean copied workspace at `/private/tmp/condrxnbench-phase3-review13b.B0IeBW/repo`.
- Ran `scripts/audit_phase3_bias_leakage.py` with Python 3.11.15 and compared its JSON byte-for-byte with the reviewed workspace JSON. The outputs are identical and valid JSON.
- This audit is correctly scoped to the strict candidate only: no split, model, or pretraining evaluation artifact exists.

## Nine risk-class acceptance checks

Each of the nine risk classes has an allowed disposition (`tested`, `not_testable`, or `not_applicable`) and a nonempty impact/control statement. Its reported quantities or explicit reason constitute the evidence record.

| Risk class | Status | Independent evidence review | Impact/control present |
| --- | --- | --- | --- |
| Identity, group, and pair leakage | tested | `invalid_pairs=0`, duplicate pair IDs = 0, duplicate graph edge keys = 0; split leakage explicitly deferred because no splits exist | Yes |
| Measurement separation | tested | 4,132 Ahneman LC-UV-product-scaled outcomes and 5,760 Perera LC-MS/UV-area-percent-reported outcomes are separately reported | Yes |
| Missingness and observed-zero pattern | tested | Ahneman 4,140 records / 4,132 observed / 273 zero; Perera 5,760 / 5,760 / 275 | Yes |
| Design-position effects | tested | Ahneman plate means: 36.839 (n=1,252), 24.161 (n=1,440), 36.319 (n=1,440); Perera batch level is `not_reported` | Yes |
| Condition frequency and covariation | tested | Ahneman has 4 observed catalyst-ligand combinations; Perera solvent labels are DMF, MeCN, MeOH, THF; output correctly limits this to a descriptive shortcut diagnostic | Yes |
| Structure/scaffold coverage | not_testable | Complete verified reaction-structure coverage is absent; scaffold/template is explicitly `not_supported`, rather than inferred from a proxy | Yes |
| Pair-degree imbalance | tested | Degree min/median/max = 21/21/27; 8 main records are isolated from strict pairs | Yes |
| Controls isolation | tested | 468 controls, 9,900 main records, overlapping reaction IDs = 0, and pair endpoints referencing controls = 0 | Yes |
| Pretraining contamination | not_applicable | No pretrained model is used or evaluated in this phase | Yes |

`audit_tool_controls` is an additional, tenth check rather than one of the nine risk classes; it also carries the required status, impact, and control fields.

## Leakage and adversarial controls

- The automated identity/group/pair check reports zero invalid pairs, zero duplicate pair IDs, and zero duplicate graph keys.
- The emitted positive control reports `positive_cross_source_detected=true`; the emitted negative control reports `negative_valid_pair_accepted=true`.
- Independently, I mutated a real strict pair so that one endpoint came from the other source dataset. The script's same predicate rejected this true cross-source-endpoint pair. The unmodified real strict pair passed. Thus the gate is not merely accepting its own JSON declaration.
- Controls remain isolated from both main records and pair endpoints; no control-outcome leakage was found.

## Decision and residual boundaries

No P0 risk is present for the current strict candidate: the audit directly quantifies leakage, measurement provenance, missingness/zeros, position, condition covariance, degree imbalance, and controls isolation; unavailable scaffold and pretraining claims are explicitly bounded rather than implied.

The synthetic control currently changes the declared source label of a valid pair; the independent true cross-source-endpoint mutation above confirms the predicate also detects the stronger case. Replacing the in-script synthetic control with that endpoint mutation would improve adversarial specificity, but it is not a release-blocking gap because the deployed predicate and the independent stronger control both reject cross-source endpoints. Split/model/pretraining leakage remains out of scope until those artifacts are introduced and must be audited then.
