# LLM Annotation Summary

## Quality

| Method | Strict Entity F1 | Strict Relation F1 | Relaxed Entity F1 | Relaxed Relation F1 |
| --- | ---: | ---: | ---: | ---: |
| one_shot | 0.5308 | 0.0000 | 0.6183 | 0.5000 |
| workflow | 0.5376 | 0.0000 | 0.6317 | 0.4837 |

## System

| Method | Avg Latency (s) | P50 (s) | P90 (s) | Parse Success | Failures | Validation Errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| one_shot | 10.8450 | 10.5143 | 15.9602 | 100/100 (100.00%) | 0 | 0 |
| workflow | 28.3279 | 26.5095 | 39.3677 | 100/100 (100.00%) | 0 | 0 |
