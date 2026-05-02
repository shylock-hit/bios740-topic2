# Extension C LLM Annotation Workflow Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a minimal, reproducible LLM-based annotation workflow for ADKG development samples and compare one-shot extraction against a 3-step agent workflow.

**Architecture:** The extension will reuse the existing dataset loader and evaluator, adding a small LLM pipeline layer. A sampling script will create a fixed ADKG dev subset. A workflow module will support both one-shot extraction and a 3-node pipeline: entity extraction, relation extraction, and review/fix. Postprocessing will align LLM text outputs back to sentence spans so the existing evaluator can compute strict metrics, while a relaxed evaluator will report overlap-based scores.

**Tech Stack:** Python 3.10+, existing project package, JSON artifacts, optional OpenAI-compatible HTTP client, LangGraph-compatible workflow abstraction, pytest.

---

### Task 1: Define LLM schemas and sample format

**Files:**
- Create: `src/bios740_topic2/llm_schema.py`
- Create: `tests/test_llm_schema.py`

**Steps:**
1. Write tests for ADKG entity and relation label sets.
2. Define constants for allowed ADKG entity types and relation types.
3. Add helper functions to validate LLM payload structure.
4. Run tests.

**Verification:**
- Run: `python -m pytest tests/test_llm_schema.py -v`
- Expected: all tests pass.

### Task 2: Build fixed-sample script for ADKG dev

**Files:**
- Create: `scripts/sample_adkg_dev_for_llm.py`
- Create: `tests/test_llm_sampling.py`

**Steps:**
1. Write a test for deterministic sampling with a fixed seed.
2. Implement a CLI that loads `data/raw/ADKG.json`, samples N dev sentences, and writes JSON.
3. Include metadata: dataset name, split, seed, sentence count.
4. Run tests.

**Verification:**
- Run: `python -m pytest tests/test_llm_sampling.py -v`
- Expected: all tests pass.

### Task 3: Add postprocessing to align LLM text back to spans

**Files:**
- Create: `src/bios740_topic2/llm_postprocess.py`
- Create: `tests/test_llm_postprocess.py`

**Steps:**
1. Write tests for exact text matching, duplicate entities, and relation endpoint linking.
2. Implement span alignment from predicted entity text to sentence character offsets.
3. Implement conversion into the existing evaluator's sample format with synthetic entity IDs.
4. Run tests.

**Verification:**
- Run: `python -m pytest tests/test_llm_postprocess.py -v`
- Expected: all tests pass.

### Task 4: Add relaxed evaluation

**Files:**
- Create: `src/bios740_topic2/relaxed_evaluate.py`
- Create: `tests/test_relaxed_evaluate.py`

**Steps:**
1. Write tests for overlap-based entity matching and relation matching built on overlapping endpoints.
2. Implement micro precision, recall, and F1 for relaxed entities and relations.
3. Keep the interface similar to the existing strict evaluator for easy reporting.
4. Run tests.

**Verification:**
- Run: `python -m pytest tests/test_relaxed_evaluate.py -v`
- Expected: all tests pass.

### Task 5: Add LLM workflow abstraction

**Files:**
- Create: `src/bios740_topic2/llm_workflow.py`
- Create: `tests/test_llm_workflow.py`

**Steps:**
1. Write tests for one-shot mode and 3-step workflow mode using a fake client.
2. Implement a provider-agnostic client interface.
3. Implement workflow functions: `run_one_shot`, `run_entities_then_relations`, and `run_review_step`.
4. Ensure outputs are normalized through `llm_schema`.
5. Run tests.

**Verification:**
- Run: `python -m pytest tests/test_llm_workflow.py -v`
- Expected: all tests pass.

### Task 6: Add experiment runner and summary script

**Files:**
- Create: `scripts/run_llm_annotation_experiment.py`
- Create: `scripts/summarize_llm_results.py`

**Steps:**
1. Implement a runner that loads sampled sentences, executes one-shot or workflow mode, and writes raw predictions.
2. Postprocess predictions into strict-eval format.
3. Run strict and relaxed metrics and write a metrics JSON.
4. Add a summary script that emits a markdown table for the report.

**Verification:**
- Run: `python scripts/run_llm_annotation_experiment.py --help`
- Expected: help text exits successfully.

### Task 7: Document extension C in the report scaffold

**Files:**
- Modify: `report/neurips6_report_draft.md`
- Modify: `report/report.md`

**Steps:**
1. Replace the transfer-learning extension description with an LLM annotation workflow section if the user confirms the switch.
2. Add tables for one-shot vs workflow strict and relaxed metrics.
3. Add cost/latency placeholders and error-analysis prompts.

**Verification:**
- Run: `test -s report/neurips6_report_draft.md`
- Expected: file exists and is non-empty.
