# Recursive Improvement Protocol (RIP)

**Purpose:** emulate the useful engineering behavior of a recursive self-improving agent by improving persistent instructions, memory, tools, tests, and workflows from measured experience. This repository does not modify the hosted ChatGPT model weights.

## Operating loop: READ → BASELINE → DIAGNOSE → PROPOSE → TEST → REVIEW → INTEGRATE → RECORD

1. **READ:** refresh GitHub at the start of each substantive lab session. Read the session-start documents and the active project's relevant files. Check recent commits and CI results.
2. **BASELINE:** state what is currently known and verified. Separate facts, assumptions, unknowns, and failed checks.
3. **DIAGNOSE:** identify a concrete limitation or repeated failure. Link it to an issue, test, log, or design artifact where possible.
4. **PROPOSE:** make a small, reviewable change to a prompt, procedure, script, test, memory document, or project artifact. State the expected measurable benefit and possible regressions.
5. **TEST:** run deterministic checks and relevant domain checks. Compare against existing tests and a held-out/regression set where available.
6. **REVIEW:** inspect the actual diff and evidence. Check that the change did not merely weaken tests, hide errors, alter labels, or exploit evaluator gaps.
7. **INTEGRATE:** commit the candidate. Prefer a feature branch and pull request for changes to core procedures, CI, safety rules, or evaluation criteria. Human approval is required for consequential engineering and governance changes.
8. **RECORD:** append a concise experiment record: hypothesis, change, commit, tests, outcomes, regressions, decision, and follow-up.

## What may improve
- Project-specific procedures and checklists
- Reusable skills and templates
- Repository structure and documentation
- Deterministic validation scripts and CI workflows
- Test fixtures, regression cases, and evaluation coverage
- Retrieval/indexing strategy for repository memory
- Hardware design artifacts after datasheet-backed review

## What must not be self-approved
- Removing or weakening a failing test to make a score improve
- Changing evaluation criteria after seeing a candidate's result without recording and independently reviewing the change
- Marking unverified hardware or firmware as verified
- Overwriting historical experiment results
- Committing credentials, private data, or unlicensed vendor material
- Making consequential electrical, safety, thermal, or manufacturing decisions without explicit review

## Evidence standard
A change is an improvement only if it has:
- a defined baseline;
- a stated expected outcome;
- reproducible test evidence;
- regression checks appropriate to the change;
- a reviewable diff and traceable commit;
- no material regression hidden by a changed metric.

Use multiple evidence types for important changes: automated tests, static analysis, independent review, datasheet checks, simulation, and prototype measurements as appropriate. A green CI badge alone is not proof of electrical correctness.

## Memory model
- **Working memory:** current conversation and active task state; temporary.
- **Episodic memory:** append-only session and experiment records, including failures.
- **Semantic memory:** curated engineering facts, architecture, decisions, and verified constraints.
- **Procedural memory:** reusable checklists, prompts, scripts, and skills.
- **Evaluation memory:** regression tests, expected outcomes, test coverage, and known evaluator limitations.

Keep source evidence and timestamps/commit references attached to durable claims. Correct semantic knowledge by creating a new version or decision record; do not silently rewrite history.

## Session record template
Create one record per meaningful improvement experiment under `docs/experiments/`:
- Date and commit
- Problem and evidence
- Baseline
- Hypothesis
- Proposed change
- Tests and exact results
- Regression/side-effect review
- Decision: accepted, rejected, or needs more evidence
- Next experiment

## Practical autonomy levels
- **L0 — Manual:** user directs every change.
- **L1 — Assisted iteration:** ChatGPT reads, diagnoses, proposes, tests, and commits supported changes with user direction.
- **L2 — Gated evolution:** candidate branches and CI are used; a human approves consequential merges.
- **L3 — Bounded automation:** approved low-risk changes may be merged automatically under fixed tests and rollback controls.
- **L4 — Open-ended self-modification:** agent changes its own code and improvement mechanism. Out of scope for the current ChatGPT + GitHub workflow.

Initial target: L1, moving selectively to L2. Do not claim L3/L4.

## Per-session checklist
- [ ] Refresh repository and default branch
- [ ] Read the required project memory documents
- [ ] Read relevant active-project files
- [ ] Inspect latest commit and CI evidence when available
- [ ] State verified facts, assumptions, unknowns, and blockers
- [ ] Make a small evidence-driven change
- [ ] Run relevant checks and inspect the diff
- [ ] Record outcomes and next step
