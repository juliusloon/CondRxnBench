# Phase 4 Round A — Proposed.9 Independent Contract Review (Iteration 21)

## Verdict

**FAIL — the functional repairs pass, but the claimed required-fixture union is
still false. Do not generate splits.**

This was a read-only independent review. JSON parsing and the toy verifier both
pass, and the matrix provenance is current. The contract nevertheless does not
declare two fixtures it depends on, so required coverage can silently regress.

## Verified functional repairs

| Check | Result | Evidence |
| --- | --- | --- |
| Generic empty/missing validator | PASS | `validate_numeric_input()` returns the fixture’s `not_supported_with_reason` for empty input and `reject_input` for missing prediction; lines 70–71 execute both. |
| Pearson wrapper and constant guard | PASS | `pearson_contract()` has the required min-n/constant guard; lines 78–80 execute a distinct Pearson/Spearman fixture and the required constant-prediction result. |
| Matrix provenance | PASS | Current proposed.9 config SHA-256 `2beb6aef…5422cd`, Core/Benchmark manifest hashes, and 84-leaf count exactly match the matrix. |
| Prior metric and label protocol | PASS | Cliff single-class full object, exclusive direction/absent class, top-k, sensitivity denominator, Task 2 direct-Δ scope, and S0–S5/matrix protocol retain the prior passing behavior. |

## Remaining blocker — required fixture union is not exact

The contract’s `metrics.fixtures.required` set contains **19** IDs, whereas
`tests/fixtures/metrics_v0_1_toy_cases.json` contains **21** keys.  No required
ID is missing from the file, but the file has two undeclared keys:

- `pearson_constant_prediction`
- `sensitivity_positive`

Both are consumed by the verifier (lines 80 and 98).  They therefore carry
contract-relevant semantics but are not protected by the machine-readable
required-fixture contract.  A future edit can remove either one and still pass
any check that only ensures each required ID exists.

**Minimal repair:** append exactly these two keys to
`metrics.fixtures.required`, and add an executable exact-set assertion in the
toy verifier:

```text
set(contract.metrics.fixtures.required) == set(fixture)
```

Use the contract file directly or expose this equality through a shared
contract-verifier helper. This prevents the current regression from recurring.

## Review decision

No other unresolved Task, S0–S5, metric, or matrix-provenance conflict was
found. Correct the machine-readable required union and rerun Round A. No split,
prediction, metric result, baseline, or promotion is authorized by this FAIL.
