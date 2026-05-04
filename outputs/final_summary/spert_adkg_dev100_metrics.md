# SpERT ADKG Dev100 Metrics

## Run Identity

- Model: `SpERT + PubMedBERT`
- Split: fixed `ADKG dev100`
- Sample file: `outputs/llm_runs/adkg_dev100_sample.json`
- Eval log: `outputs/logs/adkg_dev100_eval.log`
- Eval run log dir: `outputs/logs/adkg_dev100_eval/2026-05-04_11:59:11.331131`

## Entity Micro

| Precision | Recall | F1 | Support |
| ---: | ---: | ---: | ---: |
| 64.19 | 65.71 | 64.94 | 210 |

## Relation Micro Without NEC

| Precision | Recall | F1 | Support |
| ---: | ---: | ---: | ---: |
| 49.12 | 50.00 | 49.56 | 56 |

## Relation Micro With NEC

| Precision | Recall | F1 | Support |
| ---: | ---: | ---: | ---: |
| 43.86 | 44.64 | 44.25 | 56 |

## Type-Level Notes

- Strong NER rows: `disease` F1 76.74 and `gene` F1 62.69.
- Weakest NER row: `other` F1 22.22 on 14 examples.
- Best strict relation row: `abbreviation_for` F1 71.43 with NEC.
- Small-support relation rows vary sharply on this 100-sentence sample, so row-level variance is expected.
