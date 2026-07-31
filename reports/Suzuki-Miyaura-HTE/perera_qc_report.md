# Perera Suzuki--Miyaura HTE: reconstruction QC

## Matrix integrity

- The design is **15 substrate pairs × 12 ligand settings × 8 base settings × 4 carrier solvents = 5,760** records.
- Reconstructed records: **5,760**; substrate reaction groups: **15**; duplicate normalized condition combinations: **0**.
- Analytical outcomes observed: **5,760**; observed zero yields: **275** (4.8%). Zero is retained as an observation.
- Literal `None` in Data File S1 is encoded as `NULL_COMPONENT`, not missingness.
- `MeOH/H2O_V2 9:1` → `MeOH` and `THF_V2` → `THF` only for the normalized carrier-solvent field. The raw label remains in `solvent_1_raw`; the supporting PDF specifies a four-solvent 9:1 organic/water design.

## Field-level frequencies and response distribution

### ligand

| ligand         |   records |   zero_yield |   zero_yield_rate |   median_yield |
|:---------------|----------:|-------------:|------------------:|---------------:|
| AmPhos         |       480 |           12 |             0.025 |         42.833 |
| CataCXium A    |       480 |           11 |             0.023 |         49.526 |
| NULL_COMPONENT |       480 |           14 |             0.029 |         22.591 |
| P(Cy)3         |       480 |           12 |             0.025 |         41.291 |
| P(Ph)3         |       480 |           12 |             0.025 |         59.265 |
| P(o-Tol)3      |       480 |            8 |             0.017 |         35.978 |
| P(tBu)3        |       480 |           17 |             0.035 |         32.583 |
| SPhos          |       480 |           16 |             0.033 |         48.373 |
| XPhos          |       480 |           19 |             0.040 |         46.242 |
| Xantphos       |       480 |           90 |             0.188 |         12.896 |
| dppf           |       480 |           49 |             0.102 |         24.636 |
| dtbpf          |       480 |           15 |             0.031 |         33.338 |

### base

| base           |   records |   zero_yield |   zero_yield_rate |   median_yield |
|:---------------|----------:|-------------:|------------------:|---------------:|
| CsF            |       720 |           29 |             0.040 |         33.457 |
| Et3N           |       720 |           41 |             0.057 |         30.592 |
| K3PO4          |       720 |           31 |             0.043 |         35.337 |
| KOH            |       720 |           28 |             0.039 |         40.176 |
| LiOtBu         |       720 |           35 |             0.049 |         35.323 |
| NULL_COMPONENT |       720 |           51 |             0.071 |         26.297 |
| NaHCO3         |       720 |           33 |             0.046 |         32.412 |
| NaOH           |       720 |           27 |             0.037 |         37.536 |

### solvent_1

| solvent_1   |   records |   zero_yield |   zero_yield_rate |   median_yield |
|:------------|----------:|-------------:|------------------:|---------------:|
| DMF         |      1440 |          109 |             0.076 |         21.362 |
| MeCN        |      1440 |           66 |             0.046 |         29.083 |
| MeOH        |      1440 |           43 |             0.030 |         44.945 |
| THF         |      1440 |           57 |             0.040 |         35.646 |

## Single-factor perturbation pairs

Pairs were enumerated before any cliff threshold. Both endpoints share one strict `reaction_group_id`; exactly one of `ligand`, `base`, or normalized `solvent_1` changes. Blank ligand/base settings and zero outcomes remain eligible.

| changed_factor   |   pairs |
|:-----------------|--------:|
| base             |   20160 |
| ligand           |   31680 |
| solvent_1        |    8640 |

### Absolute Δyield distribution (percentage points)

| changed_factor   |    p50 |    p75 |    p90 |    p95 |
|:-----------------|-------:|-------:|-------:|-------:|
| base             |  6.314 | 17.145 | 29.907 | 38.445 |
| ligand           | 11.972 | 29.131 | 49.886 | 61.843 |
| solvent_1        | 12.183 | 27.182 | 44.399 | 54.325 |

No cliff threshold is set in this report. These quantiles are descriptive inputs for a later pre-registered threshold decision, not a rule used to select pairs.
