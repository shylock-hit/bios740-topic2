# LLM Annotation Summary

## Quality

| Method | Strict Entity F1 | Strict Relation F1 | Relaxed Entity F1 | Relaxed Relation F1 |
| --- | ---: | ---: | ---: | ---: |
| one_shot | 0.2989 | 0.0000 | 0.3218 | 0.2759 |
| workflow | 0.2759 | 0.0000 | 0.2989 | 0.4865 |

## System

| Method | Avg Latency (s) | P50 (s) | P90 (s) | Parse Success | Failures | Validation Errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| one_shot | 14.5633 | 8.6639 | 36.7312 | 10/10 (100.00%) | 0 | 0 |
| workflow | 22.6816 | 20.2994 | 38.7660 | 10/10 (100.00%) | 0 | 0 |
