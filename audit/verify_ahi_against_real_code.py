"""Closes a real gap the pre-results audit (D04) correctly identified: fixtures
A/H/I were previously only checked against Sam's own from-scratch simulator
(`audit/verify_accounting.py`, which imports no `ebe` code at all -- confirmed
by inspection, it predates E08's implementation). B-G were re-run against the
real `src/ebe/{observer,storage,accounting}.py` in `audit/verify_e08_neutrality.py`,
but A/H/I never were. This script drives A/H/I's exact claims through the real
shipped code, not a simulator, closing that gap for real rather than just
disclosing it.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "audit"))

import hashlib
from ebe.accounting import canonical_jsonl
from ebe.observer import BodyOutcome, Observer, ObserverConfig
from ebe.storage import Capture
from ebe.timeline import HORIZON_START
from ebe.schema import BodyEncoding
from verify_collectors_cross_policy import Mut, build_export, M  # noqa: E402

FAILURES: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    status = "PASS" if cond else "FAIL"
    print(f"  {status} {label}" + (f" -- {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(f"{label}: {detail}")


print("=== A: feed record + array framing, against the real Observer ===")
export_a = build_export([Mut("save", "A", HORIZON_START, "x", 1)])
obs_a = Observer(export_a, config=ObserverConfig(feed_publication_lag_us=0))
poll = obs_a.poll_feed(HORIZON_START)
check("one delivered record's own canonical JSONL is 87 bytes (README A)", len(poll.records[0].canonical_bytes) == 87, str(len(poll.records[0].canonical_bytes)))
check("one-record array response is 89 downloaded metadata bytes (README A)", len(poll.response_bytes) == 89, str(len(poll.response_bytes)))
export_a_empty = build_export([])
obs_a_empty = Observer(export_a_empty)
poll_empty = obs_a_empty.poll_feed(HORIZON_START)
check("an empty poll costs exactly 3 bytes ('[]'+LF) (README A subcase)", len(poll_empty.response_bytes) == 3, str(len(poll_empty.response_bytes)))
export_a_two = build_export([Mut("save", "A", HORIZON_START, "x", 1), Mut("save", "B", HORIZON_START, "y", 1)])
obs_a_two = Observer(export_a_two, config=ObserverConfig(feed_publication_lag_us=0))
poll_two = obs_a_two.poll_feed(HORIZON_START)
check("two records in one poll cost 176 downloaded bytes (README A subcase: 86+86+comma+brackets+LF)", len(poll_two.response_bytes) == 176, str(len(poll_two.response_bytes)))

print("=== H: response outcome headers + terminal directory framing, against the real Observer ===")
EXPECTED_HEADER_BYTES = {
    BodyOutcome.BODY: 19, BodyOutcome.MISSING: 22, BodyOutcome.UNKNOWN: 22,
    BodyOutcome.BODY_UNKNOWN: 27, BodyOutcome.AMBIGUOUS: 24, BodyOutcome.UNSUPPORTED: 26,
}
for outcome, expected in EXPECTED_HEADER_BYTES.items():
    real_header = canonical_jsonl({"outcome": outcome.value})
    check(f"real accounting.canonical_jsonl({{'outcome': {outcome.value!r}}}) is {expected} bytes (README H)", len(real_header) == expected, f"got {len(real_header)}")
check("README H's six outcome headers sum to 140 bytes over 6 requests", sum(EXPECTED_HEADER_BYTES.values()) == 140, str(sum(EXPECTED_HEADER_BYTES.values())))

export_dir_empty = build_export([])
check("empty terminal directory costs 3 bytes ('[]'+LF) (README H)", len(Observer(export_dir_empty).terminal_directory().response_bytes) == 3)
export_dir_one = build_export([Mut("save", "A", HORIZON_START, "x", 1)])
check("one-title terminal directory costs 10 bytes (README H)", len(Observer(export_dir_one).terminal_directory().response_bytes) == 10, str(len(Observer(build_export([Mut('save', 'A', HORIZON_START, 'x', 1)])).terminal_directory().response_bytes)))
export_dir_two = build_export([Mut("save", "A", HORIZON_START, "x", 1), Mut("save", "é", HORIZON_START, "y", 1)])
two_dir_bytes = len(Observer(export_dir_two).terminal_directory().response_bytes)
check("two-title terminal directory (page_keys dse~A, dse~é) costs 19 bytes (README H)", two_dir_bytes == 19, f"got {two_dir_bytes}")

print("=== I: encoding/transcoding equivalence, against the real Observer/schema ===")


def revision_with_encoding(encoding: BodyEncoding, source_bytes: bytes, seq: int = 1):
    export = build_export([Mut("save", "ENC", M(1), "placeholder", seq)])
    rev = export.revisions_by_id[f"dse~ENC@{seq}"]
    import dataclasses
    return dataclasses.replace(rev, body_encoding=encoding, source_body_bytes=source_bytes, body_len=len(source_bytes),
                                body_sha256=hashlib.sha256(source_bytes).hexdigest())


def export_with_revision(rev):
    import dataclasses
    from ebe.schema import NormalizedExport
    ev = None
    base = build_export([Mut("save", "ENC", M(1), "placeholder", 1)])
    ev_id = next(iter(base.events_by_id))
    ev = base.events_by_id[ev_id]
    return dataclasses.replace(base, revisions=(rev,), revisions_by_id={rev.rev_id: rev}, events=(ev,), events_by_id={ev_id: ev})


ascii_rev = revision_with_encoding(BodyEncoding.ASCII, b"abc")
utf8_rev = revision_with_encoding(BodyEncoding.UTF8, "é".encode("utf-8"))
latin1_rev = revision_with_encoding(BodyEncoding.LATIN1, "é".encode("latin-1"))
for name, rev, expected_source_len in (("ASCII abc", ascii_rev, 3), ("UTF-8 é", utf8_rev, 2), ("Latin-1 é", latin1_rev, 1)):
    check(f"{name}: source byte length is {expected_source_len} (README I)", len(rev.source_body_bytes) == expected_source_len, str(len(rev.source_body_bytes)))

obs_utf8 = Observer(export_with_revision(utf8_rev))
obs_utf8.poll_feed(M(2))
resp_utf8 = obs_utf8.get_body("dse~ENC", M(2))
obs_latin1 = Observer(export_with_revision(latin1_rev))
obs_latin1.poll_feed(M(2))
resp_latin1 = obs_latin1.get_body("dse~ENC", M(2))
check("UTF-8-encoded é and Latin-1-encoded é decode to the IDENTICAL canonical 2-byte UTF-8 body through the real Observer (README I)", resp_utf8.body == resp_latin1.body == "é".encode("utf-8"), f"utf8={resp_utf8.body} latin1={resp_latin1.body}")
check("their SHA-256 (real hashlib on real canonical bytes) is identical -- one shared object regardless of source encoding", hashlib.sha256(resp_utf8.body).hexdigest() == hashlib.sha256(resp_latin1.body).hexdigest())

empty_ascii_rev = revision_with_encoding(BodyEncoding.ASCII, b"")
obs_empty = Observer(export_with_revision(empty_ascii_rev))
obs_empty.poll_feed(M(2))
resp_empty = obs_empty.get_body("dse~ENC", M(2))
check("empty known ASCII body decodes to b'' (genuine known-empty, not an unknown sentinel) (README I)", resp_empty.outcome is BodyOutcome.BODY and resp_empty.body == b"")
check("empty body's real SHA-256 is the well-known empty-string digest", hashlib.sha256(resp_empty.body).hexdigest() == hashlib.sha256(b"").hexdigest())

generic_probe = {"flag": False, "n": None, "s": 10, "z": "é", "esc": "\n\"\\"}
real_probe_bytes = canonical_jsonl(generic_probe)
print(f"  INFO real canonical_jsonl output for the generic serializer probe: {real_probe_bytes!r} ({len(real_probe_bytes)} bytes)")
check("generic serializer probe (false/null/int/é/escapes) round-trips through the real serializer without raising, and literal é/escapes are preserved (not ASCII-escaped)", "é".encode("utf-8") in real_probe_bytes and b"\\n" in real_probe_bytes and b"\\\"" in real_probe_bytes and b"\\\\" in real_probe_bytes)

capture_a = Capture("dse~A", M(0), 1, "é".encode("utf-8"))
capture_e9 = Capture("dse~e9", M(0), 10, "é".encode("utf-8"))
check("packet width increases by exactly 2 bytes when page_key grows by 1 char and request_seq grows from 1 digit to 2 digits (README I packet-width probe)", len(capture_e9.packet_bytes) - len(capture_a.packet_bytes) == 2, f"A={len(capture_a.packet_bytes)} e9={len(capture_e9.packet_bytes)}")

print("\n" + "=" * 60)
print(f"A/H/I REAL-CODE VERIFICATION FAILURES: {len(FAILURES)}")
for f in FAILURES:
    print("  -", f)
