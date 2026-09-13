from pathlib import Path
from datetime import timedelta
import sys
from types import SimpleNamespace
from ebe.collectors import PeriodicConfig,PeriodicPolicy,EventDerivedConfig
from ebe.terminal_archive import archive_entries, run_archive_only, run_final_state_only
ROOT=Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT/"tests"))
from test_observer import SyntheticObserverTests, dt
from test_collectors import PeriodicCollectorTests
def test_repair_and_order_configs_exist():
    assert PeriodicPolicy.PCD_R.value=="PCD-R"
    assert PeriodicConfig(PeriodicPolicy.PCD_R,60_000_000,service_order="reverse").service_order=="reverse"
    assert EventDerivedConfig(30,reverse_title_ties=True).reverse_title_ties
def test_terminal_archive_enumerates_all_source_revisions_in_frozen_order():
    SyntheticObserverTests.setUpClass()
    helper=SyntheticObserverTests()
    later=helper.revision("Z", "2", dt("2026-05-24T00:00:20Z"), b"later")
    earlier=helper.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"earlier")
    assert archive_entries(SimpleNamespace(revisions=(later, earlier))) == (earlier, later)

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


def test_pcdr_pending_request_suppresses_duplicate_repair_until_completion():
    PeriodicCollectorTests.setUpClass()
    helper=PeriodicCollectorTests()
    a=helper.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"aaaa")
    b=helper.revision("B", "1", dt("2026-05-24T00:01:10Z"), b"bbbb")
    result=helper.collect(PeriodicPolicy.PCD_R,[helper.save(a),helper.save(b)],[a,b],
        interval_minutes=1,capacity=170,delay_us=30_000_000,
        checkpoint="2026-05-24T00:05:00Z")
    a_requests=[x for x in result.body_results if x.page_key=="dse~A"]
    assert [x.request_time for x in a_requests] == [
        dt("2026-05-24T00:01:00Z"), dt("2026-05-24T00:03:00Z")]
    assert all(x.response_time == x.request_time + timedelta(seconds=30) for x in a_requests)


def test_pcdr_unavailable_completion_disables_repair_until_new_known_completion():
    PeriodicCollectorTests.setUpClass()
    helper=PeriodicCollectorTests()
    known=helper.revision("A", "1", dt("2026-05-24T00:00:10Z"), b"known")
    unknown=helper.body_unknown("A", dt("2026-05-24T00:01:10Z"))
    result=helper.collect(PeriodicPolicy.PCD_R,[helper.save(known),unknown],[known],
        interval_minutes=1,capacity=1,delay_us=30_000_000,
        checkpoint="2026-05-24T00:05:00Z")
    requests=[x for x in result.body_results if x.page_key=="dse~A"]
    assert len(requests) == 2
    assert requests[-1].outcome.value == "body_unknown"


def test_pcdr_primary_zero_delay_behavior_is_unchanged():
    PeriodicCollectorTests.setUpClass()
    helper=PeriodicCollectorTests()
    when=dt("2026-05-24T00:00:10Z")
    a=helper.revision("A", "1", when, b"x")
    b=helper.revision("B", "1", when, b"x")
    result=helper.collect(PeriodicPolicy.PCD_R,[helper.save(a),helper.save(b)],[a,b],
        interval_minutes=1,capacity=170,checkpoint="2026-05-24T00:04:00Z")
    assert [(x.request_seq,x.page_key,x.request_time,x.response_time) for x in result.body_results] == [
        (1,"dse~A",dt("2026-05-24T00:01:00Z"),dt("2026-05-24T00:01:00Z")),
        (2,"dse~B",dt("2026-05-24T00:01:00Z"),dt("2026-05-24T00:01:00Z")),
        (3,"dse~A",dt("2026-05-24T00:02:00Z"),dt("2026-05-24T00:02:00Z")),
        (4,"dse~B",dt("2026-05-24T00:03:00Z"),dt("2026-05-24T00:03:00Z")),
    ]
