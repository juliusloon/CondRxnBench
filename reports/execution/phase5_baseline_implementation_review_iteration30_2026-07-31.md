# Phase 5 Round B — Baseline Candidate Implementation Independent Review (Iteration 30)

## Verdict

**FAIL — two former P0 issues are repaired, but winner-manifest provenance still violates the accepted contract.**

This was a read-only review; no training or result artifact was regenerated.

## Iteration 29 repair status

| Finding | Result | Evidence |
| --- | --- | --- |
| Persisted pretest winner freeze | PASS | Runner requires `metadata/benchmark_v0_1_pretest_winner_freeze.jsonl` before materialization. For each formal run it recomputes the train/val winner and rejects any non-identical frozen row before training on train+val or predicting test. The pretest file and candidate winner JSONL have 216 identical ordered rows. |
| Unsupported/failure audit artifacts | PASS | Candidate now has `unsupported_family_ledger.parquet` with four source×structural-family N/A rows and their evidence paths/source data versions, plus a schema-correct empty `failure_ledger.parquet`. |
| Actual control predictions | PASS | 108 control-ledger rows and 79,884 control test predictions remain present; 216 formal runs, 324 total runs, and candidate-not-promoted status remain correct. |

## Remaining P0 — winner manifest hash is still the wrong algorithm

The accepted contract defines winner-manifest hash as SHA-256 of canonical
newline-joined ordered `freeze_sha256` values.  For both the pretest and output
JSONL, independent calculation gives:

```text
c02ebfe1dd06ddecd2a76737cfb6e08ecd5ef8cd079acfb5f838ae5c6da9d8fb
```

The files and candidate manifest instead use the raw JSONL byte SHA-256:

```text
6be2a06628b5174845a0a62eaf76c502d227efd73f4e498adcd695580877c26e
```

The ordered 216 rows and individual row hashes are correct, but raw-byte hash
is not the frozen `winner_freeze.manifest_hash` algorithm.  This prevents an
independent verifier from accepting the result under the contract’s stated
provenance semantics.

**Required repair:** implement one shared winner-manifest-hash function that
hashes the ordered newline-joined row hashes; store that value in the pretest
freeze provenance and candidate manifest; verify it before every test run and
in the result verifier.  Rebuild candidate output after this semantic-preserving
change.

## Review decision

Do not compute/accept a leaderboard or promote baselines.  Repair the single
remaining P0 provenance defect, rebuild, and repeat Round B/C verification.
