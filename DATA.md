# Dataset Instructions

Assignment dataset description:

https://www.notion.so/Datasets-Description-33b3d297a55f80879988c3ffbe3b03ca

Course Google Drive folder:

https://drive.google.com/drive/folders/1AqihJVtS9ZEjZuiESYmAb_ENfL9MTV10?usp=sharing

Public source datasets found online:

- ADKG / ADERC annotation dataset: https://zenodo.org/records/5770100
- ADKG / ADERC direct file: https://zenodo.org/api/records/5770100/files/ADERC.zip/content
- MDKG / MDIEC annotation dataset: https://zenodo.org/records/10960357
- MDKG / MDIEC direct file: https://zenodo.org/api/records/10960357/files/MDIEC.zip/content
- MDKG project repository: https://github.com/MonsterTea/MDKG

The course Google Drive provides the preferred preprocessed `ADKG.json` and `MDKG.json`.
These files exactly match the assignment split statistics.

The public Zenodo files are fallback source annotation archives (`ADERC.zip`, `MDIEC.zip`).
They are brat `.txt/.ann` files and do not exactly match the course split JSON unless converted
with the same private preprocessing rules as the course mirror.

Download these files into `data/raw/`:

- `data/raw/ADKG.json`
- `data/raw/MDKG.json`

Each JSON file must be a dictionary with:

- `train`
- `dev`
- `test`

Each split contains sentence-level samples with:

- `doc_id`
- `sent_id`
- `text`
- `entities`
- `relations`

After downloading, run:

```bash
bash scripts/run_all.sh
python -m pytest -v
```

If the Google Drive folder is incomplete or slow, try the fallback source archives:

```bash
bash scripts/download_zenodo_data.sh data/raw_sources
```

Then convert them only if the course JSON files are unavailable:

```bash
python scripts/convert_brat_sources.py
```

Current project state uses the course mirror JSON files in `data/raw/`.
