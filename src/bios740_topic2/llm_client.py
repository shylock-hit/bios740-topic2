from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request

from bios740_topic2.llm_schema import DATASET_SCHEMAS


def load_env_file(path: str | Path) -> dict[str, str]:
    values: dict[str, str] = {}
    env_path = Path(path)
    if not env_path.exists():
        raise FileNotFoundError(
            f"Env file not found: {env_path}. Create .env.llm in the project root or pass --env-file."
        )
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


@dataclass
class OpenAICompatConfig:
    base_url: str
    api_key: str
    model: str
    wire_api: str = "chat_completions"
    user_agent: str = ""

    @classmethod
    def from_env(cls, env_file: str | Path | None = None) -> "OpenAICompatConfig":
        file_values = load_env_file(env_file) if env_file else {}

        def get(name: str, default: str = "") -> str:
            return os.environ.get(name) or file_values.get(name, default)

        base_url = get("LLM_BASE_URL", "https://api.openai.com/v1")
        api_key = get("LLM_API_KEY")
        model = get("LLM_MODEL", "gpt-5.2")
        wire_api = get("LLM_WIRE_API", "chat_completions")
        user_agent = get("LLM_USER_AGENT", "")
        if not api_key:
            raise ValueError("Missing LLM_API_KEY in environment or env file")
        return cls(
            base_url=base_url.rstrip("/"),
            api_key=api_key,
            model=model,
            wire_api=wire_api,
            user_agent=user_agent,
        )


def build_messages(prompt_name: str, payload: dict[str, Any], dataset: str = "ADKG") -> list[dict[str, Any]]:
    dataset_key = dataset.upper()
    if dataset_key not in DATASET_SCHEMAS:
        raise ValueError(f"Unsupported dataset: {dataset}")
    schema = DATASET_SCHEMAS[dataset_key]
    entity_types = ", ".join(schema["entities"])
    relation_types = ", ".join(schema["relations"])

    if prompt_name == "one_shot":
        user_prompt = (
            "Extract biomedical entities and relations from the sentence. "
            "Return JSON with keys entities and relations only.\n\n"
            f"Sentence: {payload['text']}"
        )
    elif prompt_name == "extract_entities":
        user_prompt = (
            "Extract all biomedical entities from the sentence. "
            "Return JSON with keys entities and relations, where relations is an empty list.\n\n"
            f"Sentence: {payload['text']}"
        )
    elif prompt_name == "extract_relations":
        user_prompt = (
            "Given the sentence and entity list, extract valid directed relations among those entities. "
            "Return JSON with keys entities and relations, where entities is an empty list.\n\n"
            f"Sentence: {payload['text']}\n"
            f"Entities: {json.dumps(payload['entities'], ensure_ascii=False)}"
        )
    elif prompt_name == "review_and_fix":
        user_prompt = (
            "Review the extracted entities and relations. Fix invalid labels, invalid head/tail references, "
            "and obvious omissions. Return JSON with keys entities and relations only.\n\n"
            f"Sentence: {payload['text']}\n"
            f"Entities: {json.dumps(payload['entities'], ensure_ascii=False)}\n"
            f"Relations: {json.dumps(payload['relations'], ensure_ascii=False)}"
        )
    else:
        raise ValueError(f"Unknown prompt {prompt_name}")

    system_prompt = (
        f"You are annotating {dataset_key} biomedical sentences. "
        f"Allowed entity types: {entity_types}. "
        f"Allowed relation types: {relation_types}. "
        "Return strict JSON only with shape "
        "{\"entities\": [{\"text\": \"...\", \"type\": \"...\"}], "
        "\"relations\": [{\"head\": \"...\", \"type\": \"...\", \"tail\": \"...\"}]}. "
        "Do not include markdown fences or extra prose."
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _build_messages(prompt_name: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    return build_messages(prompt_name, payload, dataset=str(payload.get("dataset", "ADKG")))


class OpenAICompatibleClient:
    def __init__(self, config: OpenAICompatConfig):
        self.config = config

    def _request_json(self, url: str, body: dict[str, Any]) -> dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
        }
        if self.config.user_agent:
            headers["User-Agent"] = self.config.user_agent
        req = request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with request.urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))

    def complete_json(self, prompt_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        messages = build_messages(prompt_name, payload, dataset=str(payload.get("dataset", "ADKG")))
        if self.config.wire_api == "responses":
            body = {
                "model": self.config.model,
                "input": messages,
                "text": {"format": {"type": "json_object"}},
            }
            data = self._request_json(f"{self.config.base_url}/responses", body)
            content = data["output"][0]["content"][0]["text"]
            return json.loads(content)
        if self.config.wire_api == "messages":
            body = {
                "model": self.config.model,
                "system": messages[0]["content"],
                "messages": [{"role": "user", "content": messages[1]["content"]}],
                "max_tokens": 512,
            }
            data = self._request_json(f"{self.config.base_url}/messages", body)
            content_blocks = data.get("content", [])
            text = "".join(
                block.get("text", "")
                for block in content_blocks
                if isinstance(block, dict) and block.get("type") == "text"
            )
            return json.loads(text)

        body = {
            "model": self.config.model,
            "messages": messages,
            "response_format": {"type": "json_object"},
        }
        data = self._request_json(f"{self.config.base_url}/chat/completions", body)
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)


def probe_provider(config: OpenAICompatConfig, dataset: str = "ADKG") -> dict[str, Any]:
    messages = build_messages(
        "extract_entities",
        {"text": "APOE is associated with dementia."},
        dataset=dataset,
    )
    targets = []
    if config.wire_api == "responses":
        targets.append(
            (
                "responses",
                f"{config.base_url}/responses",
                {
                    "model": config.model,
                    "input": messages,
                    "max_output_tokens": 64,
                    "text": {"format": {"type": "json_object"}},
                },
            )
        )
    elif config.wire_api == "messages":
        targets.append(
            (
                "messages",
                f"{config.base_url}/messages",
                {
                    "model": config.model,
                    "system": messages[0]["content"],
                    "messages": [{"role": "user", "content": messages[1]["content"]}],
                    "max_tokens": 128,
                },
            )
        )
    else:
        targets.append(
            (
                "chat_completions",
                f"{config.base_url}/chat/completions",
                {
                    "model": config.model,
                    "messages": messages,
                    "max_tokens": 64,
                    "response_format": {"type": "json_object"},
                },
            )
        )

    results = []
    client = OpenAICompatibleClient(config)
    for name, url, body in targets:
        try:
            data = client._request_json(url, body)
            results.append({"endpoint": name, "url": url, "ok": True, "keys": sorted(data.keys())})
        except error.HTTPError as exc:
            try:
                body_text = exc.read().decode("utf-8", errors="replace")
            except Exception:
                body_text = ""
            results.append(
                {
                    "endpoint": name,
                    "url": url,
                    "ok": False,
                    "http_status": exc.code,
                    "reason": exc.reason,
                    "body": body_text[:1000],
                }
            )
        except Exception as exc:
            results.append(
                {
                    "endpoint": name,
                    "url": url,
                    "ok": False,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
    return {
        "base_url": config.base_url,
        "model": config.model,
        "wire_api": config.wire_api,
        "user_agent": config.user_agent,
        "dataset": dataset.upper(),
        "results": results,
    }
