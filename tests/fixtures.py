def sample_dataset():
    return {
        "train": [
            {
                "doc_id": "1",
                "sent_id": "1_s0",
                "text": "18F-FDG PET helps diagnose focal dementia.",
                "entities": [
                    {
                        "id": "T1",
                        "type": "method",
                        "start": 0,
                        "end": 11,
                        "text": "18F-FDG PET",
                    },
                    {
                        "id": "T2",
                        "type": "disease",
                        "start": 27,
                        "end": 41,
                        "text": "focal dementia",
                    },
                ],
                "relations": [
                    {
                        "type": "help_diagnose",
                        "head": {
                            "id": "T1",
                            "type": "method",
                            "start": 0,
                            "end": 11,
                            "text": "18F-FDG PET",
                        },
                        "tail": {
                            "id": "T2",
                            "type": "disease",
                            "start": 27,
                            "end": 41,
                            "text": "focal dementia",
                        },
                    }
                ],
            }
        ],
        "dev": [],
        "test": [],
    }

