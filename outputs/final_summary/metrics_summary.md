# SpERT Metrics Summary

## Main Results

| Run | Entity P | Entity R | Entity F1 | Relation P (NEC) | Relation R (NEC) | Relation F1 (NEC) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ADKG | 65.41 | 65.20 | 65.30 | 41.91 | 38.75 | 40.27 |
| MDKG | 78.26 | 80.69 | 79.45 | 48.54 | 50.86 | 49.67 |

## Checkpoints

| Run | Saved In | Log Dir |
| --- | --- | --- |
| ADKG | outputs/checkpoints/adkg/adkg_pubmedbert_e20_bs2/2026-05-02_18:50:44.982426 | outputs/logs/adkg_pubmedbert_e20_bs2/2026-05-02_18:50:44.982426 |
| MDKG | outputs/checkpoints/mdkg/mdkg_pubmedbert_e20_bs2/2026-05-02_19:49:36.134736 | outputs/logs/mdkg_pubmedbert_e20_bs2/2026-05-02_19:49:36.134736 |

## Test Results

| Run | Entity P | Entity R | Entity F1 | Relation P (NEC) | Relation R (NEC) | Relation F1 (NEC) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ADKG test | 70.20 | 65.78 | 67.92 | 44.94 | 39.53 | 42.06 |
| MDKG test | 77.02 | 78.36 | 77.68 | 49.08 | 50.42 | 49.74 |

## Dev100 Results

| Run | Entity P | Entity R | Entity F1 | Relation P (NEC) | Relation R (NEC) | Relation F1 (NEC) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ADKG dev100 | 64.19 | 65.71 | 64.94 | 43.86 | 44.64 | 44.25 |
| MDKG dev100 | 83.46 | 83.04 | 83.25 | 41.36 | 50.00 | 45.27 |

## Notes

- The main table above reports completed full-run development-set metrics.
- The test table reports held-out test metrics from the AutoDL evaluation logs captured on 2026-05-04.
- The dev100 table reports fixed-sample evaluation logs captured on 2026-05-04 using the same 100-sentence subsets aligned with the LLM experiments.
