class FakeClient:
    def complete_json(self, prompt_name, payload):
        if prompt_name == "one_shot":
            return {
                "entities": [{"text": "APOE", "type": "gene"}],
                "relations": [],
            }
        if prompt_name == "extract_entities":
            return {"entities": [{"text": "APOE", "type": "gene"}], "relations": []}
        if prompt_name == "extract_relations":
            return {
                "entities": [],
                "relations": [{"head": "APOE", "type": "associated_with", "tail": "dementia"}],
            }
        if prompt_name == "review_and_fix":
            return payload
        raise AssertionError("unexpected prompt")


def test_run_one_shot_returns_normalized_payload():
    from bios740_topic2.llm_workflow import run_one_shot

    result = run_one_shot(FakeClient(), "APOE is associated with dementia.")
    assert result.mode == "one_shot"
    assert result.payload["entities"][0]["text"] == "APOE"


def test_run_workflow_composes_three_steps():
    from bios740_topic2.llm_workflow import run_entities_then_relations

    result = run_entities_then_relations(FakeClient(), "APOE is associated with dementia.")
    assert result.mode == "workflow"
    assert result.payload["relations"][0]["type"] == "associated_with"


class MDKGClient:
    def complete_json(self, prompt_name, payload):
        if prompt_name == "one_shot":
            return {
                "entities": [{"text": "younger age", "type": "Health_factors"}],
                "relations": [{"head": "younger age", "type": "occurs_in", "tail": "depression"}],
            }
        raise AssertionError("unexpected prompt")


def test_run_one_shot_validates_against_selected_dataset():
    from bios740_topic2.llm_workflow import run_one_shot

    result = run_one_shot(MDKGClient(), "younger age occurs in depression.", dataset="MDKG")
    assert result.errors == []

    adkg_result = run_one_shot(MDKGClient(), "younger age occurs in depression.", dataset="ADKG")
    assert any("invalid entity type" in error for error in adkg_result.errors)
