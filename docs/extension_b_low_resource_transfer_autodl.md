# Extension B Low-Resource Transfer AutoDL Runbook

This compact Extension B experiment tests whether shared-schema cross-domain transfer helps under a low-resource target setting.

## Design

Shared entity types:

```text
disease, drug, gene, method
```

Shared relation types:

```text
abbreviation_for, associated_with, characteristic_of, help_diagnose, hyponym_of, risk_factor_of, treatment_for
```

Target train ratio:

```text
25%
```

Final comparison:

| Run | Target | Purpose |
| --- | --- | --- |
| MDKG 25% baseline | MDKG | PubMedBERT initialized low-resource baseline |
| ADKG -> MDKG 25% transfer | MDKG | Full ADKG_shared source, then MDKG_shared train_25 fine-tune |
| ADKG 25% baseline | ADKG | PubMedBERT initialized low-resource baseline |
| MDKG -> ADKG 25% transfer | ADKG | Full MDKG_shared source, then ADKG_shared train_25 fine-tune |

The script also trains the two full source models required for transfer, so it runs six training stages total.

## Run

On AutoDL:

```bash
cd /root/autodl-tmp/graph
conda activate bios740-topic2
bash scripts/run_extension_b_low_resource_transfer_autodl.sh
```

Recommended background run:

```bash
cd /root/autodl-tmp/graph
conda activate bios740-topic2
nohup bash scripts/run_extension_b_low_resource_transfer_autodl.sh > outputs/logs/extension_b_low_resource_console.log 2>&1 &
```

Watch progress:

```bash
tail -f outputs/logs/extension_b_low_resource_console.log
```

## Faster Smoke Option

If runtime is too high, reduce epochs:

```bash
SOURCE_EPOCHS=5 TARGET_EPOCHS=5 bash scripts/run_extension_b_low_resource_transfer_autodl.sh
```

Use this only as a compact exploratory result. The default is `SOURCE_EPOCHS=8 TARGET_EPOCHS=8`.

## Outputs

Frozen summary:

```text
outputs/final_summary/extension_b_low_resource_transfer_summary.md
outputs/final_summary/extension_b_low_resource_runs.json
```

Training logs:

```text
outputs/logs/extb_source_adkg_full_e8.log
outputs/logs/extb_source_mdkg_full_e8.log
outputs/logs/extb_mdkg25_baseline_e8.log
outputs/logs/extb_adkg_to_mdkg25_e8.log
outputs/logs/extb_adkg25_baseline_e8.log
outputs/logs/extb_mdkg_to_adkg25_e8.log
```

Evaluation logs:

```text
outputs/logs/mdkg25_baseline_dev_eval.log
outputs/logs/mdkg25_baseline_test_eval.log
outputs/logs/adkg_to_mdkg25_transfer_dev_eval.log
outputs/logs/adkg_to_mdkg25_transfer_test_eval.log
outputs/logs/adkg25_baseline_dev_eval.log
outputs/logs/adkg25_baseline_test_eval.log
outputs/logs/mdkg_to_adkg25_transfer_dev_eval.log
outputs/logs/mdkg_to_adkg25_transfer_test_eval.log
```

Checkpoints:

```text
outputs/checkpoints/extension_b_low_resource/
```

## Reporting Rule

Only include Extension B in the final report if the transfer runs improve at least one target over the matched 25% baseline, especially relation F1 with NEC. If transfer does not improve, keep it as a negative exploratory result or move it to limitations/future work.
