"""Independent recomputation of the nine R04 accounting fixtures (A-I).

Does NOT trust tests/fixtures/accounting/README.md's worked arithmetic.
Rebuilds canonical serialization from R04_ACCOUNTING_AMENDMENT.md's rules
applied to each fixture's raw field *values*, independently re-hashes body
content, and independently re-simulates the FIFO admission algorithm for
E/F/G from the capacities/body sequence given -- then compares the result
against each fixture's own "expected" block.
"""
import hashlib
import json
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "accounting"


def canonical(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8") + b"\n"


def canonical_array(items_bare: list[bytes]) -> bytes:
    # items_bare = each item's canonical bytes WITHOUT its own trailing LF
    return b"[" + b",".join(items_bare) + b"]\n"


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def check(label, actual, expected):
    ok = actual == expected
    print(f"  {'OK ' if ok else 'FAIL'} {label}: got {actual!r} expected {expected!r}")
    return ok


results = {}

# ---------------- A ----------------
print("=== A (feed record) ===")
a = load("A_feed.json")
rec = a["record"]
rec_bytes = canonical(rec)
ok1 = check("record bytes match canonical_record string", rec_bytes, a["canonical_record"].encode("utf-8"))
ok2 = check("record_bytes length", len(rec_bytes), a["expected"]["record_bytes"])
response = canonical_array([rec_bytes[:-1]])
ok3 = check("response bytes match canonical_response string", response, a["canonical_response"].encode("utf-8"))
ok4 = check("downloaded_metadata_bytes", len(response), a["expected"]["downloaded_metadata_bytes"])
empty_resp = canonical_array([])
ok5 = check("empty response bytes", len(empty_resp), a["expected"]["empty_poll_downloaded_metadata_bytes"])
two_ident = canonical_array([rec_bytes[:-1], rec_bytes[:-1]])
ok6 = check("two identical records response bytes", len(two_ident), a["expected"]["two_identical_records_response_bytes"])
two_ident_retained = 2 * len(rec_bytes)
ok7 = check("two identical records retained (JSONL, own LF each, no dedup)", two_ident_retained, a["expected"]["two_identical_records_retained_metadata_bytes"])
results["A"] = all([ok1, ok2, ok3, ok4, ok5, ok6, ok7])

# ---------------- B ----------------
print("=== B (unique body) ===")
b = load("B_unique.json")
pkt = b["packet"]
pkt_bytes = canonical(pkt)
ok1 = check("packet bytes match canonical_packet", pkt_bytes, b["canonical_packet"].encode("utf-8"))
ok2 = check("packet_bytes length", len(pkt_bytes), b["expected"]["packet_bytes"])
body = bytes.fromhex(b["body_utf8_hex"])
ok3 = check("body bytes == body_text utf-8", body, b["body_text"].encode("utf-8"))
ok4 = check("body_bytes length", len(body), b["expected"]["body_bytes"])
ok5 = check("sha256 matches packet's body_sha256", hashlib.sha256(body).hexdigest(), pkt["body_sha256"])
standalone = len(pkt_bytes) + len(body)
ok6 = check("standalone admission (packet+body) fits capacity exactly", standalone, b["capacity_bytes"])
store_path = [0, standalone]
ok7 = check("store_bytes_after_operations", store_path, b["expected"]["store_bytes_after_operations"])
ok8 = check("final/peak store", standalone, b["expected"]["final_store_bytes"])
ok9 = check("store_byte_hours (1 hour at 'standalone')", standalone * 1, b["expected"]["store_byte_hours"])
results["B"] = all([ok1, ok2, ok3, ok4, ok5, ok6, ok7, ok8, ok9])


def independent_fifo(packets_json, bodies_hex, times, cap, dedup):
    """Re-simulate FIFO admission from scratch, contract-rule style.
    Returns dict of computed metrics for comparison."""
    store_path = [0]
    objects = {}  # sha -> [bytes, refcount]
    retained_packets = {}  # seq -> (pkt_bytes_len, sha)
    order = []  # FIFO order of seq
    evicted_seqs = []
    evicted_packet_bytes = 0
    evicted_body_bytes = 0
    candidates_before_eviction = []
    op_names = ["initial"]
    downloaded_metadata = 0
    downloaded_body = 0
    requests = 0

    def current_size():
        return sum(retained_packets[s][0] for s in order) + sum(len(o[0]) for o in objects.values() if o[1] > 0)

    for i, (pkt_str, body_hex) in enumerate(zip(packets_json, bodies_hex), start=1):
        pkt = json.loads(pkt_str)
        pkt_bytes = canonical(pkt)
        assert pkt_bytes == pkt_str.encode("utf-8"), f"packet {i} does not reserialize identically"
        body = bytes.fromhex(body_hex)
        sha = hashlib.sha256(body).hexdigest()
        assert sha == pkt["body_sha256"], f"packet {i} hash mismatch: {sha} vs {pkt['body_sha256']}"
        requests += 1
        downloaded_metadata += 19  # {"outcome":"body"}\n
        downloaded_body += len(body)

        p = len(pkt_bytes)
        obj_key = sha if dedup else ("private", i)  # non-dedup: fresh object every admission, never shared by hash
        need_body_store = not (dedup and sha in objects and objects[sha][1] > 0)
        if p + len(body) > cap:
            # intrinsic oversize -- reject before any eviction attempt
            op_names.append(f"reject_{i}")
            store_path.append(current_size())
            continue

        marginal = p + (len(body) if need_body_store else 0)
        candidate = current_size() + marginal
        while candidate > cap:
            candidates_before_eviction.append(candidate)
            oldest = order.pop(0)
            pb, okey = retained_packets.pop(oldest)
            evicted_seqs.append(oldest)
            evicted_packet_bytes += pb
            objects[okey][1] -= 1
            if objects[okey][1] == 0:
                evicted_body_bytes += len(objects[okey][0])
                del objects[okey]
            op_names.append(f"evict_{len(evicted_seqs)}")
            store_path.append(current_size())
            need_body_store = not (dedup and sha in objects and objects[sha][1] > 0)
            marginal = p + (len(body) if need_body_store else 0)
            candidate = current_size() + marginal

        if obj_key not in objects:
            objects[obj_key] = [body, 0]
        objects[obj_key][1] += 1
        retained_packets[i] = (p, obj_key)
        order.append(i)
        op_names.append(f"admit_{i}")
        store_path.append(current_size())

    return {
        "store_path": store_path,
        "op_names": op_names,
        "evicted_seqs": evicted_seqs,
        "evicted_packet_bytes": evicted_packet_bytes,
        "evicted_body_bytes": evicted_body_bytes,
        "retained_seqs": order,
        "retained_packet_bytes": sum(retained_packets[s][0] for s in order),
        "retained_body_objects": sum(1 for o in objects.values() if o[1] > 0),
        "retained_body_bytes": sum(len(o[0]) for o in objects.values() if o[1] > 0),
        "object_reference_counts": sorted(o[1] for o in objects.values() if o[1] > 0),
        "requests": requests,
        "downloaded_metadata": downloaded_metadata,
        "downloaded_body": downloaded_body,
        "candidates_before_eviction": candidates_before_eviction,
        "final_size": current_size(),
        "peak_size": max(store_path),
    }


def byte_hours(store_path, op_names, hour_marks):
    """store_path[i] holds from hour_marks[i] to hour_marks[i+1]. hour_marks must have
    exactly len(store_path)+1 entries: one per store_path point, plus the final checkpoint."""
    assert len(hour_marks) == len(store_path) + 1, (len(hour_marks), len(store_path))
    total = 0.0
    for i in range(len(store_path)):
        dt = hour_marks[i + 1] - hour_marks[i]
        total += store_path[i] * dt
    return total


print("=== C (duplicate, dedup) ===")
c = load("C_duplicate.json")
r = independent_fifo(c["canonical_packets"], [c["body_utf8_hex"]] * 2, None, c["capacity_bytes"], c["deduplicate"])
ok1 = check("store_bytes_after_operations", r["store_path"], c["expected"]["store_bytes_after_operations"])
ok2 = check("retained_packet_bytes", r["retained_packet_bytes"], c["expected"]["retained_packet_bytes"])
ok3 = check("retained_body_objects", r["retained_body_objects"], c["expected"]["retained_body_objects"])
ok4 = check("object_reference_counts", r["object_reference_counts"], c["expected"]["object_reference_counts"])
ok5 = check("evicted_request_seqs", r["evicted_seqs"], c["expected"]["evicted_request_seqs"])
ok6 = check("request_count", r["requests"], c["expected"]["request_count"])
ok7 = check("downloaded_metadata_bytes", r["downloaded_metadata"], c["expected"]["downloaded_metadata_bytes"])
ok8 = check("downloaded_body_bytes", r["downloaded_body"], c["expected"]["downloaded_body_bytes"])
ok9 = check("peak_store_bytes", r["peak_size"], c["expected"]["peak_store_bytes"])
ok10 = check("final_store_bytes", r["final_size"], c["expected"]["final_store_bytes"])
bh = byte_hours(r["store_path"], r["op_names"], [0, 0, 1, 2])  # initial@t0(not real), admit1@0,admit2@1,checkpoint@2
ok11 = check("store_byte_hours", bh, c["expected"]["store_byte_hours"])
results["C"] = all([ok1, ok2, ok3, ok4, ok5, ok6, ok7, ok8, ok9, ok10, ok11])

print("=== D (duplicate, no dedup) ===")
d = load("D_nondedup.json")
r = independent_fifo(d["canonical_packets"], [d["body_utf8_hex"]] * 2, None, d["capacity_bytes"], d["deduplicate"])
ok1 = check("store_bytes_after_operations", r["store_path"], d["expected"]["store_bytes_after_operations"])
ok2 = check("retained_packet_bytes", r["retained_packet_bytes"], d["expected"]["retained_packet_bytes"])
ok3 = check("retained_body_objects", r["retained_body_objects"], d["expected"]["retained_body_objects"])
ok4 = check("object_reference_counts", r["object_reference_counts"], d["expected"]["object_reference_counts"])
ok5 = check("request_count", r["requests"], d["expected"]["request_count"])
ok6 = check("downloaded_metadata_bytes", r["downloaded_metadata"], d["expected"]["downloaded_metadata_bytes"])
ok7 = check("downloaded_body_bytes", r["downloaded_body"], d["expected"]["downloaded_body_bytes"])
ok8 = check("peak_store_bytes", r["peak_size"], d["expected"]["peak_store_bytes"])
ok9 = check("final_store_bytes", r["final_size"], d["expected"]["final_store_bytes"])
bh = byte_hours(r["store_path"], r["op_names"], [0, 0, 1, 2])
ok10 = check("store_byte_hours", bh, d["expected"]["store_byte_hours"])
results["D"] = all([ok1, ok2, ok3, ok4, ok5, ok6, ok7, ok8, ok9, ok10])

print("=== E (FIFO double eviction) ===")
e = load("E_fifo.json")
r = independent_fifo(e["canonical_packets"], e["body_utf8_hex_in_request_order"], None, e["capacity_bytes"], e["deduplicate"])
ok1 = check("store_bytes_after_operations", r["store_path"], e["expected"]["store_bytes_after_operations"])
ok2 = check("op_names shape (6 entries incl initial)", len(r["op_names"]), len(e["expected"]["operation_names"]))
ok3 = check("candidates_before_eviction", r["candidates_before_eviction"], e["expected"]["request_3_candidate_totals_before_each_eviction"])
ok4 = check("evicted_request_seqs", r["evicted_seqs"], e["expected"]["evicted_request_seqs"])
ok5 = check("evicted_packet_bytes", r["evicted_packet_bytes"], e["expected"]["evicted_packet_bytes"])
ok6 = check("evicted_body_bytes", r["evicted_body_bytes"], e["expected"]["evicted_body_bytes"])
ok7 = check("retained_request_seqs", r["retained_seqs"], e["expected"]["retained_request_seqs"])
ok8 = check("retained_packet_bytes", r["retained_packet_bytes"], e["expected"]["retained_packet_bytes"])
ok9 = check("requests", r["requests"], e["expected"]["request_count"])
ok10 = check("downloaded_metadata_bytes", r["downloaded_metadata"], e["expected"]["downloaded_metadata_bytes"])
ok11 = check("downloaded_body_bytes", r["downloaded_body"], e["expected"]["downloaded_body_bytes"])
ok12 = check("peak_store_bytes", r["peak_size"], e["expected"]["peak_store_bytes"])
ok13 = check("final_store_bytes", r["final_size"], e["expected"]["final_store_bytes"])
bh = byte_hours(r["store_path"], r["op_names"], [0, 0, 1, 2, 2, 2, 3])
ok14 = check("store_byte_hours", bh, e["expected"]["store_byte_hours"])
results["E"] = all([ok1, ok3, ok4, ok5, ok6, ok7, ok8, ok9, ok10, ok11, ok12, ok13, ok14])

print("=== F (oversize rejection) ===")
f = load("F_oversize.json")
r = independent_fifo(f["canonical_packets"], f["body_utf8_hex_in_request_order"], None, f["capacity_bytes"], f["deduplicate"])
ok1 = check("store_bytes_after_operations", r["store_path"], f["expected"]["store_bytes_after_operations"])
ok2 = check("evicted_request_seqs", r["evicted_seqs"], f["expected"]["evicted_request_seqs"])
ok3 = check("retained_request_seqs", r["retained_seqs"], f["expected"]["retained_request_seqs"])
ok4 = check("requests", r["requests"], f["expected"]["request_count"])
ok5 = check("downloaded_metadata_bytes", r["downloaded_metadata"], f["expected"]["downloaded_metadata_bytes"])
ok6 = check("downloaded_body_bytes", r["downloaded_body"], f["expected"]["downloaded_body_bytes"])
ok7 = check("peak_store_bytes", r["peak_size"], f["expected"]["peak_store_bytes"])
ok8 = check("final_store_bytes", r["final_size"], f["expected"]["final_store_bytes"])
bh = byte_hours(r["store_path"], r["op_names"], [0, 0, 1, 2])
ok9 = check("store_byte_hours", bh, f["expected"]["store_byte_hours"])
results["F"] = all([ok1, ok2, ok3, ok4, ok5, ok6, ok7, ok8, ok9])

print("=== G (shared FIFO, dup body survives) ===")
g = load("G_shared_fifo.json")
r = independent_fifo(g["canonical_packets"], [g["body_utf8_hex"]] * 3, None, g["capacity_bytes"], g["deduplicate"])
ok1 = check("store_bytes_after_operations", r["store_path"], g["expected"]["store_bytes_after_operations"])
ok2 = check("candidate before eviction", r["candidates_before_eviction"][0] if r["candidates_before_eviction"] else None, g["expected"]["request_3_candidate_total_before_eviction"])
ok3 = check("evicted_request_seqs", r["evicted_seqs"], g["expected"]["evicted_request_seqs"])
ok4 = check("evicted_packet_bytes", r["evicted_packet_bytes"], g["expected"]["evicted_packet_bytes"])
ok5 = check("evicted_body_bytes", r["evicted_body_bytes"], g["expected"]["evicted_body_bytes"])
ok6 = check("retained_request_seqs", r["retained_seqs"], g["expected"]["retained_request_seqs"])
ok7 = check("retained_packet_bytes", r["retained_packet_bytes"], g["expected"]["retained_packet_bytes"])
ok8 = check("object_reference_counts", r["object_reference_counts"], g["expected"]["object_reference_counts"])
ok9 = check("requests", r["requests"], g["expected"]["request_count"])
ok10 = check("downloaded_metadata_bytes", r["downloaded_metadata"], g["expected"]["downloaded_metadata_bytes"])
ok11 = check("peak_store_bytes", r["peak_size"], g["expected"]["peak_store_bytes"])
ok12 = check("final_store_bytes", r["final_size"], g["expected"]["final_store_bytes"])
bh = byte_hours(r["store_path"], r["op_names"], [0, 0, 1, 2, 2, 3])
ok13 = check("store_byte_hours", bh, g["expected"]["store_byte_hours"])
results["G"] = all([ok1, ok2, ok3, ok4, ok5, ok6, ok7, ok8, ok9, ok10, ok11, ok12, ok13])

print("=== H (protocol headers / directory) ===")
h = load("H_protocol.json")
outcomes = h["body_responses"]
total_meta = 0
ok_all = True
for resp in outcomes:
    hdr = canonical({"outcome": resp["outcome"]})
    ok = check(f"header bytes for {resp['outcome']}", len(hdr), resp["header_bytes"])
    ok_all = ok_all and ok
    total_meta += len(hdr)
ok1 = check("total downloaded_metadata_bytes", total_meta, h["expected_response_totals"]["downloaded_metadata_bytes"])
for case in h["directory_cases_independent_of_each_other"]:
    arr = canonical_array([json.dumps(k, ensure_ascii=False).encode("utf-8") for k in case["page_keys"]])
    ok = check(f"directory bytes for {case['page_keys']}", len(arr), case["downloaded_metadata_bytes"])
    ok_all = ok_all and ok
results["H"] = ok_all and ok1

print("=== I (encoding/transcoding) ===")
i = load("I_encoding.json")
ok_all = True
for case in i["source_cases"]:
    src = bytes.fromhex(case["source_hex"])
    if case["encoding"] == "latin-1":
        text = src.decode("latin-1")
    else:
        text = src.decode("utf-8")
    canon = text.encode("utf-8")
    ok1 = check(f"{case['encoding']} canonical bytes", canon, bytes.fromhex(case["canonical_utf8_hex"]))
    ok2 = check(f"{case['encoding']} canonical length", len(canon), case["canonical_body_bytes"])
    ok3 = check(f"{case['encoding']} sha256", hashlib.sha256(canon).hexdigest(), case["canonical_sha256"])
    ok_all = ok_all and ok1 and ok2 and ok3
generic = canonical(i["generic_metadata_value_not_a_feed_or_packet"])
ok4 = check("generic metadata bytes match canonical string", generic, i["canonical_generic_metadata"].encode("utf-8"))
ok5 = check("generic metadata length", len(generic), i["expected_generic_metadata_bytes"])
probe_obj = {"body_sha256": "4a99557e4033c3539de2eb65472017cad5f9557f7a0625a09f1c3f6e2ba69c4c", "capture_time": "2026-05-24T00:00:00.000000Z", "page_key": "dse~é", "request_seq": 10}
probe_bytes = canonical(probe_obj)
ok6 = check("packet width probe matches string", probe_bytes, i["canonical_packet_width_probe"].encode("utf-8"))
ok7 = check("packet width probe length", len(probe_bytes), i["expected_packet_width_probe_bytes"])
ok8 = check("standalone with e-acute body", len(probe_bytes) + 2, i["expected_standalone_with_e_acute_body_bytes"])
results["I"] = ok_all and ok4 and ok5 and ok6 and ok7 and ok8

print("\n" + "=" * 40)
print("SUMMARY")
for k, v in results.items():
    print(f"  {k}: {'PASS' if v else 'FAIL'}")
print(f"\n{sum(results.values())}/9 independently confirmed")
