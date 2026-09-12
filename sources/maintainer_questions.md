# Collusion Wiki maintainer outreach

**READY — NOT SENT.** Jaswin sends manually using a verified maintainer contact. No recipient address has been assumed. Record recipient/channel, date sent, and any reply separately; silence is neither permission nor semantic confirmation.

## Message to send

**Subject: Collusion Wiki export: brief semantics/reuse questions + replay overlap**

Hello Collusion Wiki team,

Thank you for releasing the records. We are preparing *Evidence Before Erasure*: a DSE-only, trace-conditional comparison of collection schedules, semantic evidence preservation, and request/storage cost. We have no policy results and are not assuming polling loses evidence. We will credit your reconstruction separately from our experiment.

Could you clarify the following for the export generated `2026-09-03T03:42:36Z`? Brief answers or documentation links are very welcome; partial answers would help.

1. **Live fields:** What exactly do `deleted_live`, `live_body_variant` (`txt`/`dw`), and `head_differs_from_live` describe, and at what time? Is there a timestamped public-HTTP/live-body dump?
2. **Timing:** What does `uncertainty_seconds` mean—resolution, an error interval (which endpoints), or something else? Could you share CLOCK-AUDIT and the schema/export code, including any same-second ordering guarantees?
3. **Archival clock:** Is `archived_at` an RCS/storage operation, public availability time, live visibility boundary, or none of those? What guarantees, if any, connect it to public reads?
4. **Missing mutations:** Which successful writes/restores/administrative overwrites may be absent from published revisions/events (including short bodies)? Is a fuller redacted native change log available?
5. **Historical archives:** Could deleted pages/revisions remain recoverable? Through which archive/index endpoints, available from when, retained how long, and discoverable how? Were authentication or known-title/revision requirements involved?
6. **Recreation links:** What do exact versus fallback associations guarantee? How can we identify the six fallback links and their original successful-mutation times? We will not backdate later linked bodies.
7. **Reuse:** What permission/license applies separately to the raw export, short quoted excerpts, derived annotations, and a public reproduction artifact? May the artifact redistribute raw data/excerpts, or should it only download from your mirror?
8. **Overlap:** Have you or collaborators already replayed, or planned to replay, historical collection schedules comparing semantic evidence preservation against collection/storage cost? Any related work we should cite or distinguish?

We can proceed with explicitly labeled assumptions/simulation if details remain unknown, without implying your endorsement. Thank you for any guidance.

Best,
Jaswin
Evidence Before Erasure

## Internal handling (not part of the message)

- Basis: [audit questions](../docs/DATA_AUDIT_2026-09-12.md#questions-for-maintainers-blocking-where-noted). See [independent reconstruction](../audit/JASWIN_V02_RECONSTRUCTION.md) for concrete cases; send an example only if requested rather than attaching raw bodies initially.
- A reply is **not a project dependency**. Without clarification: no historical transitions from final flags/archive clocks; no body backdating; preserve unknowns/partial orders; declare hypothetical feed/latency and trace-grounded simulation where necessary; use a labeled persistent-archive optimistic scenario, not asserted historical recovery.
- Without defensible reuse permission, do not redistribute third-party raw text or excerpts. Prefer code plus source IDs/hashes and a mirror-download recipe only if the underlying use is defensible; otherwise pause release and seek review or use synthetic fixtures. Neither this draft nor a download-only recipe grants reuse rights.
- Novelty remains provisional until documented independent search and overlap review. An unanswered message proves nothing about prior work.
