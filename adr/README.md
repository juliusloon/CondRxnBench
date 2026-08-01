# 架构决策记录（ADR）

ADR 记录会长期影响数据语义、可复现性、接口或评测结论的决定。日常进展记入 `PROGRESS.md`，过程证据记入 `notes/`；当一个决定成为约束时新增 ADR。

## 索引

| ADR | 状态 | 摘要 |
| --- | --- | --- |
| [0001](0001-preserve-source-aware-measurement-semantics.md) | Accepted | 统一 schema 不抹平来源与测量语义 |
| [0002](0002-enumerate-strict-pairs-before-cliff-threshold.md) | Accepted | 先生成 strict pair，再确定 cliff 阈值 |
| [0003](0003-core-v0_2-storage-and-runtime-compatibility.md) | Proposed | Core v0.2 的候选 runtime、Parquet 和兼容性约束 |
| [0004](0004-core-v0_2-evidence-preserving-standardization-contract.md) | Accepted for candidate build | Core v0.2 的结构、mapping、单位和缺失语义合约 |
| [0005](0005-benchmark-v0_1-group-pair-graph-protocol.md) | Accepted for candidate build | Benchmark v0.1 的来源设计分组、严格 pair 与 graph 协议 |
| [0006](0006-benchmark-v0_1-task-split-metrics-protocol.md) | Accepted for split materialization | Benchmark v0.1 的任务、split 与指标协议 |
| [0007](0007-benchmark-v0_1-baseline-experiment-protocol.md) | Accepted for baseline materialization | Benchmark v0.1 的基线实验与结果证据协议 |

## 新 ADR 模板

文件名采用递增编号和短横线标题，例如 `0003-versioned-split-protocol.md`。

```md
# ADR 0003: 简短决策标题

## 状态
Proposed | Accepted | Superseded | Deprecated

## 背景
问题、约束与证据。

## 决策
明确选择及适用范围。

## 后果
收益、代价、限制、迁移/验证要求。
```
