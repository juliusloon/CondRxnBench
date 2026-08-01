# ADR 0003: Core v0.2 的 schema、Parquet 与 Python 运行时兼容性

## 状态

Proposed — 2026-07-31

## 背景

Core v0.1 的 CSV 具有可审计的字段语义和 hash，但当前默认 Python 3.13.2 环境没有 RDKit、pyarrow 或 scikit-learn，无法验证结构标准化、Parquet 保真或基线。Core v0.2 需要引入标准化字段和正式 Parquet，同时不得覆盖原始证据、丢失 v0.1 哨兵，或把两套不同响应语义混为一个可比较绝对产率。

## 提议决策

在独立审阅通过前，采用下列候选兼容性合约：

1. 使用独立的 Python 3.11 环境；将实际解析得到的精确包版本、平台和 Python build 写入版本化环境文件与执行报告。Python 3.13 不作为 v0.2 发布环境。
2. `reaction_records.parquet`、`condition_pairs.parquet`、condition registry 与 CSV inspection mirror 同时发布。Parquet 是正式机器交付；CSV 只用于人工检查。
3. Core v0.2 仅以新增的、版本化字段表示标准化结果：保留 `*_raw`、来源指针、现有 `not_reported` 与 `NULL_COMPONENT` 哨兵，不就地覆写 v0.1 字段或 `data/raw/`。
4. 每次 Parquet 交付必须验证与 CSV mirror 的行数、主键、布尔值、数值、`not_reported`/`NULL_COMPONENT`/缺失值语义以及 source-aware measurement 字段完全等价；差异为 release blocker。
5. schema/storage 变更与 Core v0.1 的关系必须是可读、可迁移而非静默替换；任何破坏性语义变更以新版本目录和 manifest 发布。

## 后果

- v0.2 需要额外环境和 round-trip 测试，但获得可复跑的 Parquet 与化学特征路径。
- 该 ADR 尚未接受，不能据此生成 v0.2 正式数据、标签或模型结论。
- 精确依赖解析和环境创建需要获得安装授权后执行，并由独立 reviewer 从干净环境重跑。
