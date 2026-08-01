# ADR 0002: 先生成严格单因素 pair，再确定 cliff 阈值

## 状态

Accepted — 2026-07-31

## 背景

研究需要识别 reaction-condition cliff。若先从高响应差样本反推 pair 或阈值，会混入多因素变化、反应身份变化和结果驱动的选择偏差，也无法为后续敏感性分析提供完整基线。

## 决策

先在固定 `reaction_group_id` 内枚举所有端点均为观测值、且只改变一个离散条件因素的 pair，并强制 `n_changed_factors = 1`。Core v0.1 发布连续 `delta_yield` 和 `abs_delta_yield`，将 `cliff_label` 设为 `not_assigned`。具体阈值、敏感性区间和 split 内计算规则必须在后续 benchmark 协议中版本化并记录 ADR。

## 后果

- 初始交付不能直接提供 cliff 二分类标签，但其配对宇宙完整、可审计且可支持多种阈值分析。
- pair 表规模较大，任何下游筛选都必须保存筛选规则、阈值和版本。
- 新增连续条件、多因素距离或不同反应身份定义时，需产生明确版本并重新验证 pair 不变量。
