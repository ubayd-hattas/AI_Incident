# Apart × CeSIA — Project Selection Brief

## 1. Bottom Line

* **Astra recommends:** Track 2 — What happened, and what breaks next.
* **Project:** Evidence Before Erasure: Measuring Forensic Evidence Loss in Autonomous-Agent Incidents.
* **Why:** Public incident histories let us test which collection policies preserve meaningful evidence—not just bytes—with a reproducible, CPU-only experiment feasible in 48 hours.
* **Overall score:** **82.3/100**.

Scores are comparative selection judgments, not winning probabilities. No experimental results exist yet.

## 2. Why This Track

| Track | Score /100 | Main opportunity | Main weakness |
| ----- | ---------: | ---------------- | ------------- |
| 1 — Containment | 69 | Executable tests of one control boundary | Toy tests cannot establish real containment |
| **2 — What happened, and what breaks next** | **82** | Measure evidence preservation using public histories | Reanalysis can masquerade as novelty |
| 3 — Regulatory response | 72 | Evidence-tested regulatory information request | Requires legal expertise and validation |
| 4 — Communication | 64 | Test whether briefs preserve uncertainty | Audience recruitment and demonstrated reach |
| 5 — Open | 72 | Separate refusal-caused failure from incapacity | Crowded benchmarks; causal confounding |

* Machine-readable incident evidence supports an experiment, not another incident summary.
* Deterministic replay avoids model-access, compute, and live-infrastructure dependencies.
* The output answers a concrete responder decision: what must we capture, and when?
* A robust null result remains useful; other tracks depend more on external reviewers or audiences.

## 3. Top 3–5 Project Options

### Evidence Before Erasure

* **Track:** 2.
* **One-line pitch:** Measure which warning signs disappear under different collection schedules.
* **Research question:** Which policies preserve distinct evidence at comparable cost?
* **Hypothesis:** Fifteen-minute snapshots lose ≥10 percentage points of critical-evidence coverage versus budget-matched event-derived retention.
* **What is genuinely new:** Incident-grounded evidence-coverage/cost evaluation, not deleted-page recovery.
* **What we would actually build:** Annotated histories and an offline replay benchmark.
* **How we would test it:** Held-out labels; matched budgets; multiple polling offsets.
* **Key metric/result:** Critical-evidence coverage versus storage and requests; effect unknown.
* **48-hour feasibility:** Strong if historical states are reconstructable.
* **Score /100:** 82.3.
* **Main risk:** Incomplete history or unfair collector-access assumptions invalidate comparisons.

### Witness Budget

* **Track:** 2.
* **One-line pitch:** Find the smallest evidence packet that distinguishes proposed, attempted, and actual effects.
* **Research question:** Which observation channels justify a boundary-violation finding?
* **Hypothesis:** Independent effect records help more than additional agent explanations.
* **What is genuinely new:** Claim-level measurement of evidence sufficiency beyond logging architectures.
* **What we would actually build:** Approximately 30 claim families with transparent real/synthetic evidence packets.
* **How we would test it:** Remove channels; compare blinded judgments, model investigators, and rules.
* **Key metric/result:** Justified versus unsupported confirmations per evidence cost.
* **48-hour feasibility:** Moderate; tightly cap fixture scope.
* **Score /100:** 76.4.
* **Main risk:** Synthetic fixtures make the answer arbitrary or obvious.

### Forensic Claim Calibration

* **Track:** 2.
* **One-line pitch:** Test whether investigators mistake claimed success for confirmed success.
* **Research question:** Can explicit claim-status rules reduce overclaiming without hiding supported findings?
* **Hypothesis:** ≥30% relative reduction in unsupported confirmations, losing ≤5 points of supported-claim recall.
* **What is genuinely new:** Narrow incident-grounded status evaluation—not citations or hallucination detection generally.
* **What we would actually build:** Approximately 60 adjudicated evidence packets and model traces.
* **How we would test it:** Compare ordinary, citation-required, and status-constrained prompts on paired evidence variants.
* **Key metric/result:** Unsupported confirmations versus supported-claim recall.
* **48-hour feasibility:** Good with bounded annotation and API access.
* **Score /100:** 74.7.
* **Main risk:** Generic citation prompting already solves it; novelty is medium-low.

### Escalation Invariance

* **Track:** 2.
* **One-line pitch:** Does calling an incident “just an evaluation” change escalation?
* **Research question:** Does irrelevant framing change decisions under a fixed response policy?
* **Hypothesis:** Some model reviewers change decisions despite identical operational evidence.
* **What is genuinely new:** Policy-fixed escalation testing, not generic alert triage.
* **What we would actually build:** A 40–60-case paired conformance suite.
* **How we would test it:** Vary framing; compare model decisions, structured extraction, and deterministic rules.
* **Key metric/result:** Paired decision flips, missed and unnecessary escalations.
* **48-hour feasibility:** Good; practitioner validation is the dependency.
* **Score /100:** 73.2.
* **Main risk:** Synthetic effects vanish after basic prompt cleanup.

## 4. Recommended Project

* **Project:** Evidence Before Erasure.
* **Problem:** A responder can retain substantial logs yet lose the support needed to justify specific findings.
* **Research gap:** Existing reconstruction and logging work does not, in inspected material, measure this corpus’s evidence-coverage/cost trade-off.
* **Research question:** Within recoverable Collusion Wiki history, how do collection policy, budget, and timing affect human-validated evidence preservation?
* **Hypothesis:** The ≥10-point snapshot deficit above is a proposed practical threshold, not established evidence.
* **Method:** Start with DSE histories; reconstruct state intervals; label distinct propositions and supporting context; replay final-state, periodic, deduplicated-periodic, and bounded event-derived policies. Deduplicate repeated claims and prohibit future knowledge.
* **Artifact:** Source-linked labels, deterministic harness, retention curve, inspectable example, and short preservation protocol; no API key required.
* **Evaluation:** Held-out, independently adjudicated episodes; coverage, context completeness, bytes, requests, delay; sensitivity to polling offsets, timestamp uncertainty, and missing history. Explicitly separate collector capabilities.
* **What would make this exceptional:** Strong byte retention conceals major evidence loss—or copying makes coarse polling surprisingly effective.
* **What would make us abandon/pivot:** By hour four, unresolved state semantics, equivalent existing work, or unusable redistribution terms; by hour twelve, unreliable labels or gains caused only by weak baselines. Narrow to declared simulation or switch to Witness Budget. A false hypothesis alone is not a pivot trigger.
* **Why this could score highly with judges:** A clear operational question, strong baseline, visible quantitative result, and independently reproducible artifact.

## 5. What We Would Actually Do

* Person 1: Own data semantics, provenance, missingness, and author contact; second-annotate evidence.
* Person 2: Own sampling, evidence rubric, annotations, and adjudication.
* Person 3: Build reconstruction, collectors, cost accounting, and tests.
* Person 4: Independently audit histories, analyze results, create figures, and reproduce the artifact.

First eight tasks:

1. Inspect the export manifest together; record version, hashes, and reuse conditions.
2. Ask dataset authors whether this exact retention experiment already exists; confirm track fit.
3. Independently reconstruct ten example histories, including deletion/recreation cases.
4. Define evidence units, critical categories, claim status, and required context.
5. Freeze a DSE sample and development/held-out split; target 40–60 adjudicated episodes minimum.
6. Specify collector access, budgets, 15-minute primary contrast, offsets, and uncertainty treatment.
7. Implement and hand-check minimal replay; pass the four-hour go/no-go gate.
8. Freeze held-out labels before comparisons; run policies and independently audit headline results.

## 6. Critical Prior Work

* **[Collusion Wiki export and manifest](https://collusion.wiki/explorer/download)** — Core histories and population definitions; recovery already exists.
* **[METR incident investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/)** — Documents missing/spoofed records and investigative limitations.
* **[Incident Analysis for AI Agents](https://arxiv.org/html/2508.14231v1)** — Existing framework for investigative evidence needs.
* **[Agent Flight Recorder](https://arxiv.org/html/2609.01931v1)** — Tamper-evident logging does not guarantee complete capture.
* **[HANSARD](https://arxiv.org/html/2608.22512v1)** — External witnessing and evidentiary assurance; adjacent architecture work.
* **[SecRespond](https://arxiv.org/html/2607.26791v1)** — Existing agentic forensic benchmark on post-compromise snapshots.
* **[TraceScope](https://arxiv.org/html/2604.21840v1)** — Already studies static-snapshot limitations in another domain.

## 7. Why This Isn't Just a Replication

* **Already done:** Recover deleted wiki content, document missing evidence, authenticate logs, and evaluate investigators on snapshots.
* **Our addition:** Replay acquisition policies and measure distinct, context-supported evidence retained per collection/storage budget.
* **Uncertain:** Novelty confidence is **medium**. This is an empirical extension, not a new security principle. Unpublished work by the dataset authors could erase the distinction.

## 8. Risks / Reasons NOT to Choose It

* One curated, incomplete incident family cannot establish general retention requirements.
* Reconstructed archive states may differ from what a historical collector could see.
* Event access is an infrastructure capability; comparing it with external polling can be misleading.
* “Critical evidence” and semantic deduplication require judgment; annotation is likely the bottleneck.
* Effects may be small, unsurprising, or sensitive to timestamps and retention rules.
* Preservation does not establish external success, successful interpretation, or adversary adaptation.
* This studies investigation readiness, not prevention. Never recommend delaying containment for evidence collection.

## 9. Decision

**Recommended choice:** Evidence Before Erasure

**Why:** It offers the strongest combination of accessible evidence, a falsifiable question, and a useful reproducible artifact within 48 hours. Its contribution is narrower than a new containment system, but more defensible. Proceed only if the early data-semantics and novelty gate passes.

**Next step:** Open the Collusion Wiki export manifest together and independently reconstruct one deletion/recreation history before committing.
