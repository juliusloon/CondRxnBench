# CondRxnBench-Core v0.1 统一 Schema

## 设计边界

统一 schema 的目标是让两套数据由同一程序读取、生成 pair、实施划分和计算指标；它**不**宣称两种产率测量可以无差别合并。所有绝对产率指标必须按 `source_dataset` 和 `yield_type` 分层报告；跨数据源主分析应优先比较组内 `delta_yield`、方向、排序和推荐 regret。

机器可读定义见 [`configs/core_v0_1_schema.json`](../../configs/core_v0_1_schema.json)。

## 主表的来源映射

| 规范字段 | Ahneman--Doyle | Perera | 规则 |
|---|---|---|---|
| `source_record_id` | 原始 LC/UV 文件名加孔位 | `Reaction_No` | 保持能回到原始层的 ID |
| `reaction_group_id` | 同一 aryl halide 的实验设计组 | electrophile×nucleophile 的实验设计组 | 当前为 HTE 的严格操作分组；后续结构/原子映射验证另行版本化 |
| `substrate_1_*` | aryl halide 名称及 SMILES | `Reactant_1_Name`；SMILES 未报告 | 不补造结构 |
| `substrate_2_*` | `not_reported` | `Reactant_2_Name`；SMILES 未报告 | 未报告不等于无第二底物 |
| `catalyst_system` | 原始预形成 Pd--ligand 体系 | `not_reported` | 不擅自把 Ahneman 体系拆成 catalyst |
| `catalyst` | `not_reported` | `Catalyst_1_Short_Hand` | 保留角色差异 |
| `ligand`, `base`, `additive`, `solvent_1` | 原始/重建的同名列 | 原始/重建的同名列 | Perera 溶剂保留规范化结果，原始标签仍在来源主表 |
| `yield_percent` | `product_scaled` 重建值 | `Product_Yield_PCT_Area_UV` | 数值均在 0--100，但语义不同 |
| `yield_type` | `lc_uv_product_scaled_percent` | `lc_ms_uv_area_percent_reported` | 不可删除或覆写 |
| `measurement_method` | `per_well_LC_UV_internal_standard_corrected` | `UPLC-MS/DAD; UV area percent` | 不可改写为 isolated yield |

## 状态字段的约定

- `success_label = not_assigned`：Core 只发布连续响应；成功阈值属于后续预注册 benchmark 协议。
- `cliff_label = not_assigned`：先发布连续 `delta_yield`，后发布阈值和敏感性分析。
- `quality_grade = B`：来源明确、核心离散条件完整、结果可追溯；但当前记录级数据不具备 proposal 中 A 级所需的重复/不确定度证据。
- `condition_distance = 1.0`：只对当前 strict pair 有效，表示一个离散因素改变；连续条件距离和多因素距离留待扩展版本。
- `condition_registry.component_id` 是 source-scoped ID：跨来源的同名条件默认不建立等价关系，必须有单独 evidence-backed mapping 才能合并。

## 不进入 Core v0.1 的内容

对照实验、ORD、文献优化表、专利和 ELN 均不进入本版本。Ahneman 对照组保持在原有派生文件中，不能在未说明用途的情况下混入主矩阵。
