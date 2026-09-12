from __future__ import annotations

import json
import sys
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ebe import HORIZON_END, HORIZON_START, OutOfHorizonError, TraceModel, load_export  # noqa: E402
from ebe.schema import RelationEdge  # noqa: E402
from ebe.timeline import StateKind, UnsupportedMutationError  # noqa: E402


PINNED = ROOT / "data" / "raw" / "export"
FIXTURE = ROOT / "tests" / "fixtures" / "manual" / "released_v02.json"
UTC = timezone.utc
US = timedelta(microseconds=1)


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class ReleasedManualFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.export = load_export(PINNED)
        cls.model = TraceModel(cls.export)
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_01_all_76_released_boundaries_before_at_after(self) -> None:
        checked = 0
        for case in self.fixture["cases"]:
            key = case["page_key"]
            ids = []
            if case["revision_range"]:
                first, last = case["revision_range"]
                ids.extend(f"save:{key}@{number}" for number in range(first, last + 1))
            ids.extend(case.get("deletions", ()))
            ids.extend(case.get("body_unknown", ()))
            events = sorted((self.export.events_by_id[item] for item in ids), key=lambda x: x.time.utc)
            expected_kind = StateKind.UNKNOWN
            expected_revision = None
            for event in events:
                before = self.model.state_at(key, event.time.utc - US).alternatives
                self.assertEqual(len(before), 1, event.event_id)
                self.assertEqual(before[0].state.kind, expected_kind, event.event_id)
                self.assertEqual(
                    before[0].state.body_ref.rev_id if before[0].state.body_ref else None,
                    expected_revision,
                    event.event_id,
                )
                if event.event_type.value == "save":
                    expected_kind = StateKind.LIVE_BODY
                    expected_revision = event.revision_ref
                elif event.event_type.value == "delete":
                    expected_kind = StateKind.DELETED
                    expected_revision = None
                else:
                    expected_kind = StateKind.LIVE_BODY_UNKNOWN
                    expected_revision = None
                for when in (event.time.utc, event.time.utc + US):
                    alternative = self.model.state_at(key, when).alternatives
                    self.assertEqual(len(alternative), 1, event.event_id)
                    state = alternative[0].state
                    self.assertEqual(state.kind, expected_kind, event.event_id)
                    self.assertEqual(state.body_ref.rev_id if state.body_ref else None, expected_revision)
                    if state.body_ref:
                        revision = self.export.revisions_by_id[expected_revision]
                        self.assertEqual(state.body_ref.body_sha256, revision.body_sha256)
                        self.assertEqual(state.body_ref.source_bytes, revision.source_body_bytes)
                checked += 1
        self.assertEqual(checked, 76)

    def test_02_archive_clocks_are_inspectable_no_ops(self) -> None:
        for case in self.fixture["cases"]:
            timeline = self.model.timeline(case["page_key"])
            marker_times = {marker.timestamp for marker in timeline.ignored_markers}
            for raw_time, expected_revision in case["archive_no_ops"]:
                timestamp = dt(raw_time)
                self.assertIn(timestamp, marker_times)
                state = timeline.state_at(timestamp).alternatives[0].state
                self.assertEqual(state.kind, StateKind.LIVE_BODY)
                self.assertEqual(state.body_ref.rev_id, expected_revision)

    def test_03_episode_and_censoring_anchors(self) -> None:
        key = "dse~AgentLinkma21JuneAA"
        first_episode = self.model.state_at(key, dt("2026-06-18T18:26:11Z")).alternatives[0]
        deleted = self.model.state_at(key, dt("2026-06-18T18:26:23Z")).alternatives[0]
        second_episode = self.model.state_at(key, dt("2026-06-18T18:29:39Z")).alternatives[0]
        self.assertEqual(first_episode.current_episode_id, "episode:save:dse~AgentLinkma21JuneAA@1")
        self.assertIsNone(deleted.current_episode_id)
        self.assertEqual(deleted.last_ended_episode_id, first_episode.current_episode_id)
        self.assertEqual(second_episode.current_episode_id, "episode:save:dse~AgentLinkma21JuneAA@16")
        final = self.model.state_at("dse~AgentBridgeOct2142X", HORIZON_END).alternatives[0]
        self.assertTrue(final.censoring.observation_end)
        self.assertTrue(final.censoring.live_episode_right_censored)

    def test_04_body_unknown_and_all_four_audited_classifications(self) -> None:
        rows = [event for event in self.export.events if event.event_type.value == "revert"]
        self.assertEqual(len(rows), 4)
        for event in rows:
            state = self.model.state_at(event.page_key, event.time.utc).alternatives[0].state
            self.assertEqual(state.kind, StateKind.LIVE_BODY_UNKNOWN)
            self.assertIsNone(state.body_ref)

    def test_05_unrecognized_opaque_key_and_horizon(self) -> None:
        state = self.model.state_at("../still-an-opaque-key", HORIZON_START).alternatives[0].state
        self.assertEqual(state.kind, StateKind.UNKNOWN)
        for outside in (HORIZON_START - US, HORIZON_END + US):
            with self.assertRaises(OutOfHorizonError):
                self.model.state_at("anything", outside)

    def test_06_official_query_uncertainty_boundaries(self) -> None:
        key = "dse~AgentOfficialDirectQueryAA3"
        at_35 = self.model.state_at(key, dt("2026-06-24T10:43:35Z"), mode="uncertainty")
        self.assertEqual({alt.state.kind for alt in at_35.alternatives}, {StateKind.LIVE_BODY, StateKind.DELETED})
        at_37 = self.model.state_at(key, dt("2026-06-24T10:43:37Z"), mode="uncertainty")
        self.assertEqual({alt.state.kind for alt in at_37.alternatives}, {StateKind.DELETED})

    def test_07_public_diagnostic_tie_legacy_and_control(self) -> None:
        tie_key = "dse~AgentNacoPovertyTexas2015XQ"
        tie_time = self.export.revisions_by_id[f"{tie_key}@22"].time.utc
        before = self.model.state_at(tie_key, tie_time - US).alternatives
        self.assertEqual({alt.state.body_ref.rev_id for alt in before}, {f"{tie_key}@21"})
        at = self.model.state_at(tie_key, tie_time).alternatives
        self.assertEqual({alt.state.body_ref.rev_id for alt in at}, {f"{tie_key}@22", f"{tie_key}@23"})
        revision_24 = self.export.revisions_by_id[f"{tie_key}@24"]
        converged = self.model.state_at(tie_key, revision_24.time.utc).alternatives
        self.assertTrue(all(alt.state.body_ref.rev_id == revision_24.rev_id for alt in converged))

        ai = self.model.state_at("dse~AI", self.export.revisions_by_id["dse~AI@2"].time.utc)
        self.assertEqual({alt.state.body_ref.rev_id for alt in ai.alternatives}, {"dse~AI@2"})
        control = self.model.state_at("dse~AgentBridgeOct2142X", HORIZON_END)
        self.assertEqual({alt.state.body_ref.rev_id for alt in control.alternatives}, {"dse~AgentBridgeOct2142X@1"})


class SyntheticTimelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        export = load_export(PINNED)
        cls.save_template = next(event for event in export.events if event.event_type.value == "save" and not event.relations.edges)
        cls.revision_template = export.revisions_by_id[cls.save_template.revision_ref]
        cls.delete_template = next(event for event in export.events if event.event_type.value == "delete" and not event.relations.edges)
        cls.bu_template = next(event for event in export.events if event.event_type.value == "revert")

    def revision(self, suffix: str, when: datetime, body: bytes | None = None):
        body = body or suffix.encode("ascii")
        import hashlib
        source_body = body.decode("latin-1")
        return replace(
            self.revision_template,
            rev_id=f"rev-{suffix}", page_key="opaque/synthetic", page_id="synthetic",
            name="synthetic", seq=1, body=source_body, source_body_bytes=body,
            body_len=len(body), body_sha256=hashlib.sha256(body).hexdigest(), time=replace(self.revision_template.time, raw=when.isoformat(), utc=when),
            uncertainty_seconds=1,
        )

    def save(self, revision, event_id: str | None = None, relations: RelationFields | None = None):
        return replace(
            self.save_template, event_id=event_id or f"save-{revision.rev_id}", page_key="opaque/synthetic",
            page="synthetic", revision_ref=revision.rev_id, time=revision.time,
            relations=relations or self.save_template.relations,
        )

    def delete(self, suffix: str, when: datetime):
        return replace(
            self.delete_template, event_id=f"delete-{suffix}", page_key="opaque/synthetic", page="synthetic",
            time=replace(self.delete_template.time, raw=when.isoformat(), utc=when), uncertainty_seconds=1,
        )

    def bu(self, suffix: str, when: datetime):
        return replace(
            self.bu_template, event_id=f"bu-{suffix}", page_key="opaque/synthetic", page="synthetic",
            time=replace(self.bu_template.time, raw=when.isoformat(), utc=when), uncertainty_seconds=1,
        )

    def model(self, events, revisions):
        return TraceModel(SimpleNamespace(events=tuple(events), revisions=tuple(revisions), revisions_by_id={r.rev_id: r for r in revisions}))

    def test_08_basic_delete_recreate_body_unknown_and_replacement(self) -> None:
        base = dt("2026-06-10T00:00:00Z")
        a = self.revision("A", base)
        b = self.revision("B", base + timedelta(seconds=2))
        c = self.revision("C", base + timedelta(seconds=4))
        events = [
            self.save(a),
            self.bu("one", base + timedelta(seconds=1)),
            self.save(b),
            self.delete("one", base + timedelta(seconds=3)),
            self.save(c),
        ]
        model = self.model(events, [a, b, c])
        expected = [
            StateKind.LIVE_BODY,
            StateKind.LIVE_BODY_UNKNOWN,
            StateKind.LIVE_BODY,
            StateKind.DELETED,
            StateKind.LIVE_BODY,
        ]
        for event, kind in zip(events, expected):
            self.assertEqual(model.state_at("opaque/synthetic", event.time.utc).alternatives[0].state.kind, kind)
        unknown_body = model.state_at("opaque/synthetic", events[1].time.utc).alternatives[0].state
        self.assertIsNone(unknown_body.body_ref)
        self.assertEqual(model.state_at("opaque/synthetic", c.time.utc).alternatives[0].state.body_ref.rev_id, "rev-C")

    def test_09_same_time_ambiguity_and_later_convergence(self) -> None:
        base = dt("2026-06-10T00:00:00Z")
        a, b, c = (self.revision(name, base if name != "C" else base + timedelta(seconds=5)) for name in "ABC")
        tied = self.model([self.save(a), self.save(b), self.delete("tie", base), self.save(c)], [a, b, c])
        at = tied.state_at("opaque/synthetic", base)
        self.assertEqual(
            {alt.state.body_ref.rev_id if alt.state.body_ref else alt.state.kind.value for alt in at.alternatives},
            {"rev-A", "rev-B", StateKind.DELETED.value},
        )
        converged = tied.state_at("opaque/synthetic", c.time.utc)
        self.assertTrue(all(alt.state.body_ref.rev_id == "rev-C" for alt in converged.alternatives))
        self.assertGreater(len(converged.alternatives), 1)

    def test_10_identical_body_ties_keep_distinct_provenance(self) -> None:
        base = dt("2026-06-10T00:00:00Z")
        a, b = self.revision("A", base, b"same"), self.revision("B", base, b"same")
        query = self.model([self.save(a), self.save(b)], [a, b]).state_at("opaque/synthetic", base)
        self.assertEqual(len(query.alternatives), 2)
        self.assertEqual({alt.state.body_ref.rev_id for alt in query.alternatives}, {"rev-A", "rev-B"})
        self.assertEqual(len({alt.state.body_ref.body_sha256 for alt in query.alternatives}), 1)

    def test_11_future_suffix_and_relation_metadata_do_not_leak(self) -> None:
        base = dt("2026-06-10T00:00:00Z")
        a, future = self.revision("A", base), self.revision("future", base + timedelta(days=1))
        edge = RelationEdge("first_recreation_of", "delete-unseen", "round")
        relation = replace(self.save_template.relations, edges=(edge,))
        prefix = self.model([self.save(a)], [a])
        suffix = self.model([self.save(a), self.save(future, relations=relation)], [a, future])
        for mode in ("nominal", "uncertainty"):
            first = prefix.state_at("opaque/synthetic", base + timedelta(hours=1), mode=mode)
            second = suffix.state_at("opaque/synthetic", base + timedelta(hours=1), mode=mode)
            self.assertEqual({x.state for x in first.alternatives}, {x.state for x in second.alternatives})

    def test_12_touching_windows_and_missing_prehistory(self) -> None:
        base = dt("2026-06-10T00:00:00Z")
        a = self.revision("A", base)
        delete = self.delete("touch", base + timedelta(seconds=2))
        query = self.model([self.save(a), delete], [a]).state_at(
            "opaque/synthetic", base + timedelta(seconds=1), mode="uncertainty"
        )
        # The save is certain at its closed upper endpoint while the touching
        # deletion may also occur there, with event-before-read semantics.
        self.assertEqual(
            {alt.state.kind for alt in query.alternatives},
            {StateKind.LIVE_BODY, StateKind.DELETED},
        )
        self.assertTrue(all(alt.censoring.left_censored for alt in query.alternatives))

    def test_13_repeated_delete_and_fail_closed_outcome(self) -> None:
        base = dt("2026-06-10T00:00:00Z")
        first, second = self.delete("one", base), self.delete("two", base + timedelta(seconds=3))
        query = self.model([first, second], []).state_at("opaque/synthetic", second.time.utc)
        self.assertEqual(query.alternatives[0].state.kind, StateKind.DELETED)
        self.assertIsNone(query.alternatives[0].current_episode_id)
        bad = replace(first, success_observed=False)
        with self.assertRaises(UnsupportedMutationError):
            self.model([bad], [])
        unknown_uncertainty = replace(first, uncertainty_seconds=None)
        with self.assertRaises(UnsupportedMutationError):
            self.model([unknown_uncertainty], [])


if __name__ == "__main__":
    unittest.main()
