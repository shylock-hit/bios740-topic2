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
    process: subprocess.Popen[str] | None = None


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

    def stop(self, job_id: str) -> bool:
        record = self.get(job_id)
        if record is None or record.process is None or record.status != "running":
            return False
        record.process.terminate()
        record.status = "stopping"
        return True

    def _stream_output(self, stream, record: JobRecord, field_name: str) -> None:
        chunks: list[str] = []
        try:
            for line in iter(stream.readline, ""):
                if not line:
                    break
                chunks.append(line)
                setattr(record, field_name, getattr(record, field_name) + line)
        finally:
            stream.close()

    def _run(self, job_id: str) -> None:
        record = self.get(job_id)
        if record is None:
            return
        record.status = "running"
        proc = subprocess.Popen(
            record.cmd,
            cwd=record.workdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        record.process = proc
        stdout_thread = threading.Thread(target=self._stream_output, args=(proc.stdout, record, "stdout"), daemon=True)
        stderr_thread = threading.Thread(target=self._stream_output, args=(proc.stderr, record, "stderr"), daemon=True)
        stdout_thread.start()
        stderr_thread.start()
        returncode = proc.wait()
        stdout_thread.join()
        stderr_thread.join()
        record.returncode = returncode
        if record.status == "stopping":
            record.status = "stopped"
        else:
            record.status = "completed" if returncode == 0 else "failed"
        record.process = None


def safe_relpath(root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))
