from datetime import timedelta
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "tests"))

from ebe.observer import ObserverError, ObserverTimeError, PendingBodyRequest
from test_observer import SyntheticObserverTests, dt


def test_delayed_response_is_opaque_until_due_completion():
    SyntheticObserverTests.setUpClass()
    helper = SyntheticObserverTests()
    revision = helper.revision("OPAQUE", "1", dt("2026-05-24T00:00:10Z"), b"private")
    observer = helper.observer([helper.save(revision)], [revision], delay_us=30_000_000)
    observer.poll_feed(dt("2026-05-24T00:01:00Z"))
    pending = observer.get_body("dse~OPAQUE", dt("2026-05-24T00:01:00Z"))
    assert isinstance(pending, PendingBodyRequest)
    assert observer.complete_due(dt("2026-05-24T00:01:29Z")) == ()
    completed = observer.complete_due(dt("2026-05-24T00:01:30Z"))
    assert len(completed) == 1 and completed[0].body == b"private"


def test_single_causal_clock_rejects_backdated_operations_and_terminal_reuse():
    SyntheticObserverTests.setUpClass()
    helper = SyntheticObserverTests()
    observer = helper.observer([], [])
    observer.poll_feed(dt("2026-05-24T00:02:00Z"))
    with pytest.raises(ObserverTimeError):
        observer.get_body("dse~A", dt("2026-05-24T00:01:00Z"))

    terminal = helper.observer([], [])
    terminal.terminal_directory(dt("2026-07-15T00:00:00Z"))
    with pytest.raises(ObserverError):
        terminal.terminal_directory(dt("2026-07-15T00:00:00Z"))
