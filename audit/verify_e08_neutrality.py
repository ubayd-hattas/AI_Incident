"""Independent E08 neutrality/leakage audit.

Builds small synthetic exports directly as schema dataclasses (bypassing the
E05 loader entirely) to run controlled adversarial probes against the real
`Observer`/`CaptureStore` implementation. Also independently re-derives
canonical serialization from the R04 amendment text (not by importing
`accounting.canonical_jsonl` as ground truth) and cross-checks the two agree.

This script DOES import `ebe` (unlike audit/independent_replay.py) because
the object being audited here is the E08 code itself -- the point is to
drive the real Observer/CaptureStore through adversarial inputs, not to
build a parallel reference model of E08. Where a check needs a truly
independent computation (canonical serialization, FIFO arithmetic), a
from-scratch implementation is used and compared against the real code's
output, not substituted for it.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from ebe.schema import (  # noqa: E402
    BodyEncoding, EventRecord, ExportedEventType, ExportFingerprint,
    LabelRecord, ManifestRecord, NormalizedExport, ObservedEventSemantics,
    PageRecord, RelationFields, RelationValue, RelationValueForm,
    RevisionRecord, SourceLocation, SourceTimestamp,
)
from ebe.observer import BodyOutcome, Observer, ObserverConfig  # noqa: E402
from ebe.storage import Capture, CaptureStore  # noqa: E402
from ebe.timeline import HORIZON_START  # noqa: E402

FAILURES: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    status = "PASS" if cond else "FAIL"
    print(f"  {status} {label}" + (f" -- {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(f"{label}: {detail}")


SRC = SourceLocation(Path("synthetic"), None, None)


def ts(iso: str) -> SourceTimestamp:
    return SourceTimestamp(iso, datetime.fromisoformat(iso.replace("Z", "+00:00")))


def dt(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


_no_relation = RelationFields(
    RelationValue(RelationValueForm.NULL, None),
    RelationValue(RelationValueForm.NULL, None),
    RelationValue(RelationValueForm.NULL, None),
    (),
)


def make_revision(rev_id: str, page_key: str, name: str, time_iso: str, body: str, seq: int) -> RevisionRecord:
    body_bytes = body.encode("utf-8")
    t = ts(time_iso)
    return RevisionRecord(
        source=SRC, raw={}, rev_id=rev_id, page_id=f"dse/{name}", page_key=page_key, wiki="dse", name=name,
        seq=seq, rcs_rev="1.1", rcs_path="synthetic", body=body, source_body_bytes=body_bytes,
        body_len=len(body_bytes), body_sha256=hashlib.sha256(body_bytes).hexdigest(), body_encoding=BodyEncoding.UTF8,
        lines=1, diff_base=None, diff_base_reason="page_created" if seq == 1 else None, hunks=(),
        label="TestLabel", ip16="0.0", time=t, time_grade="reqlog", winning_clock="revision.pref_ts",
        uncertainty_seconds=1, request_time=t, success_time=t, recent_changes_time=None,
        write_date=t, archived_at=t, request_action="form_edit", change_summary=None, relations=_no_relation,
    )


def make_save_event(event_id: str, page_key: str, page: str, time_iso: str, rev_id: str) -> EventRecord:
    return EventRecord(
        source=SRC, raw={}, present_fields=frozenset(), event_id=event_id, event_type=ExportedEventType.SAVE,
        observed_semantics=ObservedEventSemantics.HELD_BODY_SAVE, time=ts(time_iso), time_grade="reqlog",
        wiki="dse", page=page, page_key=page_key, revision_ref=rev_id, winning_clock=None, uncertainty_seconds=None,
        request_time=None, success_time=None, write_date=None, recent_changes_time=None, rcs_date=None,
        clock_delta_seconds=None, clock_note=None, success_observed=None, request_action=None, change_summary=None,
        actor_label=None, ip16=None, page_held=None, param_family=None, source_refs=(), relations=_no_relation,
    )


def make_delete_event(event_id: str, page_key: str, page: str, time_iso: str) -> EventRecord:
    t = ts(time_iso)
    return EventRecord(
        source=SRC, raw={}, present_fields=frozenset(), event_id=event_id, event_type=ExportedEventType.DELETE,
        observed_semantics=ObservedEventSemantics.SUCCESSFUL_DELETION, time=t, time_grade="reqlog",
        wiki="dse", page=page, page_key=page_key, revision_ref=None, winning_clock="rclog.unix_ts",
        uncertainty_seconds=1, request_time=t, success_time=t, write_date=None, recent_changes_time=None,
        rcs_date=None, clock_delta_seconds=0, clock_note=None, success_observed=True, request_action="delete",
        change_summary="Seite geloescht.", actor_label="[Admin1]", ip16="0.0", page_held=True, param_family=None,
        source_refs=(), relations=_no_relation,
    )


def make_bodyunknown_event(event_id: str, page_key: str, page: str, time_iso: str) -> EventRecord:
    t = ts(time_iso)
    return EventRecord(
        source=SRC, raw={}, present_fields=frozenset(), event_id=event_id, event_type=ExportedEventType.REVERT,
        observed_semantics=ObservedEventSemantics.BODY_UNKNOWN_FORM_EDIT, time=t, time_grade="reqlog",
        wiki="dse", page=page, page_key=page_key, revision_ref=None, winning_clock="rclog.unix_ts",
        uncertainty_seconds=1, request_time=t, success_time=t, write_date=None, recent_changes_time=None,
        rcs_date=None, clock_delta_seconds=0, clock_note=None, success_observed=True, request_action="form_edit",
        change_summary="Seite geloescht.", actor_label="[Admin1]", ip16="0.0", page_held=True, param_family=None,
        source_refs=(), relations=_no_relation,
    )


def make_export(revisions: list[RevisionRecord], events: list[EventRecord]) -> NormalizedExport:
    manifest = ManifestRecord(
        source=SRC, raw={}, generated_at=ts("2026-05-24T00:00:00.000000Z"), db_sha256="synthetic",
        cut={}, counts={}, per_wiki={}, population_counts={}, grade_histograms={}, body_bytes={},
        body_encoding={}, page_family_coverage={}, facts={}, recreation_source={}, resources={},
        tool_versions={}, source_scan={}, request_source_note="", checks=(),
    )
    fingerprint = ExportFingerprint(sha256={}, row_counts={})
    return NormalizedExport(
        (), tuple(revisions), tuple(events), (), manifest, fingerprint,
        {}, {}, {r.rev_id: r for r in revisions}, {e.event_id: e for e in events}, {},
    )


# ---------------------------------------------------------------------------
print("=== Q7: canonical serialization -- independent re-derivation ===")


def independent_canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8") + b"\n"


from ebe.accounting import canonical_jsonl, canonical_array  # noqa: E402

probes = [
    {"action": "live_change", "event_time": "2026-05-24T00:00:00.000000Z", "page_key": "dse~A"},
    {"outcome": "body"},
    {"body_sha256": "4a99557e4033c3539de2eb65472017cad5f9557f7a0625a09f1c3f6e2ba69c4c", "capture_time": "2026-05-24T00:00:00.000000Z", "page_key": "dse~é", "request_seq": 10},
    {"z": None, "flag": False, "n": 10, "s": "é\n\"\\"},
]
for p in probes:
    check(f"canonical_jsonl matches independent derivation for {p}", canonical_jsonl(p) == independent_canonical(p))
check("canonical_array matches independent list framing", canonical_array(["dse~A", "dse~é"]) == independent_canonical(["dse~A", "dse~é"]))

# ---------------------------------------------------------------------------
print("=== Q1: feed record field exposure ===")
rev1 = make_revision("dse~A@1", "dse~A", "A", "2026-05-24T00:01:00.000000Z", "hello", 1)
ev1 = make_save_event("save:dse~A@1", "dse~A", "A", "2026-05-24T00:01:00.000000Z", "dse~A@1")
export1 = make_export([rev1], [ev1])
obs = Observer(export1)
result = obs.poll_feed(HORIZON_START + timedelta(seconds=120))  # well past event_time(60s)+default 5s lag
rec = result.records[0]
d = rec.as_dict()
check("feed record has exactly {action,event_time,page_key}", set(d.keys()) == {"action", "event_time", "page_key"}, str(d.keys()))
check("no body/hash/revision_id/relation attribute exists on FeedRecord", not hasattr(rec, "body") and not hasattr(rec, "revision_ref") and not hasattr(rec, "relations"))

# ---------------------------------------------------------------------------
print("=== Q3: publication lag boundary (exact edge, landing on a scheduled poll) ===")
# event_time chosen so event_time + lag lands EXACTLY on a scheduled poll instant
# (HORIZON_START + 60s), so we can test the <= boundary precisely rather than
# just "eventually shows up."
event_time = HORIZON_START + timedelta(seconds=55)
rev2 = make_revision("dse~B@1", "dse~B", "B", event_time.isoformat().replace("+00:00", ".000000Z"), "x", 1)
ev2 = make_save_event("save:dse~B@1", "dse~B", "B", event_time.isoformat().replace("+00:00", ".000000Z"), "dse~B@1")
export2 = make_export([rev2], [ev2])
obs2 = Observer(export2, config=ObserverConfig(feed_publication_lag_us=5_000_000))
r_before = obs2.poll_feed(HORIZON_START)  # t0, one scheduled interval before publication_time
r_at = obs2.poll_feed(HORIZON_START + timedelta(seconds=60))  # exactly == event_time + 5s lag
check("record NOT visible on the scheduled poll strictly before its publication boundary", len(r_before.records) == 0)
check("record visible exactly AT publication_time == event_time + lag (closed/<= boundary)", len(r_at.records) == 1)

# ---------------------------------------------------------------------------
print("=== Q2: no future-title discovery via GET ===")
obs4 = Observer(export2, config=ObserverConfig(feed_publication_lag_us=5_000_000))
resp = obs4.get_body("dse~B", event_time)  # GET before any feed poll has ever run
check("GET on an undiscovered (never-polled) page returns UNKNOWN, not real state", resp.outcome is BodyOutcome.UNKNOWN, str(resp.outcome))
check("undiscovered GET does not leak the body even though the save already happened", resp.body is None)

# ---------------------------------------------------------------------------
print("=== Q5: cannot retrieve an overwritten trigger body retrospectively ===")
# NOTE: this test previously dispatched GETs at request_time=t1 *after* a poll
# already at t2+120s -- i.e. a GET timestamped before a poll that had already
# happened. That is exactly the causal-ordering violation X02 identified and
# Observer.get_body now correctly rejects (a real collector never does this;
# dispatch is always causally ordered after the polls that discovered a page).
# Rewritten to dispatch causally (request_time == the poll that just ran, or
# later), while still testing the same property via response delay alone.
t1 = HORIZON_START + timedelta(seconds=600)
t2 = t1 + timedelta(seconds=60)
revA1 = make_revision("dse~C@1", "dse~C", "C", t1.isoformat().replace("+00:00", ".000000Z"), "OLD_BODY", 1)
revA2 = make_revision("dse~C@2", "dse~C", "C", t2.isoformat().replace("+00:00", ".000000Z"), "NEW_BODY", 2)
evA1 = make_save_event("save:dse~C@1", "dse~C", "C", t1.isoformat().replace("+00:00", ".000000Z"), "dse~C@1")
evA2 = make_save_event("save:dse~C@2", "dse~C", "C", t2.isoformat().replace("+00:00", ".000000Z"), "dse~C@2")
export3 = make_export([revA1, revA2], [evA1, evA2])
obs5 = Observer(export3, config=ObserverConfig(feed_publication_lag_us=0, get_response_delay_us=0))
obs5.poll_feed(t1)  # discover the page exactly at the first save's own time, causally
r_at_trigger = obs5.get_body("dse~C", t1)  # dispatched AT the poll that discovered it -- causally valid
check("GET dispatched at the first trigger's own time sees the body current AT THAT TIME (old), not the future replacement", r_at_trigger.body == b"OLD_BODY", str(r_at_trigger.body))
# Now dispatch a second GET, still causally ordered (request_time == the poll
# that discovered the page, no earlier), but with a response delay pushing its
# OWN response_time past t2 -- this must see NEW_BODY, proving the observer
# never returns a cached/trigger-tied old body once time has moved past the
# overwrite, i.e. no retrospective replay of a stale capture.
obs6 = Observer(export3, config=ObserverConfig(feed_publication_lag_us=0, get_response_delay_us=int((t2 - t1).total_seconds() * 1_000_000) + 1_000_000))
obs6.poll_feed(t1)
r_after_overwrite = obs6.get_body("dse~C", t1)  # dispatched causally at t1, but its OWN delay lands the response after t2
r_after_overwrite = obs6.complete_due(r_after_overwrite.response_time)[0]
check("GET whose response completes AFTER an overwrite sees the NEW body, never the stale trigger body", r_after_overwrite.body == b"NEW_BODY", str(r_after_overwrite.body))

# ---------------------------------------------------------------------------
print("=== Q6: consistent charging of failed/unknown/pending requests ===")
t3 = HORIZON_START + timedelta(seconds=900)
revD = make_revision("dse~D@1", "dse~D", "D", t3.isoformat().replace("+00:00", ".000000Z"), "D_BODY", 1)
evD_save = make_save_event("save:dse~D@1", "dse~D", "D", t3.isoformat().replace("+00:00", ".000000Z"), "dse~D@1")
evD_delete = make_delete_event("delete:dse~D", "dse~D", "D", (t3 + timedelta(seconds=10)).isoformat().replace("+00:00", ".000000Z"))
export4 = make_export([revD], [evD_save, evD_delete])
obs7 = Observer(export4, config=ObserverConfig(feed_publication_lag_us=0))
obs7.poll_feed(t3)  # causally valid: no GET below is dispatched earlier than this poll
before_costs = obs7.costs()
r_body = obs7.get_body("dse~D", t3)  # BODY
r_missing = obs7.get_body("dse~D", t3 + timedelta(seconds=20))  # MISSING (deleted)
r_unknown_page = obs7.get_body("dse~ZZZ_never_discovered", t3 + timedelta(seconds=20))  # UNKNOWN (never discovered)
after_costs = obs7.costs()
check("every GET dispatch increments body_requests regardless of outcome", after_costs.body_requests - before_costs.body_requests == 3)
check("BODY outcome recorded", r_body.outcome is BodyOutcome.BODY)
check("MISSING outcome recorded for a deleted page", r_missing.outcome is BodyOutcome.MISSING)
check("UNKNOWN outcome recorded for an undiscovered page", r_unknown_page.outcome is BodyOutcome.UNKNOWN)
check("downloaded_metadata increased by exactly 3 headers", after_costs.downloaded_metadata_bytes - before_costs.downloaded_metadata_bytes == len(canonical_jsonl({"outcome": "body"})) + len(canonical_jsonl({"outcome": "missing"})) + len(canonical_jsonl({"outcome": "unknown"})))
check("unknown_body_byte_attempts counts the UNKNOWN response but not MISSING", after_costs.unknown_body_byte_attempts - before_costs.unknown_body_byte_attempts == 1)
check("downloaded_total_bytes is NA (None) once any unknown-byte attempt exists", after_costs.downloaded_total_bytes is None)

# pending (response after T)
from ebe.timeline import HORIZON_END  # noqa: E402
obs8 = Observer(export4, config=ObserverConfig(feed_publication_lag_us=0, get_response_delay_us=999_000_000_000))
obs8.poll_feed(t3 + timedelta(seconds=120))
pending_before = obs8.costs()
p = obs8.get_body("dse~D", HORIZON_END - timedelta(microseconds=1))
pending_after = obs8.costs()
check("a request that will complete after T is counted in body_requests at dispatch", pending_after.body_requests - pending_before.body_requests == 1)
check("a pending request charges no metadata/body bytes before T", pending_after.downloaded_metadata_bytes == pending_before.downloaded_metadata_bytes and pending_after.downloaded_known_body_bytes == pending_before.downloaded_known_body_bytes)
check("pending_body_requests reflects the pending dispatch", pending_after.pending_body_requests - pending_before.pending_body_requests == 1)

# ---------------------------------------------------------------------------
print("=== Q14: prefix invariance under different future suffixes ===")
t4 = HORIZON_START + timedelta(seconds=1200)
revE1 = make_revision("dse~E@1", "dse~E", "E", t4.isoformat().replace("+00:00", ".000000Z"), "E1", 1)
evE1 = make_save_event("save:dse~E@1", "dse~E", "E", t4.isoformat().replace("+00:00", ".000000Z"), "dse~E@1")
common_cutoff = t4 + timedelta(seconds=60)  # == the shared poll time below, so costs(checkpoint=...) is valid
# Suffix A: nothing more happens.
export_suffix_a = make_export([revE1], [evE1])
# Suffix B: a second save happens well AFTER the common cutoff.
t5 = common_cutoff + timedelta(seconds=500)
revE2 = make_revision("dse~E@2", "dse~E", "E", t5.isoformat().replace("+00:00", ".000000Z"), "E2", 2)
evE2 = make_save_event("save:dse~E@2", "dse~E", "E", t5.isoformat().replace("+00:00", ".000000Z"), "dse~E@2")
export_suffix_b = make_export([revE1, revE2], [evE1, evE2])

obs_a = Observer(export_suffix_a, config=ObserverConfig(feed_publication_lag_us=0))
obs_b = Observer(export_suffix_b, config=ObserverConfig(feed_publication_lag_us=0))
poll_a1 = obs_a.poll_feed(t4 + timedelta(seconds=60))
poll_b1 = obs_b.poll_feed(t4 + timedelta(seconds=60))
check("identical feed poll response bytes through the common prefix regardless of future suffix", poll_a1.response_bytes == poll_b1.response_bytes)
get_a = obs_a.get_body("dse~E", common_cutoff)
get_b = obs_b.get_body("dse~E", common_cutoff)
check("identical GET outcome/body at a common-prefix timestamp regardless of future suffix", (get_a.outcome, get_a.body) == (get_b.outcome, get_b.body))
costs_a = obs_a.costs(checkpoint=common_cutoff)
costs_b = obs_b.costs(checkpoint=common_cutoff)
check("identical accrued costs at the common cutoff regardless of future suffix", costs_a.downloaded_metadata_bytes == costs_b.downloaded_metadata_bytes and costs_a.shared_metadata_byte_microseconds == costs_b.shared_metadata_byte_microseconds)

# ---------------------------------------------------------------------------
print("=== terminal_directory: mutual exclusivity with continuous feed ===")
obs9 = Observer(export_suffix_a, config=ObserverConfig(feed_publication_lag_us=0))
obs9.poll_feed(t4 + timedelta(seconds=60))
try:
    obs9.terminal_directory()
    check("terminal_directory refuses to run after any feed poll has occurred", False, "no exception raised")
except Exception as exc:
    check("terminal_directory refuses to run after any feed poll has occurred", True)

obs10 = Observer(export_suffix_a, config=ObserverConfig(feed_publication_lag_us=0))
directory = obs10.terminal_directory()
check("terminal_directory on a fresh observer (no feed use) succeeds and returns modeled live keys", "dse~E" in directory.page_keys)

# ---------------------------------------------------------------------------
print("=== Q8/Q9/Q10: real CaptureStore reproduces fixtures B-G exactly ===")
FIXTURES = REPO / "tests" / "fixtures" / "accounting"


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def run_real_store(canonical_packets, bodies_hex, cap, dedup):
    store = CaptureStore(cap, deduplicate=dedup)
    for pkt_str, body_hex in zip(canonical_packets, bodies_hex):
        pkt = json.loads(pkt_str)
        capture = Capture(pkt["page_key"], dt(pkt["capture_time"]), pkt["request_seq"], bytes.fromhex(body_hex))
        assert capture.body_sha256 == pkt["body_sha256"], "fixture packet hash does not match recomputed body hash"
        store.admit(capture)
    # Use the store's OWN recorded size_history (includes each intermediate
    # eviction step, not just post-admission snapshots) rather than an
    # external tracker -- the fixtures' operation lists include eviction
    # steps as separate points.
    return store, list(store.size_history)


b = load("B_unique.json")
capB = Capture("dse~A", dt("2026-05-24T00:00:00.000000Z"), 1, bytes.fromhex(b["body_utf8_hex"]))
storeB = CaptureStore(b["capacity_bytes"], deduplicate=b["deduplicate"])
resB = storeB.admit(capB)
snapB = storeB.snapshot()
check("B: real CaptureStore final_store_bytes matches fixture", snapB.final_store_bytes == b["expected"]["final_store_bytes"])
check("B: real CaptureStore packet_bytes matches fixture", resB.packet_bytes == b["expected"]["packet_bytes"])

for name, letter in [("C_duplicate.json", "C"), ("D_nondedup.json", "D"), ("E_fifo.json", "E"), ("G_shared_fifo.json", "G")]:
    fx = load(name)
    bodies = fx.get("body_utf8_hex_in_request_order") or [fx.get("body_utf8_hex")] * len(fx["canonical_packets"])
    store, history = run_real_store(fx["canonical_packets"], bodies, fx["capacity_bytes"], fx["deduplicate"])
    snap = store.snapshot()
    check(f"{letter}: real CaptureStore store_bytes_after_operations matches fixture", history == fx["expected"]["store_bytes_after_operations"], f"got {history} expected {fx['expected']['store_bytes_after_operations']}")
    check(f"{letter}: real CaptureStore final_store_bytes matches fixture", snap.final_store_bytes == fx["expected"]["final_store_bytes"])
    check(f"{letter}: real CaptureStore peak_store_bytes matches fixture", snap.peak_store_bytes == fx["expected"]["peak_store_bytes"])
    check(f"{letter}: real CaptureStore retained_request_seqs matches fixture", list(snap.retained_request_seqs) == fx["expected"]["retained_request_seqs"])
    check(f"{letter}: real CaptureStore object_reference_counts matches fixture", list(snap.object_reference_counts) == fx["expected"]["object_reference_counts"])

fx = load("F_oversize.json")
store = CaptureStore(fx["capacity_bytes"], deduplicate=fx["deduplicate"])
results = []
for pkt_str, body_hex in zip(fx["canonical_packets"], fx["body_utf8_hex_in_request_order"]):
    pkt = json.loads(pkt_str)
    capture = Capture(pkt["page_key"], dt(pkt["capture_time"]), pkt["request_seq"], bytes.fromhex(body_hex))
    res = store.admit(capture)
    results.append(res.disposition)
snap = store.snapshot()
history = list(store.size_history)
check("F: real CaptureStore admission_results matches fixture", results == fx["expected"]["admission_results"])
check("F: real CaptureStore store_bytes_after_operations matches fixture", history == fx["expected"]["store_bytes_after_operations"])
check("F: real CaptureStore final_store_bytes matches fixture", snap.final_store_bytes == fx["expected"]["final_store_bytes"])

print("\n" + "=" * 50)
print(f"TOTAL FAILURES: {len(FAILURES)}")
for f in FAILURES:
    print("  -", f)

# ---------------------------------------------------------------------------
print("=== Adversarial: genuine ambiguity must surface as AMBIGUOUS, never a silently-picked body ===")
t_tie = HORIZON_START + timedelta(seconds=1800)
tie_iso = t_tie.isoformat().replace("+00:00", ".000000Z")
revF1 = make_revision("dse~F@1", "dse~F", "F", tie_iso, "FIRST", 1)
revF2 = make_revision("dse~F@2", "dse~F", "F", tie_iso, "SECOND", 2)
evF1 = make_save_event("save:dse~F@1", "dse~F", "F", tie_iso, "dse~F@1")
evF2 = make_save_event("save:dse~F@2", "dse~F", "F", tie_iso, "dse~F@2")
export_tie = make_export([revF1, revF2], [evF1, evF2])
obs_tie = Observer(export_tie, config=ObserverConfig(feed_publication_lag_us=0))
obs_tie.poll_feed(t_tie)  # causally valid: GET below is not dispatched earlier than this poll
resp_tie = obs_tie.get_body("dse~F", t_tie)
check("a genuine same-timestamp tie surfaces as AMBIGUOUS", resp_tie.outcome is BodyOutcome.AMBIGUOUS, str(resp_tie.outcome))
check("AMBIGUOUS response carries no body (no silent winner, no union)", resp_tie.body is None)

print("\n" + "=" * 50)
print(f"FINAL TOTAL FAILURES: {len(FAILURES)}")
for f in FAILURES:
    print("  -", f)
