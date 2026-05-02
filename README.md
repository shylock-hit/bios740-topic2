# BIOS 740 Topic 2: Biomedical NER and Relation Extraction

This repository contains code and a report scaffold for the Topic 2 final project on ADKG and
MDKG PubMed sentence datasets.

## Data

Primary path: use the course Google Drive mirror. Download the assignment JSON files from the
Notion page and place:

- `data/raw/ADKG.json`
- `data/raw/MDKG.json`

Set up a clean conda environment:

```bash
bash scripts/setup_conda_env.sh bios740-topic2
conda activate bios740-topic2
```

If `gdown` works for the course Google Drive folder, run:

```bash
bash scripts/download_data.sh
```

If Google Drive folder download is slow, open the folder manually in Chrome and download
`ADKG.json` and `MDKG.json` into `data/raw/`.

Fallback only: the public source datasets are also available from Zenodo:

```bash
bash scripts/download_zenodo_data.sh data/raw_sources
```

Those archives are named `ADERC.zip` and `MDIEC.zip`. They are abstract-level brat annotations,
not the course-ready split JSON files.

Only run this fallback conversion if `data/raw/ADKG.json` and `data/raw/MDKG.json` are missing:

```bash
python scripts/convert_brat_sources.py
```

Do not run `convert_brat_sources.py` after placing the course mirror JSON files into `data/raw`,
because it will overwrite them with a sentence-split reconstruction.

## Run

```bash
python -m pytest -v
bash scripts/run_all.sh
python scripts/estimate_resources.py
```

The pipeline writes EDA summaries to `outputs/*_eda_summary.json`, SpERT-format files to
`outputs/spert/`, and SpERT config templates to `outputs/spert_configs/`.

Report-ready EDA figures can be generated with:

```bash
python scripts/generate_report_artifacts.py
```

The images and CSV tables are written to `outputs/report_artifacts/`. They are computed from the
official assignment JSON files in `data/raw/ADKG.json` and `data/raw/MDKG.json`.

## Model

The recommended training path is SpERT with PubMedBERT:

```bash
git clone https://github.com/lavis-nlp/spert.git external/spert
bash scripts/train_spert.sh outputs/spert_configs/adkg.conf
```

The report in `report/report.md` documents the baseline, evaluation protocol, and extension
experiment plan for cross-domain transfer between ADKG and MDKG.

On AutoDL, use the prepared scripts:

```bash
chmod +x scripts/train_*.sh
bash scripts/train_adkg_smoke.sh
nohup bash scripts/train_adkg_full.sh > outputs/logs/adkg_train_console.log 2>&1 &
nohup bash scripts/train_mdkg_full.sh > outputs/logs/mdkg_train_console.log 2>&1 &
```

## GPU Estimate

Use CUDA if possible. A smoke test can run with 8-12 GB VRAM; full PubMedBERT + SpERT runs are more
comfortable on 16-24 GB VRAM. Expect roughly 2-5 hours per dataset on a T4 16 GB GPU and 1-3 hours
on an L4/A10-class GPU. See `docs/gpu_resource_estimate.md`.
