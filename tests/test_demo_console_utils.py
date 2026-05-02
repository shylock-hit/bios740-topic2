from bios740_topic2.demo_console_utils import estimate_eta_from_progress


def test_estimate_eta_uses_recent_window():
    progress = {"processed": 6, "total": 10, "avg_latency_seconds": 20.0}
    rows = [
        {"latency_seconds": 10.0},
        {"latency_seconds": 12.0},
        {"latency_seconds": 18.0},
        {"latency_seconds": 20.0},
        {"latency_seconds": 30.0},
        {"latency_seconds": 40.0},
    ]

    eta = estimate_eta_from_progress(progress, rows, window_size=3)

    assert eta["remaining"] == 4
    assert round(eta["recent_avg_latency_seconds"], 2) == 30.0
    assert round(eta["eta_seconds"], 2) == 120.0
    assert eta["source"] == "recent_window"


def test_estimate_eta_falls_back_to_overall_average():
    progress = {"processed": 1, "total": 5, "avg_latency_seconds": 11.0}
    rows = [{"latency_seconds": 7.0}]

    eta = estimate_eta_from_progress(progress, rows, window_size=5)

    assert eta["remaining"] == 4
    assert eta["recent_avg_latency_seconds"] == 11.0
    assert eta["eta_seconds"] == 44.0
    assert eta["source"] == "overall_average"
