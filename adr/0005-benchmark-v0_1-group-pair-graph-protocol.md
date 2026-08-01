# ADR 0005: Benchmark v0.1 的来源设计分组、严格 pair 与 graph 协议

## 状态

Proposed — 2026-07-31

## 背景

Core v0.2 candidate 保留了两源的实验设计分组和来源感知条件，但两源的反应结构证据不对称：Perera 没有可用于 scaffold/template 推断的底物或产物结构，Ahneman 也没有完整反应/产物证据。现有 Core v0.1 的 116,156 条 pair 是回归基线，不能替代 versioned Benchmark pair universe、graph 或 cliff policy。

## 决策

1. `design_group_id` 与 `strict_reaction_group_id` 都从来源实验设计的 `reaction_group_id` 派生，但其 `group_confidence` 是 `source_design_defined`，绝不称作 structure-verified strict group。
2. `scaffold_group_id` 与 `template_group_id` 在 Benchmark v0.1 均输出为 `not_supported`，附带原因；不因已有部分 Ahneman substrate SMILES 推断跨来源或完整反应 scaffold/template。
3. pair universe 只从同一 source、同一 strict group、两端 observed outcome 的主矩阵记录全量枚举。无自环；端点按 `reaction_id` 字典序定向；严格 pair 只能恰好改变一个 source-specific factor-view：Ahneman 为 `catalyst_system`、`base`、`additive`，Perera 为 `ligand`、`base`、`solvent_1`。Ahneman 中随预形成 `catalyst_system` 共变的 ligand 是 linked metadata，不另算第二 changed factor。Perera 的 current factor view 使用 `condition_component_refs` 解析出的 source raw solvent entity/value，不使用尚未 accepted 的 non-identity mapping；与 v0.1 normalized solvent view 的端点差异必须进入 ledger。
4. 生成顺序固定为 eligible-record manifest → full pair universe（含 deterministic universe hash）→ pair delta → cliff labels。不得按 delta、阈值或模型结果过滤 universe。每个 pair 保存两端原始指针、全部 changed-factor vector、数值 `delta_yield` 和 `abs_delta_yield`、pair/group/build version，以及由本 ADR 冻结的 cliff labels。primary 标签：`invariant` 为 `abs_delta_yield <= 10`，`moderate` 为 `10 < abs_delta_yield < 30`，`strong` 为 `abs_delta_yield >= 30`；敏感性 `strong_20` 和 `strong_40` 分别为 `abs_delta_yield >= 20` 和 `>= 40`，且 `strong_40 ⇒ strong_20`。10、20、30、40 pp 都是必测边界。没有重复实验时不生成显著性或 z-effect 结论。
5. 每个 strict group 输出 node/edge Parquet；group-level JSON 是具固定 schema 的机器可交换图表示。node 集必须等于 group 所有主记录，edge 集须以 `pair_id`、有序 endpoints、group/version、factor 和 canonical undirected key 与 strict pair 表双射。extended/multi-factor graph 在本版显式不实现，不能混入 strict graph。
6. 生成时必须输出与 Core v0.1 的 116,156-pair baseline reconciliation ledger，冻结 source×factor baseline、current count、pair endpoint intersection/difference 和原因码；任何差异必须逐类解释，否则 hard fail。

## 后果

- Benchmark pair/graph 可以忠实表示来源设计中的条件效应，但不支持宣称结构 scaffold/template 泛化。
- 图摘要只用于诊断连通性、度和因素覆盖，不作为删样本依据。
- 修改任一 factor view、group 定义、阈值或输出格式必须新版本 ADR/config，不能覆写已生成 label。
