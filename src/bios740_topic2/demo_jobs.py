from __future__ import annotations

import subprocess
import threading
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class JobRecord:
    id: str
    name: str
    cmd: list[str]
    workdir: str
    status: str = "queued"
    stdout: str = ""
    stderr: str = ""
    returncode: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class JobRegistry:
    def __init__(self) -> None:
        self.jobs: dict[str, JobRecord] = {}
        self._lock = threading.Lock()

    def create(self, name: str, cmd: list[str], workdir: str, metadata: dict[str, Any] | None = None) -> JobRecord:
        record = JobRecord(
            id=str(uuid.uuid4()),
            name=name,
            cmd=cmd,
            workdir=workdir,
            metadata=metadata or {},
        )
        with self._lock:
            self.jobs[record.id] = record
        return record

    def get(self, job_id: str) -> JobRecord | None:
        with self._lock:
            return self.jobs.get(job_id)

    def list(self) -> list[JobRecord]:
        with self._lock:
            return list(self.jobs.values())

    def run_async(self, record: JobRecord) -> None:
        thread = threading.Thread(target=self._run, args=(record.id,), daemon=True)
        thread.start()

    def _run(self, job_id: str) -> None:
        record = self.get(job_id)
        if record is None:
            return
        record.status = "running"
        proc = subprocess.run(
            record.cmd,
            cwd=record.workdir,
            capture_output=True,
            text=True,
        )
        record.stdout = proc.stdout
        record.stderr = proc.stderr
        record.returncode = proc.returncode
        record.status = "completed" if proc.returncode == 0 else "failed"


def safe_relpath(root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))
