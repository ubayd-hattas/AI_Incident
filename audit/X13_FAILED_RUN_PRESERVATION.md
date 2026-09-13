# Historical ordinal-1 failed-run preservation

The continuation handoff reports the following historical facts, which this
repair does not rewrite:

- roster: 791 collection rows and 61 stable re-score families;
- completed rows: 0; stable re-scores: 0/61;
- first row: `L-primary`, P15, phase 0;
- state: `RUNNING`, then `ExecutionTimeout` after exceeding 7,200 seconds;
- no row artifact, evidence coverage, or PCD-vs-E result;
- K remains 23 and methodology/annotations remain frozen.

The prior checked-in run manifest remains at SHA-256
`0db63b0bc62fdf2c84fb1b3e01eb3b04715679a40c66e936b9175afdebcef62b`.
This checkout contains neither a real-mode status log nor the independent Gate-2
authorization artifact described by the handoff. Their identities cannot be
preserved as local bytes or truthfully restated without the missing artifacts;
they were not fabricated. No file under the historical freeze/status/result
directories was edited by the performance repair.
