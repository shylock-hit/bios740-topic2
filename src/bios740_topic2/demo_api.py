from __future__ import annotations

import json
import subprocess
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from bios740_topic2.demo_jobs import JobRegistry, safe_relpath


APP_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = APP_ROOT / "outputs" / "llm_runs"
WEB_DIST = APP_ROOT / "web" / "dist"
registry = JobRegistry()

app = FastAPI(title="Extension C Demo Console")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


class SampleRequest(BaseModel):
    input_path: str = "data/raw/ADKG.json"
    count: int = 100
    seed: int = 740
    output_name: str = "adkg_dev100_sample.json"


class ProbeRequest(BaseModel):
    env_file: str = ".env.llm"


class RunRequest(BaseModel):
    sample_path: str
    output_dir_name: str
    mode: str = "both"
    provider: str = "openai_compat"
    env_file: str = ".env.llm"


class ArtifactRequest(BaseModel):
    run_dir_name: str
    gold_path: str = "outputs/llm_runs/adkg_dev100_sample.json"


def _run_python(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(APP_ROOT), capture_output=True, text=True)


@app.post("/api/sample")
def sample_data(request: SampleRequest) -> dict[str, str]:
    output_path = OUTPUT_ROOT / request.output_name
    result = _run_python(
        [
            "python",
            "scripts/sample_dev_for_llm.py",
            "--input",
            request.input_path,
            "--output",
            str(output_path),
            "--count",
            str(request.count),
            "--seed",
            str(request.seed),
        ]
    )
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr or result.stdout)
    return {"status": "ok", "output": safe_relpath(APP_ROOT, output_path)}


@app.post("/api/probe")
def probe_provider(request: ProbeRequest) -> JSONResponse:
    result = _run_python(["python", "scripts/probe_llm_provider.py", "--env-file", request.env_file])
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr or result.stdout)
    return JSONResponse(content=json.loads(result.stdout))


@app.post("/api/run")
def run_experiment(request: RunRequest) -> dict[str, str]:
    run_dir = OUTPUT_ROOT / request.output_dir_name
    record = registry.create(
        "run_experiment",
        [
            "python",
            "scripts/run_llm_annotation_experiment.py",
            "--sample",
            request.sample_path,
            "--output-dir",
            str(run_dir),
            "--mode",
            request.mode,
            "--provider",
            request.provider,
            "--env-file",
            request.env_file,
        ],
        str(APP_ROOT),
        metadata={"run_dir": safe_relpath(APP_ROOT, run_dir)},
    )
    registry.run_async(record)
    return {"status": "started", "job_id": record.id, "run_dir": safe_relpath(APP_ROOT, run_dir)}


@app.get("/api/status")
def list_status() -> dict[str, list[dict]]:
    records = []
    for job in registry.list():
        records.append(
            {
                "id": job.id,
                "name": job.name,
                "status": job.status,
                "returncode": job.returncode,
                "metadata": job.metadata,
                "stdout_tail": job.stdout[-1000:],
                "stderr_tail": job.stderr[-1000:],
            }
        )
    return {"jobs": records}


@app.post("/api/summarize")
def summarize_run(request: ArtifactRequest) -> dict[str, str]:
    run_dir = OUTPUT_ROOT / request.run_dir_name
    output = run_dir / "summary.md"
    result = _run_python(
        [
            "python",
            "scripts/summarize_llm_results.py",
            "--metrics",
            str(run_dir / "metrics.json"),
            "--output",
            str(output),
        ]
    )
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr or result.stdout)
    return {"status": "ok", "output": safe_relpath(APP_ROOT, output)}


@app.post("/api/artifacts")
def generate_artifacts(request: ArtifactRequest) -> dict[str, str]:
    run_dir = OUTPUT_ROOT / request.run_dir_name
    result = _run_python(["python", "scripts/generate_llm_artifacts.py", "--run-dir", str(run_dir)])
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr or result.stdout)
    return {"status": "ok", "output": safe_relpath(APP_ROOT, run_dir / "artifacts")}


@app.post("/api/errors")
def analyze_errors(request: ArtifactRequest) -> dict[str, str]:
    run_dir = OUTPUT_ROOT / request.run_dir_name
    output = run_dir / "error_summary.md"
    result = _run_python(
        [
            "python",
            "scripts/analyze_llm_errors.py",
            "--gold",
            request.gold_path,
            "--pred",
            str(run_dir / "one_shot_predictions.json"),
            "--progress-jsonl",
            str(run_dir / "one_shot_progress.jsonl"),
            "--output",
            str(output),
        ]
    )
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr or result.stdout)
    return {"status": "ok", "output": safe_relpath(APP_ROOT, output)}


@app.get("/api/files")
def list_files(run_dir_name: str) -> dict[str, list[str]]:
    run_dir = OUTPUT_ROOT / run_dir_name
    if not run_dir.exists():
        raise HTTPException(status_code=404, detail=f"Run directory not found: {run_dir_name}")
    files = sorted(str(path.relative_to(APP_ROOT)) for path in run_dir.rglob("*") if path.is_file())
    return {"files": files}


@app.get("/api/file")
def get_file(path: str):
    target = (APP_ROOT / path).resolve()
    if not str(target).startswith(str(APP_ROOT.resolve())) or not target.exists():
        raise HTTPException(status_code=404, detail="File not found")
    if target.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
        return FileResponse(target)
    return JSONResponse({"path": path, "content": target.read_text(encoding="utf-8", errors="replace")})


if WEB_DIST.exists():
    app.mount("/", StaticFiles(directory=WEB_DIST, html=True), name="web")
