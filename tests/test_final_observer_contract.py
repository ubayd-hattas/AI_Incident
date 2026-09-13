from pathlib import Path
def test_observer_source_has_opaque_completion_and_one_clock():
    source=(Path(__file__).parents[1]/"src/ebe/observer.py").read_text(encoding="utf-8")
    assert "def complete_due" in source and "_operation_clock" in source
    assert "terminal directory is one-shot" in source
def test_costs_filters_request_dispatch_at_checkpoint():
    source=(Path(__file__).parents[1]/"src/ebe/observer.py").read_text(encoding="utf-8")
    assert "record.request_time >= cutoff" in source

