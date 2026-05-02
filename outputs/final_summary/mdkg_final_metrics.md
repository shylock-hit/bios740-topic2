# MDKG Final Metrics

Model: SpERT + PubMedBERT  
Split: MDKG dev  
Epoch: 20  
Checkpoint: `outputs/checkpoints/mdkg/mdkg_pubmedbert_e20_bs2/2026-05-02_19:49:36.134736`  
Log dir: `outputs/logs/mdkg_pubmedbert_e20_bs2/2026-05-02_19:49:36.134736`

## Entity Micro

| Precision | Recall | F1 | Support |
| ---: | ---: | ---: | ---: |
| 78.26 | 80.69 | 79.45 | 3961 |

## Relation Micro Without NEC

| Precision | Recall | F1 | Support |
| ---: | ---: | ---: | ---: |
| 56.02 | 58.70 | 57.33 | 1569 |

## Relation Micro With NEC

| Precision | Recall | F1 | Support |
| ---: | ---: | ---: | ---: |
| 48.54 | 50.86 | 49.67 | 1569 |

## Type-Level Notes

- Best NER rows: `disease` F1 86.91, `drug` F1 82.74, `method` F1 81.12, `region` F1 80.21.
- Weakest NER row: `symptom` F1 39.18 over 43 development examples.
- Best strict relation row: `abbreviation_for` F1 74.47.
- Lower strict relation rows: `characteristic_of` F1 32.92 and `associated_with` F1 38.81.
