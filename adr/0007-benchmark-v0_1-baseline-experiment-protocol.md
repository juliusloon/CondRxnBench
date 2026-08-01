# ADR 0007: Benchmark v0.1 的基线实验与结果证据协议

## 状态

Accepted — 2026-07-31

接受依据：Phase 5 Round A 独立审阅通过，见
`reports/execution/phase5_baseline_contract_review_iteration28_2026-07-31.md`。
本 ADR 仅授权 Round B baseline materialization；不授权 benchmark promotion。

## 背景

Phase 4 已生成经独立审计的 split candidate，但尚无预测或分数。不同来源的
absolute yield 不可混合，Perera 不具备完整 reaction structure，而 Task 2–6
需要从同一冻结 prediction 表派生不同的 pair/ranking/recommendation 评价。若在
运行后才决定 feature、family、seed、tuning 或可行性，会污染测试证据。

## 决策

1. 每个 source、split、seed 和 baseline family 单独训练；绝不跨 source 聚合
   absolute yield。固定 seeds、feature definitions、hyperparameter grid 和 run ID。
2. hyperparameter 选择仅使用 train/val；每个 family×source×split 最多选择一个
   val winner，test 只在 winner 冻结后运行一次。所有 prediction 以
   `reaction_id`/`pair_id` 和 partition 保存。
3. 依次提供 source mean、group/condition mean、condition-only Ridge、
   condition-only Random Forest、reaction-only（仅 source-backed structure
   evidence 足够时）、full categorical Ridge、full categorical Random Forest、
   descriptor Random Forest（仅 descriptor evidence 足够时）。不适用的
   family 必须有 reason，而不能填 0 分。
4. 每个正式 source×split 至少运行 constant、shuffled-y 与 shuffled-condition
   三种负对照；负对照和失败运行进入同一结果台账。结构不足不是把 Perera
   伪装为 reaction-only/descriptor 的理由。
5. 只对 feasibility matrix 的 `supported` leaves 汇总；Task 5/6 的非 S1
   恒为 `not_supported`。Task 7 只汇总 OOD strata，不产生 prediction head。
6. 因两个来源都没有完整、source-backed reaction representation，reaction-only
   与 descriptor families 均固定为 `not_supported`。仍保留六个非结构 family
   （source mean、lookup mean、condition Ridge/RF、full categorical Ridge/RF），
   高于 goal 要求的五个独立有效 family 的降级下限；此 fallback 与每源证据矩阵
   一同接受，不允许运行后再决定。

## 后果

- Phase 5 产生的分数仍是 candidate evidence，直到 Phase 6 release gate。
- 新 family、feature 或 hyperparameter budget、test 重跑或 split 改动必须产生
  新版本 contract/run，而不覆写已有 prediction。
