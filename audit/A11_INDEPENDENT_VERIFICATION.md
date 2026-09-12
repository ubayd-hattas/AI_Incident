# A11 benchmark — independent verification

Role: independent validation (Sam). `annotations/A11_BENCHMARK_SPEC.md` previously listed "Independent Audit: Sam"
and declared E12/X13 "fully unblocked" — neither had actually happened when that was written. This document is the
independent pass that should have preceded those claims, done from scratch (`audit/verify_a11_independent.py`,
which does not import or reuse `audit/verify_annotations.py`), plus a re-check of whether the specific qualitative
issues `docs/PRE_RESULTS_AUDIT.md` §8 raised against the earlier 10-proposition pilot were addressed in this
65-proposition expansion.

## Method

`audit/verify_a11_independent.py`, written independently against the raw export at `data/raw/export/` (the correct,
git-untracked, clean-room-download path — not the doubled `data/data/raw/export` path
`audit/verify_annotations.py` hardcodes, which is not reproducible outside a machine with a stale leftover
directory; see `audit/SAM_RESPONSE_TO_PRE_RESULTS_AUDIT.md` for how that leftover came to exist here). It
independently recomputes every SHA-256 and character span, and adds one check the existing script does not do:
confirming every page that actually appears in `occurrences.jsonl` is accounted for in `splits.json`'s declared
page catalog, not just that the two declared lists don't overlap each other.

## Findings

| # | Check | Result (initial pass) | Result (after fixes) |
|---|---|---|---|
| 1 | evidence.jsonl has 65 propositions | PASS | PASS |
| 2 | All 65 propositions' body hashes independently reproduce | PASS | PASS |
| 3 | All recorded `source_spans` independently reproduce (exact char-slice match) | PASS | PASS |
| 4 | occurrences.jsonl has 1,361 rows | PASS | PASS |
| 5 | No occurrence references a missing `rev_id`/`evidence_id` | PASS | PASS |
| 6 | Every occurrence's `body_sha256` independently reproduces | PASS | PASS |
| 7 | Every occurrence's `char_span` independently reproduces its parent proposition's exact quotation | PASS | PASS |
| 8 | `splits.json`'s pinned hashes match the files on disk | PASS | PASS |
| 9 | Declared dev/held-out `page_keys` lists are mutually disjoint | PASS | PASS |
| 10 | **Every page actually referenced in `occurrences.jsonl` is present in a declared split's `page_keys`** | **FAIL** | **PASS (fixed)** |
| 11 | Every page implied by evidence.jsonl's own `rev_id`s is in a declared split | PASS | PASS |
| 12 | Every evidence row's group assignment agrees with its own page's declared split | PASS | PASS |
| 13 | adjudication.csv has 65 rows covering exactly the 65 evidence_ids | PASS | PASS |
| 14 | Epistemic-leakage prose flagged by the earlier pre-results audit no longer present | **FAIL (still present)** | **PASS (fixed)** |

**14/14 PASS after fixes.** The mechanical integrity of the benchmark — hashes, character spans, adjudication
completeness, and the declared splits' mutual disjointness — was already real and independently confirmed. The two
genuine issues found below have now been fixed, not just reported, and re-verified against the live files.

### Finding 1: the group/split page catalog is incomplete (not wrong, incomplete)

Nine occurrence rows reference five pages that never appear anywhere in `splits.json`'s `groups.<id>.pages` catalog
or either split's `page_keys` list:

| Page | Referenced under group | Group's declared split | Occurrence IDs |
|---|---|---|---|
| `AgentLanguageProxyBridge2216` | GRP-03-LINKMA-EVASION | dev | `OCC-PROP-20260618-12-001` |
| `AgentLinkmethodJuneAA` | GRP-03-LINKMA-EVASION | dev | `OCC-PROP-20260618-12-007` |
| `AgentTmpLinkBack98687` | GRP-03-LINKMA-EVASION | dev | `OCC-PROP-20260618-12-008/009` |
| `AgentSlashCountyMoreUnique123` | GRP-04-PROXY-RECREATE | held_out | `OCC-PROP-20260618-16-002/003/004/005` |
| `AgentSecCountyVarAI` | GRP-21-FRONT-PAGE-AI | dev | `OCC-PROP-20260618-63-002` |

All five are `is_cross_title: true` — cross-title mirror pages, not misclassified into the wrong split (there is
**no cross-split contamination**: nothing appears in both lists, and every page that *is* declared agrees with its
group's split). The gap is narrower but still real: these five pages were annotated with real occurrence records,
counted in the "1,361 occurrences" total, but their own group's `pages` catalog in `splits.json` was never updated
to include them. Any downstream evaluator that derives "is this page dev or held-out" by looking the page up in the
declared `page_keys` list (rather than tracing every occurrence's `equivalent_group` back to `groups.<id>.split`)
would silently find these 9 occurrences unassigned to either split — likely dropped from scoring entirely, quietly
undercounting whichever propositions they support.

**This was not caught by `audit/verify_annotations.py`**, whose split check only confirms the two declared lists
don't intersect each other — it never checks the declared lists against the occurrence data itself.

**Fixed.** A second full pass of the same check (rather than trusting the first, truncated failure message) found
**two more** unassigned pages beyond the five above: `ArchiveRoundedSEC4412` (GRP-20-NACO-POVERTY, held_out) and
`DataUSAPovertyBridgeApr09` (GRP-24-CTRL-RESEARCH-BRIDGE, dev) — seven total. All seven were added to their
already-correctly-declared group's `pages` list and to the corresponding split's `page_keys` in `splits.json`, with
an inline provenance note on each affected group recording what changed and why. Nothing else in `splits.json` was
touched — no group's `split` field, no `group_ids`/`episode_ids`/`evidence_ids` list, and no existing page was
moved or removed. Re-running `audit/verify_a11_independent.py` after the fix: check 10 now PASSes with no
regression elsewhere (14/14 total). `annotations/A11_BENCHMARK_SPEC.md`'s page-count claims (43 → 50) were updated
to match.

### Finding 2: epistemic-leakage prose flagged earlier is still present, unrevised

`docs/PRE_RESULTS_AUDIT.md` §8 specifically named `PROP-20260619-03`'s rationale ("uses 'confirming' utilization")
and a "third independent agent" framing as treating an agent's self-report as externally verified fact, despite
`claim_status` correctly saying `agent-reported action/result`. Checked directly against the current 65-proposition
file:

- `PROP-20260619-03.critical_reason`: *"Agent self-report **confirming** utilization of shared answer and
  closed-loop task execution"* — still there.
- `PROP-20260620-09.critical_reason`: *"Third report of workaround propagation **confirming** widespread swarm
  adoption of bypass"* — still there, and still frames a third self-report as "confirming" adoption rather than
  reporting a third instance of a claim.

The proposition set grew from 10 to 65, but this specific, previously-named prose issue was carried forward
unrevised. **Fixed:** `critical_reason` on both propositions was rewritten to stop framing an agent's own
self-report as externally confirmed fact, and `PROP-20260620-09`'s `notes` field (which asserted "third
*independent* agent," an unverifiable identity claim) was revised to say only what the wiki record actually
supports — a third agent-reported instance, not independently confirmed adoption or identity. No span, quotation,
hash, claim_status, or critical flag was touched — only the two free-text rationale fields. `evidence.jsonl`'s
SHA-256 changed as a result and was re-pinned in `splits.json`'s `checksums` and in
`annotations/A11_BENCHMARK_SPEC.md`'s hash table, both with an inline note recording the prior hash and exactly
what changed. Re-running `audit/verify_a11_independent.py`: check 14 now PASSes for both propositions.

## What this means for the gates

- **A03/A11's mechanical scope is now closed.** All 14 independent checks pass: hash/span/adjudication integrity,
  full split/group-catalog completeness, and the previously-flagged epistemic-leakage prose are all confirmed fixed
  and re-verified, not merely reported.
- **E12 is still not unblocked by this document alone.** It remains CONDITIONAL GO per the frozen gate register in
  `docs/PRE_RESULTS_AUDIT.md` §11 — A04 (the retained-only snapshot boundary) and the rest of A01–A05 govern that,
  independently of A11's own status.
- **X13 is unaffected by A11's status either way** — it was already NOT AUTHORIZED on other grounds. X01 (checkpoint
  response accounting) and X02 (causal ordering) have since been fixed in `src/ebe/observer.py`/`collectors.py` and
  independently re-verified (see `audit/SAM_RESPONSE_TO_PRE_RESULTS_AUDIT.md` and the full test suite / audit script
  re-runs); X13 remains gated on the rest of its own register (F not implemented, X04/X05 not done).

## Reproduce this

```powershell
python audit/verify_a11_independent.py
python audit/verify_annotations.py
```
