from fixtures import sample_dataset


def test_tokenize_with_offsets_preserves_character_spans():
    from bios740_topic2.spert_convert import tokenize_with_offsets

    tokens = tokenize_with_offsets("18F-FDG PET helps")

    assert tokens == [
        ("18F-FDG", 0, 7),
        ("PET", 8, 11),
        ("helps", 12, 17),
    ]


def test_convert_sample_maps_entities_and_relations_to_token_spans():
    from bios740_topic2.spert_convert import convert_sample

    converted = convert_sample(sample_dataset()["train"][0])

    assert converted["tokens"][:2] == ["18F-FDG", "PET"]
    assert converted["entities"][0]["start"] == 0
    assert converted["entities"][0]["end"] == 2
    assert converted["relations"][0]["head"] == 0
    assert converted["relations"][0]["tail"] == 1

