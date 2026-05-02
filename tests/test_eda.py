from fixtures import sample_dataset


def test_compute_split_stats_counts_sentences_entities_relations():
    from bios740_topic2.eda import compute_split_stats

    stats = compute_split_stats(sample_dataset())

    assert stats["train"]["sentences"] == 1
    assert stats["train"]["entities"] == 2
    assert stats["train"]["relations"] == 1
    assert stats["train"]["relations_per_sentence"] == 1.0


def test_compute_type_distributions_counts_entity_and_relation_types():
    from bios740_topic2.eda import compute_type_distributions

    distributions = compute_type_distributions(sample_dataset())

    assert distributions["entity_types"]["method"] == 1
    assert distributions["entity_types"]["disease"] == 1
    assert distributions["relation_types"]["help_diagnose"] == 1
    assert distributions["relation_pairs"]["method->disease:help_diagnose"] == 1

