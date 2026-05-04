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
        "LLM_BASE_URL=https://api.deepseek.com/v1\nLLM_API_KEY=test-key\nLLM_MODEL=deepseek-chat\nLLM_WIRE_API=responses\nLLM_USER_AGENT=Codex-CLI/1.0\n",
        encoding="utf-8",
    )
    config = OpenAICompatConfig.from_env(path)
    assert config.base_url == "https://api.deepseek.com/v1"
    assert config.model == "deepseek-chat"
    assert config.wire_api == "responses"
    assert config.user_agent == "Codex-CLI/1.0"


def test_build_messages_uses_mdkg_schema_in_system_prompt():
    from bios740_topic2.llm_client import build_messages

    messages = build_messages("one_shot", {"text": "test"}, dataset="MDKG")
    system_prompt = messages[0]["content"]
    assert "MDKG" in system_prompt
    assert "Health_factors" in system_prompt
    assert "occurs_in" in system_prompt
    assert "treatment_target_for" not in system_prompt


def test_probe_provider_messages_payload(tmp_path, monkeypatch):
    from bios740_topic2.llm_client import OpenAICompatConfig, probe_provider

    captured: dict[str, object] = {}

    def fake_request(self, url, body):  # noqa: ANN001
        captured["url"] = url
        captured["body"] = body
        return {"content": [{"type": "text", "text": "{\"entities\": [], \"relations\": []}"}]}

    monkeypatch.setattr("bios740_topic2.llm_client.OpenAICompatibleClient._request_json", fake_request)
    config = OpenAICompatConfig(
        base_url="https://example.com/v1",
        api_key="test-key",
        model="gpt-5.4",
        wire_api="messages",
        user_agent="Claude-CLI/1.0",
    )
    result = probe_provider(config, dataset="ADKG")
    assert result["results"][0]["ok"] is True
    assert captured["url"] == "https://example.com/v1/messages"
    assert captured["body"]["model"] == "gpt-5.4"
    assert captured["body"]["messages"][0]["role"] == "user"
