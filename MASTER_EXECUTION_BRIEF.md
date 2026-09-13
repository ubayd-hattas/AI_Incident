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

## Priority order for the remaining window

1. Report hygiene (this pass): done. Em dashes removed, unnecessary bold
   removed, corpus-size placeholder replaced with the verified count.
2. Close the two live blockers from `audit/FINAL_PRE_X13_INDEPENDENT_READINESS.md`
   section 12 that are actually engineering work:
   - PCD-R never received the compact/performance treatment
     (`PeriodicCollector.run` routes it straight to `_run_repair`, which
     always retains full history). Fix, then independently re-verify
     equivalence the same way the existing P/PD/PCD/E fix was verified.
   - F's `AmbiguityLimitError`. Find the actual page/mutation cluster
     responsible before deciding whether it is a genuine same-time ambiguity
     (accept as a disclosed required-row failure) or a limit that is simply
     set too low for one legitimate large cluster (raise the limit, with a
     stated reason, not a silent tweak).
3. Once both are resolved or explicitly accepted as disclosed failures,
   regenerate a fresh manifest at the final HEAD and issue the Gate 2 PASS
   and authorization artifact in the same pass, per the amendment's own
   closing instruction.
4. Execute the authorized real run within whatever time remains. If the full
   130-row candidate cannot complete before the deadline, an honest partial
   result (clearly labeled which rows completed) is what gets reported, not
   a forced completion or a fabricated number.
5. Fill in the report's Results section with whatever is actually true at
   submission time, pending or real, following the writing rules above.

## What "done" looks like

- report.tex compiles conceptually (no unmatched environments), has no em
  dashes, no unnecessary bold, and every factual claim traces to a source.
- Either a real, authorized, independently reproducible X13 result exists and
  is reported honestly with its actual scope and caveats, or the report
  says plainly that it does not and why, without inventing one.
- Every code change made under this brief has an independent re-audit
  entry, same standard as the rest of this project's audit trail.
