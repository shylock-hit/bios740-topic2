# LLM MDKG GPT or Gemini Dev100 Metrics

## Status

This file summarizes the completed MDKG-specific `dev100` LLM comparison runs for GPT and Gemini, with DeepSeek retained as an additional reference point.

## Provider Connectivity

- GPT relay status: verified working with `gpt-5.5`, `responses`, and `Codex-CLI/1.0`
- Gemini relay status: verified working with `gemini-3.1-pro-preview`, `chat_completions`, and `Codex-CLI/1.0`

## Current MDKG Comparison Artifacts

- GPT run dir: `outputs/llm_runs/mdkg_dev100_gpt_20260504_104617`
- Completed files now present:
  - `metrics.json`
  - `summary.md`
  - `one_shot_predictions.json`
  - `one_shot_progress.json`
  - `one_shot_progress.jsonl`
  - `workflow_predictions.json`
  - `workflow_progress.json`
  - `workflow_progress.jsonl`
- Gemini run dir: `outputs/llm_runs/mdkg_dev100_gemini_20260504_120235`
- Completed files now present:
  - `metrics.json`
  - `summary.md`
  - `one_shot_predictions.json`
  - `one_shot_progress.json`
  - `one_shot_progress.jsonl`
  - `workflow_predictions.json`
  - `workflow_progress.json`
  - `workflow_progress.jsonl`

## Completed GPT and Gemini Results

| Provider | Run Dir | Method | Strict Entity F1 | Strict Relation F1 | Relaxed Entity F1 | Relaxed Relation F1 | Avg Latency (s) | Success |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT | `outputs/llm_runs/mdkg_dev100_gpt_20260504_104617` | one_shot | 0.5915 | 0.0000 | 0.6521 | 0.3919 | 9.03 | 100/100 |
| GPT | `outputs/llm_runs/mdkg_dev100_gpt_20260504_104617` | workflow | 0.5782 | 0.0000 | 0.6328 | 0.3948 | 21.09 | 99/100 |
| Gemini | `outputs/llm_runs/mdkg_dev100_gemini_20260504_120235` | one_shot | 0.5308 | 0.0000 | 0.6183 | 0.5000 | 10.84 | 100/100 |
| Gemini | `outputs/llm_runs/mdkg_dev100_gemini_20260504_120235` | workflow | 0.5376 | 0.0000 | 0.6317 | 0.4837 | 28.33 | 100/100 |

## Interpretation

- Strict relation F1 remains `0.0000` for all four GPT/Gemini settings under exact matching.
- Gemini is clearly stronger than GPT on relaxed relation F1 under the MDKG-specific prompt:
  - Gemini one_shot: `0.5000`
  - Gemini workflow: `0.4837`
  - GPT one_shot: `0.3919`
  - GPT workflow: `0.3948`
- Workflow does not show a stable quality gain:
  - GPT workflow improves relaxed relation F1 by only `0.0029` over GPT one_shot
  - Gemini workflow is lower than Gemini one_shot by `0.0163`
- Workflow is substantially slower:
  - GPT: `21.09s / 9.03s ≈ 2.34x`
  - Gemini: `28.33s / 10.84s ≈ 2.61x`
- Reliability:
  - GPT workflow has `1` failure
  - GPT one_shot, Gemini one_shot, and Gemini workflow all finish `100/100`

## Closest Completed MDKG LLM References

Completed DeepSeek MDKG `dev100` runs remain useful comparison references:

| Run Dir | Method | Strict Entity F1 | Strict Relation F1 | Relaxed Entity F1 | Relaxed Relation F1 | Avg Latency (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `outputs/llm_runs/mdkg_dev100_deepseek` | one_shot | 0.4453 | 0.0000 | 0.4848 | 0.4286 | 11.49 |
| `outputs/llm_runs/mdkg_dev100_deepseek` | workflow | 0.4247 | 0.0000 | 0.4822 | 0.3673 | 18.78 |
| `outputs/llm_runs/mdkg_dev100_deepseek_clean_20260503_095653` | one_shot | 0.4163 | 0.0000 | 0.4690 | 0.4476 | 10.98 |
| `outputs/llm_runs/mdkg_dev100_deepseek_clean_20260503_095653` | workflow | 0.4005 | 0.0000 | 0.4547 | 0.4013 | 19.83 |

## Practical Takeaway

On this MDKG `dev100` comparison, the MDKG-specific Gemini prompt is the best relaxed relation extractor among the tested GPT/Gemini settings, while one_shot remains the better efficiency-quality tradeoff than workflow.
