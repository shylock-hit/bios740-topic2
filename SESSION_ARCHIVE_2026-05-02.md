# Session Archive 2026-05-02

## Project State

Workspace: `/Users/Zhuanz1/Desktop/graph`

BIOS 740 Topic 2 project is using SpERT + PubMedBERT for biomedical entity and relation extraction
on ADKG and MDKG.

Completed:

- Official ADKG/MDKG JSON files were copied into `data/raw/`.
- Old Zenodo-converted data was moved to `data/raw_zenodo_converted_backup/`.
- SpERT conversion outputs exist locally under `outputs/spert/`.
- EDA figure/CSV assets exist under `outputs/report_artifacts/`.
- ADKG full 20-epoch baseline completed.
- MDKG full 20-epoch baseline completed.
- Shared-schema transfer scripts were added for extension component B.
- `.gitignore` was added for public GitHub push safety.

Important report/status files:

- `report/neurips6_report_draft.md`
- `report/report.md`
- `outputs/final_summary/current_status.md`
- `outputs/final_summary/adkg_final_metrics.md`
- `outputs/final_summary/mdkg_final_metrics.md`

## Baseline Results

| Run | Entity P | Entity R | Entity F1 | Relation P (NEC) | Relation R (NEC) | Relation F1 (NEC) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ADKG, PubMedBERT | 65.41 | 65.20 | 65.30 | 41.91 | 38.75 | 40.27 |
| MDKG, PubMedBERT | 78.26 | 80.69 | 79.45 | 48.54 | 50.86 | 49.67 |

ADKG checkpoint/log on AutoDL:

```text
outputs/checkpoints/adkg/adkg_pubmedbert_e20_bs2/2026-05-02_18:50:44.982426
outputs/logs/adkg_pubmedbert_e20_bs2/2026-05-02_18:50:44.982426
```

MDKG checkpoint/log on AutoDL:

```text
outputs/checkpoints/mdkg/mdkg_pubmedbert_e20_bs2/2026-05-02_19:49:36.134736
outputs/logs/mdkg_pubmedbert_e20_bs2/2026-05-02_19:49:36.134736
```

## Extension Component

Selected extension: transfer learning and domain adaptation.

Implemented shared-schema transfer scripts:

```text
src/bios740_topic2/shared_schema.py
scripts/make_shared_schema_spert.py
scripts/train_transfer_adkg_to_mdkg_shared.sh
scripts/train_transfer_mdkg_to_adkg_shared.sh
```

Shared schema:

- Entities: `disease`, `drug`, `gene`, `method`
- Relations: `abbreviation_for`, `associated_with`, `characteristic_of`, `help_diagnose`,
  `hyponym_of`, `risk_factor_of`, `treatment_for`

Recommended AutoDL run:

```bash
cd /root/autodl-tmp/graph
nohup bash scripts/train_transfer_adkg_to_mdkg_shared.sh > outputs/logs/transfer_adkg_to_mdkg_shared_console.log 2>&1 &
tail -f outputs/logs/transfer_adkg_to_mdkg_shared_console.log
```

## GitHub Push

`gh` is installed locally. User terminal reports successful login as `shylock-hit`.

The repo has been initialized locally with `git init`, but no commit/push has been completed yet.

`.gitignore` excludes:

- raw course data: `ADKG.json`, `MDKG.json`, `data/raw/`
- Zenodo/source archives and backups
- tar/zip archives
- checkpoints/logs/cache/generated SpERT data
- Python/macOS/editor caches

Manual push commands to run from `/Users/Zhuanz1/Desktop/graph`:

```bash
cd /Users/Zhuanz1/Desktop/graph

git status --short --ignored
git add -A
git status --short

git commit -m "init: add BIOS 740 Topic 2 extraction pipeline"

gh repo create bios740-topic2 \
  --public \
  --description "BIOS 740 Topic 2 biomedical knowledge graph extraction with SpERT and PubMedBERT" \
  --source=. \
  --remote=origin \
  --push
```

If the repository already exists, use:

```bash
git remote add origin https://github.com/shylock-hit/bios740-topic2.git
git push -u origin main
```

If Git says the branch is not `main`, run:

```bash
git branch -M main
git push -u origin main
```

## Verification Already Run

Local tests:

```text
python -m pytest -v
11 passed
```

Shared-schema generation:

```text
ADKG train: 13,376 entities, 2,968 relations
MDKG train: 14,758 entities, 3,788 relations
```
