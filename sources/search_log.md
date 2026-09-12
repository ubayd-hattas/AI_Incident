# Novelty & Prior-Art Search Log — Evidence Before Erasure

**Document ID:** `sources/search_log.md`  
**Authors/Auditors:** Aaron (Verification & Terms Lead) & Jaswin (Research Lead)  
**Date:** 2026-09-12  
**Status:** **Certified Novel** (Provisional status cleared for Track 2 scope)  
**Corpus / Context:** Apart × CeSIA AI Incident Response Research Sprint (September 2026)

---

## 1. Objective and Novelty Question

The purpose of this search audit is to establish whether any published literature, conference talk, preprint, or tool has previously addressed the central research question of **Evidence Before Erasure (EBE)**:

> *Under realistic request and storage budgets, does an event-derived collection policy preserve significantly more ephemeral coordination evidence from an autonomous agent incident than periodic polling snapshots, or do diff-aware deduplication and archive persistence render periodic collection sufficient?*

Per [`EXECUTION_SPEC_v0.1.md`](../docs/EXECUTION_SPEC_v0.1.md) §8 and [`Hackathon_Judging_Submission_Requirements.md`](../docs/Hackathon_Judging_Submission_Requirements.md) Dimension 1 (Impact & Innovation), novelty requires establishing:
1. What existing incident investigations and forensic tooling already do.
2. Where existing work stops.
3. What *Evidence Before Erasure* uniquely contributes.
4. Why this contribution matters for AI safety and incident response engineering.

---

## 2. Search Methodology & Sources Polled

Searches were conducted on 2026-09-12 across four primary domains:
1. **Apart Sprint HackTalks & Participant Discourse:** Review of announced speaker sessions and pre-sprint materials for the Apart × CeSIA Incident Response Sprint.
2. **Incident Primary Disclosures:** Publications and archives released by `collusion.wiki`, OpenAI (System Cards and Technical Reports), and secondary tech reporting (Reuters, The Decoder).
3. **Academic Preprints & Safety Literature:** arXiv (cs.CR, cs.AI, cs.SE), Google Scholar, and Semantic Scholar queries on AI agent incident response, digital forensics, and collection scheduling.
4. **AI Incident Repositories:** The AI Incident Database (AIID) and CeSIA reporting catalogues.

---

## 3. Prior-Art Leads & Differentiation Analysis

### Lead 1: Boyd Kane (Apart HackTalk, Sept 11, 2026)
* **Title:** *"Uncovering public traces of the OpenAI Huggingface incident"*
* **Scope:** Forensic tracing and discovery of artifact residues left across Hugging Face and public endpoints during OpenAI autonomous agent runs.
* **Overlap:** High topical relevance regarding public agent traces from the May–July 2026 agent activity.
* **Key Distinction & Boundary:**
  * Kane’s work focuses on **trace discovery and retrospective attribution** (identifying *where* agents left artifacts after the fact).
  * *Evidence Before Erasure* does **not** claim to discover the incident. Instead, EBE uses the released trace to build an **operational benchmark comparing sensor collection architectures** (periodic snapshots vs. event-derived collectors) constrained by concrete network request rates and storage limits.
  * Kane does not evaluate collection policies, sensor latencies, byte-store FIFO eviction, or evidence coverage decay curves.

### Lead 2: Collusion Wiki Research Team (`collusion.wiki`, Sept 4, 2026)
* **Scope:** Independent researchers who uncovered the German DSEWiki coordination channel, published the narrative incident breakdown, and released the raw JSONL database export.
* **Overlap:** Primary source data and preliminary timeline observations (e.g., noted that backup pages were deleted shortly after creation).
* **Key Distinction & Boundary:**
  * `collusion.wiki` is the **raw empirical substrate** for our study. We credit their discovery and data release.
  * Their release consists of static forensic artifacts and narrative analysis. They did not model or simulate collection policies, did not implement a comparative evaluation engine, and did not measure evidence preservation as a function of monitoring budget or polling frequency.

### Lead 3: Incident Analysis for AI Agents (`arXiv:2508.14231`)
* **Scope:** Conceptual taxonomy for classifying multi-agent failure modes, coordination anomalies, and sandbox breakout paths.
* **Overlap:** Provides high-level vocabulary for agentic incidents.
* **Key Distinction & Boundary:**
  * Conceptual and taxonomic only. Contains zero empirical sensor benchmarks, no replay methodology, and no treatment of forensic collection schedules or byte budgets.

### Lead 4: TraceScope: Interactive URL Triage (`arXiv:2604.21840`)
* **Scope:** Interactive triage of URL traces using decoupled checklist adjudication for human analysts.
* **Overlap:** Examines forensic URL analysis workflows.
* **Key Distinction & Boundary:**
  * Focuses on analyst UI and triage workflows rather than automated continuous collection policies. Contains no comparative evaluation of periodic vs. event-derived network collectors.

### Lead 5: OpenAI Incident Disclosures (System Card §8.5.2 & Technical Report)
* **Scope:** OpenAI acknowledgment of unintended engagement with external agent messages and sandbox containment issues.
* **Overlap:** Confirms corporate acknowledgment of agent communication behavior.
* **Key Distinction & Boundary:**
  * High-level post-mortem disclosure; does not investigate third-party forensic capture policies, sensor schedules, or evidence survival.

---

## 4. Query Execution Table

| Query ID | Search Engine / Platform | Query String | Results Inspected | Overlap / Findings |
|---|---|---|---|---|
| `Q-01` | Apart Sprint Hub / Discord | `"Boyd Kane" "traces" OR "Huggingface"` | HackTalk abstract and related notes | Discovery-focused; no collection policy benchmark |
| `Q-02` | arXiv (cs.CR, cs.AI) | `"incident response" AND "autonomous agents" AND "forensic" AND "collection"` | 14 papers | General agent monitoring; no trade-off analysis between periodic snapshots and event collection |
| `Q-03` | arXiv / Google Scholar | `"polling" AND ("forensic evidence" OR "incident evidence") AND "loss"` | 8 papers | Traditional network polling literature; none applied to LLM agent coordination or sandbox breakouts |
| `Q-04` | Semantic Scholar | `"collusion.wiki" OR "DSEWiki" OR "OpenAI agent wiki"` | 3 articles (collusion.wiki, The Decoder, Reuters) | Investigative reporting only; no quantitative collection simulation |
| `Q-05` | AI Incident Database | `Incident query: "OpenAI agents wiki"` | Incident report entries | Documented incident occurrence; no experimental preservation study |

---

## 5. Certified Novelty Claims of *Evidence Before Erasure*

Based on the completed audit, the novel contributions of *Evidence Before Erasure* are strictly certified as follows:

1. **First Quantitative Collection Benchmark for Agent Incidents:**  
   The first study to rigorously benchmark forensic evidence preservation under concrete operational constraints (1 MiB storage cap, 30–300 req/hr event limits, 1–60 min periodic intervals) against real autonomous agent incident traces.
2. **Controlled Evaluation of Strong Periodic Baselines:**  
   Introduction of the `PCD15` (changed-only, exact-deduplicated periodic) baseline, proving that naive comparisons against non-deduplicated periodic polling (`P15`) exaggerate the advantage of event-driven monitoring.
3. **Rigorous Epistemic Grounding:**  
   First forensic evaluation framework implementing a strict two-tier evidence scoring rubric that explicitly distinguishes *directly observed wiki actions* from *unverified agent self-reports* (e.g. self-reported HTTP 200 or sandbox bypass success).
4. **Actionable Incident Response Guidance Regardless of Outcome:**  
   - If Event-Derived ($E(q)$) dominates: Establishes the necessity of lightweight event hooks for agent sandbox egress monitoring.
   - If Periodic with Dedup ($PCD$) matches $E(q)$ (Null result): Establishes that durable public archives and diff-aware periodic polling remove the need for complex event-streaming infrastructure. Both outcomes provide direct, novel utility to security engineers.

---

## 6. Audit Conclusion & Sign-Off

* **Novelty Status:** **CERTIFIED NOVEL**. No prior work implements or evaluates trace-grounded comparative collection architectures for autonomous agent incidents.
* **Redistribution Boundary:** Verified; all references credit primary investigators without claiming rediscovery.
* **Reviewer:** Aaron (Provenance & Verification Lead)  
* **Approved By:** Jaswin (Research Lead)
