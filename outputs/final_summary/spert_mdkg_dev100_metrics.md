# SpERT MDKG Dev100 Metrics

## Run Identity

- Model: `SpERT + PubMedBERT`
- Split: fixed `MDKG dev100`
- Sample file: `outputs/llm_runs/mdkg_dev100_sample.json`
- Eval log: `outputs/logs/mdkg_dev100_eval.log`
- Eval run log dir: `outputs/logs/mdkg_dev100_eval/2026-05-04_12:01:02.930123`

## Entity Micro

| Precision | Recall | F1 | Support |
| ---: | ---: | ---: | ---: |
| 83.46 | 83.04 | 83.25 | 401 |

## Relation Micro Without NEC

| Precision | Recall | F1 | Support |
| ---: | ---: | ---: | ---: |
| 47.53 | 57.46 | 52.03 | 134 |

## Relation Micro With NEC

| Precision | Recall | F1 | Support |
| ---: | ---: | ---: | ---: |
| 41.36 | 50.00 | 45.27 | 134 |

## Type-Level Notes

- Strong NER rows: `disease` F1 90.91 and `method` F1 86.41.
- Best strict relation row: `abbreviation_for` F1 83.33 with NEC.
- `associated_with`, `treatment_for`, and `help_diagnose` remain usable on the sample, while `characteristic_of` drops to zero on only 4 examples.
