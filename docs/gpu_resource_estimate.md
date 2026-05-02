# GPU Training and Inference Resource Estimate

This estimate targets SpERT-style joint NER/RE training with PubMedBERT on the converted ADKG and
MDKG sentence-level datasets.

## Dataset State

The public Zenodo sources were downloaded and converted from brat `.txt/.ann` annotations:

| Dataset | Source abstracts | Converted sentences | Entities | Relations |
| --- | ---: | ---: | ---: | ---: |
| ADKG / ADERC | 758 | 8,162 | 20,883 | 5,496 |
| MDKG / MDIEC | 946 | 6,852 | 28,660 | 10,552 |

The assignment page reports 8,031 ADKG sentences and 6,678 MDKG sentences. The small mismatch is
expected because the public Zenodo archives are abstract-level brat annotations and the course
Google Drive mirror appears to apply additional sentence splitting or filtering.

## Recommended GPU

| Scenario | Minimum | Recommended | Notes |
| --- | --- | --- | --- |
| Smoke test | 8 GB VRAM | 12 GB VRAM | 1-2 epochs, small batch, confirms pipeline |
| Full single-dataset run | 12 GB VRAM | 16-24 GB VRAM | Batch size 2-4 with PubMedBERT |
| Cross-domain experiments | 16 GB VRAM | 24 GB VRAM | Four runs plus checkpoint storage |
| Faster iteration | 24 GB VRAM | A10/A5000/A100 | Useful for hyperparameter sweeps |

For Apple Silicon, MPS may work for simple transformer fine-tuning, but SpERT compatibility is less
predictable than CUDA. A CUDA GPU is the safer path.

## Time Estimate

Approximate wall-clock time for PubMedBERT-base, max span size 10, batch size 2-4:

| Hardware | ADKG 20 epochs | MDKG 20 epochs | Four experiments |
| --- | ---: | ---: | ---: |
| T4 16 GB | 2-4 h | 2-5 h | 8-18 h |
| L4 24 GB | 1-2.5 h | 1.5-3 h | 5-11 h |
| A10/A5000 24 GB | 0.8-2 h | 1-2.5 h | 4-9 h |
| A100 40 GB | <1 h | <1.5 h | 2-5 h |

The relation classifier is sensitive to candidate span count. Longer sentences and larger
`max_span_size` can increase memory and runtime sharply.

## Disk and RAM

| Resource | Estimate |
| --- | ---: |
| Raw Zenodo archives and extracted brat data | ~21 MB |
| Converted JSON and SpERT inputs | ~35 MB |
| PubMedBERT model cache | ~450-700 MB |
| One SpERT checkpoint directory | ~1-2 GB |
| Four experiments with best checkpoints/logs | ~5-10 GB |
| CPU RAM | 8 GB minimum, 16 GB comfortable |

## Suggested Training Plan

1. Run `python -m pytest -v`.
2. Run `bash scripts/run_all.sh` to regenerate EDA and SpERT inputs.
3. Run a 1-epoch smoke test on ADKG with batch size 1-2.
4. Run full ADKG and MDKG single-domain baselines.
5. Run transfer experiments: ADKG to MDKG and MDKG to ADKG.
6. Fill `report/report.md` Table 1 from the evaluation outputs.

## Hyperparameter Defaults

Current generated configs use:

- Encoder: `microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract`
- Epochs: `20`
- Train batch size: `2`
- Eval batch size: `4`
- Learning rate: `5e-5`
- Max span size: `10`
- Relation filter threshold: `0.4`

If VRAM is insufficient, first reduce `train_batch_size` to `1`, then reduce `max_span_size` to `8`.

