# Biomedical Knowledge Graph Extraction from PubMed Abstracts

## Abstract

We study biomedical named entity recognition (NER) and relation extraction (RE) on two PubMed-derived datasets: ADKG, centered on Alzheimer's disease and related neurodegenerative disorders, and MDKG, centered on mental disorders. We implement a reproducible SpERT + PubMedBERT pipeline and evaluate it on both full splits and matched 100-sentence `dev100` subsets aligned with downstream LLM experiments. On ADKG dev/test, the baseline reaches entity F1 65.30/67.92 and relation F1 (with NEC) 40.27/42.06; on MDKG dev/test, it reaches 79.45/77.68 and 49.67/49.74. On the matched `dev100` subsets, SpERT reaches 64.94/44.25 on ADKG and 83.25/45.27 on MDKG. As an extension, we compare one-shot and 3-step agentic LLM annotation workflows under both strict and relaxed evaluation. On ADKG dev100, DeepSeek one-shot is both more accurate and faster than workflow. On MDKG dev100, Gemini under an MDKG-specific prompt yields the strongest relaxed relation F1 among the tested GPT/Gemini settings, while workflow does not deliver a stable quality gain over one-shot and incurs a large latency penalty.

## 1. Data and EDA

The assignment provides two JSON datasets with train/dev/test splits. ADKG contains 8,031 sentences and MDKG contains 6,678 sentences. ADKG has 6 entity types and 8 relation types; MDKG has 9 entity types and 9 relation types. MDKG is denser than ADKG, with 4.30 entities and 1.57 relations per training sentence versus 2.61 and 0.70 in ADKG. MDKG also exhibits longer relation spans on average (65.92 vs. 53.95 characters), indicating harder long-range dependencies.

The main EDA conclusion is that density alone does not determine difficulty. ADKG is less dense but noisier: it contains the ambiguous `other` entity class and a relation distribution heavily dominated by `abbreviation_for`. MDKG is denser, but its label semantics and entity boundaries appear cleaner.

## 2. Model and Setup

We use SpERT with `microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract` as the encoder. The main configuration uses 20 epochs, train batch size 2, eval batch size 4, max span size 10, and relation filter threshold 0.4. A one-epoch smoke test was used to verify the training pipeline before full runs. Full experiments were run on a CUDA GPU.

For evaluation, we report entity micro F1 and relation F1 with named entity classification (NEC). This requires exact span, type, and directed endpoint matches, making the relation score stricter and more clinically meaningful.

## 3. Main Results

### 3.1 SpERT Baseline

| Run | Entity P | Entity R | Entity F1 | Relation P (NEC) | Relation R (NEC) | Relation F1 (NEC) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ADKG dev | 65.41 | 65.20 | 65.30 | 41.91 | 38.75 | 40.27 |
| ADKG test | 70.20 | 65.78 | 67.92 | 44.94 | 39.53 | 42.06 |
| ADKG dev100 | 64.19 | 65.71 | 64.94 | 43.86 | 44.64 | 44.25 |
| MDKG dev | 78.26 | 80.69 | 79.45 | 48.54 | 50.86 | 49.67 |
| MDKG test | 77.02 | 78.36 | 77.68 | 49.08 | 50.42 | 49.74 |
| MDKG dev100 | 83.46 | 83.04 | 83.25 | 41.36 | 50.00 | 45.27 |

These results show that MDKG is consistently easier for the discriminative baseline despite its higher density. The most plausible explanation is better label consistency rather than lower structural complexity.

### 3.2 Type-Level Summary

Type-level analysis reveals stable patterns across both datasets. In ADKG, `disease` is the strongest entity type (F1 78.88), while rare `mutation` and semantically broad `other` are weakest. In MDKG, `disease`, `drug`, `method`, and `region` all exceed 80 F1. For relations, `abbreviation_for` is the easiest type in both datasets, while broad labels such as `associated_with` and `characteristic_of` remain hardest. ADKG `associated_with` is especially poor (F1 9.55), whereas MDKG `associated_with` is much stronger (F1 38.81), reinforcing the importance of schema clarity.

### 3.3 Comparison with Prior SpERT Benchmarks

Compared with SpERT results reported on SciERC, CoNLL04, and ADE, our ADKG test result (67.92 entity F1, 42.06 relation F1) is close to the SciERC range, while MDKG test performance (77.68, 49.74) is stronger. This places the biomedical assignment in a realistic difficulty range for joint entity-relation extraction and suggests that the MDKG annotation scheme provides cleaner supervision than ADKG.

## 4. Error Analysis

The main failure modes are boundary errors, endpoint mismatch cascades, and broad-relation ambiguity. Many predicted entities are semantically correct but slightly over- or under-specified, such as predicting `Hcy` instead of `increased plasma Hcy`. These span errors propagate into strict relation scoring because relation correctness depends on exact endpoints. The difficulty is especially visible for `associated_with`, where semantically plausible relations often fail exact matching.

This motivates the relaxed evaluation protocol for the LLM extension: same sentence, same type, and overlapping spans for entities; same sentence, same relation type, and overlapping head/tail spans for relations.

## 5. Extension: Agentic LLM Annotation

We compare two modes:

1. **One-shot**: a single LLM call extracts all entities and relations jointly.
2. **Workflow**: three sequential steps (`extract_entities`, `extract_relations`, `review_and_fix`).

The extension records both quality metrics and system metrics such as latency, parse success, and failure count.

### 5.1 ADKG dev100 DeepSeek

| Method | Strict Entity F1 | Strict Relation F1 | Relaxed Entity F1 | Relaxed Relation F1 | Avg Latency (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| one-shot | 0.4559 | 0.0000 | 0.4958 | 0.3750 | 15.08 |
| workflow | 0.4198 | 0.0000 | 0.4694 | 0.2730 | 29.07 |

On ADKG, one-shot is both more accurate and faster. Under this prompt and dataset setting, the workflow does not recover enough quality to justify its latency overhead.

### 5.2 MDKG dev100 GPT vs Gemini

| Provider | Mode | Strict Entity F1 | Strict Relation F1 | Relaxed Entity F1 | Relaxed Relation F1 | Avg Latency (s) | Success |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT | one-shot | 0.5915 | 0.0000 | 0.6521 | 0.3919 | 9.03 | 100/100 |
| GPT | workflow | 0.5782 | 0.0000 | 0.6328 | 0.3948 | 21.09 | 99/100 |
| Gemini | one-shot | 0.5308 | 0.0000 | 0.6183 | 0.5000 | 10.84 | 100/100 |
| Gemini | workflow | 0.5376 | 0.0000 | 0.6317 | 0.4837 | 28.33 | 100/100 |

Three conclusions are most important. First, strict relation F1 remains zero for all GPT/Gemini settings, confirming that exact endpoint matching is extremely brittle for generative outputs. Second, within this MDKG-specific prompt setting, Gemini is stronger than GPT on relaxed relation F1. Third, workflow does not provide a stable quality gain: GPT workflow is only marginally better than GPT one-shot on relaxed relation F1 (+0.0029), while Gemini workflow is slightly worse than Gemini one-shot (-0.0163). In both providers, workflow is much slower (2.34x for GPT and 2.61x for Gemini).

## 6. Limitations

This study still has important limits. The LLM experiments are sample-based (`dev100`) rather than full-dataset evaluations. Only one discriminative baseline, SpERT + PubMedBERT, was benchmarked. Exact relation scoring is harsh for generative outputs and likely understates semantic utility. The workflow implementation also does not yet track API cost or support async batching and retry logic.

## 7. Conclusion

This project delivers a complete biomedical NER/RE pipeline for ADKG and MDKG and satisfies the core assignment requirements: EDA, SpERT training, strict evaluation, type-level analysis, and error analysis. The discriminative baseline is consistently stronger on MDKG than ADKG, showing that denser data can still be easier when the schema is cleaner. The extension component shows that workflow decomposition is not automatically beneficial for LLM annotation. On ADKG, DeepSeek one-shot is better than workflow; on MDKG, Gemini is the strongest of the tested GPT/Gemini settings under dataset-specific prompting, but workflow still fails to justify its latency cost. Overall, the results suggest that prompt/schema alignment matters more than decomposition depth, and that one-shot currently offers the better efficiency-quality tradeoff for this task.
