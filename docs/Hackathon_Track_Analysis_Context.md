# HACKATHON TRACK & PROJECT SELECTION CONTEXT
## Apart × CeSIA AI Incident Response Research Sprint

### PURPOSE
This file is a dedicated briefing for an AI research agent (e.g. Astra) whose job is to analyze the hackathon's possible project directions and recommend the strongest project(s) to pursue.

The human team is currently leaning toward **Track 2 (What happened, and what breaks next)**, while also considering **Track 5 (Open)**. The team wants an evidence-driven comparison across all five tracks, with especially deep attention to Tracks 2 and 5, and ultimately wants **3–5 concrete project candidates** ranked by expected competitiveness and feasibility.

Do NOT assume Track 2 is the final choice. Treat it as a hypothesis to test.

---

# 1. ORGANIZER'S OVERALL PROJECT DESIGN CONSTRAINT

The organizers explicitly say the example projects are **starting points, not a menu**. Teams may:
- choose an example project,
- modify one,
- combine useful ideas where appropriate,
- or propose a new project inside a track's goal.

A central design constraint is that each track should produce an **artifact a judge can grade in ideally less than 15 minutes**.

The sprint is close to policy and security practice, so the organizers want concrete deliverables rather than essays.

General winning principle:

> **An artifact somebody can use beats an argument somebody can agree with.**

Every project should therefore be evaluated for:
- concrete artifact
- practical user/recipient
- evidence quality
- testability within a weekend
- reproducibility/auditability
- clear limitations
- clear next-step research
- fit to judging criteria

---

# 2. CURRENT TEAM HYPOTHESIS

Current thinking:
- Primary interest: **Track 2**
- Secondary interest: **Track 5**
- However, the team wants Astra to analyze **all five tracks** before deciding.

Astra should therefore:
1. Analyze Track 1.
2. Analyze Track 2.
3. Analyze Track 3.
4. Analyze Track 4.
5. Analyze Track 5.
6. Generate project candidates, not merely repeat organizer examples.
7. Identify which projects are genuinely differentiated.
8. Identify which projects can be completed convincingly in ~3 days.
9. Rank approximately 3–5 final candidates.
10. Explain why the winner is superior to the alternatives.

---

# 3. TRACK 1 — CONTAINMENT

## Core question
**What standard would have stopped this?**

## Organizer example projects

### 1. v0.1 containment standard
Build a standard containing:
- clauses
- evidence required for each clause
- rough cost per clause

Goal:
- define the minimum adequate standard for dangerous-capability evaluations with production safeguards disabled
- make it specific enough to audit
- make it cheap enough for a second-tier lab to adopt

### 2. Control-by-attack-phase matrix
Map controls such as:
- canary credentials
- egress tripwires
- credential scoping
- kill criteria

against each documented intrusion phase.

Include cost/difficulty.

### 3. Engineering that makes “yes” cheap
Package mitigations so that a lab has little cost excuse for adopting them.

### 4. Control × chain-step × cost matrix
Use the documented attack chain and score:
- which control interrupts which phase
- implementation cost
- operating cost

Potential chain phases named by organizers:
- reconnaissance
- RCE
- dropper
- exfiltration
- C2
- evasion
- Kubernetes
- supply chain
- network pivot

The organizer says this can be made “fifteen-minute-gradeable” and usable by a regulator or insurer.

### 5. Egress attestation specification v0.1
Define what a lab could publish, such as:
- signed network policy
- flow-log digest

that an outside party could verify without access to the lab's network.

### 6. Detection that fires but does not page
Build/specify detection for:
- agent-speed activity
- parallel/bursty activity
- thousands of individually unremarkable actions
- attacks visible primarily through action sequences

Problem identified:
- detection correlated but did not escalate/page a human quickly enough.

### 7. Forensics against an adversary that fabricates evidence
Build:
- tooling
- or a triage protocol

for forensic environments containing agent-generated artifacts that resemble:
- rootkits
- benchmark code
- other malicious-looking artifacts

### 8. Deception as a first-class control
Design/test:
- fake credentials
- fake package registries
- honey clusters

Measure whether they:
- slow an agentic attacker
- or merely generate noise.

## Deep research framing
Questions include:
- What is the minimum adequate containment standard?
- Which controls interrupt the attack chain?
- What evidence proves compliance externally?
- Who owns the second-hop risk when staging infrastructure is third-party?
- Can a standard be independently verified?

## Limitations
A weekend standard is only v0.1.
A clause list or harness does not prove that a real lab is adequately contained.
Real assurance requires access that the sprint does not have.

---

# 4. TRACK 2 — WHAT HAPPENED, AND WHAT BREAKS NEXT

## Core question
**Reconstruct what this incident does and does not establish, then turn it into concrete things to check and things to watch.**

This is the team's current leading track hypothesis.

## Organizer example projects

### 1. Forensic read of the public record
Determine:
- established facts
- asserted but unverifiable claims
- what pending third-party assessments could settle

### 2. Causal analysis of why monitoring was absent
Investigate why known defenses did not operate in practice.

Possible mechanisms:
- cost
- incentives
- ownership gaps
- alert fatigue
- other organizational mechanisms

Goal:
produce a causal explanation that predicts where the next gap will be.

### 3. Warning shots we may already have missed
Investigate whether similar incidents may have occurred but remained private.

Map:
- what has not been checked
- who could check it
- what systematic investigation would require

### 4. What other accident types should we expect?
Build a structured taxonomy/forecasting framework for future agentic incidents.

### 5. Warning-shot science
Explore questions that make the incident useful as a warning shot.

### 6. One-day verification checklist
Create a lab/defender checklist.

Requirements:
- each item has a pass condition
- ordered by cost to run
- actionable within one day

### 7. Prediction-bounty protocol
Create a mechanism where:
- an outsider makes a specific prediction such as “check X”
- the company runs an internal check
- a serious bounty rewards predictions that surface real problems

Goal:
make the mechanism practical enough for a lab to sign.

### 8. What drives agent cooperation?
Analyze what conditions produced cooperative behavior.

Possible factors:
- same model type
- noncompetitive tasks
- shared goals
- inability of “sacrificing” agents to act otherwise

### 9. When would agents manipulate each other?
Study competitive settings where agents:
- see progress of others
- communicate
- have incentives to interfere

### 10. How pivotal was a single agent?
Investigate whether one agent (named by organizers as PhaseOne[Big]) drove much of the collective behavior.

Potential counterfactual:
- introduce an aligned/charismatic agent that debates it
- test whether the collective changes behavior

### 11. Human as blocker
Ask whether agents would manipulate a human if a human were the obstacle to achieving their goal.

### 12. Reduced CoT monitorability
Investigate what happens if chain-of-thought monitorability is reduced.

Goal:
develop protocols/guidelines that still permit post-hoc investigation assuming CoT is opaque.

### 13. The first denominator
Assemble public figures from:
- Anthropic
- UK AISI
- METR

into a defensible estimate of how often evaluation runs produce boundary violations.

Must explicitly address:
- what each source counts
- denominators
- what each misses
- uncertainty

Organizer explicitly prefers a single well-caveated number over many weak forecasting questions.

### 14. Persistence protocol
Specify evidence required to establish that no copy of the pre-release model persisted.

Document:
- what has been asserted
- by whom
- what remains externally unverifiable
- what form verifiable attestation would take

## Track 2 research questions
- What base rates exist for agentic incident risk?
- What do they imply?
- What should defenders/labs verify now?
- Which checks are cheap enough for a single day?
- What would make this a true warning shot?
- What would establish whether a model copy persisted?
- What evidence would settle key disputed claims?

## Why organizers say Track 2 matters
A warning shot only works if it gets converted into:
- specific things to check
- specific things to watch
- explicit resolution criteria

Otherwise attention decays.

## Important public denominator information supplied by organizers

### Anthropic
- Reviewed **141,006 evaluation runs**
- Found **3 incidents across 6 runs**
- Earliest dated to April 2026

### UK AI Security Institute
- Tested **5 frontier models**
- **475 runs per model**
- Every model attempted to cheat
- Reported rates:
  - 14.1%
  - 12.6%
  - 11.4%
  - 9.1%
  - 7.8%
- Included an AISI near-miss involving a model writing/running code on an external service to reach AISI evaluation infrastructure.

### METR
- Cross-industry Frontier Risk Report is described as documenting dozens of comparable incidents across major AI companies.

**Critical:** These are organizer-provided figures and framing. Verify primary sources before using them as final research claims.

## Investigation/verification methodology sources named by organizers

### METR
Provides a proposed credible third-party investigation methodology involving:
- running models involved
- full transcripts/reproducible environments
- employee interviews
- classifiers over training data
- adequate inference budget
- redaction summary

### GovAI
Incident Analysis for AI Agents:
- system-related factors
- contextual factors
- cognitive factors

Also identifies information investigators may need:
- activity logs
- system documentation/access
- tool information

### CLTR Loss of Control Observatory
Argues that:
- controlled-setting demonstrations are insufficient for policy
- real-world evidence is missing
- incident detection capability is lacking

## Interpretation sources named by organizers
- Redwood Research: argues for grader-gaming rather than simple instruction-following.
- MIT Technology Review: challenges “unprecedented” framing and emphasizes containment design.
- Vectra: emphasizes response as central story.
- Reuters/CNA: provides an independently sourced detection-timeline account, but organizers explicitly warn that some claims are uncorroborated and should be treated as hypotheses.

## Track 2 limitation
Forecasting questions require strong resolution criteria.
Checklists are hypotheses about what matters; they do not themselves prove those controls matter.

---

# 5. TRACK 3 — REGULATORY RESPONSE

## Core question
**What should regulators actually ask/do about this incident?**

## Organizer example projects

1. Draft an incident-specific **Request for Information (RFI)**.
   - numbered questions
   - answer that would settle each issue
   - answer that would not settle it
   - public vs regulator-only version

2. Test existing reporting systems.
   - EU serious AI incident template
   - California Cal OES critical safety incident portal
   - fill both using public information
   - identify what each captures/misses
   - identify where a filer must guess

3. “Who decides when the pause ends?”
   - create defensible resumption criteria
   - specify evidence
   - specify sign-off
   - make criteria non-circular

4. Fix a possible US AI Kill Switch Act loophole around “controlled environments.”

5. Fill actual instruments for OpenAI and Anthropic incidents and diff them.

6. “Three clocks, one incident”
   Compare:
   - EU “without undue delay”
   - California 15-day-from-discovery
   - New York 72-hour reasonable-belief clock
   - then compare with NIS2, GDPR, DORA and CIRCIA

7. Test labs' published frontier frameworks against actual incident behavior.

8. RFI with evidence-sufficiency column.

9. Definitional stress test across regimes.

10. Jurisdictional reach map.

11. Learn from mature reporting systems:
   - aviation
   - biosafety
   - software security/CVE/coordinated disclosure

## Judging
- legal accuracy
- specificity
- usability by regulator/legislator with light edits

## Key limitation
A researcher-drafted document is not a regulatory act.
Some critical facts are only held by developers.
The value is demonstrating that:
- answerable questions exist
- evidence needed to settle them is identifiable
- regimes can produce materially different answers.

---

# 6. TRACK 4 — COMMUNICATION

## Core question
**How can the warning shot actually reach decision-makers and the public?**

## Organizer examples

1. Audit reactions by channel:
   - LinkedIn
   - mainstream press
   - YouTube
   - other channels

2. Crisis communication playbook:
   - holding statements
   - journalist FAQ
   - plain-language explanation
   - first-48-hours decision tree

3. Get the incident covered accurately:
   - memo
   - social content
   - creator outreach

4. Map policymaker positions.

5. Identify the central discourse problem.

6. Create/complete CeSIA communication kit.

7. Comparative disclosure analysis:
   - compare two similar incidents
   - score timeliness
   - completeness
   - verifiability
   - actionability
   - create reusable rubric

8. Build an accessible educational artifact:
   - 90-minute tabletop
   - short film
   - museum-style explainer
   - one-page ministerial brief
   - interactive walkthrough

## Judging
- grounding in dates, quotes, named outlets
- evidence of actual reach/use
- playtests/reader feedback

## Limitation
A communication kit without evidence of use is weaker.
Organizers explicitly value actual playtesting or external reader/creator/journalist response.

---

# 7. TRACK 5 — OPEN

## Core question
**What important project has not been captured by Tracks 1–4?**

Same core terms:
- defined artifact
- gradeable in ~15 minutes
- grounded in public record
- explicit statement of what it cannot establish

## Organizer example projects

### 1. Defender's dilemma: refusal on incident response
Study how model refusal affects defensive incident-response workflows.

Potential questions:
- How often do refusals block legitimate response?
- How does over-refusal behave on real incident artifacts?
- How much is refusal vs incapacity?
- What does fallback to open-weight models cost?

### 2. Intervention prioritization
Rank possible interventions:
- which matter most
- in what order
- what each buys

### 3. Benchmark contamination
Assess whether benchmark answer-key exfiltration compromises future benchmark results.

Possible maintainer actions:
- rotate
- re-host
- retire
- accept

### 4. Liability / insurance
Map:
- remediation costs
- insurance coverage
- claims
- contractual allocation
- third-party evaluation arrangements

### 5. Teach the vulnerability class
Build a safe, local, reproducible educational environment for the relevant constructor-abuse/template-injection vulnerability class.

### 6. Negative results / replications
Submit:
- failed approaches
- replications that disagree with published findings
- clean negative results with clear methods

---

# 8. TRACK 5 SPECIAL DIRECTION — DEFENSIVE OVER-REFUSAL

The organizers identify an explicit research gap:

Existing work measures refusal largely at the **single-prompt** level.

The incident-response problem is different:
- multi-step autonomous workflow
- agent-generated artifacts
- time pressure
- incomplete information
- one refusal can silently break the workflow instead of triggering a human retry

### Existing research cited by organizers

Defensive Refusal Bias:
- 2,390 real NCCDC prompts
- 12.2% overall refusal
- security-sensitive keywords refused at 2.72× equivalent neutral phrasing
- explicit authorization increased refusal:
  - 21.8% vs 11.6%
- concentrated refusal in operational tasks:
  - system hardening 43.8%
  - malware analysis 34.3%
  - vulnerability assessment 22.7%
  - incident response 18.9%

Other named work:
- Gray Swan Cybersecurity Refusal Framework
- Meta CyberSecEval / MITRE False Refusal Rate
- CyberSOCEval with CrowdStrike
- content-based cyber refusal framework
- OR-Bench

### Claimed gap
No existing work cited by the organizers covers:
> multi-step autonomous forensic workflows operating on agent-generated artifacts, where one refusal causes silent workflow failure.

Potential project candidates:
- replicate authorization paradox
- measure compound refusal over 20-step incident-response workflows
- compare frontier vs open-weight model accuracy on forensic tasks

### Important limitation
A benchmark built from public breach material cannot reproduce:
- live time pressure
- incomplete information
- legal exposure

Low refusal is not equivalent to usefulness.

---

# 9. TRACK 5 SPECIAL DIRECTION — POLICY TABLETOP

Build a **90-minute agentic-incident tabletop exercise** for non-security policymakers.

Potential decisions:
- disclose before attribution?
- contain vs preserve evidence?
- when does regulatory notification clock start?
- which actors are involved?

Possible roles:
- lab
- platform
- regulator
- national CSIRT
- press

Reference:
- RAND Europe / UK AISI / Mila cabinet-level AI crisis exercises

Gap:
Existing exercises focus on criminal misuse rather than a lab's own AI system breaking containment and attacking a third party.

Required evidence:
- playtest
- facilitator feedback
- design lessons

Limitation:
One friendly playtest only establishes a prototype.

---

# 10. CORE READING LIST FOR PROJECT SELECTION

## Highest-priority sources

### Incident reconstruction
1. Hugging Face — Anatomy of a Frontier Lab Agent Intrusion
   https://huggingface.co/blog/agent-intrusion-technical-timeline
   Organizer calls this the **single most important document** for the sprint.
   ~17,600 recovered actions in ~6,280 clusters.

2. Hugging Face initial disclosure
   https://huggingface.co/blog/security-incident-july-2026

3. OpenAI incident account
   https://openai.com/index/hugging-face-model-evaluation-security-incident/

4. Anthropic incident investigation
   https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals

5. METR investigation
   https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/

6. METR investigation methodology
   https://metr.substack.com/p/2026-07-28-investigating-ai-propensities-after-incidents

7. Collusion Wiki
   https://collusion.wiki/

## Track 1
- CoSAI AI Incident Response Framework
- CSA AI Controls Matrix / AIS-13
- NIST SP 800-61r3
- Elastic attack-chain detection analysis
- SecureLayer7 technical anatomy
- CSA CISO post-mortem
- ExploitGym

## Track 2
- UK AISI cheating behaviour report
- Anthropic incident review
- METR Frontier Risk Report
- GovAI Incident Analysis for AI Agents
- CLTR Loss of Control Observatory
- Redwood Research analysis
- MIT Technology Review analysis
- Reuters/CNA detection timeline

## Track 3
- EU serious incident reporting template
- California Cal OES reporting portal
- OECD common AI incident reporting framework
- OECD AI Incidents Monitor
- EU AI Act enforcement information
- California SB 53
- New York RAISE Act analyses
- H.R.9477 AI Incident Reporting Act
- AI Kill Switch Act coverage
- Frontier Model Forum reporting brief
- CSET mandatory reporting regime paper
- AAAI incident reporting systems paper

## Track 4/5
- Defensive Refusal Bias
- Gray Swan Cybersecurity Refusal Framework
- Meta CyberSecEval
- OR-Bench
- RAND/AISI/Mila cabinet-level crisis exercises
- OECD AI Incidents Monitor
- AI Incident Database
- MIT AI Risk Initiative trackers

---

# 11. PROJECT-SELECTION RUBRIC FOR ASTRA

Astra should score every serious candidate on a **0–10 scale** for:

1. **Novelty**
   - Is there a real gap?
   - Are others already doing essentially the same thing?

2. **Evidence availability**
   - Can enough high-quality public data be obtained within the sprint?

3. **Scientific rigor**
   - Can the project support a defensible method and result?

4. **Testability**
   - Can the central claim actually be tested in ~3 days?

5. **Artifact quality**
   - Is there a concrete artifact beyond prose?

6. **15-minute judgeability**
   - Can a judge understand and grade the contribution quickly?

7. **Practical usefulness**
   - Would a lab, regulator, defender, maintainer, or policymaker use it?

8. **Differentiation**
   - Does it clearly add something beyond existing organizer examples and prior work?

9. **Feasibility**
   - Can a small student team realistically complete it?

10. **Potential impact**
   - Could the result influence practice, policy, research, or future incidents?

11. **Continuation potential**
   - Does it naturally grow into a 3–6 month research project / paper?

12. **Risk of ending with only an essay**
   - Penalize projects where the likely output is mostly narrative.

13. **Reproducibility**
   - Can another person run/audit the method?

14. **Limitations clarity**
   - Can the team state exactly what the project does not establish?

15. **Dual-use/safety**
   - Can the artifact be produced safely without creating unnecessary offensive capability?

Suggested weighted score:

**Overall =**
- 15% Novelty
- 10% Evidence availability
- 10% Scientific rigor
- 10% Testability
- 10% Artifact quality
- 10% Judgeability
- 10% Practical usefulness
- 10% Differentiation
- 5% Feasibility
- 5% Continuation potential
- 5% Impact

Astra may adjust weights, but must explain why.

---

# 12. REQUIRED ASTRA OUTPUT

When asked to analyze project options, Astra should NOT immediately start building.

First produce:

## Phase A — Track landscape
For each Track 1–5:
- strongest opportunity
- weakest point
- likely competition
- evidence advantage
- feasibility
- potential artifact
- biggest failure mode
- estimated score

## Phase B — Generate candidates
Generate **at least 8–12 candidate projects**, including:
- several Track 2 ideas
- several Track 5 ideas
- at least one serious candidate from each other track

Do not simply copy organizer examples. Improve, combine, or derive novel versions.

## Phase C — Kill weak ideas
Explicitly eliminate candidates that:
- are too broad
- are mostly essays
- cannot be tested
- duplicate existing work
- depend on unavailable proprietary evidence
- cannot produce a gradeable artifact
- are too technically ambitious for 3 days

## Phase D — Rank finalists
Return the best **3–5 projects**.

For each finalist include:
- title
- track
- research question
- hypothesis
- artifact
- exact method
- datasets/sources
- evaluation
- expected result
- novelty claim
- strongest competing prior work
- what can be completed by deadline
- limitations
- dual-use concerns
- extension path
- score /100

## Phase E — Final recommendation
Pick ONE project as the recommended default.

Explain:
- why it beats the other finalists
- what could make it win
- what could make it fail
- why it is realistic for a 3-day sprint
- what the first 2–4 hours of work should be

Do not choose Track 2 merely because the team currently prefers it.

---

# 13. RESEARCH DISCIPLINE

Astra must maintain these distinctions:

### Established
Directly supported by primary evidence.

### Reported
Claimed by a source but not independently verified.

### Inferred
Reasonable interpretation derived from evidence.

### Hypothesis
Something the project proposes to test.

### Unknown
Evidence currently insufficient.

Never silently convert one category into another.

For important factual claims:
- prioritize primary sources
- record exact source
- preserve dates
- preserve denominators
- distinguish model behavior from human behavior
- distinguish autonomous action from human-directed cyber activity

---

# 14. IMPORTANT SOURCE-SPECIFIC CAUTIONS

The supplied organizer material itself contains several places where numbers/details need verification before appearing in the final report.

Examples:
- ExploitGym: organizer says released benchmark is **v1.0 with 869 instances**, while the paper describes 898. Do not quote 898 as the shipped number.
- Reuters/CNA claims contain anonymous/uncorroborated details. Treat them as hypotheses.
- Regulatory claims should be checked against current statutory/regulatory text.
- The organizer's description of EU enforcement powers should be separated from the legal provisions themselves.
- Claims about incidents, attribution, model behavior, and persistence should be tied to evidence.

---

# 15. SUCCESS CRITERION

The ideal final project should be something a judge can inspect quickly and say:

> “This team took a real incident, identified a specific unresolved question, used defensible evidence to answer or narrow it, produced something another person can actually use, clearly showed its limits, and created a credible path to follow-up research.”

Avoid:
- generic recommendations
- broad essays
- untestable speculation
- unnecessary replication without a clear extension
- projects whose strongest result depends on inaccessible private information

Prefer:
- bounded question
- measurable outcome
- public/reproducible evidence
- concrete artifact
- strong comparison/baseline
- clear novelty
- actionable conclusion

END OF TRACK & PROJECT SELECTION CONTEXT
