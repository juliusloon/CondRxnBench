# Ahneman--Doyle HTE: reconstruction QC

## Matrix integrity

- Theoretical main factorial cells: **4,140** (15 aryl halides × 4 catalyst systems × 3 bases × 23 additives).
- Reconstructed main cells: **4,140**; unique condition combinations: **4,140**; duplicate combinations: **0**.
- Analytical outcomes missing: **8**; observed yields: **4,132**.
- Observed zero yields: **273** (6.6%). Zero is retained as an observed outcome, never recoded as missing.

## Field-level frequencies, missingness, and zero yields

### aryl_halide

| aryl_halide                         |   records |   missing_yield |   zero_yield |   zero_yield_rate |   median_yield |
|:------------------------------------|----------:|----------------:|-------------:|------------------:|---------------:|
| 1-bromo-4-(trifluoromethyl)benzene  |       276 |               1 |            5 |             0.018 |         28.351 |
| 1-bromo-4-ethylbenzene              |       276 |               0 |            6 |             0.022 |         41.468 |
| 1-bromo-4-methoxybenzene            |       276 |               0 |           13 |             0.047 |         21.667 |
| 1-chloro-4-(trifluoromethyl)benzene |       276 |               0 |           15 |             0.054 |         10.107 |
| 1-chloro-4-ethylbenzene             |       276 |               2 |           35 |             0.127 |          2.794 |
| 1-chloro-4-methoxybenzene           |       276 |               0 |          114 |             0.413 |          0.379 |
| 1-ethyl-4-iodobenzene               |       276 |               1 |            2 |             0.007 |         61.437 |
| 1-iodo-4-(trifluoromethyl)benzene   |       276 |               1 |            3 |             0.011 |         36.643 |
| 1-iodo-4-methoxybenzene             |       276 |               0 |            6 |             0.022 |         35.598 |
| 2-bromopyridine                     |       276 |               0 |            5 |             0.018 |         51.749 |
| 2-chloropyridine                    |       276 |               2 |            8 |             0.029 |         36.611 |
| 2-iodopyridine                      |       276 |               0 |            3 |             0.011 |         62.287 |
| 3-bromopyridine                     |       276 |               0 |           14 |             0.051 |         41.821 |
| 3-chloropyridine                    |       276 |               0 |           35 |             0.127 |          8.411 |
| 3-iodopyridine                      |       276 |               1 |            9 |             0.033 |         55.265 |

### catalyst_system

| catalyst_system   |   records |   missing_yield |   zero_yield |   zero_yield_rate |   median_yield |
|:------------------|----------:|----------------:|-------------:|------------------:|---------------:|
| AdBrettPhos       |      1035 |               1 |           82 |             0.079 |         28.459 |
| XPhos             |      1035 |               0 |           95 |             0.092 |         15.122 |
| t-BuBrettPhos     |      1035 |               2 |           61 |             0.059 |         35.333 |
| t-BuXPhos         |      1035 |               5 |           35 |             0.034 |         39.554 |

### base

| base   |   records |   missing_yield |   zero_yield |   zero_yield_rate |   median_yield |
|:-------|----------:|----------------:|-------------:|------------------:|---------------:|
| BTMG   |      1380 |               6 |          115 |             0.083 |         28.409 |
| MTBD   |      1380 |               2 |           59 |             0.043 |         38.501 |
| P2Et   |      1380 |               0 |           99 |             0.072 |         16.714 |

### additive

| additive                                        |   records |   missing_yield |   zero_yield |   zero_yield_rate |   median_yield |
|:------------------------------------------------|----------:|----------------:|-------------:|------------------:|---------------:|
| 3,5-dimethylisoxazole                           |       180 |               0 |            3 |             0.017 |         40.695 |
| 3-methyl-5-phenylisoxazole                      |       180 |               0 |           11 |             0.061 |         39.125 |
| 3-methylisoxazole                               |       180 |               2 |            6 |             0.033 |         46.679 |
| 3-phenylisoxazole                               |       180 |               2 |            0 |             0.000 |         46.496 |
| 4-phenylisoxazole                               |       180 |               1 |            5 |             0.028 |         26.392 |
| 5-(2,6-difluorophenyl)isoxazole                 |       180 |               0 |            4 |             0.022 |         20.021 |
| 5-Phenyl-1,2,4-oxadiazole                       |       180 |               3 |           37 |             0.206 |          7.023 |
| 5-methyl-3-(1H-pyrrol-1-yl)isoxazole            |       180 |               0 |            1 |             0.006 |         41.040 |
| 5-methylisoxazole                               |       180 |               0 |            4 |             0.022 |         21.848 |
| 5-phenylisoxazole                               |       180 |               0 |            4 |             0.022 |         22.483 |
| N,N-dibenzylisoxazol-3-amine                    |       180 |               0 |            0 |             0.000 |         44.940 |
| N,N-dibenzylisoxazol-5-amine                    |       180 |               0 |           15 |             0.083 |         22.071 |
| benzo[c]isoxazole                               |       180 |               0 |           29 |             0.161 |          7.985 |
| benzo[d]isoxazole                               |       180 |               0 |            4 |             0.022 |         28.448 |
| ethyl-3-methoxyisoxazole-5-carboxylate          |       180 |               0 |            6 |             0.033 |         38.720 |
| ethyl-3-methylisoxazole-5-carboxylate           |       180 |               0 |           14 |             0.078 |         44.501 |
| ethyl-5-methylisoxazole-3-carboxylate           |       180 |               0 |            1 |             0.006 |         44.736 |
| ethyl-5-methylisoxazole-4-carboxylate           |       180 |               0 |           14 |             0.078 |         15.279 |
| ethyl-isoxazole-3-carboxylate                   |       180 |               0 |           37 |             0.206 |         20.083 |
| ethyl-isoxazole-4-carboxylate                   |       180 |               0 |           42 |             0.233 |          2.854 |
| methyl-5-(furan-2-yl)isoxazole-3-carboxylate    |       180 |               0 |           16 |             0.089 |         36.087 |
| methyl-5-(thiophen-2-yl)isoxazole-3-carboxylate |       180 |               0 |           10 |             0.056 |         35.177 |
| methyl-isoxazole-5-carboxylate                  |       180 |               0 |           10 |             0.056 |         12.508 |

## Cross-combination completeness

Every named four-factor combination is represented once in the physical design. Outcome completeness is assessed separately, so an analytical NA cannot masquerade as an absent experiment.

- Design coverage: **100.0%**
- Outcome coverage: **99.8%**

## Single-factor perturbation pairs

Pairs were enumerated before any cliff label or threshold. Both endpoints must have observed yields; all four named factors are compared exactly, and only `n_changed_factors = 1` is retained.

| changed_factor   |   pairs |
|:-----------------|--------:|
| additive         |   45365 |
| catalyst_system  |    6187 |
| base             |    4124 |

### Absolute Δyield distribution (percentage points)

| changed_factor   |    p50 |    p75 |    p90 |    p95 |
|:-----------------|-------:|-------:|-------:|-------:|
| additive         | 10.256 | 24.857 | 42.781 | 52.866 |
| base             |  8.952 | 20.204 | 35.235 | 45.754 |
| catalyst_system  |  6.550 | 19.269 | 36.849 | 46.915 |

No cliff threshold is set in this report. The quantiles are descriptive inputs for a pre-registered threshold decision, not a post hoc sample-selection rule.
