# 2026-07-31 — Core v0.1 交接笔记

## 目标

把两套已审计 HTE 主矩阵与严格单因素 condition pair 汇总为可复现的 Core v0.1，并建立项目恢复与决策追踪入口。

## 已核对的证据

- Ahneman--Doyle 主矩阵：4,140 条；独立对照：468 条；strict pair：55,676。
- Perera 主矩阵：5,760 条；strict pair：60,480。
- Core 目标：9,900 条记录、116,156 个 strict pair；详情见 `metadata/README.md` 与 `data/processed/core_v0_1/manifest.json`。

## 恢复命令

```bash
python3 scripts/build_core_v0_1.py
python3 tests/verify_core_v0_1.py
```

如需从原始层完整恢复，请按 `STATUS.md` 中的顺序运行两个数据源的构建与 QC，再构建 Core。

## 本次验证

已运行 `python3 tests/verify_core_v0_1.py`，输出为 `Core v0.1 verification passed: 9,900 records; 116,156 strict pairs.`。

## 未解决项

- 需在 Python 3.10--3.12 环境中补齐 RDKit、scikit-learn、pyarrow，才可执行化学基线与 Parquet 验证。
- benchmark split、success 和 cliff 阈值仍未版本化；不可将 `not_assigned` 当作负类或成功标签。

## 下一步

执行独立验证，审核拟提交文件，并将 benchmark 协议作为下一阶段的首要工作。
