# Baseline Training Panel Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a lightweight baseline SpERT training panel to the existing demo console so the user can choose dataset/preset/parameters, start a training job, and watch epoch-level progress with log and GPU summaries.

**Architecture:** Extend the existing FastAPI demo backend with a small baseline-training API layer that starts subprocess jobs, stores the requested config in job metadata, and parses progress from log text. Reuse the current single-page frontend by adding one new card section for training controls and one new monitoring section for status, epoch progress, and GPU summary.

**Tech Stack:** Python 3.10+, FastAPI, subprocess-based job runner, existing SpERT shell scripts, React/Vite frontend, simple regex log parsing.

---

### Task 1: Add backend training request models and status helpers

**Files:**
- Modify: `src/bios740_topic2/demo_api.py`
- Create: `src/bios740_topic2/train_monitor.py`
- Test: `tests/test_train_monitor.py`

**Step 1: Write the failing test**

Add tests for:
- parsing epoch progress from representative log lines
- building a training command config from dataset/preset/epochs/batch size/label

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src pytest tests/test_train_monitor.py -q`

**Step 3: Write minimal implementation**

Implement:
- `parse_training_progress(log_text: str) -> dict`
- `build_training_request(...) -> dict`

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src pytest tests/test_train_monitor.py -q`

**Step 5: Commit**

Skip commit for now; continue implementation in the same working state.

### Task 2: Add backend training start/status endpoints

**Files:**
- Modify: `src/bios740_topic2/demo_api.py`
- Modify: `src/bios740_topic2/demo_jobs.py`
- Test: `tests/test_training_api.py`

**Step 1: Write the failing test**

Add tests for:
- `POST /api/train/start`
- `GET /api/train/status`
- correct job metadata and command generation

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src pytest tests/test_training_api.py -q`

**Step 3: Write minimal implementation**

Add:
- training request schema
- command builder for `ADKG smoke`, `ADKG full`, `MDKG full`
- training status endpoint returning:
  - job state
  - parsed epoch progress
  - log tail

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src pytest tests/test_training_api.py -q`

**Step 5: Commit**

Skip commit for now; continue implementation in the same working state.

### Task 3: Add simple GPU summary endpoint

**Files:**
- Modify: `src/bios740_topic2/demo_api.py`
- Modify: `src/bios740_topic2/train_monitor.py`
- Test: `tests/test_train_monitor.py`

**Step 1: Write the failing test**

Add a parser test for representative `nvidia-smi` text.

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src pytest tests/test_train_monitor.py -q`

**Step 3: Write minimal implementation**

Implement:
- `parse_nvidia_smi(text: str) -> dict`
- `/api/train/gpu`

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src pytest tests/test_train_monitor.py -q`

**Step 5: Commit**

Skip commit for now; continue implementation in the same working state.

### Task 4: Add baseline training panel to the frontend

**Files:**
- Modify: `web/src/App.jsx`
- Modify: `web/src/App.css`
- Modify: `web/src/i18n.js`

**Step 1: Add frontend state for training form**

Fields:
- dataset
- preset
- epochs
- batch size
- label

**Step 2: Add frontend actions**

Use:
- `POST /api/train/start`
- `GET /api/train/status`
- `GET /api/train/gpu`

**Step 3: Add visual layout**

Add:
- training config panel
- start button
- epoch progress bar
- log tail panel
- GPU summary tiles

**Step 4: Verify local build**

Run: `cd web && npm run build`

**Step 5: Commit**

Skip commit for now; continue implementation in the same working state.

### Task 5: Add short docs for AutoDL baseline usage

**Files:**
- Modify: `docs/autodl_demo_deploy_cn.md`
- Modify: `docs/demo_console_handoff_cn.md`

**Step 1: Document training panel purpose**

Explain:
- meant for AutoDL/GPU environments
- not for local laptop CPU runs

**Step 2: Document supported presets**

Explain:
- ADKG smoke
- ADKG full
- MDKG full

**Step 3: Verify docs paths and wording**

No extra tooling needed.
