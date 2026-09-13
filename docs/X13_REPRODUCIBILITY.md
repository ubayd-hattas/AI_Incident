# X13 reproducibility — FINAL_PRE_X13_DEADLINE_v1

Gate 1 supports deterministic, offline synthetic reproduction only. The entry
point never downloads data, opens embedded URLs, calls a model/API, or requires
redistribution of the private raw export. From a clean Python environment with
the repository's local dependencies installed, run:

```text
python scripts/reproduce_x13.py --mode synthetic
```

This regenerates and verifies the immutable pre-score manifest, creates
header-only result schemas, and runs invented label-free rows with atomic output
and checksums. Interrupting with `--max-rows N` and rerunning resumes from
completed checksummed rows; append-only attempt history is retained.

`--mode real` fails closed unless a future independent Gate 2 authorization
artifact pins the exact amendment and `run_manifest.json` SHA, declares
`GATE_2_PASS`, sets `real_scoring_authorized` to true, and names the independent
reviewer. Gate 1 intentionally provides no default real executor. Source,
benchmark, stable-mask, code and environment identities are recorded in the
manifest. Dynamic timing/status files are outside `freeze/`.
