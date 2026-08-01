# ADR 0006: Benchmark v0.1 的任务、split 与指标协议

## 状态

Accepted — 2026-07-31

接受依据：Phase 4 Round A 独立合同审阅通过，见
`reports/execution/phase4_contract_review_iteration23_2026-07-31.md`。本 ADR
仅授权实现与验证正式 split manifests；不授权 benchmark promotion、模型训练、
预测或结果声明。

## 背景

严格 pair/graph candidate 已通过来源、identity 与 confounding 审计，但尚未有 test manifest。不同来源的 yield type 不可合并，Perera 缺少结构，Ahneman 只具有部分 component/substrate 结构。因此任务、split、label 与指标必须在任何测试结果前冻结。

## 决策

1. 固定 seed `20260731`。每个 source 单独划分和报告；不得混合绝对 yield。S0 是随机历史对照，S1 是 group 内条件插值，S2 是完整 source-design reaction group OOD，S3 是 source-specific condition component OOD，S4 是见过 component 的未见 condition combination OOD，S5 是 group+condition double OOD。
2. 所有 split 按 record manifest 生成；pair manifest 只能收录两个端点同属 train、val 或 test 的 strict pair。跨 partition pair 必须写入 exclusion ledger，绝不用于任何 pair 指标或训练。测试 label 从不用于 held-out 选择、seed、特征或 hyperparameter。
3. Task 1（source-stratified absolute yield）、Task 2（strict-pair delta）、Task 3（direction）、Task 4（30 pp cliff）支持于有 observed outcome 的记录/pair；Task 5 ranking 与 Task 6 recommendation 仅支持于 group 内测试候选集合；Task 7 是 S0–S5 的 OOD 分层框架而不是预测 head。success label 不在 v0.1 定义，任何 success-classification 指标均 `not_supported`。
4. 任务不得因结构缺失伪造 reaction-only/scaffold/template OOD：S2 是来源设计 group OOD，不宣称 structure OOD；结构依赖模型 family 的可行性另在 Phase 5 声明。
5. 绝对指标为 MAE/RMSE/R2；pair 为 delta MAE/RMSE、Pearson/Spearman、direction accuracy/macro-F1、cliff AUPRC/AUROC/F1；ranking 为 Spearman/NDCG/top-k；recommendation 为 top-k success against group optimum 和 regret。每项指标固定处理空集合、常数、ties、missing predictions 与 class imbalance 的行为。
6. 每个 source×Task×S0–S5 leaf 必须在 materialization 前写入 status、reason、evidence、最小 eligible count 和 nonempty disposition。S0–S5 使用由 seed、source 和 canonical selection key 定义的 hash 排序；val/test 不交叠。S3 的 `NULL_COMPONENT` 是可 held-out 的显式 entity；S4/S5 tuple 为 source-specific factor role 的 canonical ordered JSON。S5 同时要求 group 和 tuple 均不在 train，达不到则 `not_supported`。
7. direction 是互斥三分类：`delta<-10` / `abs(delta)<=10` / `delta>10`。推荐中的 top-k 是“含 observed group optimum”，不是未定义的 success label。record/pair manifest、cross-partition exclusion ledger、config/input hash、freeze version 和 test-first 规则均由 machine contract 固定。

## 后果

- Benchmark manifests 保持可复现，但个别 source×task×split 可被诚实标为 limited/not_supported。
- 阈值、split unit、held-out selection 或 metric behavior 的改变必须增加版本，不覆写 test manifest。
