# CondRxnBench-Core v0.1 条件词典规则

本版本不手写“通用条件本体”，也不为没有结构证据的条件伪造 SMILES、InChIKey、类别或跨来源等价 ID。实际可用词典由构建脚本输出为 `data/processed/core_v0_1/condition_registry.csv`。

每条词典记录包含 `role`、`raw_value`、`normalized_name`、`source_dataset`、稳定 `component_id`、`normalization_status` 和证据来源。

规则如下：

1. 默认只做恒等规范化：重建表中已确认的名称直接保留。
2. Perera 的 `None` 必须映射为 `NULL_COMPONENT`；它是实验水平。
3. Perera 的载体溶剂规范化只接受已审计映射：`MeOH/H2O_V2 9:1 → MeOH`、`THF_V2 → THF`。原始标签仍保存在来源主表。
4. `not_reported` 不写入条件词典，因为它不是条件实体。
5. 后续添加同义词、结构、InChIKey 或跨来源等价关系时，必须记录证据、原始名称、变更版本和人工复核状态。
6. `component_id` 必须包含来源作用域：同名条件在不同 `source_dataset` 中默认是不同实体，直到独立、证据支持的跨来源 mapping 明确建立等价关系。
