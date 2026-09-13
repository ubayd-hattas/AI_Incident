"""Structural-only tests for src/ebe/a11_loader.py.

IMPORTANT: these tests confirm the loader produces well-formed data (passes
the A05 population firewall, right counts, right eligibility wiring). They
deliberately do NOT run compute_core_coverage/compute_delay against any
collector output -- doing so against real capture data would be "semantic
scoring against real captures," which X13_RUN_CONTRACT.md SS9 explicitly
does not authorize yet (blocked on acceptance-matrix items C's context half
and D's near-copy review). Structural loading and firewall validation are
not scoring; they are checked here.
"""
from __future__ import annotations

import sys
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ebe.a11_loader import _canonical_body_bytes, _raw_body_bytes, load_a11_benchmark  # noqa: E402
from ebe.evaluator import DenominatorFirewallError, validate_population  # noqa: E402


class A11LoaderStructuralTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.benchmark = load_a11_benchmark()

    def test_loads_all_65_propositions(self) -> None:
        propositions = self.benchmark.propositions
        self.assertEqual(len(propositions), 65)

    def test_passes_the_population_firewall(self) -> None:
        propositions, fragments = self.benchmark.propositions, self.benchmark.fragments_by_id
        validate_population(propositions, fragments)  # raises on any violation

    def test_alternative_specific_eligibility_excludes_only_bad_anchor(self) -> None:
        prop = next(p for p in self.benchmark.propositions if p.evidence_id == "PROP-20260618-63")
        self.assertTrue(prop.eligible)
        self.assertEqual(len(prop.core_alternatives), 1)
        self.assertTrue(all("dse~AI@2" not in fragment_id for alt in prop.core_alternatives for fragment_id in alt))
        self.assertTrue(all("dse~AgentSecCountyVarAI@1" in fragment_id for alt in prop.core_alternatives for fragment_id in alt))

    def test_multi_span_proposition_gets_one_fragment_per_span(self) -> None:
        propositions, fragments = self.benchmark.propositions, self.benchmark.fragments_by_id
        prop = next(p for p in propositions if p.evidence_id == "PROP-20260619-01")
        self.assertEqual(len(prop.core_alternatives), 30)  # anchor + 29 cumulative revisions
        self.assertTrue(all(len(alt) == 2 for alt in prop.core_alternatives))
        self.assertTrue(all(fid in fragments for alt in prop.core_alternatives for fid in alt))

    def test_context_alternatives_are_finally_compiled(self) -> None:
        propositions = self.benchmark.propositions
        self.assertTrue(all(p.context_alternatives for p in propositions))
        self.assertEqual(sum(p.context_state == "required" for p in propositions), 8)

    def test_group_split_leakage_is_rejected(self) -> None:
        source = ROOT / "annotations"
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            paths = {}
            for name in ("evidence.jsonl", "occurrences.jsonl", "eligibility.jsonl", "splits.json"):
                paths[name] = temp / name
                paths[name].write_bytes((source / name).read_bytes())
            splits = json.loads(paths["splits.json"].read_text(encoding="utf-8"))
            group = splits["splits"]["dev"]["group_ids"].pop(0)
            splits["splits"]["held_out"]["group_ids"].append(group)
            paths["splits.json"].write_text(json.dumps(splits), encoding="utf-8")
            with self.assertRaises(DenominatorFirewallError):
                load_a11_benchmark(
                    paths["evidence.jsonl"], paths["occurrences.jsonl"],
                    paths["eligibility.jsonl"], paths["splits.json"],
                )

    def test_frozen_split_and_denominator_properties(self) -> None:
        propositions = self.benchmark.propositions
        self.assertEqual(sum(p.split == "dev" for p in propositions), 38)
        self.assertEqual(sum(p.split == "held_out" for p in propositions), 27)
        self.assertEqual(sum(p.eligible for p in propositions), 65)
        self.assertEqual(sum(p.split == "held_out" and p.critical and p.eligible for p in propositions), 23)

    def test_occurrences_are_alternatives_not_evidence_units(self) -> None:
        prop = next(p for p in self.benchmark.propositions if p.evidence_id == "PROP-20260619-01")
        self.assertEqual(self.benchmark.validation.occurrence_count, 1421)
        self.assertEqual(sum(p.evidence_id == prop.evidence_id for p in self.benchmark.propositions), 1)
        self.assertGreater(len(prop.core_alternatives), 1)

    def test_claim_status_is_loaded_without_upgrade(self) -> None:
        prop = next(p for p in self.benchmark.propositions if p.evidence_id == "PROP-20260619-03")
        self.assertEqual(prop.claim_status, "agent-reported action/result")

    def test_context_axis_is_frozen(self) -> None:
        self.assertEqual(self.benchmark.context_status, "FROZEN")
        self.assertTrue(self.benchmark.validation.valid)


class A11RawBodyEncodingTests(unittest.TestCase):
    def test_ascii_projection_reconstructs_source_and_canonical_bytes(self) -> None:
        self.assertEqual(_raw_body_bytes("plain ASCII"), b"plain ASCII")
        self.assertEqual(_canonical_body_bytes("plain ASCII", "ascii"), b"plain ASCII")

    def test_utf8_projection_is_reversed_before_declared_encoding_is_interpreted(self) -> None:
        projection = b"T\xc3\xbcrkiye".decode("latin-1")
        self.assertEqual(_raw_body_bytes(projection), b"T\xc3\xbcrkiye")
        self.assertEqual(_canonical_body_bytes(projection, "utf8"), "Türkiye".encode("utf-8"))

    def test_latin1_projection_is_reversed_before_canonicalization(self) -> None:
        projection = b"caf\xe9".decode("latin-1")
        self.assertEqual(_raw_body_bytes(projection), b"caf\xe9")
        self.assertEqual(_canonical_body_bytes(projection, "latin1"), "café".encode("utf-8"))

    def test_real_frozen_files_have_no_encoding_provenance_defects(self) -> None:
        benchmark = load_a11_benchmark(fail_on_error=False)
        provenance_mismatches = {
            issue.message for issue in benchmark.validation.issues
            if issue.code in {"EVIDENCE_BODY_HASH_MISMATCH", "OCCURRENCE_BODY_HASH_MISMATCH"}
        }
        self.assertEqual(provenance_mismatches, set())


if __name__ == "__main__":
    unittest.main()
