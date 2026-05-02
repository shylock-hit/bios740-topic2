# BIOS 740 课题2：生物医学命名实体识别与关系抽取

## 作业概述

在本项目中，你将基于生物医学文献构建命名实体识别（NER）和关系抽取（RE）模型。

提供两个标注数据集，均来源于 PubMed 摘要：

- **ADKG** — 阿尔茨海默病知识图谱：8,031 句关于阿尔茨海默病及相关神经退行性疾病的句子。
- **MDKG** — 精神障碍知识图谱：6,678 句涵盖广泛精神障碍（精神分裂症、抑郁症、双相情感障碍、PTSD、强迫症等）的句子。

两个数据集均标注了生物医学实体及实体间的关系。它们共享部分实体和关系类型，但也有各自领域的特定类型。

## 数据集描述

参考链接：[数据集描述（Notion）](https://www.notion.so/Datasets-Description-33b3d297a55f80879988c3ffbe3b03ca)

### ADKG（阿尔茨海默病知识图谱）

- **领域：** 阿尔茨海默病及相关神经退行性疾病
- **来源：** PubMed 摘要
- **句子数：** 8,031（训练集：5,605 | 验证集：1,206 | 测试集：1,220）
- **实体类型（6 种）：** `disease`（疾病）、`gene`（基因）、`drug`（药物）、`method`（方法）、`mutation`（突变）、`other`（其他）
- **关系类型（8 种）：** `abbreviation_for`（缩写）、`associated_with`（关联）、`characteristic_of`（特征）、`help_diagnose`（辅助诊断）、`hyponym_of`（下位词）、`risk_factor_of`（风险因素）、`treatment_for`（治疗）、`treatment_target_for`（治疗靶点）
- **实体总数：** 20,859 | **关系总数：** 5,496

### MDKG（精神障碍知识图谱）

- **领域：** 精神障碍（精神分裂症、抑郁症、双相情感障碍、PTSD、强迫症等）
- **来源：** PubMed 摘要
- **句子数：** 6,678（训练集：4,825 | 验证集：941 | 测试集：912）
- **实体类型（9 种）：** `disease`（疾病）、`method`（方法）、`Health_factors`（健康因素）、`drug`（药物）、`gene`（基因）、`physiology`（生理）、`region`（区域）、`signs`（体征）、`symptom`（症状）
- **关系类型（9 种）：** `abbreviation_for`（缩写）、`associated_with`（关联）、`characteristic_of`（特征）、`help_diagnose`（辅助诊断）、`hyponym_of`（下位词）、`located_in`（定位）、`occurs_in`（发生于）、`risk_factor_of`（风险因素）、`treatment_for`（治疗）
- **实体总数：** 28,660 | **关系总数：** 10,560

### 共享模式

- **共享实体类型：** `disease`、`drug`、`gene`、`method`
- **共享关系类型：** `abbreviation_for`、`associated_with`、`characteristic_of`、`help_diagnose`、`hyponym_of`、`risk_factor_of`、`treatment_for`

---

## 基础组件

### 1. 探索性数据分析（EDA）

分析医学数据集中的实体-关系分布，了解临床概念的密度和多样性（如药物、疾病、不良反应等）。

### 2. 模型训练与基准测试

在两个数据集上训练选定的 RE 模型。

- 使用相关指标（如论文中的 F1）评估两个数据集上的性能。需要按照 SpERT 论文（https://arxiv.org/pdf/1909.07755）中 Table 1 的格式报告指标。同时，检查数据以识别边缘案例（如实体差一个词、关系不完全正确但可接受等）。研究性能差距是否源于重叠实体、长距离依赖。
- 针对特定实体和关系类型评估性能，确定模型擅长或困难的领域。

**RE 模型选项（选择一个）：**

- SpERT：https://github.com/lavis-nlp/spert
- PURE：https://github.com/princeton-nlp/PURE

---

## 扩展组件

### A. 生成式 vs. 判别式关系抽取

- **SFT 基准测试：** 将判别式框架（SpERT/PURE）与大语言模型（LLM）的**监督微调（SFT）**进行对比。可以考虑比较不同规模、不同模型家族、使用/不使用 LoRA、不同提示设计的 SFT 模型性能。
- **范式分析：** 评估在结构化提示-补全对上微调的生成式模型是否具有更好的能力。考虑到生成式模型的特性，可以考虑将原始评估指标修改为宽松版本。可使用 strict/relaxed matching 等关键词搜索。

### B. 迁移学习与领域适应

- **跨领域提升：** 开发合理策略利用辅助数据，如通用领域数据集（如 **SemEval-2018 Task 7/10**），以提升低资源临床任务的性能。也可以直接使用提供的数据集之一作为辅助数据。

### C. 数据标注的智能体工作流

- 使用闭源 LLM（如 **Gemini**、**GPT-4**）通过 API 设计智能体工作流来执行大规模数据标注。
- 需要评估设计的流水线与基线的性能。同时，需要考虑使用不同模型和不同工作流设计。考虑到生成式模型的特性，也可以考虑将原始评估指标修改为宽松版本。可使用 strict/relaxed matching 等关键词搜索。

---

## 参考

- SpERT 论文：https://arxiv.org/pdf/1909.07755
- PURE：https://github.com/princeton-nlp/PURE
- 数据集描述：https://www.notion.so/Datasets-Description-33b3d297a55f80879988c3ffbe3b03ca
