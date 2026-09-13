from pathlib import Path
import sys
from types import SimpleNamespace
from ebe.collectors import PeriodicConfig,PeriodicPolicy,EventDerivedConfig
from ebe.terminal_archive import run_archive_only, run_final_state_only
ROOT=Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT/"tests"))
from test_observer import SyntheticObserverTests, dt
from test_collectors import PeriodicCollectorTests
def test_repair_and_order_configs_exist():
    assert PeriodicPolicy.PCD_R.value=="PCD-R"
    assert PeriodicConfig(PeriodicPolicy.PCD_R,60_000_000,service_order="reverse").service_order=="reverse"
    assert EventDerivedConfig(30,reverse_title_ties=True).reverse_title_ties
def test_terminal_archive_is_nonsemantic_and_sequence_aware():
    source=(Path(__file__).parents[1]/"src/ebe/terminal_archive.py").read_text(encoding="utf-8")
    assert "request_seq_start" in source and "archive_key" in source
    assert "critical_only" not in source and "evidence_id" not in source

def test_f_hand_counted_directory_get_and_cost():
    SyntheticObserverTests.setUpClass()
    helper=SyntheticObserverTests()
    revision=helper.revision("ALPHA","1",dt("2026-05-24T00:00:10Z"),b"alpha")
    control=run_final_state_only(helper.observer([helper.save(revision)],[revision]))
    assert control.directory_requests==1 and len(control.attempts)==1
    assert control.request_attempts==2 and control.known_body_bytes==5

def test_archive_only_seq1_and_duplicate_body_gets_are_charged():
    SyntheticObserverTests.setUpClass()
    helper=SyntheticObserverTests()
    a=helper.revision("A","1",dt("2026-05-24T00:00:10Z"),b"same")
    b=helper.revision("B","1",dt("2026-05-24T00:00:20Z"),b"same")
    control=run_archive_only(SimpleNamespace(revisions=(a,b)),capacity_bytes=None)
    assert [x.request_seq for x in control.attempts]==[1,2]
    assert control.known_body_bytes==8
    assert control.retained.accounting.retained_body_objects==1

def test_pcdr_repairs_evicted_title_without_shared_provenance():
    PeriodicCollectorTests.setUpClass()
    helper=PeriodicCollectorTests()
    when=dt("2026-05-24T00:00:10Z")
    a=helper.revision("A","1",when,b"x")
    b=helper.revision("B","1",when,b"x")
    result=helper.collect(PeriodicPolicy.PCD_R,[helper.save(a),helper.save(b)],[a,b],
                          interval_minutes=1,capacity=170,
                          checkpoint="2026-05-24T00:04:00Z")
    assert result.observer_costs.body_requests>2
    assert result.repair_metadata_peak_bytes is not None
