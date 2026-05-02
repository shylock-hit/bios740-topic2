# Current Project Status

Date: 2026-05-02

## Completed

- Official ADKG and MDKG JSON files are in `data/raw/`.
- Zenodo/brat converted fallback data is backed up in `data/raw_zenodo_converted_backup/`.
- Preprocessing has generated SpERT inputs in `outputs/spert/adkg/` and `outputs/spert/mdkg/`.
- EDA figures and CSV assets have been generated in `outputs/report_artifacts/`.
- ADKG 20-epoch SpERT + PubMedBERT run is complete.
- MDKG 20-epoch SpERT + PubMedBERT run is complete.
- ADKG final dev metrics are saved in `outputs/final_summary/adkg_final_metrics.md`.

## Current ADKG Result

| Run | Entity P | Entity R | Entity F1 | Relation P (NEC) | Relation R (NEC) | Relation F1 (NEC) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ADKG, PubMedBERT | 65.41 | 65.20 | 65.30 | 41.91 | 38.75 | 40.27 |
| MDKG, PubMedBERT | 78.26 | 80.69 | 79.45 | 48.54 | 50.86 | 49.67 |

Key ADKG type-level observations:

- `disease` NER is strongest: F1 78.88.
- `mutation` NER is weakest: F1 37.50 over only 16 development examples.
- `abbreviation_for` is the strongest relation: strict NEC F1 69.69.
- `associated_with` is difficult: strict NEC F1 9.55.

This does not simply mean the model is bad. It shows that strict relation extraction is hard for
broad biomedical association labels, especially when relation labels are semantically loose and
class distributions are imbalanced.

Key MDKG type-level observations:

- `disease` NER is strongest: F1 86.91.
- `drug`, `method`, and `region` are also strong: F1 82.74, 81.12, and 80.21.
- `symptom` NER is weakest: F1 39.18 over only 43 development examples.
- `abbreviation_for` is the strongest relation: strict NEC F1 74.47.
- `characteristic_of` is weakest among common MDKG strict relation rows: strict NEC F1 32.92.

## Not Completed Yet

- Transfer/domain-adaptation extension experiment.
- Final report table rows for transfer.
- Final error examples from prediction files/checkpoint outputs.

## Next AutoDL Command

Single-domain ADKG and MDKG are now done. The next useful run is a transfer/domain-adaptation
experiment if time permits.

Upload these new/changed files to AutoDL:

```text
src/bios740_topic2/shared_schema.py
scripts/make_shared_schema_spert.py
scripts/train_transfer_adkg_to_mdkg_shared.sh
scripts/train_transfer_mdkg_to_adkg_shared.sh
```

Recommended first extension run:

```bash
nohup bash scripts/train_transfer_adkg_to_mdkg_shared.sh > outputs/logs/transfer_adkg_to_mdkg_shared_console.log 2>&1 &
tail -f outputs/logs/transfer_adkg_to_mdkg_shared_console.log
```

This run does two stages in one script:

1. Train ADKG shared-schema source model for 10 epochs, evaluating on MDKG dev.
2. Continue fine-tuning that checkpoint on MDKG shared-schema train for 10 epochs, evaluating on MDKG dev.

The shared schema contains:

- Entities: `disease`, `drug`, `gene`, `method`.
- Relations: `abbreviation_for`, `associated_with`, `characteristic_of`, `help_diagnose`,
  `hyponym_of`, `risk_factor_of`, `treatment_for`.

The generated shared-schema data keeps:

- ADKG train: 13,376 entities, 2,968 relations.
- MDKG train: 14,758 entities, 3,788 relations.

If skipping transfer, copy back or preserve these two log/checkpoint directories:

```bash
outputs/logs/adkg_pubmedbert_e20_bs2/2026-05-02_18:50:44.982426
outputs/logs/mdkg_pubmedbert_e20_bs2/2026-05-02_19:49:36.134736
outputs/checkpoints/adkg/adkg_pubmedbert_e20_bs2/2026-05-02_18:50:44.982426
outputs/checkpoints/mdkg/mdkg_pubmedbert_e20_bs2/2026-05-02_19:49:36.134736
```

## Answer To Figure/Data Question

The EDA figures do not require training logs. They are generated from `data/raw/ADKG.json` and
`data/raw/MDKG.json`, so they already exist locally under `outputs/report_artifacts/`.

Training and validation logs are needed for result tables, type-level model performance, and error
analysis. If the full logs are not copied back locally, we can still update the report from the
final terminal output, but keeping `outputs/logs/*_train_console.log` is better because it can be
parsed automatically.
