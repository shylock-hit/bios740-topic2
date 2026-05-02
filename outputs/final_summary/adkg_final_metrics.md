# ADKG Final Metrics

Model: SpERT + PubMedBERT  
Split: ADKG dev  
Epoch: 20  
Checkpoint: `outputs/checkpoints/adkg/adkg_pubmedbert_e20_bs2/2026-05-02_18:50:44.982426`  
Log dir: `outputs/logs/adkg_pubmedbert_e20_bs2/2026-05-02_18:50:44.982426`

## Entity Micro

| Precision | Recall | F1 | Support |
| ---: | ---: | ---: | ---: |
| 65.41 | 65.20 | 65.30 | 3060 |

## Relation Micro Without NEC

| Precision | Recall | F1 | Support |
| ---: | ---: | ---: | ---: |
| 48.55 | 44.88 | 46.64 | 782 |

## Relation Micro With NEC

| Precision | Recall | F1 | Support |
| ---: | ---: | ---: | ---: |
| 41.91 | 38.75 | 40.27 | 782 |

