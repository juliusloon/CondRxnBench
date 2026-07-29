# Predicting reaction performance in C-N cross-coupling using machine learning

## Metadata

- 中文题目：利用机器学习预测 C-N 交叉耦合中的反应性能
- Authors: Derek T. Ahneman, Jesus G. Estrada, Shishi Lin, Spencer D. Dreher, Abigail G. Doyle
- Venue: *Science* (2018)
- Source type: local HTML
- Source path: `Buchwald-Hartwig-HTE.html`
- Reader status: draft reader rebuilt from the currently extractable HTML blocks

## Page Index

- p.1 Front matter and article body

## Terminology Ledger

| Canonical term | 中文 | Note |
|---|---|---|
| Buchwald-Hartwig amination / cross-coupling | Buchwald-Hartwig 胺化 / 交叉偶联 | 文中核心反应体系 |
| high-throughput experimentation (HTE) | 高通量实验 | 产率数据来源 |
| descriptor | 描述符 | 包括原子、分子、振动描述符 |
| random forest | 随机森林 | 最优预测模型 |
| linear regression | 线性回归 | 主要基线 |
| root mean squared error (RMSE) | 均方根误差 | 预测误差指标 |
| out-of-sample prediction | 样本外预测 | 泛化能力测试 |
| activity cliff | 活动悬崖 | 外推受限的重要原因 |
| oxidative addition | 氧化加成 | 机理假设核心步骤 |
| isoxazole | 异噁唑 | 关键抑制性添加剂骨架 |
| lowest unoccupied molecular orbital (LUMO) | 最低未占分子轨道 | 重要电子描述符 |

## Bilingual Reader

<a id="S001"></a>
**Source:** p.1 S001

**Function:** problem setup / dataset design

**Original:** We selected the Pd-catalyzed Buchwald-Hartwig reaction as our test reaction for model development due to its broad value in pharmaceutical synthesis (Fig. 1A) (25). Nevertheless, the application of this reaction to complex drug-like molecules remains challenging (26). One limitation is the poor performance of substrates possessing 5-membered heterocycles that contain heteroatom-heteroatom bonds, such as isoxazoles. These heterocycles have drug-like characteristics but are underrepresented in successful drug candidates (27). Thus, we sought to use ML to predict the performance of the Buchwald-Hartwig reaction in the presence of isoxazoles. Rather than evaluate the coupling of a collection of substrates directly bearing the heterocycle functionality, we pursued a Glorius fragment additive screening approach (28) wherein the impact of isoxazole fragment additives was evaluated on the amination of different aryl and heteroaryl halides. This method cannot always account for the full impact of a structural motif embedded within a substrate. However, the Glorius approach allowed us to test 345 diverse structural interactions between isoxazoles and aryl and heteroaryl halides. This large array would not be possible using whole molecules due to the necessity to synthesize and isolate all possible products for quantification in this study. We conducted the coupling reactions using the ultra-high-throughput setup recently developed in the Merck Research Laboratories for nanomole-scale experimentation in 1536-well plates (16). Use of the Mosquito robot enabled simultaneous evaluation of more reaction dimensions than previously examined using classical statistical analysis. Three 1536-well plates consisting of a full matrix of 15 aryl and heteroaryl halides, 4 Buchwald ligands, 3 bases, and 23 isoxazole additives gave a total of 4608 reactions (including controls). The yields of these reactions were used as the model output. Approximately 30% of the reactions failed to deliver any product, with the remainder quite evenly spread over the range of yields (fig. S7).

**中文:** 由于 Pd 催化 Buchwald-Hartwig 反应在药物合成中具有广泛价值，作者将其选作模型开发的测试反应（图 1A）（25）。然而，该反应用于复杂类药物分子时仍然很有挑战性（26）。一个限制在于，带有杂原子-杂原子键的五元杂环底物，例如异噁唑，往往表现较差。这类杂环具备药物样特征，但在成功药物候选中代表性不足（27）。因此，作者希望用机器学习预测异噁唑存在时 Buchwald-Hartwig 反应的表现。作者没有直接研究带杂环底物本体的偶联，而是采用 Glorius 片段添加剂筛选策略（28），评估异噁唑片段添加剂对不同芳基和杂芳基卤化物胺化反应的影响。虽然这种方法不能完全等价于真实底物中嵌入该结构基元的全部效应，但它允许系统测试异噁唑与芳基/杂芳基卤化物之间的 345 种结构相互作用。若使用整分子体系，由于需要合成并分离所有产物以定量，本研究无法实现如此大规模的阵列。作者借助 Merck Research Laboratories 开发的超高通量纳摩尔级 1536 孔板平台开展偶联反应（16），并使用 Mosquito 机器人同时评估了比传统统计分析更高维度的反应空间。三块 1536 孔板覆盖 15 个芳基/杂芳基卤化物、4 个 Buchwald 配体、3 个碱和 23 个异噁唑添加剂，共得到 4608 个反应（含对照）。模型输出为这些反应的产率，其中约 30% 的反应完全不出产物，其余产率分布相对均匀（图 S7）。

<a id="S002"></a>
**Source:** p.1 S002

**Function:** abstract / contribution claim

**Original:** Machine learning methods are becoming integral to scientific inquiry in numerous disciplines. Here we demonstrate that machine learning can be used to predict the performance of a synthetic reaction in multidimensional chemical space using data obtained via high-throughput experimentation. We created scripts to compute and extract atomic, molecular, and vibrational descriptors for the components of a palladium-catalyzed Buchwald-Hartwig cross-coupling of aryl halides with 4-methylaniline in the presence of various potentially inhibitory additives. Using these descriptors as inputs and reaction yield as output, we show that a random forest algorithm provides significantly improved predictive performance over linear regression analysis. The random forest model was also successfully applied to sparse training sets and out-of-sample prediction, suggesting its value in facilitating adoption of synthetic methodology.

**中文:** 机器学习方法正逐渐成为多个学科科学研究的一部分。作者在这里展示，利用高通量实验获得的数据，可以在多维化学空间中预测合成反应的表现。作者编写脚本，自动计算并提取钯催化 Buchwald-Hartwig 交叉偶联体系中各组分的原子、分子和振动描述符；该体系是芳基卤化物与 4-甲基苯胺在多种可能具有抑制作用的添加剂存在下发生偶联。以这些描述符为输入、反应产率为输出时，随机森林算法相比线性回归表现出显著更好的预测性能。随机森林模型还成功应用于稀疏训练集和样本外预测，说明它有望帮助合成方法学更高效地被采用。

<a id="S003"></a>
**Source:** p.1 S003

**Function:** background / gap

**Original:** Machine learning is the study and construction of computer algorithms that can learn from data (1). The ability of these algorithms to detect meaningful patterns has led to their adoption across a wide range of applications in science and technology, from autonomous vehicle control to recommender systems (2). Machine learning has also been successfully applied in the biomedical sciences to enhance the virtual screening of libraries of drug-like molecules for biological function (3-5). However, its application to the chemical sciences, and synthetic organic chemistry in particular, has been limited (6, 7). Prior efforts have primarily focused on using machine learning to assist with synthetic planning via retrosynthetic pathways or to predict the product(s) of chemical reactions given a set of reactants and conditions (8-11). Applications of machine learning to predict the performance of a given reaction, however, are rare. Studies in the area of heterogeneous catalysis have used machine learning to predict reaction performance when only a single component is varied (12, 13). Two recent studies have advanced the field by evaluating predictions in multidimensional chemical space, although these perform a binary classification of reaction success (14, 15). Using regression-based machine learning to predict reaction yields in multidimensional chemical space could provide chemists with a powerful tool to navigate the adoption of synthetic methodology.

**中文:** 机器学习是研究和构建能够从数据中学习的计算机算法的学科（1）。这类算法能够识别有意义模式，因此已被广泛应用于科学与技术的许多领域，从自动驾驶控制到推荐系统（2）。机器学习也已成功用于生物医学科学，以提升对类药分子文库生物活性的虚拟筛选能力（3-5）。然而，它在化学科学中的应用，尤其是在合成有机化学中，仍较为有限（6, 7）。此前的工作主要集中在用机器学习辅助逆合成规划，或在给定反应物和条件时预测反应产物（8-11）。相比之下，直接预测某一反应“表现”的研究很少。异相催化领域虽有工作在只改变单一组分时预测反应表现（12, 13），近来也有研究开始在多维化学空间中做预测，但大多仍是对反应成败进行二元分类（14, 15）。如果能用回归型机器学习在多维化学空间中预测反应产率，就可能为化学家提供一个强有力的工具，帮助他们更快采用新的合成方法。

<a id="S004"></a>
**Source:** p.1 S004

**Function:** motivation / feasibility

**Original:** There are many challenges in applying machine learning (ML) to reaction performance that have previously hindered its use in the field of chemical synthesis. Implementation of these algorithms has historically been challenging for nonspecialists. Further, the amount of data required to obtain statistically meaningful results grows exponentially with the number of dimensions under study, a problem known as the "curse of dimensionality" (1). Given the multidimensionality of chemical structure and reactivity, it has been difficult to generate enough data or access sufficiently complete and consistent data from databases to warrant implementation of these algorithms (14). Fortunately, over the last decade, high-throughput experimentation (HTE) has emerged as a powerful tool in industry and academia for reaction optimization and discovery (16, 17). We sought to evaluate whether ML could be applied to the scale of data available to modern HTE and enable yield prediction in multidimensional chemical space.

**中文:** 将机器学习用于反应表现预测存在许多挑战，这些挑战此前限制了它在化学合成领域的应用。首先，这类算法对非专业人士来说一向较难实施。其次，想得到有统计意义的结果，所需数据量会随研究维度数指数增长，这就是所谓的“维度诅咒”（1）。考虑到化学结构与反应性本身高度多维，过去无论是自行生成足够数据，还是从数据库中获得足够完整且一致的数据，都很困难（14）。不过在过去十年中，高通量实验（HTE）已成为工业界和学术界进行反应优化与发现的强大工具（16, 17）。因此作者要检验的是，现代 HTE 产出的数据规模，是否已经足以支撑机器学习在多维化学空间中做产率预测。

<a id="S005"></a>
**Source:** p.1 S005

**Function:** baseline framing

**Original:** Linear regression is the traditional tool for reaction prediction and analysis in both industry and academia (18). In this approach, the user assumes a linear relationship between reaction input (e.g., catalyst descriptors) and output (e.g., product selectivity), and hand-selects input variables based on specific mechanistic hypotheses (19, 20). A strength of linear regression is its interpretability: a good fit between reagent descriptors and output supports mechanistic inferences, such as in the seminal Hammett linear free-energy relationship (21).

**中文:** 线性回归一直是工业界和学术界进行反应预测与分析的传统工具（18）。在这种方法里，研究者通常假设反应输入（例如催化剂描述符）与输出（例如产物选择性）之间是线性关系，并且依据具体机理假设手动挑选输入变量（19, 20）。线性回归的优势在于可解释性强：当试剂描述符与输出之间拟合良好时，就能支持机理推断，例如经典的 Hammett 线性自由能关系（21）。

<a id="S006"></a>
**Source:** p.1 S006

**Function:** baseline limitation

**Original:** The models obtained from linear regression analysis have also been used for prediction. Recently, Sigman and co-workers have applied multivariate linear and polynomial regression analysis to optimize reaction selectivity by predicting catalyst, ligand, and substrate effects (22-24). Predicting yield tends to be more difficult; whereas product selectivity is determined by a small number of elementary steps, many on- and off-cycle events can dramatically alter reaction yield.

**中文:** 线性回归得到的模型也可以用于预测。近来 Sigman 团队已使用多元线性和多项式回归来预测催化剂、配体和底物效应，从而优化反应选择性（22-24）。但产率预测通常更难，因为产物选择性往往由少数几个基元步骤决定，而反应产率却会受到许多主循环内外事件的显著影响。

<a id="S007"></a>
**Source:** p.1 S007

**Function:** explicit contribution

**Original:** Machine learning approaches accept numerous input descriptors without recourse to a mechanistic hypothesis and evaluate functions with greater flexibility to match patterns in data. As such, we postulated that ML might outperform regression analysis for yield prediction and circumvent the challenge of selecting mechanistically relevant descriptors for large and multidimensional datasets. Here, we report that a random forest ML model trained on multidimensional chemical data can be used to predict the performance of a Buchwald-Hartwig amination reaction conducted in the presence of potentially inhibitory additives and to infer underlying reactivity. We have taken steps to automate reaction parameterization and modeling with the aim of making this tool accessible to the synthetic community.

**中文:** 机器学习方法可以接收大量输入描述符，而无需先预设明确的机理假说，并且能够用更灵活的函数形式去匹配数据中的模式。因此作者提出，机器学习或许能在产率预测上优于传统回归，并绕开在大型多维数据集中手工挑选“机理相关描述符”的难题。本文报告表明：基于多维化学数据训练的随机森林模型，可以预测在潜在抑制性添加剂存在下进行的 Buchwald-Hartwig 胺化反应表现，并且还能帮助推断其底层反应性。作者还尽量将反应参数化和建模流程自动化，希望让合成化学研究者也能实际使用这一工具。

<a id="S008"></a>
**Source:** p.1 S008

**Function:** descriptor engineering

**Original:** Next we turned to the selection of appropriate descriptors. In linear regression analysis, this is typically done by hand according to a mechanistic hypothesis, with principal component analysis sometimes being used to reduce the parameter set to an uncorrelated and statistically tractable number (29). For the ML model, we sought a set of descriptors that adequately characterizes the differences among the reactions without recourse to a specific hypothesis. For reasons of internal consistency and descriptor availability, calculated properties were used. To avoid prohibitively time-consuming analysis and logging of computational data, software was written to submit molecular, atomic, and vibrational property calculations to Spartan and subsequently extract these features from the resulting text files for accessibility to a general user (Fig. 1B). The program only requires input of reagent structures in the Spartan GUI and specification of the reaction components in a Python script; as such it is applicable to any reaction type. The program then generates the data table that can be used for modeling. In total, 120 descriptors were extracted by the software to characterize each reaction (Supplementary Section III).

**中文:** 接下来作者讨论如何选择合适的描述符。在线性回归分析中，这一步通常根据机理假设手工完成，有时也会用主成分分析把参数集压缩到彼此不相关、且统计上可处理的规模（29）。但在机器学习模型中，作者希望找到一组无需依赖特定机理假说、却能充分表征反应差异的描述符。出于内部一致性和描述符可得性的考虑，作者采用了计算得到的性质。为了避免手工分析和记录计算数据过于耗时，作者编写软件，把分子、原子和振动性质计算提交给 Spartan，并从输出文本文件中自动提取特征，供一般用户使用（图 1B）。这个程序只需要在 Spartan 图形界面中输入试剂结构，并在 Python 脚本中声明反应组分，因此原则上适用于任意反应类型。最终软件共提取了 120 个描述符来表征每个反应（补充材料第 III 节）。

<a id="S009"></a>
**Source:** p.1 S009

**Function:** main result / model comparison

**Original:** With these data in hand, the predictive accuracy of linear regression and an array of ML methods were evaluated using 70% of the data as a training set to predict the remaining 30% (test set) (Fig. 2A). For the linear regression models, dimension reduction by removing correlated descriptors as well as various regularization methods (e.g., LASSO, Ridge, and Elastic Net) were evaluated, but none generated good predictive performance. Turning to supervised ML models, k-nearest neighbors (kNN), support vector machines (SVM), and Bayes generalized linear model (GLM) provided no improvement over a linear regression model. A single-layer neural network was also evaluated, but gave no improvement. By contrast, the random forest algorithm was found to provide significant improvements over linear regression analysis and other ML methods in terms of predictive accuracy. The test set root mean squared error (RMSE) for the random forest model is 7.8% with an R² value of 0.96. A significant proportion of this variation is likely attributable to experimental and analytical error. Random forest algorithms operate by randomly sampling the data and constructing decision trees, which are then aggregated to generate an overall prediction (30). By combining a large number of low-precision models, the algorithm can deliver high predictive accuracy without succumbing to overfitting.

**中文:** 在得到这些数据后，作者用 70% 数据作为训练集，预测剩余 30% 数据作为测试集，比较线性回归和多种机器学习方法的预测精度（图 2A）。对于线性回归，作者尝试了去除相关描述符的降维，以及 LASSO、Ridge、Elastic Net 等多种正则化方法，但都没有得到好的预测表现。随后考察的监督式机器学习模型，包括 k 最近邻（kNN）、支持向量机（SVM）和贝叶斯广义线性模型（GLM），也都没有优于线性回归。单层神经网络同样没有带来提升。相比之下，随机森林在预测精度上显著优于线性回归和其他机器学习方法。其测试集均方根误差（RMSE）为 7.8%，R² 为 0.96。作者同时指出，这部分误差中相当一部分可能来自实验和分析本身的误差。随机森林通过对数据随机采样、构建决策树并对多个树模型进行集成来给出总体预测（30）；通过组合大量低精度模型，它能在避免过拟合的同时获得较高预测精度。

<a id="S010"></a>
**Source:** p.1 S010

**Function:** generalization under sparsity

**Original:** Nevertheless, ML tends to experience predictive limitations when significantly different reaction conditions are used in the test set. This problem is exacerbated by the presence of activity cliffs, which are areas in reaction space where modest changes in chemical structure can lead to dramatic changes in reaction outcome (31). The tendency of ML algorithms to overfit and the presence of activity cliffs conspire to necessitate the collection of local reaction data (see fig. S30 for prediction of ArI/ArCl reaction outcomes from ArBr training data). One method for maximizing the extrapolative ability of a model is to use training data spread across the chemical space of interest. The ability to perform accurate prediction under sparsity effectively increases the reaction space that can be explored using the same number of experiments. For the random forest model, we were surprised to discover that enhanced predictive power over other methods could be achieved using a significantly smaller subset of the training data (Fig. 2B). Specifically, the random forest algorithm trained on only 5% of the reaction data outperformed any other regression technique using 70% of the same reaction data. Because 5% of the dataset is only 230 experiments, these results indicate that ML can offer improvements in prediction on a scale routinely pursued in the course of reaction optimization and scope elucidation.

**中文:** 不过，当测试集包含与训练集差异明显的反应条件时，机器学习仍会面临预测限制。这个问题会被“活动悬崖”进一步放大，即在反应空间中，化学结构的轻微变化可能导致反应结果剧烈变化（31）。机器学习算法容易过拟合，再叠加活动悬崖的存在，就意味着往往需要收集局部反应数据才能做稳健预测（例如图 S30 中用 ArBr 训练数据去预测 ArI/ArCl 结果的例子）。提高模型外推能力的一种方法，是让训练数据尽量覆盖目标化学空间。若模型能在训练数据稀疏时依然准确预测，就等于在相同实验数量下扩大可探索的反应空间。作者惊讶地发现，对于随机森林，只用显著更小的训练子集，也能获得比其他方法更强的预测能力（图 2B）。具体来说，仅用全部反应数据的 5% 进行训练，随机森林就已经优于那些使用同一数据集 70% 数据训练的其他回归方法。由于 5% 的数据只相当于 230 个实验，这说明机器学习在常规反应优化和范围考察的实验规模上就可能带来实际预测收益。

<a id="S011"></a>
**Source:** p.1 S011

**Function:** out-of-sample prediction

**Original:** The ability of a random forest model to predict outcomes for reactions containing additives not included in its training data was next explored. If effective out-of-sample prediction were possible, ML could predict the impact of a new isoxazole or aryl halide structure on the outcome of a Buchwald-Hartwig amination and identify the combination of base and ligand that delivers highest yield. To this end, we evaluated whether the results of 15 additives could be used to predict the outcomes with 8 distinct additives (Fig. 3A). On average, the out-of-sample RMSE was 11.3% with an R2 value of 0.91 (Fig. 3B). Surprisingly, none of the additives experienced significant systematic deviations from what was predicted by the model. The high predictive ability of the model suggests that the effects of these substituents on reaction outcome were captured well by the descriptors. However, since additive consumption was not included in the output, the algorithm is likely to experience predictive limitations when applied to substrates with embedded isoxazoles.

**中文:** 接着作者考察了随机森林模型对于“训练中未出现过的添加剂”所对应反应结果的预测能力。如果样本外预测足够有效，那么机器学习就能预测新的异噁唑或芳基卤化物结构会如何影响 Buchwald-Hartwig 胺化反应，并帮助识别给出最高产率的碱和配体组合。为此，作者测试了能否用 15 种添加剂的结果去预测另外 8 种不同添加剂的结果（图 3A）。平均来看，样本外预测的 RMSE 为 11.3%，R² 为 0.91（图 3B）。令人意外的是，没有任何一种添加剂表现出明显的系统性偏差。这说明模型使用的描述符较好地捕捉到了这些取代基对反应结果的影响。不过由于模型输出中没有显式包含添加剂消耗这一因素，当它被应用到真正嵌入异噁唑骨架的底物时，仍可能存在预测局限。

<a id="S012"></a>
**Source:** p.1 S012

**Function:** descriptor interpretation / mechanism hypothesis

**Original:** Having obtained a predictive model, we sought to determine whether it could be used to guide mechanistic analysis. Unlike a linear regression model, the random forest model is challenging to interpret directly. We therefore evaluated the relative importance of descriptors used to construct the model. One such measure of a descriptor's importance is the percent increase in the model's mean squared error (MSE) when values for that descriptor are randomly shuffled and the model is retrained (1). When applied to the cross-coupling reaction, we found that four of the five most important descriptors in predicting reaction outcomes were the additive's *C3 NMR shift, LUMO energy, and *O1 and *C5 electrostatic charge (Fig. 4A). Notably, these features are not sufficient to obtain a predictive linear model (see fig. S24). The descriptors taken together suggest that the propensity of the additive to act as an electrophile influences reaction outcomes (32-34). As such, we hypothesized that competitive oxidative addition of the isoxazole could be a source of deleterious side reactivity. Although oxidative addition of Pd to isoxazoles is not known (35), such an elementary step has been reported previously for other transition metals (36).

**中文:** 在得到预测模型之后，作者进一步问：这个模型能不能反过来指导机理分析？与线性回归不同，随机森林很难直接解释，因此作者转而评估构建模型时各描述符的相对重要性。一个常用指标是：将某个描述符的值随机打乱并重新训练模型后，模型均方误差（MSE）增加了多少（1）。将这一分析用于交叉偶联反应后，作者发现，对预测结果最重要的五个描述符中，有四个都来自添加剂本身，分别是 *C3 NMR chemical shift、LUMO energy 以及 *O1 和 *C5 的静电荷（图 4A）。值得注意的是，这几个特征本身不足以构造出一个有预测力的线性模型（见图 S24）。但将它们综合起来看，说明“添加剂作为亲电体的倾向”可能在影响反应结果（32-34）。因此作者提出一个机理假设：异噁唑可能发生竞争性的氧化加成，从而导致不利的副反应。虽然 Pd 对异噁唑发生氧化加成此前并无直接报道（35），但类似基元步骤在其他过渡金属体系中已有先例（36）。

<a id="S013"></a>
**Source:** p.1 S013

**Function:** mechanistic validation and conclusion

**Original:** To evaluate this proposal, we conducted a series of experiments with isoxazoles Ia and Ib, which possess the smallest and largest predicted *C3 NMR chemical shifts of the additives in the test set, respectively (Fig. 4B). As shown in Fig. 4C, spectrum 1, isoxazole Ia underwent no reaction with tetrakis(triphenylphosphine) Pd(0) in benzene at room temperature. On the other hand, with isoxazole Ib, a new species was observed within one hour (Fig. 4C, spectrum 2). High-resolution mass spectrometry (HRMS) and spectroscopic (31P, 13C, and 1H NMR) analysis provides strong evidence that isoxazole Ib underwent oxidative addition at the N-O bond (Supplementary Section VI). Going further, we investigated how isoxazoles Ia and Ib performed in competition with an aryl halide. When Ia was mixed with aryl bromide 1c, only formation of the aryl bromide oxidative adduct (2c) was observed (Fig. 4C, spectrum 3). However, when isoxazole Ib was subjected to the same competition experiment, the oxidative adducts of both the aryl bromide 1c and isoxazole Ib were observed in roughly equal amounts (Fig. 4C, spectrum 4). These data are consistent with the hypothesis that electrophilic isoxazole additives can undergo N-O oxidative addition to Pd(0) as a deleterious side reaction, causing diminished yields of the desired Buchwald-Hartwig aminations. While such a hypothesis could have been obtained by alternate means, this study highlights how measuring the influence of a large collection of descriptors for their predictive ability in a ML algorithm can be used to generate hypotheses for further mechanistic inquiry. Although one should be hesitant to perform direct causal inference, this approach could be particularly enabling for larger and higher dimensional datasets wherein it would be challenging or impossible to intuit a unified mechanism.

**中文:** 为了检验这个假设，作者选择了一对异噁唑添加剂 Ia 和 Ib，它们分别对应测试集中最小和最大的预测 *C3 NMR chemical shift（图 4B）。图 4C 的光谱 1 显示，异噁唑 Ia 在室温苯溶液中与 tetrakis(triphenylphosphine)Pd(0) 不发生反应；而异噁唑 Ib 则在一小时内就出现了新的物种（图 4C，光谱 2）。高分辨质谱（HRMS）以及 31P、13C、1H NMR 分析提供了强有力证据，支持异噁唑 Ib 在 N-O 键处发生氧化加成（补充材料第 VI 节）。作者进一步考察它们与芳基卤化物竞争时的表现：当 Ia 与芳基溴化物 1c 混合时，只观察到芳基溴化物的氧化加成物 2c（图 4C，光谱 3）；而当 Ib 进入同样的竞争实验时，芳基溴化物 1c 和异噁唑 Ib 的氧化加成物都以大致相当的量出现（图 4C，光谱 4）。这些结果与作者的假设一致：具有更强亲电性的异噁唑添加剂可能对 Pd(0) 发生 N-O 氧化加成这一有害副反应，从而降低目标 Buchwald-Hartwig 胺化的产率。虽然这个机理假设也可能通过其他途径提出，但本研究的重要意义在于，它展示了如何利用机器学习模型中“大量描述符的预测贡献”来反推值得进一步实验检验的机理假说。作者也提醒，这种做法不应被简单地视作直接因果推断，但对于更大、更高维、难以凭直觉统一解释的数据集，它尤其有价值。

<a id="S014"></a>
**Source:** p.1 S014

**Function:** closing significance

**Original:** Vast resources and time are currently expended on the development of synthetic methods and their application to complex molecule synthesis, often in a largely ad hoc manner. Here we show that simple atomic, molecular, and vibrational descriptors that can be automatically extracted from the text files of Spartan calculations can be used as input for a random forest model to predict yields of multidimensional chemical data. Coupled with advances in high-throughput experimentation and analysis with whole-molecule systems, we expect that this approach will prove of broad utility in facilitating the adoption of synthetic methods by enabling prediction of a new substrate's performance under given conditions or prediction of the optimal conditions for a new substrate.

**中文:** 目前，合成方法开发及其在复杂分子合成中的应用仍然消耗大量资源和时间，而且很多时候仍带有较强的经验性。作者在这里展示，只要使用能够从 Spartan 计算文本中自动提取的简单原子、分子和振动描述符，就可以把它们输入随机森林模型，用来预测多维化学数据中的反应产率。随着高通量实验以及整分子体系分析能力的持续进步，作者预计这种方法将具有广泛实用性，既可以预测新底物在给定条件下的表现，也可以帮助寻找新底物的最佳反应条件，从而加速合成方法学的实际采用。

## 阅读提示

- 这篇文章最值得记住的不是“随机森林赢了线性回归”，而是它把 `HTE -> 自动特征工程 -> 监督学习 -> 机理反推 -> 实验验证` 连成了闭环。
- 真正的化学贡献点在 `S012-S013`：模型不是停在黑箱预测，而是把描述符重要性转化成了关于异噁唑 N-O 氧化加成的可实验检验假说。
- 如果我们是从 benchmark 角度读它，最关键的设定在 `S001`、`S008-S011`：4608 个反应、120 个计算描述符、5% 稀疏训练也能给出强预测、样本外预测 RMSE 11.3%。
- 如果我们是从建模角度复现它，要特别留意 `S011` 和 `S012` 提到的外推边界：activity cliffs、local data requirement，以及“重要描述符不等于线性可建模变量”。∑
