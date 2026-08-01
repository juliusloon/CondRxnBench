# ADR 0001: 统一 schema 保留来源与测量语义

## 状态

Accepted — 2026-07-31

## 背景

Core v0.1 需要让 Ahneman--Doyle 和 Perera HTE 数据可由同一程序读取、生成 pair 与实施后续划分。但前者是经内标校正的逐孔 LC/UV `product_scaled` 百分数，后者是 UPLC-MS/DAD 的 `Product_Yield_PCT_Area_UV`。若将两者都简写为“产率”并直接合并统计，会夸大其可比性；同时部分结构和实验字段在来源中未报告。

## 决策

在统一表中保留 `source_dataset`、`yield_type`、`measurement_method`、`yield_observed`、`zero_yield` 和 `quality_grade`。未报告内容写为 `not_reported`，Perera 原始的显式 `None` 条件水平写为 `NULL_COMPONENT`。绝对产率指标必须按来源与测量类型分层；跨源主分析优先报告同组内的 `delta_yield`、方向、排序和 regret。

## 后果

- 下游实现多了分层与字段检查，但可避免把分析响应错误表述为 isolated yield。
- 不允许基于未验证的结构、产品或实验条件进行填补式结论；字段证据补齐后需以新版本扩展。
- 任何取消或改变这一规则的方案都必须新增 ADR，并说明历史结果的可比性影响。
