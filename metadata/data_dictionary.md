# CondRxnBench-Core 数据字典

## Core v0.2 candidate（2026-07-31）

权威交付位于 `data/processed/core_v0_2/*.parquet`；同名 CSV 是受 `configs/core_v0_2_contract.json` 约束的人工检查镜像。它保留 v0.1 主记录字段，并新增以下受审计字段/侧表：

| 表/字段组 | 主键 | 含义与关键约束 |
|---|---|---|
| `reaction_records` extensions | `reaction_id` | `standardization_version`、source artifact/provenance、source+role-scoped `condition_component_refs`、原始条件 map、outcome/QC/eligibility 状态；保留全部 9,900 主矩阵记录。 |
| `control_records` | `reaction_id` | 468 条 Ahneman controls，与主矩阵分离，保持原始分析字段和条件 refs。 |
| `record_structure_assertions` | `structure_assertion_id` | raw/normalized/canonical SMILES、InChIKey、parse/feature/disposition/evidence；仅 Ahneman `substrate_1`、`ligand`、`base`、`additive` 可为 `source_reported`。 |
| `condition_registry` | source-scoped `component_id` | role、raw value、显式空条件状态、结构状态和 evidence；`not_reported` 不是 entity。 |
| `continuous_observations` | `continuous_observation_id` | raw/normalized value/unit、rule/evidence 和闭集 `value_state`：`observed_numeric`、`NA`、`not_reported`。 |
| `condition_compositions` | `composition_id` | Perera 载体溶剂的原始标签、两组分与 9:1 比例；不丢弃 mixture 信息。 |
| `condition_mappings` | `mapping_id` | 非恒等 mapping 的 target/scope、rule/evidence/review；当前两条 legacy Perera solvent row 均为 `pending`，不可供 record refs 使用。 |

`NULL_COMPONENT` 是文字的显式实验水平；`not_reported` 是证据缺失；`NA` 是带 state 的 typed null；观测零值仍是数值 0 + `yield_observed=true` + `zero_yield=true`。candidate 不包含 v0.2 pairs、图、split、labels 或模型结果。

## Core v0.1（immutable baseline）

## `reaction_records.csv`

| 字段组 | 字段 | 含义 |
|---|---|---|
| 版本与来源 | `schema_version`, `source_dataset`, `source_record_id`, `provenance_path`, `source_file` | 版本及从派生记录回到固化原始文件的指针 |
| 标识 | `reaction_id`, `reaction_group_id`, `record_class`, `is_control`, `plate_id`, `batch_id`, `well_id` | 实验与操作性反应组标识；Core 只收录 `main_matrix` |
| 结构 | `reaction_class`, `substrate_1_name/smiles`, `substrate_2_name/smiles`, `product_name/smiles`, `atom_mapped_rxn`, `canonical_rxn`, `bond_changes` | 原始或重建已证实的结构信息；缺失为 `not_reported` |
| 离散条件 | `catalyst_system`, `catalyst`, `ligand`, `base`, `additive`, `solvent_1`, `solvent_2`, `atmosphere`, `vessel` | 条件按角色保存；不把复合角色擅自拆解 |
| 连续条件 | `temperature_c`, `time_h`, `residence_time_min`, `concentration_m`, `pressure_bar`, `scale_mmol`, `*_equiv` | 数值保留来源单位；未报告写 `not_reported` |
| 响应 | `yield_percent`, `yield_observed`, `zero_yield`, `yield_type`, `measurement_method`, `measurement_value_raw` | `zero_yield` 仅在真实观测为零时为真，不能与缺失混淆 |
| QC | `success_label`, `quality_grade`, `qc_flags`, `manual_review_status` | 支持审计；不提前生成分类标签 |

验证规则：`reaction_id` 唯一；所有 `yield_observed=true` 的 `yield_percent` 在 0--100；`zero_yield=true` 当且仅当观测到的产率为 0。

## `condition_pairs.csv`

| 字段 | 含义 |
|---|---|
| `pair_id`, `source_dataset`, `reaction_group_id` | pair 及其严格来源分组 |
| `reaction_id_a`, `reaction_id_b` | 两端必须引用同一数据源的主表记录 |
| `changed_factor`, `n_changed_factors`, `condition_a`, `condition_b` | 被改变的单一离散条件及其两端取值 |
| `yield_a`, `yield_b`, `delta_yield`, `abs_delta_yield` | 原始、带方向和绝对的条件效应 |
| `pair_definition`, `condition_distance`, `cliff_label`, `confidence_grade` | 本版 pair 的定义、距离和审计状态 |

验证规则：所有 pair 都有 `n_changed_factors=1`，两端均为观测产率，且同属一个 `reaction_group_id`。Core v0.1 不设 cliff 标签；proposal 中 30 pp 的主阈值只能在预注册为 benchmark 规则后应用。
