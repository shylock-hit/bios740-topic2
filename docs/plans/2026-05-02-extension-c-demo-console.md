# Extension C Demo Console Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a polished local demo console for Extension C that can configure, run, monitor, and inspect LLM annotation experiments and their output artifacts.

**Architecture:** The demo will use a lightweight FastAPI backend that wraps existing experiment scripts and output files. A static single-page frontend will provide a control-console interface for sampling, probing providers, running experiments, generating summaries/artifacts, and browsing outputs. The backend remains the source of truth; the frontend orchestrates and visualizes.

**Tech Stack:** Python 3.10+, FastAPI, Uvicorn, static HTML/CSS/JS frontend, existing experiment scripts and output directories.

---

### Task 1: Add backend dependencies and app scaffold

**Files:**
- Modify: `pyproject.toml`
- Create: `src/bios740_topic2/demo_api.py`
- Create: `src/bios740_topic2/demo_jobs.py`

**Steps:**
1. Add FastAPI and Uvicorn dependencies.
2. Create a small job runner abstraction for long-running subprocess tasks.
3. Create the FastAPI app scaffold with health route.
4. Verify the app imports cleanly.

**Verification:**
- Run: `python -c "from bios740_topic2.demo_api import app; print(app.title)"`
- Expected: prints the app title.

### Task 2: Expose experiment control endpoints

**Files:**
- Modify: `src/bios740_topic2/demo_api.py`
- Modify: `src/bios740_topic2/demo_jobs.py`

**Steps:**
1. Add endpoints for sample generation, provider probe, experiment run, summary generation, artifact generation, and error analysis.
2. Run long jobs in the background with job status tracking.
3. Expose status and file listing endpoints for the frontend.
4. Keep all endpoints thin wrappers around existing scripts.

**Verification:**
- Run: `python -c "from bios740_topic2.demo_api import app; print([route.path for route in app.routes])"`
- Expected: includes `/api/sample`, `/api/probe`, `/api/run`, `/api/status`, `/api/files`.

### Task 3: Create polished single-page frontend

**Files:**
- Create: `demo/index.html`
- Create: `demo/app.js`
- Create: `demo/styles.css`

**Steps:**
1. Build a single-page control console layout with four sections:
   - Experiment Config
   - Run Control
   - Live Status
   - Outputs
2. Add actions for all backend endpoints.
3. Add file preview support for markdown, JSON, and image artifacts.
4. Style the page as a dense research console with deliberate visual design.

**Verification:**
- Run local backend and open the page in a browser.
- Expected: controls render, buttons call APIs, status refreshes, outputs list is visible.

### Task 4: Integrate output artifact browsing

**Files:**
- Modify: `src/bios740_topic2/demo_api.py`
- Modify: `demo/app.js`

**Steps:**
1. Add backend endpoints to read output files safely from `outputs/llm_runs/`.
2. Add frontend panels for:
   - metrics preview
   - markdown preview
   - chart gallery
   - produced file list
3. Make it easy to inspect the latest run directory.

**Verification:**
- Run: browse a completed mock experiment directory.
- Expected: markdown, JSON, and PNG outputs all appear in the UI.

### Task 5: Add docs and local launch commands

**Files:**
- Modify: `README.md`

**Steps:**
1. Add a short section for launching the demo console.
2. Document how it uses `.env.llm` and existing scripts.
3. Document the local URL.

**Verification:**
- Run: `python -m uvicorn bios740_topic2.demo_api:app --reload --port 8010`
- Expected: app starts successfully.
