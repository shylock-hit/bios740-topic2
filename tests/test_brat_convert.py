from pathlib import Path


def test_parse_brat_ann_reads_entities_and_relations(tmp_path):
    from bios740_topic2.brat_convert import parse_brat_ann

    ann = tmp_path / "doc.ann"
    ann.write_text(
        "T1\tdrug 0 9\tDonepezil\n"
        "T2\tdisease 17 36\tAlzheimer's disease\n"
        "R1\ttreatment_for Arg1:T1 Arg2:T2\t\n",
        encoding="utf-8",
    )

    entities, relations = parse_brat_ann(ann)

    assert entities[0]["id"] == "T1"
    assert entities[0]["type"] == "drug"
    assert relations[0]["head_id"] == "T1"
    assert relations[0]["tail_id"] == "T2"


def test_convert_document_keeps_only_sentence_internal_relations(tmp_path):
    from bios740_topic2.brat_convert import convert_document

    text = "Donepezil treats Alzheimer's disease. APOE is associated with dementia."
    txt = tmp_path / "1.txt"
    ann = tmp_path / "1.ann"
    txt.write_text(text, encoding="utf-8")
    ann.write_text(
        "T1\tdrug 0 9\tDonepezil\n"
        "T2\tdisease 17 36\tAlzheimer's disease\n"
        "T3\tgene 38 42\tAPOE\n"
        "T4\tdisease 62 70\tdementia\n"
        "R1\ttreatment_for Arg1:T1 Arg2:T2\t\n"
        "R2\tassociated_with Arg1:T2 Arg2:T4\t\n",
        encoding="utf-8",
    )

    samples = convert_document(txt, ann)

    assert len(samples) == 2
    assert samples[0]["text"] == "Donepezil treats Alzheimer's disease."
    assert samples[0]["entities"][0]["start"] == 0
    assert samples[0]["relations"][0]["type"] == "treatment_for"
    assert samples[1]["entities"][0]["text"] == "APOE"
    assert samples[1]["relations"] == []

