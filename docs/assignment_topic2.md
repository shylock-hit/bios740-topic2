# BIOS 740 Topic 2: Biomedical NER and Relation Extraction

## Assignment Overview

In this project you will build Named Entity Recognition (NER) and Relation Extraction (RE) models on biomedical literature.

You are given two annotated datasets, each derived from PubMed abstracts:

- **ADKG** — Alzheimer's Disease Knowledge Graph: 8,031 sentences about Alzheimer's disease and related neurodegenerative disorders.
- **MDKG** — Mental Disorder Knowledge Graph: 6,678 sentences covering a broad range of mental disorders (schizophrenia, depression, bipolar disorder, PTSD, OCD, etc.).

Both datasets are annotated with biomedical entities and the relations between them. They share some entity and relation types but also have domain-specific ones.

## Datasets Description

Reference: [Datasets Description (Notion)](https://www.notion.so/Datasets-Description-33b3d297a55f80879988c3ffbe3b03ca)

### ADKG (Alzheimer's Disease Knowledge Graph)

- **Domain:** Alzheimer's disease and related neurodegenerative disorders
- **Source:** PubMed abstracts
- **Sentences:** 8,031 (Train: 5,605 | Dev: 1,206 | Test: 1,220)
- **Entity Types (6):** `disease`, `gene`, `drug`, `method`, `mutation`, `other`
- **Relation Types (8):** `abbreviation_for`, `associated_with`, `characteristic_of`, `help_diagnose`, `hyponym_of`, `risk_factor_of`, `treatment_for`, `treatment_target_for`
- **Total Entities:** 20,859 | **Total Relations:** 5,496

### MDKG (Mental Disorder Knowledge Graph)

- **Domain:** Mental disorders (schizophrenia, depression, bipolar disorder, PTSD, OCD, etc.)
- **Source:** PubMed abstracts
- **Sentences:** 6,678 (Train: 4,825 | Dev: 941 | Test: 912)
- **Entity Types (9):** `disease`, `method`, `Health_factors`, `drug`, `gene`, `physiology`, `region`, `signs`, `symptom`
- **Relation Types (9):** `abbreviation_for`, `associated_with`, `characteristic_of`, `help_diagnose`, `hyponym_of`, `located_in`, `occurs_in`, `risk_factor_of`, `treatment_for`
- **Total Entities:** 28,660 | **Total Relations:** 10,560

### Shared Schema

- **Shared Entity Types:** `disease`, `drug`, `gene`, `method`
- **Shared Relation Types:** `abbreviation_for`, `associated_with`, `characteristic_of`, `help_diagnose`, `hyponym_of`, `risk_factor_of`, `treatment_for`

---

## Basic Components

### 1. Exploratory Data Analysis (EDA)

Analyze entity-relation distributions within medical datasets to understand the density and variety of clinical concepts (e.g., *Drugs, Diseases, Adverse Effects*).

### 2. Model Training & Benchmarking

Train the selected RE model on both datasets.

- Evaluate performance on both datasets using relevant metrics (F1 as in the paper). You need to report the metrics as Table 1 in the SpERT paper (https://arxiv.org/pdf/1909.07755). Also, examine the data to identify some edge cases (e.g., entity miss by one word, relation is not perfect but OK). Investigate whether performance gaps arise from overlapping entities, long-range dependencies.
- Evaluate performance across specific entity and relation types to identify where the model excels or struggles.

**RE Model Options (pick one):**

- SpERT: https://github.com/lavis-nlp/spert
- PURE: https://github.com/princeton-nlp/PURE

---

## Extension Components

### A. Generative vs. Discriminative Relation Extraction

- **SFT Benchmarking:** Compare the discriminative frameworks (SpERT/PURE) against **Supervised Fine-Tuning (SFT)** of Large Language Models (LLMs). You might consider comparing the performance of SFT model with different size, within different model family, with/without LoRA, with different prompt designs.
- **Paradigm Analysis:** Assess whether generative models, fine-tuned on structured prompt-completion pairs, offer better capabilities. Considering the nature of generative models, you may also consider modifying the original evaluation metric to a relaxed version. You may search with keywords like strict/relaxed matching.

### B. Transfer Learning & Domain Adaptation

- **Cross-Domain Improvement:** Develop plausible strategies to leverage auxiliary data, such as general-domain datasets (e.g., **SemEval-2018 Task 7/10**), to improve performance on low-resource clinical tasks. Or you can just use one of the provided datasets as auxiliary data.

### C. Agentic Workflow for Data Annotation

- Design an agentic workflow using closed-source LLMs (e.g., **Gemini**, **GPT-4**) via API to perform large-scale data annotation.
- You need to evaluate the performance of your designed pipeline with the baseline. Also, you need to consider the use of different models and different workflow designs. Considering the nature of generative models, you may also consider modifying the original evaluation metric to a relaxed version. You may search with keywords like strict/relaxed matching.

---

## Reference

- SpERT Paper: https://arxiv.org/pdf/1909.07755
- PURE: https://github.com/princeton-nlp/PURE
- Datasets Description: https://www.notion.so/Datasets-Description-33b3d297a55f80879988c3ffbe3b03ca
