# Phase 4 Round A — Proposed.7 Independent Contract Review (Iteration 19)

## Verdict

**FAIL — close, but the fixture/verifier gate still does not exercise every
required negative/edge behavior through a contract function. Do not generate
splits.**

This was a read-only independent re-review. The toy verifier was run in the
pinned environment and passed. JSON parsing also passed. Nevertheless,
inspection exposes test cases that can pass while the frozen contract is
violated.

## Checks that pass

| Check | Result | Evidence |
| --- | --- | --- |
| Required fixture IDs are closed | PASS | `metrics.fixtures.required` has 19 IDs; the fixture has exactly the same 19 keys (`required − fixture = fixture − required = ∅`). |
| Matrix is fresh | PASS | Current proposed.7 config SHA-256 `ce596ebb…1dd9b8`, Core manifest `101e9d5b…c1f05e2`, and Benchmark manifest `79066267…1c78e33` exactly match the 84-leaf matrix fields. |
| New contract functions execute | PARTIAL PASS | `top_k_recall`, guarded sensitivity denominator, and direction absent-class paths are now executed against fixture values; the full toy command passes. |
| No new task/S0–S5/matrix conflict | PASS | No remaining source-free feasibility object or task-to-variance mismatch was found. |

## Remaining blocking defects

### P0-1 — the alleged Pearson/Spearman discriminator is not discriminating

Fixture `pearson_spearman_distinct` uses `truth=[1,2,3]` and
`pred=[1,3,2]`, but declares **both** Pearson and Spearman as `0.5`. It is
therefore not a non-collinear discriminator and cannot catch a metric swap.
Moreover, `corr()` continues to implement Spearman only; Pearson is called
directly via SciPy without a contract wrapper or its constant-vector guard.

**Minimal repair:** choose a fixture where the two coefficients differ, add a
`pearson_contract()` function with the same minimum-n/constant behavior, and
exercise both normal and constant-prediction cases through the two functions.

### P0-2 — missing/empty and cliff negative contract paths remain incomplete

- Lines 58–59 still do not run a generic input validator: empty is routed only
  through `top_k_recall(set(), [], 1)`, while missing prediction is verified by
  a fixture string plus `None` membership. Neither asserts a contract metric
  path returns `reject_input`.
- `cliff_metrics()` returns three statuses on a single class, but line 75
  asserts only AUPRC. Fixture `single_class_cliff` holds only
  `expected_auprc`; AUROC and F1 are unverified even though all three are
  contract metrics.

**Minimal repair:** add a shared prediction validator and fixture-driven
empty/missing cases for every applicable metric family; make
`single_class_cliff` carry the expected complete `{auprc, auroc, f1}` object
and compare the whole result.

### P0-3 — positive sensitivity and tied-optimum recommendation are still not fixture-driven

The non-zero sensitivity ratio at lines 85–86 uses inline NumPy arrays and an
inline `0.5`, not a fixture. The multiple-optimum recommendation at line 82
uses hard-coded `{"R1", "R2"}` and `["R2"]`, not its fixture’s IDs/yields.
The underlying top-k function is a real improvement, but these required
positive cases are not protected by versioned expected inputs/outputs.

**Minimal repair:** move both arrays/IDs/expected results into named required
fixture objects and compute results solely from them. Include a second
multiple-optimum case that confirms deterministic predicted-score tie handling.

## Review decision

The required-ID set and matrix provenance are now solid, and all prior protocol
issues remain closed. The three narrow test defects above still violate the
per-metric executable toy/boundary/negative gate. Repair fixture/verifier only
and repeat Round A; no split, prediction, metric result, baseline, or promotion
is authorized by this FAIL.
