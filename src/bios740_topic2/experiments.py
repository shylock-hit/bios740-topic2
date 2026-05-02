from __future__ import annotations

from pathlib import Path


def spert_config(
    experiment_name: str,
    dataset_dir: str,
    types_path: str,
    model_path: str = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract",
) -> str:
    return f"""[model]
model_path = {model_path}
tokenizer_path = {model_path}

[dataset]
types_path = {types_path}
train_path = {dataset_dir}/train.json
valid_path = {dataset_dir}/dev.json
test_path = {dataset_dir}/test.json

[training]
label = {experiment_name}
epochs = 20
train_batch_size = 2
eval_batch_size = 4
learning_rate = 5e-5
max_span_size = 10
rel_filter_threshold = 0.4
"""


def write_configs(output_dir: str | Path = "outputs/spert_configs") -> list[Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    configs = {
        "adkg": spert_config("adkg", "outputs/spert/adkg", "outputs/spert/adkg/types.json"),
        "mdkg": spert_config("mdkg", "outputs/spert/mdkg", "outputs/spert/mdkg/types.json"),
        "adkg_to_mdkg": spert_config(
            "adkg_to_mdkg", "outputs/spert/adkg", "outputs/spert/adkg/types.json"
        ),
        "mdkg_to_adkg": spert_config(
            "mdkg_to_adkg", "outputs/spert/mdkg", "outputs/spert/mdkg/types.json"
        ),
    }
    paths = []
    for name, text in configs.items():
        path = output / f"{name}.conf"
        path.write_text(text, encoding="utf-8")
        paths.append(path)
    return paths

