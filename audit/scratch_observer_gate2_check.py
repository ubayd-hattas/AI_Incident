"""Gate 2 adversarial verification scratch script for observer/storage/accounting.

Throwaway script. Builds small synthetic histories NOT copied from any existing
test fixture. Every expected value is computed by hand and written down as a
literal/comment BEFORE the call that would reveal the real value, per project
hand-scoring discipline. Prints a PASS/FAIL table line per check.
"""
from __future__ import annotations

import dataclasses
import hashlib
import sys
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ebe.accounting import canonical_jsonl, synchronized_accounting  # noqa: E402
from ebe.observer import (  # noqa: E402
    BodyOutcome,
    BodyResponse,
    DirectoryAmbiguityError,
    Observer,
    ObserverConfig,
    ObserverError,
    ObserverTimeError,
    PendingBodyRequest,
    PollScheduleError,
)
from ebe.schema import (  # noqa: E402
    BodyEncoding, EventRecord, ExportedEventType, ExportFingerprint,
    ManifestRecord, NormalizedExport, ObservedEventSemantics, RelationFields,
    RelationValue, RelationValueForm, RevisionRecord, SourceLocation, SourceTimestamp,
)
from ebe.storage import AdmissionOrderError, Capture, CaptureStore, HashCollisionError  # noqa: E402
from ebe.timeline import HORIZON_END, HORIZON_START  # noqa: E402

UTC = timezone.utc
SRC = SourceLocation(Path("synthetic-gate2"), None, None)
_NO_RELATION = RelationFields(
    RelationValue(RelationValueForm.NULL, None),
    RelationValue(RelationValueForm.NULL, None),
    RelationValue(RelationValueForm.NULL, None),
    (),
)

RESULTS: list[tuple[str, str]] = []  # (name, "PASS"/"FAIL: ...")


def report(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else f"FAIL {detail}"
    RESULTS.append((name, status))
    print(f"[{status}] {name}" + (f" -- {detail}" if detail and ok else ""))


def S(offset_seconds: int) -> datetime:
    return HORIZON_START + timedelta(seconds=offset_seconds)


def ts(d: datetime) -> SourceTimestamp:
    return SourceTimestamp(d.isoformat(), d)


def make_save_event(page_key: str, event_idx: int, when: datetime, body: str, seq: int):
    t = ts(when)
    rev_id = f"rev~{page_key}~{seq}"
    body_bytes = body.encode("utf-8")
    rev = RevisionRecord(
        source=SRC, raw={}, rev_id=rev_id, page_id=f"id/{page_key}", page_key=page_key,
        wiki="dse", name=page_key, seq=seq, rcs_rev="1.1", rcs_path="synthetic", body=body,
        source_body_bytes=body_bytes, body_len=len(body_bytes),
        body_sha256=hashlib.sha256(body_bytes).hexdigest(), body_encoding=BodyEncoding.UTF8,
        lines=1, diff_base=None, diff_base_reason="page_created" if seq == 1 else None, hunks=(),
        label="L", ip16="0.0", time=t, time_grade="reqlog", winning_clock="revision.pref_ts",
        uncertainty_seconds=1, request_time=t, success_time=t, recent_changes_time=None,
        write_date=t, archived_at=t, request_action="form_edit", change_summary=None,
        relations=_NO_RELATION,
    )
    ev = EventRecord(
        source=SRC, raw={}, present_fields=frozenset(), event_id=f"save:{page_key}:{event_idx}",
        event_type=ExportedEventType.SAVE, observed_semantics=ObservedEventSemantics.HELD_BODY_SAVE,
        time=t, time_grade="reqlog", wiki="dse", page=page_key, page_key=page_key,
        revision_ref=rev_id, winning_clock=None, uncertainty_seconds=None, request_time=None,
        success_time=None, write_date=None, recent_changes_time=None, rcs_date=None,
        clock_delta_seconds=None, clock_note=None, success_observed=None, request_action=None,
        change_summary=None, actor_label=None, ip16=None, page_held=None, param_family=None,
        source_refs=(), relations=_NO_RELATION,
    )
    return ev, rev


def make_delete_event(page_key: str, event_idx: int, when: datetime):
    t = ts(when)
    ev = EventRecord(
        source=SRC, raw={}, present_fields=frozenset(), event_id=f"del:{page_key}:{event_idx}",
        event_type=ExportedEventType.DELETE, observed_semantics=ObservedEventSemantics.SUCCESSFUL_DELETION,
        time=t, time_grade="reqlog", wiki="dse", page=page_key, page_key=page_key,
        revision_ref=None, winning_clock="rclog.unix_ts", uncertainty_seconds=1, request_time=t,
        success_time=t, write_date=None, recent_changes_time=None, rcs_date=None,
        clock_delta_seconds=0, clock_note=None, success_observed=True, request_action="delete",
        change_summary="deleted.", actor_label="[Admin1]", ip16="0.0", page_held=True,
        param_family=None, source_refs=(), relations=_NO_RELATION,
    )
    return ev


def build_export(events, revisions) -> NormalizedExport:
    manifest = ManifestRecord(
        source=SRC, raw={}, generated_at=ts(HORIZON_START), db_sha256="synthetic",
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
# TEST 1: X01 causal accounting + fresh-prefix agreement (>=6 event history)
# ---------------------------------------------------------------------------
# History (6 mutation events across 3 pages), offsets in seconds from HORIZON_START:
#   e1: A save "a1"  @ 60
#   e2: B save "b1"  @120
#   e3: A delete     @180
#   e4: B save "b2"  @240
#   e5: B delete     @300
#   e6: C save "c1"  @360
e1, r1 = make_save_event("A", 1, S(60), "a1", 1)
e2, r2 = make_save_event("B", 2, S(120), "b1", 1)
e3 = make_delete_event("A", 3, S(180))
e4, r4 = make_save_event("B", 4, S(240), "b2", 2)
e5 = make_delete_event("B", 5, S(300))
e6, r6 = make_save_event("C", 6, S(360), "c1", 1)
EXPORT1 = build_export([e1, e2, e3, e4, e5, e6], [r1, r2, r4, r6])

# feed_publication_lag=5s (default), poll_interval=60s (default). Publication times:
# e1 pub=65, e2 pub=125, e3 pub=185, e4 pub=245, e5 pub=305, e6 pub=365.
# Poll schedule: 0,60,120,180,240,300,360,420,...
# poll@0:no visible; poll@60:no visible (65>60); poll@120: e1 visible (65<=120);
# poll@180: e2 visible (125<=180); poll@240: e3 visible (185<=240);
# poll@300: e4 visible (245<=300); poll@360: e5 visible (305<=360);
# poll@420: e6 visible (365<=420).
#
# GET dispatched on "A" at request_time=125s (after poll@120 revealed A is live),
# using get_response_delay_us=120_000_000 (120s) -> response_time=245s.
# At response_time=245, A's mutations: save@60 then delete@180 (both <=245)
# -> nominal final state = DELETED -> outcome MISSING, body None.
# Checkpoint C=200s: request_time(125) < C -> attempt counted.
#   response_time(245) > C(200) -> MUST show as pending as-of C, 0 bytes, 0 outcome.
CFG1 = ObserverConfig(get_response_delay_us=120_000_000)

# Ordered operation schedule in true causal time order (polls interleaved with the
# GET at its correct chronological slot, NOT all polls-then-GET):
OPS1 = [
    ("poll", 0), ("poll", 60), ("poll", 120),
    ("get", 125),
    ("poll", 180), ("poll", 240), ("poll", 300), ("poll", 360), ("poll", 420),
]


def run_full():
    obs = Observer(EXPORT1, config=CFG1)
    handle = None
    for kind, t in OPS1:
        if kind == "poll":
            obs.poll_feed(S(t))
        else:
            handle = obs.get_body("A", S(t))
    assert isinstance(handle, PendingBodyRequest), "GET with nonzero delay must return PendingBodyRequest"
    completions = obs.complete_due(S(500))
    return obs, handle, completions


def run_prefix(cutoff_s: int):
    obs = Observer(EXPORT1, config=CFG1)
    for kind, t in OPS1:
        if t > cutoff_s:
            continue
        if kind == "poll":
            obs.poll_feed(S(t))
        else:
            obs.get_body("A", S(t))
    obs.complete_due(S(cutoff_s))
    return obs


try:
    obs_full, handle, completions = run_full()
    costs_full_200 = obs_full.costs(S(200))

    # HAND-DERIVED expected costs(200) BEFORE looking at the numbers:
    EXPECT_FEED_REQUESTS_200 = 4       # polls at 0,60,120,180 (<=200)
    EXPECT_DIRECTORY_REQUESTS_200 = 0
    EXPECT_BODY_REQUESTS_200 = 1       # the A-GET dispatched at 125 (<200)
    EXPECT_PENDING_200 = 1             # response_time 245 > 200 -> pending
    EXPECT_BODY_OUTCOME_200 = 0        # not yet resolved as-of 200
    EXPECT_DOWNLOADED_BODY_200 = 0     # no invented bytes for the pending GET

    ok = (
        costs_full_200.feed_requests == EXPECT_FEED_REQUESTS_200
        and costs_full_200.directory_requests == EXPECT_DIRECTORY_REQUESTS_200
        and costs_full_200.body_requests == EXPECT_BODY_REQUESTS_200
        and costs_full_200.pending_body_requests == EXPECT_PENDING_200
        and costs_full_200.successful_body_responses == EXPECT_BODY_OUTCOME_200
        and costs_full_200.missing_responses == EXPECT_BODY_OUTCOME_200
        and costs_full_200.downloaded_known_body_bytes == EXPECT_DOWNLOADED_BODY_200
    )
    report(
        "X01: costs(200) hand-derived match (pending-after-C not leaked)",
        ok,
        f"got feed={costs_full_200.feed_requests} dir={costs_full_200.directory_requests} "
        f"body_req={costs_full_200.body_requests} pending={costs_full_200.pending_body_requests} "
        f"body_outcome={costs_full_200.successful_body_responses} missing={costs_full_200.missing_responses} "
        f"downloaded_body={costs_full_200.downloaded_known_body_bytes}",
    )

    # Fresh-prefix agreement: independently constructed prefix-only replay ending at C=200
    # must produce EXACTLY the same ObserverCosts as the full/longer run's costs(200).
    obs_prefix = run_prefix(200)
    costs_prefix_200 = obs_prefix.costs(S(200))
    report(
        "X01: fresh-prefix agreement costs(200) == truncated-replay costs(200)",
        costs_full_200 == costs_prefix_200,
        f"full={costs_full_200}\n    prefix={costs_prefix_200}",
    )

    # Completion later in the SAME full run reveals MISSING (deleted before response_time)
    assert len(completions) == 1
    revealed = completions[0]
    report(
        "X01: same-run later completion reveals MISSING (A deleted @180 < response @245)",
        isinstance(revealed, BodyResponse) and revealed.outcome is BodyOutcome.MISSING and revealed.body is None,
        f"outcome={revealed.outcome} body={revealed.body!r}",
    )

    # And costs() at a checkpoint AFTER the true response_time (245) must show it resolved.
    costs_full_300 = obs_full.costs(S(300))
    report(
        "X01: costs(300) resolves the same GET as MISSING (completion before C)",
        costs_full_300.missing_responses == 1 and costs_full_300.pending_body_requests == 0,
        f"missing={costs_full_300.missing_responses} pending={costs_full_300.pending_body_requests}",
    )
except Exception:
    report("X01 test block", False, traceback.format_exc())


# ---------------------------------------------------------------------------
# TEST 2: boundary asymmetry at C -- ordinary GET at C vs feed poll at C
# ---------------------------------------------------------------------------
# Fresh minimal export: one page "Z" saved at t=+60s, never deleted.
ez, rz = make_save_event("Z", 1, S(60), "z1", 1)
EXPORT2 = build_export([ez], [rz])

try:
    obs2 = Observer(EXPORT2, config=ObserverConfig())
    obs2.poll_feed(S(60))          # discovers Z (pub=65<=... wait: need >=65). Use t=120 instead.
except Exception:
    pass

try:
    obs2 = Observer(EXPORT2, config=ObserverConfig())
    obs2.poll_feed(S(0))
    obs2.poll_feed(S(60))
    p2 = obs2.poll_feed(S(120))   # pub(65)<=120 -> Z discovered here
    # dispatch a GET for Z exactly at the SAME instant as this poll (120s)
    resp = obs2.get_body("Z", S(120))
    assert isinstance(resp, BodyResponse)
    costs_at_120 = obs2.costs(S(120))
    # HAND-DERIVED expectation: feed poll AT the cutoff IS included (inclusive <=),
    # but an ordinary (non-terminal) GET dispatched AT the exact cutoff is EXCLUDED
    # entirely -- code uses request_time < cutoff (strict) for the body_requests/
    # outcomes loop unless terminal_mode. So at cutoff=120:
    EXPECT_FEED_REQUESTS = 3         # polls at 0,60,120 all <=120
    EXPECT_BODY_REQUESTS_EXCL = 0    # the GET at exactly 120 is excluded (not even "pending")
    EXPECT_PENDING_EXCL = 0
    ok2 = (
        costs_at_120.feed_requests == EXPECT_FEED_REQUESTS
        and costs_at_120.body_requests == EXPECT_BODY_REQUESTS_EXCL
        and costs_at_120.pending_body_requests == EXPECT_PENDING_EXCL
    )
    report(
        "BOUNDARY: feed poll at C included, ordinary GET at C fully excluded (not even pending)",
        ok2,
        f"feed_requests={costs_at_120.feed_requests} body_requests={costs_at_120.body_requests} "
        f"pending={costs_at_120.pending_body_requests}",
    )
    # And one microsecond later it IS visible:
    costs_after = obs2.costs(S(120) + timedelta(microseconds=1))
    report(
        "BOUNDARY: same GET visible at C+1us (available, BODY)",
        costs_after.body_requests == 1 and costs_after.successful_body_responses == 1,
        f"body_requests={costs_after.body_requests} body_ok={costs_after.successful_body_responses}",
    )
except Exception:
    report("BOUNDARY test block", False, traceback.format_exc())


# ---------------------------------------------------------------------------
# TEST 3: terminal-directory boundary exception (GET exactly at HORIZON_END)
# ---------------------------------------------------------------------------
et1, rt1 = make_save_event("T1", 1, S(60), "t1body", 1)
EXPORT3 = build_export([et1], [rt1])

try:
    obs3 = Observer(EXPORT3, config=ObserverConfig())
    dirresp = obs3.terminal_directory()  # request_time defaults HORIZON_END
    assert "T1" in dirresp.page_keys
    resp3 = obs3.get_body("T1", HORIZON_END)  # request_time == operation_clock == HORIZON_END
    assert isinstance(resp3, BodyResponse)
    costs_end = obs3.costs(HORIZON_END)
    # HAND-DERIVED: terminal_at_cutoff exception applies (terminal_mode True,
    # request_time == cutoff == HORIZON_END) -> counted AND resolved as BODY.
    ok3 = (
        costs_end.body_requests == 1
        and costs_end.successful_body_responses == 1
        and costs_end.downloaded_known_body_bytes == len(b"t1body")
    )
    report(
        "X01/X02: terminal-directory GET exactly at HORIZON_END IS counted+resolved (documented exception)",
        ok3,
        f"body_requests={costs_end.body_requests} body_ok={costs_end.successful_body_responses} "
        f"bytes={costs_end.downloaded_known_body_bytes} (expected {len(b't1body')})",
    )
except Exception:
    report("TERMINAL boundary test block", False, traceback.format_exc())


# ---------------------------------------------------------------------------
# TEST 4: X02 causal ordering guards
# ---------------------------------------------------------------------------
eo1, ro1 = make_save_event("O", 1, S(30), "o1", 1)
EXPORT4 = build_export([eo1], [ro1])

def fresh4():
    return Observer(EXPORT4, config=ObserverConfig())

# 4a: backdated GET after a poll -> reject
try:
    o = fresh4()
    o.poll_feed(S(120))
    try:
        o.get_body("O", S(60))  # 60 < last_poll(120)
        report("X02: backdated GET after poll rejected", False, "no exception raised")
    except ObserverTimeError:
        report("X02: backdated GET after poll rejected", True)
except Exception:
    report("X02: backdated GET after poll rejected", False, traceback.format_exc())

# 4b: backdated poll after a GET -> reject
try:
    o = fresh4()
    o.poll_feed(S(60))          # last_poll=60
    o.get_body("O", S(150))     # ok, operation_clock -> 150
    try:
        o.poll_feed(S(120))      # 120 < operation_clock(150) -> must reject
        report("X02: backdated poll after GET rejected", False, "no exception raised")
    except ObserverTimeError:
        report("X02: backdated poll after GET rejected", True)
except Exception:
    report("X02: backdated poll after GET rejected", False, traceback.format_exc())

# 4c: terminal directory then ordinary poll -> reject
try:
    o = fresh4()
    o.terminal_directory()
    try:
        o.poll_feed(HORIZON_END)
        report("X02: poll after terminal_directory rejected", False, "no exception raised")
    except ObserverError:
        report("X02: poll after terminal_directory rejected", True)
except Exception:
    report("X02: poll after terminal_directory rejected", False, traceback.format_exc())

# 4d: ordinary poll then terminal directory -> reject (reverse order)
try:
    o = fresh4()
    o.poll_feed(S(60))
    try:
        o.terminal_directory()
        report("X02: terminal_directory after poll rejected", False, "no exception raised")
    except ObserverError:
        report("X02: terminal_directory after poll rejected", True)
except Exception:
    report("X02: terminal_directory after poll rejected", False, traceback.format_exc())

# 4e: terminal directory called twice -> reject (one-shot)
try:
    o = fresh4()
    o.terminal_directory()
    try:
        o.terminal_directory()
        report("X02: second terminal_directory call rejected (one-shot)", False, "no exception raised")
    except ObserverError:
        report("X02: second terminal_directory call rejected (one-shot)", True)
except Exception:
    report("X02: second terminal_directory call rejected (one-shot)", False, traceback.format_exc())

# 4f: title discovered via terminal directory, then GET backdated before terminal directory's own timestamp
try:
    o = fresh4()
    o.terminal_directory()  # operation_clock -> HORIZON_END
    try:
        o.get_body("O", HORIZON_END - timedelta(minutes=1))
        report("X02: GET predating terminal_directory timestamp rejected", False, "no exception raised")
    except ObserverTimeError:
        report("X02: GET predating terminal_directory timestamp rejected", True)
except Exception:
    report("X02: GET predating terminal_directory timestamp rejected", False, traceback.format_exc())


# ---------------------------------------------------------------------------
# TEST 5: delayed-GET opacity -- structural inspection, not just behavior
# ---------------------------------------------------------------------------
ed1, rd1 = make_save_event("D", 1, S(60), "hello", 1)
EXPORT5 = build_export([ed1], [rd1])
CFG5 = ObserverConfig(get_response_delay_us=100_000_000)  # 100s delay

try:
    o5 = Observer(EXPORT5, config=CFG5)
    o5.poll_feed(S(0))
    o5.poll_feed(S(60))
    o5.poll_feed(S(120))  # discovers D (pub=65<=120)
    handle = o5.get_body("D", S(120))  # response_time = 120+100=220s
    assert isinstance(handle, PendingBodyRequest)
    field_names = {f.name for f in dataclasses.fields(handle)}
    EXPECT_FIELDS = {"page_key", "request_seq", "request_time", "response_time"}
    no_body_leak = "body" not in field_names and "outcome" not in field_names
    report(
        "OPACITY: PendingBodyRequest carries no body/outcome fields (structural)",
        field_names == EXPECT_FIELDS and no_body_leak,
        f"fields={field_names}",
    )

    # before due time, complete_due must not reveal it
    early = o5.complete_due(S(219))
    report("OPACITY: complete_due before due time reveals nothing", early == (), f"got {early}")

    # at exactly due time (220), it resolves to BODY "hello"
    due = o5.complete_due(S(220))
    ok5 = len(due) == 1 and due[0].outcome is BodyOutcome.BODY and due[0].body == b"hello"
    report("OPACITY: complete_due at due time reveals real body", ok5, f"{due}")
except Exception:
    report("OPACITY test block", False, traceback.format_exc())

# 5b: request due EXACTLY at checkpoint C -- behavior depends on whether
# complete_due(C) was called first (a real, reportable sharp edge, not assumed).
ed2, rd2 = make_save_event("D2", 1, S(60), "hello", 1)
EXPORT5B = build_export([ed2], [rd2])
CFG5B = ObserverConfig(get_response_delay_us=100_000_000)
try:
    # Case A: costs(C) queried WITHOUT calling complete_due(C) first.
    oA = Observer(EXPORT5B, config=CFG5B)
    oA.poll_feed(S(0)); oA.poll_feed(S(60)); oA.poll_feed(S(120))
    oA.get_body("D2", S(120))  # due at 220
    costsA = oA.costs(S(220))  # complete_due NOT called
    # HAND-DERIVED: audit record still has response_time=None (never revealed) ->
    # treated as pending, 0 bytes, even though C == the true due time.
    okA = costsA.pending_body_requests == 1 and costsA.successful_body_responses == 0
    report(
        "OPACITY@C: due-exactly-at-C without prior complete_due(C) => pending, 0 bytes",
        okA,
        f"pending={costsA.pending_body_requests} body_ok={costsA.successful_body_responses}",
    )

    # Case B: same scenario, but complete_due(C) IS called first (as collectors.py always does).
    oB = Observer(EXPORT5B, config=CFG5B)
    oB.poll_feed(S(0)); oB.poll_feed(S(60)); oB.poll_feed(S(120))
    oB.get_body("D2", S(120))
    oB.complete_due(S(220))
    costsB = oB.costs(S(220))
    okB = costsB.pending_body_requests == 0 and costsB.successful_body_responses == 1 and \
        costsB.downloaded_known_body_bytes == len(b"hello")
    report(
        "OPACITY@C: due-exactly-at-C WITH prior complete_due(C) => resolved BODY, real bytes only",
        okB,
        f"pending={costsB.pending_body_requests} body_ok={costsB.successful_body_responses} "
        f"bytes={costsB.downloaded_known_body_bytes}",
    )
except Exception:
    report("OPACITY@C test block", False, traceback.format_exc())


# ---------------------------------------------------------------------------
# TEST 6: STORAGE -- genuine FIFO eviction (both fit standalone, not together)
# ---------------------------------------------------------------------------
# packet_bytes formula (hand-derived from Capture.packet's canonical_jsonl):
#   {"body_sha256":"<64hex>","capture_time":"<27-char ts>","page_key":"<pk>","request_seq":<n>}\n
#   constant overhead = 157 bytes; total = 157 + len(page_key) + digit_count(request_seq)
def expect_packet_bytes(page_key: str, request_seq: int) -> int:
    return 157 + len(page_key) + len(str(request_seq))

try:
    store6 = CaptureStore(200, deduplicate=False, start_time=HORIZON_START)
    c1 = Capture("X", S(10), 1, b"aaaa")   # packet=157+1+1=159, body=4, standalone=163
    c2 = Capture("Y", S(20), 2, b"bbbb")   # packet=159, body=4, standalone=163
    assert len(c1.packet_bytes) == expect_packet_bytes("X", 1) == 159
    assert len(c2.packet_bytes) == expect_packet_bytes("Y", 2) == 159
    r1_ = store6.admit(c1)
    # HAND-DERIVED: after c1, current=163 (<=200), no eviction.
    assert r1_.disposition == "admitted" and r1_.store_bytes == 163 and r1_.evicted_request_seqs == ()
    r2_ = store6.admit(c2)
    # HAND-DERIVED: 163(current)+163(marginal for c2)=326>200 -> evict oldest (c1, seq1).
    # After evicting c1: current=0, then +163(c2)=163<=200 -> admitted.
    ok6 = (
        r2_.disposition == "admitted"
        and r2_.evicted_request_seqs == (1,)   # OLDER (X, seq1) evicted, not newer
        and r2_.store_bytes == 163
    )
    report(
        "STORAGE: genuine FIFO eviction evicts OLDER capture, not newer",
        ok6,
        f"evicted={r2_.evicted_request_seqs} store_bytes={r2_.store_bytes}",
    )
    retained_keys = [p.page_key for p in store6.retained_captures]
    report("STORAGE: retained set is exactly the newer capture (Y)", retained_keys == ["Y"], f"{retained_keys}")
except Exception:
    report("STORAGE FIFO test block", False, traceback.format_exc())


# ---------------------------------------------------------------------------
# TEST 7: STORAGE -- exact dedup (same body twice must not double body bytes)
# ---------------------------------------------------------------------------
try:
    store7 = CaptureStore(1000, deduplicate=True, start_time=HORIZON_START)
    c3 = Capture("Z", S(10), 3, b"aaaa")  # packet=157+1+1=159, body=4
    c4 = Capture("W", S(20), 4, b"aaaa")  # packet=159 (same body content, shared)
    store7.admit(c3)
    r4_ = store7.admit(c4)
    # HAND-DERIVED: two packets (159 each = 318) + ONE shared body (4 bytes) = 322.
    # NOT 326 (which would be the double-counted-body number).
    EXPECT_CURRENT_322 = 322
    snap7 = store7.snapshot()
    ok7 = (
        snap7.current_store_bytes == EXPECT_CURRENT_322
        and snap7.retained_body_bytes == 4          # body stored once, not twice
        and snap7.retained_body_objects == 1
        and snap7.object_reference_counts == (2,)   # refcount=2 (both packets share it)
    )
    report(
        "STORAGE: exact dedup -- identical body stored once, refcount=2, bytes not doubled",
        ok7,
        f"current={snap7.current_store_bytes} body_bytes={snap7.retained_body_bytes} "
        f"objects={snap7.retained_body_objects} refs={snap7.object_reference_counts}",
    )

    # TEST 8: refcounting -- evicting the OLDER shared-body packet must not delete
    # the body object while a newer packet (W) still references it; then a third,
    # distinct-body capture forces exactly that eviction.
    c5 = Capture("V", S(30), 5, b"cccc")  # packet=159, body=4, distinct sha
    store8 = CaptureStore(340, deduplicate=True, start_time=HORIZON_START)
    store8.admit(c3)  # Z, body aaaa
    store8.admit(c4)  # W, body aaaa (shared) -> current=322 as above
    r5_ = store8.admit(c5)
    # HAND-DERIVED: current(322)+marginal(159+4=163)=485>340 -> evict oldest (Z, seq3).
    # Evicting Z: packet_bytes -=159 -> 159 remains (W's packet). Z's object_id is
    # shared with W (same sha) so refcount 2->1, NOT deleted (body_bytes stays 4).
    # current becomes 159+4=163; +163(c5 marginal)=326<=340 -> admitted.
    ok8 = (
        r5_.disposition == "admitted"
        and r5_.evicted_request_seqs == (3,)   # Z (older) evicted, W (newer, same body) survives
        and r5_.store_bytes == 326
    )
    snap8 = store8.snapshot()
    retained8 = sorted(p.page_key for p in store8.retained_captures)
    refs8 = sorted(snap8.object_reference_counts)
    no_zero_ref = all(r > 0 for r in refs8)
    report(
        "STORAGE: shared body survives eviction of one referencing packet (refcount>0 kept)",
        ok8 and retained8 == ["V", "W"] and refs8 == [1, 1] and no_zero_ref,
        f"evicted={r5_.evicted_request_seqs} store_bytes={r5_.store_bytes} retained={retained8} refs={refs8}",
    )
except Exception:
    report("STORAGE dedup/refcount test block", False, traceback.format_exc())


# ---------------------------------------------------------------------------
# TEST 9: packet byte widths -- non-ASCII multi-byte UTF-8 body vs empty body
# ---------------------------------------------------------------------------
try:
    empty_capture = Capture("Q", S(1), 9, b"")
    # "café" -> c(1)+a(1)+f(1)+é(2 bytes in utf-8) = 5 bytes, 4 characters
    multi_body = "café".encode("utf-8")
    assert len(multi_body) == 5
    multi_capture = Capture("Q", S(2), 9, multi_body)
    EXPECT_PACKET_BYTES_Q9 = expect_packet_bytes("Q", 9)  # 157+1+1=159, independent of body
    ok9 = (
        len(empty_capture.packet_bytes) == EXPECT_PACKET_BYTES_Q9 == 159
        and len(multi_capture.packet_bytes) == EXPECT_PACKET_BYTES_Q9 == 159
        and len(empty_capture.body) == 0
        and len(multi_capture.body) == 5
    )
    report(
        "STORAGE: packet width independent of body (empty vs 5-byte multi-byte UTF-8 body)",
        ok9,
        f"empty_packet={len(empty_capture.packet_bytes)} multi_packet={len(multi_capture.packet_bytes)} "
        f"empty_body={len(empty_capture.body)} multi_body={len(multi_capture.body)}",
    )
except Exception:
    report("STORAGE packet-width test block", False, traceback.format_exc())


# ---------------------------------------------------------------------------
# TEST 10: synchronized S/M/peak -- true combined peak vs naive sum-of-peaks
# ---------------------------------------------------------------------------
try:
    t0 = HORIZON_START
    pts = [
        (t0, 10, 0),
        (t0 + timedelta(minutes=10), 10, 50),
        (t0 + timedelta(minutes=20), 100, 0),
    ]
    checkpoint10 = t0 + timedelta(minutes=30)
    # HAND-DERIVED (see reasoning in audit notes): intervals [0,10)->S+M=10, [10,20)->60, [20,30)->100.
    EXPECT_PEAK_S = 100
    EXPECT_PEAK_M = 50
    EXPECT_PEAK_COMBINED = 100          # NOT 150 (naive sum of independent peaks would be wrong)
    EXPECT_S_AREA_US = 72_000_000_000   # 10*600e6 + 10*600e6 + 100*600e6
    EXPECT_M_AREA_US = 30_000_000_000   # 0*600e6 + 50*600e6 + 0*600e6
    result10 = synchronized_accounting(pts, checkpoint10)
    ok10 = (
        result10.peak_s == EXPECT_PEAK_S
        and result10.peak_m == EXPECT_PEAK_M
        and result10.synchronized_peak_s_plus_m == EXPECT_PEAK_COMBINED
        and result10.s_byte_microseconds == EXPECT_S_AREA_US
        and result10.m_byte_microseconds == EXPECT_M_AREA_US
        and result10.final_s == 100 and result10.final_m == 0
    )
    report(
        "ACCOUNTING: synchronized peak(S+M) != naive sum of independently-timed peaks",
        ok10,
        f"peak_s={result10.peak_s} peak_m={result10.peak_m} "
        f"peak_combined={result10.synchronized_peak_s_plus_m} (naive sum would be 150) "
        f"s_area={result10.s_byte_microseconds} m_area={result10.m_byte_microseconds}",
    )
except Exception:
    report("ACCOUNTING synchronized test block", False, traceback.format_exc())


# ---------------------------------------------------------------------------
# TEST 11: byte-hours -- simple two-interval timeline hand-computation
# ---------------------------------------------------------------------------
try:
    store11 = CaptureStore(1000, deduplicate=False, start_time=HORIZON_START)
    cap1 = Capture("H", HORIZON_START, 1, b"1234567890")  # packet=157+1+1=159, body=10 -> 169
    store11.admit(cap1)
    t_2h = HORIZON_START + timedelta(hours=2)
    cap2 = Capture("I", t_2h, 2, b"01234567890123456789")  # packet=159, body=20 -> 179
    store11.admit(cap2)
    checkpoint11 = HORIZON_START + timedelta(hours=3)
    snap11 = store11.snapshot(checkpoint11)
    # HAND-DERIVED byte-hours = 169 bytes held for 2h + (169+179)=348 bytes held for 1h
    #                          = 338 + 348 = 686 byte-hours exactly.
    EXPECT_BYTE_HOURS = 686.0
    ok11 = snap11.store_byte_hours == EXPECT_BYTE_HOURS
    report(
        "ACCOUNTING: byte-hours hand-computation (169B*2h + 348B*1h = 686)",
        ok11,
        f"store_byte_hours={snap11.store_byte_hours}",
    )
except Exception:
    report("ACCOUNTING byte-hours test block", False, traceback.format_exc())


# ---------------------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------------------
print("\n=== SUMMARY ===")
fail_count = 0
for name, status in RESULTS:
    print(f"{status:6s} | {name}")
    if not status.startswith("PASS"):
        fail_count += 1
print(f"\n{len(RESULTS)} checks, {fail_count} failing")
sys.exit(1 if fail_count else 0)
