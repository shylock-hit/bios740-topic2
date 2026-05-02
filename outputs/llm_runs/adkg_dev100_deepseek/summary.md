# LLM Annotation Summary

## Quality

| Method | Strict Entity F1 | Strict Relation F1 | Relaxed Entity F1 | Relaxed Relation F1 |
| --- | ---: | ---: | ---: | ---: |
| one_shot | 0.4559 | 0.0000 | 0.4958 | 0.3750 |
| workflow | 0.4198 | 0.0000 | 0.4694 | 0.2730 |

## System

| Method | Avg Latency (s) | P50 (s) | P90 (s) | Parse Success | Failures | Validation Errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| one_shot | 15.0829 | 12.3360 | 29.8689 | 100/100 (100.00%) | 0 | 0 |
| workflow | 29.0727 | 26.5989 | 48.2366 | 100/100 (100.00%) | 0 | 0 |
