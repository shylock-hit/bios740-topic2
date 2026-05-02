from bios740_topic2.llm_postprocess import align_entities, build_prediction_sample


def test_align_entities_finds_exact_text_span():
    entities = align_entities(
        "18F-FDG PET helps diagnose focal dementia.",
        [{"text": "18F-FDG PET", "type": "method"}],
    )
    assert entities[0]["start"] == 0
    assert entities[0]["end"] == 11


def test_build_prediction_sample_links_relations_by_text():
    gold_sample = {
        "doc_id": "1",
        "sent_id": "1_s0",
        "text": "18F-FDG PET helps diagnose focal dementia.",
    }
    payload = {
        "entities": [
            {"text": "18F-FDG PET", "type": "method"},
            {"text": "focal dementia", "type": "disease"},
        ],
        "relations": [
            {"head": "18F-FDG PET", "type": "help_diagnose", "tail": "focal dementia"}
        ],
    }
    sample = build_prediction_sample(gold_sample, payload)
    assert len(sample["entities"]) == 2
    assert sample["relations"][0]["head"]["text"] == "18F-FDG PET"
