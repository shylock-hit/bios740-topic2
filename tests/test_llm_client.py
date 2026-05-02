def test_load_env_file_reads_key_value_pairs(tmp_path):
    from bios740_topic2.llm_client import load_env_file

    path = tmp_path / ".env.llm"
    path.write_text(
        "LLM_BASE_URL=https://api.openai.com/v1\nLLM_API_KEY=test-key\nLLM_MODEL=gpt-5.2\n",
        encoding="utf-8",
    )
    values = load_env_file(path)
    assert values["LLM_BASE_URL"] == "https://api.openai.com/v1"
    assert values["LLM_API_KEY"] == "test-key"


def test_config_from_env_file_builds_config(tmp_path):
    from bios740_topic2.llm_client import OpenAICompatConfig

    path = tmp_path / ".env.llm"
    path.write_text(
        "LLM_BASE_URL=https://api.deepseek.com/v1\nLLM_API_KEY=test-key\nLLM_MODEL=deepseek-chat\nLLM_WIRE_API=responses\n",
        encoding="utf-8",
    )
    config = OpenAICompatConfig.from_env(path)
    assert config.base_url == "https://api.deepseek.com/v1"
    assert config.model == "deepseek-chat"
    assert config.wire_api == "responses"
