# Hackathon Judging, Submission, and Reporting Requirements

## Purpose

This file captures the official judging criteria, submission requirements, recommended report structure, AI-tool guidance, publishing guidance, important notes, and FAQ material for the Apart × CeSIA AI Incident Response Research Sprint.

Use this as a constraint document when selecting, designing, executing, and writing up a project. The judging rubric applies across all tracks; tracks guide judging through track-specific criteria, but projects compete across all submissions.

---

# 1. Judging Criteria

Projects are scored across three dimensions, each on a 1–5 scale.

## Dimension 1: Impact Potential & Innovation

**Question:** How much would this matter for AI safety if it worked? How innovative is it?

For scores of 4–5, judges specifically ask whether the work is actually new to the field or merely replicating recent work.

| Score | Description |
|---|---|
| **1** | **Negligible.** No clear problem addressed, or no meaningful novelty. |
| **2** | **Limited.** Addresses a real problem but with a generic or well-trodden approach. Incremental at best. |
| **3** | **Moderate.** Clear problem with a reasonable approach; some novelty in framing or method beyond routine application of existing tools. |
| **4** | **Significant.** Important problem with an original approach, or identifies a neglected problem area. A valuable contribution others could build on. |
| **5** | **Exceptional.** Tackles a critical AI safety problem with a genuinely novel approach, or opens a new research direction. Clear theory of change. You'd be excited to share this with researchers in the area. |

### Implication for project selection

A strong project should not merely demonstrate that an existing technique works on another dataset or incident. For a high impact/innovation score, the team should be able to state:

- What important problem is being addressed.
- What existing work already does.
- What is missing or inadequate in that work.
- What the team's new contribution is.
- Why that contribution could matter for AI safety.
- What future work could build on the result.

---

## Dimension 2: Execution Quality

**Question:** How sound are the methodology, implementation, and findings?

| Score | Description |
|---|---|
| **1** | **Seriously flawed.** Methodology broken, results uninterpretable, or implementation doesn't work. |
| **2** | **Weak.** Approach has significant gaps: missing validation, flawed experimental design, or incomplete implementation. |
| **3** | **Competent.** Technically solid given the short duration. Methodology makes sense, results are interpretable, limitations acknowledged, work builds toward clear conclusions. |
| **4** | **Strong.** Thorough methodology with convincing validation. Results clearly support conclusions. Immediately useful for future work. |
| **5** | **Exceptional.** Ambitious scope executed rigorously. Surprising findings, novel methods, or unusually robust validation. |

### Implication for project selection

A high-scoring project needs to be realistically executable during the sprint. Ambition is valuable only if the team can execute it rigorously.

Prioritize:

- A clearly defined research question.
- A reproducible methodology.
- Appropriate baselines or comparisons.
- Quantitative evaluation where possible.
- Validation of important findings.
- Explicit assumptions.
- Clear limitations and threats to validity.
- A conclusion that is proportional to the evidence.

Avoid choosing a project whose scope makes rigorous execution unlikely by the deadline.

---

## Dimension 3: Presentation & Clarity

**Question:** How clearly are the work, findings, and impact potential communicated?

| Score | Description |
|---|---|
| **1** | **Incomprehensible.** Cannot determine what the project is actually claiming or doing. |
| **2** | **Hard to follow.** Key information buried, missing, or diluted by excessive length. Significant effort to extract main points. |
| **3** | **Clear enough.** Can understand the problem, approach, and results without undue effort. Core content clearly present: problem, method, findings, limitations. |
| **4** | **Well presented.** Easy to follow, well-structured, appropriate level of detail. Target audience would get it quickly. |
| **5** | **Exceptionally clear.** A pleasure to read. Complex ideas made accessible. Could serve as a model for how to present this type of work. |

### Implication for project selection

The project should have a simple, communicable core:

> Problem → Method → Finding → Why it matters → Artifact/use

A technically strong project can lose value if judges cannot quickly determine what was done and what was learned.

---

# 2. Submission Requirements

## Required

Every submission must include:

1. **Research report (PDF)** using the official template.
2. **Project title and abstract**, with the abstract limited to **150 words or fewer**.
3. **Author names and affiliations**.
4. A **"Limitations and Dual-Use Considerations" appendix**.

## Optional

- **Public GitHub repository**, subject to disclosure review.
  - Do not publicly release novel installation recipes without review.
- **3–5 minute video demo**.

## Official submission template

Use the official template linked by the organizers:

https://docs.google.com/document/d/1PQBlhI3tM5vb51x7jBWXBQMYg6hkiU_x8RaCws4kjl4/copy?usp=sharing

**Important:** The FAQ states that the template linked on the Guidelines tab should always be used because templates in acceptance emails may be older.

---

# 3. Recommended Research Report Structure

The main report has a maximum length of **8 pages**, excluding references and appendices.

Most strong projects are **4–8 pages**.

Recommended structure:

## Introduction

Explain:

- Which track and sub-problem the project addresses.
- Why the problem matters.
- What the artifact is for.

## Related Work

Explain:

- What prior research/work the project builds on.
- What existing approaches already accomplish.
- What gap remains.
- What is new in the team's work.

## Methodology

Provide enough detail for replication, including:

- Methods.
- Experimental design.
- Data.
- Sources.
- Assumptions.
- Evaluation procedure.

## Results

Present:

- Quantitative results where possible.
- Main qualitative findings where quantitative evaluation is not appropriate.
- The main threat to validity.

## Discussion

Cover:

- What the results imply.
- Limitations.
- Future work.
- Practical or AI-safety implications.

## Limitations & Dual-Use Considerations

This appendix is **required**.

It should explicitly discuss:

- Important limitations.
- Threats to validity.
- What the artifact can and cannot establish.
- Potential misuse or dual-use concerns.
- Any relevant disclosure constraints.

## References

Cite the sources used to support the work.

---

# 4. AI Tools and the Report

The organizers explicitly distinguish between using AI tools as research/coding assistance and using AI to generate the team's report.

## Permitted/useful role for AI tools

AI tools may be used like a colleague to:

- Check reasoning.
- Find gaps in an argument or methodology.
- Debug code.

## Requirement for the report

The report itself must be:

- The team's own writing.
- About the team's own work.
- Specific to what the team actually did.

Judges read every submission.

The organizers warn that a report may be penalized if it reads as generated rather than written by the team, including through:

- Generic framing.
- Padded sections.
- Claims without sources.
- Lack of evidence of what the team actually did.

### Practical rule

Keep the report:

- Short.
- Specific.
- Evidence-based.
- Written in the team's own words.
- Explicit about what was actually done during the sprint.

Every factual claim should have an appropriate source.

---

# 5. Publishing the Work

The organizers encourage publication, with LessWrong described as a natural venue for many written submissions.

For public write-ups:

- State the epistemic status of claims.
- **Do not use LLMs to write the LessWrong post.**
- LLMs may be used to find problems in drafts.
- Link primary sources for every factual claim about the incident.
- Use a title that states the finding rather than merely the topic.
- Publishing an imperfect version this month is preferred to waiting three months for a polished version.
- The organizers may link the best posts from the sprint page.

### LessWrong length guidance

Written contributions should be **1500 words maximum**, excluding appendices.

The organizers emphasize that the quality and value of the work matters much more than length.

### Important distinction

The hackathon research report has an **8-page maximum** excluding references/appendices.

The separate LessWrong written contribution has a **1500-word maximum** excluding appendices.

Do not confuse these two limits.

---

# 6. Important Notes

## Solo vs team

- Participants may enter solo or as a team.
- Teams of up to **5** are recommended.
- Larger groups are allowed.

## Prohibited activity

Do not use any model to:

- Breach into any organisation.
- Commit any other type of felony.

The organizers explicitly prohibit using models for this purpose.

## Building on existing work

Building on existing research is:

- Allowed.
- Encouraged.

However, teams must disclose what they built on and clearly identify the new work done during the sprint.

Undisclosed prior work can lead to disqualification.

## Fixing or resubmitting

If a mistake is found:

- Submit again before the deadline.
- Use the **exact same title and details**.
- The new files replace the old ones.

## Submission channel

Submit through the official submission form on the hackathon page.

## Support

Support is available through:

- The Discord help-desk channel.
- Tagging **@Support**.
- Emailing `sprints@apartresearch.com`.

Discord help-desk:

https://discord.gg/ssZDasNkSE

## Pre-submission checklist

Before submission, verify:

- [ ] Research report PDF.
- [ ] Abstract ≤150 words.
- [ ] Author names and affiliations.
- [ ] Required Limitations and Dual-Use Considerations appendix.
- [ ] Main report ≤8 pages excluding references and appendices.
- [ ] Any novel installation results are withheld pending review.
- [ ] Public repository, if used, has passed disclosure review.

---

# 7. Frequently Asked Questions

## Getting started

### How does the sprint work?

Participants:

1. Sign up.
2. Join Discord.
3. Form or join a team, or work solo.
4. Pick a track and problem.
5. Build over the weekend.
6. Submit a research report PDF by the deadline.

Talks and Q&A run throughout the sprint.

### Can I participate remotely?

Yes.

The event is online. Talks, collaboration, and submissions happen through Discord and Zoom.

### How do teams work?

Teams can form before or during the sprint.

Participants can use team-forming Discord channels to find collaborators.

Solo participation is also allowed.

Teams of up to 5 are recommended, but larger groups are allowed.

### Do tracks affect scoring?

All projects are scored using the same rubric.

Tracks guide judging through track-specific criteria, and projects compete across all submissions.

### What background is required?

No specific background is required.

Participants may come from:

- ML.
- Interpretability.
- AI safety.
- Security.
- Other backgrounds.

The Resources tab is intended to provide the material needed to get up to speed.

### Are compute credits provided?

**No.**

Project selection should therefore avoid assuming access to organizer-provided compute credits.

### Do I need to attend all three days?

No.

Participants can work at their own pace.

Talks are optional but recommended.

The hard deadline is the Sunday submission cutoff.

### Can I participate from any country?

Yes.

The sprint is open globally.

---

# 8. Submission FAQ

## What do I submit?

A research report in PDF format using the official template.

The organizers describe it as:

- A mini research paper.
- Documentation of the problem.
- Approach.
- Results.
- Implications.

It is not primarily a product demo.

The required Limitations and Dual-Use Considerations appendix must be included.

## Which template should I use?

Always use the template linked on the Guidelines tab.

The template included in an acceptance email may be older.

## Will I get a confirmation after submitting?

Yes.

Participants should receive a confirmation with their project title shortly after submitting.

If no confirmation arrives, email `sprints@apartresearch.com`.

## My project doesn't show up on the website after submitting.

Submissions are published manually and can take up to **12 hours** to appear.

If the project is still missing after that, email `sprints@apartresearch.com`.

## I made a mistake. Can I fix or update my PDF?

Yes.

Submit again using the **exact same title and details**.

The new files replace the old ones.

If uncertain, ask in the help-desk channel and tag @Support first.

## Can I add team members after submitting?

Yes.

Update the team list through the submission form.

If help is needed, contact the help desk and tag @Support.

## Can I submit unfinished work?

Yes.

Submitting something unfinished is explicitly considered better than not submitting.

Judges evaluate what was accomplished within the available timeframe.

Honest limitations are welcome.

## Can I build on existing research?

Yes.

However:

- Clearly identify what is new work done during the sprint.
- Disclose what existing work was built upon.
- Undisclosed prior work can lead to disqualification.

## Can I submit multiple projects?

Yes.

Each project requires:

- Its own submission.
- A unique title.

However, most participants are expected to focus on one project.

---

# 9. Judging and Results FAQ

## How does judging work?

Projects are assigned to expert judges.

Judges review the submitted PDF and score it using the public rubric.

Judges typically have about a week after the event to complete reviews.

## Are individual judge scores shared?

No.

The rubric is public, but individual judge scores remain internal.

Constructive feedback is shared with participants without reviewer names.

## When will results be announced?

Typically **1–2 weeks after the judging deadline**.

Winners are contacted directly.

All participants receive reviewer feedback by email.

---

# 10. Project-Selection Implications

The judging criteria should directly influence project selection.

A project is especially attractive if it can plausibly achieve all three of the following:

### Impact & Innovation

- Important AI-safety problem.
- Clearly identified gap in existing work.
- Non-trivial novelty.
- Clear theory of change.
- Potential for others to build on the result.

### Execution Quality

- Narrow research question.
- Testable hypothesis.
- Public/reproducible evidence.
- Strong baseline or comparison.
- Quantitative evaluation where possible.
- Realistic sprint scope.
- Clear validity checks.
- Explicit limitations.

### Presentation & Clarity

- Simple core claim.
- Concrete artifact.
- Easy-to-understand methodology.
- Clear quantitative/qualitative result.
- Strong distinction between evidence and interpretation.
- Concise report structure.

## High-value project pattern

A particularly strong project often follows:

> **Important gap → bounded research question → reproducible method → measurable result → concrete artifact → actionable implication**

Avoid:

- Broad essays.
- Generic recommendations.
- Projects that merely repeat known work.
- Projects with no measurable outcome.
- Projects requiring unavailable compute.
- Projects where the core evidence cannot be obtained in time.
- Projects whose scope prevents rigorous validation.
- Projects where novelty cannot be distinguished from prior work.

---

# 11. Constraints to Give Any AI Research Agent

When asking an AI coding/research agent to help with this sprint, require it to:

1. Treat this file as the official judging/submission constraint context.
2. Optimize for **all three judging dimensions**, not only novelty.
3. Explicitly assess whether a proposed contribution is genuinely new or mostly replication.
4. Respect the 8-page main-report limit and ≤150-word abstract.
5. Include the required Limitations and Dual-Use Considerations appendix in the final submission plan.
6. Distinguish hackathon report requirements from the separate 1500-word LessWrong publishing limit.
7. Avoid unsupported factual claims and link/cite primary sources.
8. Clearly separate what the team actually did from prior work.
9. Respect the prohibition on using models to breach organisations or commit felonies.
10. Treat disclosure review as a real constraint for public artifacts.
11. Prefer concrete, gradeable, reproducible artifacts over broad prose.
12. Keep project scope realistic for the sprint.
13. State uncertainty and epistemic status explicitly.
14. Do not fabricate results, citations, experiments, or evidence.
15. Treat unfinished but honest work as preferable to fabricated completeness.

---

# 12. Official Links

- Submission template: https://docs.google.com/document/d/1PQBlhI3tM5vb51x7jBWXBQMYg6hkiU_x8RaCws4kjl4/copy?usp=sharing
- Discord help desk: https://discord.gg/ssZDasNkSE
- Support email: `sprints@apartresearch.com`

