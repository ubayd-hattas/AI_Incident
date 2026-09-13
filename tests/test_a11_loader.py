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
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ebe.a11_loader import load_real_propositions  # noqa: E402
from ebe.evaluator import validate_population  # noqa: E402


class A11LoaderStructuralTests(unittest.TestCase):
    def test_loads_all_65_propositions(self) -> None:
        propositions, fragments = load_real_propositions()
        self.assertEqual(len(propositions), 65)

    def test_passes_the_population_firewall(self) -> None:
        propositions, fragments = load_real_propositions()
        validate_population(propositions, fragments)  # raises on any violation

    def test_eligibility_wiring_matches_eligibility_jsonl(self) -> None:
        propositions, _ = load_real_propositions()
        ineligible = [p.evidence_id for p in propositions if not p.eligible]
        self.assertEqual(ineligible, ["PROP-20260618-63"])
        prop = next(p for p in propositions if p.evidence_id == "PROP-20260618-63")
        self.assertIsNotNone(prop.eligibility_reason)
        self.assertIn("head-mismatch", prop.eligibility_reason)

    def test_multi_span_proposition_gets_one_fragment_per_span(self) -> None:
        propositions, fragments = load_real_propositions()
        prop = next(p for p in propositions if p.evidence_id == "PROP-20260619-01")
        self.assertEqual(len(prop.core_alternatives), 1)  # one AND-alternative
        self.assertEqual(len(prop.core_alternatives[0]), 2)  # two fragments (two spans)
        for fragment_id in prop.core_alternatives[0]:
            self.assertIn(fragment_id, fragments)

    def test_no_context_alternatives_modeled_yet(self) -> None:
        # Explicitly documents the current limitation -- context fragments
        # don't exist yet (acceptance-matrix item C context half).
        propositions, _ = load_real_propositions()
        self.assertTrue(all(p.context_alternatives == () for p in propositions))


if __name__ == "__main__":
    unittest.main()
