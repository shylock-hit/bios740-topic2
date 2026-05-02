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
    args = parser.parse_args()

    config = OpenAICompatConfig.from_env(args.env_file)
    result = probe_provider(config)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
