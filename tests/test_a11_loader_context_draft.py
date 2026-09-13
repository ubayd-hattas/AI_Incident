"""Structural-only tests for src/ebe/a11_loader_context_draft.py (Sam's DRAFT
context axis -- not accepted ground truth, see
docs/A11_CONTEXT_AXIS_DRAFT_SAM.md).

As with tests/test_a11_loader.py, these confirm the draft loads and passes
the population firewall. They do NOT run coverage/delay scoring against any
collector output -- that remains unauthorized regardless of whether the
context data is real or draft.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ebe.a11_loader_context_draft import load_draft_context  # noqa: E402
from ebe.evaluator import validate_population  # noqa: E402


class DraftContextStructuralTests(unittest.TestCase):
    def test_loads_all_65_with_context(self) -> None:
        propositions, fragments, eligibility = load_draft_context()
        self.assertEqual(len(propositions), 65)
        self.assertTrue(all(p.context_alternatives for p in propositions))

    def test_passes_the_population_firewall(self) -> None:
        propositions, fragments, _ = load_draft_context()
        validate_population(propositions, fragments)

    def test_non_trivial_context_cases_have_multiple_or_body_span_fragments(self) -> None:
        propositions, fragments, _ = load_draft_context()
        non_trivial_ids = {
            "PROP-20260619-03", "PROP-20260619-04", "PROP-20260619-05",
            "PROP-20260620-07", "PROP-20260620-08", "PROP-20260620-09",
        }
        for prop in propositions:
            if prop.evidence_id in non_trivial_ids:
                alt = prop.context_alternatives[0]
                kinds = {fragments[fid].kind for fid in alt}
                self.assertIn("body_span", kinds, prop.evidence_id)
            else:
                alt = prop.context_alternatives[0]
                self.assertEqual(len(alt), 1, prop.evidence_id)
                self.assertEqual(fragments[alt[0]].kind, "observable_feed", prop.evidence_id)

    def test_all_65_marked_context_eligible_in_draft(self) -> None:
        _, _, eligibility = load_draft_context()
        self.assertEqual(len(eligibility), 65)
        self.assertTrue(all(row["context_eligible"] for row in eligibility.values()))


if __name__ == "__main__":
    unittest.main()
