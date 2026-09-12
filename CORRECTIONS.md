# Corrections log

This project is about measuring how easily forensic evidence gets lost or
distorted. In the interest of that goal, we're documenting our own process
errors rather than hiding them — including ones made by the AI tooling used
to help build this timeline.

## Errors caught during construction

1. **Fabricated manifest hash.** An early draft cited a SHA-256 checksum for
   `manifest.json` that did not match any value in the publisher's real
   `SHA256SUMS` block. It turned out to be a different hash (an internal
   source-database hash embedded *inside* the manifest payload) presented as
   if it were the file's own checksum. Fixed by re-deriving the real hash
   directly from the published checksums page.

2. **Unverifiable citation ID.** A specific numeric X/Twitter status ID was
   initially attached to a real, accurate quote, but the ID itself could not
   be independently confirmed. It was carried over from prior notes without
   being re-checked. Removed and replaced with a citation that was
   independently re-verified in this pass.

3. **Phantom audit file.** A file named `DATA_AUDIT_2026-09-12.md` was cited
   as if it were a completed, primary verification artifact. It was actually
   a pre-existing draft note in a teammate's local folder, not something
   produced or verified in the session that cited it. All citations to it
   were stripped; every claim was re-traced to a primary source instead.

4. **Invented deletion-window start time.** A row claimed deletions began at
   exactly `2026-06-04T00:00:00Z`, sourced to "manifest.json population
   counts." That field doesn't actually record a start time — the date was
   an artifact of a query filter string. Replaced with the actual earliest
   delete event found by querying the raw data directly:
   `delete:dse:rclog:131972` at `2026-06-04T10:53:40Z`.

## How each was caught

Independent re-verification against primary sources, rather than trusting
prior output: re-fetching the real checksums page, re-searching for the
actual quote wording across independent outlets, checking whether a cited
file was ever actually shown rather than just named, and re-deriving a date
from raw records instead of accepting a summary field at face value.

## Why this matters for the project

This is a small-scale, low-stakes demonstration of the exact failure mode
the research question is about: confident, specific-looking claims (exact
hashes, IDs, timestamps) that don't survive being checked against a primary
source. The fix in every case was the same — go to the rawest available
record and verify directly, rather than accepting a plausible intermediate
claim.
