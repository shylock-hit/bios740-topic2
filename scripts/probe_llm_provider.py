#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bios740_topic2.llm_client import OpenAICompatConfig, probe_provider


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe an OpenAI-compatible or responses-style LLM provider.")
    parser.add_argument("--env-file", default=".env.llm")
    parser.add_argument("--dataset", choices=("ADKG", "MDKG"), default="ADKG")
    parser.add_argument("--base-url")
    parser.add_argument("--model")
    parser.add_argument("--wire-api", choices=("chat_completions", "responses", "messages"))
    parser.add_argument("--user-agent")
    args = parser.parse_args()

    config = OpenAICompatConfig.from_env(args.env_file)
    if args.base_url:
        config.base_url = args.base_url.rstrip("/")
    if args.model:
        config.model = args.model
    if args.wire_api:
        config.wire_api = args.wire_api
    if args.user_agent:
        config.user_agent = args.user_agent
    result = probe_provider(config, dataset=args.dataset)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
