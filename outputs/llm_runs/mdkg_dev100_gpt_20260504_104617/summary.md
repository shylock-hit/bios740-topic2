# LLM Annotation Summary

## Quality

| Method | Strict Entity F1 | Strict Relation F1 | Relaxed Entity F1 | Relaxed Relation F1 |
| --- | ---: | ---: | ---: | ---: |
| one_shot | 0.5915 | 0.0000 | 0.6521 | 0.3919 |
| workflow | 0.5782 | 0.0000 | 0.6328 | 0.3948 |

## System

| Method | Avg Latency (s) | P50 (s) | P90 (s) | Parse Success | Failures | Validation Errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| one_shot | 9.0270 | 8.3166 | 13.3771 | 100/100 (100.00%) | 0 | 0 |
| workflow | 21.0870 | 18.8925 | 31.5038 | 99/100 (99.00%) | 1 | 0 |
