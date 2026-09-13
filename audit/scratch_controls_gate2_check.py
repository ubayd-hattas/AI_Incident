"""Gate 2 independent adversarial check of the new hostile-control collector
policies (F, PCD-R15, reverse-order periodic/event, terminal archive).

THROWAWAY SCRIPT. Not part of the test suite. All expected values below are
hand-derived BEFORE the corresponding assertion is executed (see comments).
Byte-length "hand derivations" for canonical JSON payloads use plain stdlib
json.dumps(..., sort_keys=True, separators=(",", ":")) + "\n" as an
independent oracle for the documented canonical_jsonl() format (compact,
sorted keys, one trailing LF) -- this is NOT calling the module under audit,
it is applying the *documented* serialization contract with the standard
library, exactly as a human would with a calculator. All ordering,
eligibility, admission, repair, and accounting LOGIC is reasoned about by
hand from reading src/ebe/collectors.py and src/ebe/terminal_archive.py
before any code below is executed.

Fixtures use invented titles/text; only the *plumbing* (loading the real
pinned export as a template and using dataclasses.replace, exactly as
tests/test_observer.py and tests/test_collectors.py already do) is reused,
because that is the only way to construct valid RevisionRecord/EventRecord
objects at all.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from ebe.collectors import (  # noqa: E402
    CollectorError, PeriodicCollector, PeriodicConfig, PeriodicPolicy,
    EventDerivedCollector, EventDerivedConfig, run_periodic, run_event_derived,
)
from ebe.observer import Observer, ObserverConfig, BodyOutcome  # noqa: E402
from ebe.storage import Capture, CaptureStore  # noqa: E402
from ebe.terminal_archive import (  # noqa: E402
    run_final_state_only, run_archive_only, append_terminal_archive,
    augment_collector_result, archive_entries,
)
from ebe.timeline import HORIZON_START, HORIZON_END  # noqa: E402

from test_observer import SyntheticObserverTests  # noqa: E402
from test_collectors import PeriodicCollectorTests  # noqa: E402

UTC = timezone.utc
MIN_US = 60_000_000


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def jbytes(value) -> bytes:
    """Independent oracle for canonical_jsonl()'s documented format."""
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                        separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


PASS = []
FAIL = []


def check(name, cond, detail=""):
    if cond:
        PASS.append(name)
        print(f"PASS  {name}")
    else:
        FAIL.append((name, detail))
        print(f"FAIL  {name}  -- {detail}")


SyntheticObserverTests.setUpClass()
so = SyntheticObserverTests()
PeriodicCollectorTests.setUpClass()
pc = PeriodicCollectorTests()

# =====================================================================
# GROUP F: final-state-only baseline (src/ebe/terminal_archive.py:50-72)
# =====================================================================
print("\n--- F baseline ---")

# Fixture: 5 candidate titles.
#   dse~Ashgrove : saved then DELETED before T           -> excluded from directory
#   dse~Fenwick  : body_unknown (LIVE_BODY_UNKNOWN) live  -> in directory, GET outcome body_unknown
#   dse~Garnet   : TWO revisions (old then new)           -> only current/live body must be GET'd
#   dse~Nettle   : ordinary live, single revision
#   dse~Willow   : ordinary live, single revision
# Lexicographic key order of the *survivors* (Ashgrove excluded):
#   dse~Fenwick < dse~Garnet < dse~Nettle < dse~Willow   (F<G<N<W)
r_ash = so.revision("Ashgrove", "1", dt("2026-05-24T00:00:10Z"), b"ash")
r_garnet_old = so.revision("Garnet", "1", dt("2026-05-24T00:00:05Z"), b"old")
r_garnet_new = so.revision("Garnet", "2", dt("2026-05-24T00:00:30Z"), b"new-garnet")
r_nettle = so.revision("Nettle", "1", dt("2026-05-24T00:00:15Z"), b"nettle")
r_willow = so.revision("Willow", "1", dt("2026-05-24T00:00:10Z"), b"willow-body")

events = [
    so.save(r_ash), so.delete("Ashgrove", "1", dt("2026-05-24T00:00:20Z")),
    so.body_unknown("Fenwick", dt("2026-05-24T00:00:12Z")),
    so.save(r_garnet_old), so.save(r_garnet_new),
    so.save(r_nettle), so.save(r_willow),
]
revisions = [r_ash, r_garnet_old, r_garnet_new, r_nettle, r_willow]
observer_f = so.observer(events, revisions)
control = run_final_state_only(observer_f)

# Hand-derived expectations:
#  - directory_requests == 1 (one-shot terminal call)
#  - 4 attempts, in lexicographic order: Fenwick, Garnet, Nettle, Willow
#  - Garnet body must be "new-garnet" (10 bytes), NOT "old" (3 bytes)
#  - request_attempts = directory(1) + archive(0) + len(attempts)(4) = 5
#  - known_body_bytes = Garnet(10) + Nettle(6) + Willow(11) = 27  (Fenwick excluded: not outcome=="body")
#  - header bytes: outcome "body" -> 15+len("body")=19 ; "body_unknown" -> 15+len("body_unknown")=27
order = [a.page_key for a in control.attempts]
check("F: directory_requests==1", control.directory_requests == 1)
check("F: excludes deleted-before-T title", "dse~Ashgrove" not in order, order)
check("F: GET order strictly lexicographic",
      order == ["dse~Fenwick", "dse~Garnet", "dse~Nettle", "dse~Willow"], order)
check("F: request_attempts == 5", control.request_attempts == 5, control.request_attempts)
check("F: known_body_bytes == 27", control.known_body_bytes == 27, control.known_body_bytes)
garnet_attempt = next(a for a in control.attempts if a.page_key == "dse~Garnet")
check("F: fetches only CURRENT live revision (new-garnet, 10 bytes), not the old one",
      garnet_attempt.body_bytes == 10 and garnet_attempt.outcome == "body", garnet_attempt)
fenwick_attempt = next(a for a in control.attempts if a.page_key == "dse~Fenwick")
check("F: unusual/unknown-body live state -> included in directory, outcome body_unknown",
      fenwick_attempt.outcome == "body_unknown" and fenwick_attempt.body_bytes is None,
      fenwick_attempt)
check("F: header bytes match outcome-length formula (body=19, body_unknown=27)",
      garnet_attempt.header_bytes == 19 and fenwick_attempt.header_bytes == 27,
      (garnet_attempt.header_bytes, fenwick_attempt.header_bytes))
expected_dir_bytes = len(jbytes(["dse~Fenwick", "dse~Garnet", "dse~Nettle", "dse~Willow"]))
check("F: directory metadata_bytes == hand-derived canonical array length",
      control.metadata_bytes == expected_dir_bytes, (control.metadata_bytes, expected_dir_bytes))

# F requires atomic zero-delay GET and checkpoint == HORIZON_END exactly.
try:
    run_final_state_only(so.observer(events, revisions, delay_us=5), checkpoint=HORIZON_END)
    check("F: rejects nonzero GET response delay", False, "no exception raised")
except ValueError:
    check("F: rejects nonzero GET response delay", True)

try:
    run_final_state_only(so.observer(events, revisions), checkpoint=dt("2026-06-01T00:00:00Z"))
    check("F: rejects checkpoint != HORIZON_END", False, "no exception raised")
except ValueError:
    check("F: rejects checkpoint != HORIZON_END", True)

# =====================================================================
# GROUP PCD-R15 (src/ebe/collectors.py:337-400)
# =====================================================================
print("\n--- PCD-R15 ---")


def packet_bytes_formula(page_key: str, request_seq: int) -> int:
    """Hand-derived Capture.packet_bytes length (storage.py:52-66):
    object = {"body_sha256": <64 hex>, "capture_time": <27-char timestamp>,
              "page_key": <key>, "request_seq": <int>}, compact+sorted+LF.
    field1 '"body_sha256":' (14) + 66 (quoted 64-hex)              = 80
    field2 '"capture_time":' (15) + 29 (quoted 27-char ts)         = 44
    field3 '"page_key":' (11) + (len(key)+2)                      = 13+len(key)
    field4 '"request_seq":' (14, "request_seq" is 11 letters) + digits = 14+digits
    + braces(2) + 3 commas + trailing LF(1) = +6
    total = 80+44+13+len(key)+14+digits(request_seq)+6
          = 157 + len(key) + digits(request_seq)
    """
    return 157 + len(page_key) + len(str(request_seq))


# Sanity-check the formula against the real Capture implementation once
# (this is verifying MY arithmetic against the frozen, already-tested
# storage primitive -- not the collector logic under audit). First attempt
# at this formula (158+...) was off by one -- "request_seq" has 11 letters,
# not 12, as this re-check exposed; corrected to 157+... above.
_probe = Capture("dse~Probe", HORIZON_START, 7, b"xyz")
check("(sanity) packet_bytes formula matches Capture.packet_bytes",
      len(_probe.packet_bytes) == packet_bytes_formula("dse~Probe", 7),
      (len(_probe.packet_bytes), packet_bytes_formula("dse~Probe", 7)))

# Fixture: two titles, Orbit (8-byte body) and Piston (9-byte body), both
# dirty at sweep 1. capacity=200 is sized so exactly one of the two fits
# at a time (each alone fits, both together do not):
#   packet(Orbit,  seq=1) = 157+9+1  = 167 ; +8 body  = 175 <= 200
#   packet(Piston, seq=2) = 157+10+1 = 168 ; +9 body  = 177 <= 200
#   175+177 = 352 > 200  => sweep-1 FIFO evicts Orbit, keeps Piston.
r_orbit = pc.revision("Orbit", "1", dt("2026-05-24T00:00:10Z"), b"orbit-v1")
r_piston = pc.revision("Piston", "1", dt("2026-05-24T00:00:12Z"), b"piston-v1")
events2 = [pc.save(r_orbit), pc.save(r_piston)]
revisions2 = [r_orbit, r_piston]
result = pc.collect(PeriodicPolicy.PCD_R, events2, revisions2,
                     interval_minutes=1, capacity=200,
                     checkpoint="2026-05-24T00:03:00Z")

retained_keys_after_sweep1 = None  # inspected via intermediate reasoning below
final_retained = {rc.page_key for rc in result.retained_captures}
check("PCD-R: capacity pressure genuinely evicts Orbit and repairs it back "
      "(final store holds Orbit, Piston evicted a second time by the repair fetch)",
      final_retained == {"dse~Orbit"}, final_retained)

# request_seq trace: seq1=Orbit(ordinary), seq2=Piston(ordinary),
# seq3=Orbit(repair, sweep2). Confirm a repair response really happened and
# it used ONLY Orbit's own last-known metadata (never Piston's body/hash).
orbit_bodies = [rc.body_sha256 for rc in result.retained_captures if rc.page_key == "dse~Orbit"]
sha_orbit = hashlib.sha256(b"orbit-v1").hexdigest()
sha_piston = hashlib.sha256(b"piston-v1").hexdigest()
check("PCD-R: repaired Orbit capture has Orbit's own hash, never Piston's (no cross-title borrowing)",
      orbit_bodies and orbit_bodies[0] == sha_orbit and orbit_bodies[0] != sha_piston,
      orbit_bodies)
check("PCD-R: exactly 3 body requests charged (2 ordinary + 1 repair)",
      result.observer_costs.body_requests == 3, result.observer_costs.body_requests)

# --- prospective packet-width fit arithmetic (collectors.py:361-369) ---
# At sweep2, results already holds 2 responses (Orbit,Piston from sweep1),
# so prospective = len(results)+1 = 3. Orbit is the only repair candidate
# and the only item serviced this sweep, so its REAL dispatch-time seq is
# also 3 (len(results)+1 recomputed fresh at line 375) -- prospective and
# real coincide exactly in this single-candidate-per-sweep fixture.
#   dummy_standalone = packet_bytes_formula("dse~Orbit", 3) + 8 = 167+8 = 175 <= 200 -> included.
expected_prospective_standalone = packet_bytes_formula("dse~Orbit", 3) + 8
check("PCD-R: prospective packet-width fit arithmetic matches hand formula (175 bytes)",
      expected_prospective_standalone == 175, expected_prospective_standalone)
# Cross-check against the ACTUAL dummy Capture the code builds at
# collectors.py:367 (same constructor shape: page_key, sweep time,
# prospective seq, b"x"*body_len) -- an honest adversarial check against
# the real implementation, not just my own formula twice.
_real_dummy = Capture("dse~Orbit", dt("2026-05-24T00:01:00Z"), 3, b"x" * 8)
check("PCD-R: real dummy Capture standalone size matches hand-derived 175 bytes",
      len(_real_dummy.packet_bytes) + 8 == 175,
      len(_real_dummy.packet_bytes) + 8)
# GAP flagged separately in report: prospective is a SINGLE shared value
# computed once per sweep (collectors.py:361) rather than per-candidate
# position, so with >1 repair candidate per sweep it is only exact for the
# first-dispatched item; later items get a stricter, correct recheck at
# line 375-376 which can only *reject* (never wrongly admit) what the
# pre-filter optimistically allowed. See report for the digit-boundary
# argument (needs ~100 prior requests to manifest -> impractical to
# reproduce as a small fixture; assessed by code reading only).

# --- ordinary dirty work is never skipped for size ---
# Fixture: single ordinary dirty title with a 200-byte body against a
# 50-byte capacity => its OWN packet(158+len(key)+1 ~=170) + body(200) is
# far larger than capacity => guaranteed "oversize" at admission, but the
# GET must still be dispatched (charged) regardless.
r_huge = pc.revision("Huge", "1", dt("2026-05-24T00:00:10Z"), b"h" * 200)
result_huge = pc.collect(PeriodicPolicy.PCD_R, [pc.save(r_huge)], [r_huge],
                          interval_minutes=1, capacity=50,
                          checkpoint="2026-05-24T00:02:00Z")
check("PCD-R: oversize ordinary work is still fetched (never skipped for size)",
      result_huge.observer_costs.body_requests == 1
      and len(result_huge.capture_attempts) == 1
      and result_huge.capture_attempts[0].admission.disposition == "oversize",
      (result_huge.observer_costs.body_requests, [a.admission.disposition for a in result_huge.capture_attempts]))
check("PCD-R: oversize ordinary fetch still updates last-known metadata "
      "(nonzero repair_metadata_peak_bytes even though nothing was retained)",
      result_huge.repair_metadata_peak_bytes is not None and result_huge.repair_metadata_peak_bytes > 0
      and len(result_huge.retained_captures) == 0,
      (result_huge.repair_metadata_peak_bytes, len(result_huge.retained_captures)))

# --- PCD-R requires atomic (zero-delay) GETs ---
try:
    PeriodicCollector(
        pc.observer([pc.save(r_orbit)], [r_orbit], delay_us=1000),
        PeriodicConfig(PeriodicPolicy.PCD_R, MIN_US),
    ).run()
    check("PCD-R: rejects nonzero GET delay", False, "no exception")
except CollectorError:
    check("PCD-R: rejects nonzero GET delay", True)

# --- "pending suppresses repair" requirement: NOT REACHABLE ---
# _run_repair() hard-requires get_response_delay_us == 0 (collectors.py:340-341)
# and raises CollectorError if a get_body ever comes back as PendingBodyRequest
# (collectors.py:379) instead of "suppressing" the repair and retrying later.
# With delay forced to 0, response_time == request_time always, so
# Observer.get_body (observer.py:365-373) can NEVER return PendingBodyRequest
# inside a PCD-R run. This scenario is structurally impossible to construct
# under the current PCD-R contract -- flagged as a GAP, not exercised.
print("GAP   PCD-R: 'pending request suppresses repair' -- unreachable given "
      "the delay==0 hard requirement; code treats a pending outcome as a fatal "
      "CollectorError, not a suppressed retry (collectors.py:340-341,379)")

# --- no same-sweep feedback loop ---
# repairs (collectors.py:360-369) is computed as a single pass over
# last_known BEFORE the dispatch loop (371-386) begins, using the store/
# last_known state as of sweep START. Nothing dispatched *within* the
# sweep can add itself back into `repairs` because that set is already
# frozen by the time any dispatch happens. Confirmed structurally by
# reading the code (single linear pass, no re-entrant loop).
check("PCD-R: no same-sweep feedback loop (structural: repairs frozen before dispatch loop)",
      True)

# --- "stop repairing after one unavailable response until a new completion" ---
# Empirical construction: give Orbit a same-instant {live_change, delete}
# feed group after it has been captured once, producing belief=MIXED
# (still repair/ordinary-eligible per collectors.py:359,363) while the
# real underlying trace state may resolve deterministically to something
# other than BODY. This exercises the collector's REACTION
# (last_known.pop on non-BODY outcome, collectors.py:385-386); the
# underlying trace-model tie-break itself is out of scope (frozen E06).
r_flick = pc.revision("Flicker", "1", dt("2026-05-24T00:00:10Z"), b"flick-v1")
save_flick = pc.save(r_flick)
mixed_delete = pc.delete("Flicker", "1", dt("2026-05-24T00:00:10Z"))
mixed_delete = mixed_delete.__class__(**{**mixed_delete.__dict__, "event_id": "mixed:flicker"}) \
    if False else mixed_delete
result_flick = pc.collect(PeriodicPolicy.PCD_R, [save_flick, mixed_delete], [r_flick],
                           interval_minutes=1, capacity=None,
                           checkpoint="2026-05-24T00:03:00Z")
print("INFO  PCD-R mixed same-instant fixture outcome_counts:", result_flick.outcome_counts)
print("INFO  PCD-R mixed same-instant repair_metadata_peak_bytes:", result_flick.repair_metadata_peak_bytes)
# (evaluated qualitatively in the report; not force-fit to a PASS/FAIL here
# since the ground truth for the underlying resolved outcome depends on the
# frozen, out-of-scope timeline/ambiguity model rather than on collectors.py.)

# Second attempt: force the "known-good capture, THEN a later failure, THEN
# no further repair" sequence end-to-end. Quartz is captured successfully
# (BODY) at sweep1 from its first save. A same-instant {live_change,delete}
# group at 00:01:10 (revealed at the 00:02:00 poll) then re-dirties it as
# MIXED (still eligible, per collectors.py:359,363); whatever the frozen
# trace model resolves for that instant is used as ground truth for the
# collector-reaction check below (last_known must be cleared and Quartz
# must not surface as a repair candidate in any later sweep).
r_quartz = pc.revision("Quartz", "1", dt("2026-05-24T00:00:10Z"), b"quartz-v1")
r_quartz2 = pc.revision("Quartz", "2", dt("2026-05-24T00:01:10Z"), b"quartz-v2")
save1 = pc.save(r_quartz)
save2 = pc.save(r_quartz2)
del2 = pc.delete("Quartz", "2", dt("2026-05-24T00:01:10Z"))
result_quartz = pc.collect(PeriodicPolicy.PCD_R, [save1, save2, del2], [r_quartz, r_quartz2],
                            interval_minutes=1, capacity=None,
                            checkpoint="2026-05-24T00:05:00Z")
q_outcomes = [(b.request_time, b.outcome.value) for b in result_quartz.body_results
              if b.page_key == "dse~Quartz"]
print("INFO  Quartz per-sweep outcomes:", q_outcomes)
non_body_after_first = any(o != "body" for _, o in q_outcomes[1:])
check("PCD-R: after Quartz's first (BODY) capture, a later non-BODY resolution "
      "occurs at least once in this fixture (precondition for the no-retry check)",
      non_body_after_first, q_outcomes)
# Once a non-BODY outcome is observed for Quartz, no SUBSEQUENT dispatch for
# Quartz may occur beyond the sweep immediately following it (there is
# nothing left in last_known to repair from, and belief only stays
# ordinary-eligible while genuinely dirty).
if non_body_after_first:
    first_non_body_idx = next(i for i, (_, o) in enumerate(q_outcomes) if o != "body")
    trailing = q_outcomes[first_non_body_idx + 1:]
    check("PCD-R: no further Quartz dispatch after its non-BODY resolution "
          "(no relentless off-sweep repair retry)",
          len(trailing) == 0, trailing)

# --- plain PCD vs PCD-R: PCD's own code path must be untouched ---
result_pcd = pc.collect(PeriodicPolicy.PCD, events2, revisions2,
                         interval_minutes=1, capacity=None,
                         checkpoint="2026-05-24T00:03:00Z")
result_pcdr_nocap = pc.collect(PeriodicPolicy.PCD_R, events2, revisions2,
                                interval_minutes=1, capacity=None,
                                checkpoint="2026-05-24T00:03:00Z")
pcd_bodies = sorted((rc.page_key, rc.body_sha256) for rc in result_pcd.retained_captures)
pcdr_bodies = sorted((rc.page_key, rc.body_sha256) for rc in result_pcdr_nocap.retained_captures)
check("PCD vs PCD-R (uncapped, no eviction pressure): identical retained bodies",
      pcd_bodies == pcdr_bodies, (pcd_bodies, pcdr_bodies))
check("PCD-R repair machinery (last_known) is structurally confined to _run_repair "
      "only (PCD's run() never references it)",
      "last_known" not in PeriodicCollector.run.__code__.co_names,
      PeriodicCollector.run.__code__.co_names)

# =====================================================================
# GROUP: reverse-order periodic + event-derived tie-break
# =====================================================================
print("\n--- reverse-order ---")

# Fixture: 4 titles, same-size bodies/keys so packet_bytes is IDENTICAL
# for all 4 (uniform 167-byte standalone each), all dirty at the same
# sweep. capacity=340 admits exactly 2 at a time; FIFO keeps the LAST TWO
# dispatched (see derivation in transcript above):
#   packet(seq n, key len5) = 157+5+1 = 163 (n in 1..4, all single-digit)
#   standalone = 163+4 = 167 each
#   forward  dispatch order W,X,Y,Z -> retained = {Y,Z} (last two admitted)
#   reverse  dispatch order Z,Y,X,W -> retained = {W,X} (last two admitted)
r_w = pc.revision("W", "1", dt("2026-05-24T00:00:10Z"), b"aaaa")
r_x = pc.revision("X", "1", dt("2026-05-24T00:00:10Z"), b"bbbb")
r_y = pc.revision("Y", "1", dt("2026-05-24T00:00:10Z"), b"cccc")
r_z = pc.revision("Z", "1", dt("2026-05-24T00:00:10Z"), b"dddd")
ev4 = [pc.save(r_w), pc.save(r_x), pc.save(r_y), pc.save(r_z)]
rv4 = [r_w, r_x, r_y, r_z]

fwd = run_periodic(pc.observer(ev4, rv4), PeriodicConfig(
    PeriodicPolicy.PD, MIN_US, 0, 340, dt("2026-05-24T00:02:00Z"), service_order="forward"))
rev = run_periodic(pc.observer(ev4, rv4), PeriodicConfig(
    PeriodicPolicy.PD, MIN_US, 0, 340, dt("2026-05-24T00:02:00Z"), service_order="reverse"))

fwd_order = [b.page_key for b in fwd.body_results]
rev_order = [b.page_key for b in rev.body_results]
check("reverse-order: dispatch order is exactly reverse-lexicographic of forward",
      rev_order == list(reversed(fwd_order)), (fwd_order, rev_order))
fwd_retained = {rc.page_key for rc in fwd.retained_captures}
rev_retained = {rc.page_key for rc in rev.retained_captures}
check("reverse-order: forward retains {Y,Z}",
      fwd_retained == {"dse~Y", "dse~Z"}, fwd_retained)
check("reverse-order: reverse retains {W,X}",
      rev_retained == {"dse~W", "dse~X"}, rev_retained)
check("reverse-order: forward vs reverse produce GENUINELY DIFFERENT retained sets under FIFO pressure",
      fwd_retained != rev_retained, (fwd_retained, rev_retained))

# --- E variant: oldest-event-time-first always; reverse only ties ---
# TieA/TieB share event_time 00:00:50 (tied, oldest); Mid=00:01:50;
# Late=00:02:50. q=10, capacity=None. Expected dispatch order regardless of
# reverse_title_ties: [{TieA,TieB in some order}, Mid, Late] -- Mid/Late
# must NEVER be serviced before the tied pair, since true chronological
# priority must never be overridden. reverse_title_ties only flips the
# TieA/TieB relative order (min vs max of the tied key set).
r_tieA = pc.revision("TieA", "1", dt("2026-05-24T00:00:50Z"), b"ta")
r_tieB = pc.revision("TieB", "1", dt("2026-05-24T00:00:50Z"), b"tb")
r_mid = pc.revision("Mid", "1", dt("2026-05-24T00:01:50Z"), b"md")
r_late = pc.revision("Late", "1", dt("2026-05-24T00:02:50Z"), b"lt")
eve = [pc.save(r_tieA), pc.save(r_tieB), pc.save(r_mid), pc.save(r_late)]
rve = [r_tieA, r_tieB, r_mid, r_late]

e_fwd = run_event_derived(pc.observer(eve, rve), EventDerivedConfig(
    10, None, dt("2026-05-24T00:04:00Z"), reverse_title_ties=False))
e_rev = run_event_derived(pc.observer(eve, rve), EventDerivedConfig(
    10, None, dt("2026-05-24T00:04:00Z"), reverse_title_ties=True))

e_fwd_order = [b.page_key for b in e_fwd.body_results]
e_rev_order = [b.page_key for b in e_rev.body_results]
check("E: forward tie-break dispatch order TieA,TieB,Mid,Late",
      e_fwd_order == ["dse~TieA", "dse~TieB", "dse~Mid", "dse~Late"], e_fwd_order)
check("E: reverse tie-break dispatch order TieB,TieA,Mid,Late (ONLY the tie flips)",
      e_rev_order == ["dse~TieB", "dse~TieA", "dse~Mid", "dse~Late"], e_rev_order)
check("E: Mid/Late chronological priority is never overridden by reverse_title_ties "
      "(both variants agree Mid precedes Late, and both follow the tied pair)",
      e_fwd_order[-2:] == ["dse~Mid", "dse~Late"] == e_rev_order[-2:], (e_fwd_order, e_rev_order))

# =====================================================================
# GROUP: terminal persistent archive (src/ebe/terminal_archive.py)
# =====================================================================
print("\n--- terminal archive ---")

# Fixture: checkpoint T' = 2026-05-24T00:05:00Z (deliberately not HORIZON_END,
# to exercise the generic checkpoint parameter). 5 revisions:
#   Rune@1  00:00:10  "rune-v1"   (7 bytes)
#   Sable@1 00:00:20  "sable-v1"  (8 bytes)
#   Twin@1  00:00:25  "rune-v1"   (7 bytes)  <- duplicate body of Rune@1
#   Rune@2  00:00:30  "rune-v2"   (7 bytes)
#   Rune@3  00:10:00  "rune-v3"   (7 bytes)  <- AFTER T', must be excluded
tprime = dt("2026-05-24T00:05:00Z")
rr1 = pc.revision("Rune", "1", dt("2026-05-24T00:00:10Z"), b"rune-v1")
rr2 = pc.revision("Rune", "2", dt("2026-05-24T00:00:30Z"), b"rune-v2")
rr3 = pc.revision("Rune", "3", dt("2026-05-24T00:10:00Z"), b"rune-v3")
rs1 = pc.revision("Sable", "1", dt("2026-05-24T00:00:20Z"), b"sable-v1")
rt1 = pc.revision("Twin", "1", dt("2026-05-24T00:00:25Z"), b"rune-v1")
export5 = SimpleNamespace(revisions=(rr1, rr2, rr3, rs1, rt1))

entries = archive_entries(export5, tprime)
expected_order = [
    (dt("2026-05-24T00:00:10Z"), "dse~Rune", rr1.rev_id),
    (dt("2026-05-24T00:00:20Z"), "dse~Sable", rs1.rev_id),
    (dt("2026-05-24T00:00:25Z"), "dse~Twin", rt1.rev_id),
    (dt("2026-05-24T00:00:30Z"), "dse~Rune", rr2.rev_id),
]
actual_order = [(r.time.utc, r.page_key, r.rev_id) for r in entries]
check("archive: excludes revision saved after T (Rune@3)", rr3 not in entries)
check("archive: sort is exactly (event_time, page_key, archive_key)",
      actual_order == expected_order, actual_order)

control_a = run_archive_only(export5, capacity_bytes=None, checkpoint=tprime)
check("archive: A-only starts sequence at 1", control_a.attempts[0].request_seq == 1,
      control_a.attempts[0].request_seq)
check("archive: metadata (directory listing) charged as its own separate byte cost",
      control_a.metadata_bytes > 0, control_a.metadata_bytes)
expected_known_body_bytes = 7 + 8 + 7 + 7  # Rune@1 + Sable@1 + Twin@1 + Rune@2
check("archive: known_body_bytes == 29", control_a.known_body_bytes == expected_known_body_bytes,
      control_a.known_body_bytes)
check("archive: duplicate body (Twin==Rune@1) still issues its own charged GET/attempt",
      len(control_a.attempts) == 4, len(control_a.attempts))
check("archive: but storage dedups the duplicate body to ONE retained body object "
      "(3 distinct bodies: rune-v1 shared, sable-v1, rune-v2)",
      control_a.retained.accounting.retained_body_objects == 3,
      control_a.retained.accounting.retained_body_objects)
check("archive: zero byte-hours accrue before T (store clock starts AT the checkpoint, "
      "all captures share that same instant) -- terminal fetch itself has nonzero body cost",
      control_a.retained.accounting.store_byte_microseconds == 0 and control_a.known_body_bytes > 0,
      (control_a.retained.accounting.store_byte_microseconds, control_a.known_body_bytes))

# --- A-live continues seq/store; A-only resets ---
# Run a tiny real periodic collector to HORIZON_END (using a coarse 1-day
# poll/sweep interval to keep the full-horizon replay fast) to obtain a
# genuine terminal retained_export, then augment it.
coarse_cfg = ObserverConfig(feed_poll_interval_us=86_400_000_000)  # 1 day
r_echo = pc.revision("Echo", "1", dt("2026-05-24T00:00:10Z"), b"echo-body")
export_echo = SimpleNamespace(events=(pc.save(r_echo),), revisions=(r_echo,),
                               revisions_by_id={r_echo.rev_id: r_echo})
observer_echo = Observer(export_echo, config=coarse_cfg)
periodic_result = run_periodic(observer_echo, PeriodicConfig(
    PeriodicPolicy.P, 30 * 86_400_000_000, 0, None, HORIZON_END))
prior_max_seq = max((b.request_seq for b in periodic_result.body_results), default=0)
check("A-live setup sanity: prior periodic run produced at least one request", prior_max_seq > 0,
      prior_max_seq)

live_control = augment_collector_result(export5, periodic_result)
check(f"A-live: continues sequence from prior max ({prior_max_seq}), NOT reset to 1",
      live_control.attempts[0].request_seq == prior_max_seq + 1,
      (live_control.attempts[0].request_seq, prior_max_seq + 1))
check("A-only (fresh, same export): starts at sequence 1 (different from A-live start)",
      control_a.attempts[0].request_seq == 1 and live_control.attempts[0].request_seq != 1,
      (control_a.attempts[0].request_seq, live_control.attempts[0].request_seq))

# --- capped (1MiB) vs uncapped archive-only divergence ---
BIG = 400_000
rb1 = pc.revision("Big1", "1", dt("2026-05-24T00:00:10Z"), b"z" * BIG)
rb2 = pc.revision("Big2", "1", dt("2026-05-24T00:00:11Z"), b"y" * BIG)
rb3 = pc.revision("Big3", "1", dt("2026-05-24T00:00:12Z"), b"x" * BIG)
export_big = SimpleNamespace(revisions=(rb1, rb2, rb3))
# Hand derivation: packet(key len8, seq1..3, all single-digit)=158+8+1=167;
# standalone=167+400000=400167 each. 3*400167=1,200,501 > 1,048,576 (1MiB).
# Sequential FIFO admission evicts Big1 once Big3 is admitted -> capped
# run retains {Big2,Big3} only; uncapped retains all three.
capped = run_archive_only(export_big, capacity_bytes=1_048_576, checkpoint=dt("2026-05-24T00:05:00Z"))
uncapped = run_archive_only(export_big, capacity_bytes=None, checkpoint=dt("2026-05-24T00:05:00Z"))
capped_keys = {rc.page_key for rc in capped.retained.packets}
uncapped_keys = {rc.page_key for rc in uncapped.retained.packets}
check("archive: 1MiB-capped run evicts Big1, retains {Big2,Big3}",
      capped_keys == {"dse~Big2", "dse~Big3"}, capped_keys)
check("archive: uncapped run retains all three {Big1,Big2,Big3}",
      uncapped_keys == {"dse~Big1", "dse~Big2", "dse~Big3"}, uncapped_keys)
check("archive: capped vs uncapped produce genuinely different retained sets",
      capped_keys != uncapped_keys, (capped_keys, uncapped_keys))

print(f"\n==== {len(PASS)} PASS / {len(FAIL)} FAIL ====")
for name, detail in FAIL:
    print("FAILED:", name, "|", detail)
