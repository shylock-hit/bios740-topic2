# LLM ADKG DeepSeek Dev100 Metrics

## Run Identity

- Dataset: `ADKG`
- Split: fixed `dev100` sample
- Provider/model family: `DeepSeek`
- Run dir: `outputs/llm_runs/adkg_dev100_deepseek`

## Available Metrics

This local run directory currently contains a completed `workflow` evaluation entry in `metrics.json`.

| Method | Strict Entity F1 | Strict Relation F1 | Relaxed Entity F1 | Relaxed Relation F1 | Avg Latency (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| workflow | 0.6757 | 0.0000 | 0.7027 | 0.1026 | 33.35 |

## Supporting Files

- Metrics JSON: `outputs/llm_runs/adkg_dev100_deepseek/metrics.json`
- Summary: `outputs/llm_runs/adkg_dev100_deepseek/summary.md`
- Error summaries:
  - `outputs/llm_runs/adkg_dev100_deepseek/one_shot_error_summary.md`
  - `outputs/llm_runs/adkg_dev100_deepseek/workflow_error_summary.md`
- Artifact index: `outputs/llm_runs/adkg_dev100_deepseek/artifacts/artifact_index.md`

## Note

The current `metrics.json` only exposes the `workflow` entry. The repository does contain `one_shot` predictions and progress files, but no corresponding finalized `one_shot` metric block is present in the saved JSON artifact.
