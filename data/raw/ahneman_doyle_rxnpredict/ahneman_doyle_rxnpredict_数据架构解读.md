# Ahneman-Doyle Buchwald-Hartwig HTE 数据集架构解读

## 数据集概述

本数据集来源于 Ahneman 和 Doyle 等人关于 Buchwald-Hartwig 偶联反应的高通量实验（HTE）研究。数据集包含原始实验数据，用于构建反应产率预测模型。

**上游仓库**: https://github.com/doylelab/rxnpredict  
**提交哈希**: `57e15fdb7f7483c6bf3a601df69f6ac9e5af6965`  
**许可证**: MIT 许可证（见 `LICENSE.txt`）

## 目录结构

```
ahneman_doyle_rxnpredict/
├── SOURCE.md                    # 数据来源说明
├── LICENSE.txt                  # MIT 许可证
├── layout/                      # 实验板布局文件
│   ├── Table_S1.csv            # 板布局表1（配体-添加剂组合）
│   └── Table_S2.csv            # 板布局表2（碱-芳基卤化物组合）
├── smiles/                      # 化合物SMILES结构文件
│   ├── additive-list.csv       # 添加剂列表及SMILES
│   ├── aryl_halide-list.csv    # 芳基卤化物列表及SMILES
│   ├── base-list.csv           # 碱列表及SMILES
│   └── ligand-list.csv         # 配体列表及SMILES
└── yield_data/                  # 原始产率数据（12个文件）
    ├── plate1.1.csv            # 板1批次1
    ├── plate1.2.csv            # 板1批次2
    ├── plate1.3.csv            # 板1批次3
    ├── plate1.4.csv            # 板1批次4
    ├── plate2.1.csv            # 板2批次1
    ├── ...                     # 其他批次
    └── plate3.4.csv            # 板3批次4
```

## 数据架构详解

### 1. 实验板布局 (`layout/`)

#### Table_S1.csv - 配体-添加剂组合
- **行（Row）**: 32种配体-添加剂组合
- **列**: 
  - `Ligand`: 配体类型（XPhos, t-BuXPhos, t-BuBrettPhos, AdBrettPhos）
  - `Additive (Plate 1/2/3)`: 不同板中使用的添加剂编号（1-23）

#### Table_S2.csv - 碱-芳基卤化物组合
- **列（Column）**: 48种碱-芳基卤化物组合
- **内容**:
  - `Base`: 碱类型（P2Et, BTMG, MTBD）
  - `Aryl Halide`: 芳基卤化物编号（1-15）

### 2. 化合物结构文件 (`smiles/`)

每个文件包含化合物的编号、名称和SMILES结构字符串：

| 文件 | 内容 | 列名 |
|------|------|------|
| `additive-list.csv` | 23种添加剂 | component, name, Additive_SMILES |
| `aryl_halide-list.csv` | 15种芳基卤化物 | component, name, Aryl_halide_SMILES |
| `base-list.csv` | 3种碱 | component, name, CAS, Base_SMILES |
| `ligand-list.csv` | 4种配体 | component, name, CAS, Ligand_SMILES |

### 3. 原始产率数据 (`yield_data/`)

共12个CSV文件，对应3块实验板，每块板4个批次。

#### 文件命名规则
- `plate{板号}.{批次号}.csv`
- 板号: 1, 2, 3
- 批次号: 1, 2, 3, 4

#### 数据列结构

| 列名 | 说明 |
|------|------|
| `product` | 产物峰面积 |
| `additive` | 添加剂峰面积 |
| `internal_standard` | 内标峰面积 |
| `corr_factor` | 校正因子 |
| `product_scaled` | 校正后产物产率 |
| `additive_scaled` | 校正后添加剂产率 |
| `Sample Name` | 样品名称 |
| `Data File` | 原始数据文件名 |
| `Location` | 板中位置（如1:A, 2:B等） |
| `UV210_*` | 各化合物的UV检测数据（保留时间和峰面积） |

#### UV检测数据列
每个化合物在UV210检测器下有两列：
- `UV210_{化合物名} Rt(min)`: 保留时间（分钟）
- `UV210_{化合物名} AreaAbs`: 峰面积绝对值

## 实验设计原理

### 因子设计
该数据集采用多因子实验设计：
1. **配体类型**: 4种（XPhos, t-BuXPhos, t-BuBrettPhos, AdBrettPhos）
2. **添加剂**: 23种不同的添加剂
3. **碱**: 3种（P2Et, BTMG, MTBD）
4. **芳基卤化物**: 15种不同的芳基卤化物

### 实验规模
- 每块板: 384孔（16行×24列）
- 总实验数: 约4,608个反应条件（3板×384孔×4批次）
- 实际数据点取决于有效实验数量

## 数据使用注意事项

1. **原始数据**: 这些是原始的LC/UV分析数据，需要预处理才能用于机器学习
2. **缺失值**: 某些化合物可能未检测到（峰面积为0）
3. **校正因子**: `corr_factor`用于校正不同批次间的系统误差
4. **内标法**: 使用内标进行定量校正

## 数据重建说明

本数据集是重建 Ahneman-Doyle HTE 数据集的最小输入子集。以下派生数据产品被有意排除：
- `data_table.csv`
- `Response/Scaled_dataset.csv`
- `Response/Unscaled_dataset.csv`
- 描述符和模型输出

这些需要通过处理原始数据生成。

## 参考文献

1. Ahneman, D. T., Estrada, J. G., Lin, S., Dreher, S. D., & Doyle, A. G. (2018). Predicting reaction performance in C–N cross-coupling using machine learning. *Science*, 360(6385), 186-190.
2. Doyle, A. G., et al. rxnpredict GitHub repository. https://github.com/doylelab/rxnpredict