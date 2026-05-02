# BIOS 740 Final Project Topic 2 Report

## Abstract

This project builds a reproducible pipeline for biomedical named entity recognition (NER) and
relation extraction (RE) on two PubMed-derived datasets: ADKG for Alzheimer's disease knowledge
graph extraction and MDKG for mental disorder knowledge graph extraction. The code package provides
data validation, exploratory data analysis (EDA), conversion to SpERT-style input, strict
micro-averaged evaluation, type-level analysis, and scripts for SpERT training and cross-domain
transfer experiments.

## Dataset

The assignment provides two JSON files with `train`, `dev`, and `test` splits. Each sample is one
sentence with character-offset entity annotations and directed relation annotations between entity
mentions. The final experiments use the course Google Drive mirror JSON files because they exactly
match the assignment split statistics.

| Dataset | Domain | Abstracts | Sentences | Train Sent. | Dev Sent. | Test Sent. | Entity Types | Relation Types |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ADKG | Alzheimer's disease and neurodegenerative disorders | 758 | 8,031 | 5,605 | 1,206 | 1,220 | 6 | 8 |
| MDKG | Mental disorders | 946 | 6,678 | 4,825 | 941 | 912 | 9 | 9 |

The public Zenodo sources were also downloaded as a fallback. They contain the same abstract-level
annotation source in brat `.txt/.ann` format, but a local `pysbd` reconstruction produced 8,162 ADKG
sentences and 6,852 MDKG sentences. The final pipeline therefore uses the course mirror JSON files
under `data/raw/`.

ADKG contains `disease`, `gene`, `drug`, `method`, `mutation`, and `other` entities. MDKG contains
`disease`, `method`, `Health_factors`, `drug`, `gene`, `physiology`, `region`, `signs`, and
`symptom` entities. Shared relation types include `abbreviation_for`, `associated_with`,
`hyponym_of`, `treatment_for`, `risk_factor_of`, `help_diagnose`, and `characteristic_of`.

## EDA

The EDA script computes split-level sentence/entity/relation counts, entity type distributions,
relation type distributions, relation type-pair distributions, and character-distance summaries for
relation endpoints.

Run:

```bash
python scripts/eda.py --input data/raw/ADKG.json --name ADKG
python scripts/eda.py --input data/raw/MDKG.json --name MDKG
```

Expected outputs:

- `outputs/adkg_eda_summary.json`
- `outputs/mdkg_eda_summary.json`

Important analysis points to include after running on the real data:

- Entity density differs by domain: MDKG has more entities and relations per sentence than ADKG.
- Relation imbalance is expected, especially for broad labels such as `associated_with`.
- Long-range relations can be identified by high character distance between head and tail starts.
- Overlapping or near-overlapping entities should be inspected because strict NER scoring penalizes
  one-word boundary errors.

Report figure assets were generated with:

```bash
python scripts/generate_report_artifacts.py
```

They are stored in `outputs/report_artifacts/` and are derived from the official JSON files in
`data/raw/`. Use these source notes in the report captions:

| Figure | Files | Caption note |
| --- | --- | --- |
| Label distributions | `adkg_entity_counts.png`, `mdkg_entity_counts.png`, `adkg_relation_counts.png`, `mdkg_relation_counts.png` | Entity and relation type frequencies computed from official ADKG/MDKG JSON files. |
| Sentence structure | `adkg_sentence_lengths.png`, `mdkg_sentence_lengths.png`, `adkg_entities_per_sentence.png`, `mdkg_entities_per_sentence.png` | Sentence length and entity density distributions computed before model training. |
| Relation structure | `adkg_relation_pair_heatmap.png`, `mdkg_relation_pair_heatmap.png`, `adkg_relation_distance_bins.png`, `mdkg_relation_distance_bins.png` | Entity-type pair co-occurrence and relation endpoint distance summaries. |

## Model

The primary discriminative model is SpERT. SpERT jointly detects entity spans and classifies
relations over candidate entity pairs, making it a good fit for sentence-level biomedical RE. The
recommended encoder is PubMedBERT:

```text
microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract
```

The conversion script writes one JSON file per split plus a `types.json` file:

```bash
python scripts/convert_to_spert.py --input data/raw/ADKG.json --name ADKG
python scripts/convert_to_spert.py --input data/raw/MDKG.json --name MDKG
python scripts/make_spert_configs.py
```

Training command template:

```bash
git clone https://github.com/lavis-nlp/spert.git external/spert
bash scripts/train_spert.sh outputs/spert_configs/adkg.conf
bash scripts/train_spert.sh outputs/spert_configs/mdkg.conf
```

## GPU Resource Estimate

SpERT with PubMedBERT-base should be trained on a CUDA GPU when possible. A smoke test can run on
8-12 GB VRAM, but full experiments are more comfortable on 16-24 GB VRAM. With the current configs
(`epochs=20`, `train_batch_size=2`, `max_span_size=10`), expected runtime is roughly 2-5 hours per
dataset on a T4 16 GB GPU, 1-3 hours on an L4/A10-class GPU, and under 1-1.5 hours on an A100.

Disk needs are modest for the data (<100 MB after conversion), but checkpoints and model caches can
use 5-10 GB for the four planned experiments. If VRAM is insufficient, reduce `train_batch_size` to
1 first, then reduce `max_span_size` from 10 to 8. A detailed estimate is provided in
`docs/gpu_resource_estimate.md`.

## Evaluation

The project uses strict span and relation matching. An entity prediction is correct only when
sentence ID, start offset, end offset, and entity type all match. A relation prediction is correct
only when the relation type and both directed endpoints match. This mirrors the strict evaluation
style used in SpERT-style reports.

Table 1 should be filled after model training:

| Dataset | Entity P | Entity R | Entity F1 | Relation P | Relation R | Relation F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ADKG | 65.41 | 65.20 | 65.30 | 41.91 | 38.75 | 40.27 |
| MDKG | 78.26 | 80.69 | 79.45 | 48.54 | 50.86 | 49.67 |
| ADKG -> MDKG transfer | TBD | TBD | TBD | TBD | TBD | TBD |
| MDKG -> ADKG transfer | TBD | TBD | TBD | TBD | TBD | TBD |

ADKG final dev result uses entity `micro` and relation `With named entity classification (NEC)
micro` from the 20-epoch SpERT + PubMedBERT run. The checkpoint was saved at
`outputs/checkpoints/adkg/adkg_pubmedbert_e20_bs2/2026-05-02_18:50:44.982426`.

MDKG final dev result uses the same strict metrics from the 20-epoch SpERT + PubMedBERT run. The
checkpoint was saved at
`outputs/checkpoints/mdkg/mdkg_pubmedbert_e20_bs2/2026-05-02_19:49:36.134736`.

Evaluation command:

```bash
python scripts/evaluate_predictions.py --gold data/raw/ADKG.json --pred outputs/predictions/adkg_test_predictions.json --output outputs/adkg_eval.json
```

## Type-Level Analysis

The evaluation code reports per-type entity and relation metrics. The expected failure modes are:

- Rare entity types such as ADKG `mutation` may have lower recall due to fewer training examples.
- Broad classes such as ADKG `other` and MDKG `method` may produce boundary ambiguity.
- Relation types with flexible semantics, especially `associated_with`, may have lower precision.
- Directional relations such as `treatment_for`, `risk_factor_of`, and `located_in` should be
  inspected for head-tail reversal errors.

Observed ADKG patterns: `disease` NER is strongest (F1 78.88), rare `mutation` is weakest (F1
37.50 over 16 dev examples), `abbreviation_for` is the strongest strict relation (F1 69.69), and
`associated_with` is difficult (F1 9.55). Observed MDKG patterns: `disease`, `drug`, `method`, and
`region` all exceed 80 F1 for NER, `symptom` is weakest (F1 39.18 over 43 dev examples),
`abbreviation_for` is again strong (F1 74.47), and `characteristic_of` is the lowest strict
relation among common MDKG relations (F1 32.92).

## Edge Cases

The error analysis helper extracts boundary mismatches where a predicted entity overlaps a gold
entity with the same type but has different offsets. Examples to inspect:

- Missing one modifier: predicting `dementia` instead of `Focal-Onset Dementias`.
- Over-including context: predicting `patients with depression` instead of `depression`.
- Abbreviation pairs: `PTSD` and `post-traumatic stress disorder` may both appear in one sentence.
- Long-range relation: correct entities far apart in the sentence but relation missed.
- Semantically plausible but unannotated relation: model predicts a relation that is medically
  reasonable but absent from gold labels.

## Extension: Transfer Learning and Domain Adaptation

The extension component uses one dataset as auxiliary data for the other:

1. Build a shared-schema subset of ADKG and MDKG using common entity and relation types.
2. Train on the source shared-schema dataset.
3. Continue fine-tuning the source checkpoint on the target shared-schema train split.
4. Compare target development F1 against single-domain training and discuss domain shift.

This design tests whether shared biomedical entity/relation structure transfers across Alzheimer's
and mental disorder literature. It also exposes domain-specific label mismatch: ADKG has `mutation`
and `other`, while MDKG has `Health_factors`, `physiology`, `region`, `signs`, and `symptom`.
The implemented shared schema contains entities `disease`, `drug`, `gene`, and `method`, and
relations `abbreviation_for`, `associated_with`, `characteristic_of`, `help_diagnose`,
`hyponym_of`, `risk_factor_of`, and `treatment_for`.

## Reproducibility

Install:

```bash
conda create -n bios740-topic2 python=3.10 -y
conda activate bios740-topic2
python -m pip install -e ".[dev]"
conda install -c conda-forge gdown -y
```

Run local checks:

```bash
python -m pytest -v
```

Run full preprocessing after placing data under `data/raw`:

```bash
bash scripts/run_all.sh
python scripts/estimate_resources.py
```

`scripts/convert_brat_sources.py` is retained only as a fallback for reconstructing JSON from the
public Zenodo brat archives when the course mirror files are unavailable.

## Limitations

The submitted code provides the full preprocessing, evaluation, and experiment scaffolding. The
single-domain ADKG and MDKG runs are complete. The remaining experimental gap is the selected
transfer-learning extension, which should be completed if time permits or described clearly as a
planned extension rather than a finished result.
