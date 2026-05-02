from bios740_topic2.train_monitor import build_training_command, parse_nvidia_smi, parse_training_progress


def test_parse_training_progress_extracts_epoch_and_status():
    log_text = """
Train epoch 0: 100%|████| 5605/5605 [03:06<00:00, 30.13it/s]
2026-05-02 18:44:47,854 [MainThread  ] [INFO ]  Evaluate: valid
Evaluate epoch 1: 100%|████| 603/603 [00:12<00:00, 46.96it/s]
Train epoch 1:  23%|██▎| 1200/5200 [00:40<02:00, 33.0it/s]
"""
    parsed = parse_training_progress(log_text, total_epochs=20)
    assert parsed["current_epoch"] == 1
    assert parsed["completed_epochs"] == 1
    assert parsed["progress_percent"] == 10
    assert parsed["phase"] == "train"


def test_build_training_command_supports_presets():
    cmd = build_training_command(dataset="MDKG", preset="full", epochs=12, batch_size=3, label="mdkg_test")
    assert cmd[0] == "python"
    assert "external/spert/spert.py" in cmd
    assert "--train_path" in cmd
    assert "outputs/spert/mdkg/train.json" in cmd
    assert "12" in cmd
    assert "3" in cmd
    assert "mdkg_test" in cmd


def test_parse_nvidia_smi_extracts_gpu_summary():
    text = """
|   0  NVIDIA GeForce RTX 4080 ...    On  |   00000000:C9:00.0 Off |                  N/A |
| 30%   32C    P8              8W /  320W |       0MiB /  32760MiB |      0%      Default |
"""
    parsed = parse_nvidia_smi(text)
    assert parsed["gpu_name"].startswith("NVIDIA GeForce RTX 4080")
    assert parsed["memory_used_mib"] == 0
    assert parsed["memory_total_mib"] == 32760
    assert parsed["gpu_util_percent"] == 0
