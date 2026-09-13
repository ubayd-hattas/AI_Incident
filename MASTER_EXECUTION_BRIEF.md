# Master execution brief, final hours

Written 2026-09-14, local time SAST (UTC+2). Deadline is 2026-09-13 23:59 AoE
(UTC-12), which is 2026-09-14 13:59 SAST. That is the real remaining window.
This file is the standing instruction set for the rest of the sprint. Every
role below is being played by one person (the user's own account, "Sam" by
convention) because the rest of the team is out of tokens. Every action still
gets attributed honestly to the role it belongs to, and conflicts of interest
get disclosed exactly as they were earlier in this project's audit trail, not
smoothed over.

## Writing rules, apply everywhere, not just the report

1. No em dashes, anywhere, in any file: not the LaTeX `---` ligature, not the
   Unicode character. Use a period and new sentence, a colon, a comma, or
   parentheses instead, whichever reads most naturally.
2. No bolding for emphasis in prose. Bold is reserved for things that are
   structurally bold (a macro like `\todo`/`\pending`, a table header). A
   bullet's lead phrase is plain text followed by a period, not `\textbf{}`.
3. No invented facts. Every number that appears anywhere (a count, a hash, a
   timing, a percentage) must trace to something actually run or actually
   read this session or a prior one, cited by file path. If a number is not
   yet verified, it stays a marked `\todo`/`\pending`, it does not get a
   plausible-sounding placeholder value.
4. Before adding any new claim to the report, check it against the actual
   repo state (grep, read the doc, run the script) rather than recalling it
   from memory of an earlier turn in this conversation.

## Roles and how they are being covered

- Sam (independent auditor). Standing role unchanged: verify, do not trust
  claims, disclose own errors and conflicts of interest.
- Ubayd (engineering). Covered when a scientific/engineering code fix is
  needed. Every such change gets its own independent re-audit afterward,
  same as if Ubayd had pushed it and Sam were reviewing it fresh.
- Jaswin (integration, amendments, handoffs). Covered when scope decisions or
  cross-cutting documents are needed.
- Alex/Aaron (annotation). Not currently in the critical path; the benchmark
  is frozen and accepted. No annotation content gets touched.

Whenever a change is made under the Ubayd or Jaswin hat, the next action
under the Sam hat re-audits it independently before it is relied on for
authorization, exactly like the existing precedent in
`audit/FINAL_PRE_X13_INDEPENDENT_READINESS.md` (the discarded interim episode
in section 9, the repeated independent re-audits in sections 10 to 12).

## Priority order for the remaining window (updated, mid-execution)

1. Report hygiene: done. Em dashes removed, unnecessary bold removed,
   corpus-size placeholder replaced with the verified count.
2. PCD-R and F, done, both closed out (not both fixed, both closed):
   - PCD-R: fixed twice (compact-mode wiring, then an O(known pages x
     retained packets) per-sweep scan), each independently re-verified for
     exact equivalence against the unmodified algorithm on real bounded
     prefixes. Still does not complete full-horizon within any reasonable
     observation window; treat as P/PD-scale expensive, not PCD-scale.
   - F: root-caused precisely (one page, `dse~WillkommenImWiki`,
     `terminal_directory()` missing the same try/except `_observe_state`
     already has). Deliberately not fixed: it changes F's frozen contract
     semantics and there is no second reviewer available to catch a mistake
     in that specific call under today's deadline.
3. Authorization: **not issued, and not recommended today.** Given PCD-R and
   F above, plus no numeric deadline/reserve budget ever being supplied,
   attempting the full 130-row candidate is not a responsible use of the
   remaining hours. This is the actual, final answer to item 3 in the
   original plan below, not a deferral.
4. Real X13 execution: not attempted, per 3 above. The honest incomplete
   result is the real, final result for this submission cycle.
5. Report Results section: done via merge. Another teammate independently
   rewrote `report.tex` into a complete, conservative, fact-checked report
   stating the incomplete-execution outcome directly (merged at `9c7c81f`,
   one addendum paragraph added carrying the PCD-R/F findings above into
   it). `docs/PROJECT_STATUS.md` and `README.md` have been updated to match
   this same final state; they no longer describe a pending Sam audit or an
   open Gate 2.

## What "done" looks like

- report.tex compiles conceptually (no unmatched environments), has no em
  dashes, no unnecessary bold, and every factual claim traces to a source.
  Confirmed. The compiled `report.pdf` in the repo is stale relative to
  the current report.tex (needs a fresh recompile with a LaTeX toolchain,
  none available in this environment) before actual submission.
- Either a real, authorized, independently reproducible X13 result exists and
  is reported honestly with its actual scope and caveats, or the report
  says plainly that it does not and why, without inventing one. The report
  does this.
- Every code change made under this brief has an independent re-audit
  entry, same standard as the rest of this project's audit trail. Confirmed
  in `audit/FINAL_PRE_X13_INDEPENDENT_READINESS.md` sections 12-13.
