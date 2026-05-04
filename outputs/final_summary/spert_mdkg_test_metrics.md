# SpERT MDKG Test Metrics

## Run Identity

- Model: `SpERT + PubMedBERT`
- Split: `MDKG test`
- Checkpoint family: `outputs/checkpoints/mdkg/mdkg_pubmedbert_e20_bs2/`
- Eval log: `outputs/logs/mdkg_test_eval.log`
- Eval run log dir: `outputs/logs/mdkg_test_eval/2026-05-04_11:35:09.989893`

## Entity Micro

| Precision | Recall | F1 | Support |
| ---: | ---: | ---: | ---: |
| 77.02 | 78.36 | 77.68 | 3960 |

## Relation Micro Without NEC

| Precision | Recall | F1 | Support |
| ---: | ---: | ---: | ---: |
| 55.96 | 57.48 | 56.71 | 1430 |

## Relation Micro With NEC

| Precision | Recall | F1 | Support |
| ---: | ---: | ---: | ---: |
| 49.08 | 50.42 | 49.74 | 1430 |

## Type-Level Notes

- Strongest NER row: `disease` F1 87.35.
- Other strong NER rows: `method` F1 77.17, `Health_factors` F1 74.61, `region` F1 74.39, `drug` F1 74.22.
- Best strict relation row: `abbreviation_for` F1 77.17 with NEC.
- More difficult strict relation rows: `characteristic_of` F1 35.47 and `associated_with` F1 36.63.
