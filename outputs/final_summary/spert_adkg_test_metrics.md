# SpERT ADKG Test Metrics

## Run Identity

- Model: `SpERT + PubMedBERT`
- Split: `ADKG test`
- Checkpoint family: `outputs/checkpoints/adkg/adkg_pubmedbert_e20_bs2/`
- Eval log: `outputs/logs/adkg_test_eval.log`
- Eval run log dir: `outputs/logs/adkg_test_eval/2026-05-04_11:34:46.004573`

## Entity Micro

| Precision | Recall | F1 | Support |
| ---: | ---: | ---: | ---: |
| 70.20 | 65.78 | 67.92 | 3115 |

## Relation Micro Without NEC

| Precision | Recall | F1 | Support |
| ---: | ---: | ---: | ---: |
| 49.26 | 43.32 | 46.10 | 764 |

## Relation Micro With NEC

| Precision | Recall | F1 | Support |
| ---: | ---: | ---: | ---: |
| 44.94 | 39.53 | 42.06 | 764 |

## Type-Level Notes

- Strongest NER row: `mutation` F1 80.90, but support is only 44.
- Strong common NER row: `disease` F1 80.20.
- Best strict relation row: `abbreviation_for` F1 67.98 with NEC.
- Weak strict relation rows: `treatment_target_for` F1 13.33 and `associated_with` F1 13.43.
